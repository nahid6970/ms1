import tkinter as tk
import ctypes
import psutil

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

# Function to update the status bar with CPU usage
def update_status_bar():
    cpu_usage = get_cpu_usage()
    status_label.config(text=f"CPU Usage: {cpu_usage}%")
    root.after(1000, update_status_bar)

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

# Create a label to display the CPU usage
status_label = tk.Label(root, text="Initializing...", font=("Helvetica", 12), bg="black", fg="white")
status_label.pack(fill=tk.BOTH, expand=True)

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
update_status_bar()

# Reset work area when closing
def on_closing():
    reset_work_area()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the main loop
root.mainloop()
