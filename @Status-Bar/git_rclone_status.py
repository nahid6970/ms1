import tkinter as tk
import subprocess
import os
import time
import threading
from queue import Queue

# Initialize main window
root = tk.Tk()
root.title("Git & Rclone Status Monitor")
root.configure(bg="#1d2027")

# Create main container
ROOT1 = tk.Frame(root, bg="#1d2027")
ROOT1.pack(fill="both", expand=True, padx=10, pady=10)

#! ═══════════════════════════════════════════════════════════════════════════
#! GITHUB STATUS SECTION (from line 819)
#! ═══════════════════════════════════════════════════════════════════════════

# Define your repositories here
queue = Queue()
repos = [
    {"name": "ms1", "path": "C:\\@delta\\ms1", "label": "ms1"},
    {"name": "db", "path": "C:\\@delta\\db", "label": "db"},
    {"name": "test", "path": "C:\\@delta\\test", "label": "test"},
    # {"name": "ms2", "path": "C:\\ms2", "label": "2"},
    # {"name": "ms3", "path": "C:\\ms3", "label": "3"},
    # Add more as needed
]

status_labels = {}

def check_git_status(git_path, queue):
    if not os.path.exists(git_path):
        queue.put((git_path, "Invalid", "#000000"))
        return
    os.chdir(git_path)
    git_status = subprocess.run(["git", "status"], capture_output=True, text=True)
    
    label_text = next((r["label"] for r in repos if r["path"] == git_path), "?")
    
    if "nothing to commit, working tree clean" in git_status.stdout:
        queue.put((git_path, label_text, "#00ff21"))  # Green
    else:
        queue.put((git_path, label_text, "#fe1616"))  # Red


def show_git_changes(git_path):
    if not os.path.exists(git_path):
        print("Invalid path")
        return
    os.chdir(git_path)
    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", "git status && git diff --stat"])

def git_backup(event):
    commands = " ; ".join([f"{r['path']}\\scripts\\Github\\{r['name']}u.ps1" for r in repos])
    subprocess.Popen([
        "Start", "pwsh", "-NoExit", "-Command",
        f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; {commands} ; cd ~}}"
    ], shell=True)

def delete_git_lock_files(event=None):
    for repo in repos:
        lock_file = os.path.join(repo["path"], ".git", "index.lock")
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                print(f"Deleted: {lock_file}")
            else:
                print(f"File not found: {lock_file}")
        except Exception as e:
            print(f"Error deleting {lock_file}: {e}")

def update_status():
    while True:
        for repo in repos:
            check_git_status(repo["path"], queue)
        time.sleep(1)

def update_gui():
    while True:
        try:
            git_path, text, color = queue.get_nowait()
            for repo in repos:
                if git_path == repo["path"]:
                    status_labels[repo["name"]].config(text=text, fg=color)
        except:
            pass
        time.sleep(0.1)

# Git Backup All Icon
bkup = tk.Label(ROOT1, text="\udb80\udea2", bg="#1d2027", fg="#009fff", font=("JetBrainsMono NFP", 18, "bold"))
bkup.pack(side="left")
bkup.bind("<Button-1>", git_backup)

# Add repo-specific labels and bindings dynamically
for repo in repos:
    label = tk.Label(
        ROOT1, bg="#1d2027", fg="#FFFFFF",
        font=("JetBrainsMono NFP", 12, "bold"), text=repo["label"]
    )
    label.pack(side="left")
    label.bind("<Button-1>", lambda e, p=repo["path"]: subprocess.Popen(
        ["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; cd {p.replace(os.sep, '/')} ; gitter}}"], shell=True
    ))
    # Ctrl + Left click → open repo folder in Explorer
    label.bind("<Control-Button-1>", lambda e, p=repo["path"]: subprocess.Popen(
        f'explorer "{p}"', shell=True
    ))
    label.bind("<Button-3>", lambda e, p=repo["path"]: subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=p, shell=True))
    label.bind("<Control-Button-3>", lambda e, p=repo["path"]: subprocess.Popen(
        ["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='Git Restore' ; cd {p.replace(os.sep, '/')} ; git restore . }}"], shell=True
    ))
    status_labels[repo["name"]] = label

# Git Lock File Cleaner Icon
DelGitIgnore = tk.Label(ROOT1, text="\udb82\udde7", bg="#1d2027", fg="#ffffff", font=("JetBrainsMono NFP", 18, "bold"))
DelGitIgnore.pack(side="left")
DelGitIgnore.bind("<Button-1>", delete_git_lock_files)

# Start background threads
threading.Thread(target=update_status, daemon=True).start()
threading.Thread(target=update_gui, daemon=True).start()

# Separator
SEPARATOR = tk.Label(ROOT1, text="]", bg="#1d2027", fg="#009fff", height=0, width=0, relief="flat", font=("JetBrainsMono NFP", 18, "bold"))
SEPARATOR.pack(side="left", padx=(0, 0), pady=(0, 0))

#! ═══════════════════════════════════════════════════════════════════════════
#! RCLONE STATUS SECTION (from line 953)
#! ═══════════════════════════════════════════════════════════════════════════

