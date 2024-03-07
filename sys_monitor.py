import importlib
import subprocess

#? https://pypi.org/project/pretty-errors/


required_libraries = [
    "ctypes",
    "datetime",
    "os",
    "PIL",
    "psutil",
    "pyadl",
    "pyautogui",
    "shutil",
    "subprocess",
    "threading",
    "time",
    "tkinter",
    # "tkinter.messagebox",
    # "tkinter.ttk",
]

def install_missing_libraries():
    for lib in required_libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            print(f"Installing {lib}...")
            subprocess.check_call(["pip", "install", lib])

# Call the function to install missing libraries
install_missing_libraries()

#! Now import the libraries
# from tkinter import PhotoImage
# import shutil
# import tksvg
# import win32gui
from datetime import datetime
from PIL import Image, ImageTk
from pyadl import ADLManager
from time import strftime
from tkinter import Canvas, Scrollbar
from tkinter import messagebox
from tkinter import ttk
import ctypes
import os
import psutil
import pyautogui
import subprocess
import threading
import time
import tkinter as tk


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

# Vaiables to track the position of the mouse when clicking​⁡
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

def M1_hold_release(parent, text, command_on_release, **kwargs):
    def on_press(event):
        nonlocal previous_bg_color, previous_fg_color
        button.config(relief="flat")
        previous_bg_color = button.cget("bg")  # Store the previous background color
        previous_fg_color = button.cget("fg")  # Store the previous foreground color
        button.config(bg="black")
        button.config(fg="yellow")

    def on_release(event):
        button.config(relief="flat")
        command_on_release()
        # Restore the previous background and foreground color
        if previous_bg_color:
            button.config(bg=previous_bg_color)
            button.config(fg=previous_fg_color)

    previous_bg_color = None  # Store the previous background color
    previous_fg_color = None  # Store the previous foreground color
    button = tk.Label(parent, text=text, **kwargs)
    button.bind("<ButtonPress-1>", on_press)
    button.bind("<ButtonRelease-1>", on_release)
    button.pack(pady=2, padx=0)
    return button

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

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
def check_window_topmost():
    if not ROOT.attributes('-topmost'):
        ROOT.attributes('-topmost', True)
    ROOT.after(500, check_window_topmost)
# Call the function to check window topmost status periodically
check_window_topmost()
#!############################################################


# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Add bindings to make the window movable
ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

# # Calculate the screen width and height
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

#? START of alts
#! alt 1 (original)
# Calculate the x and y coordinates to center the window
x = screen_width - 520   # 400 is the width of your window higher means left side lower means right side
y = screen_height//2 - 855//2  # 700 is the height of your window higher means top side lower means bottom side
# Set the geometry of the window
ROOT.geometry(f"520x800+{x}+{y}") #! overall size of the window

#! alt 2 (modified)

# # Calculate the x and y coordinates to center the window
# # x_coordinate = 1420
# x_coordinate = 0
# y_coordinate = 162
# ROOT.geometry(f"500x700+{x_coordinate}+{y_coordinate}") # Overall size of the window

# #! alt 3 (modified start as minimized L)
# x_coordinate = 0
# window_height = 36  # Assuming the window height is 38 pixels
# y_coordinate = screen_height - window_height
# # Set the window geometry
# ROOT.geometry(f"500x36+{x_coordinate}+{y_coordinate}")
#? END of alts

#?  ██████╗  ██████╗  ██████╗ ████████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#?  ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#?  ██████╔╝██║   ██║██║   ██║   ██║       █████╗  ██████╔╝███████║██╔████╔██║█████╗
#?  ██╔══██╗██║   ██║██║   ██║   ██║       ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#?  ██║  ██║╚██████╔╝╚██████╔╝   ██║       ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#?  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

#! Close Window
def close_window(event=None):
    ROOT.destroy()

