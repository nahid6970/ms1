import importlib
import subprocess
from functionlist import *

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
    "Image",
    "lib",
    "pywin32",
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
# install_missing_libraries()

#! Now import the libraries
# from tkinter import PhotoImage
# import shutil
# import tksvg
# import win32gui
# from tkinter import Canvas, Scrollbar
from datetime import datetime
from PIL import Image, ImageTk
from pyadl import ADLManager
from time import strftime
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import ctypes
from customtkinter import *
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

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width//2 - 1920//2
# y = screen_height//2 - 800//2
y = screen_height-47-37
ROOT.geometry(f"1920x39+{x}+{y}") #! overall size of the window

#! Resize Window

# Function to toggle window size
def toggle_window_size(size):
    global window_state
    global x
    global y

    if size == 'line':
        ROOT.geometry('1920x39')
        x = screen_width // 2 - 1920 // 2
        y = screen_height-47-37
        ROOT.configure(bg='red')
        LB_L.config(text='\ueab7', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("JetBrainsMono NF", 16, "bold"))
        LB_M.config(text='\uea72', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("JetBrainsMono NF", 18, "bold"))
    elif size == 'max':
        ROOT.geometry('1920x140')
        x = screen_width // 2 - 1920 // 2
        y = screen_height-47-37
        ROOT.configure(bg='#1d2027')
        LB_L.config(text='\ueab7', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("JetBrainsMono NF", 16, "bold"))
        LB_M.config(text='\uea72', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("JetBrainsMono NF", 18, "bold"))

    ROOT.focus_force()
    ROOT.update_idletasks()
    ROOT.geometry(f'{ROOT.winfo_width()}x{ROOT.winfo_height()}+{x}+{y}')

def on_windows_x_pressed():
    global window_size_state
    if window_size_state == 'line':
        toggle_window_size('max')
        window_size_state = 'max'
    else:
        toggle_window_size('line')
        window_size_state = 'line'
        
# Initial window size state
window_size_state = 'line'
# Bind Windows + X to toggle between 'line' and 'max' sizesx
#! keyboard.add_hotkey('win+x', on_windows_x_pressed)

# x = screen_width//2 - 753//2
# y = 0
# ROOT.geometry(f"+{x}+{y}")

# Create main frame
MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920, height=800)
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1, expand=True)  # Add some padding at the top


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

def toggle_checking():
    global checking
    checking = not checking
    if checking:
        if ROOT.attributes('-topmost'):  # Only start checking if already topmost
            check_window_topmost()  # Start checking if toggled on and already topmost
        BT_TOPMOST.config(fg="#000000")  # Change text color to green
        BT_TOPMOST.config(bg="#FFFFFF")  # Change text color to green
    else:
        ROOT.after_cancel(check_window_topmost)  # Cancel the checking if toggled off
        BT_TOPMOST.config(fg="#FFFFFF")  # Change text color to white
        BT_TOPMOST.config(bg="#000000")  # Change text color to white

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
    LB_DUC.config(bg='#f12c2f' if disk_c_usage > 90 else '#464b57', fg='#FFFFFF' if disk_c_usage > 90 else '#fff')
    LB_DUD.config(bg='#f12c2f' if disk_d_usage > 90 else '#464b57', fg='#FFFFFF' if disk_d_usage > 90 else '#fff')

    ROOT.after(1000, update_info_labels)
# Initialize static variables for network speed calculation
get_net_speed.upload_speed_last = 0
get_net_speed.download_speed_last = 0

#! Github status
from queue import Queue

def check_git_status(git_path, queue):
    if not os.path.exists(git_path):
        queue.put((git_path, "Invalid path"))
        return
    os.chdir(git_path)
    git_status = subprocess.run(["git", "status"], capture_output=True, text=True)
    if "nothing to commit, working tree clean" in git_status.stdout:
        queue.put((git_path, "✅", "#00ff21"))
    else:
        queue.put((git_path, "✅", "#fe1616"))
def show_git_changes(git_path):
    if not os.path.exists(git_path):
        print("Invalid path")
        return
    os.chdir(git_path)
    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", "git status"])
def update_status():
    while True:
        check_git_status("C:\\ms1", queue)
        check_git_status("C:\\ms2", queue)
        time.sleep(1)