# Ensure log folder exists
LOG_DIR = r"C:\Users\nahid\script_output\rclone"
os.makedirs(LOG_DIR, exist_ok=True)

commands = {
    "msBackups": {
        "cmd": "rclone check src dst --fast-list --size-only",
        "src": "C:/@delta/msBackups",
        "dst": "gu:/msBackups",
        "log": f"{LOG_DIR}/msBackups_check.log",
        "label": "\udb85\ude32"
    },
    "software": {
        "cmd": "rclone check src dst --fast-list --size-only",
        "src": "D:/software",
        "dst": "gu:/software",
        "log": f"{LOG_DIR}/software_check.log",
        "label": "\uf40e"
    },
    "song": {
        "cmd": "rclone check src dst --fast-list --size-only",
        "src": "D:/song",
        "dst": "gu:/song",
        "log": f"{LOG_DIR}/song_check.log",
        "label": "\uec1b"
    },
    "ms1": {
        "cmd": 'rclone check src dst --fast-list --size-only --exclude ".git/**" --exclude "__pycache__/**"',
        "src": "C:/@delta/ms1/",
        "dst": "o0:/ms1/",
        "log": f"{LOG_DIR}/ms1_check.log",
        "label": "ms1",
        "left_click_cmd": "rclone sync src dst -P --fast-list --exclude \".git/**\" --exclude \"__pycache__/**\"  --log-level INFO",
        "right_click_cmd": "rclone sync dst src -P --fast-list"
    },
    "Photos": {
        "cmd": 'rclone check src dst --fast-list --size-only --exclude \".globalTrash/**\" --exclude \".stfolder/**\" --exclude \".stfolder (1)/**\"',
        "src": "C:/Users/nahid/Pictures/",
        "dst": "gu:/Pictures/",
        "log": f"{LOG_DIR}/Pictures_check.log",
        "label": "\uf03e",
        "left_click_cmd": "rclone sync src dst -P --fast-list --track-renames --exclude \".globalTrash/**\" --exclude \".stfolder/**\" --log-level INFO",
        "right_click_cmd": "rclone sync dst src -P --fast-list"
    },
}

# Show log output in Microsoft Edit in a new PowerShell terminal
def on_label_click(event, cfg):
    try:
        subprocess.Popen([
            "powershell", "-NoExit", "-Command", f'edit "{cfg["log"]}"'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print(f"Error opening log file for {cfg['label']}: {e}")

def ctrl_left_click(event, cfg):
    if event.state & 0x0004:  # Ctrl key mask
        # Replace placeholders and run the left_click_cmd command
        cmd = cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
        actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
        run_command(actual_cmd)

def ctrl_right_click(event, cfg):
    if event.state & 0x0004:  # Ctrl key mask
        # Replace placeholders and run the right_click_cmd command
        cmd = cfg.get("right_click_cmd", "rclone sync dst src -P --fast-list")
        actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
        run_command(actual_cmd)

def run_command(cmd):
    """Helper function to run rclone commands in a new PowerShell window"""
    subprocess.Popen([
        "powershell", "-NoExit", "-Command", cmd
    ], creationflags=subprocess.CREATE_NEW_CONSOLE)

# Periodically check using rclone
def check_and_update(label, cfg):
    def run_check():
        actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
        with open(cfg["log"], "w") as f:
            subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
        with open(cfg["log"], "r") as f:
            content = f.read()
        if not "ERROR" in content:
            label.config(text=cfg["label"], fg="#06de22")
        else:
            label.config(text=cfg["label"], fg="red")
        label.after(600000, lambda: threading.Thread(target=run_check).start())  # repeat every 10 minutes
    threading.Thread(target=run_check).start()

# GUI setup
def create_gui():
    for key, cfg in commands.items():
        lbl = tk.Label(
            ROOT1,
            width=0,
            bg="#1d2027",
            text=cfg["label"],
            font=("JetBrainsMono NFP", 16, "bold"),
            cursor="hand2"
        )
        lbl.pack(side="left", padx=(5, 5))

        # Event bindings
        lbl.bind("<Button-1>", lambda event, c=cfg: on_label_click(event, c))           # left click
        lbl.bind("<Control-Button-1>", lambda event, c=cfg: ctrl_left_click(event, c))  # ctrl + left
        lbl.bind("<Control-Button-3>", lambda event, c=cfg: ctrl_right_click(event, c)) # ctrl + right

        check_and_update(lbl, cfg)

# Call GUI init
create_gui()

#! ═══════════════════════════════════════════════════════════════════════════
#! SHORTCUTS SUMMARY
#! ═══════════════════════════════════════════════════════════════════════════
# Git Status Labels:
#   - Left Click: Open PowerShell with gitter command
#   - Ctrl + Left Click: Open repo folder in Explorer
#   - Right Click: Open lazygit in PowerShell
#   - Ctrl + Right Click: Git restore (undo changes)
#
# Rclone Labels:
#   - Left Click: View log file in editor
#   - Ctrl + Left Click: Sync local to remote
#   - Ctrl + Right Click: Sync remote to local

# Start the GUI
root.mainloop()
