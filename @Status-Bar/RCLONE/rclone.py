#? https://pypi.org/project/pretty-errors/

# Command config
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

# # Show log output in Notepad
# def on_label_click(event, cfg):
#     try:
#         notepadpp_path = r"C:\Program Files\Notepad++\notepad++.exe"
#         subprocess.Popen([notepadpp_path, cfg["log"]])
#     except Exception as e:
#         print(f"Error opening log file for {cfg['label']}: {e}")

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

# ms1_rclone_o0 = tk.Label(ROOT1,text="ms1", bg="#1d2027", fg="#cc5907", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
# ms1_rclone_o0.pack(side="left", padx=(0, 0), pady=(0, 0))
# ms1_rclone_o0.bind( "<Button-1>", lambda event=None: run_command( r'rclone sync C:/@delta/ms1/ o0:/ms1/ --exclude ".git/**" --exclude "__pycache__/**" -P --fast-list' ))


#! ██████╗ ██╗ ██████╗ ██╗  ██╗████████╗
#! ██╔══██╗██║██╔════╝ ██║  ██║╚══██╔══╝
#! ██████╔╝██║██║  ███╗███████║   ██║
#! ██╔══██╗██║██║   ██║██╔══██║   ██║
#! ██║  ██║██║╚██████╔╝██║  ██║   ██║
#! ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝

