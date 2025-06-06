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
from tkinter import Canvas, Scrollbar


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

#! Pin/Unpin
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
        if ROOT.attributes('-topmost'):
             toggle_checking()

    elif size == '■':
        ROOT.geometry('520x800')
        ROOT.configure(bg='#1d2027')
        LB_S.config(text='◀', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("ink free", 10, "bold"))
        LB_L.config(text='▼', bg="#1d2027", fg="#FFFFFF", height=1, width=2, font=("agency", 10, "bold"))
        LB_M.config(text='■', bg="#1d2027", fg="#26b2f3", height=1, width=2, font=("calibri", 10, "bold"))
        window_state = 'large'
        x_coordinate = screen_width - 520
        y_coordinate = screen_height//2 - 855//2

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
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\sync.ps1"])
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
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\backup.ps1"], shell=True)
def open_update(event=None):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\update.ps1"],  shell=True)

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

def ack_c():
    additional_text = insert_input()
    command = f'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; ack {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def ack_d():
    additional_text = insert_input()
    command = f'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; ack {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

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

FRAME_FOLDER = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800)
FRAME_FOLDER.pack_propagate(True)

BT_BACK = tk.Button(FRAME_FOLDER, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FRAME_FOLDER), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))

def create_button(text, frame, command, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button,sticky, padx_button, pady_button, padx_pack, pady_pack):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack, sticky=sticky)
    return button

BOX_1 = tk.Frame(FRAME_FOLDER, bg="#282c34")
BOX_1.pack(side="top", pady=(80,0), padx=(0,0))

BOX_2 = tk.Frame(FRAME_FOLDER, bg="#992134")
BOX_2.pack(side="top", pady=(80,0), padx=(0,0))

button_properties = [
("All Apps"      ,BOX_1, open_appsfolder_fd ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 0 ,1,1,2,"ew"   , 0,0, (0,0),(0,0)),
("AppData"       ,BOX_1, open_appdata_fd    ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 1 ,1,1,2,"ew"   , 0,0, (0,0),(0,0)),
("Git Projects"  ,BOX_1, open_git_fd        ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 2 ,1,1,2,"ew"   , 0,0, (0,0),(0,0)),
("Packages"      ,BOX_1, open_packages_fd   ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 3 ,1,1,2,"ew"   , 0,0, (0,0),(0,0)),
("ProgramData"   ,BOX_1, open_programdata_fd,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 4 ,1,1,2,"ew"   , 0,0, (0,0),(0,0)),
("Scoop"         ,BOX_1, open_scoop_fd      ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 5 ,1,1,2,"ew"   , 0,0, (0,0),(0,0)),
("Software"      ,BOX_1, open_sofware_fd    ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 6 ,1,1,2,"ew"   , 0,0, (0,0),(0,0)),
("Song"          ,BOX_1, open_song_fd       ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 7 ,1,1,2,"ew"   , 0,0, (0,0),(0,0)),
("WindowsApp"    ,BOX_1, open_Winapps_fd    ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 8 ,1,1,2,"ew"  , 0,0, (0,0),(0,0)),

("Startup System",BOX_1, open_startups_fd   ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 9 ,1,1,1,"nsew", 0,0, (0,1),(3,0)),
("Startup User"  ,BOX_1, open_usrstartups_fd,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 9 ,2,1,1,"nsew", 0,0, (1,0),(3,0)),

("Temp-AppDate"  ,BOX_1, open_templocal_fd  ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 10,1,1,1,"nsew", 0,0, (0,1),(3,0)),
("Temp-Windows"  ,BOX_1, open_tempwin_fd    ,"#ffd86a","#1D2027",1,0,"flat",("calibri",14,"bold"), 10,2,1,1,"nsew", 0,0, (1,0),(3,0)),
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

BT_PROCESS_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "Process & PKG", switch_to_process_frame, bg="#cc2400", fg="#FFFFFF", height=2, width=30, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#cc2400", font=("JetBrainsMono NF", 13, "bold"))
BT_PROCESS_MAIN_FRAME.pack(padx=(0,0),pady=(0,0))

FR_PROCESS = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800)
FR_PROCESS.pack_propagate(True)

BT_BACK = tk.Button(FR_PROCESS, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_PROCESS), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))


def insert_input():
    additional_text = WIDGET_APPID.get()
    return additional_text

