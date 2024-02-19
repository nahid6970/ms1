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


# # Calculate the screen width and height
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = 0
y = screen_height - 162

ROOT.geometry(f"50x130+{x}+{y}") #! overall size of the window


# Create a frame for the buttons
button_frame = tk.Frame(ROOT, bg="#1d2027", width=1, height=0)
button_frame.pack(side="top", padx=1, pady=10, fill="both")

# Create the buttons
buttons = [
    {"text": "❌", "command": close_window},
    {"text": "📏", "command": powertoys_ruler},
    {"text": "🖱", "command": powertoys_mouse_crosshair},
    {"text": "📝", "command": powertoys_TextExtract},
    {"text": "♾️", "command": rclone_sync},
    {"text": "💻", "command": windows_terminal},
]

for button_info in buttons:
    button = tk.Label(button_frame, text=button_info["text"], bg="#1d2027", fg="#FFFFFF", height=0, width=0,
                      relief="flat", highlightthickness=1, highlightbackground="#1d2027", padx=0, pady=0,
                      font=("ink free", 10), cursor="hand2")
    button.pack(side="top", padx=(0, 0))
    button.bind("<Button-1>", button_info["command"])

ROOT.mainloop()

