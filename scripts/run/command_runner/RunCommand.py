import os
import subprocess
import tempfile
import sys
import json

def run_command_ui():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Centralized database path
    history_file = "C:\\@delta\\db\\FZF_launcher\\command_history.json"
    bookmarks_file = "C:\\@delta\\db\\FZF_launcher\\command_bookmarks.json"
    executor_script = os.path.join(script_dir, "executor.py")
    add_bookmark_script = os.path.join(script_dir, "add_command_bookmark.py")
    view_bookmarks_script = os.path.join(script_dir, "view_command_bookmarks.py")
    terminal_chooser_script = os.path.join(script_dir, "terminal_chooser.py")

    shortcuts_text = r"""
Shortcuts available:
  Enter     : Run selected command (opens terminal chooser)
  F1        : Show this help window
  F5        : Add command to bookmarks
  Del       : Remove from history or bookmarks
  Ctrl-R    : Refresh history/bookmarks list
  ?         : Toggle help header at the top
  ESC       : Exit

Selected command can be bookmarked with F5.
History items (marked with HIST) appear after Bookmarks (marked with *).
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as help_file:
        help_file.write(shortcuts_text)
        help_path = help_file.name

    # Create feeder script content
    feeder_script_content = f'''
import json
import os
import sys

# Fix Unicode encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

history_file = r"{history_file}"
bookmarks_file = r"{bookmarks_file}"

def get_items():
    items = []
    seen = set()

    # Load Bookmarks first (priority)
    if os.path.exists(bookmarks_file):
        try:
            with open(bookmarks_file, "r", encoding="utf-8") as f:
                bms = json.load(f)
                for bm in bms:
                    cmd = bm["command"]
                    shell = bm.get("shell", "pwsh")
                    # Use * marker like Run.py
                    display = f"* {{cmd}}\\t{{shell}}\\tBM"
                    print(display)
                    seen.add(cmd)
        except: pass

    # Load History
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
                for h in history:
                    cmd = h["command"]
                    if cmd in seen: continue
                    shell = h.get("shell", "pwsh")
                    display = f"  {{cmd}}\\t{{shell}}\\tHIST"
                    print(display)
                    seen.add(cmd)
        except: pass

if __name__ == "__main__":
    get_items()
'''

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as feeder_file:
        feeder_file.write(feeder_script_content)
        feeder_path = feeder_file.name

    # Create history remover script content
    remover_script_content = f'''
import sys
import json
import os

def remove_history(command):
    history_file = r"{history_file}"
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
        # Strip the marker from the command if passed
        cmd = sys.argv[1]
        if cmd.startswith("* "): cmd = cmd[2:]
        elif cmd.startswith("  "): cmd = cmd[2:]
        remove_history(cmd)
'''

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as remover_file:
        remover_file.write(remover_script_content)
        remover_path = remover_file.name

    # Header style matching Run.py
    help_header = "Enter: Choose Terminal | F1: Help | F5: Bookmark\nDel: Remove | Ctrl-R: Refresh | ?: Toggle Help"

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
        f'--bind=enter:execute-silent(python "{terminal_chooser_script}" {{1}} {{q}} {{2}})',
        f'--bind=f5:execute-silent(python "{add_bookmark_script}" {{1}} || python "{add_bookmark_script}" {{q}})+reload(python "{feeder_path}")',
        f'--bind=del:execute-silent(python "{remover_path}" {{1}} && python "{view_bookmarks_script}" --remove {{1}})+reload(python "{feeder_path}")',
        f'--bind=ctrl-r:reload(python "{feeder_path}")',
        f'--bind=f1:execute-silent(cmd /c start cmd /k type "{help_path}" ^& pause)',
        "--bind=?:toggle-header",
        "--bind=start:toggle-header"
    ]

    try:
        initial_feed = subprocess.Popen(
            ['python', feeder_path],
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        process = subprocess.Popen(fzf_args, stdin=initial_feed.stdout, text=True, encoding='utf-8')
        initial_feed.stdout.close()
        process.wait()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(feeder_path):
            try: os.remove(feeder_path)
            except: pass
        if os.path.exists(remover_path):
            try: os.remove(remover_path)
            except: pass
        if os.path.exists(help_path):
            try: os.remove(help_path)
            except: pass

if __name__ == "__main__":
    run_command_ui()
