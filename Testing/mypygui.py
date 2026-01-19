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

OS_LB = tk.Label(ROOT1,text="OS", bg="#1d2027", fg="#59e3a7", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
OS_LB.pack(side="left", padx=(0, 0), pady=(0, 0))
OS_LB.bind( "<Button-1>", lambda event=None: subprocess.Popen( r'cmd /c start windows.py', cwd=r'C:\\@delta\\ms1\\New folder\\'))
OS_LB.bind("<Button-3>",lambda event:subprocess.Popen([r"cmd /c start C:\@delta\ms1\New folder\windows.py"], shell=True))
OS_LB.bind("<Control-Button-1>",lambda event=None:subprocess.Popen(r'cmd /c code C:\@delta\ms1\New folder\windows.py'))

Update=CTkLabel(ROOT1, text="\uf01b", bg_color="#1d2027",text_color="#16a2ff", corner_radius=5, anchor="w",font=("JetBrainsMono NFP",20,"bold"))
Update.pack(side="left",padx=(0,0),pady=(1,0))
Update.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\@delta\\ms1\\scripts\\update.ps1"], shell=True))
Update.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\update.ps1"], shell=True))

# Update=CTkLabel(ROOT1, text="\uf01b", bg_color="#1d2027",text_color="#16a2ff", corner_radius=5, anchor="w",font=("JetBrainsMono NFP",20,"bold"))
# Update.pack(side="left",padx=(0,0),pady=(1,0))
# Update.bind("<Button-1>",lambda event:subprocess.Popen(["C:\\Users\\nahid\\AppData\\Local\\Programs\\UniGetUI\\UniGetUI.exe"], shell=True))


Tools_bt=CTkLabel(ROOT1, text="\ueb51", bg_color="#1d2027",text_color="#ffffff", corner_radius=5, anchor="w",font=("JetBrainsMono NFP",20,"bold"))
Tools_bt.pack(side="left",padx=(2,0),pady=(1,0))
Tools_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\mypygui_import\\tools.py"], shell=True))
Tools_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\mypygui_import\\tools.py"], shell=True))

Startup_bt=CTkLabel(ROOT1, text="\uf4cc", bg_color="#1d2027",text_color="#10b153", anchor="w",font=("JetBrainsMono NFP",25,"bold"))
Startup_bt.pack(side="left",padx=(2,0),pady=(1,0))
Startup_bt.bind("<Button-1>",lambda event:subprocess.Popen([r"cmd /c C:\@delta\ms1\scripts\flask\4999_startup\startup.py"], shell=True))
Startup_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen([r"cmd /c code C:\@delta\ms1\scripts\flask\4999_startup\startup.py"], shell=True))


# ProcessPRLS_bt=CTkLabel(ROOT1, text="\uf4bc", bg_color="#1d2027",text_color="#f04410", anchor="w",font=("JetBrainsMono NFP",25,"bold"))
# ProcessPRLS_bt.pack(side="left",padx=(10,0),pady=(1,0))
# ProcessPRLS_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\ProcessPRLS.py"], shell=True))
# ProcessPRLS_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\ProcessPRLS.py"], shell=True))

AppManagement_bt=CTkLabel(ROOT1, text="\uf40e", bg_color="#1d2027",text_color="#26b2f3", anchor="w",font=("JetBrainsMono NFP",25,"bold"))
AppManagement_bt.pack(side="left",padx=(10,0),pady=(1,0))
AppManagement_bt.bind("<Button-1>",lambda event:subprocess.Popen([r"cmd /c start C:\@delta\ms1\scripts\flask\4998_Applist\applist.py"], shell=True))
AppManagement_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen([r"cmd /c code C:\@delta\ms1\scripts\flask\4998_Applist\applist.py"], shell=True))
AppManagement_bt.bind("<Button-3>",lambda event:subprocess.Popen(["cmd /c start C:\\@delta\\ms1\\scripts\\mypygui_import\\app_store.py"], shell=True))
AppManagement_bt.bind("<Control-Button-3>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\mypygui_import\\app_store.py"], shell=True))

