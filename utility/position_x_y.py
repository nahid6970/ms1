import tkinter as tk
import pyautogui

def update_position():
    x, y = pyautogui.position()
    position_label.config(text=f"X: {x}, Y: {y}")
    ROOT.after(1000, update_position)  # Schedule the update every 1000 milliseconds (1 second)

# Create the main window
ROOT = tk.Tk()
ROOT.title("Mouse Position Tracker")



def close_window(event=None):
    ROOT.destroy()
ROOT.attributes('-topmost', True)
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()
x = 242
y = 7
ROOT.geometry(f"+{x}+{y}")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)
box1 = tk.Frame(ROOT, bg="#1d2027")
box1.pack(side="right", anchor="center", pady=(0,0),padx=(0,0))




position_label = tk.Label(box1, text="", bg="#8de2d3", fg="#000000", font=("JETBRAINSMONO NF", 10, "bold"))
position_label.pack(side="left")
LB_name = tk.Label(box1, bg="#ff0000", fg="#FFFFFF", font=("JetBrainsMono NF", 10, "bold"), text="X")
LB_name.pack(side="left")
LB_name.bind("<Button-1>", close_window)



update_position()
ROOT.mainloop()