#! Resize Window
def toggle_window_size(size):
    global window_state
    global x_coordinate  # Make these variables accessible within the function
    global y_coordinate
    if size == '◀':
        ROOT.geometry('112x30')
        ROOT.configure(bg='red')
        LB_S.config(text='◀', bg="#1d2027", fg="#26b2f3", height=1, width=2, font=("ink free", 10, "bold"))
        LB_L.config(text='▼', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("agency", 10, "bold"))
        LB_M.config(text='■', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("calibri", 10, "bold"))
        window_state = 'small'
        x_coordinate = 0
        window_height = 30  # Assuming the window height is 38 pixels
        y_coordinate = screen_height - window_height

    elif size == '▼':
        ROOT.geometry('520x30')
        ROOT.configure(bg='red')
        LB_S.config(text='◀', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("ink free", 10, "bold"))
        LB_L.config(text='▼', bg="#1d2027", fg="#26b2f3", height=1, width=2, font=("agency", 10, "bold"))
        LB_M.config(text='■', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("calibri", 10, "bold"))
        window_state = 'medium'
        x_coordinate = 0
        window_height = 30  # Assuming the window height is 38 pixels
        y_coordinate = screen_height - window_height
        
    elif size == '■':
        ROOT.geometry('520x800')
        ROOT.configure(bg='#1d2027')
        LB_S.config(text='◀', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("ink free", 10, "bold"))
        LB_L.config(text='▼', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("agency", 10, "bold"))
        LB_M.config(text='■', bg="#1d2027", fg="#26b2f3", height=1, width=2, font=("calibri", 10, "bold"))
        window_state = 'large'
        x_coordinate = screen_width - 520
        y_coordinate = screen_height//2 - 855//2
    ROOT.focus_force()
    ROOT.update_idletasks()
    ROOT.geometry(f'{ROOT.winfo_width()}x{ROOT.winfo_height()}+{x_coordinate}+{y_coordinate}')

def on_key_press(event):
    if event.keysym == 'Left':
        toggle_window_size('◀')
    elif event.keysym == 'Down':
        toggle_window_size('▼')
    elif event.keysym == 'Up':
        toggle_window_size('■')
