import os
import sys
import socket
import subprocess
import time
import urllib.request
import urllib.error
import webbrowser

PORT = 5577
SERVER_URL = f"http://127.0.0.1:{PORT}"
SERVER_SCRIPT = r"C:\@delta\ms1\TOOLS\terminal_tui\app.py"

def is_server_running():
    try:
        s = socket.create_connection(("127.0.0.1", PORT), timeout=0.5)
        s.close()
        return True
    except OSError:
        return False

def start_server():
    if is_server_running():
        return True
        
    # Start the server process in the background without console window
    # CREATE_NO_WINDOW = 0x08000000
    # DETACHED_PROCESS = 0x00000008
    creationflags = 0x08000000 | 0x00000008
    
    try:
        subprocess.Popen(
            [sys.executable, SERVER_SCRIPT],
            creationflags=creationflags,
            cwd=r"C:\@delta\ms1\TOOLS\terminal_tui",
            close_fds=True
        )
    except Exception as e:
        print(f"Error starting background Flask server: {e}")
        return False
        
    # Wait for connection to be available
    for _ in range(30):
        if is_server_running():
            return True
        time.sleep(0.1)
    return False

def kill_server():
    if not is_server_running():
        print("Server is not running.")
        return
        
    try:
        # Send shutdown POST request
        req = urllib.request.Request(
            f"{SERVER_URL}/shutdown", 
            data=b"{}", 
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=2.0) as response:
            res = response.read().decode("utf-8")
            print("Shutdown command sent successfully to workspace server.")
    except Exception as e:
        # The request might fail because the server exits immediately and closes connection, which is normal
        print("Shutdown command triggered (server process terminated).")

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ("stop", "kill", "shutdown", "--kill"):
            kill_server()
            return
        elif cmd in ("status", "--status"):
            if is_server_running():
                print("Workspace server is running in the background.")
            else:
                print("Workspace server is not running.")
            return
        elif cmd in ("help", "--help", "-h"):
            print("Workspace Web Dashboard Launcher")
            print("Usage:")
            print("  python main.py           - Start server and open dashboard in your web browser")
            print("  python main.py stop      - Stop the background server and all active PTY shell sessions")
            print("  python main.py status    - Check if the background server is running")
            return

    # Default action: start server and open web browser
    print("Checking workspace server...")
    if not start_server():
        print("Error: Could not start or connect to the workspace server.")
        sys.exit(1)
        
    print(f"Opening Workspace Dashboard in browser: {SERVER_URL}")
    webbrowser.open(SERVER_URL)

if __name__ == "__main__":
    main()
