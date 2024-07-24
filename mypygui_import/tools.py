import subprocess
import subprocess
import tkinter as tk
from customtkinter import CTkButton, CTkLabel

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

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

# Create main window
ROOT = tk.Tk()
ROOT.title("Folder")
# ROOT.attributes('-topmost', True)  # Set always on top
# ROOT.geometry("520x800")
ROOT.configure(bg="#282c34")
# ROOT.overrideredirect(True)  # Remove default borders

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Add bindings to make the window movable
ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width//2 - 1200//2
y = screen_height//2 - 800//2
ROOT.geometry(f"1200x800+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1200, height=800) #!
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1)  # Add some padding at the top
MAIN_FRAME.pack(expand=True)


#! Close Window
def close_window(event=None):
    ROOT.destroy()

#!? Main ROOT BOX
# ROOT1 = tk.Frame(ROOT, bg="#1d2027")
# ROOT1.pack(side="right", anchor="ne", pady=(3,2),padx=(3,1))

# LB_XXX=tk.Label(ROOT1, text="\uf2d3", bg="#1d2027",fg="#ff0000",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",18,"bold"))
# LB_XXX.pack(side="left",padx=(1,10),pady=(0,0))
# LB_XXX.bind("<Button-1>",close_window)





#! Tools
ROW_1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROW_1.pack(side="top", anchor="center", pady=(30,0), padx=(0,0))

WINDOWSTOOLS_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1200 , height=800)
WINDOWSTOOLS_FRAME.pack_propagate(True)
ENTER_FRAME = CTkButton(ROW_1, text="Windows\nTools", width=100, height=100, hover_color="#1dd463", command=lambda:switch_to_frame(WINDOWSTOOLS_FRAME , MAIN_FRAME), font=("JetBrainsMono NFP",18,"bold"), corner_radius=0, border_width=1, border_color="#000000", fg_color="#ffffff", text_color="#000")
ENTER_FRAME.pack(side="left",padx=(1,1))
BOX = tk.Frame(WINDOWSTOOLS_FRAME, bg="#1D2027")
BOX.pack(side="top", pady=(30,2), padx=(5,1), anchor="center", fill="x")

BACK = tk.Button(BOX, text="\ueb6f \ueb6f \ueb6f", width=50, bg="#1d2027", fg="#ffffff", command=lambda: switch_to_frame(MAIN_FRAME, WINDOWSTOOLS_FRAME))
BACK.grid(row=0, column=0, columnspan=3, pady=(0, 10))  # Add BACK button at the top

