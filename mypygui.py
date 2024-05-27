#? https://pypi.org/project/pretty-errors/

from customtkinter import *
from datetime import datetime
from functionlist import *
from PIL import Image, ImageTk
from pyadl import ADLManager
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

#! Resize Window

# Function to toggle window size
def toggle_window_size(size):
    global window_state
    global x
    global y

    if size == 'line':
        ROOT.geometry('1920x39')
        x = screen_width // 2 - 1920 // 2
        y = 993
        ROOT.configure(bg='red')
        LB_L.config(text='\ueab7', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("JetBrainsMono NF", 16, "bold"))
        LB_M.config(text='\uea72', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("JetBrainsMono NF", 18, "bold"))
    elif size == 'max':
        ROOT.geometry('1920x140')
        x = screen_width // 2 - 1920 // 2
        y = 892
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

def toggle_checking():
    global checking
    checking = not checking
    if checking:
        if ROOT.attributes('-topmost'):  # Only start checking if already topmost
            check_window_topmost()  # Start checking if toggled on and already topmost
        Topmost_lb.config(fg="#000000")  # Change text color to green
        Topmost_lb.config(bg="#FFFFFF")  # Change text color to green
    else:
        ROOT.after_cancel(check_window_topmost)  # Cancel the checking if toggled off
        Topmost_lb.config(fg="#FFFFFF")  # Change text color to white
        Topmost_lb.config(bg="#000000")  # Change text color to white

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


def compare_path_file():
    source_dest_pairs = {
"komorebi"       :(komorebi_src    ,komorebi_dst    ),
# "glaze-wm"       :(glazewm_src     ,glazewm_dst     ),
# "Nilesoft"       :(Nilesoft_src    ,Nilesoft_dst    ),
# "whkd"           :(whkd_src        ,whkd_dst        ),
"pwshH"          :(pwshH_src       ,pwshH_dst       ),
"terminal"       :(terminal_src    ,terminal_dst    ),
"rclone_config"  :(rclone_src      ,rclone_dst      ),
"pwsh_profile"   :(pwsh_profile_src,pwsh_profile_dst),

"Sr_db"          :(Sr_db_src       ,Sr_db_dst       ),
# "Sr_cf"          :(Sr_cf_src       ,Sr_cf_dst       ),
"Rr_db"          :(Rr_db_src       ,Rr_db_dst       ),
# "Rr_cf"          :(Rr_cf_src       ,Rr_cf_dst       ),
"Pr_db"          :(Pr_db_src       ,Pr_db_dst       ),
# "Pr_cf"          :(Pr_cf_src       ,Pr_cf_dst       ),
# "br_db"          :(br_db_src       ,br_db_dst       ),
# "br_cf"          :(br_cf_src       ,br_cf_dst       ),

"Rss_db"         :(Rss_db_src      ,Rss_db_dst      ),
"Rss_cf"         :(Rss_cf_src      ,Rss_cf_dst      ),
    }
    is_all_same = True
    names = []
    for name, (source, dest) in source_dest_pairs.items():
        if os.path.isdir(source) and os.path.isdir(dest):
            dcmp = filecmp.dircmp(source, dest)
            if dcmp.diff_files or dcmp.left_only or dcmp.right_only:
                is_all_same = False
                names.append(name)
        elif os.path.isfile(source) and os.path.isfile(dest):
            if not filecmp.cmp(source, dest):
                is_all_same = False
                names.append(name)
        else:
            is_all_same = False
            names.append(name)
    if is_all_same:
        emoji = "✅"
        name = "✅"
    else:
        emoji = "❌"
        names_per_row = 4
        formatted_names = [", ".join(names[i:i + names_per_row]) for i in range(0, len(names), names_per_row)]
        name = "\n".join(formatted_names)
    Changes_Monitor_lb.config(text=f"{name}")
    Changes_Monitor_lb.after(1000, compare_path_file)


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

