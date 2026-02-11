#? https://pypi.org/project/pretty-errors/

from customtkinter import *
from datetime import datetime
from PIL import Image, ImageTk
from pyadl import ADLManager
from queue import Queue
from time import strftime
from tkinter import Label, messagebox
from tkinter import simpledialog
from tkinter import ttk
import ctypes
import filecmp
import importlib
import keyboard
import os
import psutil
import pyautogui
import subprocess
import sys
import threading
import time
import tkinter as tk
import win32gui
import win32process

def calculate_time_to_appear(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to appear: {elapsed_time:.2f} seconds")

start_time = time.time()


#! Vaiables to track the position of the mouse when clicking​⁡
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
    # Using 'start' (Windows shell command) to open a new window
    # Using pwsh with -NoExit so the window stays open
    subprocess.Popen(f'start pwsh -NoExit -Command "{pwsh_command}"', shell=True)

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.default_color = kw.pop('default_color', "#000000")
        self.hover_color = kw.pop('hover_color', "red")
        self.default_fg = kw.pop('default_fg', "#FFFFFF")
        self.hover_fg = kw.pop('hover_fg', "#000000")
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(bg=self.default_color, fg=self.default_fg)

    def on_enter(self, event):
        self.configure(bg=self.hover_color, fg=self.hover_fg)

    def on_leave(self, event):
        self.configure(bg=self.default_color, fg=self.default_fg)

# wait this time to start the gui
def long_running_function():
    time.sleep(0)
    print("Function completed!")


# Call the long-running function
long_running_function()

set_console_title("🔥")
# Create main window
ROOT = tk.Tk()
ROOT.title("Python GUI")
# ROOT.attributes('-topmost', True)  # Set always on top
# ROOT.geometry("520x800")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)  # Remove default borders


#!############################################################
# def check_window_topmost():
#     if not ROOT.attributes('-topmost'):
#         ROOT.attributes('-topmost', True)
#     ROOT.after(500, check_window_topmost)
# # Call the function to check window topmost status periodically
# check_window_topmost()
#!############################################################


# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Add bindings to make the window movable
# ROOT.bind("<ButtonPress-1>", start_drag)
# ROOT.bind("<ButtonRelease-1>", stop_drag)
# ROOT.bind("<B1-Motion>", do_drag)

default_font = ("Jetbrainsmono nfp", 10)
ROOT.option_add("*Font", default_font)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width//2 - 1920//2
# y = screen_height//2 - 800//2
# y = screen_height-47-40
y = 993
ROOT.geometry(f"1920x39+{x}+{y}") #! overall size of the window


# #! Resize Window
# #* Function to toggle window size
# def toggle_window_size(size):
#     global window_state
#     global x
#     global y
#     if size == 'line':
#         ROOT.geometry('1920x39')
#         x = screen_width // 2 - 1920 // 2
#         y = 993
#         ROOT.configure(bg='red')
#         LB_L.config(text='\ueab7', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("JetBrainsMono NF", 16, "bold"))
#         LB_M.config(text='\uea72', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("JetBrainsMono NF", 18, "bold"))
#     elif size == 'max':
#         ROOT.geometry('1920x140')
#         x = screen_width // 2 - 1920 // 2
#         y = 892
#         ROOT.configure(bg='#1d2027')
#         LB_L.config(text='\ueab7', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("JetBrainsMono NF", 16, "bold"))
#         LB_M.config(text='\uea72', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("JetBrainsMono NF", 18, "bold"))
#     ROOT.focus_force()
#     ROOT.update_idletasks()
#     ROOT.geometry(f'{ROOT.winfo_width()}x{ROOT.winfo_height()}+{x}+{y}')
# def on_windows_x_pressed():
#     global window_size_state
#     if window_size_state == 'line':
#         toggle_window_size('max')
#         window_size_state = 'max'
#     else:
#         toggle_window_size('line')
#         window_size_state = 'line'
# #* Initial window size state
# window_size_state = 'line'
# #* Bind Windows + X to toggle between 'line' and 'max' sizesx
# #! keyboard.add_hotkey('win+x', on_windows_x_pressed)

# x = screen_width//2 - 753//2
# y = 0
# ROOT.geometry(f"+{x}+{y}")

# Create main frame
MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920, height=800)
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1, expand=True)  #! Add some padding at the top

# Adding transparent background property
ROOT.wm_attributes('-transparentcolor', '#000001')





#?  ██████╗  ██████╗  ██████╗ ████████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#?  ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#?  ██████╔╝██║   ██║██║   ██║   ██║       █████╗  ██████╔╝███████║██╔████╔██║█████╗
#?  ██╔══██╗██║   ██║██║   ██║   ██║       ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#?  ██║  ██║╚██████╔╝╚██████╔╝   ██║       ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#?  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

def get_active_window_info():
   # Wait for 2 seconds
   time.sleep(2)
   # Get the position of the mouse cursor
   pos = win32gui.GetCursorPos()
   # Get the handle of the window under the cursor
   hwnd = win32gui.WindowFromPoint(pos)
   # Get the active window information
   class_name = win32gui.GetClassName(hwnd)
   window_text = win32gui.GetWindowText(hwnd)
   _, pid = win32process.GetWindowThreadProcessId(hwnd)
   process_name = psutil.Process(pid).name()
   # Print the information with colors and separators
   print(f"\033[91mActive Window Class:\033[0m {class_name}")
   print(f"\033[92mActive Window Process Name:\033[0m {process_name}")
   print(f"\033[94mActive Window Title:\033[0m {window_text}")
   print("...")  # Add dots as a visual separator






#! ALL Boxes
ROOT1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT1.pack(side="left", pady=(2,2),padx=(5,1),  anchor="w", fill="x")

ROOT2 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT2.pack(side="right", pady=(2,2),padx=(5,1), anchor="e", fill="x")


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


# check_window_topmost()
# Lockbox_update_label(LockBox_lb)
calculate_time_to_appear(start_time)

ROOT.mainloop()