def get_process():
    additional_text = insert_input()
    if not additional_text:  # Check if input is empty
        return  # Do nothing if input is empty
    command = f'Get-Process | Where-Object {{ $_.Name -like "*{additional_text}*" }} | Format-Table -Property ProcessName, Id -AutoSize'
    try:
        subprocess.run(["start","powershell", "-NoExit", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def kil_process():
    additional_text = insert_input()
    command = f'Stop-Process -Name {additional_text}'
    try:
        output = subprocess.run(["powershell", "-Command", command], stderr=subprocess.PIPE, shell=True, text=True)
        if "Cannot find a process with the name" in output.stderr:
            print(f"\033[91mError: Process {additional_text} not found.\033[0m")
        else:
            print(f"\033[94mProcess {additional_text} killed successfully.\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def custom_command():
    additional_text = insert_input()
    if not additional_text:  # Check if input is empty
        return  # Do nothing if input is empty
    profile_path = r'C:\Users\nahid\OneDrive\backup\Microsoft.PowerShell_profile.ps1'
    command = f'powershell -ExecutionPolicy Bypass -NoProfile -Command "& {{ . {profile_path}; {additional_text} }}"'
    try:
        # Execute the custom PowerShell command and capture the output
        subprocess.run(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

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

BT_CUSTOM_CMD = tk.Button(BOX_ROW_APPID2, bg="#41abff", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=custom_command, text="🏃")
BT_CUSTOM_CMD.pack(side="left", pady=0)


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


def create_button(
        text,
        command,
        bg_color,
        fg_color,
        height,
        width,
        relief,
        font,
        padx_button,
        padx_pack,
        pady_button,
        pady_pack,
        row_button,
        column_button,
        columnspan,
        sticky,
        ):
    button = tk.Button(input_frame, text=text, command=command, width=width, fg=fg_color, bg=bg_color, font=font)
    button.grid(row=row_button, column=column_button, padx=padx_button, pady=pady_button, sticky=sticky, columnspan=columnspan)
    return button

input_frame = tk.Frame(FR_PROCESS, bg="#1D2027")
input_frame.pack(pady=10)

winget_scoop_button_properties = [
("Winget"    , None               , "#76c2ff", "#000000", 1, 12, "flat", ("JetBrainsMono NF", 12), 5, 5, 0, 5,       1, 1,2 ,"ew"),
("Search"    , winget_search      , "#1D2027", "#FFFFFF", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       2, 1,1 ,""  ),
("Info"      , winget_infooo      , "#1D2027", "#FFFFFF", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       2, 2, 1,""  ),
("Install"   , winget_install     , "#1D2027", "#FFFFFF", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       3, 1,1 ,""  ),
("Uninstall" , winget_uninst      , "#1D2027", "#FFFFFF", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       3, 2, 1,""  ),
("Install"   , wget_inst_fzf      , "#1D2027", "#00FF00", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       4, 1, 1,""  ),
("Uninstall" , wget_unin_fzf      , "#1D2027", "#FF0000", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       4, 2, 1,""  ),

("Scoop"     , None               , "#95cd95", "#000000", 1, 12, "flat", ("JetBrainsMono NF", 12), 5, 5, 0, 5,       1, 3, 2,"ew"),
("Search"    , scoop_search       , "#1D2027", "#FFFFFF", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       2, 3, 1,""  ),
("Info"      , scoop_info         , "#1D2027", "#FFFFFF", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       2, 4, 1,""  ),
("Install"   , scoop_install      , "#1D2027", "#FFFFFF", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       3, 3, 1,""  ),
("Uninstall" , scoop_uninstall    , "#1D2027", "#FFFFFF", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       3, 4, 1,""  ),
("Install"   , scoop_install_fzf  , "#1D2027", "#00FF00", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       4, 3, 1,""  ),
("Uninstall" , scoop_uninstall_fzf, "#1D2027", "#FF0000", 1, 12, "flat", ("JetBrainsMono NF", 10), 5, 5, 0, 5,       4, 4, 1,""  )
]

# Create Winget buttons
for button_props in winget_scoop_button_properties:
    create_button(*button_props)


#?    █████╗ ██████╗ ██████╗ ███████╗
#?   ██╔══██╗██╔══██╗██╔══██╗██╔════╝
#?   ███████║██████╔╝██████╔╝███████╗
#?   ██╔══██║██╔═══╝ ██╔═══╝ ╚════██║
#?   ██║  ██║██║     ██║     ███████║
#?   ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝

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

#! APPLication List
BT_APPLIST = tk.Button(FR_PROCESS, text="App List", command=lambda: switch_to_frame(Page1, FR_PROCESS), bg="#ff6a2e", fg="#000", width=20, highlightthickness=5, anchor="center", font=("JetBrainsMono NF", 12, "bold"))
BT_APPLIST.pack(anchor="n", padx=(0,0), pady=(5,0))

Page1 = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800)
Page1.pack_propagate(False)

BT_BACK = tk.Button(Page1, text="◀", command=lambda: switch_to_frame(FR_PROCESS, Page1 ), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))

LB_INITIALSPC = tk.Label(Page1, text="",  bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 16, "bold"))
LB_INITIALSPC.pack(side="top", anchor="ne", padx=(0,0), pady=(50,0))

# # Create the search box label
# search_label = tk.Label(Page1, text="Search:", bg="#1d2027", fg="#fff", font=("calibri", 12, "bold"))
# search_label.pack(side="top", anchor="center", padx=(20, 0), pady=(10, 0))

# Create the search entry
search_entry = tk.Entry(Page1, font=("calibri", 12), bg="#FFFFFF", fg="#000000", insertbackground="#F00")
search_entry.pack(side="top", anchor="center", padx=(20, 0), pady=(0, 10))

def check_installation(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt):
    scoop_installed = os.path.exists(scoop_path)
    winget_installed = os.path.exists(winget_path)
    application_installed = scoop_installed or winget_installed
    chkbx_var.set(1 if application_installed else 0)

    # Change text color based on installation status if not already checked
    text_color = "green" if application_installed else "red"

    # Update the label with installation source
    installation_source = ""
    if scoop_installed:
        installation_source = "[S]"
        text_color = "#FFFFFF"  # Set color to white for [S]
    elif winget_installed:
        installation_source = "[W]"
        text_color = "#41abff"   # Set color to blue for [W]
    else:
        installation_source = "[X]"
        text_color = "#FF0000"    # Set color to red for [X]

    chkbox_bt.config(text=f"{app_name} {installation_source}", foreground=text_color)

def install_application(app_name, scoop_name, scoop_path, winget_name, winget_path, chkbx_var, chkbox_bt):
    install_options = []
    if scoop_path:
        install_options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'pwsh -Command "scoop install {scoop_name}"')})
    if winget_path:
        install_options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'winget install {winget_name}')})
    show_options(install_options)

def uninstall_application(app_name, scoop_name, scoop_path, winget_name, winget_path, chkbx_var, chkbox_bt):
    uninstall_options = []
    if scoop_path:
        uninstall_options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'pwsh -Command "scoop uninstall {scoop_name}"')})
    if winget_path:
        uninstall_options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'winget uninstall {winget_name}')})
    show_options(uninstall_options)

