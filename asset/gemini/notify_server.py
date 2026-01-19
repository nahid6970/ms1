import sys
import json
import logging
import platform

# Configure logging to stderr so it doesn't corrupt stdout
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def notify(message="Task Completed"):
    try:
        if platform.system() == "Windows":
            import winsound
            import os
            import tempfile
            import subprocess

            # 1. Play system alert sound (non-blocking)
            winsound.PlaySound("SystemExit", winsound.SND_ALIAS | winsound.SND_ASYNC)
            winsound.Beep(1000, 300)

            # 2. BLOCKING Popup via VBScript
            # We use 'cscript' and a small loop to ensure the process blocks Python
            # until either the user clicks OK or the CLI kills the process.
            safe_message = str(message).replace('"', '""').replace("\n", " ")
            vbs_content = (
                f'Set ws = CreateObject("WScript.Shell")\n'
                f'ws.Popup "{safe_message}", 0, "Gemini Task Complete", 64\n'
            )
            
            vbs_path = os.path.join(tempfile.gettempdir(), "gemini_block.vbs")
            with open(vbs_path, "w") as f:
                f.write(vbs_content)
            
            # subprocess.run will wait for the VBScript to finish.
            # When the user hits ESC in the terminal, the CLI terminates this server call.
            logging.info("Blocking for user interaction...")
            subprocess.run(["wscript.exe", vbs_path], check=False)
            
        else:
            # Generic fallback for other OS
            sys.stderr.write("\a")
            import time
            time.sleep(5)
    except Exception as e:
        logging.error(f"Failed to notify: {e}")

def run_server():
    logging.info("Notify MCP Server running...")
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
                        "name": "notify-server",
                        "version": "1.0.0"
                    }
                }
            
            elif method == "notifications/initialized":
                continue
                
            elif method == "tools/list":
                response = {
                    "tools": [
                        {
                            "name": "run_blocking_notification_script",
                            "description": "Your Job is Done & to notify the user run the script it sends a notification.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {
                                        "type": "string",
                                        "description": "Short summary of the task completed."
                                    }
                                }
                            }
                        }
                    ]
                }
            
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments", {})
                
                if name == "run_blocking_notification_script":
                    msg = args.get("message", "Task Complete")
                    notify(msg)
                    # This code is actually not reached because notify() blocks with sleep.
                    response = {
                        "content": [{"type": "text", "text": " "}],
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
