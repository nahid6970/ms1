import tkinter as tk
import subprocess
from time import strftime
from datetime import datetime
from tkinter import ttk
import ctypes

import os
import shutil
from PIL import Image, ImageTk
from tkinter import PhotoImage

from tkinter import messagebox
import time

import psutil
import threading

# For Shortcuts
import pyautogui

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
    BORDER_FRAME = tk.Frame(parent, bg="red", bd=2)
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
ROOT.attributes('-topmost', True)  # Set always on top
ROOT.geometry("400x700")
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

#! alt 1 (original)
# # Calculate the screen width and height
# screen_width = ROOT.winfo_screenwidth()
# screen_height = ROOT.winfo_screenheight()
# # Calculate the x and y coordinates to center the window
# x = (screen_width - 500) // 1  # 400 is the width of your window higher means left side lower means right side
# y = (screen_height - 755) // 2  # 700 is the height of your window higher means top side lower means bottom side
# # Set the geometry of the window
# ROOT.geometry(f"500x700+{x}+{y}") #! overall size of the window

#! alt 2 (modified)
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()
# Calculate the x and y coordinates to center the window
x_coordinate = 1420
y_coordinate = 162
ROOT.geometry(f"500x700+{x_coordinate}+{y_coordinate}") # Overall size of the window


# Create main frame
MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=500, height=700) #! this is to adjust the border for main frame #make it bigger so no problem with  # smaller will cause smaller border  # have to do it for every frame
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1)  # Add some padding at the top


#?  ██████╗  ██████╗  ██████╗ ████████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#?  ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#?  ██████╔╝██║   ██║██║   ██║   ██║       █████╗  ██████╔╝███████║██╔████╔██║█████╗
#?  ██╔══██╗██║   ██║██║   ██║   ██║       ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#?  ██║  ██║╚██████╔╝╚██████╔╝   ██║       ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#?  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
#* Close Button
def close_window(event=None):
    ROOT.destroy()