def show_options(options):
    top = tk.Toplevel()
    top.title("Select Installation Source")
    top.geometry("300x100")
    top.configure(bg="#282c34")
    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 100) // 2
    top.geometry(f"300x100+{x}+{y}")

    frame = tk.Frame(top, bg="#1d2027")
    frame.pack(side="top", expand=True, fill="none", anchor="center")

    for option in options:
        btn = tk.Button(frame, text=option["text"], command=option["command"], foreground="#fff", background="#1d2027", padx=10, pady=5, borderwidth=2, relief="raised")
        btn.pack(side="left", padx=5, pady=5, anchor="center")

# Variable to track checkbox state
chkbx_ack = tk.IntVar()
chkbx_adb = tk.IntVar()
chkbx_alacritty = tk.IntVar()
chkbx_aria2c = tk.IntVar()
chkbx_audiorelay = tk.IntVar()
chkbx_autohotkey1 = tk.IntVar()
chkbx_autohotkey2 = tk.IntVar()
chkbx_autoruns = tk.IntVar()
chkbx_baregrep = tk.IntVar()
chkbx_bat = tk.IntVar()
chkbx_bitwarden = tk.IntVar()
chkbx_btop = tk.IntVar()
chkbx_Capture2Text = tk.IntVar()
chkbx_cheatengine = tk.IntVar()
chkbx_clink = tk.IntVar()
chkbx_Cmder = tk.IntVar()
chkbx_cpu = tk.IntVar()
chkbx_crystaldiskinfo = tk.IntVar()
chkbx_dotnet8 = tk.IntVar()
chkbx_eza = tk.IntVar()
chkbx_fdm = tk.IntVar()
chkbx_ffmpeg = tk.IntVar()
chkbx_ffmpeg_batch = tk.IntVar()
chkbx_fileconvert = tk.IntVar()
chkbx_filezilla_server = tk.IntVar()
chkbx_flaresolverr = tk.IntVar()
chkbx_fzf = tk.IntVar()
chkbx_git = tk.IntVar()
chkbx_github = tk.IntVar()
chkbx_grep = tk.IntVar()
chkbx_highlight = tk.IntVar()
chkbx_imagemagick = tk.IntVar()
chkbx_inkscape = tk.IntVar()
chkbx_jackett = tk.IntVar()
chkbx_javaruntime = tk.IntVar()
chkbx_lazygit = tk.IntVar()
chkbx_less = tk.IntVar()
chkbx_localsend = tk.IntVar()
chkbx_nodejs = tk.IntVar()
chkbx_notepadplusplus = tk.IntVar()
chkbx_oh_my_posh = tk.IntVar()
chkbx_pandoc = tk.IntVar()
chkbx_perl = tk.IntVar()
chkbx_php = tk.IntVar()
chkbx_potplayer = tk.IntVar()
chkbx_powertoys = tk.IntVar()
chkbx_processexp = tk.IntVar()
chkbx_prowlarr = tk.IntVar()
chkbx_pwsh = tk.IntVar()
chkbx_python = tk.IntVar()
chkbx_qbit = tk.IntVar()
chkbx_radarr = tk.IntVar()
chkbx_rclone = tk.IntVar()
chkbx_ReIcon = tk.IntVar()
chkbx_rssguard = tk.IntVar()
chkbx_ruffle = tk.IntVar()
chkbx_rufus = tk.IntVar()
chkbx_scoop_completion = tk.IntVar()
chkbx_scoop_search = tk.IntVar()
chkbx_scrcpy = tk.IntVar()
chkbx_scrcpyplus = tk.IntVar()
chkbx_shell = tk.IntVar()
chkbx_sonarr = tk.IntVar()
chkbx_steam = tk.IntVar()
chkbx_syncthing = tk.IntVar()
chkbx_tldr = tk.IntVar()
chkbx_vcredist_aio = tk.IntVar()
chkbx_virtualbox_with_extension_pack_np = tk.IntVar()
chkbx_vscode = tk.IntVar()
chkbx_winaero_tweaker = tk.IntVar()
chkbx_windirstat = tk.IntVar()
chkbx_winget = tk.IntVar()
chkbx_wiseuninstall = tk.IntVar()
chkbx_WizTree = tk.IntVar()
chkbx_wsa_pacman = tk.IntVar()
chkbx_yt_dlp = tk.IntVar()

