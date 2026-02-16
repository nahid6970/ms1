import os
import subprocess
import tempfile
import sys
import json

# Centralized database paths
HISTORY_FILE = r"C:\@delta\db\FZF_launcher\CommandRunner\command_history.json"
BOOKMARKS_FILE = r"C:\@delta\db\FZF_launcher\CommandRunner\command_bookmarks.json"

def toggle_bookmark(command):
    if command.startswith("* "): command = command[2:]
    elif command.startswith("  "): command = command[2:]
    
    os.makedirs(os.path.dirname(BOOKMARKS_FILE), exist_ok=True)
    bookmarks = []
    if os.path.exists(BOOKMARKS_FILE):
        try:
            with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
                bookmarks = json.load(f)
        except: pass
    
    # Find and toggle
    found = None
    for bm in bookmarks:
        if bm.get("command") == command:
            found = bm
            break
    
    if found:
        bookmarks.remove(found)
    else:
        bookmarks.append({"command": command, "shell": "pwsh", "dir": ""})
    
    with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)

def move_bookmark(command, direction):
    if command.startswith("* "): command = command[2:]
    elif command.startswith("  "): command = command[2:]
    
    if not os.path.exists(BOOKMARKS_FILE): return
    try:
        with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
    except: return
    
    idx = None
    for i, bm in enumerate(bookmarks):
        if bm.get("command") == command:
            idx = i
            break
    
    if idx is None: return
    new_idx = idx + direction
    if 0 <= new_idx < len(bookmarks):
        bookmarks[idx], bookmarks[new_idx] = bookmarks[new_idx], bookmarks[idx]
        with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)

def remove_bookmark(command):
    if command.startswith("* "): command = command[2:]
    elif command.startswith("  "): command = command[2:]
    
    if not os.path.exists(BOOKMARKS_FILE): return
    try:
        with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
    except: return
    
    new_bookmarks = [bm for bm in bookmarks if bm.get("command") != command]
    if len(new_bookmarks) != len(bookmarks):
        with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_bookmarks, f, indent=2, ensure_ascii=False)

def get_feeder_data():
    """Outputs the history and bookmarks for fzf."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except: pass
    
    seen = set()
    try:
        # Load Bookmarks
        if os.path.exists(BOOKMARKS_FILE):
            with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                bms = json.load(f)
                for bm in bms:
                    cmd = bm["command"]
                    shell = bm.get("shell", "pwsh")
                    directory = bm.get("dir", "")
                    # Format: cmd \t shell \t dir \t type (with light green color)
                    print(f"\033[92m* {cmd}\033[0m\t{shell}\t{directory}\tBM")
                    seen.add(cmd)
                    
        # Load History
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                for h in history:
                    cmd = h["command"]
                    if cmd not in seen:
                        shell = h.get("shell", "pwsh")
                        directory = h.get("dir", "")
                        print(f"  {cmd}\t{shell}\t{directory}\tHIST")
                        seen.add(cmd)
        sys.stdout.flush()
    except (BrokenPipeError, IOError):
        pass
    except Exception:
        pass

def save_and_launch_chooser(selection, query, shell, directory, script_dir):
    """Saves selection data to a temp file and launches the chooser."""
    data = {
        "selection": selection,
        "query": query,
        "shell": shell,
        "dir": directory
    }
    
    fd, path = tempfile.mkstemp(suffix=".json", prefix="fzf_cmd_")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    chooser_script = os.path.join(script_dir, "terminal_chooser.py")
    subprocess.Popen(['start', '/b', 'pythonw', chooser_script, path], shell=True)

def run_command_ui():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Scripts

    shortcuts_text = r"""
Shortcuts available:
  Enter     : Run selected command (opens terminal chooser)
  F1        : Show this help window
  F5        : Bookmark/Unbookmark selected command
  Alt-Up    : Move bookmarked command up in order
  Alt-Down  : Move bookmarked command down in order
  Del       : Remove from history or bookmarks
  Ctrl-C    : Copy command to clipboard
  Ctrl-R    : Refresh history/bookmarks list
  ?         : Toggle help header at the top
  ESC       : Exit

