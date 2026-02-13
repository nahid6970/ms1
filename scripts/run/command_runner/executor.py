import sys
import os
import json
import subprocess

# Centralized database path
HISTORY_FILE = r"C:\@delta\db\FZF_launcher\command_history.json"

def add_to_history(command, shell):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
            
    # Remove if exists to move to top
    history = [h for h in history if h['command'] != command]
    history.insert(0, {"command": command, "shell": shell})
    
    # Keep last 100
    history = history[:100]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def run_command(command, shell):
    add_to_history(command, shell)
    
    # Launch the terminal in a decoupled way
    # Using a list with Popen is much safer than a string with shell=True
    if shell == "cmd":
        # cmd /c start cmd /k "command"
        subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', command])
    elif shell == "powershell":
        # start powershell -NoExit -Command "& { command }"
        ps_cmd = f"& {{ {command} }}"
        subprocess.Popen(['cmd', '/c', 'start', 'powershell', '-NoExit', '-Command', ps_cmd])
    elif shell == "pwsh":
        ps_cmd = f"& {{ {command} }}"
        subprocess.Popen(['cmd', '/c', 'start', 'pwsh', '-NoExit', '-Command', ps_cmd])
    else:
        ps_cmd = f"& {{ {command} }}"
        subprocess.Popen(['cmd', '/c', 'start', 'pwsh', '-NoExit', '-Command', ps_cmd])

if __name__ == "__main__":
    if len(sys.argv) > 3:
        # Args: requested_shell, selection, query, stored_shell
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