Rclone_bt=CTkLabel(ROOT1, text="\uef2c", font=("JetBrainsMono NFP",25,"bold"), anchor="w", bg_color="#1d2027",text_color="#fcfcfc")
Rclone_bt.pack(side="left",padx=(10,0),pady=(1,0))
Rclone_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\@delta\\ms1\\scripts\\rclone_Script.py"], shell=True))
Rclone_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\rclone_Script.py"], shell=True))

Folder_bt=CTkLabel(ROOT1, text="\ueaf7", font=("JetBrainsMono NFP",25,"bold"), anchor="w", bg_color="#1d2027",text_color="#ffd900")
Folder_bt.pack(side="left",padx=(10,0),pady=(1,0))
Folder_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\mypygui_import\\folder.py"], shell=True))
Folder_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\mypygui_import\\folder.py"], shell=True))

# ScriptList_bt=CTkLabel(ROOT1, text="\uf03a", bg_color="#1d2027",text_color="#e0a04c", anchor="w",font=("JetBrainsMono NFP",20,"bold"))
# ScriptList_bt.pack(side="left",padx=(10,0),pady=(1,0))
# ScriptList_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\mypygui_import\\script_list.py"], shell=True))
# ScriptList_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\mypygui_import\\script_list.py"], shell=True))

# ShortcutBar1=tk.Label(ROOT1, text="\udb80\udfa4",bg="#1d2027",fg="#ed4231",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",20,"bold"))
# ShortcutBar1.pack(side="left",padx=(3,0),pady=(0,0))
# ShortcutBar1.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\python\\bar_1.py"], shell=True))
# ShortcutBar1.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\python\\bar_1.py"], shell=True))

# ShortcutBar2=CTkLabel(ROOT1, text="\udb80\udf11", bg_color="#1d2027",text_color="#d4d654", anchor="w",font=("JetBrainsMono NFP",25,"bold"))
# ShortcutBar2.pack(side="left",padx=(5,0),pady=(1,0))
# ShortcutBar2.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\shortcut.py"], shell=True))
# ShortcutBar2.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\shortcut.py"], shell=True))

# PositionXY_bt=tk.Label(ROOT1, text="\udb83\ude51",bg="#1d2027",fg="#ffffff",height=0,width=0,relief="flat",anchor="w", font=("JetBrainsMono NFP",16,"bold"))
# PositionXY_bt.pack(side="left",padx=(3,0),pady=(0,0))
# PositionXY_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\xy\\XY_FULL.py"], shell=True))
# PositionXY_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\xy\\XY_FULL.py"],shell=True))
# PositionXY_bt.bind("<Button-3>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\xy\\XY_APP.py"], shell=True))
# PositionXY_bt.bind("<Control-Button-3>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\xy\\XY_APP.py"],shell=True))

PositionXY_CrossHair_bt=tk.Label(ROOT1, text="\uf05b",bg="#1d2027",fg="#ffffff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
PositionXY_CrossHair_bt.pack(side="left",padx=(3,0),pady=(0,0))
PositionXY_CrossHair_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\xy\\XY_CroosHair.py"], shell=True))
PositionXY_CrossHair_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\xy\\XY_CroosHair.py"],shell=True))
PositionXY_CrossHair_bt.bind("<Button-3>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\xy\\XY_CroosHairGemini.py"], shell=True))
PositionXY_CrossHair_bt.bind("<Control-Button-3>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\xy\\XY_CroosHairGemini.py"],shell=True))

ColorTool_bt=tk.Label(ROOT1, text="\ue22b",bg="#1d2027",fg="#c588fd",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
ColorTool_bt.pack(side="left",padx=(3,0),pady=(0,0))
ColorTool_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\color\\color_picker.py"], shell=True))
ColorTool_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\color\\color_picker.py"],shell=True))
ColorTool_bt.bind("<Button-3>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\color\\color_pallet_rand_fg_bgFF00.py"], shell=True))
ColorTool_bt.bind("<Control-Button-3>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\color\\color_pallet_rand_fg_bgFF00.py"],shell=True))

