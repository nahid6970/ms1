import tkinter as tk
import keyboard
import pygetwindow as gw

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

def create_button(text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command, window_title=None):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack, sticky=sticky)
    button.window_title = window_title  # Store the window title with the button
    return button

def send_shortcut(window_title, shortcut):
    # Find the window with the given title
    app_window = gw.getWindowsWithTitle(window_title)[0]
    app_window.activate()  # Activate the window
    # Simulate the given shortcut
    keyboard.send(shortcut)

# Create the main window
root = tk.Tk()
root.title("Shortcut Buttons")
root.attributes('-topmost', True)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = screen_width//2 - 1800//2
y = screen_height//2 + 150
root.geometry(f"1800x300+{x}+{y}")

# Create a frame for the buttons
Main_Window = tk.Frame(root, bg="#1d2027")
Main_Window.pack(side="top", anchor="center", pady=(20,0), padx=(0,0))

Comment_Window = tk.Button( root, text="Folder", command=lambda: switch_to_frame(Comment_Window, root), )

Comment_Window = tk.Frame(bg="#1D2027")
Comment_Window.pack_propagate(True)

# Button properties: (text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command, window_title)
button_properties = [
    ("VS Code"                              ,Main_Window   ,"#21a3f1","#1D2027",1,10,"flat",("JetBrainsMono NF",11,"bold"),0  ,0,1,1,"ew",0,0,(1,1),(0,0),None                                                               ),
    ("Line Join"                            ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),1  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"alt+j"               ))      ,
    ("Brackets Select"                      ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),2  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+alt+right"      ))      ,
    ("Brackets Remove"                      ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),3  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+alt+Backspace"  ))      ,
    ("Brackets GoTo"                        ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),4  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+shift+backslash"))      ,
    ("Expand Selection quota/brackets"      ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),5  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"shift+alt+right"     ))      ,
    ("Align Multi Coulmns by Separator"     ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),6  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"alt+shift+semicolon" ))      ,
    
    ("#"                                    ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),7  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: switch_to_frame(Comment_Window                              ,Main_Window           ))      ,
    ("Comment Selection"                    ,Comment_Window,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),8  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ALT+SHIFT+A"         ))      ,
    ("Comment"                              ,Comment_Window,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),9  ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+k+c"            ))      ,
    ("UnComment"                            ,Comment_Window,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),10 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+k+u"            ))      ,

    ("Sort Lines Ascending"                 ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),11 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ALT+SHIFT+S"         ))      ,
    ("Split Same Document"                  ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),12 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"CTRL+backslash"      ))      ,
    ("Add Selection To Next Find Match"     ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),13 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+d"              ))      ,
    ("Add Selection To Previous Find Match" ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),14 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+shift+d"        ))      ,
    ("Change All Occurrences"               ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),15 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"CTRL+F2"             ))      ,
    ("Table Format Properly"                ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),16 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"CTRL+T+T"            ))      ,
    ("Bookmark Line"                        ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),17 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+b+ctrl+b"       ))      ,
    ("Bookmark list all"                    ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),18 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ctrl+b+ctrl+l"       ))      ,
    ("Keyboard-Shortcut"                    ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),19 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"CTRL + K + CTRL + S"       )),
    ("Minimap"                              ,Main_Window   ,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),20 ,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut  ("Visual Studio Code"                        ,"ALT + m"       ))            ,
]

# Create buttons
for button_props in button_properties:
    create_button(*button_props)

# Start the main event loop
root.mainloop()
