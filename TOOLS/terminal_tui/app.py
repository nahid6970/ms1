import os
import sys
import json
import queue
import threading
import subprocess
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from winpty import PTY

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

PORT = 5577
BASE_DIR = r"C:\@delta\ms1\TOOLS"
PROJECTS_FILE = r"C:\@delta\ms1\TOOLS\terminal_tui\projects.json"
active_sessions = {}
git_branch_cache = {}
sessions_lock = threading.Lock()
class TerminalSession:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.cols = 100
        self.rows = 30
        self.pty = PTY(self.cols, self.rows)
        self.history = ""
        self.history_lock = threading.Lock()
        
        # Ensure project-specific data directory exists in C:\@delta\ms1\TOOLS\terminal_tui\Project_data\<project>
        project_data_dir = os.path.join(r"C:\@delta\ms1\TOOLS\terminal_tui\Project_data", name)
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
        
        self.output_queue = queue.Queue()
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()
        
    def _read_loop(self):
        while self.pty.isalive():
            try:
                data = self.pty.read(blocking=True)
                if data:
                    with self.history_lock:
                        self.history += data
                        if len(self.history) > 100000:
                            self.history = self.history[-100000:]
                    self.output_queue.put(data)
                else:
                    break
            except Exception:
                break
        self.output_queue.put(None)

    def write(self, data):
        if self.pty.isalive():
            self.pty.write(data)

    def resize(self, cols, rows):
        if self.cols != cols or self.rows != rows:
            self.cols = cols
            self.rows = rows
            if self.pty.isalive():
                self.pty.set_size(cols, rows)

def load_projects_config():
    if os.path.exists(PROJECTS_FILE):
        try:
            with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading projects config: {e}")
    return []

def save_projects_config(projects):
    try:
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2)
    except Exception as e:
        print(f"Error saving projects config: {e}")

def get_git_branch(path):
    try:
        if os.path.exists(os.path.join(path, ".git")):
            res = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=0.5
            )
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def scan_projects():
    config_projects = load_projects_config()
    projects = []
    for p in config_projects:
        name = p["name"]
        path = p["path"]
        pinned = p.get("pinned", False)
        theme = p.get("theme", {
            "background": "#000000",
            "foreground": "#d1d5db",
            "cursor": "#3b82f6"
        })
        card_theme = p.get("cardTheme", {
            "bgColor": "#161c26",
            "textColor": "#f1f5f9",
            "pathColor": "#94a3b8",
            "accentColor": "#2563eb"
        })
        if "pathColor" not in card_theme:
            card_theme["pathColor"] = "#94a3b8"
        
        # Fetch/Cache git branch
        branch = git_branch_cache.get(name)
        if branch is None:
            branch = get_git_branch(path)
            git_branch_cache[name] = branch
            
        with sessions_lock:
            is_active = name in active_sessions and active_sessions[name].pty.isalive()
            
        projects.append({
            "name": name,
            "path": path.replace("\\", "/"),
            "branch": branch,
            "is_active": is_active,
            "pinned": pinned,
            "theme": theme,
            "cardTheme": card_theme
        })
    return projects

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/projects', methods=['GET'])
def api_projects_get():
    refresh = request.args.get("refresh") == "true"
    if refresh:
        global git_branch_cache
        git_branch_cache = {}
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
        
    # Add project
    projects.append({
        "name": name,
        "path": os.path.abspath(path),
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
        }
    })
    save_projects_config(projects)
    
    # Force git branch cache refresh for this project
    git_branch_cache[name] = get_git_branch(path)
    
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
        if project in active_sessions:
            session = active_sessions[project]
            if session.pty.isalive():
                try:
                    os.close(session.pty.fd)
                except Exception:
                    pass
            del active_sessions[project]
            
    if project in git_branch_cache:
        del git_branch_cache[project]
        
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
            
    # If path is changing, check if folder exists
    path_changed = new_path and new_path != proj["path"]
    if path_changed:
        if not os.path.exists(new_path) or not os.path.isdir(new_path):
            return jsonify({"error": f"The directory path '{new_path}' does not exist."}), 400
            
    # Terminate active session if name or path changed, so it starts fresh!
    if name_changed or path_changed:
        with sessions_lock:
            if original_name in active_sessions:
                session = active_sessions[original_name]
                if session.pty.isalive():
                    try:
                        os.close(session.pty.fd)
                    except Exception:
                        pass
                del active_sessions[original_name]
                
        # Clear old branch cache
        if original_name in git_branch_cache:
            del git_branch_cache[original_name]
            
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
    if "theme" in data:
        proj["theme"] = data["theme"]
    if "cardTheme" in data:
        proj["cardTheme"] = data["cardTheme"]
        
    save_projects_config(projects)
    
    # Refresh cache branch for the project
    if name_changed or path_changed:
        git_branch_cache[proj["name"]] = get_git_branch(proj["path"])
        
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

@app.route('/api/sessions/reset', methods=['POST'])
def api_sessions_reset():
    with sessions_lock:
        for name, session in list(active_sessions.items()):
            if session.pty.isalive():
                try:
                    os.close(session.pty.fd)
                except Exception:
                    pass
        active_sessions.clear()
        
    global git_branch_cache
    git_branch_cache = {}
    
    return jsonify(scan_projects())

@app.route('/api/session/<project>', methods=['POST'])
def api_session(project):
    projects = scan_projects()
    proj_details = next((p for p in projects if p["name"] == project), None)
    if not proj_details:
        return jsonify({"error": "Project not found"}), 404
        
    with sessions_lock:
        if project not in active_sessions or not active_sessions[project].pty.isalive():
            active_sessions[project] = TerminalSession(project, proj_details["path"])
            
    return jsonify({
        "status": "connected",
        "name": project,
        "path": proj_details["path"],
        "branch": proj_details["branch"]
    })

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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PORT, debug=True)
