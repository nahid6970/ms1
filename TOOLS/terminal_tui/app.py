import os
import sys

# Redirect stdout and stderr when running windowless (e.g., with pythonw.exe)
# to prevent silent crashes from print() or logging calls.
if sys.stdout is None or sys.stderr is None:
    try:
        log_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(log_dir, "app.log")
        # Open in append mode with line buffering
        f = open(log_file, "a", encoding="utf-8", buffering=1)
        if sys.stdout is None:
            sys.stdout = f
        if sys.stderr is None:
            sys.stderr = f
    except Exception:
        # Fallback to devnull if log file is unwritable
        if sys.stdout is None:
            sys.stdout = open(os.devnull, "w")
        if sys.stderr is None:
            sys.stderr = open(os.devnull, "w")

import json
import queue
import re
import threading
import subprocess
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_socketio import SocketIO, emit, disconnect
from winpty import PTY

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'terminal-tui-secret-key'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

PORT = 5577
BASE_DIR = r"C:\@delta\ms1\TOOLS"
PROJECTS_FILE = r"C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\projects.json"
ICONS_FILE = r"C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\extension_icons.json"

def load_extension_icons():
    if not os.path.exists(ICONS_FILE):
        return {}
    try:
        with open(ICONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading extension icons: {e}")
        return {}

def save_extension_icons(icons):
    try:
        os.makedirs(os.path.dirname(ICONS_FILE), exist_ok=True)
        with open(ICONS_FILE, "w", encoding="utf-8") as f:
            json.dump(icons, f, indent=2)
    except Exception as e:
        print(f"Error saving extension icons: {e}")

active_sessions = {}
sessions_lock = threading.Lock()

def get_git_status(path):
    if not os.path.isdir(path):
        return None
    try:
        # Normalize path to avoid mixed slash issues on Windows
        path = os.path.normpath(path)
        cf = 0x08000000 if sys.platform == "win32" else 0

        # Find the git root so we can scope commands to this project subfolder
        res_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, creationflags=cf, timeout=2
        )
        if res_root.returncode != 0:
            return None
        git_root = os.path.normpath((res_root.stdout or "").strip())

        # Relative path of this project inside the repo (used as pathspec)
        rel_path = os.path.relpath(path, git_root)
        # If project IS the repo root, use '.' — otherwise use the relative subfolder
        pathspec = "." if rel_path == "." else rel_path

        # Get current branch name
        res_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, creationflags=cf, timeout=2
        )
        branch = (res_branch.stdout or "").strip()
        if not branch:
            res_branch = subprocess.run(
                ["git", "symbolic-ref", "--short", "HEAD"],
                cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, creationflags=cf, timeout=2
            )
            branch = (res_branch.stdout or "").strip()

        if not branch:
            return None

        # Get file statuses scoped to this project subfolder
        res_status = subprocess.run(
            ["git", "status", "--porcelain", "-uall", "--", pathspec],
            cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, creationflags=cf, timeout=2
        )
        status_lines = [l for l in (res_status.stdout or "").strip().split("\n") if l.strip()]
        mod_count = len(status_lines)
        staged    = len([l for l in status_lines if l[0] not in ('?', ' ')])
        unstaged  = len([l for l in status_lines if l[1] != ' '])
        untracked = len([l for l in status_lines if l.startswith('??')])

        # Get lines added/deleted scoped to this project subfolder
        insertions, deletions = 0, 0
        for extra_flag in [[], ["--cached"]]:
            res_diff = subprocess.run(
                ["git", "diff", "--shortstat"] + extra_flag + ["--", pathspec],
                cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, creationflags=cf, timeout=2
            )
            diff_out = (res_diff.stdout or "").strip()
            if diff_out:
                m_ins = re.search(r'(\d+) insertion', diff_out)
                m_del = re.search(r'(\d+) deletion', diff_out)
                if m_ins: insertions += int(m_ins.group(1))
                if m_del: deletions += int(m_del.group(1))

        return {
            "branch": branch,
            "modifications": mod_count,
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "insertions": insertions,
            "deletions": deletions,
        }
    except Exception:
        return None



def get_session_key(project, pane_id=None):
    if not pane_id or pane_id == "main":
        return project
    return f"{project}::{pane_id}"


def session_belongs_to_project(session_key, project):
    return session_key == project or session_key.startswith(f"{project}::")


def restart_current_process(delay_seconds=1.0):
    def _restart():
        print("Restarting Terminal TUI process...")
        helper_code = (
            "import os, subprocess, sys, time;"
            "time.sleep(float(sys.argv[1]));"
            "subprocess.Popen(sys.argv[3:], cwd=sys.argv[2], close_fds=True)"
        )
        subprocess.Popen(
            [sys.executable, "-c", helper_code, str(delay_seconds), os.getcwd(), sys.executable, *sys.argv],
            close_fds=True,
        )
        os._exit(0)

    timer = threading.Timer(delay_seconds, _restart)
    timer.daemon = True
    timer.start()


class TerminalSession:
    def __init__(self, name, path, use_real_dir_name=False):
        self.name = name
        self.path = path
        self.cols = 100
        self.rows = 30
        self.pty = PTY(self.cols, self.rows)
        self.history = ""
        self.history_lock = threading.Lock()
        
        # Ensure project-specific data directory exists in C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\Project_data\<project>
        project_data_dir = os.path.join(r"C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\Project_data", name)
        os.makedirs(project_data_dir, exist_ok=True)
        
        profile_path = os.path.join(project_data_dir, "profile.ps1")
        history_path = os.path.join(project_data_dir, "history.txt").replace("\\", "/")
        
        path_clean = path.replace("/", "\\")
        
        if bool(use_real_dir_name):
            prompt_display_name = os.path.basename(os.path.normpath(path))
        else:
            prompt_display_name = name
            
        system_template = f"""# Custom PowerShell Profile for project: {name}
# Everything here is loaded when you select this project workspace dashboard.

# Global project root path
$global:PROJECT_ROOT_PATH = "{path_clean}"

# Force import PSReadLine in case it is disabled due to screen reader detection in PTY
Import-Module PSReadLine -ErrorAction SilentlyContinue

# Set custom project command history file
if (Get-Command Set-PSReadLineOption -ErrorAction SilentlyContinue) {{
    Set-PSReadLineOption -HistorySavePath "{history_path}"
}}

# Custom cd command to go to project root when no arguments are provided
if (Get-Alias cd -ErrorAction SilentlyContinue) {{
    Remove-Item alias:cd -Force -ErrorAction SilentlyContinue
}}
function cd {{
    if ($args.Count -eq 0) {{
        Set-Location $global:PROJECT_ROOT_PATH
    }} else {{
        $target = $args -join " "
        Set-Location $target
    }}
}}

# Custom prompt showing project root and subdirectories
function prompt {{
    $current = $pwd.Path.Replace("/", "\\")
    $root = $global:PROJECT_ROOT_PATH.Replace("/", "\\")
    if ($current.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {{
        $relative = $current.Substring($root.Length)
        if ($relative.StartsWith("\\") -or $relative.StartsWith("/")) {{
            $relative = $relative.Substring(1)
        }}
        if ([string]::IsNullOrEmpty($relative)) {{
            "{prompt_display_name}> "
        }} else {{
            "{prompt_display_name}\\$relative> "
        }}
    }} else {{
        "$current> "
    }}
}}

# Clear screen cleanly to start with a clean prompt and hide startup warnings
Write-Host "$([char]0x1b)[2J$([char]0x1b)[H" -NoNewline
"""

        user_customization_marker = "# Add your custom project aliases, functions, and environment variables below:"

        if not os.path.exists(profile_path):
            with open(profile_path, "w", encoding="utf-8") as f:
                f.write(system_template + f"\n{user_customization_marker}\n# Example:\n# Set-Alias ll Get-ChildItem\n")
        else:
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    old_content = f.read()
                
                needs_update = True  # Always update to apply the slash normalization fix
                
                if needs_update:
                    user_custom_part = ""
                    if user_customization_marker in old_content:
                        parts = old_content.split(user_customization_marker, 1)
                        user_custom_part = parts[1]
                    else:
                        if "Write-Host" in old_content:
                            parts = old_content.split("Write-Host", 1)
                            write_host_rest = parts[1].split("\n", 1)
                            if len(write_host_rest) > 1:
                                user_custom_part = "\n" + write_host_rest[1]
                    
                    if not user_custom_part.strip():
                        user_custom_part = "\n# Example:\n# Set-Alias ll Get-ChildItem\n"
                    
                    new_content = system_template + f"\n{user_customization_marker}\n" + user_custom_part.lstrip()
                    with open(profile_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
            except Exception as e:
                print(f"Error migrating profile: {e}")
        
        # Spawn PowerShell with custom profile, bypassing main user profile
        # Wrap in curly braces script block to handle spaces/parentheses in path correctly
        profile_path_clean = profile_path.replace("\\", "/")
        cmdline = f'powershell.exe -NoProfile -NoExit -Command "{{ . \'{profile_path_clean}\' }}"'
        
        # Spawn PowerShell
        self.pty.spawn("powershell.exe", cmdline=cmdline, cwd=path)
        
        self.connected_sids = set()
        self.sids_lock = threading.Lock()
        
        self.output_queue = queue.Queue()
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()
        
    def _read_loop(self):
        import time
        while self.pty.isalive():
            try:
                data = self.pty.read(blocking=False)
                if data:
                    with self.history_lock:
                        self.history += data
                        if len(self.history) > 100000:
                            self.history = self.history[-100000:]
                    
                    self.output_queue.put(data)
                    
                    with self.sids_lock:
                        sids = list(self.connected_sids)
                    for sid in sids:
                        try:
                            socketio.emit('pty-output', {'data': data}, room=sid, namespace='/pty')
                        except Exception:
                            pass
                else:
                    time.sleep(0.005)
            except Exception:
                break
        self.output_queue.put(None)
        with self.sids_lock:
            sids = list(self.connected_sids)
        for sid in sids:
            try:
                socketio.emit('pty-output', {'eof': True}, room=sid, namespace='/pty')
            except Exception:
                pass

    def write(self, data):
        if self.pty.isalive():
            self.pty.write(data)

    def resize(self, cols, rows):
        if self.cols != cols or self.rows != rows:
            self.cols = cols
            self.rows = rows
            if self.pty.isalive():
                self.pty.set_size(cols, rows)

    def add_sid(self, sid):
        with self.sids_lock:
            self.connected_sids.add(sid)

    def remove_sid(self, sid):
        with self.sids_lock:
            self.connected_sids.discard(sid)

    def get_history(self):
        with self.history_lock:
            return self.history

    def kill(self):
        if hasattr(self, 'pty') and self.pty.pid:
            try:
                # Forcefully terminate the process tree starting from the WinPTY shell process
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.pty.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Error calling taskkill on PID {self.pty.pid}: {e}")
        if hasattr(self, 'pty') and self.pty.isalive():
            try:
                os.close(self.pty.fd)
            except Exception:
                pass

def load_projects_config():
    if os.path.exists(PROJECTS_FILE):
        try:
            with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
                projs = json.load(f)
                # Sanitize bookmarks to be dicts
                for p in projs:
                    if "bookmarks" not in p:
                        p["bookmarks"] = []
                    else:
                        sanitized = []
                        for bm in p["bookmarks"]:
                            if isinstance(bm, str):
                                sanitized.append({"command": bm, "global": False, "windowTitle": ""})
                            elif isinstance(bm, dict):
                                sanitized.append({
                                    "command": bm.get("command", ""),
                                    "global": bm.get("global", False),
                                    "name": bm.get("name", ""),
                                    "windowTitle": bm.get("windowTitle", "")
                                })
                        p["bookmarks"] = sanitized
                return projs
        except Exception as e:
            print(f"Error reading projects config: {e}")
    return []

def save_projects_config(projects):
    try:
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2)
    except Exception as e:
        print(f"Error saving projects config: {e}")

