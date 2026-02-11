#? https://pypi.org/project/pretty-errors/

from customtkinter import *
from time import strftime
import ctypes
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import json

def calculate_time_to_appear(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to appear: {elapsed_time:.2f} seconds")

start_time = time.time()

# Relative path for JSON file
JSON_PATH = os.path.join(os.path.dirname(__file__), "commands.json")
LOG_DIR = r"C:\Users\nahid\script_output\rclone"
os.makedirs(LOG_DIR, exist_ok=True)

def load_commands():
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
    return {}

def save_commands(commands):
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(commands, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")

commands = load_commands()

#! Variables to track the position of the mouse when clicking​⁡
drag_data = {"x": 0, "y": 0}

def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def stop_drag(event):
    drag_data["x"] = None
    drag_data["y"] = None

def do_drag(event):
    if drag_data["x"] is not None and drag_data["y"] is not None:
        x, y = (event.x - drag_data["x"] + ROOT.winfo_x(), event.y - drag_data["y"] + ROOT.winfo_y())
        ROOT.geometry("+%s+%s" % (x, y))

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def run_command(pwsh_command):
    """Run a PowerShell command in a new terminal window."""
    subprocess.Popen(f'start pwsh -NoExit -Command "{pwsh_command}"', shell=True)

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.default_color = kw.pop('default_color', "#1d2027")
        self.hover_color = kw.pop('hover_color', "red")
        self.default_fg = kw.pop('default_fg', "#FFFFFF")
        self.hover_fg = kw.pop('hover_fg', "#000000")
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(bg=self.default_color, fg=self.default_fg, activebackground=self.hover_color, activeforeground=self.hover_fg, bd=0, highlightthickness=0)

    def on_enter(self, event):
        self.configure(bg=self.hover_color, fg=self.hover_fg)

    def on_leave(self, event):
        self.configure(bg=self.default_color, fg=self.default_fg)

set_console_title("🔥")
# Create main window
ROOT = tk.Tk()
ROOT.title("Python GUI")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)  # Remove default borders

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)
default_font = ("Jetbrainsmono nfp", 10)
ROOT.option_add("*Font", default_font)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width//2 - 1920//2
y = 993
ROOT.geometry(f"+{x}+{y}") #! overall size of the window (auto width)

# Create main frame
MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027")
MAIN_FRAME.pack(pady=1, padx=2, expand=True, fill="both")

#! ALL Boxes
ROOT1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT1.pack(side="left", pady=(2,2), padx=(5,1), anchor="w", fill="x")

# Auto-Sync state
auto_sync_enabled = False
auto_sync_interval = 3600 # 1 hour by default, or whatever interval you want

def toggle_auto_sync():
    global auto_sync_enabled
    auto_sync_enabled = not auto_sync_enabled
    if auto_sync_enabled:
        btn_auto.config(fg="#06de22", text="\uf017 ON")
        threading.Thread(target=auto_sync_loop, daemon=True).start()
    else:
        btn_auto.config(fg="red", text="\uf017 OFF")

def auto_sync_loop():
    while auto_sync_enabled:
        for key, cfg in commands.items():
            if not auto_sync_enabled: break
            cmd = cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
            actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
            # Run silently in background for auto-sync
            subprocess.run(f'pwsh -Command "{actual_cmd}"', shell=True)
        time.sleep(auto_sync_interval)

def on_label_click(event, cfg):
    try:
        log_path = os.path.join(LOG_DIR, f"{cfg['label']}_check.log")
        subprocess.Popen([
            "powershell", "-NoExit", "-Command", f'edit "{log_path}"'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print(f"Error opening log file: {e}")

def ctrl_left_click(event, cfg):
    if event.state & 0x0004:  # Ctrl key mask
        cmd = cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
        actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
        run_command(actual_cmd)

def ctrl_right_click(event, cfg):
    if event.state & 0x0004:  # Ctrl key mask
        cmd = cfg.get("right_click_cmd", "rclone sync dst src -P --fast-list")
        actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
        run_command(actual_cmd)

def remove_command(key):
    if messagebox.askyesno("Remove", f"Remove {key}?"):
        del commands[key]
        save_commands(commands)
        refresh_gui()

def add_command():
    name = simpledialog.askstring("Input", "Name (key):")
    if not name: return
    label = simpledialog.askstring("Input", "Label (Icon/Text):")
    src = simpledialog.askstring("Input", "Source Path:")
    dst = simpledialog.askstring("Input", "Destination Path:")
    if name and label and src and dst:
        commands[name] = {
            "cmd": "rclone check src dst --fast-list --size-only",
            "src": src,
            "dst": dst,
            "label": label,
            "left_click_cmd": "rclone sync src dst -P --fast-list --log-level INFO",
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        }
        save_commands(commands)
        refresh_gui()

# Periodically check using rclone
def check_and_update(label, cfg):
    def run_check():
        log_path = os.path.join(LOG_DIR, f"{cfg['label']}_check.log")
        actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
        with open(log_path, "w") as f:
            subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
        
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                content = f.read()
            if "ERROR" not in content and "0 differences found" in content:
                label.config(fg="#06de22")
            else:
                label.config(fg="red")
        
        # Check again in 10 minutes
        if label.winfo_exists():
            label.after(600000, lambda: threading.Thread(target=run_check, daemon=True).start())
    
    threading.Thread(target=run_check, daemon=True).start()

def refresh_gui():
    for widget in ROOT1.winfo_children():
        widget.destroy()
    create_gui()

# GUI setup
def create_gui():
    for key, cfg in commands.items():
        lbl = tk.Label(
            ROOT1,
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
        
        # Right click to remove (without ctrl)
        lbl.bind("<Button-3>", lambda event, k=key: remove_command(k))

        check_and_update(lbl, cfg)
    
    # Add Button
    btn_add = HoverButton(ROOT1, text="+", font=("JetBrainsMono NFP", 14, "bold"), command=add_command, width=2)
    btn_add.pack(side="left", padx=(10, 2))

    # Auto Sync Toggle
    global btn_auto
    btn_auto = HoverButton(ROOT1, text="\uf017 OFF", font=("JetBrainsMono NFP", 10, "bold"), command=toggle_auto_sync, fg="red")
    btn_auto.pack(side="left", padx=(5, 5))

    # Update ROOT size
    ROOT.update_idletasks()

# Support dragging on the main frame
MAIN_FRAME.bind("<Button-1>", start_drag)
MAIN_FRAME.bind("<B1-Motion>", do_drag)
ROOT1.bind("<Button-1>", start_drag)
ROOT1.bind("<B1-Motion>", do_drag)

# Call GUI init
create_gui()
ROOT.mainloop()
