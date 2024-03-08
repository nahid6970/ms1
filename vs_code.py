import tkinter as tk
import keyboard
import pygetwindow as gw
import time


def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

def create_button(text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command, window_title=None):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack, sticky=sticky)
    button.window_title = window_title  # Store the window title with the button
    return button


# def send_k(window_title, shortcut):
#     # Find the window with the given title
#     app_window = gw.getWindowsWithTitle(window_title)[0]
#     app_window.activate()  # Activate the window
#     # Simulate the given shortcut
#     keyboard.send(shortcut)

def send_k(window_titles, shortcut):
    for title in window_titles:
        try:
            app_window = gw.getWindowsWithTitle(title)[0]
            app_window.activate()  # Activate the window
            keyboard.send(shortcut)
            return  # Exit the loop if shortcut sent successfully
        except IndexError:
            pass  # If window title not found, try the next one


def send_m_k(window_title, shortcuts):
    app_window = gw.getWindowsWithTitle(window_title)[0]
    app_window.activate()  # Activate the window
    # Loop through the list of shortcuts and send them one by one
    for shortcut in shortcuts:
        keyboard.send(shortcut)
        # Insert a small delay between each shortcut to ensure correct sequence
        time.sleep(0.1)

# Create the main window
root = tk.Tk()
root.title("Shortcut Buttons")
root.attributes('-topmost', True)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = screen_width-500
y = screen_height//2-800//2
root.geometry(f"500x800+{x}+{y}")

# Create a frame for the buttons
Main_Window = tk.Frame(root, bg="#1d2027")
Main_Window.pack(side="top", anchor="center", pady=(0,0), padx=(0,0))

Comment_Window = tk.Button( root, text="Folder", command=lambda: switch_to_frame(Comment_Window, root))

Comment_Window = tk.Frame(bg="#1D2027")
Comment_Window.pack_propagate(True)

# Button properties: (text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command, window_title)
button_properties=[
("VSCode"                       ,Main_Window   ,"#21a3f1","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),0 ,0,1,1,"ew",0,0,(1,1),(0,0),None),
("BracketsSelect"               ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),2 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+alt+right"      )),
("BracketsRemove"               ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),3 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+alt+Backspace"  )),
("BracketsGoTo"                 ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),4 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+shift+backslash")),
("ExpandSelectionquota/brackets",Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),5 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"shift+alt+right"     )),
("AlignMultiCoulmnsbySeparator" ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),6 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"alt+shift+semicolon" )),

("Comment"                      ,Main_Window   ,"#eac353","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),7 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:switch_to_frame(Comment_Window         ,Main_Window           )),
("CommentSelection"             ,Comment_Window,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),8 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ALT+SHIFT+A"         )),
("Comment"                      ,Comment_Window,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),9 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+k+c"            )),
("UnComment"                    ,Comment_Window,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),10,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+k+u"            )),

("LineJoin"                     ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),1 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"alt+j"               )),
("SortLinesAscending"           ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),11,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ALT+SHIFT+S"         )),

("SplitSameDocument"            ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),12,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"CTRL+backslash"      )),

("SelectNext"                   ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),13,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+d"              )),
("SelectPrevious"               ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),14,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+shift+d"        )),

("TableFormatProperly"          ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),16,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"CTRL+T+T"            )),
("TableFormatProperly2"         ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),16,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"CTRL+q+f"            )),

("ChangeAllOccurrences"         ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),15,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"CTRL+F2"             )),
("BookmarkLine"                 ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),17,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+b+ctrl+b"       )),
("Bookmarklistall"              ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),18,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+b+ctrl+l"       )),
("Keyboard-Shortcut"            ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),19,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"CTRL+K+CTRL+S"       )),
("Minimap"                      ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),20,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ALT+m"               )),
("RemoveDupLines"               ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),21,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_m_k         ("Visual Studio Code"     ,["ctrl+k" ,"alt+d"]        )),

("DeleteLine"                   ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),23,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+shift+k"        )),
("NewWindow"                    ,Main_Window   ,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),24,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k         ("VisualStudioCode"     ,"ctrl+n"              )),

("RemoveFromSelection",Main_Window,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),22,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_m_k("Visual Studio Code"  ,["ctrl+h","alt+l"])),




("Terminal-Close"     ,Main_Window,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),25,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"       ,"CommandPrompt"],"Ctrl+Shift+W"        )),
("Terminal-Split-V"   ,Main_Window,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),26,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"       ,"CommandPrompt"],"Alt+Shift+equal"     )),
("Terminal-Split-H"   ,Main_Window,"#FFFFFF","#1D2027",1,0,"flat",("JetBrainsMonoNF",11,"bold"),27,0,1,1,"ew",0,0,(1,1),(0,0),lambda:send_k  (["Powershell"       ,"Command"]      ,"Alt+Shift+underscore")),
]

# Create buttons
for button_props in button_properties:
    create_button(*button_props)

# Start the main event loop
root.mainloop()
