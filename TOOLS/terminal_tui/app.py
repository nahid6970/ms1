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
active_sessions = {}
sessions_lock = threading.Lock()


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
    def __init__(self, name, path):
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
        
        if not os.path.exists(profile_path):
            with open(profile_path, "w", encoding="utf-8") as f:
                f.write(f"""# Custom PowerShell Profile for project: {name}
# Everything here is loaded when you select this project workspace dashboard.

# Force import PSReadLine in case it is disabled due to screen reader detection in PTY
Import-Module PSReadLine -ErrorAction SilentlyContinue

# Set custom project command history file
if (Get-Command Set-PSReadLineOption -ErrorAction SilentlyContinue) {{
    Set-PSReadLineOption -HistorySavePath "{history_path}"
}}

# Custom prompt
function prompt {{
    "COMMAND> "
}}

# Clear screen cleanly to start with a clean prompt and hide startup warnings
Write-Host "$([char]0x1b)[2J$([char]0x1b)[H" -NoNewline

# Add your custom project aliases, functions, and environment variables below:
# Example:
# Set-Alias ll Get-ChildItem
""")
        else:
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    content = f.read()
                modified = False
                if "Clear-Host" in content:
                    content = content.replace("Clear-Host", 'Write-Host "$([char]0x1b)[2J$([char]0x1b)[H" -NoNewline')
                    modified = True
                if "PROFILE_LOADED_OK" in content:
                    content = content.replace('Write-Host "PROFILE_LOADED_OK"', '')
                    content = content.replace('echo "PROFILE_LOADED_OK"', '')
                    modified = True
                if "function prompt" not in content:
                    content += "\n\n# Custom prompt\nfunction prompt {\n    \"COMMAND> \"\n}\n"
                    modified = True
                if modified:
                    with open(profile_path, "w", encoding="utf-8") as f:
                        f.write(content)
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
            "cursor": "#3b82f6"
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
            "cursor": "#3b82f6"
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
        proj["bookmarks"].append({"command": command, "global": False, "windowTitle": window_title})
        
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
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"] == project), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404

    session_key = get_session_key(project, pane_id)
    with sessions_lock:
        if session_key not in active_sessions or not active_sessions[session_key].pty.isalive():
            active_sessions[session_key] = TerminalSession(project, proj_details["path"])
            
    return jsonify({
        "status": "connected",
        "name": project,
        "paneId": pane_id,
        "path": proj_details["path"]
    })

@app.route('/api/session/<project>/paste-image', methods=['POST'])
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
            active_sessions[session_key] = TerminalSession(project, proj_details["path"])
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

if __name__ == '__main__':
    debug_enabled = os.environ.get("TERMINAL_TUI_DEBUG") == "1"
    socketio.run(
        app,
        host='127.0.0.1',
        port=PORT,
        debug=debug_enabled,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
