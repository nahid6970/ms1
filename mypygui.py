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
from tkinter import simpledialog
from tkinter import ttk
import ctypes
import keyboard
import os
import psutil
import pyautogui
import subprocess
import sys
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

x = screen_width//2 - 800//2
# y = screen_height//2 - 800//2
y = 0
ROOT.geometry(f"800x30+{x}+{y}") #! overall size of the window


# x = screen_width//2 - 753//2
# y = 0
# ROOT.geometry(f"+{x}+{y}")


#?  ██████╗  ██████╗  ██████╗ ████████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#?  ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#?  ██████╔╝██║   ██║██║   ██║   ██║       █████╗  ██████╔╝███████║██╔████╔██║█████╗
#?  ██╔══██╗██║   ██║██║   ██║   ██║       ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#?  ██║  ██║╚██████╔╝╚██████╔╝   ██║       ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#?  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

#! Close Window
# def close_window(event=None):
#     ROOT.destroy()

def close_window(event=None):
    password = simpledialog.askstring("Password", "Enter the password to close the window:")
    if password == "":  # Replace "your_password_here" with your actual password
        ROOT.destroy()
    else:
        print("Incorrect password. Window not closed.")

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

#! Resize Window

# Function to toggle window size
def toggle_window_size(size):
    global window_state
    global x
    global y

    if size == 'line':
        ROOT.geometry('800x30')
        x = screen_width // 2 - 800 // 2
        y = 0
        ROOT.configure(bg='red')
        LB_L.config(text='T', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("Wingdings 3", 10, "bold"))
        LB_M.config(text='o', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("Wingdings", 10, "bold"))
    elif size == 'max':
        ROOT.geometry('800x800')
        x = screen_width // 2 - 800 // 2
        y = 0
        ROOT.configure(bg='#1d2027')
        LB_L.config(text='T', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("Wingdings 3", 10, "bold"))
        LB_M.config(text='o', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("Wingdings", 10, "bold"))

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
keyboard.add_hotkey('win+x', on_windows_x_pressed)


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

#! Github status
from queue import Queue

def check_git_status(git_path, queue):
    if not os.path.exists(git_path):
        queue.put((git_path, "Invalid path"))
        return
    os.chdir(git_path)
    git_status = subprocess.run(["git", "status"], capture_output=True, text=True)
    if "nothing to commit, working tree clean" in git_status.stdout:
        queue.put((git_path, "ü", "#00ff21"))
    else:
        queue.put((git_path, "ü", "#fe1616"))
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

#!? Main ROOT BOX
ROOT1 = tk.Frame(ROOT, bg="#1d2027")
ROOT1.pack(side="right", anchor="ne", pady=(3,2),padx=(3,1))


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
# Constants for bar appearance
BAR_WIDTH = 8
BAR_HEIGHT = 25
# Create a frame to hold the CPU core usage bars and border

BOX_ROW2_ROOT = tk.Frame(ROOT, bg="#1d2027")
BOX_ROW2_ROOT.pack(side="right", anchor="ne", pady=(1,2),padx=(3,1))

cpu_core_frame = tk.Frame(BOX_ROW2_ROOT, bg="#1d2027", highlightthickness=1, highlightbackground="#717d99", relief="solid")
cpu_core_frame.pack(side="right", anchor="nw", padx=0, pady=1)
# Create canvas widgets for CPU core bars
cpu_core_bars = []
for i in range(psutil.cpu_count()):
    frame = tk.Frame(cpu_core_frame, bg="#1d2027")
    frame.pack(side="left", padx=(0, 0), pady=0)
    core_bar = tk.Canvas(frame, bg="#1d2027", width=BAR_WIDTH, height=BAR_HEIGHT, highlightthickness=0)
    core_bar.pack(side="top")
    cpu_core_bars.append(core_bar)
update_cpu_core_bars()


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
    uptime_label.config(text=f"{uptime_str}")
    uptime_label.after(1000, update_uptime_label)  # Update every second
    # Update uptime label periodically
BOX_ROW3_ROOT = tk.Frame(ROOT, bg="#1d2027")
BOX_ROW3_ROOT.pack(side="right", anchor="nw", pady=(5,2),padx=(2,2))
uptime_label = tk.Label(BOX_ROW3_ROOT, text="uptime: 00:00:00", bg="#1d2027", fg="#FFFFFF", height="1", relief="flat", highlightthickness=0, highlightbackground="#1d2027", padx=0, pady=0, font=('JetBrainsMono NF', 10, 'bold'))
uptime_label.pack(side="left", anchor='nw', padx=(0,0), pady=(0,0)) ; update_uptime_label()