LB_K=CTkLabel(ROOT1, text="\udb80\udf0c", bg_color="#1d2027",text_color="#d4d654", anchor="w",font=("JetBrainsMono NFP",25,"bold"))
LB_K.pack(side="left",padx=(5,0),pady=(1,0))
LB_K.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\shortcut.py"], shell=True))

Tools_bt=CTkLabel(ROOT1, text="\ue20f", bg_color="#1d2027",text_color="#f37826", anchor="w",font=("JetBrainsMono NFP",20,"bold"))
Tools_bt.pack(side="left",padx=(10,0),pady=(1,0))
Tools_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\mypygui_import\\tools.py"], shell=True))

Startup_bt=CTkLabel(ROOT1, text="\uf4cc", bg_color="#1d2027",text_color="#6488ff", anchor="w",font=("JetBrainsMono NFP",25,"bold"))
Startup_bt.pack(side="left",padx=(10,0),pady=(1,0))
Startup_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\startup.py"], shell=True))
Startup_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\startup.py"], shell=True))

AppManagement_bt=CTkLabel(ROOT1, text="\uf0be", bg_color="#1d2027",text_color="#26b2f3", anchor="w",font=("JetBrainsMono NFP",25,"bold"))
AppManagement_bt.pack(side="left",padx=(10,0),pady=(1,0))
AppManagement_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\mypygui_import\\app_store.py"], shell=True))
AppManagement_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\mypygui_import\\app_store.py"], shell=True))
AppManagement_bt.bind("<Button-3>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\mypygui_import\\applist.py"], shell=True))
AppManagement_bt.bind("<Control-Button-3>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\mypygui_import\\applist.py"], shell=True))

Folder_bt=CTkLabel(ROOT1, text="\ueaf7", font=("JetBrainsMono NFP",25,"bold"), anchor="w", bg_color="#1d2027",text_color="#ffd900")
Folder_bt.pack(side="left",padx=(10,0),pady=(1,0))
Folder_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\mypygui_import\\folder.py"], shell=True))
Folder_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\mypygui_import\\folder.py"], shell=True))

Process_bt=CTkLabel(ROOT1, text="\ueba2", bg_color="#1d2027",text_color="#ff1313", anchor="w",font=("JetBrainsMono NFP",18,"bold"))
Process_bt.pack(side="left",padx=(10,0),pady=(1,0))
Process_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\mypygui_import\\process.py"], shell=True))
Process_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\mypygui_import\\process.py"], shell=True))

ScriptList_bt=CTkLabel(ROOT1, text="\uf03a", bg_color="#1d2027",text_color="#e0a04c", anchor="w",font=("JetBrainsMono NFP",18,"bold"))
ScriptList_bt.pack(side="left",padx=(10,0),pady=(1,0))
ScriptList_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\mypygui_import\\script_list.py"], shell=True))
ScriptList_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\mypygui_import\\script_list.py"], shell=True))