Info_lb=tk.Label(ROOT1, text="\udb80\udefc",bg="#1d2027",fg="#ffffff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",20,"bold"))
Info_lb.pack(side="left",padx=(3,3),pady=(0,0))
Info_lb.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\info.py"], shell=True))
Info_lb.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\info.py"], shell=True))
# Info_lb.bind("<Button-1>",lambda event:get_active_window_info())

# wifi_reboot_lb=tk.Label(ROOT1, text="\udb85\udec4",bg="#1d2027",fg="#3ac0ff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",18,"bold"))
# wifi_reboot_lb.pack(side="left",padx=(3,3),pady=(0,0))
# wifi_reboot_lb.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c C:\\@delta\\ms1\\scripts\\Autohtokey\\UIA_v2\\wifi_reboot.ahk"], shell=True))
# wifi_reboot_lb.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\Autohtokey\\UIA_v2\\wifi_reboot.ahk"], shell=True))

# LockBox_lb = tk.Label(ROOT1, bg="#1d2027", fg="#ff0000", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
# LockBox_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
# LockBox_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c "C:\\Program Files\\My Lockbox\\mylbx.exe"'))

VirtualMonitor_lb = tk.Label(ROOT1,text="2nd", bg="#1d2027", fg="#8ab9ff", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
VirtualMonitor_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
VirtualMonitor_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c C:\\@delta\\ms1\\scripts\\2nd_Monitor.py'))
VirtualMonitor_lb.bind("<Control-Button-1>",lambda event=None:subprocess.Popen('cmd /c code C:\\@delta\\ms1\\scripts\\2nd_Monitor.py'))

# ShadowFight3_lb = tk.Label(ROOT1,text="sf3", bg="#1d2027", fg="#cc5907", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
# ShadowFight3_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
# # ShadowFight3_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c start C:\\@delta\\ms1\\SH3\\SH3V2.py'))
# ShadowFight3_lb.bind( "<Button-1>", lambda event=None: run_command(r'python C:\@delta\ms1\scripts\pyautogui\sf3_Lcpu.py'))
# ShadowFight3_lb.bind("<Control-Button-1>",lambda event=None: run_command(r'code C:\@delta\ms1\scripts\pyautogui\sf3_Lcpu.py'))
# ShadowFight3_lb.bind( "<Button-3>", lambda event=None: run_command(r'python C:\@delta\ms1\scripts\pyautogui\sf3_Hcpu.py'))
# ShadowFight3_lb.bind("<Control-Button-3>",lambda event=None: run_command(r'code C:\@delta\ms1\scripts\pyautogui\sf3_Hcpu.py'))

# ollama_lb = tk.Label(ROOT1,text="ollama", bg="#1d2027", fg="#ffffff", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
# ollama_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
# ollama_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c start C:\\@delta\\ms1\\test_project\\ollama-chat-app\\kill_port_8000.py'))
# ollama_lb.bind("<Button-3>",lambda event=None:subprocess.Popen('cmd /c start C:\\@delta\\ms1\\test_project\\ollama-chat-app\\ollama_stop_models.ps1'))
# ollama_lb.bind("<Control-Button-1>",lambda event=None: run_command(r'code C:\@delta\ms1\test_project\ollama-chat-app\server.py'))

path_replace = tk.Label(ROOT1,text="PathR", bg="#1d2027", fg="#86ff45", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
path_replace.pack(side="left", padx=(0, 0), pady=(0, 0))
path_replace.bind("<Button-1>",lambda event=None:subprocess.Popen(r'cmd /c C:\@delta\ms1\path_tracker.py'))
path_replace.bind("<Control-Button-1>",lambda event=None: run_command(r'code C:\@delta\ms1\path_tracker.py'))

Automation = tk.Label(ROOT1, text="AutoM", bg="#1d2027", fg="#ffab2d",
                      height=0, width=0, relief="flat", highlightthickness=0,
                      highlightbackground="#ffffff", anchor="w",
                      font=("JetBrainsMono NFP", 16, "bold"))
Automation.pack(side="left", padx=(0, 0), pady=(0, 0))
Automation.bind("<Button-1>", lambda event=None: subprocess.Popen(
    r'cmd /c game_automation_tool.py',
    cwd=r'C:\@delta\ms1\test_project\Automation',
    shell=True
))
Automation.bind("<Control-Button-1>", lambda event=None: subprocess.Popen(
    r'code game_automation_tool.py',
    cwd=r'C:\@delta\ms1\test_project\Automation',
    shell=True
))

KomoBT = tk.Label(ROOT1, text="KOMO", bg="#1d2027", fg="#8319f5",
                      height=0, width=0, relief="flat", highlightthickness=0,
                      highlightbackground="#ffffff", anchor="w",
                      font=("JetBrainsMono NFP", 16, "bold"))
KomoBT.pack(side="left", padx=(0, 0), pady=(0, 0))
KomoBT.bind("<Button-1>", lambda event=None: subprocess.Popen(
    r'cmd /c komorebi_gui_custom.py',
    cwd=r'C:\@delta\ms1\asset\komorebi',
    shell=True
))
KomoBT.bind("<Control-Button-1>", lambda event=None: subprocess.Popen(
    r'code komorebi_gui_custom.py',
    cwd=r'C:\@delta\ms1\asset\komorebi',
    shell=True
))

AHKPY_BT = tk.Label(ROOT1, text="AHK", bg="#1d2027", fg="#84ff8e",
                      height=0, width=0, relief="flat", highlightthickness=0,
                      highlightbackground="#ffffff", anchor="w",
                      font=("JetBrainsMono NFP", 16, "bold"))
AHKPY_BT.pack(side="left", padx=(0, 0), pady=(0, 0))
AHKPY_BT.bind("<Button-1>", lambda event=None: subprocess.Popen(
    r'cmd /c C:\@delta\ms1\FFFFFFF\ahk_gui_editor.py',
    cwd=r'C:\@delta\ms1\FFFFFFF',
    shell=True
))
AHKPY_BT.bind("<Control-Button-1>", lambda event=None: subprocess.Popen(
    r'code C:\@delta\ms1\FFFFFFF\ahk_gui_editor.py',
    cwd=r'C:\@delta\ms1\FFFFFFF',
    shell=True
))


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

#! Github status
# Define your repositories here
queue = Queue()
repos = [
    {"name": "ms1", "path": "C:\\@delta\\ms1", "label": "ms1"},
    {"name": "db", "path": "C:\\@delta\\db", "label": "db"},
    {"name": "test", "path": "C:\\Users\\nahid\\ms\\test", "label": "test"},
    # {"name": "ms2", "path": "C:\\ms2", "label": "2"},
    # {"name": "ms3", "path": "C:\\ms3", "label": "3"},
    # Add more as needed
]

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

commands = {
    "msBackups": {
        "cmd": "rclone check src dst --fast-list --size-only",
        "src": "C:/@delta/msBackups",
        "dst": "o0:/msBackups",
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
        "dst": "o0:/Pictures/",
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
Download_lb.bind("<Button-1>",None)

Upload_lb=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
Upload_lb.pack(side="left",padx=(3,0 ),pady=(0,0))
Upload_lb.bind("<Button-1>",None)

LB_CPU=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#1b8af1",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_CPU.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_CPU.bind( "<Button-1>", lambda event=None: run_command(r'python C:\@delta\ms1\scripts\killprocess.py'))
LB_CPU.bind("<Control-Button-1>",lambda event=None: run_command(r'code C:\@delta\ms1\scripts\killprocess.py'))
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

Shut_Reboot=CTkButton(ROOT2, text="\udb82\udc20",fg_color="#1d2027",text_color="#fa0000", corner_radius=5,height=10,width=0, anchor="center",font=("JetBrainsMono NFP",25,"bold"))
Shut_Reboot.pack(side="left",padx=(1,1),pady=(0,0))
Shut_Reboot.bind("<Button-1>",force_shutdown)
Shut_Reboot.bind("<Button-3>",force_restart)

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



update_uptime_label()
update_info_labels()
# check_window_topmost()
# Lockbox_update_label(LockBox_lb)
calculate_time_to_appear(start_time)

ROOT.mainloop()