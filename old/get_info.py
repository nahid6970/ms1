import tkinter as tk
import win32gui
import win32process
import psutil
import time

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

root = tk.Tk()
root.title("")

button = tk.Button(root, text="Get_Info", command=get_active_window_info)
button.pack()

root.mainloop()