BOX_ROW_ROOT = tk.Frame(ROOT, bg="#1d2027") ; BOX_ROW_ROOT.pack(side="top", anchor="e", pady=(7,0),padx=(5,3))
LB_XXX = tk.Label  (BOX_ROW_ROOT, bg="#E81123", fg="#FFFFFF", width=" 2", height="1", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", text="X", font= ("AGENCY", 10, "bold")) ; LB_XXX.pack     (side="right", anchor="e", padx=(0,3), pady=(0,0)) ; LB_XXX.bind("<Button-1>", close_window)

#! Resize Window
def toggle_window_size(size):
    global window_state
    if size == 'S':
        ROOT.geometry('112x38')
        ROOT.configure(bg='red')
        LB_S.config(text='S', bg="#1fb9ff", fg="#000000", height=1, width=2, font=("agency", 10, "bold"))
        LB_M.config(text='M', bg="#0000ff", fg="#ffffff", height=1, width=2, font=("agency", 10, "bold"))
        LB_L.config(text='L', bg="#0000ff", fg="#ffffff", height=1, width=2, font=("agency", 10, "bold"))
        window_state = 'small'
        x_coordinate, y_coordinate = 1308, 1038
        # x_coordinate, y_coordinate = 1590, 0
    elif size == 'M':
        ROOT.geometry('500x38')
        ROOT.configure(bg='red')
        LB_S.config(text='S', bg="#0000ff", fg="#ffffff", height=1, width=2, font=("agency", 10, "bold"))
        LB_M.config(text='M', bg="#1fb9ff", fg="#000000", height=1, width=2, font=("agency", 10, "bold"))
        LB_L.config(text='L', bg="#0000ff", fg="#ffffff", height=1, width=2, font=("agency", 10, "bold"))
        window_state = 'medium'
        x_coordinate, y_coordinate = 920, 1038
        # x_coordinate, y_coordinate = 1180, 0
    elif size == 'L':
        ROOT.geometry('500x700')
        ROOT.configure(bg='#1d2027')
        LB_S.config(text='S', bg="#0000ff", fg="#ffffff", height=1, width=2, font=("agency", 10, "bold"))
        LB_M.config(text='M', bg="#0000ff", fg="#ffffff", height=1, width=2, font=("agency", 10, "bold"))
        LB_L.config(text='L', bg="#1fb9ff", fg="#000000", height=1, width=2, font=("agency", 10, "bold"))
        window_state = 'large'
        x_coordinate, y_coordinate = 1420, 162
        # x_coordinate, y_coordinate = 1180, 0
    
    ROOT.focus_force()  
    ROOT.update_idletasks()  
    ROOT.geometry(f'{ROOT.winfo_width()}x{ROOT.winfo_height()}+{x_coordinate}+{y_coordinate}') 

LB_S = tk.Label(BOX_ROW_ROOT, bg="#0000FF", fg="#FFFFFF", width=" 2", height="1", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", text="S", font=("AGENCY", 10, "bold")) ; LB_S.pack(side="right", anchor="e", padx=(0,3), pady=(0,0)) ; LB_S.bind("<Button-1>", lambda event: toggle_window_size('S'))
LB_M = tk.Label(BOX_ROW_ROOT, bg="#0000FF", fg="#FFFFFF", width=" 2", height="1", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", text="M", font=("AGENCY", 10, "bold")) ; LB_M.pack(side="right", anchor="e", padx=(0,3), pady=(0,0)) ; LB_M.bind("<Button-1>", lambda event: toggle_window_size('M'))
LB_L = tk.Label(BOX_ROW_ROOT, bg="#0000FF", fg="#FFFFFF", width=" 2", height="1", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", text="L", font=("AGENCY", 10, "bold")) ; LB_L.pack(side="right", anchor="e", padx=(0,3), pady=(0,0)) ; LB_L.bind("<Button-1>", lambda event: toggle_window_size('L'))
window_state = 'normal'

#* CPU / RAM / DRIVES / NET SPEED
def get_cpu_ram_info():
    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = psutil.virtual_memory().percent
    return cpu_usage, ram_usage
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
    disk_c_usage, disk_d_usage = get_disk_info()
    upload_speed, download_speed = get_net_speed()
    
    LB_CPU['text'] = f'{cpu_usage}%'
    LB_RAM['text'] = f'{ram_usage}%'
    LB_DUC['text'] = f'{disk_c_usage}%'
    LB_DUD['text'] = f'{disk_d_usage}%'
    LB_UPLOAD['text'] = f' ▲ {upload_speed} '
    LB_DWLOAD['text'] = f' ▼ {download_speed} '
    
    # Set background color based on upload speed
    if upload_speed == "0":
        LB_UPLOAD.config(bg='#FFFFFF', fg="#000000")
    elif float(upload_speed) < 0.1:  # Less than 100 KB
        LB_UPLOAD.config(bg='#99FF99', fg="#000000")
    elif 0.1 <= float(upload_speed) < 0.5:  # 100 KB to 499 KB
        LB_UPLOAD.config(bg='#19FF19', fg="#000000")
    elif 0.5 <= float(upload_speed) < 1:  # 500 KB to 1 MB
        LB_UPLOAD.config(bg='#006400', fg='#FFFFFF')  # Normal green
    else:
        LB_UPLOAD.config(bg='#0053d6', fg='#FFFFFF')  # Dark green
        
    # Set background color based on download speed
    if download_speed == "0":
        LB_DWLOAD.config(bg='#FFFFFF' , fg="#000000")
    elif float(download_speed) < 0.1:  # Less than 100 KB
        LB_DWLOAD.config(bg='#99FF99', fg="#000000")
    elif 0.1 <= float(download_speed) < 0.5:  # 100 KB to 499 KB
        LB_DWLOAD.config(bg='#4CFF4C', fg="#000000")
    elif 0.5 <= float(download_speed) < 1:  # 500 KB to 1 MB
        LB_DWLOAD.config(bg='#006400', fg='#FFFFFF')  # Normal green
    else:
        LB_DWLOAD.config(bg='#0053d6', fg='#FFFFFF')  # Dark green
    
    # Change background and foreground color based on usage thresholds
    LB_RAM.config(bg='red' if ram_usage > 80 else '#ff7500', fg='white' if ram_usage > 80 else '#000000')
    LB_CPU.config(bg='red' if cpu_usage > 85 else '#76ACFA', fg='white' if cpu_usage > 80 else '#000000')
    LB_DUC.config(bg='red' if disk_c_usage > 90 else '#aaabad', fg='white' if disk_c_usage > 90 else '#000000')
    LB_DUD.config(bg='red' if disk_d_usage > 90 else '#aaabad', fg='white' if disk_d_usage > 90 else '#000000')
    
    ROOT.after(1000, update_info_labels)

# Initialize static variables for network speed calculation
get_net_speed.upload_speed_last = 0
get_net_speed.download_speed_last = 0

LB_UPLOAD = tk.Label(BOX_ROW_ROOT, width="5", height="1", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", text="▲", font=("agency", 10, "bold")) ; LB_UPLOAD.pack(side="right", anchor="e", padx=(0,3), pady=(0,0))
LB_DWLOAD = tk.Label(BOX_ROW_ROOT, width="5", height="1", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", text="▼", font=("agency", 10, "bold")) ; LB_DWLOAD.pack(side="right", anchor="e", padx=(0,3), pady=(0,0))
LB_DUD = tk.Label  (BOX_ROW_ROOT, width=" 6", height="1", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", text=" ", font= ("agency", 10, "bold")) ; LB_DUD.pack     (side="right", anchor="e", padx=(0,3), pady=(0,0))
LB_DUC = tk.Label  (BOX_ROW_ROOT, width=" 6", height="1", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", text=" ", font= ("agency", 10, "bold")) ; LB_DUC.pack     (side="right", anchor="e", padx=(0,3), pady=(0,0))
LB_RAM = tk.Label  (BOX_ROW_ROOT, width=" 6", height="1", relief="flat", highlightthickness=1, highlightbackground="#ff7500", text=" ", font= ("agency", 10, "bold")) ; LB_RAM.pack     (side="right", anchor="e", padx=(0,3), pady=(0,0))
LB_CPU = tk.Label  (BOX_ROW_ROOT, width=" 5", height="1", relief="flat", highlightthickness=1, highlightbackground="#76acfa", text=" ", font= ("agency", 10, "bold")) ; LB_CPU.pack     (side="right", anchor="e", padx=(0,3), pady=(0,0))
update_info_labels()

def check_git_status(git_path, status_label):
    if not os.path.exists(git_path):
        status_label.config(text="Invalid path")
        return
    os.chdir(git_path)
    git_status = subprocess.run(["git", "status"], capture_output=True, text=True)
    if "nothing to commit, working tree clean" in git_status.stdout:
        status_label.config(fg="#00ff21")
    else:
        status_label.config(fg="#fe1616")

def show_git_changes(git_path):
    if not os.path.exists(git_path):
        print("Invalid path")
        return
    os.chdir(git_path)
    subprocess.Popen(["git", "status"])
    os.system("start cmd /k exit")

def update_status():
    while True:
        check_git_status("D:\@git\\ms1", STATUS_MS1)
        check_git_status("D:\@git\\ms2", STATUS_MS2)
        # Update the status every second
        time.sleep(1)

STATUS_MS1 = tk.Label(BOX_ROW_ROOT, bg="#000000", width=" 2", height="1", relief="flat", highlightthickness=1, highlightbackground="#76acfa", text="m1", font= ("agency", 10, "bold"))
STATUS_MS1.bind("<Button-1>", lambda event: show_git_changes("D:\@git\\ms1"))
STATUS_MS1.pack(side="left", anchor="e", padx=(0,3), pady=(0,0))

STATUS_MS2 = tk.Label(BOX_ROW_ROOT, bg="#000000", width=" 2", height="1", relief="flat", highlightthickness=1, highlightbackground="#76acfa", text="m2", font= ("agency", 10, "bold"))
STATUS_MS2.bind("<Button-1>", lambda event: show_git_changes("D:\@git\\ms2"))
STATUS_MS2.pack(side="left", anchor="e", padx=(0,3), pady=(0,0))

# Create label to display git path and status for ms1 project
#path_label2 = tk.Label(BOX_ROW_ROOT, text="ms2") ; path_label2.pack(pady=(10, 0))
#path_label1 = tk.Label(BOX_ROW_ROOT, text="ms1") ; path_label1.pack(pady=(10, 0))

# Start a separate thread for updating the status
status_thread = threading.Thread(target=update_status, daemon=True)
status_thread.start()

#! Clear Button
def clear_screen():
    try:
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        ascii_art = """
  ██████╗██╗     ███████╗ █████╗ ██████╗ ███████╗██████╗ 
 ██╔════╝██║     ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔══██╗
 ██║     ██║     █████╗  ███████║██████╔╝█████╗  ██║  ██║
 ██║     ██║     ██╔══╝  ██╔══██║██╔══██╗██╔══╝  ██║  ██║
 ╚██████╗███████╗███████╗██║  ██║██║  ██║███████╗██████╔╝
  ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═════╝ 
        """
        print(ascii_art)
    except Exception as e:
        print(f"Error clearing screen: {e}")

BT_CLR = tk.Button(ROOT, text="❌", command=clear_screen , fg="white" , bg="#1d2027" , width=4, height=1 ,relief="flat", font=("times", 12, "bold"))
BT_CLR.pack( side="bottom", anchor="n", pady=(0,25), padx=(0,0))


#?  ███╗   ███╗ █████╗ ██╗███╗   ██╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#?  ████╗ ████║██╔══██╗██║████╗  ██║    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#?  ██╔████╔██║███████║██║██╔██╗ ██║    █████╗  ██████╔╝███████║██╔████╔██║█████╗  
#?  ██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝  
#?  ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#?  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

#! Terminal & SYNC & Ruler
def open_sync(event=None):
    subprocess.Popen(["powershell", "start", "D:\@git\\ms1\\sync.ps1"])

def open_terminal(even=None):
    subprocess.Popen(["wt"])

def shortcut_scaleruler(event=None):
    pyautogui.hotkey('win', 'shift', 'm')

def shortcut_TextExtract(event=None):
    pyautogui.hotkey('win', 'shift', 't')

def python_regedit_run(event=None):
    subprocess.Popen(["powershell", "-Command", "Start-Process", "-FilePath", "python", "-ArgumentList", "D:\@git\\ms1\\scripts\\regedit.py", "-Verb", "RunAs"], shell=True)

def python_screenshot(event=None):
    subprocess.Popen(["powershell", "Start", "D:\@git\\ms1\\scripts\\screenshot.py"], shell=True)

BOX_ROW_MAIN = tk.Frame(MAIN_FRAME, bg="#1d2027") ; BOX_ROW_MAIN.pack(side="top", anchor="e", pady=(4,3),padx=(0,3))
LB_SCRSHOT = tk.Label (BOX_ROW_MAIN, bg="#000000", fg="#FFFFFF", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", padx=0, pady=0, font=("AGENCY", 11, "bold"), text="C") ; LB_SCRSHOT.pack(side="left", anchor='e', padx=(0,3), pady=(28,0)) ; LB_SCRSHOT.bind("<Button-1>", python_screenshot)
LB_RULERSR = tk.Label (BOX_ROW_MAIN, bg="#ff6600", fg="#000000", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", padx=0, pady=0, font=("AGENCY", 11, "bold"), text="R") ; LB_RULERSR.pack(side="left", anchor='e', padx=(0,3), pady=(28,0)) ; LB_RULERSR.bind("<Button-1>", shortcut_scaleruler)
LB_TEXTCPP = tk.Label (BOX_ROW_MAIN, bg="#ff6600", fg="#000000", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", padx=0, pady=0, font=("AGENCY", 11, "bold"), text="TE") ; LB_TEXTCPP.pack(side="left", anchor='e', padx=(0,3), pady=(28,0)) ; LB_TEXTCPP.bind("<Button-1>", shortcut_TextExtract)
LB_REGEDIT = tk.Label (BOX_ROW_MAIN, bg="#52d3ff", fg="#000000", height="1", width="3", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", padx=0, pady=0, font=("AGENCY", 11, "bold"), text="RE") ; LB_REGEDIT.pack(side="left", anchor='e', padx=(0,3), pady=(28,0)) ; LB_REGEDIT.bind("<Button-1>", python_regedit_run)
LB_SYNCCCC = tk.Label (BOX_ROW_MAIN, bg="#21a366", fg="#FFFFFF", height="1", width="2", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", padx=0, pady=0, font=("AGENCY", 11, "bold"), text="S") ; LB_SYNCCCC.pack(side="left", anchor='e', padx=(0,3), pady=(28,0)) ; LB_SYNCCCC.bind("<Button-1>", open_sync)
LB_TERMINL = tk.Label (BOX_ROW_MAIN, bg="#000000", fg="#FFFFFF", height="1", width="2", relief="flat", highlightthickness=1, highlightbackground="#FFFFFF", padx=0, pady=0, font=("AGENCY", 11, "bold"), text="T") ; LB_TERMINL.pack(side="left", anchor='e', padx=(0,1), pady=(28,0)) ; LB_TERMINL.bind("<Button-1>", open_terminal)


#! Time & Date
def update_time():
    current_time = strftime('%I:%M:%S')  # Format time in 12-hour format # %p is for am/pm
    LB_TIME['text'] = current_time
    current_date = datetime.now().strftime('%d %b %Y')  # Format date as '03 May 2023'
    LB_DATE['text'] = current_date
    ROOT.after(1000, update_time)  # Update time every 1000 milliseconds (1 second)

BOX_ROW_MAIN = tk.Frame(MAIN_FRAME, bg="#1d2027")
BOX_ROW_MAIN.pack(side="top", anchor="center", pady=(1,3),padx=(0,0))
LB_TIME = tk.Label (BOX_ROW_MAIN, bg="#1d2027", fg="#FFFFFF", width="13", height="2", relief="flat", highlightthickness=4, highlightbackground="#FFFFFF", padx=0, pady=0, font=('terminess nerd font', 16, 'bold'), text="" ) ; LB_TIME.pack(side="left", anchor='ne', padx=(0,0), pady=(0,0))
LB_DATE = tk.Label (BOX_ROW_MAIN, bg="#1d2027", fg="#FFFFFF", width="13", height="2", relief="flat", highlightthickness=4, highlightbackground="#FFFFFF", padx=0, pady=0, font=('terminess nerd font', 16, 'bold'), text="" ) ; LB_DATE.pack(side="left", anchor='ne', padx=(0,0), pady=(0,0))
update_time()  # Initial call to display time


#! Backup & Update
def open_backup():
    subprocess.Popen(["powershell", "start", "D:\@git\\ms1\\backup.ps1"], shell=True)
    
def open_update():
    subprocess.Popen(["powershell", "start", "D:\@git\\ms1\\update.ps1"],  shell=True)

BOX_ROW_MAIN = tk.Frame(MAIN_FRAME, bg="black") ; BOX_ROW_MAIN.pack(pady=2)
BT_BACKUP_MAIN_FRAME = tk.Button(BOX_ROW_MAIN, bg="#21a366", fg="#ffffff", height=1, width=12, relief="flat", highlightthickness=3, padx=5, pady=0, font=("terminess nerd font", 16, "bold"), command=open_backup, text="Backup") ; BT_BACKUP_MAIN_FRAME.pack(side="left", anchor="center", padx=(0,1), pady=0,)
BT_UPDATE_MAIN_FRAME = tk.Button(BOX_ROW_MAIN, bg="#0047ab", fg="#ffffff", height=1, width=12, relief="flat", highlightthickness=3, padx=5, pady=0, font=("terminess nerd font", 16, "bold"), command=open_update, text="Update") ; BT_UPDATE_MAIN_FRAME.pack(side="left", anchor="center", padx=(1,0), pady=0,)


#! Drive size analyze using rclone
def c_size():
    subprocess.run(["powershell", "Start-Process rclone -ArgumentList 'ncdu c:\\' "])

def d_size():
    subprocess.run(["powershell", "Start-Process rclone -ArgumentList 'ncdu d:\\' "])

BOX_ROW_MAIN = tk.Frame(MAIN_FRAME, bg="black") ; BOX_ROW_MAIN.pack(pady=2)
BT_NCDU_C_MAIN_FRAME = tk.Button(BOX_ROW_MAIN, bg="#57a9f4", fg="#000000", height=1, width=12, relief="flat", highlightthickness=3, padx=5, font=("terminess nerd font", 16, "bold"), command=c_size, text="C:\\ Drive", ) ; BT_NCDU_C_MAIN_FRAME.pack(side="left", padx=(0,1), pady=0)
BT_NCDU_D_MAIN_FRAME = tk.Button(BOX_ROW_MAIN, bg="#57a9f4", fg="#000000", height=1, width=12, relief="flat", highlightthickness=3, padx=5, font=("terminess nerd font", 16, "bold"), command=d_size, text="D:\\ Drive", ) ; BT_NCDU_D_MAIN_FRAME.pack(side="left", padx=(1,0), pady=0)

MAIN_FRAME.pack(expand=True)


#  ███████╗███████╗███╗   ███╗██████╗ ███████╗ ██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#  ██╔════╝██╔════╝████╗ ████║██╔══██╗██╔════╝██╔════╝     ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#  █████╗  █████╗  ██╔████╔██║██████╔╝█████╗  ██║  ███╗    █████╗  ██████╔╝███████║██╔████╔██║█████╗  
#  ██╔══╝  ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██╔══╝  ██║   ██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝  
#  ██║     ██║     ██║ ╚═╝ ██║██║     ███████╗╚██████╔╝    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#  ╚═╝     ╚═╝     ╚═╝     ╚═╝╚═╝     ╚══════╝ ╚═════╝     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

def open_ffmpeg_trimm():
    subprocess.Popen(["powershell", "start", "D:\@git\\ms1\\scripts\\ffmpeg\\trim.ps1"])

def open_ffmpeg_convt():
    subprocess.run(["powershell", "start", "D:\@git\\ms1\\scripts\\ffmpeg\\convert.ps1"])

def open_ffmpeg_dimns():
    subprocess.run(["powershell", "start", "D:\@git\\ms1\\scripts\\ffmpeg\\dimension.ps1"])

def open_ffmpeg_imgdm():
    subprocess.run(["powershell", "start", "D:\@git\\ms1\\scripts\\ffmpeg\\imgdim.ps1"])

def open_ffmpeg_merge():
    subprocess.run(["powershell", "start", "D:\@git\\ms1\\scripts\\ffmpeg\\merge.ps1"])

#! FRAME Function
def switch_to_ffmpeg_frame():
    switch_to_frame(FR_FFMPEG, MAIN_FRAME)

BT_FFMPEG_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "FFMPEG", switch_to_ffmpeg_frame, bg="#408b40", fg="#FFFFFF", height=2, width=30, relief="flat", highlightthickness=2, highlightbackground="#408b40", font=("Helvetica", 13, "bold")) ; BT_FFMPEG_MAIN_FRAME.pack(padx=(0,0),pady=(2,2))
FR_FFMPEG = tk.Frame(BORDER_FRAME, bg="#1D2327", width=500, height=700) ; FR_FFMPEG.pack_propagate(False)
BT_BACK = tk.Button(FR_FFMPEG, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_FFMPEG), bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 12, "bold")) ; BT_BACK.pack(side="bottom", anchor="w", padx=(125,0), pady=(0,24))

BT_TRIMM=tk.Button(FR_FFMPEG, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_trimm, text="Trim"          ) ; BT_TRIMM.pack     (pady=(35,0))
BT_CONVT=tk.Button(FR_FFMPEG, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_convt, text="Convert"       ) ; BT_CONVT.pack     (pady=(1,0))
BT_DIMNS=tk.Button(FR_FFMPEG, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_dimns, text="Dimension"     ) ; BT_DIMNS.pack     (pady=(1,0))
BT_IMGDM=tk.Button(FR_FFMPEG, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_imgdm, text="Imagedimension") ; BT_IMGDM.pack     (pady=(1,0))
BT_MERGE=tk.Button(FR_FFMPEG, bg="#FFFFFF", fg="#1D2027", height=1,width=20, bd=0,highlightthickness=0, font=("calibri",14,"bold"), command=open_ffmpeg_merge, text="Merge"         ) ; BT_MERGE.pack     (pady=(1,0))


#  ███████╗██╗███╗   ██╗██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#  ██╔════╝██║████╗  ██║██╔══██╗    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#  █████╗  ██║██╔██╗ ██║██║  ██║    █████╗  ██████╔╝███████║██╔████╔██║█████╗  
#  ██╔══╝  ██║██║╚██╗██║██║  ██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝  
#  ██║     ██║██║ ╚████║██████╔╝    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

def find_file():
    subprocess.run(["powershell", "start", "D:\@git\\ms1\\scripts\\find\\find_file.ps1"])

def find_patt():
    subprocess.run(["powershell", "start", "D:\@git\\ms1\\scripts\\find\\find_pattern.ps1"])

def find_size():
    subprocess.run(["powershell", "start", "D:\@git\\ms1\\scripts\\find\\find_size.ps1"])

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
    switch_to_frame(FR_FIND, MAIN_FRAME)

BT_FIND_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "Find", switch_to_find_frame, bg="#FFFFFF", fg="#1D2027", height=2, width=30, relief="flat", highlightthickness=2, highlightbackground="#FFFFFF", font=("Helvetica", 13, "bold")) ; BT_FIND_MAIN_FRAME.pack(padx=(0,0),pady=(2,2))
FR_FIND = tk.Frame(BORDER_FRAME, bg="#1D2027", width=500, height=700) ; FR_FIND.pack_propagate(False)
BT_BACK = tk.Button(FR_FIND, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_FIND), bg="#1d2027", fg="#FFFFFF", relief="flat", height=1, width=2, font=("calibri", 12, "bold")) ; BT_BACK.pack(side="bottom", anchor="w", padx=(125,0), pady=(0,24))

BT_FF= tk.Button(FR_FIND, bg="white", fg ="#1D2027", height=2, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=find_file, text="Find File"   ) ; BT_FF.pack(pady=(35,0))
BT_FP= tk.Button(FR_FIND, bg="white", fg ="#1D2027", height=2, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=find_patt, text="Find Pattern") ; BT_FP.pack(pady=(1,0))
BT_FS= tk.Button(FR_FIND, bg="white", fg ="#1D2027", height=2, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=find_size, text="Find Size"   ) ; BT_FS.pack(pady=(1,0))

BT_FZF_C= tk.Button(FR_FIND, height=1, bg="#f80069", fg ="#b0e1bd", width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=fzf_c, text="FZF-->C:\\") ; BT_FZF_C.pack(pady=(1,0))
BT_FZF_D= tk.Button(FR_FIND, height=1, bg="#f80069", fg ="#b0e1bd", width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=fzf_d, text="FZF-->D:\\") ; BT_FZF_D.pack(pady=(1,0))

# Assuming you have a Tkinter Entry widget for user input
FZF_SEARCH_WIDGET = tk.Entry(FR_FIND, width=30, fg="black", bg="#7D879E", relief="flat", font=("calibri", 18, "bold", "italic"), justify="center") ; FZF_SEARCH_WIDGET.pack(pady=(10,1))
BT_ACK_C= tk.Button(FR_FIND, bg="#e63a00", fg ="#fcffef", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=ack_c, text="ACK-->C:\\") ; BT_ACK_C.pack(pady=(1,0))
BT_ACK_D= tk.Button(FR_FIND, bg="#e63a00", fg ="#fcffef", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=ack_d, text="ACK-->D:\\") ; BT_ACK_D.pack(pady=(1,0))


#  ███████╗ ██████╗ ██╗     ██████╗ ███████╗██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#  ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#  █████╗  ██║   ██║██║     ██║  ██║█████╗  ██████╔╝    █████╗  ██████╔╝███████║██╔████╔██║█████╗  
#  ██╔══╝  ██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝  
#  ██║     ╚██████╔╝███████╗██████╔╝███████╗██║  ██║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#  ╚═╝      ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

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


#TODO Folder_bt = tk.Button(MAIN_FRAME, text="Folders", command=lambda: switch_to_frame(FR_FOLDER, MAIN_FRAME), height=1, width=30, bg="#ffd86a", fg="#1D2027", bd=0, highlightthickness=5, anchor="center", font=("calibri", 14, "bold"))
#TODO Folder_bt.pack(pady=2, padx=0)

icon_path = "C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"
icon_image = ImageTk.PhotoImage(Image.open(icon_path))

def switch_to_tools_frame():
    switch_to_frame(FR_FOLDER, MAIN_FRAME)

BT_FOLDER_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "FOLDER", switch_to_tools_frame,image=icon_image, compound=tk.TOP, bg="#e7d86a", fg="#1D2027", height=40, width=300, relief="flat", highlightthickness=2, highlightbackground="#e7d86a", font=("Helvetica", 13, "bold")) ; BT_FOLDER_MAIN_FRAME.pack(padx=(0,0),pady=(2,2))
FR_FOLDER = tk.Frame(BORDER_FRAME, bg="#1D2027", width=500, height=700) ; FR_FOLDER.pack_propagate(False)
BT_BACK = tk.Button(FR_FOLDER, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_FOLDER), bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 12, "bold")) ; BT_BACK.pack(side="bottom", anchor="w", padx=(125,0), pady=(0,24))

All_Apps_bt        = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_appsfolder_fd , text="All Apps"       ) ; All_Apps_bt.pack      (pady=(35,0))
AppData_bt         = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_appdata_fd    , text="AppData"        ) ; AppData_bt.pack       (pady=(1,0))
Git_Projects_bt    = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_git_fd        , text="Git Projects"   ) ; Git_Projects_bt.pack  (pady=(1,0))
Packages_bt        = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_packages_fd   , text="Packages"       ) ; Packages_bt.pack      (pady=(1,0))
Programdata_bt     = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_programdata_fd, text="ProgramData"    ) ; Programdata_bt.pack   (pady=(1,0))
Scoop_bt           = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_scoop_fd      , text="Scoop"          ) ; Scoop_bt.pack         (pady=(1,0))
Software_bt        = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_sofware_fd    , text="Software"       ) ; Software_bt.pack      (pady=(1,0))
Song_bt            = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_song_fd       , text="Song"           ) ; Song_bt.pack          (pady=(1,0))
Startup_System_bt  = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_startups_fd   , text="Startup System" ) ; Startup_System_bt.pack(pady=(1,0))
Startup_User_bt    = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_usrstartups_fd, text="Startup User"   ) ; Startup_User_bt.pack  (pady=(1,0))
Temp_AppDate_bt    = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_templocal_fd  , text="Temp-AppDate"   ) ; Temp_AppDate_bt.pack  (pady=(1,0))
Temp_Windows_bt    = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_tempwin_fd    , text="Temp-Windows"   ) ; Temp_Windows_bt.pack  (pady=(1,0))
WindowsApp_bt      = tk.Button(FR_FOLDER, bg="#ffd86a", fg="#1D2027", height=1, width=20, relief="flat", highlightthickness=0, font=("calibri", 14, "bold"), command=open_Winapps_fd    , text="WindowsApp"     ) ; WindowsApp_bt.pack    (pady=(1,0))


