import sys
import os
import json
import subprocess

def add_to_history(command, shell):
    # Centralized database path
    history_file = "C:\\@delta\\db\\FZF_launcher\\command_history.json"
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
            
    # Remove if exists to move to top
    history = [h for h in history if h['command'] != command]
    history.insert(0, {"command": command, "shell": shell})
    
    # Keep last 100
    history = history[:100]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def run_command(command, shell):
    add_to_history(command, shell)
    
    if shell == "cmd":
        # /k keeps the window open
        subprocess.run(['start', 'cmd', '/k', command], shell=True)
    elif shell == "powershell":
        subprocess.run(['start', 'powershell', '-NoExit', '-Command', command], shell=True)
    elif shell == "pwsh":
        subprocess.run(['start', 'pwsh', '-NoExit', '-Command', command], shell=True)
    else:
        # Default to pwsh if unknown
        subprocess.run(['start', 'pwsh', '-NoExit', '-Command', command], shell=True)

if __name__ == "__main__":
    if len(sys.argv) > 3:
        # Expected: python executor.py <requested_shell> <selection> <query> <stored_shell>
        req_shell = sys.argv[1]
        selection = sys.argv[2].strip()
        query = sys.argv[3].strip()
        stored_shell = sys.argv[4] if len(sys.argv) > 4 else "pwsh"
        
        command = selection if selection else query
        if not command:
            sys.exit(0)
            
        shell = stored_shell if (req_shell == "auto" and selection) else req_shell
        if shell == "auto": shell = "pwsh"
        
        run_command(command, shell)
