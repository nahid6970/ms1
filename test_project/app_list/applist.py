import subprocess
import tkinter as tk
from tkinter import Canvas, Scrollbar, messagebox, simpledialog
from tkinter import ttk
import os
import ctypes
import json

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)
set_console_title("App List")

# JSON file path
JSON_FILE = "applications.json"

# Default applications data
DEFAULT_APPLICATIONS = [
    {
        "name": "DotNet_6",
        "scoop_name": "ScoopName",
        "scoop_path": "",
        "winget_name": "Microsoft.DotNet.DesktopRuntime.6",
        "winget_path": r"C:\Program Files\dotnet\shared\Microsoft.NETCore.App\6.0.29\createdump.exe"
    },
    {
        "name": "Alacritty",
        "scoop_name": "alacritty",
        "scoop_path": r"C:\Users\nahid\scoop\apps\alacritty\current\alacritty.exe",
        "winget_name": "Alacritty.Alacritty",
        "winget_path": r"C:\Program Files\Alacritty\alacritty.exe"
    },
    {
        "name": "AutoHotkey",
        "scoop_name": "autohotkey",
        "scoop_path": "",
        "winget_name": "AutoHotkey.AutoHotkey",
        "winget_path": r"C:\Users\nahid\AppData\Local\Programs\AutoHotkey\v2\AutoHotkey64.exe"
    }
]

def load_applications():
    """Load applications from JSON file or create default if not exists"""
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            save_applications(DEFAULT_APPLICATIONS)
            return DEFAULT_APPLICATIONS
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load applications: {str(e)}")
        return DEFAULT_APPLICATIONS

def save_applications(apps):
    """Save applications to JSON file"""
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as file:
            json.dump(apps, file, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save applications: {str(e)}")

# Load applications from JSON
applications = load_applications()

# Variables to track the position of the mouse when clicking
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
ROOT.title("App Manager")
ROOT.attributes('-topmost', True)
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Add bindings to make the window movable
ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width - 450
y = screen_height//2 - 650//2
ROOT.geometry(f"450x650+{x}+{y}")

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=450, height=650)
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1)
MAIN_FRAME.pack(expand=True)

# Close Window
def close_window(event=None):
    ROOT.destroy()

# Main ROOT BOX
ROOT1 = tk.Frame(ROOT, bg="#1d2027")
ROOT1.pack(side="right", anchor="ne", pady=(3,2), padx=(3,1))

def create_label(text, parent, bg, fg, width, height, relief, font, ht, htc, padx, pady, anchor, row, column, rowspan, columnspan):
    label = tk.Label(parent, text=text, bg=bg, fg=fg, width=width, height=height, relief=relief, font=font, highlightthickness=ht, highlightbackground=htc)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky=anchor, rowspan=rowspan, columnspan=columnspan)
    return label

label_properties = [
    {"text": "r", "parent": ROOT1, "bg": "#1d2027", "fg": "#ff0000", "width": 0, "height": "0", "relief": "flat", "font": ("Webdings", 10, "bold"), "ht": 0, "htc": "#FFFFFF", "padx": (0, 2), "pady": (0, 0), "anchor": "w", "row": 1, "column": 1, "rowspan": 1, "columnspan": 1},
]
labels = [create_label(**prop) for prop in label_properties]
LB_XXX, = labels
LB_XXX.bind("<Button-1>", close_window)

# Initial space
LB_INITIALSPC = tk.Label(MAIN_FRAME, text="", bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 16, "bold"))
LB_INITIALSPC.pack(side="top", anchor="ne", padx=(0,0), pady=(0,0))

# Search entry
search_entry = tk.Entry(MAIN_FRAME, font=("calibri", 12), bg="#FFFFFF", fg="#000000", insertbackground="#F00")
search_entry.pack(side="top", anchor="center", padx=(20, 0), pady=(0, 10))

# Control buttons frame
control_frame = tk.Frame(MAIN_FRAME, bg="#1d2027")
control_frame.pack(side="top", anchor="center", padx=(20, 0), pady=(0, 10))

def add_new_app():
    """Add a new application"""
    dialog = AddEditAppDialog(ROOT, "Add New Application")
    if dialog.result:
        applications.append(dialog.result)
        save_applications(applications)
        refresh_app_list()

def edit_individual_app(app):
    """Edit individual application"""
    dialog = AddEditAppDialog(ROOT, "Edit Application", app)
    if dialog.result:
        # Update the app data
        app.update(dialog.result)
        save_applications(applications)
        refresh_app_list()

def delete_individual_app(app):
    """Delete individual application"""
    global applications
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{app['name']}'?"):
        applications = [a for a in applications if a != app]
        save_applications(applications)
        refresh_app_list()

