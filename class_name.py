import tkinter as tk
import win32gui
import time

def get_active_window_class():
    # Wait for 2 seconds
    time.sleep(2)
    
    # Get the position of the mouse cursor
    pos = win32gui.GetCursorPos()
    
    # Get the handle of the window under the cursor
    hwnd = win32gui.WindowFromPoint(pos)
    
    # Get the class name of the window
    class_name = win32gui.GetClassName(hwnd)
    
    print("Active Window Class:", class_name)

def create_button():
    button = tk.Button(root, text="Get Active Window Class", command=get_active_window_class)
    button.pack()

root = tk.Tk()
root.title("Get Active Window Class")
create_button()
root.mainloop()
