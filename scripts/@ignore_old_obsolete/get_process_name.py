import tkinter as tk
import win32gui
import win32process
import psutil
import time

def get_active_window_process_name():
    # Wait for 2 seconds
    time.sleep(2)
    
    # Get the position of the mouse cursor
    pos = win32gui.GetCursorPos()
    
    # Get the handle of the window under the cursor
    hwnd = win32gui.WindowFromPoint(pos)
    
    # Get the process ID (PID) of the window
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    # Get the process name associated with the PID
    process_name = psutil.Process(pid).name()
    
    print("Active Window Process Name:", process_name)

def create_button():
    button = tk.Button(root, text="Get Active Window Process Name", command=get_active_window_process_name)
    button.pack()

root = tk.Tk()
root.title("Get Active Window Process Name")
create_button()
root.mainloop()