#!  ██████╗ ██████╗  ██████╗  ██████╗███████╗███████╗███████╗       ██╗       ██████╗ ██╗  ██╗ ██████╗
#!  ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔════╝       ██║       ██╔══██╗██║ ██╔╝██╔════╝
#!  ██████╔╝██████╔╝██║   ██║██║     █████╗  ███████╗███████╗    ████████╗    ██████╔╝█████╔╝ ██║  ███╗
#!  ██╔═══╝ ██╔══██╗██║   ██║██║     ██╔══╝  ╚════██║╚════██║    ██╔═██╔═╝    ██╔═══╝ ██╔═██╗ ██║   ██║
#!  ██║     ██║  ██║╚██████╔╝╚██████╗███████╗███████║███████║    ██████║      ██║     ██║  ██╗╚██████╔╝
#!  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝    ╚═════╝      ╚═╝     ╚═╝  ╚═╝ ╚═════╝

#! FRAME Function
def switch_to_process_frame():
    switch_to_frame(FR_PROCESS, MAIN_FRAME)

BT_PROCESS_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "Process & PKG", switch_to_process_frame, bg="#cc2400", fg="#FFFFFF", height=2, width=30, relief="flat", highlightthickness=2, highlightbackground="#78ff81", font=("Helvetica", 13, "bold")) ; BT_PROCESS_MAIN_FRAME.pack(padx=(0,0),pady=(2,2))
FR_PROCESS = tk.Frame(BORDER_FRAME, bg="#1D2027", width=500, height=700) ; FR_PROCESS.pack_propagate(False)
BT_BACK = tk.Button(FR_PROCESS, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_PROCESS), bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 12, "bold")) ; BT_BACK.pack(side="bottom", anchor="w", padx=(125,0), pady=(0,24))

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

