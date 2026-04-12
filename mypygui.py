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
import json
import win32process

CONFIG_FILE = "mypygui_config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

CONFIG = load_config()

def handle_action(action_cfg):
    if not action_cfg: return
    atype = action_cfg.get("type")
    cmd = action_cfg.get("cmd")
    cwd = action_cfg.get("cwd")
    admin = action_cfg.get("admin", False)
    hide = action_cfg.get("hide", False)
    
    if admin:
        # Launch as admin using shell execute "runas"
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable if atype=="python" else "cmd.exe", 
                                               f"/c {cmd}" if atype!="python" else cmd, cwd, 1 if not hide else 0)
        except Exception as e:
            print(f"Admin launch failed: {e}")
        return

    flags = subprocess.CREATE_NO_WINDOW if hide else 0
    
    if atype == "subprocess":
        subprocess.Popen(cmd, cwd=cwd, shell=True, creationflags=flags)
    elif atype == "run_command":
        run_command(cmd)
    elif atype == "python":
        subprocess.Popen([sys.executable, cmd], cwd=cwd, creationflags=flags)
    elif atype == "function":
        func_name = action_cfg.get("func")
        if func_name == "restart": restart()
        elif func_name == "close_window": close_window()
        elif func_name == "clear_screen": clear_screen()