# Bind arrow key events to toggle window size
ROOT.bind("<Left>", on_key_press)
ROOT.bind("<Down>", on_key_press)
ROOT.bind("<Up>", on_key_press)

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
    LB_DUC['text'] = f'{disk_c_usage}%'
    LB_DUD['text'] = f'{disk_d_usage}%'
    LB_UPLOAD['text'] = f' ▲ {upload_speed} '
    LB_DWLOAD['text'] = f' ▼ {download_speed} '

    # Set background color based on GPU usage
    if gpu_usage == "0":
        LB_GPU.config(bg="#1d2027" , fg="#00ff21")
    elif float(gpu_usage) < 25:
        LB_GPU.config(bg="#1d2027" , fg="#00ff21")
    elif 10 <= float(gpu_usage) < 50:
        LB_GPU.config(bg="#ff9282" , fg="#000000")
    elif 50 <= float(gpu_usage) < 80:
        LB_GPU.config(bg="#ff6b54" , fg="#000000")
    else:
        LB_GPU.config(bg="#ff3010" , fg="#FFFFFF")

    # Set background color based on upload speed
    if upload_speed == "0":
        LB_UPLOAD.config(bg='#1d2027', fg="#FFFFFF")
    elif float(upload_speed) < 0.1:  # Less than 100 KB
        LB_UPLOAD.config(bg='#1d2027', fg="#FFFFFF")
    elif 0.1 <= float(upload_speed) < 0.5:  # 100 KB to 499 KB
        LB_UPLOAD.config(bg='#A8E4A8', fg="#000000")
    elif 0.5 <= float(upload_speed) < 1:  # 500 KB to 1 MB
        LB_UPLOAD.config(bg='#67D567', fg='#000000')  # Normal green
    else:
        LB_UPLOAD.config(bg='#32AB32', fg='#000000')  # Dark green
    # Set background color based on download speed
    if download_speed == "0":
        LB_DWLOAD.config(bg='#1d2027' , fg="#FFFFFF")
    elif float(download_speed) < 0.1:  # Less than 100 KB
        LB_DWLOAD.config(bg='#1d2027', fg="#FFFFFF")
    elif 0.1 <= float(download_speed) < 0.5:  # 100 KB to 499 KB
        LB_DWLOAD.config(bg='#A8E4A8', fg="#000000")
    elif 0.5 <= float(download_speed) < 1:  # 500 KB to 1 MB
        LB_DWLOAD.config(bg='#67D567', fg='#000000')  # Normal green
    else:
        LB_DWLOAD.config(bg='#32AB32', fg='#000000')  # Dark green

    #        # Write speed information to a text file
    # with open("d:\\netspeed_download_upload.log", "a") as logfile:
    #     logfile.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Download: {download_speed}, Upload: {upload_speed}\n")

    # Change background and foreground color based on usage thresholds
    LB_RAM.config(bg='#f12c2f' if ram_usage > 80 else '#1d2027', fg='#FFFFFF' if ram_usage > 80 else '#ff934b')
    LB_CPU.config(bg='#f12c2f' if cpu_usage > 80 else '#1d2027', fg='#FFFFFF' if cpu_usage > 80 else '#14bcff')
    LB_DUC.config(bg='#f12c2f' if disk_c_usage > 90 else '#79828b', fg='#FFFFFF' if disk_c_usage > 90 else '#1d2027')
    LB_DUD.config(bg='#f12c2f' if disk_d_usage > 90 else '#79828b', fg='#FFFFFF' if disk_d_usage > 90 else '#1d2027')

    ROOT.after(1000, update_info_labels)
# Initialize static variables for network speed calculation
get_net_speed.upload_speed_last = 0
get_net_speed.download_speed_last = 0

def git_sync(event=None):
    subprocess.Popen(["powershell", "C:\\ms1\\scripts\\Github\\ms1u.ps1 ; C:\\ms1\\scripts\\Github\\ms2u.ps1"])

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

#! Github status
def check_git_status(git_path, status_label):
    if not os.path.exists(git_path):
        status_label.config(text="Invalid path")
        return
    os.chdir(git_path)
    git_status = subprocess.run(["git", "status"], capture_output=True, text=True)
    if "nothing to commit, working tree clean" in git_status.stdout:
        status_label.config(fg="#00ff21", text="✔️")
    else:
        status_label.config(fg="#fe1616", text="❌")
def show_git_changes(git_path):
    if not os.path.exists(git_path):
        print("Invalid path")
        return
    os.chdir(git_path)
    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", "git status"])
def update_status():
    while True:
        check_git_status("C:\\ms1", STATUS_MS1)
        check_git_status("C:\\ms2", STATUS_MS2)
        # Update the status every second
        time.sleep(1)
def extra_bar(event=None):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\python\\bar_1.py", "-WindowStyle", "Hidden"])

BOX_ROW_ROOT = tk.Frame(ROOT, bg="#1d2027") ; BOX_ROW_ROOT.pack(side="top", anchor="e", pady=(2,2),padx=(5,3))

def create_label1(
                  parent,
                  bg_color,
                  fg_color,
                  width,
                  height,
                  relief,
                  padx_label,
                  pady_label,
                  side,
                  anchor,
                  padx_pack,
                  pady_pack,
                  ht,
                  htc,
                  font,
                  text,
                  ):
    label = tk.Label(parent, text=text, bg=bg_color, fg=fg_color, width=width, height=height, relief=relief, font=font, padx=padx_label, pady=pady_label, highlightthickness=ht, highlightcolor=htc)
    label.pack(side=side, anchor=anchor, padx=padx_pack, pady=pady_pack)
    return label