LB_1=tk.Label(ROOT1, text="\udb83\udca0",bg="#1d2027",fg="#2af083",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
LB_1.pack(side="left",padx=(3,0),pady=(0,0))
LB_1.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\scripts\\python\\bar_1.py"], shell=True))
LB_1.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\scripts\\python\\bar_1.py"], shell=True))

Update_bt=tk.Label(ROOT1, text="\uf01b",bg="#1d2027",fg="#16a2ff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
Update_bt.pack(side="left",padx=(3,0),pady=(0,0))
Update_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\update.ps1"],  shell=True))
Update_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\update.ps1"],  shell=True))

Backup_bt=tk.Label(ROOT1, text="\uf01b",bg="#1d2027",fg="#2af083",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
Backup_bt.pack(side="left",padx=(3,0),pady=(0,0))
Backup_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\backup.ps1"], shell=True))
Backup_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\backup.ps1"], shell=True))

BackupRestore_bt=tk.Label(ROOT1, text="\udb84\udc38",bg="#1d2027",fg="#3bc7ff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
BackupRestore_bt.pack(side="left",padx=(3,0),pady=(0,0))
BackupRestore_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\utility\\BackupRestore.py"], shell=True))
BackupRestore_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\utility\\BackupRestore.py"],shell=True))

PositionXY_bt=tk.Label(ROOT1, text="\udb83\ude51",bg="#1d2027",fg="#ffffff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
PositionXY_bt.pack(side="left",padx=(3,0),pady=(0,0))
PositionXY_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\utility\\PositionXY.py"], shell=True))
PositionXY_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\utility\\PositionXY.py"],shell=True))

ColorTool_bt=tk.Label(ROOT1, text="\ue22b",bg="#1d2027",fg="#c588fd",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
ColorTool_bt.pack(side="left",padx=(3,0),pady=(0,0))
ColorTool_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\utility\\color\\color_picker.py"], shell=True))
ColorTool_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\utility\\color\\color_picker.py"],shell=True))
ColorTool_bt.bind("<Button-3>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\utility\\color\\color_pallet_rand_fg_bgFF00.py"], shell=True))
ColorTool_bt.bind("<Control-Button-3>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\utility\\color\\color_pallet_rand_fg_bgFF00.py"],shell=True))

RoundedCorner_lb = tk.Label(ROOT1, text="\udb81\ude07", bg="#1d2027", fg="#ffffff", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
RoundedCorner_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
RoundedCorner_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c "C:\\ms1\\utility\\RoundedCornerOnOff.py"'))
RoundedCorner_lb.bind("<Control-Button-1>",lambda event=None:subprocess.Popen('cmd /c Code "C:\\ms1\\utility\\RoundedCornerOnOff.py"'))

Search_bt=tk.Label(ROOT1, text="\uf422",bg="#1d2027",fg="#95c64d",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
Search_bt.pack(side="left",padx=(3,0),pady=(0,0))
Search_bt.bind("<Button-1>",fzf_search)
Search_bt.bind("<Control-Button-1>",edit_fzfSearch)

LB_get=tk.Label(ROOT1, text="\uf05a",bg="#1d2027",fg="#b9b1f1",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
LB_get.pack(side="left",padx=(3,0),pady=(0,0))
LB_get.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\ms1\\utility\\info.py"], shell=True))
LB_get.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\utility\\info.py"], shell=True))
# LB_get.bind("<Button-1>",lambda event:get_active_window_info())

LockBox_lb = tk.Label(ROOT1, bg="#1d2027", fg="#ff0000", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
LockBox_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
LockBox_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c "C:\\Program Files\\My Lockbox\\mylbx.exe"'))

Encrypt_lb = tk.Label(ROOT1,text="\uf084", bg="#1d2027", fg="#ff0000", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
Encrypt_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
Encrypt_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c C:\\ms1\\utility\\Encryption.py'))
Encrypt_lb.bind("<Control-Button-1>",lambda event=None:subprocess.Popen('cmd /c code C:\\ms1\\utility\\Encryption.py'))

VirtualMonitor_lb = tk.Label(ROOT1,text="2nd", bg="#1d2027", fg="#8ab9ff", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
VirtualMonitor_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
VirtualMonitor_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c C:\\ms1\\2nd_Monitor.py'))
VirtualMonitor_lb.bind("<Control-Button-1>",lambda event=None:subprocess.Popen('cmd /c code C:\\ms1\\2nd_Monitor.py'))

ShadowFight3_lb = tk.Label(ROOT1,text="SH3", bg="#1d2027", fg="#cc5907", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
ShadowFight3_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
ShadowFight3_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c C:\\ms1\\SH3\\SH3V2.py'))
ShadowFight3_lb.bind("<Control-Button-1>",lambda event=None:subprocess.Popen('cmd /c code C:\\ms1\\SH3\\SH3V2.py'))

#! FFMPEG
FFMPEG_bt = CTkButton(ROOT1, text="\uf07cFFMPEG",width=0, command=lambda:switch_to_frame(FR_FFmpeg , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1,hover_color="#1dd463", border_color="#000000", fg_color="#bff130", text_color="#000")
FFMPEG_bt.pack(side="left")
FR_FFmpeg = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
FR_FFmpeg.pack_propagate(True)
BoxForFFmpeg = tk.Frame(FR_FFmpeg, bg="#1d2027")
BoxForFFmpeg.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
back_ffmpeg=tk.Button(BoxForFFmpeg,text="\ueb6f",width=0,bg="#1D2027",fg="#FFFFFF",command=lambda:switch_to_frame (MAIN_FRAME,FR_FFmpeg))
back_ffmpeg.pack(side="left" )
def ffmpeg(FR_FFmpeg):
    Trim_bt          =tk.Button(BoxForFFmpeg,text="Trim"          ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_trim        ); Trim_bt.pack          (side="left",padx=(0,0))
    Convert_bt       =tk.Button(BoxForFFmpeg,text="Convert"       ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_convert     ); Convert_bt.pack       (side="left",padx=(0,0))
    Dimension_bt     =tk.Button(BoxForFFmpeg,text="Dimension"     ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_dimension   ); Dimension_bt.pack     (side="left",padx=(0,0))
    Imagedimension_bt=tk.Button(BoxForFFmpeg,text="Imagedimension",width=0,fg="#FFFFFF",bg="#1D2027",command=start_imgdimension); Imagedimension_bt.pack(side="left",padx=(0,0))
    Merge_bt         =tk.Button(BoxForFFmpeg,text="Merge"         ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_merge       ); Merge_bt.pack         (side="left",padx=(0,0))
ffmpeg(FR_FFmpeg)

#! Find
Find_bt = CTkButton(ROOT1, text="\uf07cFind",width=0, command=lambda:switch_to_frame(FR_Find , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0,hover_color="#1dd463", border_width=1, border_color="#000000", fg_color="#bff130", text_color="#000")
Find_bt.pack(side="left")
FR_Find = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
FR_Find.pack_propagate(True)
BoxForFind = tk.Frame(FR_Find, bg="#1d2027")
BoxForFind.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
back_find=tk.Button(BoxForFind,text="\ueb6f",width=0 ,bg="#1D2027", fg="#FFFFFF", command=lambda:switch_to_frame(MAIN_FRAME,FR_Find))
back_find.pack(side="left" ,padx=(0,0))
def find(FR_Find):
    File_bt    =tk.Button(BoxForFind,text="File"       ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_file   ); File_bt.pack   (side="left" ,padx=(0,0))
    Pattern_bt =tk.Button(BoxForFind,text="Pattern"    ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_pattern); Pattern_bt.pack(side="left" ,padx=(0,0))
    Size_bt    =tk.Button(BoxForFind,text="Size"       ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_size   ); Size_bt.pack   (side="left" ,padx=(0,0))
    FZFC_bt    =tk.Button(BoxForFind,text="FZF-C"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_fzf_c       ); FZFC_bt.pack   (side="left" ,padx=(0,0))
    FZFD_bt    =tk.Button(BoxForFind,text="FZF-D"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_fzf_d       ); FZFD_bt.pack   (side="left" ,padx=(0,0))
    ackc_bt    =tk.Button(BoxForFind,text="ACK-C"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_ack_c       ); ackc_bt.pack   (side="left" ,padx=(0,0))
    ackd_bt    =tk.Button(BoxForFind,text="ACK-D"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_ack_d       ); ackd_bt.pack   (side="left" ,padx=(0,0))
find(FR_Find)

#! Desktop
Desktop_bt = CTkButton(ROOT1, text="\uf07cDesktop",width=0, command=lambda:switch_to_frame(FR_Desktop , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0,hover_color="#1dd463", border_width=1, border_color="#FFFFFF", fg_color="#0099ff", text_color="#000000")
Desktop_bt.pack(side="left")
FR_Desktop = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
FR_Desktop.pack_propagate(True)
BoxForDesktop = tk.Frame(FR_Desktop, bg="#1d2027")
BoxForDesktop.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
BACK=tk.Button(BoxForDesktop,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,FR_Desktop))
BACK.pack(side="left" ,padx=(0,0))

sonarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\sonarr-20x20.png"))
radarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\radarr-20x20.png"))
def Folder(FR_Desktop):
    Sonarr_bt=tk.Label(BoxForDesktop, image=sonarr_img, compound=tk.TOP, text="", height=30, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
    Sonarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Sonarr"],shell=True)))
    Sonarr_bt.pack(pady=(0,2), side="left", anchor="w", padx=(0,0))
    Radarr_bt=tk.Label(BoxForDesktop, image=radarr_img, compound=tk.TOP, text="", height=50, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
    Radarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Radarr"],shell=True)))
    Radarr_bt.pack(pady=(0,2), side="left", anchor="w", padx=(0,0))
Folder(FR_Desktop)

#! Worspace_1
WorkSpace_1 = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
WorkSpace_1.pack_propagate(True)
Enter_WS1 = CTkButton(ROOT1, text="\uf07cP", width=0, hover_color="#1dd463", command=lambda:switch_to_frame(WorkSpace_1 , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, border_color="#000000", fg_color="#bff130", text_color="#000")
Enter_WS1.pack(side="left", padx=(1,1))
BOX = tk.Frame(WorkSpace_1, bg="#1D2027")
BOX.pack(side="top", pady=(4,2),padx=(5,1), anchor="center", fill="x")
BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,WorkSpace_1))
BACK.pack(side="left" ,padx=(0,0))

#! EDIT SPACE
EDIT_SPACE = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
EDIT_SPACE.pack_propagate(True)
Enter_WS2 = CTkButton(ROOT1, text="\uf07cEdit", width=0, hover_color="#1dd463", command=lambda:switch_to_frame(EDIT_SPACE , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, border_color="#000000", fg_color="#bff130", text_color="#000")
Enter_WS2.pack(side="left", padx=(1,1))
BOX = tk.Frame(EDIT_SPACE, bg="#1D2027")
BOX.pack(side="top", pady=(4,2),padx=(5,1), anchor="center", fill="x")
BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,EDIT_SPACE))
BACK.pack(side="left" ,padx=(0,0))
def Folder(EDIT_SPACE):
    MYPYGUI=tk.Button(BOX,text="MYPYGUI",width=0 ,fg="#ffffff", bg="#204892", command=lambda:(subprocess.Popen(["cmd /c Code C:\\ms1\\mypygui.py"],shell=True)))
    MYPYGUI.pack(side="left" ,padx=(0,0))
    AHKEDIT=tk.Button(BOX,text="AHKSCRIPT",width=0 ,fg="#ffffff", bg="#5f925f", command=lambda:(subprocess.Popen(["cmd /c Code C:\\ms1\\ahkscripts.ahk"],shell=True)))
    AHKEDIT.pack(side="left" ,padx=(0,0))
Folder(EDIT_SPACE)

#! Worspace_3

SEPARATOR=tk.Label(ROOT1,text="[",bg="#1d2027",fg="#009fff",height=0,width=0,relief="flat",font=("JetBrainsMono NFP",18,"bold"))
SEPARATOR.pack(side="left",padx=(3,0),pady=(0,0))
bkup=tk.Label(ROOT1,text="\udb80\udea2",bg="#1d2027",fg="#009fff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",18,"bold"))
bkup.pack(side="left",padx=(0,0),pady=(0,0))
bkup.bind ("<Button-1>",git_backup)
STATUS_MS1=tk.Label(ROOT1,bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",10,"bold"),text="")
STATUS_MS1.pack(side="left",padx=(0,0),pady=(0,0))
STATUS_MS1.bind("<Button-1>",lambda event:show_git_changes("C:\\ms1"))
STATUS_MS2=tk.Label(ROOT1,bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",10,"bold"),text="")
STATUS_MS2.pack(side="left",padx=(0,0),pady=(0,0))
STATUS_MS2.bind("<Button-1>",lambda event:show_git_changes("C:\\ms2"))
SEPARATOR=tk.Label(ROOT1,text="]",bg="#1d2027",fg="#009fff",height=0,width=0,relief="flat",font=("JetBrainsMono NFP",18,"bold"))
SEPARATOR.pack(side="left",padx=(0,0),pady=(0,0))

Changes_Monitor_lb = tk.Label(ROOT1, text="", bg="#1d2027", fg="#68fc2d")
Changes_Monitor_lb.pack(side="left",padx=(0,0),pady=(0,0))

#! ██████╗ ██╗ ██████╗ ██╗  ██╗████████╗
#! ██╔══██╗██║██╔════╝ ██║  ██║╚══██╔══╝
#! ██████╔╝██║██║  ███╗███████║   ██║
#! ██╔══██╗██║██║   ██║██╔══██║   ██║
#! ██║  ██║██║╚██████╔╝██║  ██║   ██║
#! ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝

cpu_core_frame =CTkFrame(ROOT2,corner_radius=5,bg_color="#1d2027",border_width=1,border_color="#000000", fg_color="#fff")
cpu_core_frame.pack(side="left",padx=(3,0),pady=(0,0))

Download_lb=tk.Label(ROOT2,bg="#000000",fg="#080505",height=0,width =7,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
Download_lb.pack(side="left",padx=(3,0 ),pady=(0,0))
Download_lb.bind("<Button-1>",None)

Upload_lb=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =7,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
Upload_lb.pack(side="left",padx=(3,0 ),pady=(0,0))
Upload_lb.bind("<Button-1>",None)

LB_CPU=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#1b8af1",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_CPU.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_CPU.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\utility\\kill_process.ps1"], shell=True))

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

ShutReboot=CTkButton(ROOT2, text="\udb82\udc20",fg_color="#1d2027",text_color="#fa0000", corner_radius=5,height=10,width=0, anchor="center",font=("JetBrainsMono NFP",25,"bold"))
ShutReboot.pack(side="left",padx=(1,1),pady=(0,0))
ShutReboot.bind("<Button-1>",force_shutdown)
ShutReboot.bind("<Button-3>",force_restart)

LB_R=tk.Label(ROOT2 ,text="\uf2f1", bg="#1d2027",fg="#26b2f3",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",16,"bold"))
LB_R.pack(side="left",padx=(1,1 ),pady=(0,0))
LB_R.bind("<Button-1>",restart)

# LB_L=tk.Label(ROOT2,bg="#1d2027",fg="#00FF00",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",16,"bold"),text="\uf106")
# LB_L.pack(side="left",padx=(3,0 ),pady=(0,0))
# LB_L.bind("<Button-1>",lambda event:toggle_window_size('line'))

# LB_M=tk.Label(ROOT2,bg="#1d2027",fg="#26b2f3",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",18,"bold"),text="\uea72")
# LB_M.pack(side="left",padx=(3,0 ),pady=(0,0))
# LB_M.bind("<Button-1>",lambda event:toggle_window_size('max'))

LB_XXX=tk.Label(ROOT2, text="\uf2d3", bg="#1d2027",fg="#ff0000",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",18,"bold"))
LB_XXX.pack(side="left",padx=(1,10),pady=(0,0))
LB_XXX.bind("<Button-1>",close_window)


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

queue = Queue()
status_thread = threading.Thread(target=update_status, daemon=True)
gui_thread = threading.Thread(target=update_gui, daemon=True)
status_thread.start()
gui_thread.start()

update_uptime_label()

update_info_labels()

# check_window_topmost()

Lockbox_update_label(LockBox_lb)

compare_path_file()










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