BT_AUTORUNS = tk.Button(FR_PROCESS, text="AutoRuns", command=launch_autoruns, height=1, width=20, bg="#1d2027", fg="#fff", bd=0, highlightthickness=0, font=("times", 14, "bold"))
BT_AUTORUNS.pack(pady=(30, 0))

def process_name():
    # Assuming you have a Tkinter Entry widget for input
    additional_text = WIDGET_APPID.get()
    return additional_text
def get_process():
    additional_text = process_name()
    command = f'Get-Process | Where-Object {{ $_.Name -like "*{additional_text}*" }}'
    try:
        subprocess.Popen(["powershell", "-Command", command])
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
def kil_process():
    additional_text = process_name()
    command = f'Stop-Process -Name {additional_text}'
    try:
        subprocess.Popen(["powershell", "-Command", command])
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

BOX_WIDGET_APPID = tk.Frame(FR_PROCESS, bg="red")
BOX_WIDGET_APPID.pack(pady=1)
WIDGET_APPID = tk.Entry(BOX_WIDGET_APPID, width=30, fg="#fff", bg="#1d2027", font=("calibri", 18, "bold", "italic"), justify="center", relief="flat")
WIDGET_APPID.pack(padx=2, pady=2)

BOX_ROW_APPID2 = tk.Frame(FR_PROCESS, bg="black")
BOX_ROW_APPID2.pack(pady=2)
BT_GET_ID = tk.Button(BOX_ROW_APPID2, bg="#1d2027", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=get_process, text="🔍"); BT_GET_ID.pack(side="left", pady=0)
BT_KIL_ID = tk.Button(BOX_ROW_APPID2, bg="#ff4f00", fg="#fcffef", height=1, width=15, bd=0, highlightthickness=0, font=("calibri", 14, "bold"), command=kil_process, text="❌"); BT_KIL_ID.pack(side="left", pady=0)


