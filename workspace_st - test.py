import tkinter as tk
import ctypes
import psutil
from datetime import datetime

# Define RECT structure
class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]

# Function to get CPU usage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Function to get system uptime
def get_system_uptime():
    uptime_seconds = psutil.boot_time()
    current_time = datetime.now().timestamp()
    uptime = current_time - uptime_seconds
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(hours), int(minutes), int(seconds)

# Function to format uptime
def format_uptime():
    hours, minutes, seconds = get_system_uptime()
    return f"\u25b6 {hours:02d}:{minutes:02d}:{seconds:02d}"  # Unicode symbol for right-pointing triangle bullet

# Function to update the uptime label
def update_uptime_label():
    uptime_str = format_uptime()
    uptime_label.config(text=uptime_str)
    uptime_label.after(1000, update_uptime_label)

# Function to make the window stay on top and adjust work area
def adjust_work_area():
    # Set the window always on top
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0003)
    
    # Adjust the work area to exclude the 30px at the top
    SPI_SETWORKAREA = 47
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETWORKAREA, 0, ctypes.byref(rect), 0)

# Function to reset the work area when the program closes
def reset_work_area():
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETWORKAREA, 0, ctypes.byref(original_rect), 0)

# Create the main window
root = tk.Tk()
root.overrideredirect(True)  # Remove window decorations
root.geometry('1920x30+0+0')  # Full width of the screen, height 30px, top-left corner

# Save the original work area
rect = RECT()
SPI_GETWORKAREA = 48
ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)

# Adjust the work area to exclude the 30px at the top
original_rect = RECT(rect.left, rect.top, rect.right, rect.bottom)
rect.top += 30
adjust_work_area()

# Ensure the window stays on top and update the status bar
root.after(100, adjust_work_area)

# Create a label to display the CPU usage
status_label = tk.Label(root, text="Initializing...", font=("Helvetica", 12), bg="black", fg="white")
status_label.pack(side="left", padx=(10, 5), pady=(1, 0))

# Create a label to display system uptime
uptime_label = tk.Label(root, text="", font=("Helvetica", 12), bg="black", fg="white")
uptime_label.pack(side="right", padx=(5, 10), pady=(1, 0))

# Function to update both labels
def update_labels():
    cpu_usage = get_cpu_usage()
    status_label.config(text=f"CPU Usage: {cpu_usage}%")
    uptime_str = format_uptime()
    uptime_label.config(text=uptime_str)
    root.after(1000, update_labels)

# Update labels initially and start updating them periodically
update_labels()

# Reset work area when closing
def on_closing():
    reset_work_area()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the main loop
root.mainloop()