label_properties = [
(BOX_ROW_ROOT,"#1d2027","#ff0000","2","1","flat",1,0,"right","e", (0,1),(0,0), 0,"#FFFFFF", ("times"    ,10,"bold"),"X")  ,
(BOX_ROW_ROOT,"#1d2027","#26b2f3","2","1","flat",1,0,"right","e", (1,1),(0,2), 0,"#FFFFFF", ("calibri"  ,10,"bold"),"■")  ,
(BOX_ROW_ROOT,"#1d2027","#FFFFFF","2","1","flat",1,0,"right","e", (1,1),(0,0), 0,"#FFFFFF", ("agency"   ,10,"bold"),"▼")  ,
(BOX_ROW_ROOT,"#1d2027","#FFFFFF","2","1","flat",1,0,"right","e", (1,1),(0,0), 0,"#FFFFFF", ("ink free" ,10,"bold"),"◀")  ,
(BOX_ROW_ROOT,"#000000","#FFFFFF","1","1","flat",0,0,"right","e", (1,1),(0,0), 1,"#FFFFFF", ("Times"    ,10,"bold"),"+")  ,
(BOX_ROW_ROOT,"#1d2027","#00FF00","2","1","flat",1,0,"left" ,"e", (0,3),(0,0), 0,"#FFFFFF", ("agency"   ,10,"bold"),"⭕")  ,
(BOX_ROW_ROOT,"#1d2027","#FFFFFF","2","1","flat",1,0,"left" ,"e", (0,3),(0,0), 0,"#FFFFFF", ("agency"   ,10,"bold"),"⚠️") ,
(BOX_ROW_ROOT,"#1d2027","#FFFFFF","2","1","flat",1,0,"left" ,"e", (0,3),(0,0), 0,"#FFFFFF", ("agency"   ,10,"bold"),"⚠️")
]
labels = [create_label1(*prop) for prop in label_properties]
LB_XXX, LB_M, LB_L, LB_S, LB_1, bkup, STATUS_MS1, STATUS_MS2 = labels

LB_XXX.bind    ("<Button-1>", close_window)
LB_M.bind      ("<Button-1>", lambda event: toggle_window_size('■'))
LB_L.bind      ("<Button-1>", lambda event: toggle_window_size('▼'))
LB_S.bind      ("<Button-1>", lambda event: toggle_window_size('◀'))
LB_1.bind      ("<Button-1>", lambda event: extra_bar         ())
bkup.bind      ("<Button-1>", lambda event: git_sync          ())
STATUS_MS1.bind("<Button-1>", lambda event: show_git_changes  ("C:\\ms1"))
STATUS_MS2.bind("<Button-1>", lambda event: show_git_changes  ("C:\\ms2"))


def create_label2(
                    parent,
                    text,
                    bg_color,
                    fg_color,
                    width,
                    height,
                    relief,
                    font,
                    padx_label,
                    pady_label,
                    side,
                    anchor,
                    padx_pack,
                    pady_pack,
                    ht,
                    htc,
                    ):
    label = tk.Label(parent, text=text, bg=bg_color, fg=fg_color, width=width, height=height, relief=relief, font=font, padx=padx_label, pady=pady_label, highlightthickness=ht, highlightbackground=htc)
    label.pack(side=side, anchor=anchor, padx=padx_pack, pady=pady_pack)
    return label