#?   ██╗ ██╗     ██╗    ██╗       ██╗       ███████╗
#?  ████████╗    ██║    ██║       ██║       ██╔════╝
#?  ╚██╔═██╔╝    ██║ █╗ ██║    ████████╗    ███████╗
#?  ████████╗    ██║███╗██║    ██╔═██╔═╝    ╚════██║
#?  ╚██╔═██╔╝    ╚███╔███╔╝    ██████║      ███████║
#?   ╚═╝ ╚═╝      ╚══╝╚══╝     ╚═════╝      ╚══════╝

# winget / scoop text based info/show search install etc
def insert_text():
    # Assuming you have a Tkinter Entry widget for input
    additional_text = WIDGET_STORE.get()
    return additional_text

def winget_search():
    additional_text = insert_text()
    # Enclose additional_text in double quotes if it contains spaces
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Winget Search\' ; winget search {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def winget_instal():
    additional_text = insert_text()
    # Enclose additional_text in double quotes if it contains spaces
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Winget install\' ; winget install {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def winget_uninst():
    additional_text = insert_text()
    # Enclose additional_text in double quotes if it contains spaces
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground red \'- Winget Uninstall\' ; winget uninstall {additional_text}"'
    try:
        subprocess.Popen(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def winget_infooo():
    additional_text = insert_text()
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
    command = ' $host.UI.RawUI.WindowTitle = "wget❌" ; winget list "" | fzf --multi --preview \'winget show {1}\' | ForEach-Object { winget uninstall $_.split()[0] }'
    try:
        subprocess.Popen([ 'start' , 'pwsh', '-Command', command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_search():
    additional_text = insert_text()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Scoop Search\' ; scoop search {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_install():
    additional_text = insert_text()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Scoop Install\' ; scoop install {additional_text}"'
    print("Executing command:", command)  # Print the command before executing
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_uninstall():
    additional_text = insert_text()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground red \'- Scoop UnInstall\' ; scoop uninstall {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_info():
    additional_text = insert_text()
    additional_text = f'"{additional_text}"' if " " in additional_text else additional_text
    command = f'pwsh -Command "cd ; write-host  -foreground blue \'- Scoop Info\' ; scoop info {additional_text}"'
    try:
        subprocess.Popen(["powershell", "-Command", command], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def scoop_install_fzf():
    # Path to the Python script generating the package list
    python_script = r"D:\@git\ms1\scripts\scoop\package_list_from_buckets.py"

    # Run the Python script to generate the package list
    try:
        subprocess.run(['python', python_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return

    # Path to the text file containing package list
    package_list_file = r"D:\@git\ms1\scripts\scoop\package_list_bucket.txt"

    # Command to read from the text file and pipe it to fzf
    command = f"type {package_list_file} | fzf --multi --preview 'scoop info {{1}}' | ForEach-Object {{ scoop install $_.split()[0] }}"

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

BOX_ROW_STORE = tk.Frame(FR_PROCESS, bg="green") ; BOX_ROW_STORE.pack(pady=(100,2))
WIDGET_STORE = tk.Entry(BOX_ROW_STORE, width=30, fg="#fff", bg="#1d2027", font=("calibri", 18, "bold", "italic"), justify="center", relief="flat") ; WIDGET_STORE.pack(padx=2, pady=2)

BOX_WINGET_STORE = tk.Frame(FR_PROCESS, bg="#1d2027") ; BOX_WINGET_STORE.pack(pady=2)
LB_WINGET_TITLE=tk.Label (BOX_WINGET_STORE, bg="#FFFFFF", fg="#000000", height=1, width=5, highlightthickness=3, font=("calibri",14,"bold"), text="Winget") ; LB_WINGET_TITLE.pack(side="left",pady=1,padx=1)
BT_WINGET_SEARC=tk.Button(BOX_WINGET_STORE, bg="#1d2027", fg="#fcffef", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), text="🔍", command = winget_search ) ; BT_WINGET_SEARC.pack(side="left",pady=1,padx=1)
BT_WINGET_INSTL=tk.Button(BOX_WINGET_STORE, bg="#1d2027", fg="#6ae56a", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), text="🔽", command = winget_instal ) ; BT_WINGET_INSTL.pack(side="left",pady=(1,8),padx=1)
BT_WINGET_UINST=tk.Button(BOX_WINGET_STORE, bg="#1d2027", fg="#ff3046", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), text="❌", command = winget_uninst ) ; BT_WINGET_UINST.pack(side="left",pady=1,padx=1)
BT_WINGET_INFOO=tk.Button(BOX_WINGET_STORE, bg="#1d2027", fg="#fcffef", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), text="❓", command = winget_infooo ) ; BT_WINGET_INFOO.pack(side="left",pady=1,padx=1)
BT_WINGET_FINST=tk.Button(BOX_WINGET_STORE, bg="#1d2027", fg="#2e80f7", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), text="🔎", command = wget_inst_fzf ) ; BT_WINGET_FINST.pack(side="left",pady=(1,8),padx=1)
BT_WINGET_FUNIN=tk.Button(BOX_WINGET_STORE, bg="#1d2027", fg="#2e80f7", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), text="❌", command = wget_unin_fzf ) ; BT_WINGET_FUNIN.pack(side="left",pady=1,padx=1)


