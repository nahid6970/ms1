import subprocess
import subprocess
import tkinter as tk
from tkinter import Canvas, Scrollbar
from tkinter import ttk
import customtkinter
import os
import ctypes

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)
set_console_title("App List")

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
    BORDER_FRAME = tk.Frame(parent, bg="#d32f2f", bd=0, highlightthickness=0)
    BORDER_FRAME.place(x=0, y=0, relwidth=1, relheight=1)
    return BORDER_FRAME

# Create main window
ROOT = tk.Tk()
ROOT.title("Folder")
ROOT.attributes('-topmost', True)  # Set always on top
# ROOT.geometry("520x800")
ROOT.configure(bg="#d32f2f")
ROOT.overrideredirect(True)  # Remove default borders

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Drag only from the header area so interactive widgets like the search bar
# do not move the whole window.
DRAG_BAR = tk.Frame(BORDER_FRAME, bg="#1d2027", height=24)
DRAG_BAR.pack(side="top", fill="x")
DRAG_BAR.pack_propagate(False)

# Add bindings to make the window movable
DRAG_BAR.bind("<ButtonPress-1>", start_drag)
DRAG_BAR.bind("<ButtonRelease-1>", stop_drag)
DRAG_BAR.bind("<B1-Motion>", do_drag)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width - 430
y = screen_height//2 - 600//2
ROOT.geometry(f"430x600+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=430, height=600) #!
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(fill="both", expand=True, padx=1, pady=1)


#! Close Window
def close_window(event=None):
    ROOT.destroy()

#!? Main ROOT BOX
ROOT1 = tk.Frame(DRAG_BAR, bg="#1d2027")
ROOT1.pack(side="right", anchor="ne", pady=(1, 0), padx=(3, 1))

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

#! Applist
LB_INITIALSPC = tk.Label(MAIN_FRAME, text="",  bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 16, "bold"))
LB_INITIALSPC.pack(side="top", anchor="ne", padx=(0,0), pady=(0,0))

# # Create the search box label
# search_label = tk.Label(Page1, text="Search:", bg="#1d2027", fg="#fff", font=("calibri", 12, "bold"))
# search_label.pack(side="top", anchor="center", padx=(20, 0), pady=(10, 0))

# Create a frame for search and add button
search_controls_frame = tk.Frame(MAIN_FRAME, bg="#1d2027")
search_controls_frame.pack(side="top", anchor="center", pady=(0, 10))

# Create the search entry
search_entry = customtkinter.CTkEntry(search_controls_frame, font=("calibri", 14), width=250, placeholder_text="Search apps...")
search_entry.grid(row=0, column=0, padx=(20, 10), pady=(0, 0))

def add_app_window():
    add_window = customtkinter.CTkToplevel(ROOT)
    add_window.title("Add New Application")
    add_window.geometry("450x380")
    add_window.attributes('-topmost', True)

    frame = customtkinter.CTkFrame(add_window)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    labels = ["App Name:", "Scoop Name:", "Scoop Path:", "Winget Name:", "Winget Path:"]
    entries = {}

    for i, text in enumerate(labels):
        customtkinter.CTkLabel(frame, text=text, font=("calibri", 14)).grid(row=i, column=0, padx=10, pady=10, sticky="w")
        entry = customtkinter.CTkEntry(frame, width=250)
        entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
        entries[text.replace(":", "").replace(" ", "_").lower()] = entry

    def save_new_app():
        new_app = {
            "name": entries["app_name"].get(),
            "scoop_name": entries["scoop_name"].get(),
            "scoop_path": entries["scoop_path"].get(),
            "winget_name": entries["winget_name"].get(),
            "winget_path": entries["winget_path"].get()
        }
        applications.append(new_app)
        save_applications(applications)
        add_window.destroy()
        refresh_app_list()

    customtkinter.CTkButton(frame, text="Save App", command=save_new_app, font=("calibri", 14, "bold"), fg_color="#4CAF50", hover_color="#45a049").grid(row=len(labels), columnspan=2, pady=20)