label_properties = [
(BOX_ROW_ROOT,"CPU"   ,"#1d2027","#ffffff","4","1","flat",("arial",10,"bold"),1,0,"left","e",(0,3),(0,0), 0, "#FFFFFF"),
(BOX_ROW_ROOT,"GPU"   ,"#1d2027","#ffffff","4","1","flat",("arial",10,"bold"),1,0,"left","e",(0,3),(0,0), 0, "#FFFFFF"),
(BOX_ROW_ROOT,"RAM"   ,"#1d2027","#ffffff","4","1","flat",("arial",10,"bold"),1,0,"left","e",(0,3),(0,0), 0, "#FFFFFF"),
(BOX_ROW_ROOT,"Disk C","#1d2027","#ffffff","4","1","flat",("arial",10,"bold"),1,0,"left","e",(0,3),(0,0), 0, "#FFFFFF"),
(BOX_ROW_ROOT,"Disk D","#1d2027","#ffffff","4","1","flat",("arial",10,"bold"),1,0,"left","e",(0,3),(0,0), 0, "#FFFFFF"),
(BOX_ROW_ROOT,"▲"     ,"#1d2027","#ffffff","5","1","flat",("arial",10,"bold"),1,0,"left","e",(0,3),(0,0), 0, "#FFFFFF"),
(BOX_ROW_ROOT,"▼"     ,"#1d2027","#ffffff","5","1","flat",("arial",10,"bold"),1,0,"left","e",(0,3),(0,0), 0, "#FFFFFF")
]
labels = [create_label2(*prop) for prop in label_properties]
LB_CPU, LB_GPU, LB_RAM, LB_DUC, LB_DUD, LB_UPLOAD, LB_DWLOAD = labels

#????????????????????????????????????????????????????????????w
#????????????????????????????????????????????????????????????
#!This is for ROW 2
#! Terminal & SYNC & Ruler
def rclone_sync(event=None):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\sync.ps1"])
def windows_terminal(even=None):
    subprocess.Popen(["wt"])
def powertoys_ruler(event=None):
    pyautogui.hotkey('win', 'shift', 'm')
def powertoys_TextExtract(event=None):
    pyautogui.hotkey('win', 'shift', 't')
def powertoys_mouse_crosshair(event=None):
    pyautogui.hotkey('win', 'alt', 'p')

def get_system_uptime():
    uptime_seconds = psutil.boot_time()
    current_time = datetime.now().timestamp()
    uptime = current_time - uptime_seconds
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(hours), int(minutes), int(seconds)

def format_uptime():
    hours, minutes, seconds = get_system_uptime()
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def update_uptime_label():
    uptime_str = format_uptime()
    uptime_label.config(text=f"Uptime: {uptime_str}")
    uptime_label.after(1000, update_uptime_label)  # Update every second
    # Update uptime label periodically


BOX_ROW2_ROOT = tk.Frame(ROOT, bg="#1d2027") ; BOX_ROW2_ROOT.pack(side="top", anchor="e", pady=(0,7),padx=(5,3))

uptime_label = tk.Label(BOX_ROW2_ROOT, text="uptime: 00:00:00", bg="#1d2027", fg="#FFFFFF", height="2", relief="flat", highlightthickness=4, highlightbackground="#1d2027", padx=0, pady=0, font=('JetBrainsMono NF', 10, 'bold'))
uptime_label.pack(side="left", anchor='ne', padx=(0,0), pady=(0,0)) ; update_uptime_label()