def Folder(WINDOWSTOOLS_FRAME):
    items = [
("#204892", "#ffffff", "Advanced Adapter",              {"command": "control ncpa.cpl"}),
("#204892", "#ffffff", "CheckDisk",                     {"command": ["powershell", "Start-Process", "-FilePath", "chkdsk", "-ArgumentList", '"/f /r"', "-Verb", "RunAs"]}),
("#000000", "#ffffff", "Chris Titus Win Utility",       {"command": ["powershell", "Start-Process", "-FilePath", "powershell", "-ArgumentList", 'C:/ms1/scripts/ctt.ps1', "-Verb", "RunAs"]}),
("#204892", "#ffffff", "Disk Cleanup",                  {"command": ["powershell", "Start-Process", "-FilePath","cleanmgr","-Verb", "RunAs"]}),
("#204892", "#ffffff", "DISM",                          {"command": ["powershell","Start-Process","-FilePath","cmd","-ArgumentList",'"/k DISM /Online /Cleanup-Image /RestoreHealth"',"-Verb", "RunAs"]}),
("#204892", "#ffffff", "DxDiag",                        {"command": "dxdiag"}),
("#204892", "#ffffff", "Flush DNS",                     {"command": ["powershell", "Start-Process", "-FilePath","cmd","-ArgumentList",'"/k ipconfig /flushdns"', "-Verb", "RunAs"]}),
("#204892", "#ffffff", "MSconfig",                      {"command": ["msconfig.exe"]}),
("#204892", "#ffffff", "Netplwiz",                      {"command": "netplwiz.exe"}),
("#204892", "#ffffff", "Power Plan",                    {"command": "powercfg.cpl"}),
("#204892", "#ffffff", "SFC",                           {"command": ["powershell", "Start-Process", "-FilePath", "cmd","-ArgumentList",'"/k sfc /scannow"', "-Verb", "RunAs"]}),
("#204892", "#ffffff", "Systeminfo [Terminal]",         {"command": ["powershell", "Start-Process", "cmd","-ArgumentList",'"/k systeminfo"']}),
("#204892", "#ffffff", "UAC",                           {"command": "UserAccountControlSettings.exe"}),
("#204892", "#ffffff", "Turn on Windows Features",      {"command": "optionalfeatures"}),
("#204892", "#ffffff", "Winsock Reset",                 {"command": ["powershell", "Start-Process", "-FilePath", "cmd","-ArgumentList",'"/k netsh winsock reset"' ,"-Verb", "RunAs"]}),
("#204892", "#ffffff", "Character Map",                 {"command": "charmap"}),
("#204892", "#ffffff", "Desktop Icon",                  {"command": "rundll32.exe shell32.dll,Control_RunDLL desk.cpl,,0"}),
("#204892", "#ffffff", "Text Service & Input Language", {"command": "rundll32 Shell32.dll,Control_RunDLL input.dll,,{C07337D3-DB2C-4D0B-9A93-B722A6C106E2}"}),
("#204892", "#ffffff", "System Information",            {"command": "msinfo32"}),
("#204892", "#ffffff", "Show / Hide Updates",           {"command": "D:\\software\\@MustApp\\wushowhide.diagcab"}),
("#204892", "#ffffff", "God Mode",                      {"command": "explorer shell:::{ED7BA470-8E54-465E-825C-99712043E01C}"}),
("#204892", "#ffffff", "Performance Options",           {"command": "systempropertiesperformance"}),
    ]

    # Sort the items alphabetically by their text
    items.sort(key=lambda x: x[2])
    # Number of items per column
    max_items_per_column = 15
    # Items Property
    for index, (bg_color, fg_color, item_text, command_dict) in enumerate(items):
        row = (index % max_items_per_column) + 1  # Start from row 1 to leave space for the BACK button
        column = index // max_items_per_column
        item = tk.Label(BOX, text=item_text, font=("jetbrainsmono nfp",12,"bold"), width=0, fg=fg_color, bg=bg_color)
        # Function to handle click effect
        def on_click(event, cmd=command_dict["command"], item=item, bg=bg_color, fg=fg_color):
            item.config(bg="#ffffff", fg="#204892")  # Change colors temporarily
            subprocess.Popen(cmd, shell=True)
            WINDOWSTOOLS_FRAME.after(100, lambda: item.config(bg=bg, fg=fg))  # Restore original colors after 100ms
        item.bind("<Button-1>", on_click)
        item.grid(row=row, column=column, padx=(0, 10), pady=(0, 2), sticky="w")
Folder(WINDOWSTOOLS_FRAME)







PYTHON_SCRIPT_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1200 , height=800)
PYTHON_SCRIPT_FRAME.pack_propagate(True)
ENTER_FRAME = CTkButton(ROW_1, text="PYTHON\nSCRIPTS", width=100, height=100, hover_color="#1dd463", command=lambda:switch_to_frame(PYTHON_SCRIPT_FRAME , MAIN_FRAME), font=("JetBrainsMono NFP",18,"bold"), corner_radius=0, border_width=1, border_color="#000000", fg_color="#6ca9cd", text_color="#000")
ENTER_FRAME.pack(side="left",padx=(1,1))
BOX = tk.Frame(PYTHON_SCRIPT_FRAME, bg="#1D2027")
BOX.pack(side="top", pady=(30,2), padx=(5,1), anchor="center", fill="x")

BACK = tk.Button(BOX, text="\ueb6f \ueb6f \ueb6f", width=50, bg="#1d2027", fg="#ffffff", command=lambda: switch_to_frame(MAIN_FRAME, PYTHON_SCRIPT_FRAME))
BACK.grid(row=0, column=0, columnspan=3, pady=(0, 10))  # Add BACK button at the top

def Folder(PYTHON_SCRIPT_FRAME):
    items = [
("#204892", "#ffffff", "Rounded Corner",       {"command": "C:\\ms1\\utility\\RoundedCornerOnOff.py"}),
("#204892", "#ffffff", "Font",                 {"command": "C:\\ms1\\scripts\\python\\font_style.py"}),
("#204892", "#ffffff", "Dictionary",           {"command": "C:\\ms1\\scripts\\python\\dictionary.py"}),
("#204892", "#ffffff", "Process",              {"command": "cmd /c start C:\\ms1\\mypygui_import\\process.py"}),
("#204892", "#ffffff", "Rock-Paper-Scissor",   {"command": "C:\\ms1\\scripts\\python\\Game_rock_paper_scissor.py"}),
("#204892", "#ffffff", "Morse-Code",           {"command": "cmd /c start C:\\ms1\\scripts\\python\\morse.py"}),
    ]

    # Sort the items alphabetically by their text
    items.sort(key=lambda x: x[2])
    # Number of items per column
    max_items_per_column = 15
    # Items Property
    for index, (bg_color, fg_color, item_text, command_dict) in enumerate(items):
        row = (index % max_items_per_column) + 1  # Start from row 1 to leave space for the BACK button
        column = index // max_items_per_column
        item = tk.Label(BOX, text=item_text, font=("jetbrainsmono nfp",12,"bold"), width=0, fg=fg_color, bg=bg_color)
        # Function to handle click effect
        def on_click(event, cmd=command_dict["command"], item=item, bg=bg_color, fg=fg_color):
            item.config(bg="#ffffff", fg="#204892")  # Change colors temporarily
            subprocess.Popen(cmd, shell=True)
            PYTHON_SCRIPT_FRAME.after(100, lambda: item.config(bg=bg, fg=fg))  # Restore original colors after 100ms
        item.bind("<Button-1>", on_click)
        item.grid(row=row, column=column, padx=(0, 10), pady=(0, 2), sticky="w")
