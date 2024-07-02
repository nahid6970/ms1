import tkinter as tk
import pyautogui
import threading
import keyboard
import pygetwindow as gw

def update_position():
    while True:
        try:
            # Get the currently active window
            active_window = gw.getActiveWindow()
            if active_window:
                win_x, win_y = active_window.topleft
                win_width, win_height = active_window.size

                # Get the mouse position
                mouse_x, mouse_y = pyautogui.position()

                # Calculate the mouse position relative to the active window
                rel_x = mouse_x - win_x
                rel_y = mouse_y - win_y

                # Update the label with the relative position
                position_label.config(text=f"X: {rel_x}, Y: {rel_y}")

                # Move the tracking window
                move_window(mouse_x, mouse_y)
        except Exception as e:
            print(f"Error: {e}")

def move_window(mouse_x, mouse_y):
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
    ROOT.destroy()

ROOT = tk.Tk()
ROOT.title("Mouse Position Tracker")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)
ROOT.attributes('-topmost', True)
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()
x = 0
y = screen_height - 30
ROOT.geometry(f"+{x}+{y}")
ROOT.bind("<Escape>", close_window)

box1 = tk.Frame(ROOT, bg="#1d2027")
box1.pack(side="right", anchor="center", pady=(0, 0), padx=(0, 0))

position_label = tk.Label(box1, text="", bg="#ffffff", fg="#000000", font=("JETBRAINSMONO NF", 10, "bold"))
position_label.pack(side="left")

# Create a separate thread for updating the window position
thread = threading.Thread(target=update_position, daemon=True)
thread.start()
keyboard.add_hotkey("esc", close_window)

ROOT.mainloop()