# Control buttons
add_btn = tk.Button(control_frame, text="Add", bg="#00AA00", fg="#FFFFFF", font=("calibri", 10, "bold"), command=add_new_app)
add_btn.pack(side="left", padx=(0, 5))

class AddEditAppDialog:
    def __init__(self, parent, title, app_data=None):
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x300")
        self.top.configure(bg="#282c34")
        self.top.resizable(False, False)
        
        # Center the dialog
        self.top.transient(parent)
        self.top.grab_set()
        
        # Create form fields
        self.create_form(app_data)
        
    def create_form(self, app_data):
        # Name
        tk.Label(self.top, text="Name:", bg="#282c34", fg="#FFFFFF", font=("calibri", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.top, font=("calibri", 10), width=40)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Scoop Name
        tk.Label(self.top, text="Scoop Name:", bg="#282c34", fg="#FFFFFF", font=("calibri", 10, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.scoop_name_entry = tk.Entry(self.top, font=("calibri", 10), width=40)
        self.scoop_name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Scoop Path
        tk.Label(self.top, text="Scoop Path:", bg="#282c34", fg="#FFFFFF", font=("calibri", 10, "bold")).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.scoop_path_entry = tk.Entry(self.top, font=("calibri", 10), width=40)
        self.scoop_path_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Winget Name
        tk.Label(self.top, text="Winget Name:", bg="#282c34", fg="#FFFFFF", font=("calibri", 10, "bold")).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.winget_name_entry = tk.Entry(self.top, font=("calibri", 10), width=40)
        self.winget_name_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Winget Path
        tk.Label(self.top, text="Winget Path:", bg="#282c34", fg="#FFFFFF", font=("calibri", 10, "bold")).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.winget_path_entry = tk.Entry(self.top, font=("calibri", 10), width=40)
        self.winget_path_entry.grid(row=4, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.top, bg="#282c34")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(button_frame, text="Save", bg="#00AA00", fg="#FFFFFF", font=("calibri", 10, "bold"), command=self.save)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", bg="#FF0000", fg="#FFFFFF", font=("calibri", 10, "bold"), command=self.cancel)
        cancel_btn.pack(side="left", padx=10)
        
        # Populate fields if editing
        if app_data:
            self.name_entry.insert(0, app_data.get("name", ""))
            self.scoop_name_entry.insert(0, app_data.get("scoop_name", ""))
            self.scoop_path_entry.insert(0, app_data.get("scoop_path", ""))
            self.winget_name_entry.insert(0, app_data.get("winget_name", ""))
            self.winget_path_entry.insert(0, app_data.get("winget_path", ""))
    
    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required!")
            return
        
        self.result = {
            "name": name,
            "scoop_name": self.scoop_name_entry.get().strip(),
            "scoop_path": self.scoop_path_entry.get().strip(),
            "winget_name": self.winget_name_entry.get().strip(),
            "winget_path": self.winget_path_entry.get().strip()
        }
        self.top.destroy()
    
    def cancel(self):
        self.top.destroy()

def check_installation(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt):
    scoop_installed = os.path.exists(scoop_path) if scoop_path else False
    winget_installed = os.path.exists(winget_path) if winget_path else False
    application_installed = scoop_installed or winget_installed
    chkbx_var.set(1 if application_installed else 0)

    installation_source = ""
    if scoop_installed:
        installation_source = "[S]"
        text_color = "#FFFFFF"
    elif winget_installed:
        installation_source = "[W]"
        text_color = "#41abff"
    else:
        installation_source = "[X]"
        text_color = "#FF0000"

    chkbox_bt.config(text=f"{app_name} {installation_source}", foreground=text_color)

def install_application(app_name, scoop_name, scoop_path, winget_name, winget_path, chkbx_var, chkbox_bt):
    install_options = []
    if winget_name:
        install_options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'winget install {winget_name}')})
    if scoop_name:
        install_options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'pwsh -Command "scoop install {scoop_name}"')})
    if install_options:
        show_options(install_options)

def uninstall_application(app_name, scoop_name, scoop_path, winget_name, winget_path, chkbx_var, chkbox_bt):
    uninstall_options = []
    if winget_name:
        uninstall_options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'winget uninstall {winget_name}')})
    if scoop_name:
        uninstall_options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'pwsh -Command "scoop uninstall {scoop_name}"')})
    if uninstall_options:
        show_options(uninstall_options)

def open_file_location(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt):
    options = []
    if winget_path and os.path.exists(winget_path):
        options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'explorer /select,"{winget_path}"')})
    if scoop_path and os.path.exists(scoop_path):
        options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'explorer /select,"{scoop_path}"')})
    if options:
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

