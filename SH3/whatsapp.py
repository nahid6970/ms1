import datetime
import subprocess
import sys
import time
import pyautogui
import pygetwindow as gw
import random
import threading
from tkinter import Tk, Button
import win32gui
# from ctypes import windll, c_char_p, c_buffer
# from struct import calcsize, pack
# from PIL import Image
# from PIL import Image, ImageDraw
import os
# from tkinter import messagebox
import tkinter as tk

# Path to the shortcut file
shortcut_path = r'C:\Users\nahid\OneDrive\Desktop\WhatsApp - Shortcut.lnk'

# Use os.startfile to open the shortcut
os.startfile(shortcut_path)


ROOT = tk.Tk()
ROOT.title("Utility Buttons")
ROOT.attributes('-topmost', True) 
ROOT.overrideredirect(True)
ROOT.configure(bg="#282c34")

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="#66fd1f")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

BORDER_FRAME = create_custom_border(ROOT)
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()
x = screen_width - 60
y = screen_height - 800
ROOT.geometry(f"+{x}+{y}")

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

# find_image
error_count = 0  # Initialize the error counter
def find_image(image_path, confidence=0.7):
    """Find the location of the image on the screen and show time in 12-hour format."""
    global error_count
    output_file = r"C:\Users\nahid\OneDrive\backup\shadowfight3\output.txt"
    def get_current_time():
        """Return the current time in 12-hour format."""
        return datetime.datetime.now().strftime("%I:%M:%S %p")
    def log_output(message):
        """Save output message to file."""
        with open(output_file, 'a') as file:
            file.write(f"{get_current_time()} - {message}\n")
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
        if location:
            image_name = os.path.basename(image_path)
            message = f"Found image: {image_name}"
            print(f"{get_current_time()} - {message}")
            log_output(message)
            return location
    except Exception as e:
        error_count += 1
        error_message = f"{error_count} times not found. Error: {e}"
        print(f"{get_current_time()} - {error_message}")
        log_output(error_message)
    return None

# focus_window
def focus_window(window_title):
    """Set focus to the window with the given title."""
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        window = windows[0]
        window.activate()
        return window
    return None

def get_window_rect(hwnd):
    """Get the window's position and size."""
    rect = win32gui.GetWindowRect(hwnd)
    return rect  # Returns (left, top, right, bottom)

# press_buttons_with_delays
def press_screen_with_delays(window, *args):
    """Press buttons at specified x, y locations with delays, relative to the window's position.
    Usage: press_buttons_with_delays(window, (100, 200, 2), (150, 250, 3), (300, 400, 2))
    """
    if len(args) == 0:
        raise ValueError("At least one (x, y, delay) tuple is required.")
    # Activate the window
    window.activate()
    # Get the window handle (HWND) using the window title
    hwnd = win32gui.FindWindow(None, window.title)
    if not hwnd:
        raise ValueError("Could not find window with the specified title.")
    # Get the window's position (top-left corner)
    window_rect = get_window_rect(hwnd)
    window_x, window_y = window_rect[0], window_rect[1]
    for i in range(len(args)):
        if len(args[i]) != 3:
            raise ValueError("Each argument should be a tuple (x, y, delay).")
        x, y, delay = args[i]
        # Adjust x, y coordinates to be relative to the window's position
        adjusted_x = window_x + x
        adjusted_y = window_y + y
        # Click at the given coordinates relative to the window
        pyautogui.click(adjusted_x, adjusted_y)
        # Wait for the specified delay before the next action
        time.sleep(delay)

# window title
window_title='WhatsApp'

profile_pic=r'C:\Users\nahid\OneDrive\backup\whatsapp_notify\image_59.png'
call_me=r'C:\Users\nahid\OneDrive\backup\whatsapp_notify\image_60.png'

def close_window(event=None):
    # Close the current window
    ROOT.destroy()
    # Start the specified script
    script_path = r"C:\ms1\SH3\SH3V2__AHK.py"
    subprocess.Popen([sys.executable, script_path])

def WhatsPhotoClick():
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while True:  # Loop will continue indefinitely unless interrupted by an external condition
            focus_window(window_title)

            # Check for profile_pic image and click
            if find_image(profile_pic): 
                press_screen_with_delays(window, (94, 181, 2))
            # Check for call_me image and click
            elif find_image(call_me, confidence=0.8): 
                press_screen_with_delays(window, (835, 71, 2))

            time.sleep(0.1)  # Small delay between iterations to reduce CPU usage

    except KeyboardInterrupt:
        print("Script stopped by user.")


WhatsPhotoClick()

ROOT.mainloop()