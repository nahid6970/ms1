import tkinter as tk
from datetime import datetime
import subprocess
import pyautogui

def rclone_sync(event=None):
    subprocess.Popen(["powershell", "start", "D:\\@git\\ms1\\sync.ps1"])

def windows_terminal(event=None):
    subprocess.Popen(["wt"])

def powertoys_ruler(event=None):
    pyautogui.hotkey('win', 'shift', 'm')

def powertoys_TextExtract(event=None):
    pyautogui.hotkey('win', 'shift', 't')

def capture2text(event=None):
    ROOT.after(3000, pyautogui.hotkey, 'win', 'ctrl', 'alt', 'shift', 'q')

def powertoys_mouse_crosshair(event=None):
    pyautogui.hotkey('win', 'alt', 'p')

def stop_wsa(event=None):
    subprocess.Popen(["powershell", "Stop-Process -Name WsaClient -Force"])

def close_window(event=None):
    ROOT.destroy()



ROOT = tk.Tk()
ROOT.title("Utility Buttons")
ROOT.attributes('-topmost', True) 
ROOT.overrideredirect(True)
ROOT.configure(bg="#282c34")

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

BORDER_FRAME = create_custom_border(ROOT)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = 0
y = screen_height - 308

ROOT.geometry(f"40x260+{x}+{y}")  

button_frame = tk.Frame(ROOT, bg="#1d2027", width=1, height=0)
button_frame.pack(side="top", padx=1, pady=10, fill="both")

def create_label(text, command, bg_color, fg_color, initial_color, release_color, anchor="center", side="left", width=10, height=1, font=("Arial", 12), relief="flat", highlight_color="#FFFFFF", highlight_thickness=0, padx=(0,0), pady=(0,0)):
    label = tk.Label(button_frame, text=text, bg=bg_color, fg=fg_color, width=width, height=height, font=font, relief=relief, highlightcolor=highlight_color, highlightthickness=highlight_thickness)
    label.pack(side=side, anchor=anchor, padx=padx, pady=pady)
    label.bind("<Button-1>", lambda event, l=label, ic=initial_color, c=command: on_click(l, ic, c))
    label.bind("<ButtonRelease-1>", lambda event, l=label, rc=release_color: on_release(l, rc))
    return label

def on_click(label, initial_color, command):
    label.config(bg=initial_color)
    if command:
        command()

def on_release(label, release_color):
    label.config(bg=release_color)

button_properties = [
("❌",  close_window             ,"#1d2027", "#FF0000", "#1d2027", "#1d2027", "center", "top", 10, 1, ("Arial",16), "flat", "#FFFFFF", 0,(0,0), (0,0)),
("📏",  powertoys_ruler          ,"#1d2027", "#FFFFFF", "#1d2027", "#1d2027", "center", "top", 10, 1, ("Arial",16), "flat", "#FFFFFF", 0,(0,0), (0,0)),
("🐭",  powertoys_mouse_crosshair,"#1d2027", "#FFFFFF", "#1d2027", "#1d2027", "center", "top", 10, 1, ("Arial",16), "flat", "#FFFFFF", 0,(0,0), (0,0)),
("📝",  powertoys_TextExtract    ,"#1d2027", "#FFFFFF", "#1d2027", "#1d2027", "center", "top", 10, 1, ("Arial",16), "flat", "#FFFFFF", 0,(0,0), (0,0)),
("📝",  capture2text             ,"#1d2027", "#db1725", "#1d2027", "#1d2027", "center", "top", 10, 1, ("Arial",16), "flat", "#FFFFFF", 0,(0,0), (0,0)),
("♾️",  rclone_sync              ,"#1d2027", "#3bda00", "#1d2027", "#1d2027", "center", "top", 10, 1, ("Arial",16), "flat", "#FFFFFF", 0,(0,0), (0,0)),
("💻",  windows_terminal         ,"#1d2027", "#FFFFFF", "#1d2027", "#1d2027", "center", "top", 10, 1, ("Arial",16), "flat", "#FFFFFF", 0,(0,0), (0,0)),
("📵",  stop_wsa                 ,"#1d2027", "#FF0000", "#1d2027", "#1d2027", "center", "top", 10, 1, ("Arial",16), "flat", "#FFFFFF", 0,(0,0), (0,0))
]

labels = []
for props in button_properties:
    label = create_label(*props)
    labels.append(label)

ROOT.mainloop()