Bookmarks are marked with *. History is marked with HIST.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as help_file:
        help_file.write(shortcuts_text)
        help_path = help_file.name

    # Create history remover script content
    remover_script_content = f'''
import sys
import json
import os

def remove_history(command):
    history_file = r"{HISTORY_FILE}"
    if command.startswith("* "): command = command[2:]
    elif command.startswith("  "): command = command[2:]
    
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            history = [h for h in history if h["command"] != command]
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except: pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        remove_history(sys.argv[1])
'''

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as remover_file:
        remover_file.write(remover_script_content)
        remover_path = remover_file.name

    # Create clipboard copy script
    copy_script_content = '''
import sys
import subprocess

if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd.startswith("* "): cmd = cmd[2:]
    elif cmd.startswith("  "): cmd = cmd[2:]
    subprocess.run(["clip"], input=cmd.encode("utf-8"), check=True)
'''

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as copy_file:
        copy_file.write(copy_script_content)
        copy_path = copy_file.name

    help_header = "Enter: Choose Terminal | F1: Help | F5: Toggle Bookmark\nDel: Remove | Ctrl-C: Copy | Ctrl-R: Refresh | ?: Toggle Help"

    fzf_args = [
        "fzf",
        "--ansi",
        "--prompt=Run Command [?] > ",
        "--header-first",
        "--no-header",
        f"--header={help_header}",
        "--delimiter=\\t",
        "--with-nth=1",
        "--layout=reverse",
        "--border",
        "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff",
        # Enter: Run command and reload. {1}=cmd, {2}=shell, {3}=dir
        f'--bind=enter:execute-silent(python "{script_path}" --launch {{1}} {{q}} {{2}} {{3}})+reload(python "{script_path}" --feed)+clear-query',
        # F5: Toggle bookmark and reload
        f'--bind=f5:execute-silent(python "{script_path}" --toggle-bookmark {{1}} {{q}})+reload(python "{script_path}" --feed)+clear-query',
        # Del: Remove from history AND bookmarks
        f'--bind=del:execute-silent(python "{remover_path}" {{1}} && python "{script_path}" --remove-bookmark {{1}})+reload(python "{script_path}" --feed)',
        # Ctrl-C: Copy to clipboard
        f'--bind=ctrl-c:execute-silent(python "{copy_path}" {{1}})',
        f'--bind=ctrl-r:reload(python "{script_path}" --feed)+clear-query',
        f'--bind=f1:execute-silent(cmd /c start cmd /k type "{help_path}" ^& pause)',
        f'--bind=alt-up:execute-silent(python "{script_path}" --move-bookmark up {{1}})+reload(python "{script_path}" --feed)+up',
        f'--bind=alt-down:execute-silent(python "{script_path}" --move-bookmark down {{1}})+reload(python "{script_path}" --feed)+down',
        "--bind=?:toggle-header",
        "--bind=start:toggle-header"
    ]

    try:
        while True:
            initial_feed = subprocess.Popen(['python', script_path, '--feed'], stdout=subprocess.PIPE, text=True, encoding='utf-8')
            process = subprocess.Popen(fzf_args, stdin=initial_feed.stdout, text=True, encoding='utf-8')
            initial_feed.stdout.close()
            process.wait()
            break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        for f in [help_path, remover_path, copy_path]:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass

if __name__ == "__main__":
    if "--feed" in sys.argv:
        get_feeder_data()
        os._exit(0)
    elif "--launch" in sys.argv:
        # Args: selection, query, shell, dir
        selection = sys.argv[2] if len(sys.argv) > 2 else ""
        query = sys.argv[3] if len(sys.argv) > 3 else ""
        shell = sys.argv[4] if len(sys.argv) > 4 else "pwsh"
        directory = sys.argv[5] if len(sys.argv) > 5 else ""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        save_and_launch_chooser(selection, query, shell, directory, script_dir)
        os._exit(0)
    elif "--toggle-bookmark" in sys.argv:
        # Toggle bookmark for command (either from {1} or {q})
        command = sys.argv[2] if len(sys.argv) > 2 else ""
        if not command and len(sys.argv) > 3:
            command = sys.argv[3]
        if command:
            toggle_bookmark(command)
        os._exit(0)
    elif "--move-bookmark" in sys.argv and len(sys.argv) > 3:
        direction = -1 if sys.argv[2] == "up" else 1
        command = sys.argv[3] if len(sys.argv) > 3 else ""
        if command:
            move_bookmark(command, direction)
        os._exit(0)
    elif "--remove-bookmark" in sys.argv and len(sys.argv) > 2:
        remove_bookmark(sys.argv[2])
        os._exit(0)
    else:
        run_command_ui()