BOX_SCOOP_STORE = tk.Frame(FR_PROCESS, bg="#1d2027")
BOX_SCOOP_STORE.pack(pady=2)
LB_SCOOP_TITLE = tk.Label(BOX_SCOOP_STORE, text="Scoop", fg="#000", bg="#fff", width=5, height=1, font=("calibri", 14, "bold"), highlightthickness=3) ; LB_SCOOP_TITLE.pack(side="left", pady=1, padx=1)
BT_SCOOP_SEARC = tk.Button(BOX_SCOOP_STORE, bg="#1d2027",fg="#fcffef", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), command = scoop_search       , text="🔍" ) ; BT_SCOOP_SEARC.pack(side="left", pady=1, padx=1)
BT_SCOOP_INSTL = tk.Button(BOX_SCOOP_STORE, bg="#1d2027",fg="#6ae56a", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), command = scoop_install      , text="🔽" ) ; BT_SCOOP_INSTL.pack(side="left", pady=(1,8), padx=1)
BT_SCOOP_UINST = tk.Button(BOX_SCOOP_STORE, bg="#1d2027",fg="#ff3046", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), command = scoop_uninstall    , text="❌" ) ; BT_SCOOP_UINST.pack(side="left", pady=1, padx=1)
BT_SCOOP_INFOO = tk.Button(BOX_SCOOP_STORE, bg="#1d2027",fg="#fcffef", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), command = scoop_info         , text="❓" ) ; BT_SCOOP_INFOO.pack(side="left", pady=1, padx=1)
BT_SCOOP_FINST = tk.Button(BOX_SCOOP_STORE, bg="#1d2027",fg="#2e80f7", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), command = scoop_install_fzf  , text="🔎" ) ; BT_SCOOP_FINST.pack(side="left", pady=(1,8), padx=1)
BT_SCOOP_FUNIN = tk.Button(BOX_SCOOP_STORE, bg="#1d2027",fg="#2e80f7", height=1, width=4, relief="flat", highlightthickness=0, font=("calibri",14,"bold"), command = scoop_uninstall_fzf, text="❌" ) ; BT_SCOOP_FUNIN.pack(side="left", pady=1, padx=1)