add_app_button = customtkinter.CTkButton(search_controls_frame, text="+", command=add_app_window, width=32, height=32, font=("calibri", 18, "bold"), fg_color="#007bff", hover_color="#0056b3")
add_app_button.grid(row=0, column=1, padx=(0, 20), pady=(0, 0))

def check_installation(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt):
    scoop_installed = os.path.exists(scoop_path)
    winget_installed = os.path.exists(winget_path)
    application_installed = scoop_installed or winget_installed
    chkbx_var.set(1 if application_installed else 0)

    # Change text color based on installation status if not already checked
    text_color = "green" if application_installed else "red"

    # Update the label with installation source
    installation_source = ""
    if scoop_installed:
        installation_source = "[S]"
        text_color = "#FFFFFF"  # Set color to white for [S]
    elif winget_installed:
        installation_source = "[W]"
        text_color = "#41abff"   # Set color to blue for [W]
    else:
        installation_source = "[X]"
        text_color = "#FF0000"    # Set color to red for [X]

    chkbox_bt.config(text=f"{app_name} {installation_source}", foreground=text_color)

def install_application(app_name, scoop_name, scoop_path, winget_name, winget_path, chkbx_var, chkbox_bt):
    install_options = []
    if winget_name:
        install_options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'start pwsh -NoExit -Command "winget install {winget_name}"', shell=True)})
    if scoop_name:
        install_options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'start pwsh -NoExit -Command "scoop install {scoop_name}"', shell=True)})
    show_options(install_options)

def uninstall_application(app_name, scoop_name, scoop_path, winget_name, winget_path, chkbx_var, chkbox_bt):
    uninstall_options = []
    if winget_name:
        uninstall_options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'start pwsh -NoExit -Command "winget uninstall {winget_name}"', shell=True)})
    if scoop_name:
        uninstall_options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'start pwsh -NoExit -Command "scoop uninstall {scoop_name}"', shell=True)})
    show_options(uninstall_options)

def open_file_location(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt):
    options = []
    if winget_path:
        options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'explorer /select,"{winget_path}"')})
    if scoop_path:
        options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'explorer /select,"{scoop_path}"')})
    show_options(options)

def show_options(options):
    top = tk.Toplevel()
    top.title("Select Source")
    top.geometry("300x100")
    top.configure(bg="#282c34")
    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = 800
    top.geometry(f"300x100+{x}+{y}")

    frame = tk.Frame(top, bg="#1d2027")
    frame.pack(side="top", expand=True, fill="none", anchor="center")

    for option in options:
        # Set background color based on the source type
        if "Winget" in option["text"]:
            bg_color = "#0078D7"
            fg_color = "#FFFFFF"
        elif "Scoop" in option["text"]:
            bg_color = "#FFFFFF"
            fg_color = "#000000"
        else:
            bg_color = "#1d2027"
            fg_color = "#000000"

        btn = tk.Button(frame, text=option["text"], command=option["command"], background=bg_color, foreground=fg_color, padx=10, pady=5, borderwidth=2, relief="raised")
        btn.pack(side="left", padx=5, pady=5, anchor="center")

def edit_application(app_to_edit):
    edit_window = customtkinter.CTkToplevel(ROOT)
    edit_window.title("Edit Application")
    edit_window.geometry("450x380")
    edit_window.attributes('-topmost', True)

    frame = customtkinter.CTkFrame(edit_window)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    labels = ["App Name:", "Scoop Name:", "Scoop Path:", "Winget Name:", "Winget Path:"]
    entries = {}

    for i, text in enumerate(labels):
        customtkinter.CTkLabel(frame, text=text, font=("calibri", 14)).grid(row=i, column=0, padx=10, pady=10, sticky="w")
        entry = customtkinter.CTkEntry(frame, width=250)
        entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
        entries[text.replace(":", "").replace(" ", "_").lower()] = entry

    # Pre-fill entries with current app data
    entries["app_name"].insert(0, app_to_edit["name"])
    entries["scoop_name"].insert(0, app_to_edit.get("scoop_name", ""))
    entries["scoop_path"].insert(0, app_to_edit.get("scoop_path", ""))
    entries["winget_name"].insert(0, app_to_edit.get("winget_name", ""))
    entries["winget_path"].insert(0, app_to_edit.get("winget_path", ""))

    def save_edited_app():
        app_to_edit["name"] = entries["app_name"].get()
        app_to_edit["scoop_name"] = entries["scoop_name"].get()
        app_to_edit["scoop_path"] = entries["scoop_path"].get()
        app_to_edit["winget_name"] = entries["winget_name"].get()
        app_to_edit["winget_path"] = entries["winget_path"].get()
        save_applications(applications)
        edit_window.destroy()
        refresh_app_list()

    customtkinter.CTkButton(frame, text="Save Changes", command=save_edited_app, font=("calibri", 14, "bold"), fg_color="#007bff", hover_color="#0056b3").grid(row=len(labels), columnspan=2, pady=20)

