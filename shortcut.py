import argparse
import subprocess
import tkinter as tk
from tkinter import ttk
import keyboard
import pygetwindow as gw
import time
from idlelib.tooltip import Hovertip
from functionlist import *
import pyautogui
from tkinter import *
from tkinter.ttk import *

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()


root = tk.Tk()
root.title("Shortcut Buttons")
root.attributes('-topmost', True)
root.overrideredirect(True)  # Remove default borders
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = 0
y = 0
root.geometry(f"700x400+{x}+{y}")

default_font = ("Jetbrainsmono nfp", 14, "bold")
root.option_add("*Font", default_font)







def on_enter(event):
    event.widget.configure(style='Hover.TButton')

def on_leave(event):
    event.widget.configure(style='Custom.TButton')
# Create a style object
style = Style()

# Configure a custom style for TButton
style.configure('Custom.TButton', 
                font=('Jetbrainsmono nfp', 12, 'italic'), 
                background='lightgrey', 
                foreground='darkblue', 
                borderwidth=2, 
                relief='solid',
                padding=(10, 5),
                width=18,
                anchor='center')

# Configure a hover style
style.configure('Hover.TButton', 
                font=('Jetbrainsmono nfp', 12, 'italic'), 
                background='red', 
                foreground='red', 
                borderwidth=2, 
                relief='solid',
                padding=(10, 5),
                width=18,
                anchor='center')


# ("Terminal"           ,Main_Window   ,"#000000","#ffffff",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:switch_to_frame(terminal         ,Main_Window))   ,
# ("Terminal-Close"     ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),0,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"           ,"CommandPrompt"],"Ctrl+Shift+W"        )),
# ("Terminal-Split-V"   ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"           ,"CommandPrompt"],"Alt+Shift+equal"     )),
# ("Terminal-Split-H"   ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),2,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell","Command"]      ,"Alt+Shift+underscore")),


#! chrome
#! ctrl+shift+b




main_frame = tk.Frame(root, bg="#1d2027")
main_frame.pack(fill='both', expand=True)
# Main_Window.pack(side="top", anchor="w", pady=(0,0), padx=(0,0))


vscode_window = tk.Button( root, text="Folder", command=lambda: switch_to_frame(vscode_window, root))
vscode_window = tk.Frame(bg="#1D2027")
vscode_window.pack_propagate(True)
VSCode = HoverButton(main_frame, bg="#23a8f2", fg="#000000", h_bg="#FFFFFF", h_fg="#000000", height=1, width=10, bd=0, highlightthickness=0, command=lambda:switch_to_frame(vscode_window , main_frame), text="\udb81\ude10")
VSCode.pack(padx=(1,1), pady=(1,1))

# Create buttons
buttons = [
    ("BookmarkLine"                ,"Bookmark Line")                   ,
    ("Bookmarklistall"             ,"? Bookmark list All")             ,
    ("BracketsGoTo"                ,"Brackets GoTo")                   ,
    ("BracketsRemove"              ,"Brackets Remove")                 ,
    ("BracketsSelect"              ,"Brackets Select")                 ,
    ("AlignMultiCoulmnsbySeparator","Align Multi Coulmns by Separator"),
    ("ChangeAllOccurrences"        ,"Change All Occurrences")          ,
    ("Comment"                     ,"Comment")                         ,
    ("CommentSelection"            ,"Comment Selection")               ,
    ("DeleteLine"                  ,"Delete Line")                     ,
    ("Keyboard_Shortcut"           ,"VSCODE Keyboard Shortcut")        ,
    ("LineJoin"                    ,"Line Join")                       ,
    ("Minimap"                     ,"Minimap")                         ,
    ("NewWindow"                   ,"New Window")                      ,
    ("remove_dup_lines"            ,"Remove Dup Lines")                ,
    ("RemoveFromSelection"         ,"Remove From Selection")           ,
    ("SelectNext"                  ,"Select Next")                     ,
    ("SelectPrevious"              ,"Select Previous")                 ,
    ("SortLinesAscending"          ,"Sort Lines Ascending")            ,
    ("SplitSameDocument"           ,"Split Same Document")             ,
    ("TableFormatProperly"         ,"Table Format Properly")           ,
    ("TableFormatProperly2"        ,"Table Format Properly 2")         ,
    ("UnComment"                   ,"UnComment")                       ,
]
max_rows = 10
# Create buttons and apply initial styles and bindings
for i, (command_name, btn_text) in enumerate(buttons):
    # Create each button with the 'Custom.TButton' style initially
    button = Button(vscode_window, text=btn_text, style='Custom.TButton', command=lambda c=command_name: subprocess.Popen(["powershell", f"python c:/ms1/HotKeys.py {c}"]))
    button.grid(row=i % max_rows, column=i // max_rows, padx=(0, 0), pady=(0, 0), sticky="ew")
    # Bind hover events to the button
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    # Make rows and columns resizable
    vscode_window.grid_columnconfigure(i // max_rows, weight=1)
    vscode_window.grid_rowconfigure(i % max_rows, weight=1)



Excel_frame = tk.Button( root, text="Folder", command=lambda: switch_to_frame(Excel_frame, root))
Excel_frame = tk.Frame(bg="#1D2027")
Excel_frame.pack_propagate(True)
Excel = HoverButton(main_frame, bg="#21a366", fg="#000000", h_bg="#FFFFFF", h_fg="#000000", height=1, width=10, bd=0, highlightthickness=0, command=lambda:switch_to_frame(Excel_frame , main_frame), text="\udb84\udf8f")
Excel.pack(padx=(1,1), pady=(1,1))

Series = HoverButton(Excel_frame, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Series"]), text="\udb81\udc8b")
Series.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Fit_Row = HoverButton(Excel_frame, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Fit_Row"]), text="\udb82\udc37")
Fit_Row.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Fit_Column = HoverButton(Excel_frame, text="\udb82\udc35", bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0,
                         tooltip_text="Adjust Column",tooltip_delay=100,tooltip_font_size=12,
                         command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Fit_Column"]))
Fit_Column.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))


terminal = tk.Button( root, text="Folder", command=lambda: switch_to_frame(terminal, root))
terminal = tk.Frame(bg="#1D2027")
terminal.pack_propagate(True)



def center_and_press_alt_2(window):
    def center_window():
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    def press_alt_2():
        pyautogui.hotkey('alt', '2')
    center_window()
    window.after(25, press_alt_2)

center_and_press_alt_2(root)
root.mainloop()