#   ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗     █████╗ ██████╗ ██████╗ ███████╗
#  ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝    ██╔══██╗██╔══██╗██╔══██╗██╔════╝
#  ██║     ███████║█████╗  ██║     █████╔╝     ███████║██████╔╝██████╔╝███████╗
#  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗     ██╔══██║██╔═══╝ ██╔═══╝ ╚════██║
#  ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗    ██║  ██║██║     ██║     ███████║
#   ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝

BT_APPLIST = tk.Button(FR_PROCESS, text="App List", command=lambda: switch_to_frame(Page1, FR_PROCESS), bg="#fff", fg="#000", width=20, highlightthickness=5, anchor="center", font=("times", 12, "bold"))
BT_APPLIST.pack(anchor="n", padx=(0,0), pady=(220,0))

Page1 = tk.Frame(BORDER_FRAME, bg="#1D2027", width=500, height=700)
Page1.pack_propagate(False)

BT_BACK = tk.Button(Page1, text="◀", command=lambda: switch_to_frame(FR_PROCESS, Page1 ), bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 12, "bold")) ; BT_BACK.pack(side="bottom", anchor="w", padx=(125,0), pady=(0,24))

LB_INITIALSPC = tk.Label(Page1, text="",  bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 16, "bold"))
LB_INITIALSPC.pack(side="top", anchor="ne", padx=(0,0), pady=(0,0))

def check_installation(app_name, paths_to_check, chkbx_var, chkbox_bt):
    application_installed = any(os.path.exists(path) for path in paths_to_check)
    chkbx_var.set(1 if application_installed else 0)

    # Change text color based on installation status if not already checked
    if not chkbx_var.get():
        text_color = "green" if application_installed else "red"
        chkbox_bt.config(foreground=text_color)

def install_application(app_name, install_command, chkbx_var, chkbox_bt):
    subprocess.Popen(install_command)
    chkbx_var.set(1)

    # After installation, set the text color to green if not already checked
    if not chkbx_var.get():
        chkbox_bt.config(foreground="green")

# Variable to track checkbox state
chkbx_rclone = tk.IntVar()
chkbx_powertoys = tk.IntVar()
chkbx_sonarr = tk.IntVar()
chkbx_radarr = tk.IntVar()
chkbx_prowlarr = tk.IntVar()
chkbx_bazarr = tk.IntVar()

# Define applications and their information
applications = [
    {"name": "Rclone", "paths": [r'C:\Users\nahid\scoop\apps\rclone\current\rclone.exe', r'C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\Rclone.Rclone_Microsoft.Winget.Source_8wekyb3d8bbwe\rclone-v1.65.2-windows-amd64\rclone.exe'], "install_command": 'pwsh -Command "cd ; write-host -foreground blue \'- Scoop Install\' ; scoop install rclone"', "chkbx_var": chkbx_rclone},
    {"name": "Powertoys", "paths": [r'C:\Users\nahid\scoop\apps\PowerToys\current\PowerToys.exe', r'C:\Program Files\PowerToys\PowerToys.exe'], "install_command": 'pwsh -Command "cd ; write-host -foreground blue  \'- Scoop Install\' ; scoop install PowerToys"', "chkbx_var": chkbx_powertoys},
    {"name": "Sonarr", "paths": [r'C:\ProgramData\Sonarr\bin\Sonarr.exe'], "install_command": 'pwsh -Command "cd ; write-host -foreground blue  \'- Winget Install\' ; winget install TeamSonarr.Sonarr"', "chkbx_var": chkbx_sonarr},
    {"name": "Radarr", "paths": [r'C:\ProgramData\Radarr\bin\Radarr.exe'], "install_command": 'pwsh -Command "cd ; write-host -foreground blue  \'- Winget Install\' ; winget install TeamRadarr.Radarr"', "chkbx_var": chkbx_radarr},
    {"name": "Prowlarr", "paths": [r'C:\ProgramData\Prowlarr\bin\Prowlarr.exe'], "install_command": 'pwsh -Command "cd ; write-host -foreground blue  \'- Winget Install\' ; winget install TeamProwlarr.Prowlarr"', "chkbx_var": chkbx_prowlarr},
    {"name": "Bazarr", "paths": [r'C:\ProgramData\Bazarr\bin\Bazarr.exe'], "install_command": 'pwsh -Command "cd ; write-host -foreground blue  \'- Winget Install\' ; winget install Morpheus.Bazarr"', "chkbx_var": chkbx_bazarr},
    # Add more applications here
]