Folder(PYTHON_SCRIPT_FRAME)











# PYTHON_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1200 , height=800)
# PYTHON_FRAME.pack_propagate(True)
# ENTER_FRAME = CTkButton(ROW_1, text="Python", width=100, height=100, hover_color="#1dd463", command=lambda:switch_to_frame(PYTHON_FRAME , MAIN_FRAME), font=("JetBrainsMono NFP",18,"bold"), corner_radius=0, border_width=1, border_color="#000000", fg_color="#bff130", text_color="#000")
# ENTER_FRAME.pack(side="left", padx=(1,1))
# BOX = tk.Frame(PYTHON_FRAME, bg="#1D2027")
# BOX.pack(side="top", pady=(30,2),padx=(5,1), anchor="center", fill="x")
# def Folder(PYTHON_FRAME):
#     RoundedCorner_lb = tk.Label(BOX, text="Rounded Corner", font=("jetbrainsmono nf",12,"bold"),width=0 ,fg="#ffffff", bg="#204892")
#     RoundedCorner_lb.pack(side="top", anchor="w", padx=(0, 0), pady=(0, 0))
#     RoundedCorner_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c "C:\\ms1\\utility\\RoundedCornerOnOff.py"'))
#     RoundedCorner_lb.bind("<Control-Button-1>",lambda event=None:subprocess.Popen('cmd /c Code "C:\\ms1\\utility\\RoundedCornerOnOff.py"'))

#     Process_bt=tk.Label(BOX, text="Process", font=("jetbrainsmono nf",12,"bold"),width=0 ,fg="#ffffff", bg="#204892")
#     Process_bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
#     Process_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\mypygui_import\\process.py"], shell=True))
#     Process_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\mypygui_import\\process.py"], shell=True))

#     BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,PYTHON_FRAME))
#     BACK.pack(side="top" ,padx=(0,0))
# Folder(PYTHON_FRAME)



ROW_2 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROW_2.pack(side="top", anchor="center", pady=(30,0), padx=(0,0))

Update_bt=tk.Label(ROW_2, text="\uf01b",bg="#1d2027",fg="#16a2ff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",50,"bold"))
Update_bt.pack(side="left",padx=(3,0),pady=(0,0))
Update_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\update.ps1"],  shell=True))
Update_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\update.ps1"],  shell=True))

Backup_bt=tk.Label(ROW_2, text="\uf01b",bg="#1d2027",fg="#2af083",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",50,"bold"))
Backup_bt.pack(side="left",padx=(3,0),pady=(0,0))
Backup_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\backup.ps1"], shell=True))
Backup_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\backup.ps1"], shell=True))

BackupRestore_bt=tk.Label(ROW_2, text="\udb84\udc38",bg="#1d2027",fg="#3bc7ff",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",50,"bold"))
BackupRestore_bt.pack(side="left",padx=(3,0),pady=(0,0))
BackupRestore_bt.bind("<Button-1>",lambda event:subprocess.Popen(["cmd /c start C:\\ms1\\utility\\BackupRestore.py"], shell=True))
BackupRestore_bt.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\ms1\\utility\\BackupRestore.py"],shell=True))

Encrypt_lb = tk.Label(ROW_2,text="\uf084", bg="#1d2027", fg="#ff0000", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 50, "bold"))
Encrypt_lb.pack(side="left", padx=(0, 0), pady=(0, 0))
Encrypt_lb.bind("<Button-1>",lambda event=None:subprocess.Popen('cmd /c C:\\ms1\\utility\\Encryption.py'))
Encrypt_lb.bind("<Control-Button-1>",lambda event=None:subprocess.Popen('cmd /c code C:\\ms1\\utility\\Encryption.py'))









#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
