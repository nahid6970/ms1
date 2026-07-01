import os
import sys
import json
import asyncio
import subprocess
import traceback
from winpty import PTY
import pyte

PORT = 9988
BASE_DIR = r"C:\@delta\ms1\TOOLS"
LOG_FILE = r"C:\@delta\ms1\TOOLS\terminal_tui\server.log"

active_sessions = {}
active_project = None
active_client_writer = None
cols = 100
rows = 30

# Caching for git branches
git_branch_cache = {}

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")

def get_project_list():
    try:
        entries = os.listdir(BASE_DIR)
        projects = []
        for entry in entries:
            path = os.path.join(BASE_DIR, entry)
            if os.path.isdir(path):
                # Filter out standard non-project folders
                if entry.startswith(".") or entry.startswith("_"):
                    continue
                if entry in ("__pycache__", "ENV", "node_modules", "DesktopOK"):
                    continue
                projects.append(entry)
        return sorted(projects)
    except Exception as e:
        log(f"Error getting project list: {e}")
        return []

def get_project_info(name):
    path = os.path.join(BASE_DIR, name)
    rel_path = path
    if path.lower().startswith(r"c:\users\nahid"):
        rel_path = "~" + path[len(r"c:\users\nahid"):].replace("\\", "/")
    else:
        # standard display
        rel_path = path.replace("\\", "/")
        
    branch = git_branch_cache.get(name)
    if branch is None:
        branch = ""
        try:
            if os.path.exists(os.path.join(path, ".git")):
                res = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=0.5
                )
                branch = res.stdout.strip()
                git_branch_cache[name] = branch
        except Exception:
            pass
            
    session = active_sessions.get(name)
    status = ""
    if session:
        status = session.get("last_line", "")
        if not session["pty"].isalive():
            status = "[Exited - Enter to restart]"
            
    return {
        "path": rel_path,
        "branch": branch,
        "status": status
    }

async def read_msg(reader):
    try:
        header = await reader.readexactly(4)
        length = int.from_bytes(header, byteorder="big")
        data = await reader.readexactly(length)
        return json.loads(data.decode("utf-8"))
    except (asyncio.IncompleteReadError, ConnectionError):
        return None

async def write_msg(writer, msg):
    try:
        data = json.dumps(msg).encode("utf-8")
        header = len(data).to_bytes(4, byteorder="big")
        writer.write(header + data)
        await writer.drain()
    except ConnectionError:
        pass

def serialize_screen(screen):
    lines = []
    for y in range(screen.lines):
        line = []
        row = screen.buffer[y]
        for x in range(screen.columns):
            cell = row[x]
            line.append((
                cell.data,
                cell.fg,
                cell.bg,
                cell.bold,
                cell.italics,
                bool(cell.underscore)
            ))
        lines.append(line)
    return {
        "lines": lines,
        "cursor_x": screen.cursor.x,
        "cursor_y": screen.cursor.y,
        "cursor_hidden": screen.cursor.hidden
    }

async def send_screen_update():
    global active_client_writer, active_project
    if not active_client_writer or not active_project:
        return
    session = active_sessions.get(active_project)
    if not session:
        return
        
    msg = {
        "type": "screen_update",
        "project": active_project,
        "screen": serialize_screen(session["screen"])
    }
    await write_msg(active_client_writer, msg)

async def send_status_update():
    global active_client_writer
    if not active_client_writer:
        return
    projects = get_project_list()
    proj_details = {name: get_project_info(name) for name in projects}
    msg = {
        "type": "status_update",
        "projects": proj_details,
        "active_project": active_project
    }
    await write_msg(active_client_writer, msg)