def scan_projects():
    config_projects = load_projects_config()
    projects = []
    for p in config_projects:
        name = p["name"]
        path = p["path"]
        pinned = p.get("pinned", False)
        default_theme = {
            "background": "#000000",
            "foreground": "#d1d5db",
            "cursor": "#3b82f6",
            "scrollbarColor": "#475569",
            "scrollbarIdleColor": "#2d3748"
        }
        theme = p.get("theme", {})
        for k, v in default_theme.items():
            if k not in theme:
                theme[k] = v

        default_card_theme = {
            "bgColor": "#161c26",
            "textColor": "#f1f5f9",
            "pathColor": "#94a3b8",
            "accentColor": "#2563eb"
        }
        card_theme = p.get("cardTheme", {})
        for k, v in default_card_theme.items():
            if k not in card_theme:
                card_theme[k] = v
        
        with sessions_lock:
            is_active = any(
                session_belongs_to_project(session_key, name) and session.pty.isalive()
                for session_key, session in active_sessions.items()
            )
            
        bookmarks = p.get("bookmarks", [])
        layout = p.get("layout", {})
        category = p.get("category", "")
        projects.append({
            "name": name,
            "path": path.replace("\\", "/"),
            "category": category,
            "is_active": is_active,
            "pinned": pinned,
            "theme": theme,
            "cardTheme": card_theme,
            "bookmarks": bookmarks,
            "layout": layout
        })
    return projects

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/projects', methods=['GET'])
def api_projects_get():
    return jsonify(scan_projects())

@app.route('/api/projects', methods=['POST'])
def api_projects_post():
    data = request.json
    name = data.get("name", "").strip()
    path = data.get("path", "").strip()
    if not name or not path:
        return jsonify({"error": "Project Name and Path are required"}), 400
        
    # Check if folder exists
    if not os.path.exists(path) or not os.path.isdir(path):
        return jsonify({"error": f"The directory path '{path}' does not exist."}), 400
        
    projects = load_projects_config()
    
    # Check duplicate name
    if any(p["name"].lower() == name.lower() for p in projects):
        return jsonify({"error": f"A workspace named '{name}' already exists."}), 400
        
    category = data.get("category", "").strip()
    # Add project
    projects.append({
        "name": name,
        "path": os.path.abspath(path),
        "category": category,
        "pinned": False,
        "theme": {
            "background": "#000000",
            "foreground": "#d1d5db",
            "cursor": "#3b82f6",
            "scrollbarColor": "#475569",
            "scrollbarIdleColor": "#2d3748"
        },
        "cardTheme": {
            "bgColor": "#161c26",
            "textColor": "#f1f5f9",
            "pathColor": "#94a3b8",
            "accentColor": "#2563eb"
        },
        "bookmarks": []
    })
    save_projects_config(projects)
    
    return jsonify(scan_projects())

@app.route('/api/projects/<project>', methods=['DELETE'])
def api_projects_delete(project):
    projects = load_projects_config()
    
    # Filter out project
    filtered_projects = [p for p in projects if p["name"].lower() != project.lower()]
    
    if len(filtered_projects) == len(projects):
        return jsonify({"error": "Project not found"}), 404
        
    save_projects_config(filtered_projects)
    
    # Kill active session if any
    with sessions_lock:
        for session_key, session in list(active_sessions.items()):
            if not session_belongs_to_project(session_key, project):
                continue
            session.kill()
            del active_sessions[session_key]
            
    return jsonify(scan_projects())

@app.route('/api/projects/<project>/bookmarks', methods=['POST'])
def api_add_bookmark(project):
    data = request.json
    command = data.get("command", "").strip()
    name = data.get("name", "").strip()
    window_title = data.get("windowTitle", "").strip()
    if not command:
        return jsonify({"error": "Command is required"}), 400
        
    projects = load_projects_config()
    proj = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
        
    if "bookmarks" not in proj:
        proj["bookmarks"] = []
    # Check duplicate
    exists = False
    for bm in proj["bookmarks"]:
        if bm.get("command", "").lower() == command.lower():
            exists = True
            break
    if not exists:
        proj["bookmarks"].append({"command": command, "global": False, "name": name, "windowTitle": window_title})
        
    save_projects_config(projects)
    return jsonify(scan_projects())

@app.route('/api/projects/<project>/bookmarks/<int:index>', methods=['DELETE'])
def api_delete_bookmark(project, index):
    projects = load_projects_config()
    proj = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
        
    if "bookmarks" in proj and 0 <= index < len(proj["bookmarks"]):
        proj["bookmarks"].pop(index)
        
    save_projects_config(projects)
    return jsonify(scan_projects())

@app.route('/api/projects/<project>/bookmarks/<int:index>/global', methods=['POST'])
def api_toggle_bookmark_global(project, index):
    data = request.json or {}
    is_global = data.get("global", False)
    
    projects = load_projects_config()
    proj = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
        
    if "bookmarks" in proj and 0 <= index < len(proj["bookmarks"]):
        proj["bookmarks"][index]["global"] = is_global
        
    save_projects_config(projects)
    return jsonify(scan_projects())

@app.route('/api/projects/<project>/bookmarks/<int:index>/edit', methods=['POST'])
def api_edit_bookmark(project, index):
    data = request.json or {}
    command = data.get("command", "").strip()
    name = data.get("name", "").strip()
    window_title = data.get("windowTitle", "").strip()
    new_index = data.get("newIndex")
    
    if not command:
        return jsonify({"error": "Command is required"}), 400
        
    projects = load_projects_config()
    proj = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
        
    if "bookmarks" in proj and 0 <= index < len(proj["bookmarks"]):
        # Get target bookmark
        bm = proj["bookmarks"][index]
        bm["command"] = command
        bm["name"] = name
        bm["windowTitle"] = window_title
        
        # If new_index is provided and valid, move the bookmark
        if new_index is not None:
            try:
                new_index = int(new_index)
                if 0 <= new_index < len(proj["bookmarks"]) and new_index != index:
                    # Pop from old position and insert at new position
                    bm_pop = proj["bookmarks"].pop(index)
                    proj["bookmarks"].insert(new_index, bm_pop)
            except Exception as e:
                print(f"Error reordering bookmark: {e}")
                
    save_projects_config(projects)
    return jsonify(scan_projects())

