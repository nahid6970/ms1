#? https://pypi.org/project/pretty-errors/

from customtkinter import *
from time import strftime
import ctypes
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import json
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import sys
import win32gui
import win32con

def calculate_time_to_appear(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to appear: {elapsed_time:.2f} seconds")

start_time = time.time()

# Relative path for JSON files
JSON_PATH = os.path.join(os.path.dirname(__file__), "commands.json")
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
LOG_DIR = r"C:\Users\nahid\script_output\rclone"
os.makedirs(LOG_DIR, exist_ok=True)

def load_commands():
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
    return {}

def save_commands(commands):
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(commands, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")

def load_settings():
    default_settings = {
        "width": None, # Auto
        "height": 39,
        "x": None,
        "y": 993,
        "interval": 3600,
        "check_interval": 600,
        "minimize_to_tray": True,
        "auto_sync_enabled": False,
        "auto_sync_on_red": True,
        "topmost": False,
        "dialog_width": 550,
        "settings_win_width": 480,
        "settings_win_height": 700,
        "show_command_output": False,
        "buffer_output": True
    }
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return {**default_settings, **json.load(f)}
        except Exception as e:
            print(f"Error loading settings: {e}")
    return default_settings

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

# Tray Icon logic
tray_icon = None

def create_image():
    # Generate a simple icon
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (29, 32, 39)) # Match bg color
    dc = ImageDraw.Draw(image)
    dc.rectangle([width // 4, height // 4, width * 3 // 4, height * 3 // 4], fill='red')
    return image

def show_window(icon=None, item=None):
    if icon:
        icon.stop()
    ROOT.after(0, ROOT.deiconify)
    ROOT.after(0, ROOT.lift)
    ROOT.after(0, ROOT.focus_force)

def quit_app(icon=None, item=None):
    if icon:
        icon.stop()
    ROOT.quit()
    os._exit(0)

def setup_tray():
    global tray_icon
    image = create_image()
    menu = (item('Show', show_window), item('Quit', quit_app))
    tray_icon = pystray.Icon("rclone_gui", image, "RClone GUI", menu)
    tray_icon.run()

def on_close_click():
    if app_settings.get("minimize_to_tray"):
        ROOT.withdraw()
        threading.Thread(target=setup_tray, daemon=True).start()
    else:
        quit_app()

commands = load_commands()
app_settings = load_settings()

# Fullscreen detection and topmost management
def is_fullscreen_app_active():
    """Check if a fullscreen application is currently active"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return False
        
        # Get window rect
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Check if window covers entire screen
        if width >= screen_width and height >= screen_height:
            # Additional check: is it actually fullscreen style?
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            if not (style & win32con.WS_CAPTION):
                return True
        
        return False
    except:
        return False

def manage_topmost():
    """Manage topmost state based on fullscreen detection"""
    if not app_settings.get("topmost", False):
        return
    
    if is_fullscreen_app_active():
        ROOT.attributes('-topmost', False)
    else:
        ROOT.attributes('-topmost', True)
    
    # Check every 500ms
    ROOT.after(500, manage_topmost)

# Auto-Sync logic
auto_sync_enabled = app_settings.get("auto_sync_enabled", False)
auto_sync_on_red = app_settings.get("auto_sync_on_red", True)
pulse_id = None
check_cycle_running = False
all_items = []

def run_sync_for_item(cfg, label):
    """Run sync for a specific item"""
    print(f"\n{'='*60}")
    print(f"🔄 AUTO-SYNC TRIGGERED -- {cfg['label']}")
    print(f"{'='*60}")
    
    log_path = os.path.join(LOG_DIR, f"{cfg['label']}_sync.log")
    cmd = cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
    actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
    
    print(f"📁 Source: {cfg['src']}")
    print(f"📁 Destination: {cfg['dst']}")
    print(f"⚙️  Running sync command...")
    
    with open(log_path, "w") as f:
        subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
    
    print(f"✅ Sync completed -- {cfg['label']}")
    print(f"📝 Log saved to: {log_path}")
    
    # After sync, run check immediately
    print(f"🔍 Running check -- {cfg['label']}...")
    check_single_item(label, cfg)
    print(f"{'='*60}\n")

def toggle_auto_sync():
    global auto_sync_enabled
    auto_sync_enabled = not auto_sync_enabled
    app_settings["auto_sync_enabled"] = auto_sync_enabled
    save_settings(app_settings)
    update_auto_sync_ui()

def update_auto_sync_ui():
    global pulse_id
    if auto_sync_enabled:
        # Stop any existing pulse effect
        if pulse_id:
            ROOT.after_cancel(pulse_id)
            pulse_id = None
        # Light green background with black text
        btn_auto.config(text="\uf017 ON", bg="#06de22", fg="black")
    else:
        if pulse_id:
            ROOT.after_cancel(pulse_id)
            pulse_id = None
        btn_auto.config(fg="red", text="\uf017 OFF", bg="#2c313a")

def pulse_effect(color_idx=0):
    global pulse_id
    if not auto_sync_enabled: return
    colors = ["#06de22", "#05a81a", "#047512", "#05a81a"]
    btn_auto.config(fg=colors[color_idx % len(colors)])
    pulse_id = ROOT.after(500, lambda: pulse_effect(color_idx + 1))

#! Variables to track the position of the mouse when clicking​⁡
drag_data = {"x": 0, "y": 0}

def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def stop_drag(event):
    drag_data["x"] = None
    drag_data["y"] = None
    # Save new position
    app_settings["x"] = ROOT.winfo_x()
    app_settings["y"] = ROOT.winfo_y()
    save_settings(app_settings)

def do_drag(event):
    if drag_data["x"] is not None and drag_data["y"] is not None:
        x, y = (event.x - drag_data["x"] + ROOT.winfo_x(), event.y - drag_data["y"] + ROOT.winfo_y())
        ROOT.geometry("+%s+%s" % (x, y))

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def run_command(pwsh_command):
    """Run a PowerShell command in a new terminal window."""
    subprocess.Popen(f'start pwsh -NoExit -Command "{pwsh_command}"', shell=True)

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.default_color = kw.pop('default_color', "#2c313a")
        self.hover_color = kw.pop('hover_color', "red")
        self.default_fg = kw.pop('default_fg', "#FFFFFF")
        self.hover_fg = kw.pop('hover_fg', "#000000")
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(bg=self.default_color, fg=self.default_fg, activebackground=self.hover_color, activeforeground=self.hover_fg, bd=0, highlightthickness=0)

    def on_enter(self, event):
        self.configure(bg=self.hover_color, fg=self.hover_fg)

    def on_leave(self, event):
        self.configure(bg=self.default_color, fg=self.default_fg)

set_console_title("🔥")
# Create main window
ROOT = tk.Tk()
ROOT.title("Python GUI")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)  # Remove default borders

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)
default_font = ("Jetbrainsmono nfp", 10)
ROOT.option_add("*Font", default_font)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

# Initial geometry from settings
init_x = app_settings["x"] if app_settings["x"] is not None else (screen_width//2 - 1920//2)
init_y = app_settings["y"]
init_w = app_settings["width"] if app_settings["width"] else ""
init_h = app_settings["height"]

if init_w:
    ROOT.geometry(f"{init_w}x{init_h}+{init_x}+{init_y}")
else:
    ROOT.geometry(f"+{init_x}+{init_y}")

# Create main frame
MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027")
MAIN_FRAME.pack(pady=1, padx=2, expand=True, fill="both")

#! ALL Boxes
ROOT1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT1.pack(side="left", pady=(2,2), padx=(5,1), anchor="w", fill="x")

# Auto-Sync state (Handled above with persistence)

def open_settings():
    settings_win = tk.Toplevel(ROOT)
    settings_win.title("Settings")
    
    sw = app_settings.get("settings_win_width", 480)
    sh = app_settings.get("settings_win_height", 700)
    settings_win.geometry(f"{sw}x{sh}")
    settings_win.configure(bg="#1D2027")
    
    # Main container for settings (no scrolling as requested)
    main_container = tk.Frame(settings_win, bg="#1D2027")
    main_container.pack(fill="both", expand=True)

    # Grid container for settings
    grid_frame = tk.Frame(main_container, bg="#1D2027")
    grid_frame.pack(pady=10, padx=20, fill="x")
    grid_frame.columnconfigure(1, weight=1)

    # Helper to add grid row
    def add_setting_row(row, text, entry_val):
        lbl = tk.Label(grid_frame, text=text, bg="#1D2027", fg="white", anchor="e", width=25)
        lbl.grid(row=row, column=0, padx=(0, 10), pady=6, sticky="e")
        ent = tk.Entry(grid_frame, bg="#2c313a", fg="white", insertbackground="white", bd=1)
        ent.insert(0, str(entry_val))
        ent.grid(row=row, column=1, pady=6, sticky="ew")
        return ent

    w_entry = add_setting_row(0, "Main Window Width (auto):", app_settings["width"] or "")
    h_entry = add_setting_row(1, "Main Window Height:", app_settings["height"])
    x_entry = add_setting_row(2, "X Position (auto):", app_settings["x"] or "")
    y_entry = add_setting_row(3, "Y Position:", app_settings["y"])
    i_entry = add_setting_row(4, "Auto-Sync Interval (sec):", app_settings["interval"])
    c_entry = add_setting_row(5, "Check Interval (sec):", app_settings.get("check_interval", 600))
    dw_entry = add_setting_row(6, "Edit/Add Window Width:", app_settings.get("dialog_width", 550))
    sw_entry = add_setting_row(7, "Settings Win Width:", app_settings.get("settings_win_width", 480))
    sh_entry = add_setting_row(8, "Settings Win Height:", app_settings.get("settings_win_height", 700))

    # Checkbuttons container
    cb_frame = tk.Frame(main_container, bg="#1D2027")
    cb_frame.pack(pady=5, padx=20, fill="x")

    tray_var = tk.BooleanVar(value=app_settings.get("minimize_to_tray", True))
    tk.Checkbutton(cb_frame, text="Minimize to Tray on Close", variable=tray_var, bg="#1D2027", fg="white", selectcolor="#1d2027", activebackground="#1D2027", activeforeground="white").pack(anchor="w", pady=1)

    topmost_var = tk.BooleanVar(value=app_settings.get("topmost", False))
    tk.Checkbutton(cb_frame, text="Always on Top (hides for fullscreen)", variable=topmost_var, bg="#1D2027", fg="white", selectcolor="#1d2027", activebackground="#1D2027", activeforeground="white").pack(anchor="w", pady=1)

    auto_sync_red_var = tk.BooleanVar(value=app_settings.get("auto_sync_on_red", True))
    tk.Checkbutton(cb_frame, text="Auto-Sync When Item Turns Red", variable=auto_sync_red_var, bg="#1D2027", fg="white", selectcolor="#1d2027", activebackground="#1D2027", activeforeground="white").pack(anchor="w", pady=1)

    show_output_var = tk.BooleanVar(value=app_settings.get("show_command_output", False))
    tk.Checkbutton(cb_frame, text="Show Command Output in Terminal", variable=show_output_var, bg="#1D2027", fg="white", selectcolor="#1d2027", activebackground="#1D2027", activeforeground="white").pack(anchor="w", pady=1)

    buffer_output_var = tk.BooleanVar(value=app_settings.get("buffer_output", True))
    tk.Checkbutton(cb_frame, text="Buffer Output (prevents mixing, recommended)", variable=buffer_output_var, bg="#1D2027", fg="white", selectcolor="#1d2027", activebackground="#1D2027", activeforeground="white").pack(anchor="w", pady=1)

    # Note container
    notes_frame = tk.Frame(main_container, bg="#1D2027")
    notes_frame.pack(pady=5)
    tk.Label(notes_frame, text="Note: Enable Auto-Sync button in main window", bg="#1D2027", fg="yellow", font=("JetBrainsMono NFP", 8)).pack()
    tk.Label(notes_frame, text="Items sync individually when they turn red", bg="#1D2027", fg="yellow", font=("JetBrainsMono NFP", 8)).pack()

    def save():
        try:
            global auto_sync_on_red
            app_settings["width"] = int(w_entry.get()) if w_entry.get() else None
            app_settings["height"] = int(h_entry.get())
            app_settings["x"] = int(x_entry.get()) if x_entry.get() else None
            app_settings["y"] = int(y_entry.get())
            app_settings["interval"] = int(i_entry.get())
            app_settings["check_interval"] = int(c_entry.get())
            app_settings["dialog_width"] = int(dw_entry.get())
            app_settings["settings_win_width"] = int(sw_entry.get())
            app_settings["settings_win_height"] = int(sh_entry.get())
            app_settings["minimize_to_tray"] = tray_var.get()
            app_settings["topmost"] = topmost_var.get()
            app_settings["auto_sync_on_red"] = auto_sync_red_var.get()
            app_settings["show_command_output"] = show_output_var.get()
            app_settings["buffer_output"] = buffer_output_var.get()
            auto_sync_on_red = auto_sync_red_var.get()
            save_settings(app_settings)
            
            # Apply topmost setting immediately
            if app_settings["topmost"]:
                ROOT.attributes('-topmost', True)
                manage_topmost()
            else:
                ROOT.attributes('-topmost', False)
            
            messagebox.showinfo("Success", "Settings saved.")
            settings_win.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Use numbers.")

    tk.Button(main_container, text="Save Settings", command=save, bg="#2c313a", fg="white", width=20, height=1).pack(pady=15)

def on_label_click(event, cfg):
    try:
        log_path = os.path.join(LOG_DIR, f"{cfg['label']}_check.log")
        subprocess.Popen([
            "powershell", "-NoExit", "-Command", f'edit "{log_path}"'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print(f"Error opening log file: {e}")

def ctrl_left_click(event, cfg):
    if event.state & 0x0004:  # Ctrl key mask
        cmd = cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
        actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
        run_command(actual_cmd)

def ctrl_right_click(event, cfg):
    if event.state & 0x0004:  # Ctrl key mask
        cmd = cfg.get("right_click_cmd", "rclone sync dst src -P --fast-list")
        actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
        run_command(actual_cmd)

def remove_command(key):
    if messagebox.askyesno("Remove", f"Remove {key}?"):
        del commands[key]
        save_commands(commands)
        refresh_gui()

def edit_command(key):
    """Open edit dialog for a command"""
    cfg = commands[key]
    
    dialog_w = app_settings.get("dialog_width", 550)
    edit_win = tk.Toplevel(ROOT)
    edit_win.title(f"Edit: {key}")
    edit_win.geometry(f"{dialog_w}x680")
    edit_win.configure(bg="#1D2027")
    
    tk.Label(edit_win, text="Name (key):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    name_entry = tk.Entry(edit_win)
    name_entry.insert(0, key)
    name_entry.pack(fill="x", padx=20)
    
    tk.Label(edit_win, text="Label (Icon/Text):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    label_entry = tk.Entry(edit_win)
    label_entry.insert(0, cfg["label"])
    label_entry.pack(fill="x", padx=20)
    
    tk.Label(edit_win, text="Source Path:", bg="#1D2027", fg="white").pack(pady=(10, 0))
    src_entry = tk.Entry(edit_win)
    src_entry.insert(0, cfg["src"])
    src_entry.pack(fill="x", padx=20)
    
    tk.Label(edit_win, text="Destination Path:", bg="#1D2027", fg="white").pack(pady=(10, 0))
    dst_entry = tk.Entry(edit_win)
    dst_entry.insert(0, cfg["dst"])
    dst_entry.pack(fill="x", padx=20)
    
    tk.Label(edit_win, text="Check Command:", bg="#1D2027", fg="white").pack(pady=(10, 0))
    check_entry = tk.Entry(edit_win)
    check_entry.insert(0, cfg.get("cmd", "rclone check src dst --fast-list --size-only"))
    check_entry.pack(fill="x", padx=20)
    
    tk.Label(edit_win, text="Left Click Command:", bg="#1D2027", fg="white").pack(pady=(10, 0))
    left_entry = tk.Entry(edit_win)
    left_entry.insert(0, cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO"))
    left_entry.pack(fill="x", padx=20)
    
    tk.Label(edit_win, text="Right Click Command:", bg="#1D2027", fg="white").pack(pady=(10, 0))
    right_entry = tk.Entry(edit_win)
    right_entry.insert(0, cfg.get("right_click_cmd", "rclone sync dst src -P --fast-list"))
    right_entry.pack(fill="x", padx=20)
    
    tk.Label(edit_win, text="Display Order (Index):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    index_entry = tk.Entry(edit_win)
    index_entry.insert(0, str(cfg.get("index", 0)))
    index_entry.pack(fill="x", padx=20)
    
    enabled_var = tk.BooleanVar(value=cfg.get("enabled", True))
    tk.Checkbutton(edit_win, text="Enabled", variable=enabled_var, bg="#1D2027", fg="white", selectcolor="#1d2027", activebackground="#1D2027", activeforeground="white").pack(pady=10)
    
    button_frame = tk.Frame(edit_win, bg="#1D2027")
    button_frame.pack(pady=15)
    
    def save_edit():
        new_key = name_entry.get()
        if not new_key:
            messagebox.showerror("Error", "Name cannot be empty")
            return
        
        # Remove old key if name changed
        if new_key != key:
            del commands[key]
        
        commands[new_key] = {
            "cmd": check_entry.get(),
            "src": src_entry.get(),
            "dst": dst_entry.get(),
            "label": label_entry.get(),
            "left_click_cmd": left_entry.get(),
            "right_click_cmd": right_entry.get(),
            "index": int(index_entry.get()) if index_entry.get().isdigit() else 0,
            "enabled": enabled_var.get()
        }
        save_commands(commands)
        refresh_gui()
        edit_win.destroy()
    
    def delete_item():
        if messagebox.askyesno("Delete", f"Delete {key}?"):
            del commands[key]
            save_commands(commands)
            refresh_gui()
            edit_win.destroy()
    
    def duplicate_item():
        base_name = name_entry.get()
        new_key = base_name + "_copy"
        counter = 1
        while new_key in commands:
            new_key = f"{base_name}_copy_{counter}"
            counter += 1
        
        commands[new_key] = {
            "cmd": check_entry.get(),
            "src": src_entry.get(),
            "dst": dst_entry.get(),
            "label": label_entry.get(),
            "left_click_cmd": left_entry.get(),
            "right_click_cmd": right_entry.get(),
            "index": int(index_entry.get()) if index_entry.get().isdigit() else 0,
            "enabled": enabled_var.get()
        }
        save_commands(commands)
        refresh_gui()
        edit_win.destroy()
        messagebox.showinfo("Success", f"Duplicated as: {new_key}")

    tk.Button(button_frame, text="Save", command=save_edit, bg="#2c313a", fg="white", width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="Duplicate", command=duplicate_item, bg="#2c313a", fg="white", width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="Delete", command=delete_item, bg="red", fg="white", width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=edit_win.destroy, bg="#2c313a", fg="white", width=10).pack(side="left", padx=5)

def add_command():
    dialog_w = app_settings.get("dialog_width", 550)
    add_win = tk.Toplevel(ROOT)
    add_win.title("Add New Command")
    add_win.geometry(f"{dialog_w}x680")
    add_win.configure(bg="#1D2027")
    
    tk.Label(add_win, text="Name (key):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    name_entry = tk.Entry(add_win)
    name_entry.pack(fill="x", padx=20)
    
    tk.Label(add_win, text="Label (Icon/Text):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    label_entry = tk.Entry(add_win)
    label_entry.pack(fill="x", padx=20)
    
    tk.Label(add_win, text="Source Path:", bg="#1D2027", fg="white").pack(pady=(10, 0))
    src_entry = tk.Entry(add_win)
    src_entry.pack(fill="x", padx=20)
    
    tk.Label(add_win, text="Destination Path:", bg="#1D2027", fg="white").pack(pady=(10, 0))
    dst_entry = tk.Entry(add_win)
    dst_entry.pack(fill="x", padx=20)
    
    tk.Label(add_win, text="Check Command (optional):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    check_entry = tk.Entry(add_win)
    check_entry.insert(0, "rclone check src dst --fast-list --size-only")
    check_entry.pack(fill="x", padx=20)
    
    tk.Label(add_win, text="Left Click Command (optional):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    left_entry = tk.Entry(add_win)
    left_entry.insert(0, "rclone sync src dst -P --fast-list --log-level INFO")
    left_entry.pack(fill="x", padx=20)
    
    tk.Label(add_win, text="Right Click Command (optional):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    right_entry = tk.Entry(add_win)
    right_entry.insert(0, "rclone sync dst src -P --fast-list")
    right_entry.pack(fill="x", padx=20)

    tk.Label(add_win, text="Display Order (Index):", bg="#1D2027", fg="white").pack(pady=(10, 0))
    index_entry = tk.Entry(add_win)
    index_entry.insert(0, str(len(commands)))
    index_entry.pack(fill="x", padx=20)
    
    enabled_var = tk.BooleanVar(value=True)
    tk.Checkbutton(add_win, text="Enabled", variable=enabled_var, bg="#1D2027", fg="white", selectcolor="#1d2027", activebackground="#1D2027", activeforeground="white").pack(pady=10)
    
    def save_new():
        name = name_entry.get()
        label = label_entry.get()
        src = src_entry.get()
        dst = dst_entry.get()
        
        if not all([name, label, src, dst]):
            messagebox.showerror("Error", "Name, Label, Source, and Destination are required")
            return
        
        commands[name] = {
            "cmd": check_entry.get(),
            "src": src,
            "dst": dst,
            "label": label,
            "left_click_cmd": left_entry.get(),
            "right_click_cmd": right_entry.get(),
            "index": int(index_entry.get()) if index_entry.get().isdigit() else 0,
            "enabled": enabled_var.get()
        }
        save_commands(commands)
        refresh_gui()
        add_win.destroy()
    
    button_frame = tk.Frame(add_win, bg="#1D2027")
    button_frame.pack(pady=15)
    
    tk.Button(button_frame, text="Add", command=save_new, bg="#2c313a", fg="white", width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=add_win.destroy, bg="#2c313a", fg="white", width=10).pack(side="left", padx=5)

# Periodically check using rclone
def check_single_item(label, cfg):
    """Run check for a single item"""
    log_path = os.path.join(LOG_DIR, f"{cfg['label']}_check.log")
    actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
    
    print(f"🔍 Checking -- {cfg['label']}")
    
    if app_settings.get("show_command_output"):
        print(f"\n{'*'*40}")
        print(f"🛠️  COMMAND -- {actual_cmd}")
        print(f"{'*'*40}")
        process = subprocess.Popen(actual_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        with open(log_path, "w") as f:
            for line in process.stdout:
                print(f"  > {line.strip()}")
                f.write(line)
        process.wait()
        print(f"{'*'*40}\n")
    else:
        with open(log_path, "w") as f:
            subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
    
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            content = f.read()
        if "ERROR" not in content and "0 differences found" in content:
            label.config(fg="#06de22")
            print(f"✅ {cfg['label']} -- No differences (GREEN)")
        else:
            label.config(fg="red")
            print(f"❌ {cfg['label']} -- Differences found (RED)")

# Global check cycle management
check_cycle_running = False
last_check_time = {}
pending_checks = 0
check_lock = threading.Lock()
output_lock = threading.Lock()  # Prevent mixed output

def start_global_countdown():
    """Start a global countdown timer for all items"""
    check_interval_sec = app_settings.get("check_interval", 600)
    
    def countdown(remaining):
        if remaining > 0:
            print(f"⏱️  Next check cycle in {remaining} seconds...", end='\r')
            ROOT.after(1000, lambda: countdown(remaining - 1))
        elif remaining == 0:
            print(f"\n{'='*60}")
            print(f"⏰ Check interval reached - Starting new check cycle")
            print(f"{'='*60}")
            # Trigger all checks and wait for completion
            trigger_all_checks_and_wait()
    
    countdown(check_interval_sec)

def trigger_all_checks_and_wait():
    """Trigger all checks and wait for them to complete before starting countdown"""
    global pending_checks
    
    # Count how many checks we need to run
    with check_lock:
        pending_checks = 0
        for widget in ROOT1.winfo_children():
            if isinstance(widget, tk.Label) and hasattr(widget, 'trigger_check'):
                pending_checks += 1
    
    if pending_checks == 0:
        # No items to check, start countdown immediately
        start_global_countdown()
        return
    
    # Trigger all checks
    for widget in ROOT1.winfo_children():
        if isinstance(widget, tk.Label) and hasattr(widget, 'trigger_check'):
            widget.trigger_check()
    
    # Wait for all checks to complete
    check_completion()

def check_completion():
    """Check if all checks are done, verify all GREEN, then start countdown"""
    global pending_checks
    
    with check_lock:
        if pending_checks <= 0:
            # All checks complete, now verify all items are GREEN
            red_items = []
            for widget in ROOT1.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget('fg') == 'red' and hasattr(widget, 'cfg'):
                    red_items.append(widget)
            
            if red_items:
                print(f"\n⚠️  {len(red_items)} item(s) still RED after sync, re-syncing...")
                # Reset counter for red items
                pending_checks = len(red_items)
                # Re-trigger sync for red items
                for widget in red_items:
                    widget.trigger_check()
                # Wait for completion
                ROOT.after(500, check_completion)
            else:
                print(f"\n{'='*60}")
                print(f"✅ All items GREEN - Starting countdown")
                print(f"{'='*60}\n")
                start_global_countdown()
            return
    
    # Check again in 500ms
    ROOT.after(500, check_completion)

def mark_check_complete():
    """Mark one check as complete"""
    global pending_checks
    with check_lock:
        pending_checks -= 1

def check_and_update(label, cfg):
    def run_check():
        try:
            log_path = os.path.join(LOG_DIR, f"{cfg['label']}_check.log")
            actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])

            with output_lock:
                print(f"🔍 Periodic check -- {cfg['label']}")

            if app_settings.get("show_command_output"):
                if app_settings.get("buffer_output", True):
                    # Buffered mode - collect all output then print
                    output_buffer = []
                    output_buffer.append(f"\n{'*'*40}")
                    output_buffer.append(f"🛠️  CHECK COMMAND: {actual_cmd}")
                    output_buffer.append(f"{'*'*40}")
                    
                    process = subprocess.Popen(actual_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    with open(log_path, "w") as f:
                        for line in process.stdout:
                            f.write(line)
                            if any(x in line for x in ["ERROR", "NOTICE", "INFO", "differences found"]) and "symlink" not in line.lower():
                                output_buffer.append(f"  > {line.strip()}")
                    process.wait()
                    output_buffer.append(f"{'*'*40}\n")
                    
                    with output_lock:
                        for line in output_buffer:
                            print(line)
                else:
                    # Real-time mode - print each line with project label
                    print(f"\n{'*'*40}")
                    print(f"🛠️  CHECK COMMAND: {actual_cmd}")
                    print(f"{'*'*40}")
                    
                    process = subprocess.Popen(actual_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    with open(log_path, "w") as f:
                        for line in process.stdout:
                            f.write(line)
                            if any(x in line for x in ["ERROR", "NOTICE", "INFO", "differences found"]) and "symlink" not in line.lower():
                                print(f"\033[42m\033[30m{cfg['label']}\033[0m > {line.strip()}")
                    process.wait()
                    print(f"{'*'*40}\n")
            else:
                with open(log_path, "w") as f:
                    subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)

            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    content = f.read()

                # Check if differences found
                if "ERROR" not in content and "0 differences found" in content:
                    label.config(fg="#06de22")
                    with output_lock:
                        print(f"✅ {cfg['label']} -- No differences (GREEN)")
                else:
                    # Differences found - turn red and auto-sync
                    label.config(fg="red")
                    with output_lock:
                        print(f"❌ {cfg['label']} -- Differences detected (RED)")
                        print(f"🚀 Auto-syncing -- {cfg['label']}...")

                    # Auto-sync
                    sync_log_path = os.path.join(LOG_DIR, f"{cfg['label']}_sync.log")
                    sync_cmd = cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
                    actual_sync_cmd = sync_cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])

                    if app_settings.get("show_command_output"):
                        if app_settings.get("buffer_output", True):
                            # Buffered mode
                            output_buffer = []
                            output_buffer.append(f"\n{'*'*40}")
                            output_buffer.append(f"🛠️  SYNC COMMAND: {actual_sync_cmd}")
                            output_buffer.append(f"{'*'*40}")
                            
                            process = subprocess.Popen(actual_sync_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                            with open(sync_log_path, "w") as f:
                                for line in process.stdout:
                                    f.write(line)
                                    if any(x in line for x in ["ERROR", "NOTICE", "INFO :", "Copied", "Deleted"]) and "symlink" not in line.lower():
                                        output_buffer.append(f"  >> {line.strip()}")
                            process.wait()
                            output_buffer.append(f"{'*'*40}\n")
                            
                            with output_lock:
                                for line in output_buffer:
                                    print(line)
                        else:
                            # Real-time mode with project label
                            print(f"\n{'*'*40}")
                            print(f"🛠️  SYNC COMMAND: {actual_sync_cmd}")
                            print(f"{'*'*40}")
                            
                            process = subprocess.Popen(actual_sync_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                            with open(sync_log_path, "w") as f:
                                for line in process.stdout:
                                    f.write(line)
                                    if any(x in line for x in ["ERROR", "NOTICE", "INFO :", "Copied", "Deleted"]) and "symlink" not in line.lower():
                                        print(f"\033[42m\033[30m{cfg['label']}\033[0m >> {line.strip()}")
                            process.wait()
                            print(f"{'*'*40}\n")
                    else:
                        with open(sync_log_path, "w") as f:
                            subprocess.run(actual_sync_cmd, shell=True, stdout=f, stderr=f)

                    with output_lock:
                        print(f"✅ Sync completed -- {cfg['label']} verifying...")

                    # Check again after sync to verify
                    if app_settings.get("show_command_output"):
                        process = subprocess.Popen(actual_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                        with open(log_path, "w") as f:
                            for line in process.stdout:
                                f.write(line)
                        process.wait()
                    else:
                        with open(log_path, "w") as f:
                            subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)

                    # Read result after sync
                    if os.path.exists(log_path):
                        with open(log_path, "r") as f:
                            content = f.read()
                        if "ERROR" not in content and "0 differences found" in content:
                            label.config(fg="#06de22")
                            with output_lock:
                                print(f"✅ {cfg['label']} -- Verified - No differences after sync (GREEN)")
                        else:
                            label.config(fg="red")
                            with output_lock:
                                print(f"⚠️ {cfg['label']} -- Still has differences after sync (RED)")
        finally:
            # Mark this check as complete
            mark_check_complete()

    # Store the check function on the label so it can be triggered globally
    label.trigger_check = lambda: threading.Thread(target=run_check, daemon=True).start()
    label.cfg = cfg  # Store config reference for re-sync
    
    # Don't run initial check here - let trigger_all_checks_and_wait handle it


def create_gui():
    # Clear existing widgets if any (for refresh)
    global all_items
    all_items = []
    
    for widget in ROOT1.winfo_children():
        widget.destroy()

    # Sort items by index
    sorted_items = sorted(commands.items(), key=lambda x: (x[1].get("index", 0), x[0]))

    for key, cfg in sorted_items:
        is_enabled = cfg.get("enabled", True)
        
        lbl = tk.Label(
            ROOT1,
            bg="#1d2027",
            text=cfg["label"],
            font=("JetBrainsMono NFP", 16, "bold"),
            fg="#555555" if not is_enabled else "#FFFFFF",
            cursor="hand2"
        )
        lbl.pack(side="left", padx=(5, 5))

        # Event bindings
        lbl.bind("<Button-1>", lambda event, c=cfg: on_label_click(event, c))           # left click
        lbl.bind("<Control-Button-1>", lambda event, c=cfg: ctrl_left_click(event, c))  # ctrl + left
        lbl.bind("<Control-Button-3>", lambda event, c=cfg: ctrl_right_click(event, c)) # ctrl + right
        
        # Right click to edit
        lbl.bind("<Button-3>", lambda event, k=key: edit_command(k))

        if is_enabled:
            check_and_update(lbl, cfg)
    
    # Add separator or just more padding
    tk.Frame(ROOT1, width=10, bg="#1d2027").pack(side="left")

    # Add Button (+)
    btn_add = HoverButton(ROOT1, text="+", font=("JetBrainsMono NFP", 14, "bold"), command=add_command, width=2)
    btn_add.pack(side="left", padx=2)

    # Auto Sync Toggle (🕒)
    global btn_auto
    btn_auto = HoverButton(ROOT1, text="\uf017 OFF", font=("JetBrainsMono NFP", 10, "bold"), command=toggle_auto_sync, fg="red")
    btn_auto.pack(side="left", padx=2)
    
    # Initialize UI state
    update_auto_sync_ui()

    # Reload Button (🔄)
    btn_reload = HoverButton(ROOT1, text="\uf021", font=("JetBrainsMono NFP", 12, "bold"), command=lambda: os.execv(sys.executable, ['python'] + sys.argv))
    btn_reload.pack(side="left", padx=2)

    # Settings Button (⚙️)
    btn_settings = HoverButton(ROOT1, text="\uf013", font=("JetBrainsMono NFP", 12, "bold"), command=open_settings)
    btn_settings.pack(side="left", padx=2)

    # Close Button (X)
    btn_close = HoverButton(ROOT1, text="\uf00d", font=("JetBrainsMono NFP", 12, "bold"), command=on_close_click, hover_color="red")
    btn_close.pack(side="left", padx=(5, 2))

    # Update ROOT size logic
    def adjust_width():
        ROOT.update_idletasks()
        # Ensure ROOT1 is fully updated
        req_width = ROOT1.winfo_reqwidth() + 25 
        req_height = app_settings["height"]
        
        # Current position
        curr_x = ROOT.winfo_x()
        curr_y = ROOT.winfo_y()
        
        # If no width is set in settings, or if it's auto-adjusting
        if not app_settings.get("width"):
            ROOT.geometry(f"{req_width}x{req_height}+{curr_x}+{curr_y}")
        else:
            ROOT.geometry(f"{app_settings['width']}x{req_height}+{curr_x}+{curr_y}")
    
    # Schedule multiple updates to ensure layout is finalized
    ROOT.after(100, adjust_width)
    ROOT.after(500, adjust_width)

def refresh_gui():
    create_gui()
    trigger_all_checks_and_wait()

# Support dragging on the main frame
MAIN_FRAME.bind("<Button-1>", start_drag)
MAIN_FRAME.bind("<B1-Motion>", do_drag)
ROOT1.bind("<Button-1>", start_drag)
ROOT1.bind("<B1-Motion>", do_drag)

# Call GUI init
create_gui()

# Start global countdown timer
trigger_all_checks_and_wait()

# Apply topmost setting on startup
if app_settings.get("topmost", False):
    ROOT.attributes('-topmost', True)
    manage_topmost()

ROOT.mainloop()
