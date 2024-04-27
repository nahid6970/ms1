import subprocess
import tkinter as tk
import keyboard
import pygetwindow as gw
import time

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
y = screen_height//2-1000//2
root.geometry(f"30x1000+{x}+{y}")

default_font = ("Jetbrainsmono nfp", 14, "bold")
root.option_add("*Font", default_font)

Main_Window = tk.Frame(root, bg="#1d2027")
Main_Window.pack(side="top", anchor="center", pady=(0,0), padx=(0,0))



# Button properties: (text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command, window_title)
button_properties=[
("VSCode"                       ,Main_Window   ,"#21a3f1","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),0 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:switch_to_frame(vscode_window         ,Main_Window)),
#! ("AlignMultiCoulmnsbySeparator" ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"alt+shift+semicolon" )),
#! ("BookmarkLine"                 ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),2,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+b+ctrl+b"       )),
#! ("Bookmarklistall"              ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),3,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+b+ctrl+l"       )),
#! ("BracketsGoTo"                 ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),4,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+shift+backslash")),
#! ("BracketsRemove"               ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),5,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+alt+Backspace"  )),
#! ("BracketsSelect"               ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),6,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+alt+right"      )),
#! ("ChangeAllOccurrences"         ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),7,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"CTRL+F2"             )),
#! ("Comment"                      ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),8,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+k+c"            )),
#! ("CommentSelection"             ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),9,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ALT+SHIFT+A"         )),
#! ("DeleteLine"                   ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),10,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+shift+k"        )),
#? ("ExpandSelectionquota/brackets",vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),11,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"shift+alt+right"     )),
#! ("Keyboard-Shortcut"            ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),12,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"CTRL+K+CTRL+S"       )),
#! ("LineJoin"                     ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),13,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"alt+j"               )),
#! ("Minimap"                      ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),14,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ALT+m"               )),
#! ("NewWindow"                    ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),15,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+n"              )),


#! ("RemoveDupLines"               ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),16,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_m_k         ("Visual Studio Code"     ,["ctrl+k","alt+d"])),
#! ("RemoveFromSelection"          ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),17,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_m_k("Visual Studio Code"              ,["ctrl+h","alt+l"])),


#! ("SelectNext"                   ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),18,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+d"              )),
#! ("SelectPrevious"               ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),19,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+shift+d"        )),
#! ("SortLinesAscending"           ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),20,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ALT+SHIFT+S"         )),
#! ("SplitSameDocument"            ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),21,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"CTRL+backslash"      )),
#! ("TableFormatProperly"          ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),22,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"CTRL+T+T"            )),
#! ("TableFormatProperly2"         ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),23,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"CTRL+q+f"            )),
#! ("UnComment"                    ,vscode_window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),24,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"         ,"ctrl+k+u"            )),


# ("Terminal"           ,Main_Window   ,"#000000","#ffffff",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:switch_to_frame(terminal         ,Main_Window))   ,
# ("Terminal-Close"     ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),0,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"           ,"CommandPrompt"],"Ctrl+Shift+W"        )),
# ("Terminal-Split-V"   ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"           ,"CommandPrompt"],"Alt+Shift+equal"     )),
# ("Terminal-Split-H"   ,terminal      ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),2,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell","Command"]      ,"Alt+Shift+underscore")),


# ("Excel"         ,Main_Window,"#1b8655","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),2,0,1,1,"ew",0,0,(1,1),(0,0),lambda:switch_to_frame(Excel         ,Main_Window))  ,
# ("Series"        ,Excel      ,"#1b8655","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),0,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Excel"]            ,"Alt+h+f+i+s")),
# ("Fit Row"       ,Excel      ,"#1b8655","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Excel"]            ,"Alt+h+o+a"))  ,
# ("Fit Column"    ,Excel      ,"#1b8655","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),2,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Excel"]            ,"Alt+h+o+i"))  ,

]


# # Button properties: (text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command, window_title)
# button_properties=[
#     ("VSCode", Main_Window, "#21a3f1", "#1D2027", 1, 0, "flat", ("JetBrainsMonoNF", 11, "bold"), 0, 0, 1, 1, "ew", 0, 0, (1, 1), (0, 0), lambda: switch_to_frame(vscode_window, Main_Window)),
#     ("RemoveDupLines", vscode_window, "#FFFFFF", "#1D2027", 1, 0, "flat", ("JetBrainsMonoNF", 11, "bold"), 16, 0, 1, 1, "ew", 0, 0, (1, 1), (0, 0),lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Series"])),
# ]


# # Create buttons
# for button_props in button_properties:
#     create_button(*button_props)


#! chrome
#! ctrl+shift+b


vscode_window = tk.Button( root, text="Folder", command=lambda: switch_to_frame(vscode_window, root))
vscode_window = tk.Frame(bg="#1D2027")
vscode_window.pack_propagate(True)

Excel = tk.Button( root, text="Folder", command=lambda: switch_to_frame(Excel, root))
Excel = tk.Frame(bg="#1D2027")
Excel.pack_propagate(True)

terminal = tk.Button( root, text="Folder", command=lambda: switch_to_frame(terminal, root))
terminal = tk.Frame(bg="#1D2027")
terminal.pack_propagate(True)

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.bg = kw.pop('bg', "#000000")
        self.h_bg = kw.pop('h_bg', "red")
        self.default_fg = kw.pop('fg', "#FFFFFF")
        self.h_fg = kw.pop('h_fg', "#000000")
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(bg=self.bg, fg=self.default_fg)

    def on_enter(self, event):
        self.configure(bg=self.h_bg, fg=self.h_fg)

    def on_leave(self, event):
        self.configure(bg=self.bg, fg=self.default_fg)


VSCode = HoverButton(Main_Window, bg="#23a8f2", fg="#000000", h_bg="green", h_fg="white", height=1, width=10, bd=0, highlightthickness=0, command=lambda:switch_to_frame(vscode_window , Main_Window), text="\udb81\ude10")
VSCode.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

AlignMultiCoulmnsbySeparator = HoverButton(vscode_window, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py AlignMultiCoulmnsbySeparator"]), text="\uf037")
AlignMultiCoulmnsbySeparator.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

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








root.mainloop()
