import subprocess
import tkinter as tk
import keyboard
import pygetwindow as gw
import time


def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

def create_button(text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.grid(row=row_button, column=column_button, rowspan=rowspan_button, columnspan=columnspan_button, padx=padx_pack, pady=pady_pack, sticky=sticky)
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


vscode_window = tk.Button( root, text="Folder", command=lambda: switch_to_frame(vscode_window, root))
vscode_window = tk.Frame(bg="#1D2027")
vscode_window.pack_propagate(True)

Excel = tk.Button( root, text="Folder", command=lambda: switch_to_frame(Excel, root))
Excel = tk.Frame(bg="#1D2027")
Excel.pack_propagate(True)

terminal = tk.Button( root, text="Folder", command=lambda: switch_to_frame(terminal, root))
terminal = tk.Frame(bg="#1D2027")
terminal.pack_propagate(True)

# Button properties: (text, frame, bg_color, fg_color, height, width, relief, font, row_button, column_button, rowspan_button, columnspan_button, sticky, padx_button, pady_button, padx_pack, pady_pack, command, window_title)
button_properties=[
    ("VSCode", Main_Window, "#21a3f1", "#1D2027", 1, 0, "flat", ("JetBrainsMonoNF", 11, "bold"), 0, 0, 1, 1, "ew", 0, 0, (1, 1), (0, 0), lambda: switch_to_frame(vscode_window, Main_Window)),
    ("RemoveDupLines", vscode_window, "#FFFFFF", "#1D2027", 1, 0, "flat", ("JetBrainsMonoNF", 11, "bold"), 16, 0, 1, 1, "ew", 0, 0, (1, 1), (0, 0),lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py kill_process"])),
]

#! chrome
#! ctrl+shift+b


# Create buttons
for button_props in button_properties:
    create_button(*button_props)

# Start the main event loop
root.mainloop()
