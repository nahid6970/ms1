import argparse
import subprocess
import tkinter as tk
from tkinter import ttk
import keyboard
import pygetwindow as gw
import time
from idlelib.tooltip import Hovertip
import pyautogui
from tkinter import *
from tkinter.ttk import *
from Reference import *

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

root = tk.Tk()
root.title("Shortcut Labels")
root.attributes('-topmost', True)
root.overrideredirect(True)  # Remove default borders
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"800x500")

default_font = ("Jetbrainsmono nfp", 14, "bold")
root.option_add("*Font", default_font)

def on_enter(event):
    event.widget.configure(style='Hover.TLabel')

def on_leave(event):
    event.widget.configure(style='Custom.TLabel')

def on_mouse_wheel(event):
    # Scroll vertically based on the wheel movement
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

main_frame = tk.Frame(root, bg="#1d2027")
main_frame.pack(fill='both', expand=True)

# Create the container frame for the canvas and scrollbar
container_frame = tk.Frame(root)
container_frame.pack(fill='both', expand=True)
# Create a canvas widget
canvas = tk.Canvas(container_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# Create a vertical scrollbar linked to the canvas
scrollbar = tk.Scrollbar(container_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill='y')
# Create a frame to hold the labels and place it on the canvas
vscode_window = tk.Frame(canvas, bg="#1D2027")
vscode_window.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
# Create an anchor frame to be placed on the canvas
canvas.create_window((0, 0), window=vscode_window, anchor="nw")
# Configure the scrollbar to control the canvas
canvas.configure(yscrollcommand=scrollbar.set)
root.bind_all("<MouseWheel>", on_mouse_wheel)

# Create a style object
style = ttk.Style()
# Configure a custom style for TLabel
style.configure('Custom.TLabel', 
                font=('Jetbrainsmono nfp', 12, 'italic'), 
                background='lightgrey', 
                foreground='darkblue', 
                borderwidth=2, 
                relief='solid',
                padding=(10, 5),
                width=20,
                anchor='center')
# Configure a hover style
style.configure('Hover.TLabel', 
                font=('Jetbrainsmono nfp', 12, 'italic'), 
                background='Black', 
                foreground='Green', 
                borderwidth=2, 
                relief='solid',
                padding=(10, 5),
                width=20,
                anchor='center')

# Create labels with different styles
labels = [
    ("BookmarkLine"                ,"Bookmark Line",'Custom.TLabel')                   ,
    ("Bookmarklistall"             ,"? Bookmark list All",'Custom.TLabel')             ,
    ("BracketsGoTo"                ,"Brackets GoTo",'Custom.TLabel')                   ,
    ("BracketsRemove"              ,"Brackets Remove",'Custom.TLabel')                 ,
    ("BracketsSelect"              ,"Brackets Select",'Custom.TLabel')                 ,
    ("AlignMultiCoulmnsbySeparator","Align Multi Coulmns by Separator",'Custom.TLabel'),
    ("ChangeAllOccurrences"        ,"Change All Occurrences",'Custom.TLabel')          ,
    ("Comment"                     ,"Comment",'Custom.TLabel')                         ,
    ("CommentSelection"            ,"Comment Selection",'Custom.TLabel')               ,
    ("DeleteLine"                  ,"Delete Line",'Custom.TLabel')                     ,
    ("Keyboard_Shortcut"           ,"VSCODE Keyboard Shortcut",'Custom.TLabel')        ,
    ("LineJoin"                    ,"Line Join",'Custom.TLabel')                       ,
    ("Minimap"                     ,"Minimap",'Custom.TLabel')                         ,
    ("NewWindow"                   ,"New Window",'Custom.TLabel')                      ,
    ("remove_dup_lines"            ,"Remove Dup Lines",'Custom.TLabel')                ,
    ("RemoveFromSelection"         ,"Remove From Selection",'Custom.TLabel')           ,
    ("SelectNext"                  ,"Select Next",'Custom.TLabel')                     ,
    ("SelectPrevious"              ,"Select Previous",'Custom.TLabel')                 ,
    ("SortLinesAscending"          ,"Sort Lines Ascending",'Custom.TLabel')            ,
    ("SplitSameDocument"           ,"Split Same Document",'Custom.TLabel')             ,
    ("TableFormatProperly"         ,"Table Format Properly",'Custom.TLabel')           ,
    ("TableFormatProperly2"        ,"Table Format Properly 2",'Custom.TLabel')         ,
    ("UnComment"                   ,"UnComment",'Custom.TLabel')                       ,
]

# Number of columns per row
max_columns = 4

for i, (command_name, lbl_text, style_name) in enumerate(labels):
    row = i // max_columns
    column = i % max_columns
    label = ttk.Label(vscode_window, text=lbl_text, style=style_name, cursor='hand2')
    label.grid(row=row, column=column, padx=(0, 0), pady=(0, 0), sticky="ew")
    label.bind("<Enter>", on_enter)
    label.bind("<Leave>", on_leave)
    label.bind("<Button-1>", lambda e, c=command_name: subprocess.Popen(["powershell", f"python c:/ms1/HotKeys.py {c}"]))

    # Configure row and column weights
    vscode_window.grid_columnconfigure(column, weight=1)
    vscode_window.grid_rowconfigure(row, weight=1)

# Pack the canvas and scrollbar into the container frame
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill='y')

# Pack the container frame into the root window
container_frame.pack(fill='both', expand=True)

root.mainloop()