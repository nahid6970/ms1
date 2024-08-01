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

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.bg = kw.pop('bg', "#000000")
        self.h_bg = kw.pop('h_bg', "red")
        self.default_fg = kw.pop('default_fg', "#FFFFFF")
        self.h_fg = kw.pop('h_fg', "#000000")
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(bg=self.bg, fg=self.default_fg)

    def on_enter(self, event):
        self.configure(bg=self.h_bg, fg=self.h_fg)

    def on_leave(self, event):
        self.configure(bg=self.bg, fg=self.default_fg)


def close_window(event=None):
    ROOT.destroy()
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

# x = screen_width - 200
# y = screen_height//2 - 700//2

# mouse_x = ROOT.winfo_pointerx()
# mouse_y = ROOT.winfo_pointery()
# window_offset = 10
# x = mouse_x
# y = mouse_y + window_offset
x= screen_width - 200
y=screen_height//2 - 700//2
ROOT.geometry(f"200x700+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=400, height=700) #!
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1)  # Add some padding at the top
MAIN_FRAME.pack(expand=True)

#! Folder
default_font = ("Jetbrainsmono nf", 14, "italic")
ROOT.option_add("*Font", default_font)

BOX_2 = tk.Frame(MAIN_FRAME, bg="#1d2027")
BOX_2.pack(pady=(5,0))

bt =HoverButton(BOX_2,text="\uf52f"               ,bg="#fc0808",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=20,relief="solid",font=("jetbrainsmono nf", 10, "normal") ,command=close_window); bt.pack(side="top",padx=(0,0),pady=(0,0))

bt =HoverButton(BOX_2,text="\uf07c .yasb"         ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\ms1\\yasb"],shell=True),close_window()));                                                                         bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c .glaze-wm"     ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Users\\nahid\\.glaze-wm"                                                          ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c All Apps"      ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","shell:AppsFolder"                                                                     ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c AppData"       ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData"                                                            ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Git-Projects"  ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Users\\nahid\\OneDrive\\Git"                                                      ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Packages"      ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Local\\Packages"                                           ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c ProgramData"   ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\ProgramData"                                                                      ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Scoop"         ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Users\\nahid\\scoop"                                                              ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Software"      ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","D:\\software"                                                                         ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Song"          ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","D:\\song"                                                                             ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c WindowsApp"    ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Program Files\\WindowsApps"                                                       ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Startup-System",bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"                   ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Startup-User"  ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Temp-AppDate"  ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Local\\Temp"                                               ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))
bt =HoverButton(BOX_2,text="\uf07c Temp-Windows"  ,bg="#000000",activebackground="green",h_bg="red",fg="#FFFFFF",h_fg="#000000",height=0,width=0,relief="solid",command=lambda:(subprocess.Popen(["explorer","C:\\Windows\\Temp"                                                                    ],shell=True),close_window())); bt.pack(side="top", anchor="w",padx=(0,0),pady=(0,0))




#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()



# def create_button(text, frame, bg_color, fg_color, height, width, relief, font, padx_button, pady_button, padx_pack, pady_pack, anchor, command):
#     button = tk.Button(frame, anchor=anchor, text=text, bg=bg_color, fg=fg_color, height=height, width=width, relief=relief, font=font, padx=padx_button, pady=pady_button, command=command)
#     button.pack(padx=padx_pack, pady=pady_pack)
#     return button

# BOX_1 = tk.Frame(MAIN_FRAME, bg="#282c34")
# BOX_1.pack(side="top", pady=(30,0), padx=(0,0))

# button_properties =[
# ("\uf07c .yasb"          ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\.yasb"]                                                              ,shell=True)),
# ("\uf07c .glaze-wm"      ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\.glaze-wm"]                                                          ,shell=True)),
# ("\uf07c All Apps"       ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","shell:AppsFolder"]                                                                     ,shell=True)),
# ("\uf07c AppData"        ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData"]                                                            ,shell=True)),
# ("\uf07c Git Projects"   ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\OneDrive\\Git"]                                                      ,shell=True)),
# ("\uf07c Packages"       ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Local\\Packages"]                                           ,shell=True)),
# ("\uf07c ProgramData"    ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\ProgramData"]                                                                      ,shell=True)),
# ("\uf07c Scoop"          ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\scoop"]                                                              ,shell=True)),
# ("\uf07c Software"       ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","D:\\software"]                                                                         ,shell=True)),
# ("\uf07c Song"           ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","D:\\song"]                                                                             ,shell=True)),
# ("\uf07c WindowsApp"     ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,0),(0,0),"w",lambda: subprocess.Popen(["explorer","C:\\Program Files\\WindowsApps"]                                                       ,shell=True)),
# ("\uf07c Startup System" ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,1),(3,0),"w",lambda: subprocess.Popen(["explorer","C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"]                   ,shell=True)),
# ("\uf07c Startup User"   ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(1,0),(3,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"],shell=True)),
# ("\uf07c Temp-AppDate"   ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(0,1),(3,0),"w",lambda: subprocess.Popen(["explorer","C:\\Users\\nahid\\AppData\\Local\\Temp"]                                               ,shell=True)),
# ("\uf07c Temp-Windows"   ,BOX_1,"#1D2027","#ffffff",1,15,"flat",("calibri",14,"bold"),0,0,(1,0),(3,0),"w",lambda: subprocess.Popen(["explorer","C:\\Windows\\Temp"]                                                                    ,shell=True)),
# ]
# for button_props in button_properties:
#     create_button(*button_props)