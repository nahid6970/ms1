import tkinter as tk
import win32gui
import time

def get_active_window_name():
    # Wait for 2 seconds
    time.sleep(2)
    
    # Get the position of the mouse cursor
    pos = win32gui.GetCursorPos()
    
    # Get the handle of the window under the cursor
    hwnd = win32gui.WindowFromPoint(pos)
    
    # Get the title (name) of the window
    window_text = win32gui.GetWindowText(hwnd)
    
    print("Active Window Name:", window_text)

def create_button():
    button = tk.Button(root, text="Get Active Window Name", command=get_active_window_name)
    button.pack()

root = tk.Tk()
root.title("Get Active Window Name")
create_button()
root.mainloop()
