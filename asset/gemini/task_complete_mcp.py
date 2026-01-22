import sys
import json
import logging
import subprocess
import os
import time

# Configure logging to stderr so it doesn't corrupt stdout
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def show_notification():
    """Launch the PyQt6 task complete notification (non-blocking) then block with pause"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        task_complete_path = os.path.join(script_dir, "task_complete.py")
        
        logging.info("Launching task complete notification (non-blocking)...")
        
        # Launch the GUI with Popen (non-blocking, so it shows immediately)
        subprocess.Popen([sys.executable, task_complete_path], 
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        
        logging.info("Notification launched, now blocking AI with pause command...")
        
        # Now block the AI by running a pause command
        # This will wait until user presses a key
        subprocess.run(["cmd", "/c", "pause"], 
                      shell=False,
                      creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0)
        
        logging.info("User acknowledged, continuing...")
        return True
    except Exception as e:
        logging.error(f"Failed to show notification: {e}")
        return False

def run_server():
    logging.info("Task Complete MCP Server running...")
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue

            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})
            
            response = None
            
            if method == "initialize":
                response = {
                    "protocolVersion": "2024-11-05", 
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "task-complete-server",
                        "version": "1.0.0"
                    }
                }
            
            elif method == "notifications/initialized":
                continue
                
            elif method == "tools/list":
                response = {
                    "tools": [
                        {
                            "name": "show_task_complete_notification",
                            "description": "Shows a cyberpunk-styled notification popup to alert the user that the AI task is complete. Call this as the LAST action after finishing your work.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                }
            
            elif method == "tools/call":
                name = params.get("name")
                
                if name == "show_task_complete_notification":
                    # Popen shows notification, then subprocess.run blocks
                    success = show_notification()
                    response = {
                        "content": [{"type": "text", "text": ""}],
                        "isError": False
                    }
                else:
                    raise ValueError(f"Unknown tool: {name}")

            if response is not None and req_id is not None:
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": response
                }) + "\n")
                sys.stdout.flush()

        except Exception as e:
            logging.error(f"Error handling request: {e}")
            if req_id is not None:
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": str(e)}
                }) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    run_server()
