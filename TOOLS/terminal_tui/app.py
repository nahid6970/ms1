import os
import sys
import json
import queue
import threading
import subprocess
import webbrowser
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from winpty import PTY

app = Flask(__name__)

PORT = 5577
BASE_DIR = r"C:\@delta\ms1\TOOLS"
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
        
        # Spawn PowerShell
        self.pty.spawn("powershell.exe", cwd=path)
        
        self.output_queue = queue.Queue()
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()
        
    def _read_loop(self):
        while self.pty.isalive():
            try:
                # Read blocking is extremely CPU friendly
                data = self.pty.read(blocking=True)
                if data:
                    self.output_queue.put(data)
                else:
                    break
            except Exception:
                break
        self.output_queue.put(None) # Signal EOF

    def write(self, data):
        if self.pty.isalive():
            self.pty.write(data)

    def resize(self, cols, rows):
        if self.cols != cols or self.rows != rows:
            self.cols = cols
            self.rows = rows
            if self.pty.isalive():
                self.pty.set_size(cols, rows)

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
    projects = []
    try:
        entries = os.listdir(BASE_DIR)
        for entry in entries:
            path = os.path.join(BASE_DIR, entry)
            if os.path.isdir(path):
                if entry.startswith(".") or entry.startswith("_"):
                    continue
                if entry in ("__pycache__", "ENV", "node_modules", "DesktopOK"):
                    continue
                
                # Fetch/Cache git branch
                branch = git_branch_cache.get(entry)
                if branch is None:
                    branch = get_git_branch(path)
                    git_branch_cache[entry] = branch
                    
                with sessions_lock:
                    is_active = entry in active_sessions and active_sessions[entry].pty.isalive()
                    
                projects.append({
                    "name": entry,
                    "path": path.replace("\\", "/"),
                    "branch": branch,
                    "is_active": is_active
                })
        projects.sort(key=lambda x: x["name"].lower())
    except Exception as e:
        print(f"Error scanning projects: {e}")
    return projects

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/projects', methods=['GET'])
def api_projects():
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
        while True:
            try:
                # Timeout so the loop can check for disconnected clients occasionally
                data = session.output_queue.get(timeout=2.0)
                if data is None:
                    # EOF
                    yield f"data: {json.dumps({'eof': True})}\n\n"
                    break
                yield f"data: {json.dumps({'data': data})}\n\n"
            except queue.Empty:
                # Yield heartbeat to keep connection alive
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
            except Exception as e:
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
    print(f"Starting Workspace Manager on http://localhost:{PORT}")
    app.run(host='127.0.0.1', port=PORT, debug=False)
