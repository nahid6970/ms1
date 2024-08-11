import argparse
import subprocess
import tkinter as tk
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

Main_Window = tk.Frame(root, bg="#1d2027")
Main_Window.pack(side="top", anchor="center", pady=(0,0), padx=(0,0))


def apply_hover_effect(widget):
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
def on_enter(event):
    event.widget.configure(style='Hover.TLabel')
def on_leave(event):
    event.widget.configure(style='Custom.TLabel')
# Create a style object
style = Style()
# Configure a custom style for TLabel
style.configure('Custom.TLabel',
                font=('Helvetica', 12, 'italic'),
                background='lightgrey',
                foreground='darkblue',
                borderwidth=2,
                relief='solid',
                padding=(10, 5),
                anchor='center',
                width=10)
# Configure a hover style
style.configure('Hover.TLabel',
                font=('Helvetica', 12, 'italic'),
                background='red',
                foreground='darkblue',
                borderwidth=2,
                relief='solid',
                padding=(10, 5),
                anchor='center',
                width=10)


# ("Terminal"           ,Main_Window   ,"#000000","#ffffff",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:switch_to_frame(terminal         ,Main_Window))   ,
# ("Terminal-Close"     ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),0,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"           ,"CommandPrompt"],"Ctrl+Shift+W"        )),
# ("Terminal-Split-V"   ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"           ,"CommandPrompt"],"Alt+Shift+equal"     )),
# ("Terminal-Split-H"   ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),2,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell","Command"]      ,"Alt+Shift+underscore")),


#! chrome
#! ctrl+shift+b






terminal = tk.Button( root, text="Folder", command=lambda: switch_to_frame(terminal, root))
terminal = tk.Frame(bg="#1D2027")
terminal.pack_propagate(True)



vscode_window = tk.Button( root, text="Folder", command=lambda: switch_to_frame(vscode_window, root))
vscode_window = tk.Frame(bg="#1D2027")
vscode_window.pack_propagate(True)
VSCode = HoverButton(Main_Window, bg="#23a8f2", fg="#000000", h_bg="#FFFFFF", h_fg="#000000", height=1, width=10, bd=0, highlightthickness=0, command=lambda:switch_to_frame(vscode_window , Main_Window), text="\udb81\ude10")
VSCode.pack(side="left", anchor="center", padx=(0,0), pady=(0,0))

AlignMultiCoulmnsbySeparator = Label(vscode_window, style='Custom.TLabel', text="\uf037")
AlignMultiCoulmnsbySeparator.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))
AlignMultiCoulmnsbySeparator.bind("<Button-1>", lambda event: subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py AlignMultiCoulmnsbySeparator"]))
apply_hover_effect(AlignMultiCoulmnsbySeparator)

BookmarkLine = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py BookmarkLine"]), text="⭐")
BookmarkLine.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Bookmarklistall = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Bookmarklistall"]), text="?⭐")
Bookmarklistall.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

BracketsGoTo = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py BracketsGoTo"]), text="\uebe5")
BracketsGoTo.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

BracketsRemove = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py BracketsRemove"]), text="\uebe6")
BracketsRemove.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

BracketsSelect = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py BracketsSelect"]), text="\uf2f5")
BracketsSelect.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

ChangeAllOccurrences = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py ChangeAllOccurrences"]), text="\udb81\udc86")
ChangeAllOccurrences.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Comment = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Comment"]), text="\uf27b")
Comment.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

CommentSelection = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py CommentSelection"]), text="\udb80\udd84")
CommentSelection.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

DeleteLine = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py DeleteLine"]), text="\udb80\uddb4")
DeleteLine.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

#! ?? ExpandSelectionquota_brackets = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py ExpandSelectionquota_brackets"]), text="")
#! ?? ExpandSelectionquota_brackets.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Keyboard_Shortcut = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Keyboard_Shortcut"]), text="\uf11c")
Keyboard_Shortcut.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

LineJoin = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py LineJoin"]), text="\uebb6")
LineJoin.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Minimap = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Minimap"]), text="\uf279")
Minimap.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

NewWindow = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py NewWindow"]), text="\uea7f")
NewWindow.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

RemoveDupLines = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py remove_dup_lines"]), text="\udb84\ude33")
RemoveDupLines.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

RemoveFromSelection = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py RemoveFromSelection"]), text="\ueb3c")
RemoveFromSelection.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

SelectNext = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py SelectNext"]), text="\udb82\udfb0")
SelectNext.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

SelectPrevious = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py SelectPrevious"]), text="\udb82\udfb2")
SelectPrevious.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

SortLinesAscending = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py SortLinesAscending"]), text="\udb81\udcbc")
SortLinesAscending.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

SplitSameDocument = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py SplitSameDocument"]), text="\ueb56")
SplitSameDocument.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

TableFormatProperly = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py TableFormatProperly"]), text="\uebb7")
TableFormatProperly.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

TableFormatProperly2 = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py TableFormatProperly2"]), text="\uebb7")
TableFormatProperly2.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

UnComment = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py UnComment"]), text="\udb85\udde1")
UnComment.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))



Excel_window = tk.Button( root, text="Folder", command=lambda: switch_to_frame(Excel_window, root))
Excel_window = tk.Frame(bg="#1D2027")
Excel_window.pack_propagate(True)
Excel = HoverButton(Main_Window, bg="#21a366", fg="#000000", h_bg="#FFFFFF", h_fg="#000000", height=1, width=10, bd=0, highlightthickness=0, command=lambda:switch_to_frame(Excel_window , Main_Window), text="\udb84\udf8f")
Excel.pack(side="left", anchor="center", padx=(0,0), pady=(0,0))

Series = HoverButton(Excel_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Series"]), text="\udb81\udc8b")
Series.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Fit_Row = HoverButton(Excel_window, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Fit_Row"]), text="\udb82\udc37")
Fit_Row.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Fit_Column = HoverButton(Excel_window, text="\udb82\udc35", bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0,
                         tooltip_text="Adjust Column",tooltip_delay=100,tooltip_font_size=12,
                         command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Fit_Column"]))
Fit_Column.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))



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