def open_edit_gui(item_cfg, category, index=None):
    edit_win = tk.Toplevel(ROOT)
    edit_win.title(f"Edit {item_cfg.get('id', 'Item')}")
    edit_win.geometry("700x850")
    edit_win.configure(bg="#282c34")
    edit_win.attributes("-topmost", True)

    # Scrollable frame for many options
    canvas = tk.Canvas(edit_win, bg="#282c34", highlightthickness=0)
    scrollbar = ttk.Scrollbar(edit_win, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#282c34")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Basic Info
    fields = ["text", "fg", "bg", "id"]
    entries = {}
    for i, field in enumerate(fields):
        tk.Label(scroll_frame, text=field.upper(), fg="#abb2bf", bg="#282c34", font=("Arial", 10, "bold")).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        ent = tk.Entry(scroll_frame, width=50, bg="#1d2027", fg="white", insertbackground="white")
        ent.insert(0, str(item_cfg.get(field, "")))
        ent.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        entries[field] = ent

    # Bindings Sections
    click_types = [
        ("Left Click", "Button-1"),
        ("Right Click", "Button-3"),
        ("Ctrl + Left Click", "Control-Button-1"),
        ("Ctrl + Right Click", "Control-Button-3")
    ]
    
    binding_inputs = {}
    current_row = len(fields)

    for label, key in click_types:
        frame = tk.LabelFrame(scroll_frame, text=label, fg="#61afef", bg="#282c34", font=("Arial", 11, "bold"), padx=10, pady=10)
        frame.grid(row=current_row, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")
        current_row += 1
        
        cfg = item_cfg.get("bindings", {}).get(key, {})
        
        # Command
        tk.Label(frame, text="Command:", fg="white", bg="#282c34").grid(row=0, column=0, sticky="w")
        cmd_ent = tk.Entry(frame, width=60, bg="#1d2027", fg="white", insertbackground="white")
        cmd_ent.insert(0, cfg.get("cmd", cfg.get("func", "")))
        cmd_ent.grid(row=0, column=1, padx=5, pady=2)
        
        # Type Dropdown
        tk.Label(frame, text="Type:", fg="white", bg="#282c34").grid(row=1, column=0, sticky="w")
        type_var = tk.StringVar(value=cfg.get("type", "subprocess"))
        type_combo = ttk.Combobox(frame, textvariable=type_var, values=["subprocess", "run_command", "python", "function"], state="readonly", width=20)
        type_combo.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Options
        opt_frame = tk.Frame(frame, bg="#282c34")
        opt_frame.grid(row=2, column=1, sticky="w")
        
        hide_var = tk.BooleanVar(value=cfg.get("hide", False))
        tk.Checkbutton(opt_frame, text="Hide Terminal", variable=hide_var, fg="white", bg="#282c34", selectcolor="#1d2027", activebackground="#282c34", activeforeground="white").pack(side="left")
        
        admin_var = tk.BooleanVar(value=cfg.get("admin", False))
        tk.Checkbutton(opt_frame, text="Run as Admin", variable=admin_var, fg="white", bg="#282c34", selectcolor="#1d2027", activebackground="#282c34", activeforeground="white").pack(side="left", padx=20)
        
        binding_inputs[key] = {
            "cmd": cmd_ent,
            "type": type_var,
            "hide": hide_var,
            "admin": admin_var
        }

    def save():
        for field in fields:
            item_cfg[field] = entries[field].get()
        
        new_bindings = {}
        for key, inputs in binding_inputs.items():
            cmd = inputs["cmd"].get()
            if not cmd: continue
            
            b_type = inputs["type"].get()
            new_bindings[key] = {
                "type": b_type,
                "hide": inputs["hide"].get(),
                "admin": inputs["admin"].get()
            }
            if b_type == "function":
                new_bindings[key]["func"] = cmd
            else:
                new_bindings[key]["cmd"] = cmd
        
        item_cfg["bindings"] = new_bindings
        
        config = load_config()
        if category in config:
            if index is not None:
                config[category][index] = item_cfg
            else: 
                config[category][item_cfg["id"]] = item_cfg
        
        save_config(config)
        edit_win.destroy()
        if messagebox.askyesno("Restart", "Settings saved. Restart GUI to apply?"):
            restart()

    tk.Button(scroll_frame, text="SAVE CONFIGURATION", command=save, bg="#98c379", fg="black", font=("Arial", 12, "bold"), pady=10).grid(row=current_row, column=0, columnspan=2, pady=30, sticky="nsew")

def create_dynamic_button(parent, btn_cfg, category, index=None):
    widget_type = btn_cfg.get("widget_type", "Label")
    font = tuple(btn_cfg.get("font", ["JetBrainsMono NFP", 16, "bold"]))
    
    if widget_type == "CTkLabel":
        lbl = CTkLabel(parent, text=btn_cfg.get("text", ""), text_color=btn_cfg.get("fg", "white"), font=font)
    elif widget_type == "CTkButton":
        lbl = CTkButton(parent, text=btn_cfg.get("text", ""), text_color=btn_cfg.get("fg", "white"), fg_color=btn_cfg.get("bg", "#1d2027"), font=font, width=0, height=10)
    else:
        lbl = tk.Label(parent, text=btn_cfg.get("text", ""), bg=btn_cfg.get("bg", "#1d2027"), fg=btn_cfg.get("fg", "white"), font=font, relief="flat")
    
    lbl.pack(side="left", padx=(1, 1))
    
    bindings = btn_cfg.get("bindings", {})
    for event, action in bindings.items():
        # Handle simple string function calls for backward compatibility if any
        if isinstance(action, str):
            lbl.bind(f"<{event}>", lambda e, a=action: handle_action({"type": "function", "func": a}))
        else:
            lbl.bind(f"<{event}>", lambda e, a=action: handle_action(a))
    
    # Shift+Click for editing
    lbl.bind("<Shift-Button-1>", lambda e: open_edit_gui(btn_cfg, category, index))
    return lbl


def calculate_time_to_appear(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to appear: {elapsed_time:.2f} seconds")

start_time = time.time()

# Print ASCII art in the console
print(r"""

$$\   $$\           $$\       $$\       $$\ $$\   $$\  $$$$$$\
$$$\  $$ |          $$ |      \__|      $$ |$$$\  $$ |$$  __$$\
$$$$\ $$ | $$$$$$\  $$$$$$$\  $$\  $$$$$$$ |$$$$\ $$ |$$ /  $$ |
$$ $$\$$ | \____$$\ $$  __$$\ $$ |$$  __$$ |$$ $$\$$ |$$$$$$$$ |
$$ \$$$$ | $$$$$$$ |$$ |  $$ |$$ |$$ /  $$ |$$ \$$$$ |$$  __$$ |
$$ |\$$$ |$$  __$$ |$$ |  $$ |$$ |$$ |  $$ |$$ |\$$$ |$$ |  $$ |
$$ | \$$ |\$$$$$$$ |$$ |  $$ |$$ |\$$$$$$$ |$$ | \$$ |$$ |  $$ |
\__|  \__| \_______|\__|  \__|\__| \_______|\__|  \__|\__|  \__|

""")

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

#! Close Window
def close_window(event=None):
    ROOT.destroy()

# def close_window(event=None):
#     password = simpledialog.askstring("Password", "Enter the password to close the window:")
#     if password == "":  # Replace "your_password_here" with your actual password
#         ROOT.destroy()
#     else:
#         print("Incorrect password. Window not closed.")

def restart(event=None):
    ROOT.destroy()
    subprocess.Popen([sys.executable] + sys.argv)

#! Pin/Unpin
def check_window_topmost():
    if not ROOT.attributes('-topmost'):
        ROOT.attributes('-topmost', True)
    if checking:  # Only continue checking if the flag is True
        ROOT.after(500, check_window_topmost)

# def toggle_checking():
#     global checking
#     checking = not checking
#     if checking:
#         if ROOT.attributes('-topmost'):  # Only start checking if already topmost
#             check_window_topmost()  # Start checking if toggled on and already topmost
#         Topmost_lb.config(fg="#000000")  # Change text color to green
#         Topmost_lb.config(bg="#FFFFFF")  # Change text color to green
#     else:
#         ROOT.after_cancel(check_window_topmost)  # Cancel the checking if toggled off
#         Topmost_lb.config(fg="#FFFFFF")  # Change text color to white
#         Topmost_lb.config(bg="#000000")  # Change text color to white

checking = False

#! CPU / RAM / DRIVES / NET SPEED
def get_cpu_ram_info():
    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = psutil.virtual_memory().percent
    return cpu_usage, ram_usage
def get_gpu_usage():
    # Get the first GPU device (you can modify this if you have multiple GPUs)
    device = ADLManager.getInstance().getDevices()[0]
    # Get the current GPU usage
    gpu_usage = device.getCurrentUsage()
    return gpu_usage
def get_disk_info():
    disk_c_usage = psutil.disk_usage('C:').percent
    disk_d_usage = psutil.disk_usage('D:').percent
    return disk_c_usage, disk_d_usage
def get_net_speed():
    net_io = psutil.net_io_counters()
    upload_speed = convert_bytes(net_io.bytes_sent - get_net_speed.upload_speed_last)
    download_speed = convert_bytes(net_io.bytes_recv - get_net_speed.download_speed_last)
    get_net_speed.upload_speed_last = net_io.bytes_sent
    get_net_speed.download_speed_last = net_io.bytes_recv
    return upload_speed, download_speed
def convert_bytes(bytes):
    mb = bytes / (1024 * 1024)
    return f'{mb:.2f}'
def update_info_labels():
    cpu_usage, ram_usage = get_cpu_ram_info()
    gpu_usage = get_gpu_usage()
    disk_c_usage, disk_d_usage = get_disk_info()
    upload_speed, download_speed = get_net_speed()
    LB_CPU['text'] = f'{cpu_usage}%'
    LB_RAM['text'] = f'{ram_usage}%'
    LB_GPU.config(text=f'{gpu_usage}%')
    LB_DUC['text'] = f'\uf0a0 {disk_c_usage}%'
    LB_DUD['text'] = f'\uf0a0 {disk_d_usage}%'
    Upload_lb['text'] = f' ▲ {upload_speed} '
    Download_lb['text'] = f' ▼ {download_speed} '

    # Set background color based on GPU usage
    if gpu_usage == "0":
        LB_GPU.config(bg="#1d2027" , fg="#00ff21")
    elif float(gpu_usage) < 50:
        LB_GPU.config(bg="#1d2027" , fg="#00ff21")
    elif 10 <= float(gpu_usage) < 50:
        LB_GPU.config(bg="#00ff21" , fg="#000000")
    elif 50 <= float(gpu_usage) < 80:
        LB_GPU.config(bg="#00ff21" , fg="#000000")
    else:
        LB_GPU.config(bg="#00ff21" , fg="#FFFFFF")

    # Set background color based on upload speed
    if upload_speed == "0":
        Upload_lb.config(bg='#1d2027', fg="#FFFFFF")
    elif float(upload_speed) < 0.1:  # Less than 100 KB
        Upload_lb.config(bg='#1d2027', fg="#FFFFFF")
    elif 0.1 <= float(upload_speed) < 0.5:  # 100 KB to 499 KB
        Upload_lb.config(bg='#A8E4A8', fg="#000000")
    elif 0.5 <= float(upload_speed) < 1:  # 500 KB to 1 MB
        Upload_lb.config(bg='#67D567', fg='#000000')  # Normal green
    else:
        Upload_lb.config(bg='#32AB32', fg='#000000')  # Dark green
    # Set background color based on download speed
    if download_speed == "0":
        Download_lb.config(bg='#1d2027' , fg="#FFFFFF")
    elif float(download_speed) < 0.1:  # Less than 100 KB
        Download_lb.config(bg='#1d2027', fg="#FFFFFF")
    elif 0.1 <= float(download_speed) < 0.5:  # 100 KB to 499 KB
        Download_lb.config(bg='#A8E4A8', fg="#000000")
    elif 0.5 <= float(download_speed) < 1:  # 500 KB to 1 MB
        Download_lb.config(bg='#67D567', fg='#000000')  # Normal green
    else:
        Download_lb.config(bg='#32AB32', fg='#000000')  # Dark green

    #        # Write speed information to a text file
    # with open("d:\\netspeed_download_upload.log", "a") as logfile:
    #     logfile.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Download: {download_speed}, Upload: {upload_speed}\n")

    # Change background and foreground color based on usage thresholds
    LB_RAM.config(bg='#ff934b' if ram_usage > 80 else '#1d2027', fg='#1d2027' if ram_usage > 80 else '#ff934b')
    LB_CPU.config(bg='#14bcff' if cpu_usage > 80 else '#1d2027', fg='#1d2027' if cpu_usage > 80 else '#14bcff')
    LB_DUC.config(bg='#f12c2f' if disk_c_usage > 90 else '#044568', fg='#FFFFFF' if disk_c_usage > 90 else '#fff')
    LB_DUD.config(bg='#f12c2f' if disk_d_usage > 90 else '#044568', fg='#FFFFFF' if disk_d_usage > 90 else '#fff')

    ROOT.after(1000, update_info_labels)
# Initialize static variables for network speed calculation
get_net_speed.upload_speed_last = 0
get_net_speed.download_speed_last = 0


#! Clear Button
def clear_screen():
    try:
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        ascii_art = """
##################################################
************* Everything is clean ****************
##################################################
        """
        print(ascii_art)
    except Exception as e:
        print(f"Error clearing screen: {e}")


def get_system_uptime():
    uptime_seconds = psutil.boot_time()
    current_time = datetime.now().timestamp()
    uptime = current_time - uptime_seconds
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(hours), int(minutes), int(seconds)
def format_uptime():
    hours, minutes, seconds = get_system_uptime()
    return f"\udb81\udf8c {hours:02d}:{minutes:02d}:{seconds:02d}"
def update_uptime_label():
    uptime_str = format_uptime()
    uptime_label.configure(text=f"{uptime_str}")
    uptime_label.after(1000, update_uptime_label)



def Lockbox_update_label(LockBox_lb):
    path = "d:/tt/"
    if os.path.exists(path):
        status = "\uf13e"
        color = "#f44336"
    else:
        status = "\uf023"
        color = "#4CAF50"
    LockBox_lb.config(text=status, fg=color, font=("JetBrainsMono NFP", 16, "bold"))
    LockBox_lb.after(1000, lambda: Lockbox_update_label(LockBox_lb))


# def compare_path_file():
#     source_dest_pairs = {
# "komorebi"       :(komorebi_src    ,komorebi_dst    ),
# # "glaze-wm"       :(glazewm_src     ,glazewm_dst     ),
# # "Nilesoft"       :(Nilesoft_src    ,Nilesoft_dst    ),
# # "whkd"           :(whkd_src        ,whkd_dst        ),
# "pwshH"          :(pwshH_src       ,pwshH_dst       ),
# "terminal"       :(terminal_src    ,terminal_dst    ),
# "rclone_config"  :(rclone_src      ,rclone_dst      ),
# "pwsh_profile"   :(pwsh_profile_src,pwsh_profile_dst),
# "ProwlarrDB"        :(ProwlarrDB_src     ,ProwlarrDB_dst     ),
# "RadarrDB"          :(RadarrDB_src       ,RadarrDB_dst       ),
# "SonarrDB"          :(SonarrDB_src       ,SonarrDB_dst       ),
# # "br_cf"          :(br_cf_src       ,br_cf_dst       ),
# # "br_db"          :(br_db_src       ,br_db_dst       ),
# # "Pr_cf"          :(Pr_cf_src       ,Pr_cf_dst       ),
# # "Rr_cf"          :(Rr_cf_src       ,Rr_cf_dst       ),
# # "Sr_cf"          :(Sr_cf_src       ,Sr_cf_dst       ),
# "RssDB"         :(Rss_db_src      ,Rss_db_dst      ),
# "RssCF"         :(Rss_cf_src      ,Rss_cf_dst      ),
#     }
#     is_all_same = True
#     names = []
#     for name, (source, dest) in source_dest_pairs.items():
#         if os.path.isdir(source) and os.path.isdir(dest):
#             dcmp = filecmp.dircmp(source, dest)
#             if dcmp.diff_files or dcmp.left_only or dcmp.right_only:
#                 is_all_same = False
#                 names.append(name)
#         elif os.path.isfile(source) and os.path.isfile(dest):
#             if not filecmp.cmp(source, dest):
#                 is_all_same = False
#                 names.append(name)
#         else:
#             is_all_same = False
#             names.append(name)
#     if is_all_same:
#         emoji = "✅"
#         name = "✅"
#     else:
#         emoji = "❌"
#         names_per_row = 4
#         formatted_names = [", ".join(names[i:i + names_per_row]) for i in range(0, len(names), names_per_row)]
#         name = "\n".join(formatted_names)
#     Changes_Monitor_lb.config(text=f"{name}")
#     Changes_Monitor_lb.after(1000, compare_path_file)


def get_cpu_core_usage():
    # Get CPU usage for each core
    cpu_usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
    return cpu_usage_per_core
def update_cpu_core_bars():
    # Get CPU usage for each core
    cpu_core_usage = get_cpu_core_usage()
    # Update the bars for each CPU core
    for i, usage in enumerate(cpu_core_usage):
        core_bar = cpu_core_bars[i]
        # Clear the previous bar
        core_bar.delete("all")
        # Calculate the half height of the bar based on usage percentage
        bar_height = int((usage / 100) * (BAR_HEIGHT / 2))
        # Determine the color based on usage percentage
        bar_color = determine_color(usage)
        # Draw the bar with the determined color from the center vertically
        core_bar.create_rectangle(0, (BAR_HEIGHT / 2) - bar_height, BAR_WIDTH, (BAR_HEIGHT / 2) + bar_height, fill=bar_color)
    # Schedule the next update
    ROOT.after(1000, update_cpu_core_bars)
def determine_color(usage):
    if usage >= 90:
        return "#8B0000"  # Dark red for usage >= 90%
    elif usage >= 80:
        return "#f12c2f"  # Red for usage >= 80%
    elif usage >= 50:
        return "#ff9282"  # Light red for usage >= 50%
    else:
        return "#14bcff"  # Default color
BAR_WIDTH = 8
BAR_HEIGHT = 25





#! ALL Boxes
ROOT1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT1.pack(side="left", pady=(2,2),padx=(5,1),  anchor="w", fill="x")

ROOT2 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT2.pack(side="right", pady=(2,2),padx=(5,1), anchor="e", fill="x")

#! ██╗     ███████╗███████╗████████╗
#! ██║     ██╔════╝██╔════╝╚══██╔══╝
#! ██║     █████╗  █████╗     ██║
#! ██║     ██╔══╝  ██╔══╝     ██║
#! ███████╗███████╗██║        ██║
#! ╚══════╝╚══════╝╚═╝        ╚═╝

uptime_label=CTkLabel(ROOT1, text="", corner_radius=3, width=100,height=20,  text_color="#6bc0f8",fg_color="#1d2027", font=("JetBrainsMono NFP" ,16,"bold"))
uptime_label.pack(side="left",padx=(0,5),pady=(1,0))

# Load dynamic buttons for ROOT1
for idx, btn_cfg in enumerate(CONFIG.get("buttons_left", [])):
    create_dynamic_button(ROOT1, btn_cfg, "buttons_left", idx)



#! FFMPEG
# FFMPEG_bt = CTkButton(ROOT1, text="\uf07cffmpeg",width=0, command=lambda:switch_to_frame(FR_FFmpeg , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, hover_color="#6824b6", border_color="#000000", fg_color="#1d2027", text_color="#ffdb75")
# FFMPEG_bt.pack(side="left")
# FR_FFmpeg = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# FR_FFmpeg.pack_propagate(True)
# BoxForFFmpeg = tk.Frame(FR_FFmpeg, bg="#1d2027")
# BoxForFFmpeg.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
# back_ffmpeg=tk.Button(BoxForFFmpeg,text="\ueb6f",width=0,bg="#1D2027",fg="#FFFFFF",command=lambda:switch_to_frame (MAIN_FRAME,FR_FFmpeg))
# back_ffmpeg.pack(side="left" )
# def ffmpeg(FR_FFmpeg):
#     Trim_bt          =tk.Button(BoxForFFmpeg,text="Trim"          ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_trim        ); Trim_bt.pack          (side="left",padx=(0,0))
#     Convert_bt       =tk.Button(BoxForFFmpeg,text="Convert"       ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_convert     ); Convert_bt.pack       (side="left",padx=(0,0))
#     Dimension_bt     =tk.Button(BoxForFFmpeg,text="Dimension"     ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_dimension   ); Dimension_bt.pack     (side="left",padx=(0,0))
#     Imagedimension_bt=tk.Button(BoxForFFmpeg,text="Imagedimension",width=0,fg="#FFFFFF",bg="#1D2027", command=lambda: subprocess.Popen(["cmd /c start C:\\@delta\\ms1\\scripts\\ffmpeg\\imgdim.ps1"], shell=True)) ; Imagedimension_bt.pack(side="left",padx=(0,0))
#     Merge_bt         =tk.Button(BoxForFFmpeg,text="Merge"         ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_merge       ); Merge_bt.pack         (side="left",padx=(0,0))
# ffmpeg(FR_FFmpeg)

#! Find
# Find_bt = CTkButton(ROOT1, text="\uf07cfind",width=0, command=lambda:switch_to_frame(FR_Find , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, hover_color="#6824b6", border_color="#000000", fg_color="#1d2027", text_color="#ffdb75")
# Find_bt.pack(side="left")
# FR_Find = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# FR_Find.pack_propagate(True)
# BoxForFind = tk.Frame(FR_Find, bg="#1d2027")
# BoxForFind.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
# back_find=tk.Button(BoxForFind,text="\ueb6f",width=0 ,bg="#1D2027", fg="#FFFFFF", command=lambda:switch_to_frame(MAIN_FRAME,FR_Find))
# back_find.pack(side="left" ,padx=(0,0))
# def find(FR_Find):
#     Search_bt=tk.Label(BoxForFind, text="\uf422",bg="#1d2027",fg="#95c64d",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
#     Search_bt.pack(side="left",padx=(3,0),pady=(0,0))
#     Search_bt.bind("<Button-1>",fzf_search)
#     Search_bt.bind("<Control-Button-1>",edit_fzfSearch)

#     File_bt    =tk.Button(BoxForFind,text="File"       ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_file   ); File_bt.pack   (side="left" ,padx=(0,0))
#     Pattern_bt =tk.Button(BoxForFind,text="Pattern"    ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_pattern); Pattern_bt.pack(side="left" ,padx=(0,0))
#     Size_bt    =tk.Button(BoxForFind,text="Size"       ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_size   ); Size_bt.pack   (side="left" ,padx=(0,0))
#     FZFC_bt    =tk.Button(BoxForFind,text="FZF-C"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_fzf_c       ); FZFC_bt.pack   (side="left" ,padx=(0,0))
#     FZFD_bt    =tk.Button(BoxForFind,text="FZF-D"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_fzf_d       ); FZFD_bt.pack   (side="left" ,padx=(0,0))
#     # ackc_bt    =tk.Button(BoxForFind,text="ACK-C"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_ack_c       ); ackc_bt.pack   (side="left" ,padx=(0,0)) #! removed from reference
#     # ackd_bt    =tk.Button(BoxForFind,text="ACK-D"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_ack_d       ); ackd_bt.pack   (side="left" ,padx=(0,0)) #! removed from reference
# find(FR_Find)

# #! Desktop
# Desktop_bt = CTkButton(ROOT1, text="\uf07cDesktop",width=0, command=lambda:switch_to_frame(FR_Desktop , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0,hover_color="#1dd463", border_width=1, border_color="#FFFFFF", fg_color="#0099ff", text_color="#000000")
# Desktop_bt.pack(side="left")
# FR_Desktop = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# FR_Desktop.pack_propagate(True)
# BoxForDesktop = tk.Frame(FR_Desktop, bg="#1d2027")
# BoxForDesktop.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
# BACK=tk.Button(BoxForDesktop,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,FR_Desktop))
# BACK.pack(side="left" ,padx=(0,0))

# sonarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\sonarr-20x20.png"))
# radarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\radarr-20x20.png"))
# def Folder(FR_Desktop):
#     Sonarr_bt=tk.Label(BoxForDesktop, image=sonarr_img, compound=tk.TOP, text="", height=30, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
#     Sonarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Sonarr"],shell=True)))
#     Sonarr_bt.pack(pady=(0,2), side="left", anchor="w", padx=(0,0))
#     Radarr_bt=tk.Label(BoxForDesktop, image=radarr_img, compound=tk.TOP, text="", height=50, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
#     Radarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Radarr"],shell=True)))
#     Radarr_bt.pack(pady=(0,2), side="left", anchor="w", padx=(0,0))
# Folder(FR_Desktop)

# #! Worspace_1
# WorkSpace_1 = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# WorkSpace_1.pack_propagate(True)
# Enter_WS1 = CTkButton(ROOT1, text="\uf07cP", width=0, hover_color="#1dd463", command=lambda:switch_to_frame(WorkSpace_1 , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, border_color="#000000", fg_color="#bff130", text_color="#000")
# Enter_WS1.pack(side="left", padx=(1,1))
# BOX = tk.Frame(WorkSpace_1, bg="#1D2027")
# BOX.pack(side="top", pady=(4,2),padx=(5,1), anchor="center", fill="x")
# BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,WorkSpace_1))
# BACK.pack(side="left" ,padx=(0,0))

# #! EDIT SPACE
# EDIT_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# EDIT_FRAME.pack_propagate(True)
# ENTER_FRAME = CTkButton(ROOT1, text="\uf07cedit", width=0, command=lambda:switch_to_frame(EDIT_FRAME , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, hover_color="#6824b6", border_color="#000000", fg_color="#1d2027", text_color="#ffdb75")
# ENTER_FRAME.pack(side="left", padx=(1,1))
# BOX = tk.Frame(EDIT_FRAME, bg="#1D2027")
# BOX.pack(side="top", pady=(4,2),padx=(5,1), anchor="center", fill="x")
# BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,EDIT_FRAME))
# BACK.pack(side="left" ,padx=(0,0))
# def Folder(EDIT_FRAME):
#     MYPYGUI=tk.Button(BOX,text="MYPYGUI",width=0 ,fg="#ffffff", bg="#204892", command=lambda:(subprocess.Popen(["cmd /c Code C:\\@delta\\ms1\\mypygui.py"],shell=True), switch_to_frame(MAIN_FRAME,EDIT_FRAME)))
#     MYPYGUI.pack(side="left" ,padx=(0,0))
#     AHKEDIT=tk.Button(BOX,text="AHKSCRIPT",width=0 ,fg="#020202", bg="#5f925f", command=lambda:(subprocess.Popen(["cmd /c Code C:\\@delta\\ms1\\ahk_v2.ahk"],shell=True), switch_to_frame(MAIN_FRAME,EDIT_FRAME)))
#     AHKEDIT.pack(side="left" ,padx=(0,0))
#     KOMOREBIC=tk.Button(BOX,text="Komoreb",width=0 ,fg="#080808", bg="#7fc8f3", command=lambda:(subprocess.Popen(["cmd /c Code C:\\Users\\nahid\\komorebi.json"],shell=True), switch_to_frame(MAIN_FRAME,EDIT_FRAME)))
#     KOMOREBIC.pack(side="left" ,padx=(0,0))
#     MYHOMEHTML=tk.Button(BOX,text="myhome.html",width=0 ,fg="#080808", bg="#c7d449", command=lambda:(subprocess.Popen(["cmd /c Code C:\\ms2\\myhome.html"],shell=True), switch_to_frame(MAIN_FRAME,EDIT_FRAME)))
#     MYHOMEHTML.pack(side="left" ,padx=(0,0))
# Folder(EDIT_FRAME)

#! Function SPACE
# FUNCTION_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# FUNCTION_FRAME.pack_propagate(True)
# ENTER_FRAME = CTkButton(ROOT1, text="\uf07cF", width=0, command=lambda:switch_to_frame(FUNCTION_FRAME , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, hover_color="#6824b6", border_color="#000000", fg_color="#1d2027", text_color="#ffdb75")
# ENTER_FRAME.pack(side="left", padx=(1,1))
# BOX = tk.Frame(FUNCTION_FRAME, bg="#1D2027")
# BOX.pack(side="top", pady=(4,2),padx=(5,1), anchor="center", fill="x")
# BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,FUNCTION_FRAME))
# BACK.pack(side="left" ,padx=(0,0))
# def Folder(FUNCTION_FRAME):
#         # Function to simulate key press
#         # def send_f13():
#         #     keyboard.send('f13')
#         # F13=tk.Button(BOX,text="F13",width=0 ,fg="#ffffff", bg="#204892", command=send_f13)
#         # F13.pack(side="left" ,padx=(0,0))

#         # def send_f15():
#         #     keyboard.send('f15')
#         # F15=tk.Button(BOX,text="F15",width=0 ,fg="#ffffff", bg="#204892", command=send_f15)
#         # F15.pack(side="left" ,padx=(0,0))

#         def powertoys_ruler():
#             keyboard.press_and_release('win+shift+m')
#         TOY_RULER=tk.Button(BOX,text="\uee11",width=0 ,fg="#ffffff", bg="#204892", command=powertoys_ruler)
#         TOY_RULER.pack(side="left" ,padx=(0,0))

#         def powertoys_mousecrosshair():
#             keyboard.press_and_release('win+alt+p')
#         TOY_MCROSSHAIR=tk.Button(BOX,text="\uf245",width=0 ,fg="#ffffff", bg="#204892", command=powertoys_mousecrosshair)
#         TOY_MCROSSHAIR.pack(side="left" ,padx=(0,0))

#         def powertoys_TextExtract():
#             keyboard.press_and_release('win+shift+f')
#         TOY_TEXTEXTRACT=tk.Button(BOX,text="\ueb69",width=0 ,fg="#ffffff", bg="#204892", command=powertoys_TextExtract)
#         TOY_TEXTEXTRACT.pack(side="left" ,padx=(0,0))

#         def capture2text():
#             is_running = any(proc.name() == "Capture2Text.exe" for proc in psutil.process_iter())
#             if not is_running:
#                 subprocess.Popen(r"C:\Users\nahid\scoop\apps\Capture2Text\current\Capture2Text.exe")
#                 time.sleep(2)  # Wait 2 seconds if the app had to be started
#             else:
#                 time.sleep(1)  # Wait 1 second if the app is already running
#             keyboard.press_and_release('win+ctrl+alt+shift+q')
#         CAPTURE2_TEXTEXTRACT=tk.Button(BOX,text="\ueb69",width=0 ,fg="#db1725", bg="#204892", command=capture2text)
#         CAPTURE2_TEXTEXTRACT.pack(side="left" ,padx=(0,0))

# Folder(FUNCTION_FRAME)

#! Worspace_3
SEPARATOR=tk.Label(ROOT1,text="[",bg="#1d2027",fg="#009fff",height=0,width=0,relief="flat",font=("JetBrainsMono NFP",18,"bold"))
SEPARATOR.pack(side="left",padx=(3,0),pady=(0,0))

CONFIG = load_config()

#! Github status
# Define your repositories here
queue = Queue()
repos = CONFIG.get("git_repos", [])

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

#! For Github Status
status_thread = threading.Thread(target=update_status, daemon=True)
gui_thread = threading.Thread(target=update_gui, daemon=True)
status_thread.start()
gui_thread.start()

SEPARATOR=tk.Label(ROOT1,text="]",bg="#1d2027",fg="#009fff",height=0,width=0,relief="flat",font=("JetBrainsMono NFP",18,"bold"))
SEPARATOR.pack(side="left",padx=(0,0),pady=(0,0))

# sonarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\sonarr-20x20.png"))
# Sonarr_bt=tk.Label(ROOT1, image=sonarr_img, compound=tk.TOP, text="", height=30, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
Sonarr_bt=tk.Label(ROOT1, text="\udb81\udff4", height=0, width=0, bg="#000000", fg="#ffdb75", bd=0, highlightthickness=0, anchor="center", font=("Jetbrainsmono nfp", 20, "bold"))
Sonarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Sonarr"],shell=True)))
Sonarr_bt.pack(pady=(2,2), side="left", anchor="w", padx=(1,1))

# radarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\radarr-20x20.png"))
# Radarr_bt=tk.Label(ROOT1, image=radarr_img, compound=tk.TOP, text="", height=50, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
Radarr_bt=tk.Label(ROOT1, text="\udb83\udfce", height=0, width=0, bg="#000000", fg="#ffdb75", bd=0, highlightthickness=0, anchor="center", font=("Jetbrainsmono nfp", 20, "bold"))
Radarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Radarr"],shell=True)))
Radarr_bt.pack(pady=(2,2), side="left", anchor="w", padx=(1,10))

# Changes_Monitor_lb = tk.Label(ROOT1, text="", bg="#1d2027", fg="#68fc2d")
# Changes_Monitor_lb.pack(side="left",padx=(0,0),pady=(0,0))
# compare_path_file()
 



# Command config
# Ensure log folder exists
LOG_DIR = r"C:\Users\nahid\script_output\rclone"
os.makedirs(LOG_DIR, exist_ok=True)

commands = CONFIG.get("rclone_commands", {})

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
def create_rclone_gui():
    for key, cfg in commands.items():
        if "id" not in cfg: cfg["id"] = key
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
        lbl.bind("<Shift-Button-1>", lambda e, c=cfg: open_edit_gui(c, "rclone_commands")) # Shift+Click edit

        check_and_update(lbl, cfg)

# Call GUI init
create_rclone_gui()


# ms1_rclone_o0 = tk.Label(ROOT1,text="ms1", bg="#1d2027", fg="#cc5907", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
# ms1_rclone_o0.pack(side="left", padx=(0, 0), pady=(0, 0))
# ms1_rclone_o0.bind( "<Button-1>", lambda event=None: run_command( r'rclone sync C:/@delta/ms1/ o0:/ms1/ --exclude ".git/**" --exclude "__pycache__/**" -P --fast-list' ))


#! ██████╗ ██╗ ██████╗ ██╗  ██╗████████╗
#! ██╔══██╗██║██╔════╝ ██║  ██║╚══██╔══╝
#! ██████╔╝██║██║  ███╗███████║   ██║
#! ██╔══██╗██║██║   ██║██╔══██║   ██║
#! ██║  ██║██║╚██████╔╝██║  ██║   ██║
#! ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝


# import requests
# import tkinter as tk
# import re

# ANDROID_URL = "http://mi9t:5002"
# LOW_BATTERY_THRESHOLD = 15
# UPDATE_INTERVAL = 60000  # 60 seconds
# def fetch_battery_percentage():
#     try:
#         response = requests.get(ANDROID_URL)
#         if response.ok:
#             match = re.search(r'(\d+)\s*%', response.text)
#             if match:
#                 return int(match.group(1))
#     except Exception as e:
#         print(f"Error fetching battery: {e}")
#     return None

# def update_status_battery_mi9t():
#     percent = fetch_battery_percentage()
#     if percent is not None:
#         Android_mi9t_battery.config(text=f"mi9t {percent}%")
#         if percent == 100:
#             Android_mi9t_battery.config(fg="black", bg="#58a6ff")
#         elif percent < LOW_BATTERY_THRESHOLD:
#             Android_mi9t_battery.config(fg="white", bg="red")
#         else:
#             Android_mi9t_battery.config(fg="black", bg="#abec72")
#     else:
#         Android_mi9t_battery.config(
#             text="Error fetching battery",
#             fg="white",
#             bg="gray"
#         )
#     ROOT2.after(UPDATE_INTERVAL, update_status_battery_mi9t)

# Android_mi9t_battery = tk.Label(ROOT2, text="Loading...", font=("Jetbrainsmono nfp", 10, "bold"), width=10)
# Android_mi9t_battery.pack(side="left", padx=(3,10), pady=(0,0))
# # Start updates
# update_status_battery_mi9t()




# UPDATE_INTERVAL_SEC = 60  # 600 seconds = 10 minutes
# PING_COMMAND = ["ping", "-n", "1", "-w", "1000", "192.168.0.103"]  # -n 1 = once, -w 1000 = 1s timeout

# def ping_mi9t():
#     def run_ping():
#         try:
#             result = subprocess.run(PING_COMMAND, capture_output=True, text=True, timeout=5)
#             output = result.stdout + result.stderr

#             if "Reply from" in output:
#                 update_ui("mi9t ✓", "black", "#abec72")  # green
#             elif "Request timed out" in output or "Destination host unreachable" in output:
#                 update_ui("mi9t ✗", "white", "red")  # red
#             else:
#                 update_ui("mi9t ?", "white", "gray")  # unknown
#         except Exception as e:
#             update_ui("Error", "white", "gray")
#             print(f"Ping error: {e}")
#         finally:
#             ROOT2.after(UPDATE_INTERVAL_SEC * 1000, ping_mi9t)

#     threading.Thread(target=run_ping, daemon=True).start()

# def update_ui(text, fg, bg):
#     Android_mi9t_status.config(text=text, fg=fg, bg=bg)


# Android_mi9t_status = tk.Label(ROOT2, text="Loading...", font=("Jetbrainsmono NFP", 10, "bold"), width=10)
# Android_mi9t_status.pack(side="left", padx=(3,10), pady=(0,0))

# ping_mi9t()







cpu_core_frame =CTkFrame(ROOT2,corner_radius=5,bg_color="#1d2027",border_width=1,border_color="#000000", fg_color="#fff")
cpu_core_frame.pack(side="left",padx=(3,0),pady=(0,0))

Download_lb=tk.Label(ROOT2,bg="#000000",fg="#080505",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
Download_lb.pack(side="left",padx=(3,0 ),pady=(0,0))
Download_lb.bind("<Button-1>", lambda event: subprocess.Popen(["sniffnet"], shell=True))

Upload_lb=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
Upload_lb.pack(side="left",padx=(3,0 ),pady=(0,0))
Upload_lb.bind("<Button-1>", lambda event: subprocess.Popen(["sniffnet"], shell=True))

LB_CPU=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#1b8af1",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_CPU.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_CPU.bind( "<Button-1>", lambda event=None: subprocess.Popen([sys.executable, r'C:\@delta\ms1\scripts\process\process_viewer.py']))
LB_CPU.bind("<Control-Button-1>",lambda event=None: subprocess.Popen(['code', r'C:\@delta\ms1\scripts\process\process_viewer.py']))
# LB_CPU.bind("<Button-1>", lambda event: subprocess.Popen( [r"C:\WINDOWS\SYSTEM32\cmd.exe", "/c", "start" ,"powershell", "-ExecutionPolicy", "Bypass", "-File", r"C:\@delta\ms1\scripts\pk.ps1"], shell=True))
# LB_CPU.bind("<Button-3>", lambda event: subprocess.Popen( [r"C:\WINDOWS\SYSTEM32\cmd.exe", "/c", "start" ,"powershell", "-ExecutionPolicy", "Bypass", "-File", r"C:\@delta\ms1\scripts\pk2.ps1"], shell=True))
# LB_CPU.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\pk.ps1"], shell=True))
# LB_CPU.bind("<Control-Button-3>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\pk2.ps1"], shell=True))

LB_GPU=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#00ff21",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_GPU.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_GPU.bind("<Button-1>",None)

LB_RAM=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#f08d0c",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_RAM.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_RAM.bind("<Button-1>",None)

LB_DUC=tk.Label(ROOT2,height=0,width =8,relief="flat",highlightthickness=1,highlightbackground="#1b8af1",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_DUC.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_DUC.bind("<Button-1>",None)

LB_DUD=tk.Label(ROOT2,height=0,width =8,relief="flat",highlightthickness=1,highlightbackground="#1b8af1",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_DUD.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_DUD.bind("<Button-1>",None)

# Topmost_lb=tk.Label(ROOT2,text="\udb81\udc03",bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",12,"bold"))
# Topmost_lb.pack(side="left",padx=(3,0),pady=(0,0))
# Topmost_lb.bind  ("<Button-1>",lambda event:toggle_checking())

# CLEAR=tk.Label(ROOT2, text="\ueabf",bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",12,"bold"))
# CLEAR.pack(side="left",padx=(3,0),pady=(0,0))
# CLEAR.bind("<Button-1>",lambda event:clear_screen())











countdown_active = False
shutdown_thread = None
alarm_window = None
blinking = False
last_countdown_type = None  # To store the last chosen type (1 for alarm, 2 for shutdown)
last_countdown_minutes = None  # To store the last entered minutes

def shutdown_timer(minutes):
    global countdown_active
    countdown_time = minutes * 60
    while countdown_time > 0:
        if not countdown_active:
            time_left_label.config(text="Timer")
            return
        minutes_left = int(countdown_time) // 60
        seconds_left = int(countdown_time) % 60
        time_left_label.config(text=f"\udb86\udee1:{minutes_left:02}:{seconds_left:02}")
        time_left_label.update()
        time.sleep(1)
        countdown_time -= 1
    if countdown_active:
        os.system("shutdown /s /f /t 1")
        countdown_active = False
        time_left_label.config(text="Timer")

def alarm_timer(minutes):
    global countdown_active
    countdown_time = minutes * 60
    while countdown_time > 0:
        if not countdown_active:
            time_left_label.config(text="Timer")
            return
        minutes_left = int(countdown_time) // 60
        seconds_left = int(countdown_time) % 60
        time_left_label.config(text=f"\udb86\udee1:{minutes_left:02}:{seconds_left:02}")
        time_left_label.update()
        time.sleep(1)
        countdown_time -= 1
    if countdown_active:
        show_big_alarm()
        countdown_active = False
        time_left_label.config(text="Timer")

# Show blinking alarm in a new window
def show_big_alarm():
    global alarm_window, blinking

    alarm_window = tk.Toplevel(ROOT)
    alarm_window.title("ALARM!")
    alarm_window.geometry("600x300")
    alarm_window.configure(bg="#1d2027")
    alarm_window.attributes("-topmost", True)
    alarm_window.overrideredirect(True)
    alarm_window.resizable(False, False)
    width = alarm_window.winfo_width()
    height = alarm_window.winfo_height()
    x = (alarm_window.winfo_screenwidth() // 2) - (width // 2)
    y = (alarm_window.winfo_screenheight() // 2) - (height // 2)
    alarm_window.geometry(f'{width}x{height}+{x}+{y}')

    label = tk.Label(
        alarm_window,
        text="ALARM! Time's up!",
        font=("JetBrainsMono NFP", 36, "bold"),
        fg="#ff0000",
        bg="#1d2027"
    )
    label.pack(expand=True)

    blinking = True
    blink_state = True

    def blink():
        nonlocal blink_state
        if blinking:
            label.config(fg="#ff0000" if blink_state else "#00aaff")
            blink_state = not blink_state
            alarm_window.after(500, blink)

    def stop_alarm(event=None):
        global blinking
        blinking = False
        alarm_window.destroy()

    alarm_window.bind("<Button-1>", stop_alarm)
    blink()

# Custom input for countdown minutes
def get_countdown_input():
    input_window = tk.Toplevel(ROOT)
    input_window.title("Enter Countdown Minutes")
    input_window.geometry("300x100")
    input_window.grab_set()

    # Center the window on the screen
    input_window.update_idletasks()
    w = 300
    h = 100
    screen_width = input_window.winfo_screenwidth()
    screen_height = input_window.winfo_screenheight()
    x = (screen_width // 2) - (w // 2)
    y = (screen_height // 2) - (h // 2)
    input_window.geometry(f"{w}x{h}+{x}+{y}")

    label = tk.Label(input_window, text="Enter minutes for the countdown:")
    label.pack(pady=5)

    minutes_entry = tk.Entry(input_window, font=("JetBrainsMono NFP", 14))
    minutes_entry.pack(pady=5)
    minutes_entry.focus()

    result = {"minutes": None}

    def on_submit(event=None):  # Accept optional event for key binding
        try:
            val = float(minutes_entry.get())
            if val > 0:
                result["minutes"] = val
                input_window.destroy()
        except ValueError:
            error_label.config(text="Enter a valid number > 0")

    submit_btn = tk.Button(input_window, text="Start", command=on_submit)
    submit_btn.pack(pady=5)

    error_label = tk.Label(input_window, text="", fg="red")
    error_label.pack()

    # Bind Enter key to submit
    minutes_entry.bind("<Return>", on_submit)

    input_window.wait_window()
    return result["minutes"]


# Main click handler
def start_countdown_option(event=None):
    global countdown_active, shutdown_thread, last_countdown_type, last_countdown_minutes
    choice = simpledialog.askinteger("Select Timer Type", "Choose an option:\n1 - Countdown Alarm\n2 - Countdown Shutdown")
    if choice == 1:
        if countdown_active:
            countdown_active = False
            time_left_label.config(text="Timer")
            return
        minutes = get_countdown_input()
        if minutes:
            countdown_active = True
            last_countdown_type = 1
            last_countdown_minutes = minutes
            shutdown_thread = threading.Thread(target=alarm_timer, args=(minutes,))
            shutdown_thread.start()
            time_left_label.config(text=f"\udb86\udee1:{minutes:02}:00")
    elif choice == 2:
        if countdown_active:
            countdown_active = False
            time_left_label.config(text="Timer")
            return
        minutes = get_countdown_input()
        if minutes:
            countdown_active = True
            last_countdown_type = 2
            last_countdown_minutes = minutes
            shutdown_thread = threading.Thread(target=shutdown_timer, args=(minutes,))
            shutdown_thread.start()
            time_left_label.config(text=f"\udb86\udee1:{minutes:02}:00")

# Function to run the last used countdown
def run_last_countdown():
    global countdown_active, shutdown_thread, last_countdown_type, last_countdown_minutes
    if last_countdown_type is None or last_countdown_minutes is None:
        # Optionally, inform the user that no previous countdown exists
        print("No previous countdown to run.") # Or show a message box
        return

    if countdown_active:
        countdown_active = False
        time_left_label.config(text="Timer")
        # Give a moment for the current thread to stop if it's running
        if shutdown_thread and shutdown_thread.is_alive():
            shutdown_thread.join(timeout=1) # Wait briefly for the thread to terminate
        time.sleep(0.1) # Small delay to ensure state update

    countdown_active = True
    if last_countdown_type == 1:
        shutdown_thread = threading.Thread(target=alarm_timer, args=(last_countdown_minutes,))
        shutdown_thread.start()
        time_left_label.config(text=f"Time left: {int(last_countdown_minutes):02}:00 (Last Alarm)")
    elif last_countdown_type == 2:
        shutdown_thread = threading.Thread(target=shutdown_timer, args=(last_countdown_minutes,))
        shutdown_thread.start()
        time_left_label.config(text=f"Time left: {int(last_countdown_minutes):02}:00 (Last Shutdown)")


# Add this to your layout wherever your buttons/widgets go
time_left_label = tk.Label(
    ROOT2,
    text="\udb86\udee1",
    font=("JetBrainsMono NFP", 16, "bold"),
    fg="#fc6a35",
    bg="#1d2027",
    cursor="hand2",
    relief="flat"
)
time_left_label.pack(side="left", padx=(10, 0), pady=(0, 0))
time_left_label.bind("<Button-1>", start_countdown_option)

# New "Run Last" button
run_last_button = tk.Button(
    ROOT2,
    text="\udb86\udee5",
    font=("JetBrainsMono NFP", 16),
    command=run_last_countdown,
    fg="#50fa7b",
    bg="#1d2027",
    activeforeground="#ffffff",
    activebackground="#2e7d32",
    relief="flat"
)
run_last_button.pack(side="left", padx=(0, 0), pady=(0, 0))









def force_shutdown(event):
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to shutdown?")
    if confirmed:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
        # subprocess.run(["shutdown", "/s", "/t", "0"])
def force_restart(event):
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to restart?")
    if confirmed:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])
        # subprocess.run(["shutdown", "/r", "/t", "0"])

# Load dynamic buttons for ROOT2
for idx, btn_cfg in enumerate(CONFIG.get("buttons_right", [])):
    create_dynamic_button(ROOT2, btn_cfg, "buttons_right", idx)

LB_R=None # Dummy to avoid errors if referenced elsewhere
LB_XXX=None # Dummy to avoid errors if referenced elsewhere

#! Slider Left
#! Slider Right


cpu_core_bars = []
for i in range(psutil.cpu_count()):
    frame = CTkFrame(cpu_core_frame, bg_color="#1d2027")
    frame.pack(side="left", padx=(0, 0), pady=0)
    core_bar = CTkCanvas(frame, bg="#333333", width=BAR_WIDTH, height=BAR_HEIGHT, highlightthickness=0)
    core_bar.pack(side="top")
    cpu_core_bars.append(core_bar)
update_cpu_core_bars()



update_uptime_label()
update_info_labels()
# check_window_topmost()
# Lockbox_update_label(LockBox_lb)
calculate_time_to_appear(start_time)

ROOT.mainloop()
