import importlib
import subprocess

required_libraries = [
    "tkinter",
    "subprocess",
    "time",
    "datetime",
    "tkinter.ttk",
    "ctypes",
    "pyadl",
    "os",
    "shutil",
    "PIL",
    "tkinter.messagebox",
    "psutil",
    "threading",
    "pyautogui",
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

# Now import the libraries
import tkinter as tk
import subprocess
from time import strftime
from datetime import datetime
from tkinter import ttk
import ctypes
from pyadl import ADLManager
import os
import shutil
from PIL import Image, ImageTk
from tkinter import PhotoImage
from tkinter import messagebox
import time
import psutil
import threading
import pyautogui
import tksvg


# # For topmost
# import win32gui


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

def check_window_topmost():
    if not ROOT.attributes('-topmost'):
        ROOT.attributes('-topmost', True)
    if checking:  # Only continue checking if the flag is True
        ROOT.after(500, check_window_topmost)

def toggle_checking():
    global checking
    checking = not checking
    if checking:
        if ROOT.attributes('-topmost'):  # Only start checking if already topmost
            check_window_topmost()  # Start checking if toggled on and already topmost
        BT_TOPMOST.config(fg="#3bda00")  # Change text color to green
    else:
        ROOT.after_cancel(check_window_topmost)  # Cancel the checking if toggled off
        BT_TOPMOST.config(fg="#FFFFFF")  # Change text color to white

checking = False

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
        # x_coordinate, y_coordinate = 0, 1038
        # x_coordinate, y_coordinate = 1390, 1038
        # x_coordinate, y_coordinate = 1308, 1038
        # x_coordinate, y_coordinate = 1590, 0
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
        # x_coordinate, y_coordinate = 0, 1038
        # x_coordinate, y_coordinate = 1002, 1038
        # x_coordinate, y_coordinate = 920, 1038
        # x_coordinate, y_coordinate = 1180, 0
        if ROOT.attributes('-topmost'):
             toggle_checking()
    elif size == '■':
        ROOT.geometry('520x800')
        ROOT.configure(bg='#1d2027')
        LB_S.config(text='◀', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("ink free", 10, "bold"))
        LB_L.config(text='▼', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("agency", 10, "bold"))
        LB_M.config(text='■', bg="#1d2027", fg="#26b2f3", height=1, width=2, font=("calibri", 10, "bold"))
        window_state = 'large'
        # x_coordinate = 0
        # window_height = 700
        # y_coordinate = screen_height - window_height

        x_coordinate = screen_width - 520
        y_coordinate = screen_height//2 - 855//2
        # x_coordinate, y_coordinate = 0, 374
        # x_coordinate, y_coordinate = 1002, 374
        # x_coordinate, y_coordinate = 1420, 162
        # x_coordinate, y_coordinate = 1180, 0
        if checking:
            toggle_checking()
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

# Create the toggle button
BT_TOPMOST = tk.Button(BOX_ROW_ROOT, text="📌", bg="#1d2027", fg="#FFFFFF", command=toggle_checking, font=("JetBrainsMono NF", 10, "bold"))
BT_TOPMOST.pack(pady=0)
# Call the function to check window topmost status periodically
check_window_topmost()

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

#! Time & Date
def update_time():
    current_time = strftime('%I:%M:%S')  # Format time in 12-hour format # %p is for am/pm
    LB_TIME['text'] = current_time
    current_date = datetime.now().strftime('%d %b %Y')  # Format date as '03 May 2023'
    LB_DATE['text'] = current_date
    ROOT.after(1000, update_time)  # Update time every 1000 milliseconds (1 second)

BOX_ROW_MAIN = tk.Frame(MAIN_FRAME, bg="#1493df") ; BOX_ROW_MAIN.pack(side="top", anchor="center", pady=(80,0),padx=(0,0), fill="x")
LB_TIME = tk.Label (BOX_ROW_MAIN, bg="#1493df", fg="#000000", width="13", height="1", relief="flat", highlightthickness=4, highlightbackground="#1493df", anchor="center", padx=0, pady=0, font=('JetBrainsMono NF', 18, 'bold'), text="" )
LB_DATE = tk.Label (BOX_ROW_MAIN, bg="#1493df", fg="#000000", width="13", height="1", relief="flat", highlightthickness=4, highlightbackground="#1493df", anchor="center", padx=0, pady=0, font=('JetBrainsMono NF', 14, 'bold'), text="" )
LB_TIME.pack(side="top", anchor='center', padx=(0,0), pady=(0,0))
LB_DATE.pack(side="top", anchor='center', padx=(0,0), pady=(0,0))

update_time()

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
cpu_core_frame.pack(side="top", anchor="center", padx=0, pady=10, fill="x")
# Create canvas widgets for CPU core bars
cpu_core_bars = []
for i in range(psutil.cpu_count()):
    core_bar = tk.Canvas(cpu_core_frame, bg="#1d2027", width=BAR_WIDTH, height=BAR_HEIGHT, highlightthickness=0)
    core_bar.pack(side="left", anchor="center", padx=(10,10), pady=0, expand=True)
    cpu_core_bars.append(core_bar)
# Update CPU core bars
update_cpu_core_bars()


#! Backup & Update
def open_backup(event=None):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\backup.ps1"], shell=True)
def open_update(event=None):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\update.ps1"],  shell=True)

BOX_ROW_MAIN = tk.Frame(MAIN_FRAME, bg="black") ; BOX_ROW_MAIN.pack(pady=(5,0))
BACKUP_BT = tk.Label(BOX_ROW_MAIN, bg="#21a366", fg="#ffffff", height=1, width=13, relief="flat", highlightthickness=1, highlightbackground="#21a366", padx=3, pady=0, font=("JetBrainsMono NF", 14, "bold"), text="Backup")
UPDATE_BT = tk.Label(BOX_ROW_MAIN, bg="#0047ab", fg="#ffffff", height=1, width=13, relief="flat", highlightthickness=1, highlightbackground="#0047ab", padx=3, pady=0, font=("JetBrainsMono NF", 14, "bold"), text="Update")
BACKUP_BT.pack(side="left", anchor="center", padx=(0,0), pady=0) ; BACKUP_BT.bind("<Button-1>", open_backup)
UPDATE_BT.pack(side="left", anchor="center", padx=(0,0), pady=0) ; UPDATE_BT.bind("<Button-1>", open_update)

#! Drive size analyze using rclone
def c_size(event=None):
    subprocess.run(["powershell", "Start-Process rclone -ArgumentList 'ncdu c:\\' "])
def d_size(event=None):
    subprocess.run(["powershell", "Start-Process rclone -ArgumentList 'ncdu d:\\' "])

BOX_ROW_MAIN = tk.Frame(MAIN_FRAME, bg="black") ; BOX_ROW_MAIN.pack(pady=0)
BT_NCDU_C = tk.Label(BOX_ROW_MAIN, bg="#57a9f4", fg="#000000", height=1, width=13, relief="flat", highlightthickness=1, highlightbackground="#57a9f4", padx=3, font=("JetBrainsMono NF", 14, "bold"), text="C:\\ Drive" )
BT_NCDU_D = tk.Label(BOX_ROW_MAIN, bg="#57a9f4", fg="#000000", height=1, width=13, relief="flat", highlightthickness=1, highlightbackground="#57a9f4", padx=3, font=("JetBrainsMono NF", 14, "bold"), text="D:\\ Drive" )
BT_NCDU_C.pack(side="left", padx=(0,0), pady=0) ; BT_NCDU_C.bind("<Button-1>", c_size)
BT_NCDU_D.pack(side="left", padx=(0,0), pady=0) ; BT_NCDU_C.bind("<Button-1>", d_size)

MAIN_FRAME.pack(expand=True)


#*  ███████╗███████╗███╗   ███╗██████╗ ███████╗ ██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#*  ██╔════╝██╔════╝████╗ ████║██╔══██╗██╔════╝██╔════╝     ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#*  █████╗  █████╗  ██╔████╔██║██████╔╝█████╗  ██║  ███╗    █████╗  ██████╔╝███████║██╔████╔██║█████╗
#*  ██╔══╝  ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██╔══╝  ██║   ██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#*  ██║     ██║     ██║ ╚═╝ ██║██║     ███████╗╚██████╔╝    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#*  ╚═╝     ╚═╝     ╚═╝     ╚═╝╚═╝     ╚══════╝ ╚═════╝     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

def open_ffmpeg_trimm():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\trim.ps1"])

def open_ffmpeg_convt():
    subprocess.run(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\convert.ps1"])

def open_ffmpeg_dimns():
    subprocess.run(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\dimension.ps1"])

def open_ffmpeg_imgdm():
    subprocess.run(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\imgdim.ps1"])

def open_ffmpeg_merge():
    subprocess.run(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\merge.ps1"])

#! FRAME Function
def switch_to_ffmpeg_frame():
    switch_to_frame(FRAME_FFMPEG, MAIN_FRAME)

BT_FFMPEG = M1_hold_release(MAIN_FRAME, "FFmpeg", switch_to_ffmpeg_frame, bg="#408b40", fg="#FFFFFF", height=1, width=30, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#408b40", font=("JetBrainsMono NF", 13, "bold"))
BT_FFMPEG.pack(padx=(0,0),pady=(0,0))

FRAME_FFMPEG = tk.Frame(BORDER_FRAME, bg="#1D2327", width=520, height=800) ; FRAME_FFMPEG.pack_propagate(False)

BT_BACK = tk.Button(FRAME_FFMPEG, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FRAME_FFMPEG), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))

BOX_1 = tk.Frame(FRAME_FFMPEG, bg="#1d2027") ; BOX_1.pack(side="top", anchor="center", pady=(80,0), padx=(0,0))
BT_TRIMM=tk.Button(BOX_1, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_trimm, text="Trim"          ) ; BT_TRIMM.pack     (pady=(1,0))
BT_CONVT=tk.Button(BOX_1, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_convt, text="Convert"       ) ; BT_CONVT.pack     (pady=(1,0))
BT_DIMNS=tk.Button(BOX_1, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_dimns, text="Dimension"     ) ; BT_DIMNS.pack     (pady=(1,0))
BT_IMGDM=tk.Button(BOX_1, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_imgdm, text="Imagedimension") ; BT_IMGDM.pack     (pady=(1,0))
BT_MERGE=tk.Button(BOX_1, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_merge, text="Merge"         ) ; BT_MERGE.pack     (pady=(1,0))


#*  ███████╗██╗███╗   ██╗██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#*  ██╔════╝██║████╗  ██║██╔══██╗    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#*  █████╗  ██║██╔██╗ ██║██║  ██║    █████╗  ██████╔╝███████║██╔████╔██║█████╗
#*  ██╔══╝  ██║██║╚██╗██║██║  ██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#*  ██║     ██║██║ ╚████║██████╔╝    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#*  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

def find_file():
    subprocess.run(["powershell", "start", "C:\\ms1\\scripts\\find\\find_file.ps1"])

def find_patt():
    subprocess.run(["powershell", "start", "C:\\ms1\\scripts\\find\\find_pattern.ps1"])

def find_size():
    subprocess.run(["powershell", "start", "C:\\ms1\\scripts\\find\\find_size.ps1"])

def fzf_c():
    command = 'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; fzf --preview=\'highlight -O ansi -l {}\'"'
    try:
        subprocess.run(["powershell", "-Command", command], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def fzf_d():
    command = 'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; fzf --preview=\'bat {}\'"'
    try:
        subprocess.run(["powershell", "-Command", command], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def ack_c():
    additional_text = input("Enter additional text: ")
    command = f'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; ack {additional_text}"'
    try:
        subprocess.run(["powershell", "-Command", command], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def ack_d():
    additional_text = input("Enter additional text: ")
    command = f'Start-Process powershell -ArgumentList "-NoExit -Command cd D: ; ack {additional_text}"'
    try:
        subprocess.run(["powershell", "-Command", command], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def get_additional_text():
    # Assuming you have a Tkinter Entry widget for input
    additional_text = FZF_SEARCH_WIDGET.get()
    return additional_text

def ack_c():
    additional_text = get_additional_text()
    command = f'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; ack {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def ack_d():
    additional_text = get_additional_text()
    command = f'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; ack {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

#! FRAME Function
def switch_to_find_frame():
    switch_to_frame(FRAME_FIND, MAIN_FRAME)

BT_FIND = M1_hold_release(MAIN_FRAME, "Find", switch_to_find_frame, bg="#FFFFFF", fg="#1D2027", height=1, width=30, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#FFFFFF", font=("JetBrainsMono NF", 13, "bold"))
BT_FIND.pack(padx=(0,0),pady=(0,0))

FRAME_FIND = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800) ; FRAME_FIND.pack_propagate(True)

BT_BACK = tk.Button(FRAME_FIND, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FRAME_FIND), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))

BOX_1 = tk.Frame(FRAME_FIND, bg="#1d2027") ; BOX_1.pack(side="top", anchor="center", pady=(80,0), padx=(0,0))

BT_FF= tk.Button(BOX_1, bg="white", fg ="#1D2027", height=2, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=find_file, text="Find File"   ) ; BT_FF.pack(pady=(1,0))
BT_FP= tk.Button(BOX_1, bg="white", fg ="#1D2027", height=2, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=find_patt, text="Find Pattern") ; BT_FP.pack(pady=(1,0))
BT_FS= tk.Button(BOX_1, bg="white", fg ="#1D2027", height=2, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=find_size, text="Find Size"   ) ; BT_FS.pack(pady=(1,0))

BT_FZF_C= tk.Button(BOX_1, height=1, bg="#f80069", fg ="#b0e1bd", width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=fzf_c, text="FZF-->C:\\") ; BT_FZF_C.pack(pady=(1,0))
BT_FZF_D= tk.Button(BOX_1, height=1, bg="#f80069", fg ="#b0e1bd", width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=fzf_d, text="FZF-->D:\\") ; BT_FZF_D.pack(pady=(1,0))

# Assuming you have a Tkinter Entry widget for user input
BOX_3 = tk.Frame(FRAME_FIND, bg="#1d2027") ; BOX_3.pack(side="top", anchor="center", pady=(0,0), padx=(0,0))

FZF_SEARCH_WIDGET = tk.Entry(BOX_3, width=30, fg="black", bg="#7D879E", relief="flat", font=("calibri", 18, "bold", "italic"), justify="center")
BT_ACK_C= tk.Button(BOX_3, text="ACK-->C:\\", font=("calibri", 14, "bold"), command=ack_c, bg="#e63a00", fg ="#fcffef", height=1, width=20, relief="flat", highlightthickness=0)
BT_ACK_D= tk.Button(BOX_3, text="ACK-->D:\\", font=("calibri", 14, "bold"), command=ack_d, bg="#e63a00", fg ="#fcffef", height=1, width=20, relief="flat", highlightthickness=0)
FZF_SEARCH_WIDGET.pack(pady=(10,1))
BT_ACK_C.pack(side="left", anchor="e", pady=(1,0))
BT_ACK_D.pack(side="left", anchor="e", pady=(1,0))



#*  ███████╗ ██████╗ ██╗     ██████╗ ███████╗██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#*  ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#*  █████╗  ██║   ██║██║     ██║  ██║█████╗  ██████╔╝    █████╗  ██████╔╝███████║██╔████╔██║█████╗
#*  ██╔══╝  ██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#*  ██║     ╚██████╔╝███████╗██████╔╝███████╗██║  ██║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#*  ╚═╝      ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

def open_appdata_fd():
    subprocess.run(["powershell", "-Command", "Invoke-Item", "C:\\Users\\nahid\\AppData"])

def open_appsfolder_fd():
    subprocess.run(["explorer", "shell:AppsFolder"])

def open_git_fd():
    subprocess.run(["powershell", "-Command", "Invoke-Item", "C:\\Users\\nahid\\OneDrive\\Git"])

def open_packages_fd():
    subprocess.run(["powershell", "-Command", "Invoke-Item", "C:\\Users\\nahid\\AppData\\Local\\Packages"])

def open_scoop_fd():
    subprocess.run(["powershell", "-Command", "Invoke-Item", "C:\\Users\\nahid\\scoop"])

def open_sofware_fd():
    subprocess.run(["powershell", "-Command", "Invoke-Item", "D:\\software"])

def open_song_fd():
    subprocess.run(["powershell", "-Command", "Invoke-Item", "D:\\song"])

def open_startups_fd():
    subprocess.run(["explorer", "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"])

def open_usrstartups_fd():
    subprocess.run(["explorer", "C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"])

def open_templocal_fd():
    subprocess.run(["powershell", "-Command", "Invoke-Item", "C:\\Users\\nahid\\AppData\\Local\\Temp"])

def open_tempwin_fd():
    subprocess.run(["powershell", "-Command", "Invoke-Item", "C:\\Windows\\Temp"])

def open_Winapps_fd():
    subprocess.run(["explorer", "C:\\Program Files\\WindowsApps"])

def open_programdata_fd():
    subprocess.run(["explorer", "C:\\ProgramData"])

icon_path = "C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"
icon_image = ImageTk.PhotoImage(Image.open(icon_path))

def switch_to_tools_frame():
    switch_to_frame(FRAME_FOLDER, MAIN_FRAME)

BT_FOLDER = M1_hold_release(MAIN_FRAME, "Folder", switch_to_tools_frame,image=icon_image, compound=tk.TOP, bg="#e7d86a", fg="#1D2027", height=40, width=300, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#e7d86a", font=("JetBrainsMono NF", 13, "bold"))
BT_FOLDER.pack(padx=(0,0),pady=(0,0))

FRAME_FOLDER = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800) ; FRAME_FOLDER.pack_propagate(True)

BT_BACK = tk.Button(FRAME_FOLDER, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FRAME_FOLDER), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))




def create_button(text, command, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, padx_button, pady_button, padx_pack, pady_pack):
    button = tk.Button(BOX_1, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack)
    return button

BOX_1 = tk.Frame(FRAME_FOLDER, bg="#1d9027")
BOX_1.pack(side="top", pady=(80,0), padx=(0,0))

button_properties = [
("All Apps"      ,open_appsfolder_fd ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    0 ,1,1,1,       0,0, (0,0),(0,0)),
("AppData"       ,open_appdata_fd    ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    1 ,1,1,1,       0,0, (0,0),(0,0)),
("Git Projects"  ,open_git_fd        ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    2 ,1,1,1,       0,0, (0,0),(0,0)),
("Packages"      ,open_packages_fd   ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    3 ,1,1,1,       0,0, (0,0),(0,0)),
("ProgramData"   ,open_programdata_fd,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    4 ,1,1,1,       0,0, (0,0),(0,0)),
("Scoop"         ,open_scoop_fd      ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    5 ,1,1,1,       0,0, (0,0),(0,0)),
("Software"      ,open_sofware_fd    ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    6 ,1,1,1,       0,0, (0,0),(0,0)),
("Song"          ,open_song_fd       ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    7 ,1,1,1,       0,0, (0,0),(0,0)),
("Startup System",open_startups_fd   ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    8 ,1,1,1,       0,0, (0,0),(0,0)),
("Startup User"  ,open_usrstartups_fd,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    9 ,1,1,1,       0,0, (0,0),(0,0)),
("Temp-AppDate"  ,open_templocal_fd  ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    10,1,1,1,       0,0, (0,0),(0,0)),
("Temp-Windows"  ,open_tempwin_fd    ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    11,1,1,1,       0,0, (0,0),(0,0)),
("WindowsApp"    ,open_Winapps_fd    ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),    12,1,1,1,       0,0, (0,0),(0,0))
]

for button_props in button_properties:
    create_button(*button_props)


# #! Example With Place
# def create_button(text, command, bg_color, fg_color, height, width, relief, font, padx_button, pady_button, x_button, y_button, padx_pack, pady_pack):
#     button = tk.Button(BOX_1, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
#     button.place(x=x_button, y=y_button)
#     return button

# BOX_1 = tk.Frame(FRAME_FOLDER, bg="#1d9027", width=520, height=800)
# BOX_1.pack(side="top", pady=(80,0), padx=(0,0))

# button_properties = [
#     ("All Apps"      ,open_appsfolder_fd ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 10, (0,0),(0,0)),
#     ("AppData"       ,open_appdata_fd    ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 60, (0,0),(0,0)),
#     ("Git Projects"  ,open_git_fd        ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 110, (0,0),(0,0)),
#     ("Packages"      ,open_packages_fd   ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 160, (0,0),(0,0)),
#     ("ProgramData"   ,open_programdata_fd,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 210, (0,0),(0,0)),
#     ("Scoop"         ,open_scoop_fd      ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 260, (0,0),(0,0)),
#     ("Software"      ,open_sofware_fd    ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 310, (0,0),(0,0)),
#     ("Song"          ,open_song_fd       ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 360, (0,0),(0,0)),
#     ("Startup System",open_startups_fd   ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 410, (0,0),(0,0)),
#     ("Startup User"  ,open_usrstartups_fd,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 460, (0,0),(0,0)),
#     ("Temp-AppDate"  ,open_templocal_fd  ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 510, (0,0),(0,0)),
#     ("Temp-Windows"  ,open_tempwin_fd    ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 560, (0,0),(0,0)),
#     ("WindowsApp"    ,open_Winapps_fd    ,"#ffd86a","#1D2027",1,20,"flat",("calibri",14,"bold"),0,0, 10, 610, (0,0),(0,0))
# ]

# for button_props in button_properties:
#     create_button(*button_props)


#!  ██████╗ ██████╗  ██████╗  ██████╗███████╗███████╗███████╗       ██╗       ██████╗ ██╗  ██╗ ██████╗
#!  ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔════╝       ██║       ██╔══██╗██║ ██╔╝██╔════╝
#!  ██████╔╝██████╔╝██║   ██║██║     █████╗  ███████╗███████╗    ████████╗    ██████╔╝█████╔╝ ██║  ███╗
#!  ██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝  ╚════██║╚════██║    ██╔═██╔═╝    ██╔═══╝ ██╔═██╗ ██║   ██║
#!  ██║     ██║  ██║╚██████╔╝╚██████╗███████╗███████║███████║    ██████║      ██║     ██║  ██╗╚██████╔╝
#!  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝    ╚═════╝      ╚═╝     ╚═╝  ╚═╝ ╚═════╝

#! FRAME Function
def switch_to_process_frame():
    switch_to_frame(FR_PROCESS, MAIN_FRAME)

BT_PROCESS_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "Process & PKG", switch_to_process_frame, bg="#cc2400", fg="#FFFFFF", height=2, width=30, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#cc2400", font=("JetBrainsMono NF", 13, "bold")) ; BT_PROCESS_MAIN_FRAME.pack(padx=(0,0),pady=(0,0))
FR_PROCESS = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800) ; FR_PROCESS.pack_propagate(False)
BT_BACK = tk.Button(FR_PROCESS, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_PROCESS), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold")) ; BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))


def insert_input():
    additional_text = WIDGET_APPID.get()
    return additional_text

def highlight_matching_string(text_widget, pattern):
    start_index = "1.0"
    pattern = pattern.lower()  # Convert pattern to lowercase for case-insensitive search
    while True:
        start_index = text_widget.search(pattern, start_index, stopindex=tk.END, nocase=True)
        if not start_index:
            break
        end_index = text_widget.index(f"{start_index}+{len(pattern)}c")
        text_widget.tag_add("match", start_index, end_index)
        text_widget.tag_config("match", foreground="red")
        start_index = end_index

def get_process():
    additional_text = insert_input()
    if not additional_text:  # Check if input is empty
        return  # Do nothing if input is empty
    command = f'Get-Process | Where-Object {{ $_.Name -like "*{additional_text}*" }} | Format-Table -Property ProcessName, Id -AutoSize | Out-String'
    try:
        # Execute the PowerShell command and capture the output
        output = subprocess.check_output(["powershell", "-Command", command], shell=True, text=True)
        # Display the output in the GUI
        output_text.delete(1.0, tk.END)  # Clear previous output
        output_text.insert(tk.END, output)
        # Highlight matching string in blue
        highlight_matching_string(output_text, additional_text)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def kil_process():
    additional_text = insert_input()
    command = f'Stop-Process -Name {additional_text}'
    try:
        subprocess.check_output(["powershell", "-Command", command], stderr=subprocess.STDOUT, shell=True, text=True)
        # Display confirmation in the GUI
        output_text.delete(1.0, tk.END)  # Clear previous output
        output_text.insert(tk.END, f"Process {additional_text} killed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        # Display error message in the GUI
        output_text.delete(1.0, tk.END)  # Clear previous output
        output_text.insert(tk.END, f"Error: {e.output}")

def custom_command():
    additional_text = insert_input()
    if not additional_text:  # Check if input is empty
        return  # Do nothing if input is empty
    profile_path = r'C:\Users\nahid\OneDrive\backup\Microsoft.PowerShell_profile.ps1'
    command = f'powershell -ExecutionPolicy Bypass -NoProfile -Command "& {{ . {profile_path}; {additional_text} }}"'
    try:
        # Execute the custom PowerShell command and capture the output
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
        # Display the output in the GUI
        output_text.delete(1.0, tk.END)  # Clear previous output
        output_text.insert(tk.END, output)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        # Display error message in the GUI
        output_text.delete(1.0, tk.END)  # Clear previous output
        output_text.insert(tk.END, f"Error: {e.output}")

BOX_WIDGET_APPID = tk.Frame(FR_PROCESS, bg="#14bcff")
BOX_WIDGET_APPID.pack(pady=(80,0))
WIDGET_APPID = tk.Entry(BOX_WIDGET_APPID, width=30, fg="#000000", bg="#FFFFFF", font=("calibri", 18, "bold", "italic"), justify="center", relief="flat")
WIDGET_APPID.pack(padx=2, pady=2)

BOX_ROW_APPID2 = tk.Frame(FR_PROCESS, bg="black")
BOX_ROW_APPID2.pack(pady=2)
BT_GET_ID = tk.Button(BOX_ROW_APPID2, bg="#00ff21", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=get_process, text="🔍")
BT_GET_ID.pack(side="left", pady=0)
BT_KIL_ID = tk.Button(BOX_ROW_APPID2, bg="#ff4f00", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=kil_process, text="❌")
BT_KIL_ID.pack(side="left", pady=0)
# New button and function for running custom command
BT_CUSTOM_CMD = tk.Button(BOX_ROW_APPID2, bg="#41abff", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=custom_command, text="🏃")
BT_CUSTOM_CMD.pack(side="left", pady=0)

#! Output text widget
output_text = tk.Text(FR_PROCESS, height=5, width=50, font=("JetBrainsMono NF", 12), bg="#ddf581")
output_text.pack()

#?   ██╗ ██╗     ██╗    ██╗       ██╗       ███████╗
#?  ████████╗    ██║    ██║       ██║       ██╔════╝
#?  ╚██╔═██╔╝    ██║ █╗ ██║    ████████╗    ███████╗
#?  ████████╗    ██║███╗██║    ██╔═██╔═╝    ╚════██║
#?  ╚██╔═██╔╝    ╚███╔███╔╝    ██████║      ███████║
#?   ╚═╝ ╚═╝      ╚══╝╚══╝     ╚═════╝      ╚══════╝

# winget / scoop text based info/show search install etc

def winget_search():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Winget Search\' ; winget search {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def winget_install():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Winget install\' ; winget install {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def winget_uninst():
    additional_text = insert_input()
    # Enclose additional_text in double quotes if it contains spaces
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground red \'- Winget Uninstall\' ; winget uninstall {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def winget_infooo():
    additional_text = insert_input()
    # Enclose additional_text in double quotes if it contains spaces
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Winget Show\' ; winget show {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def wget_inst_fzf():
    command = ' $host.UI.RawUI.WindowTitle = "wget🔽" ; winget search --exact "" | fzf --multi --preview-window=up:60% --preview \'winget show {1}\' | ForEach-Object { winget install $_.split()[0] }'
    try:
        subprocess.Popen([ 'start' , 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def wget_unin_fzf():
    command = ' $host.UI.RawUI.WindowTitle = "wget❌" ; winget list "" | fzf --multi --preview-window=up:60% --preview \'winget show {1}\' | ForEach-Object { winget uninstall $_.split()[0] }'
    try:
        subprocess.Popen([ 'start' , 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")



def scoop_search():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'$host.UI.RawUI.WindowTitle = "Scoop-Search" ; pwsh -Command "cd ; write-host  -foreground blue \'- Scoop Search\' ; scoop search {additional_text}"' #! tf how it works??????????????????
    try:
        subprocess.Popen([ "start", "powershell", "-NoExit", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_install():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Scoop Install\' ; scoop install {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_uninstall():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground red \'- Scoop UnInstall\' ; scoop uninstall {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_info():
    additional_text = insert_input()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Scoop Info\' ; scoop info {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_install_fzf():
    # Path to the Python script generating the package list
    python_script = r"C:\ms1\scripts\python\scoop_list.py"

    # Run the Python script to generate the package list
    try:
        subprocess.run(['python', python_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return
    # Path to the text file containing package list
    package_list_file = r"C:\Users\nahid\OneDrive\backup\installed_apps\python_scoop_list_fzf.txt"
    # Command to read from the text file and pipe it to fzf
    command = f'$host.UI.RawUI.WindowTitle = "scoop🔽" ; type {package_list_file} | fzf --multi --preview "scoop info {{1}}" | ForEach-Object {{scoop install $_.split()[0]}}'
    try:
        subprocess.Popen(['start', 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_uninstall_fzf():
    command = '$host.UI.RawUI.WindowTitle = "scoop❌" ; scoop list "" | fzf --multi --preview \'scoop info {1}\' | ForEach-Object { scoop uninstall $_.split()[0] }'
    try:
        subprocess.Popen(['start' , 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")


def create_button(text, command, bg_color, fg_color, height, width, relief, font, row_button, column_button, padx_button, padx_pack, pady_button, pady_pack):
    button = tk.Button(input_frame, text=text, command=command, width=width, fg=fg_color, bg=bg_color, font=font)
    button.grid(row=row_button, column=column_button, padx=padx_button, pady=pady_button)
    return button

input_frame = tk.Frame(FR_PROCESS, bg="#1D2027")
input_frame.pack(pady=10)

winget_scoop_button_properties = [
("Winget"       , None               , "#FFFFFF", "#000000", 1, 12, "flat", ("calibri", 12), 1, 1,       5, 5, 0, 5),
("Search"       , winget_search      , "#1D2027", "#FFFFFF", 1, 12, "flat", ("calibri", 10), 2, 1,       5, 5, 0, 5),
("Install"      , winget_install     , "#1D2027", "#FFFFFF", 1, 12, "flat", ("calibri", 10), 3, 1,       5, 5, 0, 5),
("Uninstall"    , winget_uninst      , "#1D2027", "#FFFFFF", 1, 12, "flat", ("calibri", 10), 4, 1,       5, 5, 0, 5),
("Info"         , winget_infooo      , "#1D2027", "#FFFFFF", 1, 12, "flat", ("calibri", 10), 5, 1,       5, 5, 0, 5),
("FZF-Install"  , wget_inst_fzf      , "#1D2027", "#00FF00", 1, 12, "flat", ("calibri", 10), 6, 1,       5, 5, 0, 5),
("FZF-Uninstall", wget_unin_fzf      , "#1D2027", "#FF0000", 1, 12, "flat", ("calibri", 10), 7, 1,       5, 5, 0, 5),

("Scoop"        , None               , "#FFFFFF", "#000000", 1, 12, "flat", ("calibri", 12), 1, 2,       5, 5, 0, 5),
("Search"       , scoop_search       , "#1D2027", "#FFFFFF", 1, 12, "flat", ("calibri", 10), 2, 2,       5, 5, 0, 5),
("Install"      , scoop_install      , "#1D2027", "#FFFFFF", 1, 12, "flat", ("calibri", 10), 3, 2,       5, 5, 0, 5),
("Uninstall"    , scoop_uninstall    , "#1D2027", "#FFFFFF", 1, 12, "flat", ("calibri", 10), 4, 2,       5, 5, 0, 5),
("Info"         , scoop_info         , "#1D2027", "#FFFFFF", 1, 12, "flat", ("calibri", 10), 5, 2,       5, 5, 0, 5),
("FZF-Install"  , scoop_install_fzf  , "#1D2027", "#00FF00", 1, 12, "flat", ("calibri", 10), 6, 2,       5, 5, 0, 5),
("FZF-Uninstall", scoop_uninstall_fzf, "#1D2027", "#FF0000", 1, 12, "flat", ("calibri", 10), 7, 2,       5, 5, 0, 5)
]

# Create Winget buttons
for button_props in winget_scoop_button_properties:
    create_button(*button_props)


#*   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗     █████╗ ██████╗ ██████╗ ███████╗
#*  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝    ██╔══██╗██╔══██╗██╔══██╗██╔════╝
#*  ██║     ███████║█████╗  ██║     █████╔╝     ███████║██████╔╝██████╔╝███████╗
#*  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗     ██╔══██║██╔═══╝ ██╔═══╝ ╚════██║
#*  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗    ██║  ██║██║     ██║     ███████║
#*   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝
# Install Autoruns using winget and check first
def check_autoruns_installed():
    autoruns_installed = os.path.exists(r'C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\Microsoft.Sysinternals.Autoruns_Microsoft.Winget.Source_8wekyb3d8bbwe\autoruns.exe')
    return autoruns_installed
def install_autoruns():
    try:
        subprocess.run(["winget", "install", "autoruns"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing Autoruns: {e}")
def launch_autoruns():
    if not check_autoruns_installed():
        install_autoruns()
    autoruns_path = r'autoruns'
    # Launch Autoruns in admin mode
    command = f'Start-Process "{autoruns_path}" -Verb RunAs'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching Autoruns: {e}")

BT_AUTORUNS = tk.Button(FR_PROCESS, text="AutoRuns", command=launch_autoruns, height=1, width=20, bg="#FFFFFF", fg="#000000", highlightthickness=5, font=("JetBrainsMono NF", 12, "bold"))
BT_AUTORUNS.pack(pady=(10, 0))


BT_APPLIST = tk.Button(FR_PROCESS, text="App List", command=lambda: switch_to_frame(Page1, FR_PROCESS), bg="#fff", fg="#000", width=20, highlightthickness=5, anchor="center", font=("JetBrainsMono NF", 12, "bold"))
BT_APPLIST.pack(anchor="n", padx=(0,0), pady=(5,0))

Page1 = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800) ; Page1.pack_propagate(False)

BT_BACK = tk.Button(Page1, text="◀", command=lambda: switch_to_frame(FR_PROCESS, Page1 ), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold")) ; BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))


LB_INITIALSPC = tk.Label(Page1, text="",  bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 16, "bold"))
LB_INITIALSPC.pack(side="top", anchor="ne", padx=(0,0), pady=(80,0))

import tkinter as tk
import os
import subprocess

def check_installation(app_name, paths_to_check, chkbx_var, chkbox_bt):
    application_installed = any(os.path.exists(path) for path in paths_to_check)
    chkbx_var.set(1 if application_installed else 0)

    # Change text color based on installation status if not already checked
    if not chkbx_var.get():
        text_color = "green" if application_installed else "red"
        chkbox_bt.config(foreground=text_color)

def install_application(app_name, chkbx_var, chkbox_bt):
    install_options = [
        {"text": "Scoop", "command": lambda: subprocess.Popen(f'pwsh -Command "scoop install {app_name}"')},
        {"text": "Winget", "command": lambda: subprocess.Popen(f'winget install {app_name}')}
    ]
    show_options(install_options)

def uninstall_application(app_name, chkbx_var, chkbox_bt):
    uninstall_options = [
        {"text": "Scoop", "command": lambda: subprocess.Popen(f'pwsh -Command "scoop uninstall {app_name}"')},
        {"text": "Winget", "command": lambda: subprocess.Popen(f'winget uninstall {app_name}')}
    ]
    show_options(uninstall_options)

def show_options(options):
    top = tk.Toplevel()
    top.title("Select Installation Source")
    top.geometry("300x100")
    for option in options:
        btn = tk.Button(top, text=option["text"], command=option["command"])
        btn.pack()

# Variable to track checkbox state
chkbx_rclone = tk.IntVar()

# Define applications and their information
applications = [
    {"name": "Rclone", "paths": [r'C:\Users\nahid\scoop\apps\rclone\current\rclone.exe', r'C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\Rclone.Rclone_Microsoft.Winget.Source_8wekyb3d8bbwe\rclone-v1.65.2-windows-amd64\rclone.exe'], "chkbx_var": chkbx_rclone}
    # Add more applications here
]

# Create and pack checkboxes, check buttons, install buttons, and uninstall buttons for each application
for app in applications:
    frame = tk.Frame(Page1, bg="#1d2027")
    frame.pack(padx=(5,0), pady=(5,0), anchor="center")

    application_installed = any(os.path.exists(path) for path in app["paths"])
    installation_source = "[scoop]" if os.path.exists(os.path.join(r'C:\Users\nahid\scoop\apps', app["name"])) else "[winget]" if application_installed else "[X]"
    app_name_with_source = f"{app['name']} {installation_source}"

    chkbox_bt = tk.Checkbutton(frame, text=app_name_with_source, variable=app["chkbx_var"], font=("calibri", 14, "bold"), foreground="green" if application_installed else "red", background="#1d2027", activebackground="#1d2027", selectcolor="#1d2027", padx=10, pady=5, borderwidth=2, relief="flat", command=lambda app=app: check_installation(app["name"], app.get("paths", []), app["chkbx_var"], chkbox_bt))
    chk_bt = tk.Button(frame, text=f"Check", foreground="green", background="#1d2027", command=lambda app=app: check_installation(app["name"], app.get("paths", []), app["chkbx_var"], chkbox_bt))
    ins_bt = tk.Button(frame, text=f"Install", foreground="green", background="#1d2027", command=lambda app=app: install_application(app["name"], app["chkbx_var"], chkbox_bt))
    unins_bt = tk.Button(frame, text=f"Uninstall", foreground="red", background="#1d2027", command=lambda app=app: uninstall_application(app["name"], app["chkbx_var"], chkbox_bt))

    chkbox_bt.pack(side="left", padx=(0,0), pady=(0,0))
    chk_bt.pack(side="left", padx=(0,0), pady=(0,0))
    ins_bt.pack(side="left", padx=(0,0), pady=(0,0))
    unins_bt.pack(side="left", padx=(0,0), pady=(0,0))

    # Check installation status at the start
    check_installation(app["name"], app.get("paths", []), app["chkbx_var"], chkbox_bt)






#*  ████████╗ ██████╗  ██████╗ ██╗     ███████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#*  ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#*     ██║   ██║   ██║██║   ██║██║     ███████╗    █████╗  ██████╔╝███████║██╔████╔██║█████╗
#*     ██║   ██║   ██║██║   ██║██║     ╚════██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#*     ██║   ╚██████╔╝╚██████╔╝███████╗███████║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#*     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

def open_dxdiag():
    subprocess.run(["powershell", "dxdiag"])
def open_systeminfo():
    subprocess.run(["powershell", "systeminfo"])
def ctt():
    command= 'Invoke-RestMethod christitus.com/win | Invoke-Expression'
    subprocess.Popen(['powershell', '-Command', command])
def open_uac():
    subprocess.run(["UserAccountControlSettings.exe"])
def open_netplwiz():
    subprocess.run(["powershell", "netplwiz.exe"])
def open_msconfig():
    subprocess.run(["powershell", "msconfig.exe"])
def open_powerplan():
    subprocess.run(["powershell", "powercfg.cpl"])
def open_snippingtool():
    subprocess.Popen(["powershell", "SnippingTool.exe"])
def open_dism():
    subprocess.Popen(["powershell", "Start-Process", "-FilePath", "DISM", "-ArgumentList", '"/Online /Cleanup-Image /RestoreHealth"', "-Verb", "RunAs"], shell=True)
def open_sfc():
    subprocess.Popen(["powershell", "Start-Process", "-FilePath", "sfc", "-ArgumentList", '"/scannow"', "-Verb", "RunAs"], shell=True)
def open_chkdsk():
    subprocess.Popen(["powershell", "Start-Process", "-FilePath", "chkdsk", "-ArgumentList", '"/f /r"', "-Verb", "RunAs"], shell=True)
def open_cleanmgr():
    subprocess.Popen(["powershell", "Start-Process", "cleanmgr" , "-Verb", "RunAs"], shell=True)
def flush_dns():
    subprocess.Popen(["powershell", "Start-Process", "-FilePath", "cmd", "-ArgumentList", '"/k ipconfig /flushdns"', "-Verb", "RunAs"], shell=True)
def winsock_reset():
    subprocess.Popen(["powershell", "Start-Process", "-FilePath", "cmd", "-ArgumentList", '"/k netsh winsock reset"', "-Verb", "RunAs"], shell=True)
def optionalfeatures():
    subprocess.Popen(["powershell", "optionalfeatures"])
def advanced_adapter():
    subprocess.Popen(["powershell", "control ncpa.cpl"])

#! Tool Button

def switch_to_tools_frame():
    switch_to_frame(FRAME_TOOLS, MAIN_FRAME)

BT_TOOLS = M1_hold_release(MAIN_FRAME, "TOOLS", switch_to_tools_frame, bg="#454545", fg="#FFFFFF", height=2, width=30, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#454545", font=("JetBrainsMono NF", 13, "bold"))
BT_TOOLS.pack(padx=(0,0),pady=(0,0))

FRAME_TOOLS = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800) ; FRAME_TOOLS.pack_propagate(False)

BT_BACK = tk.Button(FRAME_TOOLS, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FRAME_TOOLS), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))

def create_button(text, command, bg_color, fg_color, height, width, relief, font, padx_button, pady_button, x_button, y_button, anchor_button):
    button = tk.Button(BOX_1, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command, anchor=anchor_button)
    button.place(x=x_button, y=y_button)
    return button

BOX_1 = tk.Frame(FRAME_TOOLS, bg="#1d2027",width=520, height=720)
BOX_1.pack(side="top", anchor="center", pady=(80,0), padx=(0,0))

button_properties = [
    ("Advanced Adapter"        ,advanced_adapter ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,10,     "w") ,
    ("CheckDisk"               ,open_chkdsk      ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,40,     "w") ,
    ("Chris Titus Win Utility" ,ctt              ,"#000000","#FFFFFF",1,25,"solid",("agency",14,"bold"),0,0,  100,70,     "w") ,
    ("Disk Cleanup"            ,open_cleanmgr    ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,100,    "w") ,
    ("DISM"                    ,open_dism        ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,130,    "w") ,
    ("DxDiag"                  ,open_dxdiag      ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,160,    "w") ,
    ("Flush DNS"               ,flush_dns        ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,190,    "w") ,
    ("msconfig"                ,open_msconfig    ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,220,    "w") ,
    ("Netplwiz"                ,open_netplwiz    ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,250,    "w") ,
    ("Power Plan"              ,open_powerplan   ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,280,    "w") ,
    ("SFC"                     ,open_sfc         ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,310,    "w") ,
    ("Sniping Tool"            ,open_snippingtool,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,340,    "w") ,
    ("Systeminfo"              ,open_systeminfo  ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,370,    "w") ,
    ("UAC"                     ,open_uac         ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,400,    "w") ,
    ("Turn on Windows Features",optionalfeatures ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,430,    "w") ,
    ("Winsock Reset"           ,winsock_reset    ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,460,    "w")
]

for button_props in button_properties:
    create_button(*button_props)



#?  ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗    ████████╗ ██████╗  ██████╗ ██╗     ███████╗
#?  ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
#?  ██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║       ██║   ██║   ██║██║   ██║██║     ███████╗
#?  ██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║       ██║   ██║   ██║██║   ██║██║     ╚════██║
#?  ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║       ██║   ╚██████╔╝╚██████╔╝███████╗███████║
#?  ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝

def switch_to_pythontool_frame():
    switch_to_frame(FR_PYTHON_TOOL, MAIN_FRAME)

BT_PYTHON_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "Python Tools", switch_to_pythontool_frame, bg="#366c9c", fg="#f6d24a", height=2, width=30, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#366c9c", font=("JetBrainsMono NF", 13, "bold")) ; BT_PYTHON_MAIN_FRAME.pack(padx=(0,0),pady=(0,0))
FR_PYTHON_TOOL = tk.Frame(BORDER_FRAME, bg="#1d2027", width=520, height=800) ; FR_PYTHON_TOOL.pack_propagate(False)
BT_BACK = tk.Button(FR_PYTHON_TOOL, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_PYTHON_TOOL), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))


BOX_PYTHON_1 = tk.Frame(FR_PYTHON_TOOL, bg="#1d2027") ; BOX_PYTHON_1.pack(side="top", anchor="center", pady=(80,0), padx=(0,0))
def font_style():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\python\\font_style.py"],  shell=True)
def Keybinding():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\python\\Keybinding.py"],  shell=True)
def dictionary():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\python\\dictionary.py"],  shell=True)
def regedit_run(event=None):
    subprocess.Popen(["powershell", "-Command", "Start-Process", "-FilePath", "python", "-ArgumentList", "C:\\ms1\\scripts\\python\\regedit.py", "-Verb", "RunAs"], shell=True)


BT_font =        tk.Button(BOX_PYTHON_1, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=font_style, text="Font Style")
BT_KeyBindings = tk.Button(BOX_PYTHON_1, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=Keybinding, text="KeyBindngs")
BT_Dictionary =  tk.Button(BOX_PYTHON_1, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=dictionary, text="Dictionary")
LB_REGEDIT = tk.Label (BOX_PYTHON_1,  bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), text="Registry Editor-Run")

BT_font       .pack(side="top", anchor="center", padx=(0,0), pady=(0,0))
BT_KeyBindings.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))
BT_Dictionary .pack(side="top", anchor="center", padx=(0,0), pady=(0,0))
LB_REGEDIT.pack(side="top", anchor='center', padx=(0,0), pady=(0,0)) ; LB_REGEDIT.bind("<Button-1>", regedit_run)


def load_scripts(folder_path):
    script_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.ahk', '.ps1', '.py')):
                script_files.append(os.path.join(root, file))
    return script_files

def folder_selected(event):
    selected_folder = folder_var.get()
    script_files = load_scripts(selected_folder)
    script_var.set("Select a script")
    script_dropdown['menu'].delete(0, 'end') # Clear previous items
    for script_file in script_files:
        script_dropdown['menu'].add_command(label=os.path.basename(script_file), command=tk._setit(script_var, os.path.abspath(script_file)))

def run_script():
    selected_script = script_var.get()
    if selected_script:
        subprocess.Popen(selected_script, shell=True)

# Folders
folders = [
"C:\\ms1\\scripts\\autohotkey",
"C:\\ms1\\scripts\\python"
]
BOX_PYTHON_2 = tk.Frame(FR_PYTHON_TOOL, bg="#1d2027") ; BOX_PYTHON_2.pack(side="top", anchor="center", pady=(0,0), padx=(0,0))
# Dropdown for folders
folder_var = tk.StringVar(BOX_PYTHON_2)
folder_var.set("Select a folder")
folder_dropdown = tk.OptionMenu(BOX_PYTHON_2, folder_var, *folders, command=folder_selected)

folder_dropdown.configure(width=30, background="#ddf581", foreground="black", font=("JetBrainsMono NF", 10))
folder_dropdown.config(indicatoron=False)

# Dropdown for scripts
script_var = tk.StringVar(BOX_PYTHON_2)
script_var.set("Select a script")
script_dropdown = tk.OptionMenu(BOX_PYTHON_2, script_var, "Select a script")
script_dropdown.configure(width=30, background="#ddf581", foreground="black", font=("JetBrainsMono NF", 10))
script_dropdown.config(indicatoron=False)

run_button = tk.Button(BOX_PYTHON_2, text="Run", command=run_script, bg="#41abff", font=("JetBrainsMono NF", 12))

folder_dropdown.grid(row=0, column=1, rowspan=1, padx=5, pady=10)
script_dropdown.grid(row=1, column=1, rowspan=1, padx=5, pady=10)
run_button.grid(row=0, column=2, rowspan=2, padx=5, pady=10, sticky="nsew") #! nwse means full filling up down left right spaces so if ns means fullfill up and down portion



#! ██████╗ ███████╗███████╗████████╗ █████╗ ██████╗ ████████╗       ██╗       ███████╗██╗  ██╗██╗   ██╗████████╗██████╗  ██████╗ ██╗    ██╗███╗   ██╗
#! ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝       ██║       ██╔════╝██║  ██║██║   ██║╚══██╔══╝██╔══██╗██╔═══██╗██║    ██║████╗  ██║
#! ██████╔╝█████╗  ███████╗   ██║   ███████║██████╔╝   ██║       ████████╗    ███████╗███████║██║   ██║   ██║   ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
#! ██╔══██╗██╔══╝  ╚════██║   ██║   ██╔══██║██╔══██╗   ██║       ██╔═██╔═╝    ╚════██║██╔══██║██║   ██║   ██║   ██║  ██║██║   ██║██║███╗██║██║╚██╗██║
#! ██║  ██║███████╗███████║   ██║   ██║  ██║██║  ██║   ██║       ██████║      ███████║██║  ██║╚██████╔╝   ██║   ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
#! ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═════╝      ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝

def force_shutdown():
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to shutdown?")
    if confirmed:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
def force_restart():
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to restart?")
    if confirmed:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])

shutdown = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\shutdown3.png"))
restart = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\reboot-50x50.png"))

BOX_1 = tk.Frame(MAIN_FRAME, bg="#1d2027") ; BOX_1.pack(pady=(5,0))
# force_shutdown_bt = tk.Button(BOX_1, text="Shutdown [F]", command=force_shutdown, height=1, width=15, bg="#ff0000", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
# force_restart_bt  = tk.Button(BOX_1, text="Restart [F]",  command=force_restart,  height=1, width=15, bg="#ff6600", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
force_shutdown_bt = tk.Button(BOX_1, image=shutdown,compound=tk.TOP, text="", command=force_shutdown, height=50, width=50, bg="#1d2027", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
force_restart_bt  = tk.Button(BOX_1, image=restart, compound=tk.TOP, text="", command=force_restart,  height=50, width=50, bg="#1d2027", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))

force_shutdown_bt.pack(pady=0, side="left", anchor="w", padx=(0,30))
force_restart_bt.pack (pady=0, side="left", anchor="w", padx=(30,0))



























# Start with main frame visible
MAIN_FRAME.pack()

# Use threading to continuously update system information
# thread = threading.Thread(target=continuous_monitor, daemon=True)
# thread.start()

calculate_time_to_appear(start_time)

ROOT.mainloop()

#? EXAMPLES FOR USING PIC AS BUTTON
#* Load the PNG image
# image_path = "C:/Users/nahid/OneDrive/Desktop/aaa.png"
# photo = tk.PhotoImage(file=image_path)

#* Create the button with the image
# button = tk.Button(root, image=photo, command=lambda: print("Button clicked"))
# button.pack()

#* Test
#! Test
#? Test
#// Test
# todo Test

#! font list
# 3270 nerd font
# Agency FB
# Arial
# Calibri
# Candara
# Cascadia Code PL Nerd Font
# Comic Sans MS
# Consolas
# Courier New
# DejaVu Sans Mono Nerd Font
# FiraCode Nerd Font
# Georgia
# Hack Nerd Font
# Helvetica
# Inconsolata Nerd Font
# JetBrainsMono Nerd Font
# JetBrainsMono NF #! (must use it for tkinter)
# Lucida Console
# Meslo Nerd Font
# Mononoki Nerd Font
# Palatino Linotype
# Segoe UI
# Source Code Pro Nerd Font
# SpaceMono Nerd Font
# Tahoma
# terminess Nerd Font
# Times New Roman
# Trebuchet MS
# Verdana
# Victoria