def update_gui():
    while True:
        try:
            git_path, text, color = queue.get_nowait()
            if git_path == "C:\\ms1":
                STATUS_MS1.config(text=text, fg=color)
            elif git_path == "C:\\ms2":
                STATUS_MS2.config(text=text, fg=color)
        except:
            pass
        time.sleep(0.1)  # Adjust sleep time as needed

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
    uptime_label.configure(text=f"{uptime_str}")
    uptime_label.after(1000, update_uptime_label)




default_font = ("Jetbrainsmono nfp", 10)
ROOT.option_add("*Font", default_font)


#! ALL Boxes
ROOT1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT1.pack(side="left", pady=(2,2),padx=(5,1),  anchor="w", fill="x")

ROOT2 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT2.pack(side="right", pady=(2,2),padx=(5,1), anchor="e", fill="x")

FR_FFmpeg = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
FR_FFmpeg.pack_propagate(True)

FR_Find = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
FR_Find.pack_propagate(True)

#! Left Side
uptime_label=CTkLabel(ROOT1, text="", corner_radius=25, width=100,height=20,  text_color="#ffffff",fg_color="#44547a", font=("JetBrainsMono NFP" ,16,"bold"))
uptime_label.pack(side="left",padx=(0,0),pady=(1,0))
uptime_label.bind("<Button-1>",None)

LB_K=CTkLabel(ROOT1, text="\udb80\udf0c", bg_color="#1d2027",text_color="#26b2f3", anchor="w",font=("JetBrainsMono NFP",25,"bold"))
LB_K.pack(side="left",padx=(10,0),pady=(1,0))
LB_K.bind("<Button-1>",start_shortcut)

Tools_bt=CTkLabel(ROOT1, text="\ue20f", bg_color="#1d2027",text_color="#26b2f3", anchor="w",font=("JetBrainsMono NFP",18,"bold"))
Tools_bt.pack(side="left",padx=(10,0),pady=(1,0))
Tools_bt.bind("<Button-1>", start_tools)

AppManagement_bt=CTkLabel(ROOT1, text="\uf40e", bg_color="#1d2027",text_color="#26b2f3", anchor="w",font=("JetBrainsMono NFP",18,"bold"))
AppManagement_bt.pack(side="left",padx=(10,0),pady=(1,0))
AppManagement_bt.bind("<Button-1>", start_appstore)
AppManagement_bt.bind("<Button-3>", start_applist)

Folder_bt=CTkLabel(ROOT1, text="\ueaf7", bg_color="#1d2027",text_color="#ffd900", anchor="w",font=("JetBrainsMono NFP",18,"bold"))
Folder_bt.pack(side="left",padx=(10,0),pady=(1,0))
Folder_bt.bind("<Button-1>", start_folder)
Folder_bt.bind("<Control-Button-1>", Edit_folder)

Process_bt=CTkLabel(ROOT1, text="\ueba2", bg_color="#1d2027",text_color="#ff1313", anchor="w",font=("JetBrainsMono NFP",18,"bold"))
Process_bt.pack(side="left",padx=(10,0),pady=(1,0))
Process_bt.bind("<Button-1>", start_process)
Process_bt.bind("<Control-Button-1>", Edit_process)

ScriptList_bt=CTkLabel(ROOT1, text="\uf03a", bg_color="#1d2027",text_color="#e0a04c", anchor="w",font=("JetBrainsMono NFP",18,"bold"))
ScriptList_bt.pack(side="left",padx=(10,0),pady=(1,0))
ScriptList_bt.bind("<Button-1>", start_script_list)
ScriptList_bt.bind("<Control-Button-1>", edit_script_list)

