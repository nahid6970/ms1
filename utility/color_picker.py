import tkinter as tk
import pyautogui
import pyperclip
import keyboard

def update_color():
    x, y = pyautogui.position()
    color = pyautogui.screenshot().getpixel((x, y))
    hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
    color_label.config(text=f"Color: {hex_color}", bg=hex_color)
    color_label_white.config(text=f"Color: {hex_color}", bg=hex_color)
    ROOT.after(100, update_color)

def copy_color():
    color_text = color_label.cget("text")
    hex_color = color_text.split(": ")[1]
    pyperclip.copy(hex_color)

ROOT = tk.Tk()
ROOT.title("Color Picker")
ROOT.configure(bg="#282c34")
ROOT.attributes('-topmost', True)
ROOT.overrideredirect(True)
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()
x = 242
y = 7
ROOT.geometry(f"+{x}+{y}")

def close_window(event=None):
    ROOT.destroy()

box1 = tk.Frame(ROOT, bg="#1d2027")
box1.pack(side="right", anchor="center", pady=(0,0),padx=(0,0))

color_label_white = tk.Label(box1, text="Color: ", font=("JetBrainsMono NF", 10, "bold"), fg="white", bg="#1d2027")
color_label_white.pack(side="left")

color_label = tk.Label(box1, text="Color: ", font=("JetBrainsMono NF", 10, "bold"), fg="black", bg="#1d2027")
color_label.pack(side="left")

LB_x = tk.Label(box1, bg="#ff0000", fg="#FFFFFF", font=("JetBrainsMono NF", 10, "bold"), text="X")
LB_x.pack(side="left")
LB_x.bind("<Button-1>", close_window)

update_color()
keyboard.add_hotkey("ctrl+space", copy_color)
print("Hotkey registered")

ROOT.mainloop()
