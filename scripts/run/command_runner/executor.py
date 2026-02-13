import sys
import os
import json
import subprocess

# Centralized database path
HISTORY_FILE = r"C:\@delta\db\FZF_launcher\CommandRunner\command_history.json"
BOOKMARKS_FILE = r"C:\@delta\db\FZF_launcher\CommandRunner\command_bookmarks.json"

def add_to_history(command, shell, dir_path=None):
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
    
    # Save with directory if provided
    entry = {"command": command, "shell": shell}
    if dir_path:
        entry["dir"] = dir_path
        
    history.insert(0, entry)
    
    # Keep last 100
    history = history[:100]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
        
    # Also update bookmarks if the command is bookmarked
    if os.path.exists(BOOKMARKS_FILE):
        try:
            with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
                bookmarks = json.load(f)
            updated = False
            for bm in bookmarks:
                if bm['command'] == command:
                    bm['shell'] = shell
                    if dir_path: bm['dir'] = dir_path
                    updated = True
            if updated:
                with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        except: pass

def run_command(command, shell, dir_path=None):
    add_to_history(command, shell, dir_path)
    
    # Base start command
    start_args = ['cmd', '/c', 'start']
    
    # Handle working directory
    if dir_path and os.path.isdir(dir_path):
        start_args.extend(['/D', dir_path])
    
    if shell == "cmd":
        start_args.extend(['cmd', '/k', command])
    elif shell == "powershell":
        ps_cmd = f"& {{ {command} }}"
        start_args.extend(['powershell', '-NoExit', '-Command', ps_cmd])
    elif shell == "pwsh":
        ps_cmd = f"& {{ {command} }}"
        start_args.extend(['pwsh', '-NoExit', '-Command', ps_cmd])
    else:
        ps_cmd = f"& {{ {command} }}"
        start_args.extend(['pwsh', '-NoExit', '-Command', ps_cmd])

    subprocess.Popen(start_args)

if __name__ == "__main__":
    if len(sys.argv) > 3:
        # Args: requested_shell, selection, query, stored_shell, optional_dir
        req_shell = sys.argv[1]
        selection = sys.argv[2].strip()
        query = sys.argv[3].strip()
        stored_shell = sys.argv[4] if len(sys.argv) > 4 else "pwsh"
        dir_path = sys.argv[5] if len(sys.argv) > 5 else None
        
        command = selection if selection else query
        if not command:
            sys.exit(0)
            
        shell = stored_shell if (req_shell == "auto" and selection) else req_shell
        if shell == "auto": shell = "pwsh"
        
        run_command(command, shell, dir_path)
