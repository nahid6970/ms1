import tkinter as tk
from datetime import datetime
import subprocess
import pyautogui
# import ctypes

def rclone_sync(event=None):
    subprocess.Popen(["powershell", "start", "D:\\@git\\ms1\\sync.ps1"])

def windows_terminal(event=None):
    subprocess.Popen(["wt"])

def powertoys_ruler(event=None):
    pyautogui.hotkey('win', 'shift', 'm')

def powertoys_TextExtract(event=None):
    pyautogui.hotkey('win', 'shift', 't')

def capture2text(event=None):
    # Define the capture2text function with a delay
    ROOT.after(3000, pyautogui.hotkey, 'win', 'ctrl', 'alt', 'shift', 'q')

def powertoys_mouse_crosshair(event=None):
    pyautogui.hotkey('win', 'alt', 'p')

# def set_console_title(title):
#     ctypes.windll.kernel32.SetConsoleTitleW(title)

def close_window(event=None):
    ROOT.destroy()

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


#! set_console_title("1")
# Create the main Tkinter window
ROOT = tk.Tk()
ROOT.title("Utility Buttons")
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
y = screen_height - 288

ROOT.geometry(f"50x240+{x}+{y}")  # Overall size of the window

# Create a frame for the buttons
button_frame = tk.Frame(ROOT, bg="#1d2027", width=1, height=0)
button_frame.pack(side="top", padx=1, pady=10, fill="both")


# Define button texts, commands, background colors, and foreground colors
button_texts          = ["❌"        ,"📏"         ,"🖱"                   ,"📝"               ,"📝"      ,"♾️"     ,"💻"          ]
button_commands       = [close_window,powertoys_ruler,powertoys_mouse_crosshair,powertoys_TextExtract,capture2text,rclone_sync,windows_terminal]
bg_colors             = ["#1d2027"   ,"#1d2027"      ,"#1d2027"                ,"#1d2027"            ,"#1d2027"   ,"#1d2027"  ,"#1d2027"       ]
fg_colors             = ["#FF0000"   ,"#FFFFFF"      ,"#FFFFFF"                ,"#FFFFFF"            ,"#db1725"   ,"#3bda00"  ,"#FFFFFF"       ]
initial_colors        = ["#1d2027"   ,"#1d2027"      ,"#1d2027"                ,"#1d2027"            ,"#1d2027"   ,"#1d2027"  ,"#1d2027"       ]
release_colors        = ["#1d2027"   ,"#1d2027"      ,"#1d2027"                ,"#1d2027"            ,"#1d2027"   ,"#1d2027"  ,"#1d2027"       ]
anchors               = ["center"    ,"center"       ,"center"                 ,"center"             ,"center"    ,"center"   ,"center"        ]
sides                 = ["top"       ,"top"          ,"top"                    ,"top"                ,"top"       ,"top"      ,"top"           ]
widths                = [10          ,10             ,10                       ,10                   ,10          ,10         ,10              ]
heights               = [1           ,1              ,1                        ,1                    ,1           ,1          ,1               ]
reliefs               = ["flat"      ,"flat"         ,"flat"                   ,"flat"               ,"flat"      ,"flat"     ,"flat"          ]
highlight_colors      = ["#FFFFFF"   ,"#FFFFFF"      ,"#FFFFFF"                ,"#FFFFFF"            ,"#FFFFFF"   ,"#FFFFFF"  ,"#FFFFFF"       ]
highlight_thicknesses = [0           ,0              ,0                        ,0                    ,0           ,0          ,0               ]
padx_values           = [(0, 0),     (0, 0),           (0, 0),                   (0, 0),                 (0, 0),       (0, 0),      (0, 0)]
pady_values           = [(0, 0),     (0, 0),           (0, 0),                   (0, 0),                 (0, 0),       (0, 0),      (0, 0)]
font_styles           = [("Arial", 16), ("Arial", 16), ("Arial", 16), ("Arial", 16), ("Arial", 16), ("Arial", 16), ("Arial", 16)]

# Create individual labels
labels = []
for text, command, bg_color, fg_color, initial_color, release_color, anchor, side, width, height, font_style, relief, highlight_color, highlight_thickness, padx_val, pady_val in zip(button_texts, button_commands, bg_colors, fg_colors, initial_colors, release_colors, anchors, sides, widths, heights, font_styles, reliefs, highlight_colors, highlight_thicknesses, padx_values, pady_values):
    label = create_label(text, command, bg_color, fg_color, initial_color, release_color, anchor, side, width, height, font_style, relief, highlight_color, highlight_thickness, padx_val, pady_val)
    labels.append(label)

ROOT.mainloop()
