import subprocess
import tkinter as tk
from PIL import Image, ImageTk


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





#! Desktop
BOX_1_2nd = tk.Frame(MAIN_FRAME, bg="#1d2027")
BOX_1_2nd.pack(pady=(30,0))

icon_folder     =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_applist    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_appstore   =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_ffmpeg     =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_find       =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_process    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_tools      =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))
icon_ScriptList =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-20x20.png"))

def create_button_advanced(parent, text="", image=None, command=None, compound=None, height=0, width=0, bg="#e7d86a", fg="#1D2027", font=("JetBrainsMono NF", 13, "bold"), anchor="center", bd=0, relief="flat", highlightthickness=4, activebackground="#000000", activeforeground="#f6d24a", cursor="hand2", side="left", padx=(0,0), pady=(0,0)):
    button = tk.Button(parent, text=text, image=image, command=command, compound=compound, height=height, width=width, bg=bg, fg=fg, font=font, anchor=anchor, bd=bd, relief=relief, highlightthickness=highlightthickness, activebackground=activebackground, activeforeground=activeforeground, cursor=cursor)
    button.pack(side="top", padx=padx, pady=pady)
    return button

# Creating buttons with advanced properties
button_properties_advanced =[
{"parent": BOX_1_2nd,"text": "Folder"    ,"image": icon_folder     ,"compound": tk.LEFT,"height": 0,"width": 0,"bg": "#e7d86a","fg": "#1D2027","font": ("JetBrainsMono NF",13,"bold"),"anchor": "center","bd": 0,"relief": "flat","highlightthickness": 4,"activebackground": "#000000","activeforeground": "#f6d24a","cursor": "hand2" ,"command": lambda: subprocess.Popen(["powershell","start-process","C:\\ms1\\mypygui_import\\folder.py","-WindowStyle","Hidden"],shell=True)},
{"parent": BOX_1_2nd,"text": "AppList"   ,"image": icon_applist    ,"compound": tk.LEFT,"height": 0,"width": 0,"bg": "#3498db","fg": "#1D2027","font": ("JetBrainsMono NF",13,"bold"),"anchor": "center","bd": 0,"relief": "flat","highlightthickness": 4,"activebackground": "#000000","activeforeground": "#f6d24a","cursor": "hand2" ,"command": lambda: subprocess.Popen(["powershell","start-process","C:\\ms1\\mypygui_import\\applist.py"],shell=True)},
{"parent": BOX_1_2nd,"text": "AppStore"  ,"image": icon_appstore   ,"compound": tk.LEFT,"height": 0,"width": 0,"bg": "#426f7e","fg": "#FFFFFF","font": ("JetBrainsMono NF",13,"bold"),"anchor": "center","bd": 0,"relief": "flat","highlightthickness": 4,"activebackground": "#000000","activeforeground": "#f6d24a","cursor": "hand2" ,"command": lambda: subprocess.Popen(["powershell","start-process","C:\\ms1\\mypygui_import\\app_store.py"],shell=True)},
{"parent": BOX_1_2nd,"text": "Process"   ,"image": icon_process    ,"compound": tk.LEFT,"height": 0,"width": 0,"bg": "#cc2400","fg": "#ffffff","font": ("JetBrainsMono NF",13,"bold"),"anchor": "center","bd": 0,"relief": "flat","highlightthickness": 4,"activebackground": "#000000","activeforeground": "#f6d24a","cursor": "hand2" ,"command": lambda: subprocess.Popen(["powershell","start-process","C:\\ms1\\mypygui_import\\process.py"],shell=True)},
{"parent": BOX_1_2nd,"text": "Tools"     ,"image": icon_tools      ,"compound": tk.LEFT,"height": 0,"width": 0,"bg": "#454545","fg": "#FFFFFF","font": ("JetBrainsMono NF",13,"bold"),"anchor": "center","bd": 0,"relief": "flat","highlightthickness": 4,"activebackground": "#000000","activeforeground": "#f6d24a","cursor": "hand2" ,"command": lambda: subprocess.Popen(["powershell","start-process","C:\\ms1\\mypygui_import\\tools.py","-WindowStyle","Hidden"],shell=True)},
{"parent": BOX_1_2nd,"text": "Script"    ,"image": icon_ScriptList ,"compound": tk.LEFT,"height": 0,"width": 0,"bg": "#366c9c","fg": "#f6d24a","font": ("JetBrainsMono NF",13,"bold"),"anchor": "center","bd": 0,"relief": "flat","highlightthickness": 4,"activebackground": "#000000","activeforeground": "#f6d24a","cursor": "hand2" ,"command": lambda: subprocess.Popen(["powershell","start-process","C:\\ms1\\mypygui_import\\script_list.py","-WindowStyle","Hidden"],shell=True)},
]
advanced_buttons = [create_button_advanced(**prop) for prop in button_properties_advanced]



#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
