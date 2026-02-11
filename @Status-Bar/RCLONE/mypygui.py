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
        "auto_sync_enabled": False
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

# Auto-Sync logic
auto_sync_enabled = app_settings.get("auto_sync_enabled", False)
pulse_id = None

def toggle_auto_sync():
    global auto_sync_enabled
    auto_sync_enabled = not auto_sync_enabled
    app_settings["auto_sync_enabled"] = auto_sync_enabled
    save_settings(app_settings)
    update_auto_sync_ui()
    if auto_sync_enabled:
        threading.Thread(target=auto_sync_loop, daemon=True).start()

def update_auto_sync_ui():
    global pulse_id
    if auto_sync_enabled:
        btn_auto.config(text="\uf017 ON")
        pulse_effect()
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

def auto_sync_loop():
    while auto_sync_enabled:
        for key, cfg in commands.items():
            if not auto_sync_enabled: break
            cmd = cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
            actual_cmd = cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
            subprocess.run(f'pwsh -Command "{actual_cmd}"', shell=True)
        # Sleep in increments to remain responsive to toggle
        for _ in range(app_settings["interval"]):
            if not auto_sync_enabled: break
            time.sleep(1)

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
    settings_win.geometry("300x350")
    settings_win.configure(bg="#1D2027")
    
    tk.Label(settings_win, text="Width (empty for auto):", bg="#1D2027", fg="white").pack()
    w_entry = tk.Entry(settings_win)
    w_entry.insert(0, str(app_settings["width"] or ""))
    w_entry.pack()

    tk.Label(settings_win, text="Height:", bg="#1D2027", fg="white").pack()
    h_entry = tk.Entry(settings_win)
    h_entry.insert(0, str(app_settings["height"]))
    h_entry.pack()

    tk.Label(settings_win, text="X Position (empty for auto):", bg="#1D2027", fg="white").pack()
    x_entry = tk.Entry(settings_win)
    x_entry.insert(0, str(app_settings["x"] or ""))
    x_entry.pack()

    tk.Label(settings_win, text="Y Position:", bg="#1D2027", fg="white").pack()
    y_entry = tk.Entry(settings_win)
    y_entry.insert(0, str(app_settings["y"]))
    y_entry.pack()

    tk.Label(settings_win, text="Auto-Sync Interval (sec):", bg="#1D2027", fg="white").pack()
    i_entry = tk.Entry(settings_win)
    i_entry.insert(0, str(app_settings["interval"]))
    i_entry.pack()

    tk.Label(settings_win, text="Check Interval (sec):", bg="#1D2027", fg="white").pack()
    c_entry = tk.Entry(settings_win)
    c_entry.insert(0, str(app_settings.get("check_interval", 600)))
    c_entry.pack()

    tray_var = tk.BooleanVar(value=app_settings.get("minimize_to_tray", True))
    tk.Checkbutton(settings_win, text="Minimize to Tray on Close", variable=tray_var, bg="#1D2027", fg="white", selectcolor="#1D2027", activebackground="#1D2027", activeforeground="white").pack(pady=5)

    def save():
        try:
            app_settings["width"] = int(w_entry.get()) if w_entry.get() else None
            app_settings["height"] = int(h_entry.get())
            app_settings["x"] = int(x_entry.get()) if x_entry.get() else None
            app_settings["y"] = int(y_entry.get())
            app_settings["interval"] = int(i_entry.get())
            app_settings["check_interval"] = int(c_entry.get())
            app_settings["minimize_to_tray"] = tray_var.get()
            save_settings(app_settings)
            messagebox.showinfo("Success", "Settings saved.")
            settings_win.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Use numbers.")

    tk.Button(settings_win, text="Save", command=save).pack(pady=10)

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

def add_command():
    name = simpledialog.askstring("Input", "Name (key):")
    if not name: return
    label = simpledialog.askstring("Input", "Label (Icon/Text):")
    src = simpledialog.askstring("Input", "Source Path:")
    dst = simpledialog.askstring("Input", "Destination Path:")
    if name and label and src and dst:
        commands[name] = {
            "cmd": "rclone check src dst --fast-list --size-only",
            "src": src,
            "dst": dst,
            "label": label,
            "left_click_cmd": "rclone sync src dst -P --fast-list --log-level INFO",
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        }
        save_commands(commands)
        refresh_gui()

# Periodically check using rclone
def check_and_update(label, cfg):
    def run_check():
        log_path = os.path.join(LOG_DIR, f"{cfg['label']}_check.log")
        actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
        with open(log_path, "w") as f:
            subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
        
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                content = f.read()
            if "ERROR" not in content and "0 differences found" in content:
                label.config(fg="#06de22")
            else:
                label.config(fg="red")
        
        # Check again based on check_interval setting (in milliseconds)
        check_interval_ms = app_settings.get("check_interval", 600) * 1000
        if label.winfo_exists():
            label.after(check_interval_ms, lambda: threading.Thread(target=run_check, daemon=True).start())
    
    threading.Thread(target=run_check, daemon=True).start()

def create_gui():
    # Clear existing widgets if any (for refresh)
    for widget in ROOT1.winfo_children():
        widget.destroy()

    for key, cfg in commands.items():
        lbl = tk.Label(
            ROOT1,
            bg="#1d2027",
            text=cfg["label"],
            font=("JetBrainsMono NFP", 16, "bold"),
            fg="#FFFFFF",
            cursor="hand2"
        )
        lbl.pack(side="left", padx=(5, 5))

        # Event bindings
        lbl.bind("<Button-1>", lambda event, c=cfg: on_label_click(event, c))           # left click
        lbl.bind("<Control-Button-1>", lambda event, c=cfg: ctrl_left_click(event, c))  # ctrl + left
        lbl.bind("<Control-Button-3>", lambda event, c=cfg: ctrl_right_click(event, c)) # ctrl + right
        
        # Right click to remove (without ctrl)
        lbl.bind("<Button-3>", lambda event, k=key: remove_command(k))

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
    if auto_sync_enabled:
        threading.Thread(target=auto_sync_loop, daemon=True).start()

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

# Support dragging on the main frame
MAIN_FRAME.bind("<Button-1>", start_drag)
MAIN_FRAME.bind("<B1-Motion>", do_drag)
ROOT1.bind("<Button-1>", start_drag)
ROOT1.bind("<B1-Motion>", do_drag)

# Call GUI init
create_gui()
ROOT.mainloop()