# Define applications and their information
applications = [
# {"name": "AppName"                , "scoop_name": "ScoopName"                         , "scoop_path": r'xx'                                                                                 , "winget_name": "WingetName"                               , "winget_path": r"xx"                                                                                                                                                      , "chkbx_var": chkbx_xx}                               ,
{"name": "Ack [Find]"               , "scoop_name": "ack"                               , "scoop_path": r'C:\Users\nahid\scoop\apps\ack\current\ack.bat'                                      , "winget_name": ""                                         , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_ack}                              ,
{"name": "Adb"                      , "scoop_name": "adb"                               , "scoop_path": r'C:\Users\nahid\scoop\apps\adb\current\platform-tools\adb.exe'                       , "winget_name": ""                                         , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_adb}                              ,
{"name": "Alacritty [Terminal]"     , "scoop_name": "alacritty"                         , "scoop_path": r'C:\Users\nahid\scoop\apps\alacritty\current\alacritty.exe'                          , "winget_name": "Alacritty.Alacritty"                      , "winget_path": r"C:\Program Files\Alacritty\alacritty.exe"                                                                                                                , "chkbx_var": chkbx_alacritty}                        ,
{"name": "Aria2"                    , "scoop_name": "aria2"                             , "scoop_path": r'xx'                                                                                 , "winget_name": "aria2.aria2"                              , "winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\aria2c.exe"                                                                                          , "chkbx_var": chkbx_aria2c}                           ,
{"name": "AudioRelay"               , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "AsaphaHalifa.AudioRelay"                  , "winget_path": r"C:\Program Files (x86)\AudioRelay\AudioRelay.exe"                                                                                                        , "chkbx_var": chkbx_audiorelay}                       ,
{"name": "AutoHotkey v1"            , "scoop_name": "autohotkey1.1"                     , "scoop_path": r'xx'                                                                                 , "winget_name": "9NQ8Q8J78637 --accept-package-agreements" , "winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WindowsApps\AutoHotkeyU64.exe"                                                                                    , "chkbx_var": chkbx_autohotkey1}                      ,
{"name": "AutoHotkey v2"            , "scoop_name": "autohotkey"                        , "scoop_path": r'xx'                                                                                 , "winget_name": "AutoHotkey.AutoHotkey"                    , "winget_path": r"C:\Users\nahid\AppData\Local\Programs\AutoHotkey\v2\AutoHotkey64.exe"                                                                                    , "chkbx_var": chkbx_autohotkey2}                      ,
{"name": "Autoruns"                 , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "Microsoft.Sysinternals.Autoruns"          , "winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\Microsoft.Sysinternals.Autoruns_Microsoft.Winget.Source_8wekyb3d8bbwe\autoruns.exe"               , "chkbx_var": chkbx_autoruns}                         ,
{"name": "BareGrep [Find]"          , "scoop_name": "baregrep"                          , "scoop_path": r'C:\Users\nahid\scoop\apps\baregrep\current\baregrep.exe'                            , "winget_name": "xx"                                       , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_baregrep}                         ,
{"name": "Bat [Text-View]"          , "scoop_name": "bat"                               , "scoop_path": r'C:\Users\nahid\scoop\apps\bat\current\bat.exe'                                      , "winget_name": ""                                         , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_bat}                              ,
{"name": "Bitwarden"                , "scoop_name": "bitwarden"                         , "scoop_path": r'xx'                                                                                 , "winget_name": "Bitwarden.Bitwarden"                      , "winget_path": r"C:\Users\nahid\AppData\Local\Programs\Bitwarden\Bitwarden.exe"                                                                                           , "chkbx_var": chkbx_bitwarden}                        ,
{"name": "btop [Sys-Monitor]"       , "scoop_name": "btop"                              , "scoop_path": r'C:\Users\nahid\scoop\apps\btop\current\btop.exe'                                    , "winget_name": "aristocratos.btop4win"                    , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_btop}                             ,
{"name": "Capture2Text"             , "scoop_name": "Capture2Text"                      , "scoop_path": r'C:\Users\nahid\scoop\apps\capture2text\current\Capture2Text.exe'                    , "winget_name": "xx"                                       , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_Capture2Text}                     ,
{"name": "Cheat Engine [7.4]"      , "scoop_name": "cheat-engine"                      , "scoop_path": r'C:\Users\nahid\scoop\apps\cheat-engine\current\Cheat Engine.exe'                    , "winget_name": ""                                         , "winget_path": r""                                                                                                                                                        , "chkbx_var": chkbx_cheatengine}                      ,
{"name": "clink [Terminal]"         , "scoop_name": "clink"                             , "scoop_path": r'C:\Users\nahid\scoop\apps\clink\current\clink_x64.exe'                              , "winget_name": "chrisant996.Clink"                        , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_clink}                            ,
{"name": "Cmder [Terminal]"         , "scoop_name": "Cmder"                             , "scoop_path": r'C:\Users\nahid\scoop\apps\cmder\current\Cmder.exe'                                  , "winget_name": "xx"                                       , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_Cmder}                            ,
{"name": "CPU-Z"                    , "scoop_name": "cpu-z"                             , "scoop_path": r'C:\Users\nahid\scoop\apps\cpu-z\current\cpuz_x64.exe'                               , "winget_name": "CPUID.CPU-Z"                              , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_cpu}                              ,
{"name": "Crystal DiskInfo"         , "scoop_name": "crystaldiskinfo"                   , "scoop_path": r'C:\Users\nahid\scoop\apps\crystaldiskinfo\current\DiskInfo64.exe'                   , "winget_name": "CrystalDewWorld.CrystalDiskInfo"          , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_crystaldiskinfo}                  ,
{"name": "DotNet DesktopRuntime 8"  , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "Microsoft.DotNet.DesktopRuntime.8"        , "winget_path": r"C:\Program Files\dotnet\dotnet.exe"                                                                                                                      , "chkbx_var": chkbx_dotnet8}                          ,
{"name": "eza"                      , "scoop_name": "eza"                               , "scoop_path": r'C:\Users\nahid\scoop\apps\eza\current\eza.exe'                                      , "winget_name": "eza-community.eza"                        , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_eza}                              ,
{"name": "FFmpeg-Batch"             , "scoop_name": "ffmpeg-batch"                      , "scoop_path": r'C:\Users\nahid\scoop\apps\ffmpeg-batch\current\FFBatch.exe'                         , "winget_name": "eibol.FFmpegBatchAVConverter"             , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_ffmpeg_batch}                     ,
{"name": "ffmpeg"                   , "scoop_name": "ffmpeg"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\ffmpeg\current\bin\ffmpeg.exe'                            , "winget_name": "Gyan.FFmpeg"                              , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_ffmpeg}                           ,
{"name": "FileConverter"            , "scoop_name": "file-converter-np"                 , "scoop_path": r'xx'                                                                                 , "winget_name": "AdrienAllard.FileConverter"               , "winget_path": r"C:\Program Files\File Converter\FileConverter.exe"                                                                                                       , "chkbx_var": chkbx_fileconvert}                      ,
{"name": "filezilla-server"         , "scoop_name": "filezilla-server"                  , "scoop_path": r'C:\Users\nahid\scoop\apps\filezilla-server\current\filezilla-server.exe'            , "winget_name": "xx"                                       , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_filezilla_server}                 ,
{"name": "flaresolverr"             , "scoop_name": "flaresolverr"                      , "scoop_path": r'C:\Users\nahid\scoop\apps\flaresolverr\current\flaresolverr.exe'                    , "winget_name": "xx"                                       , "winget_path": ""                                                                                                                                                         , "chkbx_var": chkbx_flaresolverr}                     ,
{"name": "FreeDownloadManager"      , "scoop_name": "ScoopName"                         , "scoop_path": r'xx'                                                                                 , "winget_name": "SoftDeluxe.FreeDownloadManager"           , "winget_path": r"C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe"                                                                                   , "chkbx_var": chkbx_fdm}                              ,
{"name": "fzf"                      , "scoop_name": "fzf"                               , "scoop_path": r'C:\Users\nahid\scoop\apps\fzf\current\fzf.exe'                                      , "winget_name": "junegunn.fzf"                             , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_fzf}                              ,
{"name": "git"                      , "scoop_name": "git"                               , "scoop_path": r'C:\Users\nahid\scoop\apps\git\current\cmd\git.exe'                                  , "winget_name": "Git.Git"                                  , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_git}                              ,
{"name": "GitHubDesktop"            , "scoop_name": "github"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\github\current\GitHubDesktop.exe'                         , "winget_name": "GitHub.GitHubDesktop"                     , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_github}                           ,
{"name": "grep [Find]"              , "scoop_name": "grep"                              , "scoop_path": r'C:\Users\nahid\scoop\apps\grep\current\grep.exe'                                    , "winget_name": "xx"                                       , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_grep}                             ,
{"name": "highlight [Text-View]"    , "scoop_name": "highlight"                         , "scoop_path": r'C:\Users\nahid\scoop\apps\highlight\current\highlight.exe'                          , "winget_name": "xx"                                       , "winget_path": ""                                                                                                                                                         , "chkbx_var": chkbx_highlight}                        ,
{"name": "imagemagick"              , "scoop_name": "imagemagick"                       , "scoop_path": r'C:\Users\nahid\scoop\apps\imagemagick\current\magick.exe'                           , "winget_name": "ImageMagick.ImageMagick"                  , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_imagemagick}                      ,
{"name": "Inkscape"                 , "scoop_name": "inkscape"                          , "scoop_path": r'xx'                                                                                 , "winget_name": "Inkscape.Inkscape"                        , "winget_path": r"C:\Program Files\Inkscape\bin\inkscape.exe"                                                                                                              , "chkbx_var": chkbx_inkscape}                         ,
{"name": "Jackett"                  , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "Jackett.Jackett"                          , "winget_path": r"C:\ProgramData\Jackett\JackettTray.exe"                                                                                                                  , "chkbx_var": chkbx_jackett}                          ,
{"name": "Java Runtime Environment" , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "Oracle.JavaRuntimeEnvironment"            , "winget_path": r"C:\Program Files (x86)\Common Files\Oracle\Java\javapath\java.exe"                                                                                       , "chkbx_var": chkbx_javaruntime}                      ,
{"name": "lazygit"                  , "scoop_name": "lazygit"                           , "scoop_path": r'C:\Users\nahid\scoop\apps\lazygit\current\lazygit.exe'                              , "winget_name": "JesseDuffield.lazygit"                    , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_lazygit}                          ,
{"name": "less [Text-View]"         , "scoop_name": "less"                              , "scoop_path": r'C:\Users\nahid\scoop\apps\less\current\less.exe'                                    , "winget_name": "jftuga.less"                              , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_less}                             ,
{"name": "localsend"                , "scoop_name": "localsend"                         , "scoop_path": r'C:\Users\nahid\scoop\apps\localsend\current\localsend_app.exe'                      , "winget_name": "LocalSend.LocalSend"                      , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_localsend}                        ,
{"name": "Nilesoft Shell"           , "scoop_name": "nilesoft-shell"                    , "scoop_path": r'xx'                                                                                 , "winget_name": "nilesoft.shell"                           , "winget_path": r"xx"                                                                                                                                                      , "chkbx_var": chkbx_shell}                            ,
{"name": "node"                     , "scoop_name": "nodejs"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\nodejs\current\node.exe'                                  , "winget_name": "OpenJS.NodeJS"                            , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_nodejs}                           ,
{"name": "notepad++"                , "scoop_name": "notepadplusplus"                   , "scoop_path": r'C:\Users\nahid\scoop\apps\notepadplusplus\current\notepad++.exe'                    , "winget_name": "Notepad++.Notepad++"                      , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_notepadplusplus}                  ,
{"name": "oh-my-posh"               , "scoop_name": "oh-my-posh"                        , "scoop_path": r'C:\Users\nahid\scoop\apps\oh-my-posh\current\oh-my-posh.exe'                        , "winget_name": "JanDeDobbeleer.OhMyPosh"                  , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_oh_my_posh}                       ,
{"name": "pandoc"                   , "scoop_name": "pandoc"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\pandoc\current\pandoc.exe'                                , "winget_name": "JohnMacFarlane.Pandoc"                    , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_pandoc}                           ,
{"name": "perl [Language]"          , "scoop_name": "perl"                              , "scoop_path": r'C:\Users\nahid\scoop\apps\perl\current\perl\bin\perl.exe'                           , "winget_name": "StrawberryPerl.StrawberryPerl"            , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_perl}                             ,
{"name": "php [Language]"           , "scoop_name": "php"                               , "scoop_path": r'C:\Users\nahid\scoop\apps\php\current\php.exe'                                      , "winget_name": ""                                         , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_php}                              ,
{"name": "PotPlayer"                , "scoop_name": "potplayer"                         , "scoop_path": r'xx'                                                                                 , "winget_name": "Daum.PotPlayer"                           , "winget_path": r"C:\Program Files\PotPlayer\PotPlayerMini64.exe"                                                                                                          , "chkbx_var": chkbx_potplayer}                        ,
{"name": "PowerShell"               , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "Microsoft.PowerShell"                     , "winget_path": r"C:\Program Files\PowerShell\7\pwsh.exe"                                                                                                                  , "chkbx_var": chkbx_pwsh}                             ,
{"name": "PowerToys"                , "scoop_name": "powertoys"                         , "scoop_path": r'C:\Users\nahid\scoop\apps\PowerToys\current\PowerToys.exe'                          , "winget_name": "Microsoft.PowerToys"                      , "winget_path": r"C:\Users\nahid\AppData\Local\PowerToys\PowerToys.exe"                                                                                                    , "chkbx_var": chkbx_powertoys}                        ,
{"name": "ProcessExplorer"          , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "Microsoft.Sysinternals.ProcessExplorer"   , "winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\Microsoft.Sysinternals.ProcessExplorer_Microsoft.Winget.Source_8wekyb3d8bbwe\process-explorer.exe", "chkbx_var": chkbx_processexp}                       ,
{"name": "Prowlarr"                 , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "TeamProwlarr.Prowlarr"                    , "winget_path": r"C:\ProgramData\Prowlarr\bin\Prowlarr.exe"                                                                                                                , "chkbx_var": chkbx_prowlarr}                         ,
{"name": "Python"                   , "scoop_name": "python"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\python\current\python.exe'                                , "winget_name": "Python.Python.3.12"                       , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_python}                           ,
{"name": "qBittorrent"              , "scoop_name": "qbittorrent"                       , "scoop_path": r'xx'                                                                                 , "winget_name": "qBittorrent.qBittorrent"                  , "winget_path": r"C:\Program Files\qBittorrent\qbittorrent.exe"                                                                                                            , "chkbx_var": chkbx_qbit}                             ,
{"name": "Radarr"                   , "scoop_name": "ScoopName"                         , "scoop_path": r'xx'                                                                                 , "winget_name": "TeamRadarr.Radarr"                        , "winget_path": r"C:\ProgramData\Radarr\bin\Radarr.exe"                                                                                                                    , "chkbx_var": chkbx_radarr}                           ,
{"name": "Rclone"                   , "scoop_name": "rclone"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\rclone\current\rclone.exe'                                , "winget_name": "Rclone.Rclone"                            , "winget_path": r'C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\rclone.exe'                                                                                          , "chkbx_var": chkbx_rclone}                           ,
{"name": "ReIcon"                   , "scoop_name": "ReIcon"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\reicon\current\ReIcon.exe'                                , "winget_name": ""                                         , "winget_path": r""                                                                                                                                                        , "chkbx_var": chkbx_ReIcon}                           ,
{"name": "Rss Guard"                , "scoop_name": "rssguard"                          , "scoop_path": r'C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe'                            , "winget_name": "martinrotter.RSSGuard"                    , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_rssguard}                         ,
{"name": "Ruffle"                   , "scoop_name": "ruffle-nightly"                    , "scoop_path": r'C:\Users\nahid\scoop\apps\ruffle-nightly\current\ruffle.exe'                        , "winget_name": "xx"                                       , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_ruffle}                           ,
{"name": "Rufus"                    , "scoop_name": "rufus"                             , "scoop_path": r'C:\Users\nahid\scoop\apps\rufus\current\rufus.exe'                                  , "winget_name": "Rufus.Rufus"                              , "winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\rufus.exe"                                                                                           , "chkbx_var": chkbx_rufus}                            ,
{"name": "scoop-completion"         , "scoop_name": "scoop-completion"                  , "scoop_path": r'C:\Users\nahid\scoop\apps\scoop-completion\current\scoop-completion.psm1'           , "winget_name": ""                                         , "winget_path": r""                                                                                                                                                        , "chkbx_var": chkbx_scoop_completion}                 ,
{"name": "scoop-search"             , "scoop_name": "scoop-search"                      , "scoop_path": r'C:\Users\nahid\scoop\apps\scoop-search\current\scoop-search.exe'                    , "winget_name": ""                                         , "winget_path": r""                                                                                                                                                        , "chkbx_var": chkbx_scoop_search}                     ,
{"name": "scrcpy"                   , "scoop_name": "scrcpy"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\scrcpy\current\scrcpy.exe'                                , "winget_name": "Genymobile.scrcpy"                        , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_scrcpy}                           ,
{"name": "scrcpy+"                  , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "Frontesque.scrcpy+"                       , "winget_path": r"C:\Users\nahid\AppData\Local\Programs\scrcpy-plus\scrcpy+.exe"                                                                                           , "chkbx_var": chkbx_scrcpyplus}                       ,
{"name": "Sonarr"                   , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "TeamSonarr.Sonarr"                        , "winget_path": r"C:\ProgramData\Sonarr\bin\Sonarr.exe"                                                                                                                    , "chkbx_var": chkbx_sonarr}                           ,
{"name": "Steam"                    , "scoop_name": "steam"                             , "scoop_path": r'xx'                                                                                 , "winget_name": "Valve.Steam"                              , "winget_path": r"C:\Program Files (x86)\Steam\steam.exe"                                                                                                                  , "chkbx_var": chkbx_steam}                            ,
{"name": "Syncthing"                , "scoop_name": "syncthing"                         , "scoop_path": r'C:\Users\nahid\scoop\apps\syncthing\current\syncthing.exe'                          , "winget_name": "Syncthing.Syncthing"                      , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_syncthing}                        ,
{"name": "tldr"                     , "scoop_name": "tldr"                              , "scoop_path": r'C:\Users\nahid\scoop\apps\tldr\current\tldr.exe'                                    , "winget_name": "tldr-pages.tlrc"                          , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_tldr}                             ,
{"name": "VCredist-aio"             , "scoop_name": "vcredist-aio"                      , "scoop_path": r'C:\Users\nahid\scoop\apps\vcredist-aio\current\VisualCppRedist_AIO_x86_x64.exe'     , "winget_name": "abbodi1406.vcredist"                      , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_vcredist_aio}                     ,
{"name": "VirtualBox"               , "scoop_name": "virtualbox-with-extension-pack-np" , "scoop_path": r'C:\Users\nahid\scoop\apps\virtualbox-with-extension-pack-np\current\VirtualBox.exe' , "winget_name": "Oracle.VirtualBox"                        , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_virtualbox_with_extension_pack_np},
{"name": "VSCode"                   , "scoop_name": "vscode"                            , "scoop_path": r''                                                                                   , "winget_name": "Microsoft.VisualStudioCode"               , "winget_path": r"C:\Users\nahid\AppData\Local\Programs\Microsoft VS Code\Code.exe"                                                                                        , "chkbx_var": chkbx_vscode}                           ,
{"name": "WinaeroTweaker"           , "scoop_name": "winaero-tweaker"                   , "scoop_path": r'C:\Users\nahid\scoop\apps\winaero-tweaker\current\WinaeroTweaker.exe'               , "winget_name": ""                                         , "winget_path": "r"                                                                                                                                                        , "chkbx_var": chkbx_winaero_tweaker}                  ,
{"name": "windirstat"               , "scoop_name": "windirstat"                        , "scoop_path": r'C:\Users\nahid\scoop\apps\windirstat\current\windirstat.exe'                        , "winget_name": "WinDirStat.WinDirStat"                    , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_windirstat}                       ,
{"name": "winget"                   , "scoop_name": "winget"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\winget\current\winget.exe'                                , "winget_name": ""                                         , "winget_path": r""                                                                                                                                                        , "chkbx_var": chkbx_winget}                           ,
{"name": "Wise Program Uninstaller" , "scoop_name": ""                                  , "scoop_path": r''                                                                                   , "winget_name": "WiseCleaner.WiseProgramUninstaller"       , "winget_path": r"C:\Program Files (x86)\Wise\Wise Program Uninstaller\WiseProgramUninstaller.exe"                                                                         , "chkbx_var": chkbx_wiseuninstall}                    ,
{"name": "WizTree"                  , "scoop_name": "WizTree"                           , "scoop_path": r'C:\Users\nahid\scoop\apps\wiztree\current\WizTree64.exe'                            , "winget_name": "AntibodySoftware.WizTree"                 , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_WizTree}                          ,
{"name": "WSA-pacman"               , "scoop_name": "wsa-pacman"                        , "scoop_path": r'C:\Users\nahid\scoop\apps\wsa-pacman\current\WSA-pacman.exe'                        , "winget_name": "alesimula.wsa_pacman"                     , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_wsa_pacman}                       ,
{"name": "yt-dlp"                   , "scoop_name": "yt-dlp"                            , "scoop_path": r'C:\Users\nahid\scoop\apps\yt-dlp\current\yt-dlp.exe'                                , "winget_name": "yt-dlp.yt-dlp"                            , "winget_path": "xx"                                                                                                                                                       , "chkbx_var": chkbx_yt_dlp}                           ,
]

# Create canvas and scrollbar
canvas = Canvas(Page1, bg="#1d2027", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

#! scrollbar Start
def on_mousewheel(event):
    # Check if the mouse is over the scrollbar
    if event.widget == scrollbar:
        canvas.yview_scroll(-5 * (event.delta // 120), "units")  # Increase scroll speed
    else:
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)


# Create a vertical scrollbar
scrollbar = ttk.Scrollbar(Page1, orient="vertical", style="Custom.Vertical.TScrollbar")
scrollbar.pack(side="right", fill="y")

# Configure canvas to use the scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

# Configure the style of the scrollbar
style = ttk.Style()
style.theme_use("default")

# Set the background color of the scrollbar to red
style.configure("Custom.Vertical.TScrollbar", background="#ff922e", troughcolor="#626c80", width=25)

# Set the thickness of the outside bar to 10 pixels
style.map("Custom.Vertical.TScrollbar",
    background=[("active", "#ff922e")],  # Changed from blue to red
)

# Set the thickness of the inside bar to 5 pixels
style.map("Custom.Vertical.TScrollbar",
    troughcolor=[("active", "#626c80")],  # Changed from blue to red
)
#! scrollbar End

# Create a frame inside the canvas
frame = tk.Frame(canvas, bg="#1d2027")
canvas.create_window((0, 0), window=frame, anchor="nw")

# Update the applications dictionary to store the row number for each app
for app in applications:
    app["frame"] = tk.Frame(frame, bg="#1d2027")
row_number = 0

# Create and pack checkboxes, check buttons, install buttons, and uninstall buttons for each application inside the frame
for app in applications:
    app_frame = app["frame"]
    app_frame.grid(row=row_number, column=0, padx=(80,0), pady=(0,0), sticky="ew")  # Adjusted sticky parameter
    row_number += 1

    app_name = app["name"]
    scoop_name = app["scoop_name"]
    scoop_path = app["scoop_path"]
    winget_name = app["winget_name"]
    winget_path = app["winget_path"]
    chkbx_var = app["chkbx_var"]

    chkbox_bt = tk.Checkbutton(app_frame, text=app_name, variable=chkbx_var, font=("JetBrainsMono NF", 12, "bold"), foreground="green", background="#1d2027", activebackground="#1d2027", selectcolor="#1d2027", padx=10, pady=1, borderwidth=2, relief="flat")
    chkbox_bt.configure(command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: check_installation(name, scoop, winget, var, cb))
    chk_bt = tk.Button(app_frame, text=f"Check", foreground="green", background="#1d2027", command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: check_installation(name, scoop, winget, var, cb))
    ins_bt = tk.Button(app_frame, text=f"n", foreground="green", background="#1d2027", font=("webdings", 5), relief="flat", command=lambda name=app_name, scoop=scoop_name, scoop_path=scoop_path, winget=winget_name, winget_path=winget_path, var=chkbx_var, cb=chkbox_bt: install_application(name, scoop, scoop_path, winget, winget_path, var, cb))
    unins_bt = tk.Button(app_frame, text=f"n", foreground="red",  background="#1d2027", font=("webdings", 5), relief="flat", command=lambda name=app_name, scoop=scoop_name, scoop_path=scoop_path, winget=winget_name, winget_path=winget_path, var=chkbx_var, cb=chkbox_bt: uninstall_application(name, scoop, scoop_path, winget, winget_path, var, cb))

    chkbox_bt.grid(row=0, column=0, padx=(0,0), pady=(0,0))
    # chk_bt.pack(side="left", padx=(0,0), pady=(0,0))
    ins_bt.grid(row=0, column=1, padx=(0,0), pady=(0,0))
    unins_bt.grid(row=0, column=2, padx=(0,0), pady=(0,0))
    check_installation(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt)

# Function to filter and update displayed apps based on search query
def filter_apps(event=None):
    search_query = search_entry.get().lower()
    for app in applications:
        app_name = app["name"]
        app_frame = app["frame"]
        if search_query in app_name.lower():
            app_frame.grid()
        else:
            app_frame.grid_remove()

# Bind the filtering function to the KeyRelease event of the search entry
search_entry.bind("<KeyRelease>", filter_apps)

# Update scroll region
frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))



def create_button(text, frame, command, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button,sticky, padx_button, pady_button, padx_pack, pady_pack):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack, sticky=sticky)
    return button

BOX_1 = tk.Frame(FR_PROCESS, bg="#1d2027")
BOX_1.pack(side="top", anchor="center", pady=(20,0), padx=(0,0))




button_properties = [
("FFMPEG"         ,BOX_1, "none"            ,"#98c379","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 0 ,1,1,5,"ew" , 0,0, (1,1),(0,0)),
("Trim"           ,BOX_1, open_ffmpeg_trimm ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,1,1,1,"ew" , 0,0, (1,1),(0,0)),
("Convert"        ,BOX_1, open_ffmpeg_convt ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,2,1,1,"ew" , 0,0, (1,1),(0,0)),
("Dimension"      ,BOX_1, open_ffmpeg_dimns ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,3,1,1,"ew" , 0,0, (1,1),(0,0)),
("Imagedimension" ,BOX_1, open_ffmpeg_imgdm ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,4,1,1,"ew" , 0,0, (1,1),(0,0)),
("Merge"          ,BOX_1, open_ffmpeg_merge ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,5,1,1,"ew" , 0,0, (1,1),(0,0)),
]

for button_props in button_properties:
    create_button(*button_props)

BOX_find = tk.Frame(FR_PROCESS, bg="#1d2027")
BOX_find.pack(side="top", anchor="center", pady=(20,0), padx=(0,0))

button_properties = [
("Find"         ,BOX_find, "none"    ,"#79828b","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 0 ,1,1,5,"ew" , 0,0, (1,1),(0,0)),
("File"    ,BOX_find, find_file ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,1,1,1,"ew" , 0,0, (1,1),(0,0)),
("Pattern" ,BOX_find, find_patt ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,2,1,1,"ew" , 0,0, (1,1),(0,0)),
("Size"    ,BOX_find, find_size ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,3,1,1,"ew" , 0,0, (1,1),(0,0)),

("FZF-->C:\\"    ,BOX_find, fzf_c ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,4,1,1,"ew" , 0,0, (1,1),(0,0)),
("FZF-->D:\\"    ,BOX_find, fzf_d ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 1 ,5,1,1,"ew" , 0,0, (1,1),(0,0)),


("ACK-->C:\\"    ,BOX_find, ack_c ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 2 ,1,1,1,"ew" , 0,0, (1,1),(0,0)),
("ACK-->D:\\"    ,BOX_find, ack_d ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 2 ,2,1,1,"ew" , 0,0, (1,1),(0,0)),
]

for button_props in button_properties:
    create_button(*button_props)



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
def character_map():
    subprocess.Popen(["powershell", "charmap"])

#! Tool Button

def switch_to_tools_frame():
    switch_to_frame(FRAME_TOOLS, MAIN_FRAME)

BT_TOOLS = M1_hold_release(MAIN_FRAME, "TOOLS", switch_to_tools_frame, bg="#454545", fg="#FFFFFF", height=2, width=30, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#454545", font=("JetBrainsMono NF", 13, "bold"))
BT_TOOLS.pack(padx=(0,0),pady=(0,0))

FRAME_TOOLS = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800)
FRAME_TOOLS.pack_propagate(True)

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
    ("Winsock Reset"           ,winsock_reset    ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,460,    "w") ,
    ("Character Map"           ,character_map    ,"#FFFFFF","#1D2027",1,25,"solid",("agency",14,"bold"),0,0,  100,460,    "w") ,
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

BT_PYTHON_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "Python Tools", switch_to_pythontool_frame, bg="#366c9c", fg="#f6d24a", height=2, width=30, anchor="w", relief="flat", highlightthickness=2, highlightbackground="#366c9c", font=("JetBrainsMono NF", 13, "bold"))
BT_PYTHON_MAIN_FRAME.pack(padx=(0,0),pady=(0,0))

FR_PYTHON_TOOL = tk.Frame(BORDER_FRAME, bg="#1d2027", width=520, height=800)
FR_PYTHON_TOOL.pack_propagate(False)

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