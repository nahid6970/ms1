import os
import sys
import socket
import subprocess
import time
import json

PORT = 9988
SERVER_SCRIPT = r"C:\@delta\ms1\TOOLS\terminal_tui\tui_server.py"
CLIENT_SCRIPT = r"C:\@delta\ms1\TOOLS\terminal_tui\tui_client.py"

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
        print(f"Error starting background server: {e}")
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
        s = socket.create_connection(("127.0.0.1", PORT), timeout=1.0)
        # Send shutdown command
        msg = {"type": "shutdown"}
        data = json.dumps(msg).encode("utf-8")
        header = len(data).to_bytes(4, byteorder="big")
        s.sendall(header + data)
        s.close()
        print("Shutdown command sent to terminal server.")
    except Exception as e:
        print(f"Error sending shutdown command: {e}")

def run_client():
    # Run the client in the current terminal process
    try:
        subprocess.run([sys.executable, CLIENT_SCRIPT])
    except KeyboardInterrupt:
        pass

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ("stop", "kill", "shutdown", "--kill"):
            kill_server()
            return
        elif cmd in ("status", "--status"):
            if is_server_running():
                print("Terminal server is running in the background.")
            else:
                print("Terminal server is not running.")
            return
        elif cmd in ("help", "--help", "-h"):
            print("Terminal TUI Manager")
            print("Usage:")
            print("  python main.py           - Start client and connect to server (starts server if needed)")
            print("  python main.py stop      - Stop the background server and all active terminal sessions")
            print("  python main.py status    - Check if background server is running")
            return

    # Default action: start server and run client
    print("Checking background terminal server...")
    if not start_server():
        print("Error: Could not start or connect to the terminal server.")
        sys.exit(1)
        
    run_client()

if __name__ == "__main__":
    main()