async def pty_reader_loop(name):
    log(f"Starting PTY reader loop for {name}")
    session = active_sessions.get(name)
    if not session:
        return
    pty = session["pty"]
    stream = session["stream"]
    screen = session["screen"]
    loop = asyncio.get_running_loop()
    
    while pty.isalive():
        try:
            # Use blocking=True so the background executor thread blocks until new data is available.
            # This completely eliminates idle CPU consumption and polling latency!
            data = await loop.run_in_executor(None, lambda: pty.read(blocking=True))
            if data:
                stream.feed(data)
                
                # Get last non-empty line (scan backwards for speed)
                last_line = ""
                for y in range(screen.lines - 1, -1, -1):
                    line_chars = [screen.buffer[y][x].data for x in range(screen.columns)]
                    line_str = "".join(line_chars).strip()
                    if line_str:
                        last_line = line_str
                        break
                session["last_line"] = last_line
                    
                if name == active_project:
                    await send_screen_update()
            else:
                break
        except Exception as e:
            log(f"Error in pty_reader_loop for {name}: {e}")
            break
            
    log(f"PTY for {name} exited.")
    session["last_line"] = "[Exited - Enter to restart]"
    if name == active_project:
        await send_screen_update()
    await send_status_update()

def spawn_project_session(name):
    if name in active_sessions:
        # Check if still alive
        if active_sessions[name]["pty"].isalive():
            return active_sessions[name]
            
    log(f"Spawning session for {name}")
    path = os.path.join(BASE_DIR, name)
    pty = PTY(cols, rows)
    
    # Spawn PowerShell
    shell = "powershell.exe"
    pty.spawn(shell, cwd=path)
    
    screen = pyte.Screen(cols, rows)
    stream = pyte.Stream(screen)
    
    session = {
        "name": name,
        "pty": pty,
        "screen": screen,
        "stream": stream,
        "last_line": "Session started.",
        "reader_task": None
    }
    active_sessions[name] = session
    session["reader_task"] = asyncio.create_task(pty_reader_loop(name))
    return session

async def handle_client(reader, writer):
    global active_client_writer, active_project, cols, rows
    log("Client connected")
    active_client_writer = writer
    
    try:
        # Initialize default project if none is active
        projects = get_project_list()
        if projects:
            if active_project not in projects:
                active_project = projects[0]
            spawn_project_session(active_project)
            
        await send_status_update()
        await send_screen_update()
        
        while True:
            msg = await read_msg(reader)
            if not msg:
                break
                
            msg_type = msg.get("type")
            if msg_type == "keypress":
                session = active_sessions.get(active_project)
                if session:
                    # Write to PTY
                    data = msg.get("data", "")
                    if session["pty"].isalive():
                        session["pty"].write(data)
                    else:
                        # If exited and user hits enter, restart session
                        if data == "\r":
                            spawn_project_session(active_project)
                            await send_status_update()
                            await send_screen_update()
                            
            elif msg_type == "resize":
                new_cols = msg.get("cols", cols)
                new_rows = msg.get("rows", rows)
                if new_cols != cols or new_rows != rows:
                    cols = new_cols
                    rows = new_rows
                    log(f"Resizing active session to {cols}x{rows}")
                    session = active_sessions.get(active_project)
                    if session:
                        if session["pty"].isalive():
                            session["pty"].set_size(cols, rows)
                        session["screen"].resize(rows, cols)
                        await send_screen_update()
                        
            elif msg_type == "switch_project":
                proj = msg.get("project")
                projects = get_project_list()
                if proj in projects:
                    active_project = proj
                    log(f"Switched project to {active_project}")
                    session = spawn_project_session(active_project)
                    # Resize the newly active session to the client's current size
                    if session["pty"].isalive():
                        session["pty"].set_size(cols, rows)
                    session["screen"].resize(rows, cols)
                    await send_status_update()
                    await send_screen_update()
                    
            elif msg_type == "refresh_branches":
                # Clear branch cache to force reload
                git_branch_cache.clear()
                await send_status_update()
                
            elif msg_type == "shutdown":
                log("Shutdown command received")
                import os
                os._exit(0)
                
    except Exception as e:
        log(f"Exception handling client: {e}\n{traceback.format_exc()}")
    finally:
        log("Client disconnected")
        if active_client_writer == writer:
            active_client_writer = None

async def main():
    # Clear log
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("Server started\n")
        
    server = await asyncio.start_server(handle_client, "127.0.0.1", PORT)
    addr = server.sockets[0].getsockname()
    log(f"Serving on {addr}")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped via KeyboardInterrupt")
    except Exception as e:
        log(f"Server crashed: {e}")