LB_1=tk.Label(ROOT1, text="\udb83\udca0",bg="#1d2027",fg="#2af083",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
LB_1.pack(side="left",padx=(3,0),pady=(0,0))
LB_1.bind("<Button-1>",start_bar_1)

BT_TOPMOST=tk.Label(ROOT1,text="\udb81\udc03",bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",12,"bold"))
BT_TOPMOST.pack(side="left",padx=(3,0),pady=(0,0))
BT_TOPMOST.bind  ("<Button-1>",lambda event:toggle_checking())

CLEAR=tk.Label(ROOT1, text="\ueabf",bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",12,"bold"))
CLEAR.pack(side="left",padx=(3,0),pady=(0,0))
CLEAR.bind("<Button-1>",lambda event:clear_screen())

LB_get=tk.Label(ROOT1, text="G",bg="#1d2027",fg="#ff0000",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",12,"bold"))
LB_get.pack(side="left",padx=(3,0),pady=(0,0))
LB_get.bind("<Button-1>",lambda event:get_active_window_info())

bkup=tk.Label(ROOT1,text="\ue621 \udb80\udea2",bg="#1d2027",fg="#009fff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
bkup.pack(side="left",padx=(3,0),pady=(0,0))
bkup.bind ("<Button-1>",start_backup)

STATUS_MS1=tk.Label(ROOT1,bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",10,"bold"),text="")
STATUS_MS1.pack(side="left",padx=(3,0),pady=(0,0))
STATUS_MS1.bind("<Button-1>",lambda event:show_git_changes("C:\\ms1"))
STATUS_MS2=tk.Label(ROOT1,bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",10,"bold"),text="")
STATUS_MS2.pack(side="left",padx=(3,0),pady=(0,0))
STATUS_MS2.bind("<Button-1>",lambda event:show_git_changes("C:\\ms2"))

FFMPEG_bt = CTkButton(ROOT1, text="FFMPEG",width=0, command=lambda:switch_to_frame(FR_FFmpeg , MAIN_FRAME)) ; FFMPEG_bt.pack(side="left")
back_button      =tk.Button(FR_FFmpeg,text="\ueb6f FFMPEG"     ,width=0,bg="#98c379",fg="#1D2027",command=lambda:switch_to_frame (MAIN_FRAME    ,FR_FFmpeg)); back_button.pack(side="left" )
Trim_bt          =tk.Button(FR_FFmpeg,text="Trim"              ,width=0,fg="#FFFFFF",bg="#1D2027",command=lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\trim.ps1"     ])); Trim_bt.pack          (side="left",padx=(0,0))
Convert_bt       =tk.Button(FR_FFmpeg,text="Convert"           ,width=0,fg="#FFFFFF",bg="#1D2027",command=lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\convert.ps1"  ])); Convert_bt.pack       (side="left",padx=(0,0))
Dimension_bt     =tk.Button(FR_FFmpeg,text="Dimension"         ,width=0,fg="#FFFFFF",bg="#1D2027",command=lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\dimension.ps1"])); Dimension_bt.pack     (side="left",padx=(0,0))
Imagedimension_bt=tk.Button(FR_FFmpeg,text="Imagedimension"    ,width=0,fg="#FFFFFF",bg="#1D2027",command=lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\imgdim.ps1"   ])); Imagedimension_bt.pack(side="left",padx=(0,0))
Merge_bt         =tk.Button(FR_FFmpeg,text="Merge"             ,width=0,fg="#FFFFFF",bg="#1D2027",command=lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\merge.ps1"    ])); Merge_bt.pack         (side="left",padx=(0,0))

Find_bt = CTkButton(MAIN_FRAME, text="Find",width=0, command=lambda:switch_to_frame(FR_Find , MAIN_FRAME)) ; Find_bt.pack(side="left")
back_button=tk.Button(FR_Find,text="\ueb6f Find",width=0 ,bg="#98c379", fg="#1D2027", command=lambda:switch_to_frame(MAIN_FRAME,FR_Find)); back_button.pack(side="left" ,padx=(0,0))
File_bt    =tk.Button(FR_Find,text="File"       ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_file        ); File_bt.pack                       (side="left" ,padx=(0,0))
Pattern_bt =tk.Button(FR_Find,text="Pattern"    ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_pattern     ); Pattern_bt.pack                    (side="left" ,padx=(0,0))
Size_bt    =tk.Button(FR_Find,text="Size"       ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_size        ); Size_bt.pack                       (side="left" ,padx=(0,0))
FZFC_bt    =tk.Button(FR_Find,text="FZF-C"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_fzf_c            ); FZFC_bt.pack                       (side="left" ,padx=(0,0))
FZFD_bt    =tk.Button(FR_Find,text="FZF-D"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_fzf_d            ); FZFD_bt.pack                       (side="left" ,padx=(0,0))
ackc_bt    =tk.Button(FR_Find,text="ACK-C"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_ack_c            ); ackc_bt.pack                       (side="left" ,padx=(0,0))
ackd_bt    =tk.Button(FR_Find,text="ACK-D"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_ack_d            ); ackd_bt.pack                       (side="left" ,padx=(0,0))





#! Right Side
LB_DWLOAD=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =7,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_DWLOAD.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_DWLOAD.bind("<Button-1>",None)

LB_UPLOAD=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =7,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_UPLOAD.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_UPLOAD.bind("<Button-1>",None)

cpu_core_frame =CTkFrame(ROOT2,corner_radius=5,bg_color="#1d2027",border_width=1,border_color="#000000", fg_color="#fff")
cpu_core_frame.pack(side="left",padx=(3,0),pady=(0,0))

LB_CPU=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#ffffff",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_CPU.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_CPU.bind   ("<Button-1>",None)

LB_GPU=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#ffffff",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_GPU.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_GPU.bind("<Button-1>",None)

LB_RAM=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#ffffff",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_RAM.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_RAM.bind("<Button-1>",None)

LB_DUC=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =8,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_DUC.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_DUC.bind("<Button-1>",None)

LB_DUD=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =8,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_DUD.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_DUD.bind("<Button-1>",None)

LB_R=tk.Label(ROOT2,bg="#1d2027",fg="#26b2f3",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",12,"bold"),text="\uf0e2")
LB_R.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_R.bind("<Button-1>",restart)

LB_L=tk.Label(ROOT2,bg="#1d2027",fg="#00FF00",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",16,"bold"),text="\uf106")
LB_L.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_L.bind("<Button-1>",lambda event:toggle_window_size('line'))

LB_M=tk.Label(ROOT2,bg="#1d2027",fg="#26b2f3",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",18,"bold"),text="\uea72")
LB_M.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_M.bind("<Button-1>",lambda event:toggle_window_size('max'))

LB_XXX=tk.Label(ROOT2,bg="#1d2027",fg="#ff0000",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",16,"bold"),text="\uf00d")
LB_XXX.pack(side="left",padx=(3,10),pady=(0,0))
LB_XXX.bind("<Button-1>",close_window)




cpu_core_bars = []
for i in range(psutil.cpu_count()):
    frame = CTkFrame(cpu_core_frame, bg_color="#1d2027")
    frame.pack(side="left", padx=(0, 0), pady=0)
    core_bar = CTkCanvas(frame, bg="#53565c", width=BAR_WIDTH, height=BAR_HEIGHT, highlightthickness=0)
    core_bar.pack(side="top")
    cpu_core_bars.append(core_bar)
update_cpu_core_bars()

queue = Queue()
status_thread = threading.Thread(target=update_status, daemon=True)
gui_thread = threading.Thread(target=update_gui, daemon=True)
status_thread.start()
gui_thread.start()

update_uptime_label()
update_info_labels()
check_window_topmost()

#!  ███╗   ███╗ █████╗ ██╗███╗   ██╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#!  ████╗ ████║██╔══██╗██║████╗  ██║    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#!  ██╔████╔██║███████║██║██╔██╗ ██║    █████╗  ██████╔╝███████║██╔████╔██║█████╗
#!  ██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#!  ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#!  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

BOX_1_2nd = tk.Frame(MAIN_FRAME, bg="#1d2027")
BOX_1_2nd.pack(pady=(32,0))

icon_folder     =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_applist    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_appstore   =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_ffmpeg     =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_find       =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_process    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_tools      =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_ScriptList =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))

def create_button_advanced(parent, text="", image=None, command=None, compound=None, height=0, width=0, bg="#e7d86a", fg="#1D2027", font=("JetBrainsMono NF", 13, "bold"), anchor="center", bd=0, relief="flat", highlightthickness=4, activebackground="#000000", activeforeground="#f6d24a", cursor="hand2", side="left", padx=(0,0), pady=(0,0)):
    button = tk.Button(parent, text=text, image=image, command=command, compound=compound, height=height, width=width, bg=bg, fg=fg, font=font, anchor=anchor, bd=bd, relief=relief, highlightthickness=highlightthickness, activebackground=activebackground, activeforeground=activeforeground, cursor=cursor)
    button.pack(side=side, padx=padx, pady=pady)
    return button

# Creating buttons with advanced properties
button_properties_advanced =[
]
advanced_buttons = [create_button_advanced(**prop) for prop in button_properties_advanced]




#! ██████╗ ███████╗███████╗████████╗ █████╗ ██████╗ ████████╗       ██╗       ███████╗██╗  ██╗██╗   ██╗████████╗██████╗  ██████╗ ██╗    ██╗███╗   ██╗
#! ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝       ██║       ██╔════╝██║  ██║██║   ██║╚══██╔══╝██╔══██╗██╔═══██╗██║    ██║████╗  ██║
#! ██████╔╝█████╗  ███████╗   ██║   ███████║██████╔╝   ██║       ████████╗    ███████╗███████║██║   ██║   ██║   ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
#! ██╔══██╗██╔══╝  ╚════██║   ██║   ██╔══██║██╔══██╗   ██║       ██╔═██╔═╝    ╚════██║██╔══██║██║   ██║   ██║   ██║  ██║██║   ██║██║███╗██║██║╚██╗██║
#! ██║  ██║███████╗███████║   ██║   ██║  ██║██║  ██║   ██║       ██████║      ███████║██║  ██║╚██████╔╝   ██║   ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
#! ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═════╝      ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝

BOX_2 = tk.Frame(MAIN_FRAME, bg="#1d2027")
BOX_2.pack(pady=(5,0))

def force_shutdown():
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to shutdown?")
    if confirmed:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
def force_restart():
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to restart?")
    if confirmed:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])

def open_backup(event=None):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\backup.ps1"], shell=True)
def open_update(event=None):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\update.ps1"],  shell=True)

def c_size(event=None):
    subprocess.run(["powershell", "Start-Process rclone -ArgumentList 'ncdu c:\\' "])
def d_size(event=None):
    subprocess.run(["powershell", "Start-Process rclone -ArgumentList 'ncdu d:\\' "])

# shutdown_window =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\shutdown3.png"))
# restart_window  =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\reboot-50x50.png"))
# update_image    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\inkspace\\update.png"))
# backup_image    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\inkspace\\backup-50x50.png"))
# rclone_c        =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\inkspace\\rclone_c.png"))
# rclone_d        =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\inkspace\\rclone_d.png"))


# def create_button(parent, text="", image=None, compound=None, command=None, height=50, width=50, bg="#1d2027", fg="#ffffff", bd=0, relief="flat", highlightthickness=4, activebackground="#000000", activeforeground="#FFFFFF", row=0, column=0, rowspan=1, columnspan=1):
#     button = tk.Button(parent, text=text, image=image, compound=compound, command=command, height=height, width=width, bg=bg, fg=fg, bd=bd, relief=relief, highlightthickness=highlightthickness, activebackground=activebackground, activeforeground=activeforeground)
#     button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="w", padx=(0,0), pady=0)
#     return button

# button_properties = [
# {"parent": BOX_2,"image": shutdown_window,"compound": tk.TOP,"text": "","command": force_shutdown,"row": 1,"column": 1,"rowspan":1,"columnspan":1},
# {"parent": BOX_2,"image": restart_window ,"compound": tk.TOP,"text": "","command": force_restart ,"row": 1,"column": 2,"rowspan":1,"columnspan":1},
# {"parent": BOX_2,"image": backup_image   ,"compound": tk.TOP,"text": "","command": open_backup   ,"row": 1,"column": 3,"rowspan":1,"columnspan":1},
# {"parent": BOX_2,"image": update_image   ,"compound": tk.TOP,"text": "","command": open_update   ,"row": 1,"column": 4,"rowspan":1,"columnspan":1},
# {"parent": BOX_2,"image": rclone_c       ,"compound": tk.TOP,"text": "","command": c_size        ,"row": 1,"column": 5,"rowspan":1,"columnspan":1},
# {"parent": BOX_2,"image": rclone_d       ,"compound": tk.TOP,"text": "","command": d_size        ,"row": 1,"column": 6,"rowspan":1,"columnspan":1},
# ]
# buttons = [create_button(**prop) for prop in button_properties]





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

def force_shutdown():
    # Your function logic here
    pass

BOX_2 = tk.Frame(MAIN_FRAME, bg="#1d2027")
BOX_2.pack(pady=(5,0))

BT_name = HoverButton(BOX_2, bg="#000000",activebackground="green", hover_color="red", fg="#FFFFFF", hover_fg="#000000", height=0, width=0, relief="solid",  font=("jetbrainsmono nf", 14, "bold"), command=force_shutdown, text="\uf011")
BT_name.pack(side="top",  padx=(0,0), pady=(0,0))




# Start with main frame visible

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