# Create canvas and scrollbar
canvas = Canvas(MAIN_FRAME, bg="#1d2027", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

def on_mousewheel(event):
    if event.widget == scrollbar:
        canvas.yview_scroll(-5 * (event.delta // 120), "units")
    else:
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

scrollbar = ttk.Scrollbar(MAIN_FRAME, orient="vertical", style="Custom.Vertical.TScrollbar")
scrollbar.pack(side="right", fill="y")

style = ttk.Style()
style.theme_use("default")
style.configure("Custom.Vertical.TScrollbar", background="#FF0000", troughcolor="#25072c")
style.map("Custom.Vertical.TScrollbar",
    background=[("active", "#72a9ec")],
)
style.map("Custom.Vertical.TScrollbar",
    troughcolor=[("active", "#25072c")],
    width=[("active", 10)]
)
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas
frame = tk.Frame(canvas, bg="#1d2027")
canvas.create_window((0, 0), window=frame, anchor="nw")

def refresh_app_list():
    """Refresh the application list display"""
    # Clear existing widgets
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Reset applications data
    for app in applications:
        app["frame"] = tk.Frame(frame, bg="#1d2027")
        app["chkbx_var"] = tk.IntVar()
    
    row_number = 0
    
    # Create widgets for each application
    for app in applications:
        app_frame = app["frame"]
        app_frame.grid(row=row_number, column=0, padx=(10,0), pady=(0,0), sticky="ew")
        row_number += 1
        
        app_name = app["name"]
        scoop_name = app["scoop_name"]
        scoop_path = app["scoop_path"]
        winget_name = app["winget_name"]
        winget_path = app["winget_path"]
        chkbx_var = app["chkbx_var"]
        
        # App status checkbox
        chkbox_bt = tk.Checkbutton(app_frame, text=app_name, variable=chkbx_var, font=("JetBrainsMono NF", 12, "bold"), 
                                   foreground="green", background="#1d2027", activebackground="#1d2027", selectcolor="#1d2027", 
                                   padx=10, pady=1, borderwidth=2, relief="flat")
        chkbox_bt.configure(command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: check_installation(name, scoop, winget, var, cb))
        chkbox_bt.grid(row=0, column=0, padx=(0,0), pady=(0,0))
        
        # Action buttons
        ins_bt = tk.Button(app_frame, text="n", foreground="#00FF00", background="#1d2027", font=("webdings", 5), relief="flat", 
                          command=lambda name=app_name, scoop=scoop_name, scoop_path=scoop_path, winget=winget_name, winget_path=winget_path, var=chkbx_var, cb=chkbox_bt: install_application(name, scoop, scoop_path, winget, winget_path, var, cb))
        ins_bt.grid(row=0, column=1, padx=(0,0), pady=(0,0))
        
        unins_bt = tk.Button(app_frame, text="n", foreground="#FF0000", background="#1d2027", font=("webdings", 5), relief="flat", 
                            command=lambda name=app_name, scoop=scoop_name, scoop_path=scoop_path, winget=winget_name, winget_path=winget_path, var=chkbx_var, cb=chkbox_bt: uninstall_application(name, scoop, scoop_path, winget, winget_path, var, cb))
        unins_bt.grid(row=0, column=2, padx=(0,0), pady=(0,0))
        
        open_bt = tk.Button(app_frame, text="n", foreground="#eac353", background="#1d2027", font=("webdings", 5), relief="flat", 
                           command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: open_file_location(name, scoop, winget, var, cb))
        open_bt.grid(row=0, column=3, padx=(0, 0), pady=(0, 0))
        
        # Individual Edit and Delete buttons
        edit_bt = tk.Button(app_frame, text="✏", foreground="#0078D7", background="#1d2027", font=("Arial", 8), relief="flat",
                           command=lambda a=app: edit_individual_app(a))
        edit_bt.grid(row=0, column=4, padx=(2, 0), pady=(0, 0))
        
        delete_bt = tk.Button(app_frame, text="🗑", foreground="#FF0000", background="#1d2027", font=("Arial", 8), relief="flat",
                             command=lambda a=app: delete_individual_app(a))
        delete_bt.grid(row=0, column=5, padx=(2, 0), pady=(0, 0))
        
        # Check installation status
        check_installation(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt)
    
    # Update scroll region
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def filter_apps(event=None):
    search_query = search_entry.get().lower()
    for app in applications:
        app_name = app["name"]
        app_frame = app["frame"]
        if search_query in app_name.lower():
            app_frame.grid()
        else:
            app_frame.grid_remove()

# Initialize the app list
refresh_app_list()

# Bind the filtering function to the KeyRelease event of the search entry
search_entry.bind("<KeyRelease>", filter_apps)

# Ending
MAIN_FRAME.pack()
ROOT.mainloop()