def delete_application(app_to_delete):
    global applications
    applications = [app for app in applications if app != app_to_delete]
    save_applications(applications)
    refresh_app_list()

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "data.json")

def load_applications():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            apps = json.load(f)
            # Sort applications by name
            apps.sort(key=lambda x: x.get("name", "").lower())
            
            for app in apps:
                if app.get("scoop_name") and not app.get("scoop_path"):
                    app["scoop_path"] = os.path.join(os.path.expanduser("~"), "scoop", "apps", app["scoop_name"], "current")
            
            return apps
    return []

def save_applications(apps):
    serializable_apps = []
    for app in apps:
        scoop_path = app.get("scoop_path", "")
        if not scoop_path and app.get("scoop_name"):
            scoop_path = os.path.join(os.path.expanduser("~"), "scoop", "apps", app["scoop_name"], "current")
            app["scoop_path"] = scoop_path
            
        serializable_apps.append({
            "name": app["name"],
            "scoop_name": app["scoop_name"],
            "scoop_path": scoop_path,
            "winget_name": app["winget_name"],
            "winget_path": app["winget_path"]
        })
    with open(DATA_FILE, "w") as f:
        json.dump(serializable_apps, f, indent=4)

applications = load_applications()

customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

# Create canvas and scrollbar
canvas = tk.Canvas(MAIN_FRAME, bg="#1d2027", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

#! scrollbar Start
def on_mousewheel(event):
    # Get current scroll position
    current_top = canvas.canvasy(0)
    scroll_region = canvas.cget('scrollregion')
    
    if scroll_region:
        # Parse scroll region to get bounds
        x1, y1, x2, y2 = map(float, scroll_region.split())
        
        # Calculate scroll amount
        scroll_amount = -1 * (event.delta // 120)
        
        # Prevent scrolling above the top of content
        if current_top <= y1 and scroll_amount < 0:
            canvas.yview_moveto(0.0)
            return "break"
        
        # Prevent scrolling below the bottom of content
        canvas_height = canvas.winfo_height()
        if current_top + canvas_height >= y2 and scroll_amount > 0:
            return "break"
        
        canvas.yview_scroll(scroll_amount, "units")
    return "break"

# Bind mousewheel to the main frame and canvas
def bind_mousewheel_to_widget(widget):
    widget.bind("<MouseWheel>", on_mousewheel)
    for child in widget.winfo_children():
        bind_mousewheel_to_widget(child)

# Initial binding
MAIN_FRAME.bind("<MouseWheel>", on_mousewheel)
canvas.bind("<MouseWheel>", on_mousewheel)

scrollbar = customtkinter.CTkScrollbar(MAIN_FRAME, orientation="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

#! scrollbar End

# Create a frame inside the canvas
frame = tk.Frame(canvas, bg="#1d2027")
canvas_window = canvas.create_window((0, 0), window=frame, anchor="nw")

# Function to update scroll region and canvas window
def update_scroll_region():
    # Update the scroll region
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Make sure the frame fills the canvas width
    canvas_width = canvas.winfo_width()
    frame_width = frame.winfo_reqwidth()
    if canvas_width > frame_width:
        canvas.itemconfig(canvas_window, width=canvas_width)

def toggle_actions(a_frame):
    if a_frame.winfo_viewable():
        a_frame.grid_remove()
    else:
        a_frame.grid(row=1, column=0, pady=(0,5), padx=(32,0), sticky="w")
    ROOT.after(10, update_scroll_region)

def refresh_app_list():
    global applications
    applications = load_applications()
    for widget in frame.winfo_children():
        widget.destroy()
    
    row_number = 0
    for app in applications:
        app["chkbx_var"] = tk.IntVar()
        app_frame = tk.Frame(frame, bg="#1d2027")
        app_frame.grid(row=row_number, column=0, padx=(10,0), pady=(0,0), sticky="ew")
        app["frame"] = app_frame
        row_number += 1

        app_name = app["name"]
        scoop_name = app["scoop_name"]
        scoop_path = app["scoop_path"]
        winget_name = app["winget_name"]
        winget_path = app["winget_path"]
        chkbx_var = app["chkbx_var"]

        # Frame for action buttons (initially hidden)
        actions_frame = tk.Frame(app_frame, bg="#1d2027")

        chkbox_bt = tk.Checkbutton(app_frame, text=app_name, variable=chkbx_var, font=("JetBrainsMono NF", 12, "bold"), background="#1d2027", activebackground="#1d2027", selectcolor="#1d2027", padx=10, pady=1, borderwidth=2, relief="flat", anchor="w")
        chkbox_bt.configure(command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: check_installation(name, scoop, winget, var, cb))
        chkbox_bt.bind("<Button-1>", lambda event, a_frame=actions_frame: toggle_actions(a_frame))

        ins_bt = tk.Button(actions_frame, text="\uf192", foreground="#00FF00", background="#1d2027", font=("Jetbrainsmono nfp", 10), relief="flat", command=lambda name=app_name, scoop=scoop_name, scoop_path=scoop_path, winget=winget_name, winget_path=winget_path, var=chkbx_var, cb=chkbox_bt: install_application(name, scoop, scoop_path, winget, winget_path, var, cb))
        unins_bt = tk.Button(actions_frame, text="\uf192", foreground="#FF0000",  background="#1d2027", font=("Jetbrainsmono nfp", 10), relief="flat", command=lambda name=app_name, scoop=scoop_name, scoop_path=scoop_path, winget=winget_name, winget_path=winget_path, var=chkbx_var, cb=chkbox_bt: uninstall_application(name, scoop, scoop_path, winget, winget_path, var, cb))
        open_bt = tk.Button(actions_frame, text="\uf192", foreground="#eac353", background="#1d2027", font=("Jetbrainsmono nfp", 10), relief="flat", command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: open_file_location(name, scoop, winget, var, cb))
        edit_bt = tk.Button(actions_frame, text="\uf044", foreground="#007bff", background="#1d2027", font=("Jetbrainsmono nfp", 10), relief="flat", command=lambda app=app: edit_application(app))
        delete_bt = tk.Button(actions_frame, text="\uf192", foreground="#dc3545", background="#1d2027", font=("Jetbrainsmono nfp", 10), relief="flat", command=lambda app=app: delete_application(app))

        # Layout for buttons inside the actions_frame
        actions_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        ins_bt.grid(row=0, column=0)
        unins_bt.grid(row=0, column=1)
        open_bt.grid(row=0, column=2)
        edit_bt.grid(row=0, column=3)
        delete_bt.grid(row=0, column=4)

        # Layout for the main app entry
        chkbox_bt.grid(row=0, column=0, sticky="ew")
        actions_frame.grid_remove()  # Hide by default

        check_installation(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt)
    
    # Update scroll region after all widgets are created
    ROOT.after(1, update_scroll_region)
    
    # Bind mousewheel to all new widgets
    ROOT.after(10, lambda: bind_mousewheel_to_widget(frame))

# Initial display of applications
refresh_app_list()

def filter_apps(event=None):
    search_query = search_entry.get().lower()
    for app in applications:
        app_name = app["name"]
        app_frame = app["frame"]
        if search_query in app_name.lower():
            app_frame.grid()
        else:
            app_frame.grid_remove()
    
    # Update scroll region after filtering
    ROOT.after(1, update_scroll_region)

# Bind the filtering function to the KeyRelease event of the search entry
search_entry.bind("<KeyRelease>", filter_apps)

# Handle canvas resize
def on_canvas_configure(event):
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind("<Configure>", on_canvas_configure)

#! Ending
ROOT.mainloop()
