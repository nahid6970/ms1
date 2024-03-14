import importlib
import subprocess
from datetime import datetime
from PIL import Image, ImageTk
from pyadl import ADLManager
from time import strftime
from tkinter import Canvas, Scrollbar
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import ctypes
import keyboard
import os
import psutil
import pyautogui
import subprocess
import sys
import threading
import time
import tkinter as tk


def calculate_time_to_appear(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to appear: {elapsed_time:.2f} seconds")

start_time = time.time()

# Print ASCII art in the console
print(r"""

$$\   $$\           $$\       $$\       $$\ $$\   $$\  $$$$$$\
$$$\  $$ |          $$ |      \__|      $$ |$$$\  $$ |$$  __$$\
$$$$\ $$ | $$$$$$\  $$$$$$$\  $$\  $$$$$$$ |$$$$\ $$ |$$ /  $$ |
$$ $$\$$ | \____$$\ $$  __$$\ $$ |$$  __$$ |$$ $$\$$ |$$$$$$$$ |
$$ \$$$$ | $$$$$$$ |$$ |  $$ |$$ |$$ /  $$ |$$ \$$$$ |$$  __$$ |
$$ |\$$$ |$$  __$$ |$$ |  $$ |$$ |$$ |  $$ |$$ |\$$$ |$$ |  $$ |
$$ | \$$ |\$$$$$$$ |$$ |  $$ |$$ |\$$$$$$$ |$$ | \$$ |$$ |  $$ |
\__|  \__| \_______|\__|  \__|\__| \_______|\__|  \__|\__|  \__|

""")

# Vaiables to track the position of the mouse when clicking​⁡
drag_data = {"x": 0, "y": 0}

def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def stop_drag(event):
    drag_data["x"] = None
    drag_data["y"] = None

def do_drag(event):
    if drag_data["x"] is not None and drag_data["y"] is not None:
        x, y = (event.x - drag_data["x"] + ROOT.winfo_x(), event.y - drag_data["y"] + ROOT.winfo_y())
        ROOT.geometry("+%s+%s" % (x, y))

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

# Create main window
ROOT = tk.Tk()
ROOT.title("Folder")
ROOT.attributes('-topmost', True)  # Set always on top
# ROOT.geometry("520x800")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)  # Remove default borders

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Add bindings to make the window movable
ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width - 400
y = screen_height//2 - 600//2
ROOT.geometry(f"400x600+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=400, height=600) #!
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1)  # Add some padding at the top
MAIN_FRAME.pack(expand=True)


#! Close Window
def close_window(event=None):
    ROOT.destroy()

#!? Main ROOT BOX
ROOT1 = tk.Frame(ROOT, bg="#1d2027")
ROOT1.pack(side="right", anchor="ne", pady=(3,2),padx=(3,1))

def create_label(text, parent, bg, fg, width, height, relief, font, ht, htc, padx, pady, anchor, row, column, rowspan, columnspan):
    label = tk.Label(parent, text=text, bg=bg, fg=fg, width=width, height=height, relief=relief, font=font, highlightthickness=ht, highlightbackground=htc)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky=anchor, rowspan=rowspan, columnspan=columnspan)
    return label

label_properties = [
{"text": "r","parent": ROOT1,"bg": "#1d2027","fg": "#ff0000","width": 0  ,"height": "0","relief": "flat","font": ("Webdings",10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,2) ,"pady": (0,0),"anchor": "w","row": 1,"column": 1 ,"rowspan": 1,"columnspan": 1},#! LB_X alternative wingdings x
]
labels = [create_label(**prop) for prop in label_properties]
LB_XXX, = labels
LB_XXX.bind("<Button-1>", close_window)





#! Folder
def create_button(text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button,sticky, padx_button, pady_button, padx_pack, pady_pack, command):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack, sticky=sticky)
    return button

BOX_1 = tk.Frame(MAIN_FRAME, bg="#282c34")
BOX_1.pack(side="top", pady=(30,0), padx=(0,0))

button_properties = [
("All Apps"      , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 0 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","shell:AppsFolder"], shell=True)                                                                     ),
("AppData"       , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 1 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData"], shell=True)                                                            ),
("Git Projects"  , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 2 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\OneDrive\\Git"], shell=True)                                                      ),
("Packages"      , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 3 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Local\\Packages"], shell=True)                                           ),
("ProgramData"   , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 4 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","C:\\ProgramData"], shell=True)                                                                      ),
("Scoop"         , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 5 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\scoop"], shell=True)                                                              ),
("Software"      , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 6 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","D:\\software"], shell=True)                                                                         ),
("Song"          , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 7 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","D:\\song"], shell=True)                                                                             ),
("WindowsApp"    , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 8 , 1, 1, 2, "ew"  , 0, 0, (0, 0), (0, 0), lambda: subprocess.Popen(["explorer","C:\\Program Files\\WindowsApps"], shell=True)                                                       ),
("Startup System", BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 9 , 1, 1, 1, "nsew", 0, 0, (0, 1), (3, 0), lambda: subprocess.Popen(["explorer","C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"], shell=True)                   ),
("Startup User"  , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 9 , 2, 1, 1, "nsew", 0, 0, (1, 0), (3, 0), lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"], shell=True)),
("Temp-AppDate"  , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 10, 1, 1, 1, "nsew", 0, 0, (0, 1), (3, 0), lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Local\\Temp"], shell=True)                                               ),
("Temp-Windows"  , BOX_1, "#ffd86a", "#1D2027", 1, 0, "flat", ("calibri", 14, "bold"), 10, 2, 1, 1, "nsew", 0, 0, (1, 0), (3, 0), lambda: subprocess.Popen(["explorer","C:\\Windows\\Temp"], shell=True)                                                                    ),
]
for button_props in button_properties:
    create_button(*button_props)


#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