@app.route('/api/projects/customize', methods=['POST'])
def api_projects_customize():
    data = request.json
    original_name = data.get("originalName", "").strip()
    if not original_name:
        # Fallback to name if originalName is not sent
        original_name = data.get("name", "").strip()
        
    if not original_name:
        return jsonify({"error": "Project Name is required"}), 400
        
    projects = load_projects_config()
    proj = next((p for p in projects if p["name"].lower() == original_name.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
        
    new_name = data.get("name", "").strip()
    new_path = data.get("path", "").strip()
    
    # If name is changing, check duplicate name
    name_changed = new_name and new_name.lower() != original_name.lower()
    if name_changed:
        if any(p["name"].lower() == new_name.lower() for p in projects):
            return jsonify({"error": f"A workspace named '{new_name}' already exists."}), 400
            
    # If path is changing, check if folder exists (normalized comparison)
    norm_existing_path = os.path.normpath(os.path.abspath(proj["path"])).lower()
    norm_new_path = os.path.normpath(os.path.abspath(new_path)).lower() if new_path else ""
    path_changed = bool(norm_new_path and norm_new_path != norm_existing_path)
    if path_changed:
        if not os.path.exists(new_path) or not os.path.isdir(new_path):
            return jsonify({"error": f"The directory path '{new_path}' does not exist."}), 400
            
    # Terminate active session if name or path changed, so it starts fresh!
    if name_changed or path_changed:
        with sessions_lock:
            for session_key, session in list(active_sessions.items()):
                if not session_belongs_to_project(session_key.lower(), original_name.lower()):
                    continue
                session.kill()
                del active_sessions[session_key]
                
    # Update properties
    if new_name:
        proj["name"] = new_name
    if new_path:
        proj["path"] = os.path.abspath(new_path)
    if "pinned" in data:
        proj["pinned"] = bool(data["pinned"])
        if proj["pinned"]:
            # Move pinned project to the top
            projects.remove(proj)
            projects.insert(0, proj)
    if "category" in data:
        proj["category"] = data["category"].strip()
    if "theme" in data:
        proj["theme"] = data["theme"]
    if "cardTheme" in data:
        proj["cardTheme"] = data["cardTheme"]
        
    save_projects_config(projects)
    
    return jsonify(scan_projects())

@app.route('/api/projects/reorder', methods=['POST'])
def api_projects_reorder():
    data = request.json
    ordered_names = data.get("names", [])
    if not ordered_names:
        return jsonify({"error": "Names are required"}), 400
        
    projects = load_projects_config()
    name_to_proj = {p["name"].lower(): p for p in projects}
    reordered_projects = []
    
    for name in ordered_names:
        proj = name_to_proj.get(name.lower())
        if proj:
            reordered_projects.append(proj)
            
    # Include any missing projects
    for p in projects:
        if p["name"].lower() not in [n.lower() for n in ordered_names]:
            reordered_projects.append(p)
            
    save_projects_config(reordered_projects)
    return jsonify(scan_projects())

@app.route('/api/projects/<project>/layout', methods=['POST'])
def api_projects_save_layout(project):
    data = request.json
    layout_class = data.get("layoutClass")
    pane_ids = data.get("paneIds")
    
    projects = load_projects_config()
    proj = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
        
    proj["layout"] = {
        "layoutClass": layout_class,
        "paneIds": pane_ids
    }
    save_projects_config(projects)
    return jsonify({"success": True})

@app.route('/api/sessions/reset', methods=['POST'])
def api_sessions_reset():
    with sessions_lock:
        for name, session in list(active_sessions.items()):
            session.kill()
        active_sessions.clear()

    # Reset layout configuration to default (single terminal pane) for all workspaces
    projects = load_projects_config()
    for p in projects:
        if "layout" in p:
            del p["layout"]
    save_projects_config(projects)

    restart_current_process()
    return jsonify({
        "projects": scan_projects(),
        "restarting": True,
    })

@app.route('/api/session/<project>/stop', methods=['POST'])
def api_session_stop(project):
    projects = scan_projects()
    # Case-insensitive lookup
    proj_details = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404
        
    with sessions_lock:
        for session_key, session in list(active_sessions.items()):
            if not session_belongs_to_project(session_key.lower(), project.lower()):
                continue
            session.kill()
            del active_sessions[session_key]
            
    return jsonify(scan_projects())

@app.route('/api/session/<project>', methods=['POST'])
def api_session(project):
    data = request.get_json(silent=True) or {}
    pane_id = data.get("paneId", "main")
    use_real_dir_name = data.get("useRealDirName", False)
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"] == project), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404

    session_key = get_session_key(project, pane_id)
    with sessions_lock:
        if session_key not in active_sessions or not active_sessions[session_key].pty.isalive():
            active_sessions[session_key] = TerminalSession(project, proj_details["path"], use_real_dir_name=use_real_dir_name)
            
    return jsonify({
        "status": "connected",
        "name": project,
        "paneId": pane_id,
        "path": proj_details["path"]
    })

def get_process_stats(pid):
    try:
        import psutil
        parent = psutil.Process(pid)
        # Get parent stats
        cpu_percent = parent.cpu_percent(interval=None)
        rss = parent.memory_info().rss
        
        # Get children recursively
        try:
            children = parent.children(recursive=True)
            for child in children:
                try:
                    cpu_percent += child.cpu_percent(interval=None)
                    rss += child.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
            
        memory_mb = rss / (1024 * 1024)
        return {
            "cpu": round(cpu_percent, 1),
            "memory": round(memory_mb, 1)
        }
    except Exception:
        return {"cpu": 0.0, "memory": 0.0}

@app.route('/api/debug/git/<project>', methods=['GET'])
def api_debug_git(project):
    import traceback as tb
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "not found"}), 404
    path = proj["path"]
    try:
        result = get_git_status(path)
        return jsonify({"path": path, "result": result})
    except Exception:
        return jsonify({"path": path, "error": tb.format_exc()}), 500

@app.route('/api/session/<project>/stats', methods=['GET'])
def api_session_stats(project):
    project_sessions = []
    with sessions_lock:
        for key, session in active_sessions.items():
            if session_belongs_to_project(key, project):
                project_sessions.append(session)
                
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"].lower() == project.lower()), None)
    git_info = None
    if proj_details:
        git_info = get_git_status(proj_details["path"])
        
    if not project_sessions:
        return jsonify({
            "cpu": 0.0,
            "memory": 0.0,
            "panes_count": 0,
            "git": git_info
        })
        
    total_cpu = 0.0
    total_mem = 0.0
    
    for session in project_sessions:
        if session.pty.isalive():
            pid = session.pty.pid
            stats = get_process_stats(pid)
            total_cpu += stats["cpu"]
            total_mem += stats["memory"]
            
    return jsonify({
        "cpu": round(total_cpu, 1),
        "memory": round(total_mem, 1),
        "panes_count": len(project_sessions),
        "git": git_info
    })

@app.route('/api/project/<project>/git/files', methods=['GET'])
def api_git_changed_files(project):
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())
        rel_path = os.path.relpath(path, git_root)
        pathspec = "." if rel_path == "." else rel_path

        res = subprocess.run(["git", "status", "--porcelain", "-uall", "--", pathspec], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=3)
        files = []
        for line in res.stdout.splitlines():
            if not line.strip():
                continue
            xy = line[:2]
            fname = line[3:].strip().strip('"')
            index_status = xy[0]
            work_status  = xy[1]
            if index_status == '?' and work_status == '?':
                label, color = "untracked", "#64748b"
            elif index_status != ' ' and index_status != '?':
                label, color = "staged", "#f59e0b"
                if work_status != ' ':
                    label, color = "modified+staged", "#f59e0b"
            else:
                label, color = "modified", "#94a3b8"
            files.append({"path": fname, "label": label, "color": color})
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project>/git/commit', methods=['POST'])
def api_git_commit(project):
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    add_all  = data.get("add_all", True)
    do_push  = data.get("push", False)

    if not message:
        return jsonify({"error": "Commit message is required"}), 400

    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())
        rel_path = os.path.relpath(path, git_root)
        pathspec = "." if rel_path == "." else rel_path

        if add_all:
            # Use git add -A to stage all changes including new directories
            res_add = subprocess.run(["git", "add", "-A", pathspec], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=10)
            if res_add.returncode != 0:
                return jsonify({"error": f"git add failed: {(res_add.stderr or "").strip()}"}), 500

        res_commit = subprocess.run(["git", "commit", "-m", message], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15)
        if res_commit.returncode != 0:
            err = (res_commit.stderr or "").strip() or (res_commit.stdout or "").strip()
            return jsonify({"error": f"git commit failed: {err}"}), 500

        output = (res_commit.stdout or "").strip()

        if do_push:
            res_push = subprocess.run(["git", "push"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=30)
            push_out = (res_push.stdout + res_push.stderr).strip()
            if res_push.returncode != 0:
                # Auto-retry with --set-upstream if branch has no upstream yet
                if "no upstream branch" in push_out or "set-upstream" in push_out:
                    res_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=5)
                    branch_name = (res_branch.stdout or "").strip() if res_branch.returncode == 0 else "HEAD"
                    res_push2 = subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=30)
                    push_out2 = (res_push2.stdout + res_push2.stderr).strip()
                    if res_push2.returncode == 0:
                        return jsonify({"success": True, "committed": True, "pushed": True, "output": output, "push_output": push_out2, "note": f"New branch '{branch_name}' pushed with --set-upstream"})
                    return jsonify({"success": True, "committed": True, "pushed": False, "output": output, "push_error": push_out2})
                return jsonify({"success": True, "committed": True, "pushed": False, "output": output, "push_error": push_out})
            return jsonify({"success": True, "committed": True, "pushed": True, "output": output, "push_output": push_out})

        return jsonify({"success": True, "committed": True, "pushed": False, "output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/commits', methods=['GET'])
def api_git_past_commits(project):
    """Get recent commits for this project, scoped to its directory"""
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())

        # Respect the same limit as the graph panel
        limit = request.args.get("limit", "40")
        try:
            limit = min(int(limit), 200)
        except Exception:
            limit = 40

        # Scope to project subdirectory (same as graph)
        rel_path = os.path.relpath(path, git_root).replace('\\', '/')
        scope_args = ["--", rel_path] if rel_path != '.' else []

        res = subprocess.run(
            ["git", "log", "--pretty=format:%h|%an|%ar|%s", "-n", str(limit)] + scope_args,
            cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', creationflags=cf, timeout=5
        )
        
        if res.returncode != 0:
            return jsonify({"error": "Failed to get commits"}), 500
            
        commits = []
        for line in (res.stdout or "").strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 3)
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3]
                })
                
        return jsonify({"commits": commits})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/graph', methods=['GET'])
def api_git_graph(project):
    """Get git log graph data for visual commit graph"""
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or '').strip())

        limit = request.args.get("limit", "40")
        try:
            limit = min(int(limit), 100)
        except Exception:
            limit = 40

        # Scope graph to project subdirectory so unrelated commits don't appear.
        # Use --simplify-merges so git rewrites parents to only reference commits
        # in the filtered output — prevents ghost parent slots in the lane algorithm.
        # --all ensures all branch heads are included.
        rel_path = os.path.relpath(path, git_root).replace('\\', '/')
        scope_args = ["--", rel_path] if rel_path != '.' else []
        extra_args = ["--simplify-merges"] if scope_args else []

        res = subprocess.run(
            ["git", "log", "--all", f"-n{limit}",
             "--pretty=format:%h%x00%H%x00%P%x00%D%x00%an%x00%ar%x00%s%x00",
             "--shortstat"] + extra_args + scope_args,
            cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', creationflags=cf, timeout=10
        )
        if res.returncode != 0:
            return jsonify({"error": "Failed to get git log"}), 500

        commits = []
        stdout = res.stdout or ''
        # git log --shortstat interleaves commit meta lines (containing \x00) and
        # stat lines (plain text like " 2 files changed...").
        # Merge commits produce NO stat line, so we can't rely on \n\n block splitting.
        # Instead: scan line-by-line. Any line with \x00 is a commit meta line;
        # any line without \x00 that follows a meta line is the stat for that commit.
        import re as _re
        pending_meta = None
        pending_stat = ''
        def flush_commit(meta_line, stat_line):
            parts = meta_line.split('\x00')
            if len(parts) < 6:
                return None
            short_hash  = parts[0].strip()
            full_hash   = parts[1].strip() if len(parts) > 1 else ''
            parents_str = parts[2].strip() if len(parts) > 2 else ''
            refs        = parts[3].strip() if len(parts) > 3 else ''
            author      = parts[4].strip() if len(parts) > 4 else ''
            date        = parts[5].strip() if len(parts) > 5 else ''
            message     = parts[6].strip() if len(parts) > 6 else ''
            if not short_hash:
                return None
            parents  = [p.strip() for p in parents_str.split() if p.strip()]
            ref_list = [r.strip() for r in refs.split(',') if r.strip()]
            insertions, deletions = 0, 0
            m_ins = _re.search(r'(\d+) insertion', stat_line)
            m_del = _re.search(r'(\d+) deletion', stat_line)
            if m_ins: insertions = int(m_ins.group(1))
            if m_del: deletions = int(m_del.group(1))
            return {
                "hash": short_hash, "fullHash": full_hash,
                "parents": parents, "refs": ref_list,
                "author": author, "date": date, "message": message,
                "insertions": insertions, "deletions": deletions
            }
        for raw_line in stdout.split('\n'):
            line = raw_line.strip()
            if not line:
                continue
            if '\x00' in line:
                # New commit meta line — flush previous
                if pending_meta:
                    c = flush_commit(pending_meta, pending_stat)
                    if c:
                        commits.append(c)
                pending_meta = line
                pending_stat = ''
            else:
                # Stat line for current pending commit
                if pending_meta:
                    pending_stat = line
        # Flush last
        if pending_meta:
            c = flush_commit(pending_meta, pending_stat)
            if c:
                commits.append(c)

        # Get current branch
        res_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', creationflags=cf, timeout=2)
        current_branch = (res_branch.stdout or '').strip() if res_branch.returncode == 0 else ""

        return jsonify({"commits": commits, "currentBranch": current_branch})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/commit/rename', methods=['POST'])