def create_label(text, parent, bg, fg, width, height, relief, font, ht, htc, padx, pady, anchor, row, column, rowspan, columnspan, comment=None):
    label = tk.Label(parent, text=text, bg=bg, fg=fg, width=width, height=height, relief=relief, font=font, highlightthickness=ht, highlightbackground=htc)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky=anchor, rowspan=rowspan, columnspan=columnspan)
    label.comment = comment  # Store comment in a property of the label
    return label

label_properties =[
{"comment":"CPU"     ,"text": "CPU"         ,"parent": ROOT1,"bg": "#1d2027","fg": "#ffffff","width": "5","height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 1  ,"rowspan": 1,"columnspan": 1},#! CPU
{"comment":"GPU"     ,"text": "GPU"         ,"parent": ROOT1,"bg": "#1d2027","fg": "#ffffff","width": "5","height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 2  ,"rowspan": 1,"columnspan": 1},#! GPU
{"comment":"RAM"     ,"text": "RAM"         ,"parent": ROOT1,"bg": "#1d2027","fg": "#ffffff","width": "5","height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 3  ,"rowspan": 1,"columnspan": 1},#! RAM
{"comment":"Disk_C"  ,"text": "Disk_C"      ,"parent": ROOT1,"bg": "#1d2027","fg": "#ffffff","width": "5","height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (4 ,2) ,"pady": (0,0),"anchor": "w","row": 1,"column": 4  ,"rowspan": 1,"columnspan": 1},#! Disk_C
{"comment":"Disk_D"  ,"text": "Disk_D"      ,"parent": ROOT1,"bg": "#1d2027","fg": "#ffffff","width": "5","height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (2 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 5  ,"rowspan": 1,"columnspan": 1},#! Disk_D
{"comment":"Upload"  ,"text": "^"           ,"parent": ROOT1,"bg": "#1d2027","fg": "#ffffff","width": "7","height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (3 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 6  ,"rowspan": 1,"columnspan": 1},#! Upload
{"comment":"Download","text": "v"           ,"parent": ROOT1,"bg": "#1d2027","fg": "#ffffff","width": "7","height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (3 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 7  ,"rowspan": 1,"columnspan": 1},#! Download
{"comment":"GitSync" ,"text": "Git"         ,"parent": ROOT1,"bg": "#1d2027","fg": "#009fff","width": 0  ,"height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (10,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 8  ,"rowspan": 1,"columnspan": 1},#! GitSync
{"comment":"GitMs1"  ,"text": "m1"          ,"parent": ROOT1,"bg": "#1d2027","fg": "#FFFFFF","width": 0  ,"height": "0","relief": "flat","font": ("Wingdings"           ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 9  ,"rowspan": 1,"columnspan": 1},#! GitMs1
{"comment":"GitMs2"  ,"text": "m2"          ,"parent": ROOT1,"bg": "#1d2027","fg": "#FFFFFF","width": 0  ,"height": "0","relief": "flat","font": ("Wingdings"           ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,10),"pady": (0,0),"anchor": "w","row": 1,"column": 10 ,"rowspan": 1,"columnspan": 1},#! GitMs2
{"comment":"Keyboard","text": "7"           ,"parent": ROOT1,"bg": "#1d2027","fg": "#FFFFFF","width": 0  ,"height": "0","relief": "flat","font": ("wingdings"           ,10,"normal"),"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 11 ,"rowspan": 1,"columnspan": 1},#! Keyboard
{"comment":"Bar_1"   ,"text": "1"           ,"parent": ROOT1,"bg": "#FFFFFF","fg": "#1d2027","width": 0  ,"height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 12 ,"rowspan": 1,"columnspan": 1},#! Bar_1
{"comment":"Pin"     ,"text": "Pin"         ,"parent": ROOT1,"bg": "#1d2027","fg": "#FFFFFF","width": 0  ,"height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 13 ,"rowspan": 1,"columnspan": 1},#! Pin
{"comment":"Clear"   ,"text": "Clear"       ,"parent": ROOT1,"bg": "#FFFFFF","fg": "#1d2027","width": 0  ,"height": "0","relief": "flat","font": ("JetBrainsMono NF"    ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,10),"pady": (0,0),"anchor": "w","row": 1,"column": 14 ,"rowspan": 1,"columnspan": 1},#! Clear
{"comment":"Reload"  ,"text": "Q"           ,"parent": ROOT1,"bg": "#1d2027","fg": "#26b2f3","width": 0  ,"height": "0","relief": "flat","font": ("wingdings 3"         ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 15 ,"rowspan": 1,"columnspan": 1},#! Reload
{"comment":"Line"    ,"text": "T"           ,"parent": ROOT1,"bg": "#1d2027","fg": "#00FF00","width": 0  ,"height": "0","relief": "flat","font": ("wingdings 3"         ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (3,0),"anchor": "w","row": 1,"column": 16 ,"rowspan": 1,"columnspan": 1},#! Line
{"comment":"Maximize","text": "o"           ,"parent": ROOT1,"bg": "#1d2027","fg": "#26b2f3","width": 0  ,"height": "0","relief": "flat","font": ("wingdings"           ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,0) ,"pady": (0,0),"anchor": "w","row": 1,"column": 17 ,"rowspan": 1,"columnspan": 1},#! Maximize
{"comment":"Close"   ,"text": "r"           ,"parent": ROOT1,"bg": "#1d2027","fg": "#ff0000","width": 0  ,"height": "0","relief": "flat","font": ("Webdings"            ,10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,2) ,"pady": (0,0),"anchor": "w","row": 1,"column": 18 ,"rowspan": 1,"columnspan": 1},#! Close
]
labels = [create_label(**prop) for prop in label_properties]
LB_CPU, LB_GPU, LB_RAM, LB_DUC, LB_DUD, LB_UPLOAD, LB_DWLOAD, bkup, STATUS_MS1, STATUS_MS2, LB_K, LB_1, BT_TOPMOST, CLEAR, LB_R, LB_L, LB_M, LB_XXX = labels

LB_XXX.bind    ("<Button-1>", close_window)
LB_R.bind      ("<Button-1>", restart)
LB_M.bind      ("<Button-1>", lambda event: toggle_window_size('max'))
LB_L.bind      ("<Button-1>", lambda event: toggle_window_size('line'))
BT_TOPMOST.bind("<Button-1>", lambda event: toggle_checking())
CLEAR.bind     ("<Button-1>", lambda event: clear_screen())
LB_1.bind      ("<Button-1>", lambda event: subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\python\\bar_1.py", "-WindowStyle", "Hidden"],shell=True))
LB_K.bind      ("<Button-1>", lambda event: subprocess.Popen(["powershell", "start-process", "C:\\ms1\\shortcut.py", "-WindowStyle", "Hidden"],shell=True))
bkup.bind      ("<Button-1>", lambda event: subprocess.Popen(["Start", "powershell",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle = 'GiTSync' ; C:\\ms1\\scripts\\Github\\ms1u.ps1 ; C:\\ms1\\scripts\\Github\\ms2u.ps1 ; cd ~}"],shell=True))
STATUS_MS1.bind("<Button-1>", lambda event: show_git_changes("C:\\ms1"))
STATUS_MS2.bind("<Button-1>", lambda event: show_git_changes("C:\\ms2"))

queue = Queue()
status_thread = threading.Thread(target=update_status, daemon=True)
gui_thread = threading.Thread(target=update_gui, daemon=True)
status_thread.start()
gui_thread.start()

update_info_labels()
check_window_topmost()


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

BOX_ROW_MAIN = tk.Frame(MAIN_FRAME, bg="#1493df") ; BOX_ROW_MAIN.pack(side="top", anchor="center", pady=(30,0),padx=(0,0), fill="x")
LB_TIME = tk.Label (BOX_ROW_MAIN, bg="#1493df", fg="#000000", width="13", height="1", relief="flat", highlightthickness=4, highlightbackground="#1493df", anchor="center", padx=0, pady=0, font=('JetBrainsMono NF', 18, 'bold'), text="" )
LB_DATE = tk.Label (BOX_ROW_MAIN, bg="#1493df", fg="#000000", width="13", height="1", relief="flat", highlightthickness=4, highlightbackground="#1493df", anchor="center", padx=0, pady=0, font=('JetBrainsMono NF', 14, 'bold'), text="" )
LB_TIME.pack(side="top", anchor='center', padx=(0,0), pady=(0,0))
LB_DATE.pack(side="top", anchor='center', padx=(0,0), pady=(0,0))

update_time()




MAIN_FRAME.pack(expand=True)

#*  ███████╗ ██████╗ ██╗     ██████╗ ███████╗██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#*  ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#*  █████╗  ██║   ██║██║     ██║  ██║█████╗  ██████╔╝    █████╗  ██████╔╝███████║██╔████╔██║█████╗
#*  ██╔══╝  ██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#*  ██║     ╚██████╔╝███████╗██████╔╝███████╗██║  ██║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#*  ╚═╝      ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
#! Folder
icon_folder = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
BT_FOLDER = tk.Button(
MAIN_FRAME,
text="Folder",
command=lambda: subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\folder.py", "-WindowStyle", "Hidden"],shell=True),
image=icon_folder,
compound=tk.LEFT,
bg="#e7d86a",
fg="#1D2027",
height="0",
width="0",
font=("JetBrainsMono NF", 13, "bold"),
anchor="center",
bd=0,
highlightthickness=4,
relief="flat",
activebackground="#000000",
activeforeground="#f6d24a",
cursor="hand2",
)
BT_FOLDER.pack(side="top", padx=(0, 0), pady=(0, 0))

#! App List
icon_applist = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
AppList = tk.Button(
MAIN_FRAME,
text="AppList",
command=lambda: subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\applist.py"],shell=True),
image=icon_applist,
compound=tk.LEFT,
bg="#e7d86a",
fg="#1D2027",
height="0",
width="0",
font=("JetBrainsMono NF", 13, "bold"),
anchor="center",
bd=0,
highlightthickness=4,
relief="flat",
activebackground="#000000",
activeforeground="#f6d24a",
cursor="hand2",
)
AppList.pack(side="top", padx=(0, 0), pady=(0, 0))


#! App Store
icon_appstore = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
AppList = tk.Button(
MAIN_FRAME,
text="AppStore",
command=lambda: subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\app_store.py"],shell=True),
image=icon_appstore,
compound=tk.LEFT,
bg="#e7d86a",
fg="#1D2027",
height="0",
width="0",
font=("JetBrainsMono NF", 13, "bold"),
anchor="center",
bd=0,
highlightthickness=4,
relief="flat",
activebackground="#000000",
activeforeground="#f6d24a",
cursor="hand2",
)
AppList.pack(side="top", padx=(0, 0), pady=(0, 0))

#! FFmpeg
BT_FFMPEG = tk.Button(
MAIN_FRAME,
text="FFmpeg",
command=lambda: switch_to_frame(FR_FFmpeg, MAIN_FRAME),
bg="#009fff",
fg="#FFFFFF",
height=2,
width=30,
font=("JetBrainsMono NF", 13, "bold"),
anchor="w",
bd=0,
highlightthickness=4,
relief="flat",
activebackground="#000000",
activeforeground="#f6d24a",
cursor="hand2",
)
BT_FFMPEG.pack(padx=(0, 0), pady=(0, 0))

FR_FFmpeg = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800)
FR_FFmpeg.pack_propagate(True)

def create_button(text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button,sticky, padx_button, pady_button, padx_pack, pady_pack, command):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack, sticky=sticky)
    return button

BOX_1 = tk.Frame(FR_FFmpeg, bg="#1d2027")
BOX_1.pack(side="top", anchor="center", pady=(30,0), padx=(0,0))

button_properties = [
("FFMPEG",BOX_1,"#98c379","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"), 0 ,1,1,5,"ew" , 0,0, (1,1),(0,0), "none"),
("Trim"           ,BOX_1,"#FFFFFF" ,"#1D2027",1 ,0 ,"flat" ,("JetBrainsMono NF",11 ,"bold"   ),1 ,1,1,1,"ew" ,0,0,(1,1),(0,0),lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\trim.ps1"]     )),
("Convert"        ,BOX_1,"#FFFFFF" ,"#1D2027",1 ,0 ,"flat" ,("JetBrainsMono NF",11 ,"bold"   ),1 ,2,1,1,"ew" ,0,0,(1,1),(0,0),lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\convert.ps1"]  )),
("Dimension"      ,BOX_1,"#FFFFFF" ,"#1D2027",1 ,0 ,"flat" ,("JetBrainsMono NF",11 ,"bold"   ),1 ,3,1,1,"ew" ,0,0,(1,1),(0,0),lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\dimension.ps1"])),
("Imagedimension" ,BOX_1,"#FFFFFF" ,"#1D2027",1 ,0 ,"flat" ,("JetBrainsMono NF",11 ,"bold"   ),1 ,4,1,1,"ew" ,0,0,(1,1),(0,0),lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\imgdim.ps1"]   )),
("Merge"          ,BOX_1,"#FFFFFF" ,"#1D2027",1 ,0 ,"flat" ,("JetBrainsMono NF",11 ,"bold"   ),1 ,5,1,1,"ew" ,0,0,(1,1),(0,0),lambda:subprocess.Popen(["powershell" ,"start","C:\\ms1\\scripts\\ffmpeg\\merge.ps1"]    )),
]

for button_props in button_properties:
    create_button(*button_props)


#!  ██████╗ ██████╗  ██████╗  ██████╗███████╗███████╗███████╗       ██╗       ██████╗ ██╗  ██╗ ██████╗
#!  ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔════╝       ██║       ██╔══██╗██║ ██╔╝██╔════╝
#!  ██████╔╝██████╔╝██║   ██║██║     █████╗  ███████╗███████╗    ████████╗    ██████╔╝█████╔╝ ██║  ███╗
#!  ██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝  ╚════██║╚════██║    ██╔═██╔═╝    ██╔═══╝ ██╔═██╗ ██║   ██║
#!  ██║     ██║  ██║╚██████╔╝╚██████╗███████╗███████║███████║    ██████║      ██║     ██║  ██╗╚██████╔╝
#!  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝    ╚═════╝      ╚═╝     ╚═╝  ╚═╝ ╚═════╝

#! FRAME Function

BT_PROCESS = tk.Button(
MAIN_FRAME,
text="Process & PKG & FFMPEG & FIND",
command=lambda: switch_to_frame(FR_PROCESS, MAIN_FRAME),
bg="#009fff",
fg="#FFFFFF",
height=2,
width=30,
font=("JetBrainsMono NF", 13, "bold"),
anchor="w",
bd=0,
highlightthickness=4,
relief="flat",
activebackground="#000000",
activeforeground="#f6d24a",
cursor="hand2",
)
BT_PROCESS.pack(padx=(0, 0), pady=(0, 0))

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



def create_button(text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button,sticky, padx_button, pady_button, padx_pack, pady_pack, command):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack, sticky=sticky)
    return button

BOX_find = tk.Frame(FR_PROCESS, bg="#1d2027")
BOX_find.pack(side="top", anchor="center", pady=(20,0), padx=(0,0))

button_properties = [
("Find",BOX_find,"#79828b","#1D2027",1,0,"flat",("JetBrainsMono NF",11,"bold"),0 ,1,1,5,"ew" ,0 ,0,(1,1),(0,0),"none"),
("File"    ,BOX_find ,"#FFFFFF","#1D2027",1 ,0 ,"flat",("JetBrainsMono NF",11,"bold"),1 ,1,1 ,1 ,"ew" ,0 ,0,(1,1),(0,0),lambda: subprocess.Popen(["start" ,"C:\\ms1\\scripts\\find\\find_file.ps1"]   ,shell=True)),
("Pattern" ,BOX_find ,"#FFFFFF","#1D2027",1 ,0 ,"flat",("JetBrainsMono NF",11,"bold"),1 ,2,1 ,1 ,"ew" ,0 ,0,(1,1),(0,0),lambda: subprocess.Popen(["start" ,"C:\\ms1\\scripts\\find\\find_pattern.ps1"],shell=True)),
("Size"    ,BOX_find ,"#FFFFFF","#1D2027",1 ,0 ,"flat",("JetBrainsMono NF",11,"bold"),1 ,3,1 ,1 ,"ew" ,0 ,0,(1,1),(0,0),lambda: subprocess.Popen(["start" ,"C:\\ms1\\scripts\\find\\find_size.ps1"]   ,shell=True)),

("FZF-->C:\\" ,BOX_find ,"#FFFFFF","#1D2027",1 ,0 ,"flat",("JetBrainsMono NF",11 ,"bold") ,2 ,1,1,1,"ew" ,0 ,0,(1,1),(0 ,0),lambda:subprocess.Popen(["powershell", "-Command", 'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; fzf --preview=\'highlight -O ansi -l {}\'"'], shell=True)),
("FZF-->D:\\" ,BOX_find ,"#FFFFFF","#1D2027",1 ,0 ,"flat",("JetBrainsMono NF",11 ,"bold") ,2 ,2,1,1,"ew" ,0 ,0,(1,1),(0 ,0),lambda:subprocess.Popen(["powershell", "-Command", 'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; fzf --preview=\'bat {}\'"'], shell=True) ),

("ACK-->C:\\" ,BOX_find ,"#FFFFFF","#1D2027",1 ,0 ,"flat",("JetBrainsMono NF",11 ,"bold") ,3 ,1,1,1,"ew" ,0 ,0,(1,1),(0 ,0),lambda: subprocess.Popen(["powershell", "-Command", f'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; ack {insert_input()}"'], shell=True)),
("ACK-->D:\\" ,BOX_find ,"#FFFFFF","#1D2027",1 ,0 ,"flat",("JetBrainsMono NF",11 ,"bold") ,3 ,2,1,1,"ew" ,0 ,0,(1,1),(0 ,0),lambda: subprocess.Popen(["powershell", "-Command", f'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; ack {insert_input()}"'], shell=True)),

]

for button_props in button_properties:
    create_button(*button_props)

#*  ████████╗ ██████╗  ██████╗ ██╗     ███████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#*  ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#*     ██║   ██║   ██║██║   ██║██║     ███████╗    █████╗  ██████╔╝███████║██╔████╔██║█████╗
#*     ██║   ██║   ██║██║   ██║██║     ╚════██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#*     ██║   ╚██████╔╝╚██████╔╝███████╗███████║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#*     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

BT_TOOLS = tk.Button(
MAIN_FRAME,
text="TOOLS",
command=lambda: switch_to_frame(FRAME_TOOLS, MAIN_FRAME),
bg="#454545",
fg="#FFFFFF",
height=2,
width=30,
font=("JetBrainsMono NF", 13, "bold"),
anchor="w",
bd=0,
highlightthickness=4,
relief="flat",
activebackground="#000000",
activeforeground="#f6d24a",
cursor="hand2",
)
BT_TOOLS.pack(padx=(0, 0), pady=(0, 0))

FRAME_TOOLS = tk.Frame(BORDER_FRAME, bg="#1D2027", width=520, height=800)
FRAME_TOOLS.pack_propagate(True)

BT_BACK = tk.Button(FRAME_TOOLS, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FRAME_TOOLS), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))

def create_button(text, bg_color, fg_color, height, width, relief, font, padx_button, pady_button, x_button, y_button, anchor_button, command):
    button = tk.Button(BOX_1, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command, anchor=anchor_button)
    button.place(x=x_button, y=y_button)
    return button

BOX_1 = tk.Frame(FRAME_TOOLS, bg="#1d2027",width=520, height=720)
BOX_1.pack(side="top", anchor="center", pady=(80,0), padx=(0,0))

button_properties = [
("Advanced Adapter"        ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,10 ,"w" ,lambda: subprocess.Popen ("control ncpa.cpl")),
("CheckDisk"               ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,40 ,"w" ,lambda: subprocess.Popen (["powershell", "Start-Process", "-FilePath", "chkdsk","-ArgumentList", '"/f /r"', "-Verb", "RunAs"],shell=True)),
("Chris Titus Win Utility" ,"#000000","#FFFFFF",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,70 ,"w" ,lambda: subprocess.Popen (["powershell","Invoke-RestMethod christitus.com/win | Invoke-Expression"],shell=True)),
("Disk Cleanup"            ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,100,"w" ,lambda: subprocess.Popen (["powershell", "Start-Process","-FilePath","cleanmgr","-Verb", "RunAs"],shell=True)),
("DISM"                    ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,130,"w" ,lambda: subprocess.Popen (["powershell","Start-Process","-FilePath","cmd","-ArgumentList",'"/k DISM /Online /Cleanup-Image /RestoreHealth"',"-Verb", "RunAs"],shell=True)),
("DxDiag"                  ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,160,"w" ,lambda: subprocess.Popen ("dxdiag")),
("Flush DNS"               ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,190,"w" ,lambda: subprocess.Popen (["powershell", "Start-Process", "-FilePath","cmd","-ArgumentList",'"/k ipconfig /flushdns"', "-Verb", "RunAs"],shell=True                     )),
("msconfig"                ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,220,"w" ,lambda: subprocess.Popen (["msconfig.exe"],shell=True)),
("Netplwiz"                ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,250,"w" ,lambda: subprocess.Popen (["netplwiz.exe"],shell=True)),
("Power Plan"              ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,280,"w" ,lambda: subprocess.Popen (["powercfg.cpl"],shell=True)),
("SFC"                     ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,310,"w" ,lambda: subprocess.Popen (["powershell", "Start-Process", "-FilePath", "cmd","-ArgumentList",'"/k sfc /scannow"', "-Verb", "RunAs"],shell=True)),
("Sniping Tool"            ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,340,"w" ,lambda: subprocess.Popen ("SnippingTool.exe")),
("Systeminfo"              ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,370,"w" ,lambda: subprocess.Popen (["powershell", "Start-Process", "cmd","-ArgumentList",'"/k systeminfo"'],shell=True)),
("UAC"                     ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,400,"w" ,lambda: subprocess.Popen ("UserAccountControlSettings.exe")),
("Turn on Windows Features","#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,430,"w" ,lambda: subprocess.Popen (["optionalfeatures"],shell=True)),
("Winsock Reset"           ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,460,"w" ,lambda: subprocess.Popen (["powershell", "Start-Process", "-FilePath", "cmd","-ArgumentList",'"/k netsh winsock reset"' ,"-Verb", "RunAs"],shell=True)),
("Character Map"           ,"#FFFFFF","#1D2027",1,25,"solid",("jetbrainsmono nf",14,"bold"),0,0,100,490,"w" ,lambda: subprocess.Popen ("charmap")),
]
for button_props in button_properties:
    create_button(*button_props)


#?  ███████╗ ██████╗██████╗ ██╗██████╗ ████████╗    ██╗     ██╗███████╗████████╗
#?  ██╔════╝██╔════╝██╔══██╗██║██╔══██╗╚══██╔══╝    ██║     ██║██╔════╝╚══██╔══╝
#?  ███████╗██║     ██████╔╝██║██████╔╝   ██║       ██║     ██║███████╗   ██║   
#?  ╚════██║██║     ██╔══██╗██║██╔═══╝    ██║       ██║     ██║╚════██║   ██║   
#?  ███████║╚██████╗██║  ██║██║██║        ██║       ███████╗██║███████║   ██║   
#?  ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝       ╚══════╝╚═╝╚══════╝   ╚═╝   

BT_Script_list = tk.Button(
                                MAIN_FRAME,
                                text="Script List",
                                command=lambda: switch_to_frame(FR_PYTHON_TOOL, MAIN_FRAME),
                                bg="#00a600",
                                fg="#000000",
                                height=2,
                                width=30,
                                font=("JetBrainsMono NF", 13, "bold"),
                                anchor="w",
                                bd=0,
                                highlightthickness=4,
                                relief="flat",
                                activebackground="#000000",
                                activeforeground="#f6d24a",
                                cursor="hand2",
                                )
BT_Script_list.pack(padx=(0, 0), pady=(0, 0))

FR_PYTHON_TOOL = tk.Frame(BORDER_FRAME, bg="#1d2027", width=520, height=800)
FR_PYTHON_TOOL.pack_propagate(False)

BT_BACK = tk.Button(FR_PYTHON_TOOL, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_PYTHON_TOOL), bg="#FFFFFF", fg="#000", height=1, width=5, relief="flat", padx=0, font=("calibri", 10, "bold"))
BT_BACK.pack(side="bottom", anchor="center", padx=(0,5), pady=(0,30))

BOX_1 = tk.Frame(FR_PYTHON_TOOL, bg="#1d2027")
BOX_1.pack(side="top", anchor="center", pady=(80,0), padx=(0,0))

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

# Dropdown for folders
folder_var = tk.StringVar(BOX_1)
folder_var.set("Select a folder")
folder_dropdown = tk.OptionMenu(BOX_1, folder_var, *folders, command=folder_selected)

folder_dropdown.configure(width=30, background="#ddf581", foreground="black", font=("JetBrainsMono NF", 10))
folder_dropdown.config(indicatoron=False)

# Dropdown for scripts
script_var = tk.StringVar(BOX_1)
script_var.set("Select a script")
script_dropdown = tk.OptionMenu(BOX_1, script_var, "Select a script")
script_dropdown.configure(width=30, background="#ddf581", foreground="black", font=("JetBrainsMono NF", 10))
script_dropdown.config(indicatoron=False)

run_button = tk.Button(BOX_1, text="Run", command=run_script, bg="#41abff", font=("JetBrainsMono NF", 12))

folder_dropdown.grid(row=0, column=1, rowspan=1, padx=5, pady=10)
script_dropdown.grid(row=1, column=1, rowspan=1, padx=5, pady=10)
run_button.grid(row=0, column=2, rowspan=2, padx=5, pady=10, sticky="nsew") #! nwse means full filling up down left right spaces so if ns means fullfill up and down portion



#! ██████╗ ███████╗███████╗████████╗ █████╗ ██████╗ ████████╗       ██╗       ███████╗██╗  ██╗██╗   ██╗████████╗██████╗  ██████╗ ██╗    ██╗███╗   ██╗
#! ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝       ██║       ██╔════╝██║  ██║██║   ██║╚══██╔══╝██╔══██╗██╔═══██╗██║    ██║████╗  ██║
#! ██████╔╝█████╗  ███████╗   ██║   ███████║██████╔╝   ██║       ████████╗    ███████╗███████║██║   ██║   ██║   ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
#! ██╔══██╗██╔══╝  ╚════██║   ██║   ██╔══██║██╔══██╗   ██║       ██╔═██╔═╝    ╚════██║██╔══██║██║   ██║   ██║   ██║  ██║██║   ██║██║███╗██║██║╚██╗██║
#! ██║  ██║███████╗███████║   ██║   ██║  ██║██║  ██║   ██║       ██████║      ███████║██║  ██║╚██████╔╝   ██║   ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
#! ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═════╝      ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝

BOX_1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
BOX_1.pack(pady=(5,0))

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

shutdown_window =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\shutdown3.png"))
restart_window  =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\reboot-50x50.png"))
update_image    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\inkspace\\update.png"))
backup_image    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\inkspace\\backup-50x50.png"))
rclone_c        =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\inkspace\\rclone_c.png"))
rclone_d        =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\inkspace\\rclone_d.png"))


def create_button(parent, text="", image=None, compound=None, command=None, height=50, width=50, bg="#1d2027", fg="#ffffff", bd=0, relief="flat", highlightthickness=4, activebackground="#000000", activeforeground="#FFFFFF", row=0, column=0, rowspan=1, columnspan=1):
    button = tk.Button(parent, text=text, image=image, compound=compound, command=command, height=height, width=width, bg=bg, fg=fg, bd=bd, relief=relief, highlightthickness=highlightthickness, activebackground=activebackground, activeforeground=activeforeground)
    button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="w", padx=(0,0), pady=0)
    return button

# Button Properties
button_properties = [
{"parent": BOX_1,"image": shutdown_window,"compound": tk.TOP,"text": "","command": force_shutdown,"row": 1,"column": 1,"rowspan":1,"columnspan":1},
{"parent": BOX_1,"image": restart_window ,"compound": tk.TOP,"text": "","command": force_restart ,"row": 1,"column": 2,"rowspan":1,"columnspan":1},
{"parent": BOX_1,"image": backup_image   ,"compound": tk.TOP,"text": "","command": open_backup   ,"row": 1,"column": 3,"rowspan":1,"columnspan":1},
{"parent": BOX_1,"image": update_image   ,"compound": tk.TOP,"text": "","command": open_update   ,"row": 1,"column": 4,"rowspan":1,"columnspan":1},
{"parent": BOX_1,"image": rclone_c       ,"compound": tk.TOP,"text": "","command": c_size        ,"row": 1,"column": 5,"rowspan":1,"columnspan":1},
{"parent": BOX_1,"image": rclone_d       ,"compound": tk.TOP,"text": "","command": d_size        ,"row": 1,"column": 6,"rowspan":1,"columnspan":1},
]

# Create Buttons
buttons = [create_button(**prop) for prop in button_properties]















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