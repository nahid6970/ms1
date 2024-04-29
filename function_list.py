from datetime import datetime
from PIL import Image, ImageTk
from pyadl import ADLManager
from time import strftime
# from tkinter import Canvas, Scrollbar
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
import win32gui
import win32process


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


def calculate_time_to_appear(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to appear: {elapsed_time:.2f} seconds")
start_time = time.time()


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

def long_running_function():
    time.sleep(0)
    print("Function completed!")
long_running_function()

set_console_title("🔥")

ROOT = tk.Tk()
ROOT.title("Python GUI")
# ROOT.attributes('-topmost', True)  # Set always on top
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)
ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width//2 - 1920//2
y = screen_height-47-37
ROOT.geometry(f"1920x39+{x}+{y}") #! overall size of the window


#! Resize Window
def toggle_window_size(size):
    global window_state
    global x
    global y
    if size == 'line':
        ROOT.geometry('1920x39')
        x = screen_width // 2 - 1920 // 2
        y = screen_height-47-37
        ROOT.configure(bg='red')
        LB_L.config(text='\ueab7', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("JetBrainsMono NF", 16, "bold"))
        LB_M.config(text='\uea72', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("JetBrainsMono NF", 18, "bold"))
    elif size == 'max':
        ROOT.geometry('1920x140')
        x = screen_width // 2 - 1920 // 2
        y = screen_height-47-37
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

window_size_state = 'line'
#! keyboard.add_hotkey('win+x', on_windows_x_pressed)
# x = screen_width//2 - 753//2
# y = 0
# ROOT.geometry(f"+{x}+{y}")

# Create main frame
MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=800, height=800)
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1, expand=True)

#! Close Window
def close_window(event=None):
    ROOT.destroy()


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