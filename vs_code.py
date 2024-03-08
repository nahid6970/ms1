import tkinter as tk
import keyboard
import pygetwindow as gw
import subprocess

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

# Create a frame for the buttons
button_frame = tk.Frame(root, bg="#1d2027")
button_frame.pack(side="top", anchor="center", pady=(20,0), padx=(0,0))

# Button properties: (text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command, window_title)
button_properties = [
    ("VS Code"        ,button_frame,"#21a3f1","#1D2027",1,10,"flat",("JetBrainsMono NF",11,"bold"),0,0,1,1,"ew",0,0,(1,1),(0,0),None)                                     ,
    ("Brackets Select",button_frame,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),1,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut("Visual Studio Code","ctrl+alt+right")),
    ("Brackets Remove",button_frame,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),2,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut("Visual Studio Code","ctrl+alt+Backspace")),
    ("Line Join"      ,button_frame,"#FFFFFF","#1D2027",1,20,"flat",("JetBrainsMono NF",11,"bold"),3,0,1,1,"ew",0,0,(1,1),(0,0),lambda: send_shortcut("Visual Studio Code","alt+j")),
]

# Create buttons
for button_props in button_properties:
    create_button(*button_props)

# Start the main event loop
root.mainloop()