LB_RULERSR = tk.Label (BOX_ROW2_ROOT, font=("ink free", 10), text="📏", bg="#1d2027", fg="#FFFFFF", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#1d2027", padx=1, pady=0)
LB_MICECRS = tk.Label (BOX_ROW2_ROOT, font=("ink free", 10), text="🖱", bg="#1d2027", fg="#FFFFFF", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#1d2027", padx=1, pady=0)
LB_TEXTCPP = tk.Label (BOX_ROW2_ROOT, font=("ink free", 10), text="📝", bg="#1d2027", fg="#FFFFFF", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#1d2027", padx=1, pady=0)
LB_SYNCCCC = tk.Label (BOX_ROW2_ROOT, font=("ink free", 10), text="♾️", bg="#1d2027", fg="#3bda00", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#1d2027", padx=1, pady=0)
LB_TERMINL = tk.Label (BOX_ROW2_ROOT, font=("ink free", 10), text="💻", bg="#000000", fg="#FFFFFF", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#1d2027", padx=1, pady=0)
LB_RULERSR.pack(side="left", anchor='e', padx=(0,1), pady=(0,0)) ; LB_RULERSR.bind("<Button-1>", powertoys_ruler)
LB_MICECRS.pack(side="left", anchor='e', padx=(0,1), pady=(0,0)) ; LB_MICECRS.bind("<Button-1>", powertoys_mouse_crosshair)
LB_TEXTCPP.pack(side="left", anchor='e', padx=(0,1), pady=(0,0)) ; LB_TEXTCPP.bind("<Button-1>", powertoys_TextExtract)
LB_SYNCCCC.pack(side="left", anchor='e', padx=(0,1), pady=(0,0)) ; LB_SYNCCCC.bind("<Button-1>", rclone_sync)
LB_TERMINL.pack(side="left", anchor='e', padx=(0,1), pady=(0,0)) ; LB_TERMINL.bind("<Button-1>", windows_terminal)

BOX_ROW3_ROOT = tk.Frame(ROOT, bg="#1d2027") ; BOX_ROW3_ROOT.pack(side="bottom", anchor="e", pady=(0,7),padx=(5,3))
BT_CLR = tk.Button(BOX_ROW3_ROOT, bg="#1d2027", fg="white" ,  width=2, height=1, relief="flat",highlightthickness=1, highlightbackground="#FFFFFF", padx=1, pady=0, font=("AGENCY", 10, "bold"), text="❌", command=clear_screen) ; BT_CLR.pack( side="bottom", anchor="e", pady=(0,0), padx=(0,0))

#! Here are all the exit function for row 1 and 2 and 3
# CPU / RAM / DRIVES / NET SPEED
update_info_labels()
# Resize Window (seems to have no effect may be coz of modification)
window_state = 'normal'
# Start a separate thread for updating the git status
status_thread = threading.Thread(target=update_status, daemon=True)
status_thread.start()


#?  ███╗   ███╗ █████╗ ██╗███╗   ██╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#?  ████╗ ████║██╔══██╗██║████╗  ██║    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#?  ██╔████╔██║███████║██║██╔██╗ ██║    █████╗  ██████╔╝███████║██╔████╔██║█████╗
#?  ██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#?  ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#?  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
# Create main frame
MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800) #! this is to adjust the border for main frame #make it bigger so no problem with  # smaller will cause smaller border  # have to do it for every frame
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1)  # Add some padding at the top

#! ALL CPU CORES
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
        # Calculate the height of the bar based on usage percentage
        bar_height = int((usage / 100) * BAR_HEIGHT)
        # Determine the color based on usage percentage
        bar_color = determine_color(usage)
        # Draw the bar with the determined color
        core_bar.create_rectangle(0, BAR_HEIGHT - bar_height, BAR_WIDTH, BAR_HEIGHT, fill=bar_color)
        # Display the usage percentage at the top of the bar
        core_bar.create_text(BAR_WIDTH // 2, 5, text=f"{usage}%", fill="white")
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
# Constants for bar appearance
BAR_WIDTH = 35
BAR_HEIGHT = 50
# Create a frame to hold the CPU core usage bars
cpu_core_frame = tk.Frame(MAIN_FRAME, bg="#1d2027")
cpu_core_frame.pack(side="top", anchor="center", padx=0, pady=100, fill="x")
# Create canvas widgets for CPU core bars
cpu_core_bars = []
for i in range(psutil.cpu_count()):
    core_bar = tk.Canvas(cpu_core_frame, bg="#1d2027", width=BAR_WIDTH, height=BAR_HEIGHT, highlightthickness=0)
    core_bar.pack(side="left", anchor="center", padx=(10,10), pady=0, expand=True)
    cpu_core_bars.append(core_bar)
# Update CPU core bars
update_cpu_core_bars()


MAIN_FRAME.pack()
ROOT.mainloop()