def api_git_rename_commit(project):
    """Rename (amend) the most recent commit message"""
    data = request.get_json() or {}
    new_message = data.get("new_message", "").strip()

    if not new_message:
        return jsonify({"error": "New commit message is required"}), 400

    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())

        # Get full HEAD hash and check if requested commit hash is a prefix of it
        res_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        full_head_hash = (res_head.stdout or "").strip()

        commit_hash = data.get("commit_hash", "").strip()

        # Allow rename if commit_hash is a prefix of the full HEAD hash
        if not full_head_hash.startswith(commit_hash):
            return jsonify({"error": "Only the most recent (HEAD) commit can be renamed here."}), 400

        res_amend = subprocess.run(
            ["git", "commit", "--amend", "-m", new_message],
            cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15
        )
        if res_amend.returncode != 0:
            err = (res_amend.stderr or "").strip() or (res_amend.stdout or "").strip()
            return jsonify({"error": f"git commit --amend failed: {err}"}), 500

        return jsonify({"success": True, "message": "Commit message updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/push', methods=['POST'])
def api_git_push(project):
    """Push commits to remote"""
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())
        
        res_push = subprocess.run(["git", "push"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=30)
        push_out = (res_push.stdout + res_push.stderr).strip()
        
        if res_push.returncode != 0:
            if "no upstream branch" in push_out or "set-upstream" in push_out:
                res_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=5)
                branch_name = (res_branch.stdout or "").strip() if res_branch.returncode == 0 else "HEAD"
                res_push2 = subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=30)
                push_out2 = (res_push2.stdout + res_push2.stderr).strip()
                if res_push2.returncode == 0:
                    return jsonify({"success": True, "output": push_out2, "note": f"New branch '{branch_name}' pushed with --set-upstream"})
                return jsonify({"success": False, "error": push_out2}), 500
            return jsonify({"success": False, "error": push_out}), 500
            
        return jsonify({"success": True, "output": push_out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/diff', methods=['GET'])
def api_git_diff(project):
    """Get git diff. from_ref defaults to HEAD (last commit). to_ref defaults to working tree."""
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    from_ref = request.args.get("from", "HEAD")
    to_ref   = request.args.get("to", "")   # empty = working tree

    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or '').strip())

        # Build diff command
        if to_ref:
            cmd = ["git", "diff", from_ref, to_ref, "--"]
        else:
            # diff between from_ref and working tree (includes staged+unstaged)
            cmd = ["git", "diff", from_ref, "--"]

        res = subprocess.run(cmd, cwd=git_root,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', errors='replace', creationflags=cf, timeout=15)

        diff_text = (res.stdout or '')

        # Also get list of changed files with status
        stat_cmd = ["git", "diff", "--stat", from_ref] if not to_ref else ["git", "diff", "--stat", from_ref, to_ref]
        res_stat = subprocess.run(stat_cmd, cwd=git_root,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', errors='replace', creationflags=cf, timeout=10)

        # Parse changed files from name-status
        ns_cmd = ["git", "diff", "--name-status", from_ref] if not to_ref else ["git", "diff", "--name-status", from_ref, to_ref]
        res_ns = subprocess.run(ns_cmd, cwd=git_root,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', errors='replace', creationflags=cf, timeout=10)

        files = []
        for line in (res_ns.stdout or '').strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('\t', 1)
            if len(parts) == 2:
                status, fname = parts[0].strip(), parts[1].strip()
                files.append({"status": status, "file": fname})

        return jsonify({
            "diff": diff_text,
            "files": files,
            "from": from_ref,
            "to": to_ref or "working tree",
            "stat": (res_stat.stdout or '').strip()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/checkout', methods=['POST'])
def api_git_checkout(project):
    """Checkout a specific commit (detached HEAD)"""
    data = request.get_json() or {}
    commit_hash = data.get("commit_hash", "").strip()
    
    if not commit_hash:
        return jsonify({"error": "Commit hash is required"}), 400
        
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())
        
        res_checkout = subprocess.run(["git", "checkout", commit_hash], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15)
        checkout_out = (res_checkout.stdout + res_checkout.stderr).strip()
        
        if res_checkout.returncode != 0:
            return jsonify({"success": False, "error": checkout_out}), 500
            
        return jsonify({"success": True, "output": checkout_out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/tree', methods=['GET'])
def api_git_tree(project):
    """List all files at a specific commit (git ls-tree) — no checkout"""
    commit_hash = request.args.get("hash", "HEAD").strip()
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())
        rel_path = os.path.relpath(path, git_root).replace("\\", "/")
        pathspec = rel_path if rel_path != "." else None

        cmd = ["git", "ls-tree", "-r", "--name-only", commit_hash]
        if pathspec:
            cmd.append(pathspec)
        res = subprocess.run(cmd, cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=10)
        if res.returncode != 0:
            return jsonify({"error": (res.stderr or "").strip() or "Failed to list tree"}), 400
        files = [f for f in (res.stdout or "").strip().split("\n") if f.strip()]
        # Strip project subfolder prefix for display
        if pathspec and pathspec != ".":
            prefix = pathspec.rstrip("/") + "/"
            files = [f[len(prefix):] if f.startswith(prefix) else f for f in files]
        return jsonify({"files": files, "hash": commit_hash})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/show', methods=['GET'])
def api_git_show(project):
    """Get file content at a specific commit (git show hash:path) — no checkout"""
    commit_hash = request.args.get("hash", "HEAD").strip()
    file_path = request.args.get("path", "").strip()
    if not file_path:
        return jsonify({"error": "path is required"}), 400
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())
        rel_path = os.path.relpath(path, git_root).replace("\\", "/")
        # Build full path spec: project_subdir/file_path
        full_path_spec = file_path if rel_path == "." else f"{rel_path}/{file_path}"
        obj_spec = f"{commit_hash}:{full_path_spec}"
        res = subprocess.run(["git", "show", obj_spec], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", creationflags=cf, timeout=10)
        if res.returncode != 0:
            return jsonify({"error": (res.stderr or "").strip() or "File not found at this commit"}), 404
        content = res.stdout
        size = len(content.encode("utf-8"))
        lines = content.count("\n")
        return jsonify({"content": content, "size": size, "lines": lines, "hash": commit_hash, "path": file_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/restore-file', methods=['POST'])
def api_git_restore_file(project):
    """Restore a specific file to a past commit version (git checkout hash -- path) — no HEAD detach"""
    data = request.get_json() or {}
    commit_hash = data.get("hash", "").strip()
    file_path = data.get("path", "").strip()
    if not commit_hash or not file_path:
        return jsonify({"error": "hash and path are required"}), 400
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())
        rel_path = os.path.relpath(path, git_root).replace("\\", "/")
        full_path_spec = file_path if rel_path == "." else f"{rel_path}/{file_path}"
        res = subprocess.run(["git", "checkout", commit_hash, "--", full_path_spec], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=10)
        if res.returncode != 0:
            return jsonify({"error": (res.stderr or "").strip() or "Restore failed"}), 500
        return jsonify({"success": True, "hash": commit_hash, "path": file_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/return-branch', methods=['POST'])
def api_git_return_branch(project):
    """Return to the latest commit on the current branch"""
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())
        
        # Get current branch name
        res_branch = subprocess.run(["git", "branch", "--show-current"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        branch = (res_branch.stdout or "").strip()
        
        if not branch:
            # Fallback: try symbolic-ref
            res_branch = subprocess.run(["git", "symbolic-ref", "--short", "HEAD"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
            branch = (res_branch.stdout or "").strip()
            
        if not branch:
            # If still no branch (detached), checkout main/master as fallback
            branch = "main"
        
        res_checkout = subprocess.run(["git", "checkout", branch], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15)
        checkout_out = (res_checkout.stdout + res_checkout.stderr).strip()
        
        if res_checkout.returncode != 0:
            return jsonify({"success": False, "error": checkout_out}), 500
            
        return jsonify({"success": True, "branch": branch, "output": checkout_out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/discard', methods=['POST'])
def api_git_discard(project):
    """Discard all uncommitted changes (git restore . and git clean -fd)"""
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())

        rel_path = os.path.relpath(path, git_root)
        pathspec = "." if rel_path == "." else rel_path

        # Restore tracked files to last commit state
        res_restore = subprocess.run(["git", "restore", pathspec], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15)
        # Also remove untracked files/dirs in this pathspec
        res_clean = subprocess.run(["git", "clean", "-fd", "--", pathspec], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15)

        if res_restore.returncode != 0:
            err = (res_restore.stderr or "").strip() or (res_restore.stdout or "").strip()
            return jsonify({"error": f"git restore failed: {err}"}), 500

        out = (res_restore.stdout + res_restore.stderr + res_clean.stdout).strip()
        return jsonify({"success": True, "output": out or "All changes discarded."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def api_paste_image(project):
    projects = scan_projects()
    proj = next((p for p in projects if p["name"] == project), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
        
    if 'image' not in request.files:
        return jsonify({"error": "No image file sent"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    original_filename = file.filename
    # Detect if it's from clipboard paste
    is_clipboard = original_filename in ["clipboard.png", "pasted_image.png", "image.png", "blob"]
    
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if is_clipboard:
        filename = f"pasted_image_{timestamp}.png"
    else:
        # For dragged files, preserve their original name to avoid confusion
        name_part, ext_part = os.path.splitext(original_filename)
        name_part = os.path.basename(name_part)  # Sanitize name
        if not ext_part:
            ext_part = ".png"
        filename = f"{name_part}_{timestamp}{ext_part}"
    
    dest_path = os.path.join(proj["path"], filename)
    try:
        file.save(dest_path)
        return jsonify({
            "status": "success",
            "path": dest_path.replace("\\", "/"),
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

@app.route('/api/project/<project>/files', methods=['GET'])
def api_project_files(project):
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404
        
    path = proj_details["path"]
    if not os.path.exists(path) or not os.path.isdir(path):
        return jsonify({"error": "Directory does not exist"}), 404
        
    sub_dir = request.args.get("subdir", "")
    target_path = os.path.normpath(os.path.join(path, sub_dir))
    
    # Prevent directory traversal attacks
    if not os.path.abspath(target_path).startswith(os.path.abspath(path)):
        return jsonify({"error": "Unauthorized path access"}), 403
         
    try:
        items = []
        for name in os.listdir(target_path):
            if name in [".git", "node_modules", "dist", ".next", ".cache"]:
                continue
            full_item_path = os.path.join(target_path, name)
            is_dir = os.path.isdir(full_item_path)
            items.append({
                "name": name,
                "is_dir": is_dir,
                "rel_path": os.path.relpath(full_item_path, path).replace("\\", "/")
            })
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return jsonify({"items": items, "current_dir": sub_dir.replace("\\", "/")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/file-content', methods=['GET'])
def api_project_file_content(project):
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404
    base_path = os.path.abspath(proj_details["path"])
    rel_path = request.args.get("path", "")
    if not rel_path:
        return jsonify({"error": "No path provided"}), 400
    target = os.path.normpath(os.path.join(base_path, rel_path))
    if not os.path.abspath(target).startswith(base_path):
        return jsonify({"error": "Unauthorized path"}), 403
    if not os.path.isfile(target):
        return jsonify({"error": "Not a file"}), 404
    size = os.path.getsize(target)
    if size > 1 * 1024 * 1024:  # 1 MB limit
        return jsonify({"error": "File too large to preview (> 1 MB)"}), 413
    try:
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return jsonify({"content": content, "path": rel_path, "size": size})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project>/file-delete', methods=['POST'])
def api_project_file_delete(project):
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404
    base_path = os.path.abspath(proj_details["path"])
    rel_path = request.json.get("path", "")
    if not rel_path:
        return jsonify({"error": "No path provided"}), 400
    target = os.path.normpath(os.path.join(base_path, rel_path))
    if not os.path.abspath(target).startswith(base_path):
        return jsonify({"error": "Unauthorized path"}), 403
    if not os.path.exists(target):
        return jsonify({"error": "File or directory does not exist"}), 404
    
    try:
        import shutil
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project>/file-write', methods=['POST'])
def api_project_file_write(project):
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404
    base_path = os.path.abspath(proj_details["path"])
    filename = request.json.get("filename", "").strip()
    content = request.json.get("content", "")
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    target = os.path.normpath(os.path.join(base_path, filename))
    if not os.path.abspath(target).startswith(base_path):
        return jsonify({"error": "Unauthorized path"}), 403
    if os.path.exists(target):
        return jsonify({"error": "File already exists"}), 409
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project>/paste-clipboard', methods=['POST'])
def api_project_paste_clipboard(project):
    import shutil
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404
    base_path = os.path.abspath(proj_details["path"])
    
    try:
        cf = 0x08000000 if sys.platform == "win32" else 0
        # Use PowerShell to get file paths from clipboard
        ps_cmd = (
            'Add-Type -AssemblyName System.Windows.Forms; '
            '$files = [System.Windows.Forms.Clipboard]::GetFileDropList(); '
            'if ($files.Count -eq 0) { Write-Error "NO_FILES"; exit 1 } '
            '$files | ForEach-Object { $_ }'
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10,
            creationflags=cf
        )
        if result.returncode != 0:
            return jsonify({"error": "No files found in clipboard."}), 400
        
        file_paths = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
        if not file_paths:
            return jsonify({"error": "No files found in clipboard."}), 400
        
        copied = 0
        for src in file_paths:
            src = os.path.normpath(src)
            if not os.path.exists(src):
                continue
            dest = os.path.join(base_path, os.path.basename(src))
            if os.path.isdir(src):
                if os.path.exists(dest):
                    # Merge into existing dir
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                else:
                    shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
            copied += 1
        
        if copied == 0:
            return jsonify({"error": "No valid files to paste."}), 400
        return jsonify({"status": "success", "count": copied})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Clipboard read timed out."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/project/<project>/init-framework', methods=['POST'])
def api_project_init_framework(project):
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"].lower() == project.lower()), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404
    base_path = os.path.abspath(proj_details["path"])
    
    framework = request.json.get("framework", "").strip().lower()
    if not framework:
        return jsonify({"error": "No framework selected"}), 400

    templates = {}
    
    if framework == "react":
        templates = {
            "package.json": """{
  "name": "react-starter",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.15",
    "@types/react-dom": "^18.2.7",
    "@vitejs/plugin-react": "^4.0.3",
    "vite": "^4.4.5"
  }
}""",
            "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})""",
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>React Starter</title>
  </head>
  <body style="margin: 0; background: #0f172a; color: #f8fafc; font-family: sans-serif;">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",
            "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
            "src/index.css": """body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}""",
            "src/App.jsx": """import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100vw', height: '100vh', gap: '20px' }}>
      <h1 style={{ color: '#61dafb', fontSize: '3rem', margin: 0 }}>React + Vite</h1>
      <p style={{ fontSize: '1.2rem', color: '#94a3b8' }}>Get started by editing <code>src/App.jsx</code></p>
      <button 
        onClick={() => setCount((count) => count + 1)}
        style={{ padding: '10px 20px', fontSize: '1rem', background: '#61dafb', border: 'none', borderRadius: '8px', color: '#0f172a', fontWeight: 'bold', cursor: 'pointer', transition: 'transform 0.1s' }}
        onMouseDown={(e) => e.target.style.transform = 'scale(0.95)'}
        onMouseUp={(e) => e.target.style.transform = 'scale(1)'}
      >
        Count is {count}
      </button>
    </div>
  )
}

export default App"""
        }
    elif framework == "vue":
        templates = {
            "package.json": """{
  "name": "vue-starter",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.4"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.3",
    "vite": "^4.3.9"
  }
}""",
            "vite.config.js": """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})""",
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vue Starter</title>
  </head>
  <body style="margin: 0; background: #1e1e24; color: #e1e1e6; font-family: sans-serif;">
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>""",
            "src/main.js": """import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')""",
            "src/App.vue": """<template>
  <div class="container">
    <h1 class="title">Vue 3 + Vite</h1>
    <p class="subtitle">Get started by editing <code>src/App.vue</code></p>
    <button class="btn" @click="count++">Count is {{ count }}</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const count = ref(0)
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  gap: 20px;
}
.title {
  color: #42b883;
  font-size: 3rem;
  margin: 0;
}
.subtitle {
  font-size: 1.2rem;
  color: #888;
}
.btn {
  padding: 10px 20px;
  font-size: 1rem;
  background: #42b883;
  border: none;
  border-radius: 8px;
  color: #1a1a1a;
  font-weight: bold;
  cursor: pointer;
}
</style>"""
        }
    elif framework == "angularjs":
        templates = {
            "index.html": """<!DOCTYPE html>
<html lang="en" ng-app="app">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AngularJS 1.x Starter</title>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.2/angular.min.js"></script>
  </head>
  <body ng-controller="MainController" style="margin: 0; background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100vw; height: 100vh; gap: 20px;">
    <h1 style="color: #dd1b16; fontSize: '3rem'; margin: 0;">AngularJS 1.x</h1>
    <p style="fontSize: '1.2rem'; color: '#94a3b8';">{{ greeting }}</p>
    <button ng-click="increment()" style="padding: 10px 20px; font-size: 1rem; background: #dd1b16; border: none; border-radius: 8px; color: white; font-weight: bold; cursor: pointer;">
      Count is {{ count }}
    </button>
    <script src="/app.js"></script>
  </body>
</html>""",
            "app.js": """angular.module('app', [])
.controller('MainController', ['$scope', function($scope) {
  $scope.greeting = 'Get started by editing index.html and app.js';
  $scope.count = 0;
  $scope.increment = function() {
    $scope.count++;
  };
}]);"""
        }
    elif framework == "svelte":
        templates = {
            "package.json": """{
  "name": "svelte-starter",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^2.4.2",
    "svelte": "^4.0.5",
    "vite": "^4.4.5"
  }
}""",
            "vite.config.js": """import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
})""",
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Svelte Starter</title>
  </head>
  <body style="margin: 0; background: #1a1a24; color: #fff; font-family: sans-serif;">
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>""",
            "src/main.js": """import App from './App.svelte'

const app = new App({
  target: document.getElementById('app'),
})

export default app""",
            "src/App.svelte": """<script>
  let count = 0;
</script>

<main class="container">
  <h1 class="title">Svelte + Vite</h1>
  <p class="subtitle">Get started by editing <code>src/App.svelte</code></p>
  <button class="btn" on:click={() => count++}>Count is {count}</button>
</main>

<style>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    gap: 20px;
  }
  .title {
    color: #ff3e00;
    font-size: 3rem;
    margin: 0;
  }
  .subtitle {
    font-size: 1.2rem;
    color: #888;
  }
  .btn {
    padding: 10px 20px;
    font-size: 1rem;
    background: #ff3e00;
    border: none;
    border-radius: 8px;
    color: #fff;
    font-weight: bold;
    cursor: pointer;
  }
</style>"""
        }
    elif framework == "tailwind_html":
        templates = {
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tailwind Play CDN Starter</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col items-center justify-center p-6">
    <div class="max-w-md w-full bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl p-8 flex flex-col items-center text-center gap-6">
      <div class="h-16 w-16 bg-sky-500/10 rounded-full flex items-center justify-center text-sky-400 text-3xl font-bold">
        ⚡
      </div>
      <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">Tailwind CSS</h1>
      <p class="text-slate-400 text-sm leading-relaxed">
        This template uses the Tailwind Play CDN. Get started by modifying <code class="bg-slate-950 px-2 py-1 rounded text-pink-400 font-mono text-xs">index.html</code>.
      </p>
      <button class="w-full bg-sky-500 hover:bg-sky-400 active:scale-[0.98] transition text-slate-950 font-bold py-3 px-6 rounded-xl shadow-lg shadow-sky-500/20">
        Get Started
      </button>
    </div>
  </body>
</html>"""
        }
    elif framework == "nextjs":
        templates = {
            "package.json": """{
  "name": "nextjs-starter",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}""",
            "app/layout.js": """export const metadata = {
  title: 'Next.js App',
  description: 'Created with Next.js Starter',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, boxSizing: 'border-box', background: '#09090b', color: '#fafafa', fontFamily: 'sans-serif' }}>
        {children}
      </body>
    </html>
  )
}""",
            "app/page.js": """export default function Home() {
  return (
    <main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', gap: '16px' }}>
      <h1 style={{ fontSize: '3rem', margin: 0, fontWeight: '800' }}>Next.js App Router</h1>
      <p style={{ color: '#a1a1aa' }}>Get started by editing <code>app/page.js</code></p>
    </main>
  )
}"""
        }
    elif framework == "solidjs":
        templates = {
            "package.json": """{
  "name": "solid-starter",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "solid-js": "^1.7.6"
  },
  "devDependencies": {
    "vite": "^4.3.9",
    "vite-plugin-solid": "^2.7.0"
  }
}""",
            "vite.config.js": """import { defineConfig } from 'vite'
import solidPlugin from 'vite-plugin-solid'

export default defineConfig({
  plugins: [solidPlugin()],
})""",
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SolidJS Starter</title>
  </head>
  <body style="margin: 0; background: #13141f; color: #fff; font-family: sans-serif;">
    <div id="app"></div>
    <script type="module" src="/src/index.jsx"></script>
  </body>
</html>""",
            "src/index.jsx": """import { render } from 'solid-js/web'
import App from './App'

render(() => <App />, document.getElementById('app'))""",
            "src/App.jsx": """import { createSignal } from 'solid-js'

function App() {
  const [count, setCount] = createSignal(0)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100vw', height: '100vh', gap: '20px' }}>
      <h1 style={{ color: '#446b9e', fontSize: '3rem', margin: 0 }}>SolidJS + Vite</h1>
      <p style={{ fontSize: '1.2rem', color: '#888' }}>Get started by editing <code>src/App.jsx</code></p>
      <button 
        onClick={() => setCount(count() + 1)}
        style={{ padding: '10px 20px', fontSize: '1rem', background: '#446b9e', border: 'none', borderRadius: '8px', color: '#fff', fontWeight: 'bold', cursor: 'pointer' }}
      >
        Count is {count()}
      </button>
    </div>
  )
}

export default App"""
        }
    elif framework == "preact":
        templates = {
            "package.json": """{
  "name": "preact-starter",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "preact": "^10.15.1"
  },
  "devDependencies": {
    "@preact/preset-vite": "^2.5.0",
    "vite": "^4.3.9"
  }
}""",
            "vite.config.js": """import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'

export default defineConfig({
  plugins: [preact()],
})""",
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Preact Starter</title>
  </head>
  <body style="margin: 0; background: #191919; color: #f3f3f3; font-family: sans-serif;">
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",
            "src/main.jsx": """import { render } from 'preact'
import App from './App.jsx'

render(<App />, document.body)""",
            "src/App.jsx": """import { useState } from 'preact/hooks'

export default function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100vw', height: '100vh', gap: '20px' }}>
      <h1 style={{ color: '#673ab8', fontSize: '3rem', margin: 0 }}>Preact + Vite</h1>
      <p style={{ fontSize: '1.2rem', color: '#888' }}>Get started by editing <code>src/App.jsx</code></p>
      <button 
        onClick={() => setCount(count + 1)}
        style={{ padding: '10px 20px', fontSize: '1rem', background: '#673ab8', border: 'none', borderRadius: '8px', color: '#fff', fontWeight: 'bold', cursor: 'pointer' }}
      >
        Count is {count}
      </button>
    </div>
  )
}"""
        }
    elif framework == "alpinejs":
        templates = {
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Alpine.js Play CDN Starter</title>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  </head>
  <body style="margin: 0; background: #0f172a; color: #f8fafc; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100vw; height: 100vh; gap: 20px;">
    <div x-data="{ count: 0, title: 'Alpine.js' }" style="text-align: center; display: flex; flex-direction: column; gap: 16px; align-items: center;">
      <h1 x-text="title" style="color: #77c1d4; font-size: 3rem; margin: 0;"></h1>
      <p style="font-size: 1.2rem; color: #94a3b8;">Get started by editing <code>index.html</code></p>
      <button @click="count++" style="padding: 10px 20px; font-size: 1rem; background: #77c1d4; border: none; border-radius: 8px; color: #0f172a; font-weight: bold; cursor: pointer;">
        Count is <span x-text="count"></span>
      </button>
    </div>
  </body>
</html>"""
        }
    elif framework == "angular":
        templates = {
            "package.json": """{
  "name": "angular-starter",
  "version": "1.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "watch": "ng build --watch --configuration development"
  },
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "rxjs": "~7.8.0",
    "tslib": "^2.5.0",
    "zone.js": "~0.14.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^17.0.0",
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "typescript": "~5.2.2"
  }
}""",
            "tsconfig.json": """{
  "compileOnSave": false,
  "compilerOptions": {
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}""",
            "angular.json": """{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "angular-starter": {
      "projectType": "application",
      "schematics": {},
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:application",
          "options": {
            "outputPath": "dist/angular-starter",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.css"],
            "scripts": []
          }
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {
            "production": {
              "buildTarget": "angular-starter:build:production"
            },
            "development": {
              "buildTarget": "angular-starter:build:development"
            }
          },
          "defaultConfiguration": "development"
        }
      }
    }
  }
}""",
            "tsconfig.app.json": """{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/app",
    "types": []
  },
  "files": ["src/main.ts"],
  "include": ["src/**/*.d.ts"]
}""",
            "src/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Angular Modern Starter</title>
    <base href="/" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body style="margin: 0; background: #1a1a2e; color: #fff; font-family: sans-serif;">
    <app-root></app-root>
  </body>
</html>""",
            "src/styles.css": """/* Global styles */""",
            "src/main.ts": """import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent).catch(err => console.error(err));""",
            "src/app/app.component.ts": """import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  standalone: true,
  template: `
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100vw; height: 100vh; gap: 20px;">
      <h1 style="color: #c3002f; font-size: 3rem; margin: 0;">Angular 17+</h1>
      <p style="font-size: 1.2rem; color: #aaa;">Get started by editing <code>src/app/app.component.ts</code></p>
      <button (click)="increment()" style="padding: 10px 20px; font-size: 1rem; background: #c3002f; border: none; border-radius: 8px; color: #fff; font-weight: bold; cursor: pointer;">
        Count is {{ count }}
      </button>
    </div>
  `
})
export class AppComponent {
  count = 0;
  increment() {
    this.count++;
  }
}"""
        }
    else:
        return jsonify({"error": "Unknown framework template"}), 400

    try:
        for rel_file, content in templates.items():
            file_path = os.path.join(base_path, rel_file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        return jsonify({"status": "success", "files": list(templates.keys())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/temp', methods=['POST'])
def api_temp_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file sent"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    import datetime
    import tempfile

    original_filename = os.path.basename(file.filename)
    name_part, ext_part = os.path.splitext(original_filename)
    if not name_part:
        name_part = "dropped_image"
    if not ext_part:
        ext_part = ".png"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name_part}_{timestamp}{ext_part}"
    temp_dir = os.path.join(tempfile.gettempdir(), "terminal_tui_images")
    os.makedirs(temp_dir, exist_ok=True)

    dest_path = os.path.join(temp_dir, filename)
    try:
        file.save(dest_path)
        return jsonify({
            "status": "success",
            "path": dest_path.replace("\\", "/"),
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": f"Failed to save temporary image: {str(e)}"}), 500

@app.route('/api/session/<project>/paste-image', methods=['POST'])
def api_project_paste_image(project):
    if 'image' not in request.files:
        return jsonify({"error": "No image file sent"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    import datetime
    import tempfile

    original_filename = os.path.basename(file.filename)
    name_part, ext_part = os.path.splitext(original_filename)
    if not name_part:
        name_part = "pasted_image"
    if not ext_part:
        ext_part = ".png"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name_part}_{timestamp}{ext_part}"
    
    # Save it to target folder C:\Users\nahid\AppData\Local\Temp\screenshot_temp
    target_dir = r"C:\Users\nahid\AppData\Local\Temp\screenshot_temp"
    
    os.makedirs(target_dir, exist_ok=True)
    dest_path = os.path.join(target_dir, filename)
    try:
        file.save(dest_path)
        return jsonify({
            "status": "success",
            "path": dest_path.replace("\\", "/"),
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": f"Failed to save image: {str(e)}"}), 500


@app.route('/input/<project>', methods=['POST'])
def api_input(project):
    with sessions_lock:
        session = active_sessions.get(project)
    if not session:
        return jsonify({"error": "Session not found"}), 404
        
    data = request.json.get("data", "")
    session.write(data)
    return jsonify({"status": "ok"})

@app.route('/resize/<project>', methods=['POST'])
def api_resize(project):
    with sessions_lock:
        session = active_sessions.get(project)
    if not session:
        return jsonify({"error": "Session not found"}), 404
        
    cols = request.json.get("cols", 100)
    rows = request.json.get("rows", 30)
    session.resize(cols, rows)
    return jsonify({"status": "ok"})

@app.route('/stream/<project>')
def api_stream(project):
    with sessions_lock:
        session = active_sessions.get(project)
    if not session:
        return Response("Session not found", status=404)
        
    def generate():
        # Yield accumulated terminal history immediately on stream open!
        with session.history_lock:
            history_data = session.history
        if history_data:
            yield f"data: {json.dumps({'data': history_data})}\n\n"
            
        while True:
            try:
                data = session.output_queue.get(timeout=2.0)
                if data is None:
                    yield f"data: {json.dumps({'eof': True})}\n\n"
                    break
                yield f"data: {json.dumps({'data': data})}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
            except Exception:
                break
                
    return Response(stream_with_context(generate()), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

@app.route('/api/project/<project>/git/branches', methods=['GET'])
def api_git_branches(project):
    """List all local and remote branches"""
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())

        # Current branch
        res_cur = subprocess.run(["git", "branch", "--show-current"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        current = (res_cur.stdout or "").strip()

        # All local branches
        res_branches = subprocess.run(["git", "branch"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=5)
        branches = []
        for line in res_branches.stdout.splitlines():
            name = line.strip().lstrip("* ").strip()
            if name:
                branches.append({"name": name, "current": name == current})

        return jsonify({"branches": branches, "current": current})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/branch/create', methods=['POST'])
def api_git_branch_create(project):
    """Create a new branch and switch to it"""
    data = request.get_json() or {}
    branch_name = data.get("branch_name", "").strip()
    if not branch_name:
        return jsonify({"error": "Branch name is required"}), 400
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())

        res = subprocess.run(["git", "checkout", "-b", branch_name], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15)
        output = (res.stdout + res.stderr).strip()
        if res.returncode != 0:
            return jsonify({"success": False, "error": output}), 500
        return jsonify({"success": True, "branch": branch_name, "output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/branch/switch', methods=['POST'])
def api_git_branch_switch(project):
    """Switch to an existing branch"""
    data = request.get_json() or {}
    branch_name = data.get("branch_name", "").strip()
    if not branch_name:
        return jsonify({"error": "Branch name is required"}), 400
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())

        res = subprocess.run(["git", "checkout", branch_name], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15)
        output = (res.stdout + res.stderr).strip()
        if res.returncode != 0:
            return jsonify({"success": False, "error": output}), 500
        return jsonify({"success": True, "branch": branch_name, "output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/branch/merge', methods=['POST'])
def api_git_branch_merge(project):
    """Merge a branch into the current branch"""
    data = request.get_json() or {}
    branch_name = data.get("branch_name", "").strip()
    if not branch_name:
        return jsonify({"error": "Branch name is required"}), 400
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())

        res = subprocess.run(["git", "merge", "--no-ff", branch_name, "-m", f"Merge branch '{branch_name}'"], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=30)
        output = (res.stdout + res.stderr).strip()
        if res.returncode != 0:
            return jsonify({"success": False, "error": output}), 500
        return jsonify({"success": True, "output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project/<project>/git/branch/delete', methods=['POST'])
def api_git_branch_delete(project):
    """Delete a local branch (must not be the current branch)"""
    data = request.get_json() or {}
    branch_name = data.get("branch_name", "").strip()
    force = data.get("force", False)
    if not branch_name:
        return jsonify({"error": "Branch name is required"}), 400
    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404
    path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=2)
        if res_root.returncode != 0:
            return jsonify({"error": "Not a git repository"}), 400
        git_root = os.path.normpath((res_root.stdout or "").strip())

        flag = "-D" if force else "-d"
        res = subprocess.run(["git", "branch", flag, branch_name], cwd=git_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=10)
        output = (res.stdout + res.stderr).strip()
        if res.returncode != 0:
            # If it failed because branch not fully merged, return a specific signal
            if "not fully merged" in output:
                return jsonify({"success": False, "error": output, "not_merged": True}), 409
            return jsonify({"success": False, "error": output}), 500
        return jsonify({"success": True, "output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/open-explorer', methods=['POST'])
def api_open_explorer():
    data = request.json or {}
    path = data.get('path', '')
    if not path or not os.path.isdir(path):
        return jsonify({"status": "error", "message": "Invalid path"}), 400
    import subprocess
    subprocess.Popen(['explorer.exe', os.path.normpath(path)])
    return jsonify({"status": "ok"})

@app.route('/shutdown', methods=['POST'])
def api_shutdown():
    import signal
    print("Shutdown request received, terminating Flask server...")
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({"status": "shutdown"})

# ─────────────────────────────────────────────────────────────────────────────
# WebSocket handlers (namespace /pty)
# ─────────────────────────────────────────────────────────────────────────────

@socketio.on('connect', namespace='/pty')
def ws_connect():
    pass

@socketio.on('disconnect', namespace='/pty')
def ws_disconnect():
    sid = request.sid
    with sessions_lock:
        for session in active_sessions.values():
            session.remove_sid(sid)

@socketio.on('join-session', namespace='/pty')
def ws_join_session(data):
    project = data.get('project')
    pane_id = data.get('paneId', 'main')
    use_real_dir_name = data.get('useRealDirName', False)
    if not project:
        emit('error', {'msg': 'Project name required'})
        return
        
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"] == project), None)
    if not proj_details:
        emit('error', {'msg': 'Project not found'})
        return

    session_key = get_session_key(project, pane_id)
    with sessions_lock:
        if session_key not in active_sessions or not active_sessions[session_key].pty.isalive():
            active_sessions[session_key] = TerminalSession(project, proj_details["path"], use_real_dir_name=use_real_dir_name)
        session = active_sessions[session_key]
        session.add_sid(request.sid)
        
    # Send history immediately
    history = session.get_history()
    if history:
        emit('pty-output', {'data': history})
        
    emit('session-ready', {'name': project, 'paneId': pane_id, 'path': proj_details["path"]})

@socketio.on('pty-input', namespace='/pty')
def ws_pty_input(data):
    project = data.get('project')
    pane_id = data.get('paneId', 'main')
    input_data = data.get('data', '')
    if not project:
        return

    session_key = get_session_key(project, pane_id)
    with sessions_lock:
        session = active_sessions.get(session_key)
    if session and session.pty.isalive():
        session.write(input_data)

@socketio.on('resize', namespace='/pty')
def ws_resize(data):
    project = data.get('project')
    pane_id = data.get('paneId', 'main')
    cols = data.get('cols', 100)
    rows = data.get('rows', 30)
    if not project:
        return

    session_key = get_session_key(project, pane_id)
    with sessions_lock:
        session = active_sessions.get(session_key)
    if session:
        session.resize(cols, rows)

@app.route('/api/extension-icons', methods=['GET'])
def api_get_extension_icons():
    return jsonify(load_extension_icons())

@app.route('/api/extension-icons', methods=['POST'])
def api_post_extension_icons():
    data = request.json or {}
    save_extension_icons(data)
    return jsonify({"status": "success"})

@app.route('/api/fonts')
def list_system_fonts():
    fonts = set()
    
    # Common monospace fonts as baseline presets
    presets = ["Fira Code", "Consolas", "Courier New", "Source Code Pro", "JetBrains Mono", "Cascadia Code", "Hack", "Monaco", "SF Mono", "monospace"]
    for p in presets:
        fonts.add(p)
        
    if sys.platform == 'win32':
        import winreg
        # Query local machine fonts
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
            for i in range(winreg.QueryInfoKey(key)[1]):
                name, _, _ = winreg.EnumValue(key, i)
                clean_name = name.split(" (")[0].strip()
                if clean_name:
                    fonts.add(clean_name)
            winreg.CloseKey(key)
        except Exception:
            pass

        # Query current user fonts
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts")
            for i in range(winreg.QueryInfoKey(key)[1]):
                name, _, _ = winreg.EnumValue(key, i)
                clean_name = name.split(" (")[0].strip()
                if clean_name:
                    fonts.add(clean_name)
            winreg.CloseKey(key)
        except Exception:
            pass

    return jsonify(sorted(list(fonts), key=lambda s: s.lower()))


# ─────────────────────────────────────────────────────────────────────────────
# Scheduled Commands
# ─────────────────────────────────────────────────────────────────────────────

_scheduled = {}          # { id: {...} }
_scheduled_lock = threading.Lock()
_sched_counter = 0

def _next_sched_id():
    global _sched_counter
    _sched_counter += 1
    return str(_sched_counter)

def _run_scheduled(sched_id):
    with _scheduled_lock:
        entry = _scheduled.get(sched_id)
        if not entry or entry["status"] != "pending":
            return
        entry["status"] = "running"
        project = entry["project"]
        pane_id = entry["pane_id"]
        command = entry["command"]
    session_key = get_session_key(project, pane_id)
    with sessions_lock:
        session = active_sessions.get(session_key)
    if session and session.pty.isalive():
        session.write(command + "\r")
        with _scheduled_lock:
            if sched_id in _scheduled:
                _scheduled[sched_id]["status"] = "done"
    else:
        with _scheduled_lock:
            if sched_id in _scheduled:
                _scheduled[sched_id]["status"] = "failed"

@app.route('/api/project/<project>/schedule', methods=['POST'])
def api_schedule_command(project):
    data = request.get_json(silent=True) or {}
    command = (data.get("command") or "").strip()
    pane_id = data.get("pane_id", "main")
    try:
        delay = float(data.get("delay_seconds", 10))
        if delay < 0: delay = 0
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid delay"}), 400
    if not command:
        return jsonify({"error": "Command required"}), 400

    import time as _t
    sched_id = _next_sched_id()
    run_at = _t.time() + delay
    timer = threading.Timer(delay, _run_scheduled, args=[sched_id])
    timer.daemon = True
    with _scheduled_lock:
        _scheduled[sched_id] = {
            "id": sched_id, "project": project, "pane_id": pane_id,
            "command": command, "delay": delay, "run_at": run_at,
            "status": "pending", "timer": timer
        }
    timer.start()
    return jsonify({"id": sched_id, "status": "pending", "delay": delay, "command": command})

@app.route('/api/project/<project>/schedule', methods=['GET'])
def api_list_scheduled(project):
    import time as _t
    now = _t.time()
    with _scheduled_lock:
        items = [
            {"id": v["id"], "command": v["command"], "delay": v["delay"],
             "remaining": max(0.0, round(v["run_at"] - now, 1)), "status": v["status"]}
            for v in _scheduled.values() if v["project"] == project
        ]
    return jsonify({"scheduled": items})

@app.route('/api/project/<project>/schedule/<sched_id>', methods=['DELETE'])
def api_cancel_scheduled(project, sched_id):
    with _scheduled_lock:
        entry = _scheduled.get(sched_id)
        if not entry or entry["project"] != project:
            return jsonify({"error": "Not found"}), 404
        t = entry.get("timer")
        if t: t.cancel()
        entry["status"] = "cancelled"
        del _scheduled[sched_id]
    return jsonify({"success": True})


# ─────────────────────────────────────────────────────────────────────────────
# Quick Tools — grep & file stats
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/api/project/<project>/tools/grep', methods=['POST'])
def api_tools_grep(project):
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    include_pat = (data.get("include") or "*").strip() or "*"
    case_sensitive = bool(data.get("case_sensitive", False))
    max_results = min(int(data.get("max_results", 200)), 500)
    if not query:
        return jsonify({"error": "Query required"}), 400

    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    project_path = os.path.normpath(proj["path"])
    cf = 0x08000000 if sys.platform == "win32" else 0
    try:
        flags = [] if case_sensitive else ["-i"]
        cmd = ["git", "grep", "-n", "--no-color", "-I"] + flags + ["-e", query, "--", include_pat]
        res = subprocess.run(cmd, cwd=project_path, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, creationflags=cf, timeout=15)
        if res.returncode not in (0, 1):
            # fallback: findstr
            fi = "/S /N /P" + ("" if case_sensitive else " /I")
            res2 = subprocess.run(
                f'findstr {fi} "{query}" "{project_path}\\*"',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, creationflags=cf, timeout=15)
            raw = res2.stdout.splitlines()
        else:
            raw = res.stdout.splitlines()

        results = []
        for line in raw[:max_results]:
            parts = line.split(":", 2)
            if len(parts) >= 3:
                results.append({"file": parts[0], "line": parts[1], "text": parts[2]})
            elif len(parts) == 2:
                results.append({"file": parts[0], "line": parts[1], "text": ""})
        return jsonify({"results": results, "total": len(raw)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _human_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

@app.route('/api/project/<project>/tools/stats', methods=['POST'])
def api_tools_stats(project):
    data = request.get_json(silent=True) or {}
    rel = (data.get("path") or "").strip()

    projects_list = scan_projects()
    proj = next((p for p in projects_list if p["name"].lower() == project.lower()), None)
    if not proj:
        return jsonify({"error": "Project not found"}), 404

    base = os.path.normpath(proj["path"])
    full = os.path.normpath(os.path.join(base, rel)) if rel else base
    if not os.path.abspath(full).startswith(os.path.abspath(base)):
        return jsonify({"error": "Path traversal denied"}), 403

    try:
        if os.path.isdir(full):
            files = lines = size = 0
            for root, dirs, fnames in os.walk(full):
                dirs[:] = [d for d in dirs if d not in (".git","node_modules","dist","build","__pycache__")]
                for fn in fnames:
                    fp = os.path.join(root, fn)
                    try:
                        sz = os.path.getsize(fp)
                        size += sz; files += 1
                        if sz < 5_000_000:
                            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                                lines += sum(1 for _ in f)
                    except Exception: pass
            return jsonify({"type":"directory","path":rel or ".","files":files,"lines":lines,
                            "size_bytes":size,"size_human":_human_size(size)})
        else:
            sz = os.path.getsize(full)
            lc = wc = cc = 0
            if sz < 10_000_000:
                with open(full,"r",encoding="utf-8",errors="ignore") as f:
                    content = f.read()
                lc = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
                wc = len(content.split())
                cc = len(content)
            return jsonify({"type":"file","path":rel,"lines":lc,"words":wc,"chars":cc,
                            "size_bytes":sz,"size_human":_human_size(sz)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools/kill', methods=['POST'])
def api_tools_kill():
    """Kill a process by PID or name"""
    import signal as _signal
    import re as _re
    data = request.get_json(silent=True) or {}
    target = str(data.get("target", "")).strip()
    if not target:
        return jsonify({"error": "No PID or name provided"}), 400

    cf = 0x08000000 if sys.platform == "win32" else 0
    killed = []
    errors = []

    if target.isdigit():
        # Kill by PID
        pid = int(target)
        try:
            if sys.platform == "win32":
                res = subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, creationflags=cf)
                if res.returncode == 0:
                    killed.append(f"PID {pid}")
                else:
                    errors.append((res.stderr or "").strip() or f"Failed to kill PID {pid}")
            else:
                os.kill(pid, _signal.SIGKILL)
                killed.append(f"PID {pid}")
        except Exception as e:
            errors.append(str(e))
    else:
        # Kill by name
        if sys.platform == "win32":
            # Use tasklist to find all matching PIDs (case-insensitive, partial match)
            try:
                tl = subprocess.run(["tasklist", "/FO", "CSV", "/NH"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, creationflags=cf)
                matched_pids = []
                for line in (tl.stdout or "").strip().splitlines():
                    # CSV format: "name.exe","pid","session","session#","mem"
                    parts = [p.strip('"') for p in line.split('","')]
                    if len(parts) >= 2:
                        proc_name = parts[0]
                        proc_pid  = parts[1]
                        # Match if target appears anywhere in the process name (case-insensitive)
                        if target.lower() in proc_name.lower():
                            matched_pids.append((proc_pid, proc_name))

                if not matched_pids:
                    errors.append(f'No process matching "{target}" found')
                else:
                    for proc_pid, proc_name in matched_pids:
                        res = subprocess.run(["taskkill", "/F", "/PID", proc_pid],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             text=True, creationflags=cf)
                        if res.returncode == 0:
                            killed.append(f"{proc_name} (PID {proc_pid})")
                        else:
                            errors.append((res.stderr or "").strip() or f"Failed to kill PID {proc_pid}")
            except Exception as e:
                errors.append(str(e))
        else:
            try:
                res = subprocess.run(["pkill", "-9", "-f", target],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True)
                if res.returncode == 0:
                    killed.append(f'"{target}" (matching processes)')
                else:
                    errors.append(f'No process matching "{target}" found')
            except Exception as e:
                errors.append(str(e))

    if killed:
        return jsonify({"success": True, "killed": killed, "errors": errors})
    else:
        return jsonify({"success": False, "killed": [], "errors": errors}), 500


@app.route('/api/tools/port', methods=['POST'])
def api_tools_port():
    """Check what process is using a port, or list all listening ports"""
    import re as _re
    data = request.get_json(silent=True) or {}
    port_filter = str(data.get("port", "")).strip()
    cf = 0x08000000 if sys.platform == "win32" else 0

    try:
        if sys.platform == "win32":
            res = subprocess.run(
                ["netstat", "-ano"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding='utf-8', errors='replace', creationflags=cf
            )
            lines = (res.stdout or "").splitlines()
            # Get pid→name map from tasklist
            tl = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding='utf-8', errors='replace', creationflags=cf
            )
            pid_names = {}
            for tline in (tl.stdout or "").splitlines():
                parts = [p.strip('"') for p in tline.split('","')]
                if len(parts) >= 2:
                    pid_names[parts[1]] = parts[0]

            ports = []
            seen = set()
            for line in lines:
                # TCP    0.0.0.0:8080    0.0.0.0:0    LISTENING    1234
                m = _re.match(r'\s*(TCP|UDP)\s+[\d\.\[\]:*]+:(\d+)\s+[\d\.\[\]:*:*]+\s+(\w+)\s+(\d+)', line)
                if not m:
                    # UDP has no state column
                    m = _re.match(r'\s*(UDP)\s+[\d\.\[\]:*]+:(\d+)\s+[\d\.\[\]:*:*]+\s+(\d+)', line)
                    if m:
                        proto, port, pid = m.group(1), m.group(2), m.group(3)
                        state = 'UDP'
                    else:
                        continue
                else:
                    proto, port, state, pid = m.group(1), m.group(2), m.group(3), m.group(4)

                if port_filter and port != port_filter:
                    continue
                if state not in ('LISTENING', 'UDP') and port_filter == '':
                    continue  # when listing all, only show listening
                key = (port, pid)
                if key in seen:
                    continue
                seen.add(key)
                proc = pid_names.get(pid, 'Unknown')
                ports.append({"port": port, "state": state, "pid": pid, "process": proc, "proto": proto})

        else:
            # Linux/Mac — use ss or netstat
            res = subprocess.run(
                ["ss", "-tlnup"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, errors='replace'
            )
            lines = (res.stdout or "").splitlines()
            ports = []
            for line in lines[1:]:  # skip header
                parts = line.split()
                if len(parts) < 5:
                    continue
                # Local address is parts[4], format 0.0.0.0:PORT or *:PORT
                addr = parts[4]
                m = _re.search(r':(\d+)$', addr)
                if not m:
                    continue
                port = m.group(1)
                if port_filter and port != port_filter:
                    continue
                # Extract pid/process from users:(("name",pid=X,...))
                proc = 'Unknown'
                pid = '-'
                if len(parts) > 6:
                    pm = _re.search(r'"([^"]+)",pid=(\d+)', parts[-1])
                    if pm:
                        proc, pid = pm.group(1), pm.group(2)
                ports.append({"port": port, "state": "LISTENING", "pid": pid, "process": proc, "proto": "TCP"})

        # Sort by port number
        ports.sort(key=lambda x: int(x["port"]))
        return jsonify({"ports": ports})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


SNIPPETS_FILE = r"C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\snippets.json"

@app.route('/api/snippets', methods=['GET'])
def api_get_snippets():
    """Return saved snippets list"""
    try:
        if os.path.exists(SNIPPETS_FILE):
            with open(SNIPPETS_FILE, 'r', encoding='utf-8') as f:
                return jsonify({"snippets": json.load(f)})
        return jsonify({"snippets": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/snippets', methods=['POST'])
def api_save_snippets():
    """Save full snippets list"""
    data = request.get_json(silent=True) or {}
    snippets = data.get("snippets", [])
    try:
        os.makedirs(os.path.dirname(SNIPPETS_FILE), exist_ok=True)
        with open(SNIPPETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, ensure_ascii=False, indent=2)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    debug_enabled = os.environ.get("TERMINAL_TUI_DEBUG") == "1"
    
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    print(f"\n * Running on local address: http://127.0.0.1:{PORT}/")
    if local_ip != "127.0.0.1":
        print(f" * Running on network address: http://{local_ip}:{PORT}/\n")

    socketio.run(
        app,
        host='0.0.0.0',
        port=PORT,
        debug=debug_enabled,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
