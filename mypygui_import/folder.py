



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



#! Close Window
def close_window(event=None):
    ROOT.destroy()

#!? Main ROOT BOX
# ROOT1 = tk.Frame(ROOT, bg="#1d2027")
# ROOT1.pack(side="right", anchor="ne", pady=(3,2),padx=(3,1))

# LB_XXX=tk.Label(ROOT1, text="\uf2d3", bg="#1d2027",fg="#ff0000",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",18,"bold"))
# LB_XXX.pack(side="left",padx=(1,10),pady=(0,0))
# LB_XXX.bind("<Button-1>",close_window)






WINDOWSTOOLS_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1200 , height=800)
WINDOWSTOOLS_FRAME.pack_propagate(True)
BOX = tk.Frame(WINDOWSTOOLS_FRAME, bg="#1D2027")
BOX.pack(side="top", pady=(30,2), padx=(5,1), anchor="center", fill="x")

# BACK = tk.Button(BOX, text="\ueb6f \ueb6f \ueb6f", width=50, bg="#1d2027", fg="#ffffff", command=lambda: switch_to_frame(MAIN_FRAME, WINDOWSTOOLS_FRAME))
# BACK.grid(row=0, column=0, columnspan=3, pady=(0, 10))  # Add BACK button at the top

def Folder(WINDOWSTOOLS_FRAME):
    items = [
("#204892", "#ffffff", "\uf07c AppData",        {"command": "explorer C:\\Users\\nahid\\AppData"}),
("#204892", "#ffffff", "\uf07c AppsFolder",     {"command": "explorer shell:AppsFolder"}),
("#204892", "#ffffff", "\uf07c Packages",       {"command": "explorer C:\\Users\\nahid\\AppData\\Local\\Packages"}),
("#204892", "#ffffff", "\uf07c ProgramData",    {"command": "explorer C:\\ProgramData"}),
("#204892", "#ffffff", "\uf07c Scoop",          {"command": "explorer C:\\Users\\nahid\\scoop"}),
("#204892", "#ffffff", "\uf07c Software",       {"command": "explorer D:\\software"}),
("#204892", "#ffffff", "\uf07c Song",           {"command": "explorer D:\\song"}),
("#204892", "#ffffff", "\uf07c Startup-System", {"command": "explorer C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"}),
("#204892", "#ffffff", "\uf07c Startup-User",   {"command": "explorer C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"}),
("#204892", "#ffffff", "\uf07c Temp-AppDate",   {"command": "explorer C:\\Users\\nahid\\AppData\\Local\\Temp"}),
("#204892", "#ffffff", "\uf07c Temp-Windows",   {"command": "explorer C:\\Windows\\Temp"}),
("#204892", "#ffffff", "\uf07c WindowsApp",     {"command": "explorer C:\\Program Files\\WindowsApps"}),
# ("#204892", "#ffffff", "\uf07c .glaze-wm",              {"command": "explorer C:\\Users\\nahid\\.glaze-wm"}),
# ("#204892", "#ffffff", "\uf07c ",              {"command": ""}),
# ("#204892", "#ffffff", "\uf07c Git-Projects",              {"command": "explorer C:\\Users\\nahid\\OneDrive\\Git"}),

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

#! Ending
WINDOWSTOOLS_FRAME.pack()
ROOT.mainloop()
