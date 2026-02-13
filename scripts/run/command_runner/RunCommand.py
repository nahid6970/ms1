import os
import subprocess
import tempfile
import sys
import json

# Centralized database paths
HISTORY_FILE = r"C:\@delta\db\FZF_launcher\command_history.json"
BOOKMARKS_FILE = r"C:\@delta\db\FZF_launcher\command_bookmarks.json"

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
                    print(f"* {cmd}\t{shell}\tBM")
                    seen.add(cmd)
                    
        # Load History
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                for h in history:
                    cmd = h["command"]
                    if cmd not in seen:
                        shell = h.get("shell", "pwsh")
                        print(f"  {cmd}\t{shell}\tHIST")
                        seen.add(cmd)
        sys.stdout.flush()
    except (BrokenPipeError, IOError):
        pass
    except Exception:
        pass

def run_command_ui():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Scripts
    terminal_chooser_script = os.path.join(script_dir, "terminal_chooser.py")
    add_bookmark_script = os.path.join(script_dir, "add_command_bookmark.py")
    view_bookmarks_script = os.path.join(script_dir, "view_command_bookmarks.py")

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
        # Use start /b to detach the GUI completely - this keeps fzf responsive
        f'--bind=enter:execute-silent(start /b pythonw "{terminal_chooser_script}" "{{1}}" "{{q}}" "{{2}}")',
        f'--bind=f5:execute-silent(python "{add_bookmark_script}" "{{1}}" || python "{add_bookmark_script}" "{{q}}")+reload(python "{script_path}" --feed)',
        f'--bind=del:execute-silent(python "{view_bookmarks_script}" --remove {{1}})+reload(python "{script_path}" --feed)',
        f'--bind=ctrl-r:reload(python "{script_path}" --feed)',
        f'--bind=f1:execute-silent(cmd /c start cmd /k type "{help_path}" ^& pause)',
        "--bind=?:toggle-header",
        "--bind=start:toggle-header"
    ]

    try:
        # Run fzf in a loop to allow for complete refreshes if needed, matching Run.py
        while True:
            initial_feed = subprocess.Popen(['python', script_path, '--feed'], stdout=subprocess.PIPE, text=True, encoding='utf-8')
            process = subprocess.Popen(fzf_args, stdin=initial_feed.stdout, text=True, encoding='utf-8')
            initial_feed.stdout.close()
            process.wait()
            
            # If fzf exited with 0 (Enter pressed on a non-binding) or 130 (ESC), exit the loop
            if process.returncode != 0 and process.returncode != 1:
                break
            if process.returncode == 130:
                break
            # Otherwise loop continues (e.g. if we used an action that didn't exit fzf)
            # But since we use bindings for everything, fzf usually stays open.
            # We only get here if fzf itself exits.
            break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(help_path):
            try: os.remove(help_path)
            except: pass

if __name__ == "__main__":
    if "--feed" in sys.argv:
        get_feeder_data()
        os._exit(0)
    else:
        run_command_ui()
