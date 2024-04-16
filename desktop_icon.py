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

ROOT = tk.Tk()
ROOT.title("Folder")
# ROOT.attributes('-topmost', True)
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)

BORDER_FRAME = create_custom_border(ROOT)

ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = 0
y = 39
ROOT.geometry(f"1920x500+{x}+{y}")

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920, height=500) #!
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1) 
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



import os
from tkinter import Tk, Button, simpledialog, messagebox
def launch_shortcut():
    password = simpledialog.askstring("Password", "Enter the password:", show='*')
    if password == "753951":
        shortcut_path = "C:/Riot Games/Riot Client/RiotClientServices.exe"
        command = [shortcut_path, '--launch-product=valorant', '--launch-patchline=live']
        os.chdir("C:/Riot Games/Riot Client")
        subprocess.Popen(command)
    else:
        messagebox.showerror("Error", "Incorrect password!")


#! Desktop
column_1 = tk.Frame(MAIN_FRAME, bg="#393f4d")
column_1.pack(pady=(0,0), side="left")

column_2 = tk.Frame(MAIN_FRAME, bg="#393f4d")
column_2.pack(pady=(0,0), side="left")

column_3 = tk.Frame(MAIN_FRAME, bg="#393f4d")
column_3.pack(pady=(0,0), side="left")

column_4 = tk.Frame(MAIN_FRAME, bg="#393f4d")
column_4.pack(pady=(0,0), side="left")

icon_folder  =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Dolphin_icon-50x50.png"))
icon_thispc  =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\this-pc-computer-50x50.png"))
icon_control =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Control-Panel-icon-50x50.png"))
icon_sonarr  =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\sonarr-50x50.png"))
icon_radarr  =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\radarr-50x50.png"))
icon_music   =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\Folder Music-50x50.png"))
icon_download=ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\downloadfolder-50x50.png"))
icon_software=ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\pngegg (1)-50x50.png"))
icon_user    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\user (1)-50x50.png"))
icon_sage    =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\valo_sage_5050.png"))
desktop_ok   =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\desktopok220-220-50x50.png"))
local_send   =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\localsend-50x50.ico"))
audio_relay   =ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\audiorelaya-50x50.png"))


def create_button_advanced(parent, text="", image=None, command=None, compound=None, height=0, width=0, bg="#e7d86a", fg="#1D2027", font=("JetBrainsMono NF", 13, "bold"), anchor="center", bd=0, relief="flat", highlightthickness=4, activebackground="#000000", activeforeground="#f6d24a", cursor="hand2", side="top", padx=(0,0), pady=(0,0)):
    button = tk.Button(parent, text=text, image=image, command=command, compound=compound, height=height, width=width, bg=bg, fg=fg, font=font, anchor=anchor, bd=bd, relief=relief, highlightthickness=highlightthickness, activebackground=activebackground, activeforeground=activeforeground, cursor=cursor)
    button.pack(side="top", padx=padx, pady=pady)
    return button

# Creating buttons with advanced properties
button_properties_advanced =[
{"parent":column_1,"text":"User"        ,"image":icon_user          ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"C:\\Users\\nahid"]                                                                    ,shell=True)}                              ,
{"parent":column_1,"text":"ThisPC"      ,"image":icon_thispc        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"],shell=True)}                                                                           ,
{"parent":column_1,"text":"RecycleBin"  ,"image":icon_folder        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"/root                                                                                 ,::{645FF040-5081-101B-9F08-00AA002F954E}"],shell=True)},
{"parent":column_1,"text":"ControlPanel","image":icon_control       ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["control"]                                                          ,shell=True)}                                                                           ,
{"parent":column_1,"text":"Startup"     ,"image":icon_folder        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\StartMenu\\Programs\\Startup"],shell=True)}                              ,
{"parent":column_1,"text":"WindowsApp"  ,"image":icon_folder        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"C:\\ProgramFiles\\WindowsApps"]                                                       ,shell=True)}                              ,

{"parent":column_2,"text":"Packages"    ,"image":icon_folder        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"C:\\Users\\nahid\\AppData\\Local\\Packages"]                                          ,shell=True)}                              ,
{"parent":column_2,"text":"AppData"     ,"image":icon_folder        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"C:\\Users\\nahid\\AppData"]                                                           ,shell=True)}                              ,
{"parent":column_2,"text":"Music"       ,"image":icon_music         ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"D:\\song"]                                                                            ,shell=True)}                              ,
{"parent":column_2,"text":"Software"    ,"image":icon_software      ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"D:\\software"]                                                                        ,shell=True)}                              ,
{"parent":column_2,"text":"Downloads"   ,"image":icon_download      ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"D:\\Downloads"]                                                                       ,shell=True)}                              ,

{"parent":column_3,"text":"ms1"         ,"image":icon_folder        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"C:\\ms1"]                                                                             ,shell=True)}                              ,
{"parent":column_3,"text":"ms2"         ,"image":icon_folder        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"C:\\ms2"]                                                                             ,shell=True)}                              ,
{"parent":column_3,"text":"Sonarr"      ,"image":icon_sonarr        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer"                                                          ,"D:\\Downloads\\@Sonarr"]                                                              ,shell=True)}                              ,
{"parent":column_3,"text":"Radarr"      ,"image":icon_radarr        ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["explorer","D:\\Downloads\\@Radarr"]                                                              ,shell=True)}                              ,
{"parent":column_3,"text":"VLR"         ,"image":icon_sage          ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":launch_shortcut},

{"parent":column_4,"text":"DesktopOK"   ,"image":desktop_ok         ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["C:\\Users\\nahid\\OneDrive\\backup\\desktopok\\DesktopOK_x64.exe"] ,shell=True)},
{"parent":column_4,"text":"Local Send"   ,"image":local_send         ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["C:\\Users\\nahid\\scoop\\apps\\localsend\\current\\localsend_app.exe"] ,shell=True)},
{"parent":column_4,"text":"AudioRelay"   ,"image":audio_relay         ,"compound":tk.TOP  ,"height":0,"width":100  ,"bg":"#1D2027","fg":"#fff","font":("JetBrainsMonoNF",12,"bold"),"anchor":"center","bd":0,"relief":"flat","highlightthickness":4,"activebackground":"#000000","activeforeground":"#f6d24a","cursor":"hand2","command":lambda:subprocess.Popen(["C:\\Program Files (x86)\\AudioRelay\\AudioRelay.exe"] ,shell=True)},


]
advanced_buttons = [create_button_advanced(**prop) for prop in button_properties_advanced]



#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
