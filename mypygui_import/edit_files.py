import subprocess
import subprocess
import tkinter as tk

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
def create_button(text, frame, bg_color, fg_color, height, width, relief, font, padx_button, pady_button, padx_pack, pady_pack, command):
    button = tk.Button(frame, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
    button.pack(padx=padx_pack, pady=pady_pack)
    return button

BOX_1 = tk.Frame(MAIN_FRAME, bg="#282c34")
BOX_1.pack(side="top", pady=(30,0), padx=(0,0))

button_properties = [
("mypygui.py"      ,BOX_1,"#346c9a","#ffffff",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,0),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\mypygui.py }"]                                            ,shell=True)                                                                     ),
("desktop_icon.py" ,BOX_1,"#346c9a","#ffffff",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,5),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\desktop_icon.py }"]                                       ,shell=True)                                                                     ),
("edit_files.py"   ,BOX_1,"#346c9a","#ffffff",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,5),lambda: subprocess.Popen(["Start","powershell","-Command","& { code c:\\ms1\\mypygui_import\\edit_files.py }"]                         ,shell=True)                                                                     ),

("ahkscripts.ahk"  ,BOX_1,"#599b59","#ffffff",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,5),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\ahkscripts.ahk }"]                                        ,shell=True)                                                                     ),

("backup.ps1"      ,BOX_1,"#499eda","#000000",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,0),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\backup.ps1 }"]                                            ,shell=True)                                                                     ),
("startup.ps1"     ,BOX_1,"#499eda","#000000",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,0),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\startup.ps1 }"]                                           ,shell=True)                                                                     ),
("update.ps1"      ,BOX_1,"#499eda","#000000",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,5),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\update.ps1 }"]                                            ,shell=True)                                                                     ),

("glaze-wm.yaml"   ,BOX_1,"#9068b0","#ffffff",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,0),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\Users\\nahid\\.glaze-wm\\config.yaml }"]                       ,shell=True)                                                                     ),
("komorebi.json"   ,BOX_1,"#b7b73b","#000000",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,5),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\Users\\nahid\\komorebi.json }"]                                ,shell=True)                                                                     ),

("whkd"            ,BOX_1,"#ffffff","#000000",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,5),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\Users\\nahid\\.config\\whkdrc }"]                              ,shell=True)                                                                     ),

("yasb-config.yaml",BOX_1,"#9068b0","#ffffff",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,0),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\yasb\\config.yaml }"]                           ,shell=True)                                                                     ),
("yasb-styles.css" ,BOX_1,"#5995af","#ffffff",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,0),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\yasb\\styles.css }"]                            ,shell=True)                                                                     ),
("yasb-folder"     ,BOX_1,"#ffd359","#000000",1,47,"flat",("calibri",12,"bold"),0,0,(0,0),(0,0),lambda: subprocess.Popen(["Start","powershell","-Command","& { code C:\\ms1\\yasb\\ }"]                                        ,shell=True)                                                                     ),
]
for button_props in button_properties:
    create_button(*button_props)


#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
