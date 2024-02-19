import tkinter as tk
from datetime import datetime
import subprocess
import pyautogui
import ctypes

def rclone_sync(event=None):
    subprocess.Popen(["powershell", "start", "D:\\@git\\ms1\\sync.ps1"])

def windows_terminal(event=None):
    subprocess.Popen(["wt"])

def powertoys_ruler(event=None):
    pyautogui.hotkey('win', 'shift', 'm')

def powertoys_TextExtract(event=None):
    pyautogui.hotkey('win', 'shift', 't')

def powertoys_mouse_crosshair(event=None):
    pyautogui.hotkey('win', 'alt', 'p')

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def close_window(event=None):
    ROOT.destroy()

def create_button(text, command, bg_color, fg_color):
    button = tk.Label(button_frame, text=text, bg=bg_color, fg=fg_color, height=0, width=0,
                      relief="flat", highlightthickness=1, highlightbackground="#1d2027", padx=0, pady=0,
                      font=("ink free", 10), cursor="hand2")
    button.pack(side="top", padx=(0, 0))
    button.bind("<Button-1>", command)

set_console_title("1")
# Create the main Tkinter window
ROOT = tk.Tk()
ROOT.title("Utility Buttons")
ROOT.geometry("50x130")
ROOT.attributes('-topmost', True)  # Set always on top
ROOT.overrideredirect(True)  # Remove default borders
ROOT.configure(bg="#282c34")

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

BORDER_FRAME = create_custom_border(ROOT)

# Calculate the screen width and height
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = 0
y = screen_height - 178

ROOT.geometry(f"50x130+{x}+{y}")  # Overall size of the window

# Create a frame for the buttons
button_frame = tk.Frame(ROOT, bg="#1d2027", width=1, height=0)
button_frame.pack(side="top", padx=1, pady=10, fill="both")

# Define button texts, commands, background colors, and foreground colors
button_texts = ["❌", "📏", "🖱", "📝", "♾️", "💻"]
button_commands = [close_window, powertoys_ruler, powertoys_mouse_crosshair, powertoys_TextExtract, rclone_sync, windows_terminal]
bg_colors = ["#1d2027", "#1d2027", "#1d2027", "#1d2027", "#1d2027", "#1d2027"]
fg_colors = ["#FF0000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#3bda00", "#FFFFFF"]

# Create individual buttons
for text, command, bg_color, fg_color in zip(button_texts, button_commands, bg_colors, fg_colors):
    create_button(text, command, bg_color, fg_color)

ROOT.mainloop()
