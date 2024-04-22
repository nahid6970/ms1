import tkinter as tk
import pyautogui
import threading

def update_position():
    while True:
        x, y = pyautogui.position()
        position_label.config(text=f"X: {x}, Y: {y}")
        move_window(x, y)

def move_window(mouse_x, mouse_y):
    window_offset = 10
    screen_width = ROOT.winfo_screenwidth()
    screen_height = ROOT.winfo_screenheight()
    window_width = ROOT.winfo_width()
    window_height = ROOT.winfo_height()
    
    # Calculate the adjusted window position
    x = min(max(mouse_x, 0), screen_width - window_width)
    y = min(max(mouse_y + window_offset, 0), screen_height - window_height)
    
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

position_label = tk.Label(box1, text="", bg="#8de2d3", fg="#000000", font=("JETBRAINSMONO NF", 10, "bold"))
position_label.pack(side="left")

# LB_name = tk.Label(box1, bg="#ff0000", fg="#FFFFFF", font=("JetBrainsMono NF", 10, "bold"), text="X")
# LB_name.pack(side="left")
# LB_name.bind("<Button-1>", close_window)

# Create a separate thread for updating the window position
thread = threading.Thread(target=update_position, daemon=True)
thread.start()

ROOT.mainloop()