# Create and pack checkboxes, check buttons, and install buttons for each application
for app in applications:
    frame = tk.Frame(Page1, bg="#1d2027")
    frame.pack( padx=(5,0), pady=(5,0), anchor="ne")

    chkbox_bt = tk.Checkbutton(frame, text=app["name"], variable=app["chkbx_var"], font=("calibri", 14, "bold"), foreground="green", background="#1d2027", activebackground="#1d2027", selectcolor="#1d2027", padx=10, pady=5, borderwidth=2, relief="solid", command=lambda app=app: check_installation(app["name"], app["paths"], app["chkbx_var"], chkbox_bt))
    chk_bt = tk.Button(frame, text=f"Check", foreground="green", background="#1d2027", command=lambda app=app: check_installation(app["name"], app["paths"], app["chkbx_var"], chkbox_bt))
    ins_bt = tk.Button(frame, text=f"Install", foreground="green", background="#1d2027", command=lambda app=app: install_application(app["name"], app["install_command"], app["chkbx_var"], chkbox_bt))

    chkbox_bt.pack(side="left", padx=(0,5  ), pady=(0,0))
    chk_bt.pack   (side="left", padx=(10,0 ), pady=(0,0))
    ins_bt.pack   (side="left", padx=(0,100), pady=(0,0))

    # Check installation status at the start
    check_installation(app["name"], app["paths"], app["chkbx_var"], chkbox_bt)



#  ████████╗ ██████╗  ██████╗ ██╗     ███████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#  ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#     ██║   ██║   ██║██║   ██║██║     ███████╗    █████╗  ██████╔╝███████║██╔████╔██║█████╗  
#     ██║   ██║   ██║██║   ██║██║     ╚════██║    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝  
#     ██║   ╚██████╔╝╚██████╔╝███████╗███████║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

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
    switch_to_frame(FR_TOOLS, MAIN_FRAME)

BT_TOOLS_MAIN_FRAME = M1_hold_release(MAIN_FRAME, "TOOLS", switch_to_tools_frame, bg="#454545", fg="#FFFFFF", height=2, width=30, relief="flat", highlightthickness=2, highlightbackground="#FFFFFF", font=("Helvetica", 13, "bold")) ; BT_TOOLS_MAIN_FRAME.pack(padx=(0,0),pady=(2,2))

FR_TOOLS = tk.Frame(BORDER_FRAME, bg="#1D2027", width=500, height=700)
FR_TOOLS.pack_propagate(False)

BT_BACK = tk.Button(FR_TOOLS, text="◀", command=lambda: switch_to_frame(MAIN_FRAME, FR_TOOLS), bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 12, "bold")) ; BT_BACK.pack(side="bottom", anchor="w", padx=(125,0), pady=(0,24))

adapter_bt      = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=advanced_adapter,  text="Advanced Adapter",         ) ; adapter_bt.pack     (pady=(35,0))
chkdsk_bt       = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_chkdsk,       text="CheckDisk",                ) ; chkdsk_bt.pack      (pady=(1,0))
ctt_bt          = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=ctt,               text="Chris Titus Win Utility",  ) ; ctt_bt.pack         (pady=(1,0))
diskcleanmgr_bt = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_cleanmgr,     text="Disk Cleanup",             ) ; diskcleanmgr_bt.pack(pady=(1,0))
dism_bt         = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_dism,         text="DISM",                     ) ; dism_bt.pack        (pady=(1,0))
dxdiag_bt       = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_dxdiag,       text="DxDiag",                   ) ; dxdiag_bt.pack      (pady=(1,0))
flushdns_bt     = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=flush_dns,         text="Flush DNS",                ) ; flushdns_bt.pack    (pady=(1,0))
msconfig_bt     = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_msconfig,     text="msconfig",                 ) ; msconfig_bt.pack    (pady=(1,0))
netplwiz_bt     = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_netplwiz,     text="Netplwiz",                 ) ; netplwiz_bt.pack    (pady=(1,0))
powerplan_bt    = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_powerplan,    text="Power Plan",               ) ; powerplan_bt.pack   (pady=(1,0))
sfc_bt          = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_sfc,          text="SFC",                      ) ; sfc_bt.pack         (pady=(1,0))
snip_bt         = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_snippingtool, text="Sniping Tool",             ) ; snip_bt.pack        (pady=(1,0))
systeminfo_bt   = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_systeminfo,   text="Systeminfo",               ) ; systeminfo_bt.pack  (pady=(1,0))
uac_bt          = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=open_uac,          text="UAC",                      ) ; uac_bt.pack         (pady=(1,0))
winfeatures_bt  = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=optionalfeatures,  text="Turn on Windows Features", ) ; winfeatures_bt.pack (pady=(1,0))
Winsock_bt      = tk.Button(FR_TOOLS, bg="white", fg ="#1D2027", height =1, width=25, relief="solid", bd=0, highlightthickness=0, anchor="w", font=("calibri", 14, "bold"), command=winsock_reset,     text="Winsock Reset",            ) ; Winsock_bt.pack     (pady=(1,0))


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

button_row1 = tk.Frame(MAIN_FRAME, bg="black")
button_row1.pack(pady=2)
force_shutdown_bt = tk.Button(button_row1, text="Shutdown [F]", command=force_shutdown, height=2, width=15, bg="#ff0000", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
force_restart_bt  = tk.Button(button_row1, text="Restart [F]",  command=force_restart,  height=2, width=15, bg="#ff6600", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))

force_shutdown_bt.pack(pady=0, side="left", anchor="w")
force_restart_bt.pack (pady=0, side="left", anchor="w")





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
# todo Test