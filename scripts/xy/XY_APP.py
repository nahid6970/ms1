import tkinter as tk
import pyautogui
import threading
import keyboard
import win32gui

def update_position():
    """Continuously update mouse position and window location."""
    while True:
        # Get current mouse position
        x, y = pyautogui.position()
        
        # Get the window under the mouse
        hwnd = win32gui.WindowFromPoint((x, y))
        window_rect = win32gui.GetWindowRect(hwnd)
        window_x, window_y = window_rect[0], window_rect[1]

        # Calculate relative mouse position within the window
        relative_x = x - window_x
        relative_y = y - window_y
        
        # Update the label with relative coordinates
        position_label.config(text=f"X: {relative_x}, Y: {relative_y}")
        
        # Move the window near the mouse pointer
        move_window(x, y)

def move_window(mouse_x, mouse_y):
    """Move the window with a small offset from the mouse position."""
    window_offset_x = 10
    window_offset_y = 20
    screen_width = ROOT.winfo_screenwidth()
    screen_height = ROOT.winfo_screenheight()
    window_width = ROOT.winfo_width()
    window_height = ROOT.winfo_height()
    
    # Calculate the adjusted window position
    x = min(max(mouse_x + window_offset_x, 0), screen_width - window_width)
    y = min(max(mouse_y + window_offset_y, 0), screen_height - window_height)
    
    ROOT.geometry(f"+{x}+{y}")

def close_window(event=None):
    """Close the window when Esc is pressed."""
    ROOT.destroy()

# Initialize the Tkinter root window
ROOT = tk.Tk()
ROOT.title("Mouse Position Tracker")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)  # Remove window borders
ROOT.attributes('-topmost', True)  # Always keep window on top

# Set initial window position at the bottom of the screen
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()
x = 0
y = screen_height - 30
ROOT.geometry(f"+{x}+{y}")

# Bind the Esc key to close the window
ROOT.bind("<Escape>", close_window)

# Create a frame to hold the position label
box1 = tk.Frame(ROOT, bg="#1d2027")
box1.pack(side="right", anchor="center", pady=(0, 0), padx=(0, 0))

# Label to display the mouse position
position_label = tk.Label(box1, text="", bg="#ffffff", fg="#000000", font=("JETBRAINSMONO NF", 10, "bold"))
position_label.pack(side="left")

# Create a separate thread for updating the mouse position
thread = threading.Thread(target=update_position, daemon=True)
thread.start()

# Use the 'esc' key to close the window
keyboard.add_hotkey("esc", close_window)

# Start the Tkinter event loop
ROOT.mainloop()
