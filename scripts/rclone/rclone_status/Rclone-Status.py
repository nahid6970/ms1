#? https://pypi.org/project/pretty-errors/

from customtkinter import *
import ctypes
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import sys
import win32gui
import win32con
from io import StringIO, BytesIO
try:
    import cairosvg
except ImportError:
    cairosvg = None

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#06de22"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

# SVG Icons
RCLONE_SVG = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="256" height="257" viewBox="0 0 256 257" version="1.1" xmlns="http://www.w3.org/2000/svg">
    <g transform="matrix(1,0,0,1,0,-213)">
        <g id="favicon_color" transform="matrix(3.85779,0,0,3.85779,-459.077,-1271.68)">
            <rect x="119" y="385" width="66.359" height="66.359" style="fill:none;"/>
            <clipPath id="_clip1">
                <rect x="119" y="385" width="66.359" height="66.359"/>
            </clipPath>
            <g clip-path="url(#_clip1)">
                <g transform="matrix(0.57336,0,0,0.57336,23.1139,331.755)">
                    <g transform="matrix(1.65888,0,0,1.65888,278.227,196.518)">
                        <path d="M0,-26.524C-2.206,-30.345 -5.416,-33.225 -9.105,-35.023C-9.577,-32.503 -10.47,-30.019 -11.823,-27.675L-13.958,-23.97C-12.536,-23.18 -11.298,-22.017 -10.425,-20.505C-7.86,-16.063 -9.383,-10.381 -13.826,-7.816C-18.268,-5.251 -23.95,-6.773 -26.515,-11.216L-30.823,-18.666L-37.775,-18.666L-41.251,-12.646L-36.94,-5.197C-31.05,5.004 -18.007,8.499 -7.806,2.609C2.394,-3.28 5.889,-16.323 0,-26.524" style="fill:rgb(112,202,242);fill-rule:nonzero;"/>
                    </g>
                    <g transform="matrix(1.65888,0,0,1.65888,242.791,151.553)">
                        <path d="M0,-30.703C-10.201,-36.592 -23.244,-33.097 -29.133,-22.897C-31.34,-19.076 -32.228,-14.856 -31.941,-10.762C-29.523,-11.613 -26.925,-12.082 -24.218,-12.082L-19.943,-12.086C-19.97,-13.712 -19.581,-15.366 -18.709,-16.877C-16.143,-21.32 -10.462,-22.843 -6.019,-20.277C-1.576,-17.712 -0.054,-12.031 -2.619,-7.588L-6.916,-0.132L-3.441,5.889L3.511,5.888L7.806,-1.57C13.696,-11.77 10.201,-24.814 0,-30.703" style="fill:rgb(180,227,249);fill-rule:nonzero;"/>
                    </g>
                    <g transform="matrix(1.65888,0,0,1.65888,214.076,150.846)">
                        <path d="M0,23.335L-2.142,19.634C-3.537,20.471 -5.163,20.961 -6.908,20.961C-12.039,20.961 -16.198,16.802 -16.198,11.671C-16.198,6.541 -12.039,2.382 -6.908,2.382L1.697,2.376L5.174,-3.644L1.697,-9.664L-6.909,-9.656C-18.688,-9.656 -28.236,-0.107 -28.236,11.671C-28.236,23.45 -18.688,32.999 -6.909,32.999C-2.498,32.999 1.599,31.659 5,29.366C3.054,27.697 1.353,25.678 0,23.335" style="fill:rgb(63,121,173);fill-rule:nonzero;"/>
                    </g>
                </g>
            </g>
        </g>
    </g>
</svg>"""

ARROW_RIGHT_SVG = """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="#00F0FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
ARROW_LEFT_SVG = """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M19 12H5M5 12L12 5M5 12L12 19" stroke="#00F0FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

# File paths
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
        "width": None,
        "height": 39,
        "x": None,
        "y": 993,
        "check_interval": 600,
        "minimize_to_tray": True,
        "topmost": False,
        "dialog_width": 550,
        "settings_win_width": 480,
        "settings_win_height": 700,
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

# Global variables
commands = load_commands()
app_settings = load_settings()
tray_icon = None
pending_checks = 0
check_lock = threading.Lock()

def get_svg_image(svg_data, size=(32, 32)):
    if cairosvg:
        try:
            png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), output_width=size[0], output_height=size[1])
            return ImageTk.PhotoImage(Image.open(BytesIO(png_data)))
        except: pass
    # Fallback text-based look if SVG rendering fails
    return None

class ProjectActionWindow(tk.Toplevel):
    def __init__(self, master, cfg, key):
        super().__init__(master)
        self.cfg = cfg
        self.key = key
        self.title(f"Rclone: {key}")
        self.geometry("900x550")
        self.configure(bg=CP_BG)
        self.direction = "L2R" # Default Left to Right
        
        self.init_ui()

    def init_ui(self):
        # Header
        header = tk.Frame(self, bg=CP_PANEL, height=40)
        header.pack(fill="x", side="top")
        tk.Label(header, text=f"PROJECT: {self.key}", bg=CP_PANEL, fg=CP_YELLOW, font=("Consolas", 12, "bold")).pack(pady=10)

        # Main Layout
        main_content = tk.Frame(self, bg=CP_BG)
        main_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Path Selection Area
        path_frame = tk.Frame(main_content, bg=CP_BG)
        path_frame.pack(fill="x")

        # Left Side
        left_frame = tk.Frame(path_frame, bg=CP_BG)
        left_frame.pack(side="left", fill="both", expand=True)
        tk.Label(left_frame, text="SIDE A", bg=CP_BG, fg=CP_CYAN, font=("Consolas", 10)).pack(anchor="w")
        self.side_a_ent = tk.Entry(left_frame, bg=CP_PANEL, fg=CP_TEXT, insertbackground=CP_CYAN, bd=1, relief="solid")
        self.side_a_ent.insert(0, self.cfg["src"])
        self.side_a_ent.pack(fill="x", pady=5)

        # Middle (Arrow Button)
        mid_frame = tk.Frame(path_frame, bg=CP_BG)
        mid_frame.pack(side="left", padx=20)
        self.arrow_btn = tk.Button(mid_frame, text="==>", bg=CP_DIM, fg=CP_CYAN, font=("Consolas", 14, "bold"), 
                                  command=self.toggle_direction, relief="flat", padx=10)
        self.arrow_btn.pack()

        # Right Side
        right_frame = tk.Frame(path_frame, bg=CP_BG)
        right_frame.pack(side="left", fill="both", expand=True)
        tk.Label(right_frame, text="SIDE B", bg=CP_BG, fg=CP_CYAN, font=("Consolas", 10)).pack(anchor="e")
        self.side_b_ent = tk.Entry(right_frame, bg=CP_PANEL, fg=CP_TEXT, insertbackground=CP_CYAN, bd=1, relief="solid", justify="right")
        self.side_b_ent.insert(0, self.cfg["dst"])
        self.side_b_ent.pack(fill="x", pady=5)

        # Operation Selection
        op_frame = tk.Frame(main_content, bg=CP_BG)
        op_frame.pack(pady=20)
        self.op_var = tk.StringVar(value="sync")
        for op in ["sync", "copy", "check"]:
            rb = tk.Radiobutton(op_frame, text=op.upper(), variable=self.op_var, value=op, bg=CP_BG, fg=CP_TEXT, 
                                selectcolor=CP_PANEL, activebackground=CP_BG, activeforeground=CP_CYAN, font=("Consolas", 10))
            rb.pack(side="left", padx=15)

        # Middle Action Button
        self.action_btn = tk.Button(main_content, text="START OPERATION", bg=CP_YELLOW, fg="black", font=("Consolas", 12, "bold"), 
                                    command=self.execute_task, relief="flat", pady=10, width=30)
        self.action_btn.pack()

        # Additional Fields
        extra_frame = tk.Frame(main_content, bg=CP_BG)
        extra_frame.pack(fill="x", pady=20)
        
        tk.Label(extra_frame, text="Ignore (e.g. node_modules,*.tmp):", bg=CP_BG, fg=CP_TEXT, font=("Consolas", 9)).grid(row=0, column=0, sticky="w")
        self.ignore_ent = tk.Entry(extra_frame, bg=CP_PANEL, fg=CP_CYAN, bd=1, relief="solid")
        self.ignore_ent.grid(row=0, column=1, sticky="ew", padx=(10,0))

        tk.Label(extra_frame, text="Flags (e.g. --fast-list -P):", bg=CP_BG, fg=CP_TEXT, font=("Consolas", 9)).grid(row=1, column=0, sticky="w", pady=10)
        self.flags_ent = tk.Entry(extra_frame, bg=CP_PANEL, fg=CP_CYAN, bd=1, relief="solid")
        self.flags_ent.insert(0, "--fast-list -P --size-only")
        self.flags_ent.grid(row=1, column=1, sticky="ew", padx=(10,0))
        extra_frame.columnconfigure(1, weight=1)

        # Status / Log
        self.log_text = tk.Text(main_content, height=8, bg=CP_PANEL, fg=CP_TEXT, font=("Consolas", 9), bd=0)
        self.log_text.pack(fill="both", expand=True)

    def toggle_direction(self):
        if self.direction == "L2R":
            self.direction = "R2L"
            self.arrow_btn.config(text="<==")
            self.side_a_ent.config(fg=CP_YELLOW)
            self.side_b_ent.config(fg=CP_CYAN)
        else:
            self.direction = "L2R"
            self.arrow_btn.config(text="==>")
            self.side_a_ent.config(fg=CP_CYAN)
            self.side_b_ent.config(fg=CP_YELLOW)

    def execute_task(self):
        op = self.op_var.get()
        side_a = self.side_a_ent.get()
        side_b = self.side_b_ent.get()
        ignore = self.ignore_ent.get()
        flags = self.flags_ent.get()

        if self.direction == "L2R":
            src, dst = side_a, side_b
        else:
            src, dst = side_b, side_a

        cmd = f'rclone {op} "{src}" "{dst}" {flags}'
        if ignore:
            for item in ignore.split(','):
                cmd += f' --exclude "{item.strip()}"'

        self.action_btn.config(state="disabled", text="RUNNING...")
        self.log_text.insert("end", f"\n> Executing: {cmd}\n")
        self.log_text.see("end")

        def run():
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.log_text.insert("end", line)
                self.log_text.see("end")
            process.wait()
            self.action_btn.config(state="normal", text="START OPERATION")
            self.log_text.insert("end", f"\n> Finished with code {process.returncode}\n")
            # Refresh status in main window after operation
            trigger_all_checks()

        threading.Thread(target=run, daemon=True).start()

def on_label_click(event, cfg, key):
    ProjectActionWindow(ROOT, cfg, key)

def add_command():
    edit_command(None)

def edit_command(key):
    is_edit = key is not None
    cfg = commands.get(key, {
        "label": "NEW", "src": "C:/", "dst": "remote:/", 
        "cmd": "rclone check src dst --size-only", "index": len(commands), "enabled": True
    })
    
    dialog = tk.Toplevel(ROOT)
    dialog.title("Edit Project" if is_edit else "Add Project")
    dialog.geometry("500x550")
    dialog.configure(bg=CP_BG)
    dialog.transient(ROOT)

    def create_field(parent, label, default_val):
        frame = tk.Frame(parent, bg=CP_BG)
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text=label, bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 10)).pack(anchor="w")
        ent = tk.Entry(frame, bg=CP_PANEL, fg=CP_CYAN, insertbackground=CP_CYAN, bd=1, relief="solid")
        ent.insert(0, str(default_val))
        ent.pack(fill="x", pady=2)
        return ent

    name_ent = create_field(dialog, "Unique Name (Key):", key if key else f"project_{len(commands)}")
    label_ent = create_field(dialog, "Display Icon/Label:", cfg["label"])
    src_ent = create_field(dialog, "Side A (Source):", cfg["src"])
    dst_ent = create_field(dialog, "Side B (Destination):", cfg["dst"])
    cmd_ent = create_field(dialog, "Check Command:", cfg["cmd"])
    idx_ent = create_field(dialog, "Sort Index:", cfg["index"])

    def save():
        new_key = name_ent.get()
        if is_edit and new_key != key:
            del commands[key]
        
        commands[new_key] = {
            "label": label_ent.get(),
            "src": src_ent.get(),
            "dst": dst_ent.get(),
            "cmd": cmd_ent.get(),
            "index": int(idx_ent.get()),
            "enabled": True
        }
        save_commands(commands)
        create_gui()
        dialog.destroy()
        trigger_all_checks()

    def delete():
        if messagebox.askyesno("Confirm", f"Delete {key}?"):
            del commands[key]
            save_commands(commands)
            create_gui()
            dialog.destroy()

    btn_frame = tk.Frame(dialog, bg=CP_BG)
    btn_frame.pack(pady=20)
    
    HoverButton(btn_frame, text="SAVE", command=save, width=15, default_color=CP_GREEN, hover_color=CP_YELLOW).pack(side="left", padx=5)
    if is_edit:
        HoverButton(btn_frame, text="DELETE", command=delete, width=15, default_color=CP_RED, hover_color=CP_YELLOW).pack(side="left", padx=5)
    HoverButton(btn_frame, text="CANCEL", command=dialog.destroy, width=15).pack(side="left", padx=5)


def check_and_update_label(label, cfg):
    def run_check():
        actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
        try:
            res = subprocess.run(actual_cmd, shell=True, capture_output=True, text=True)
            if "0 differences found" in res.stdout and "ERROR" not in res.stdout:
                label.config(fg=CP_GREEN)
            else:
                label.config(fg=CP_RED)
        finally:
            mark_check_complete()

    label.trigger_check = lambda: threading.Thread(target=run_check, daemon=True).start()

def mark_check_complete():
    global pending_checks
    with check_lock:
        pending_checks -= 1
        if pending_checks <= 0:
            start_global_countdown()

def start_global_countdown():
    interval = app_settings.get("check_interval", 600)
    ROOT.after(interval * 1000, trigger_all_checks)

def trigger_all_checks():
    global pending_checks
    widgets = [w for w in ROOT1.winfo_children() if hasattr(w, 'trigger_check')]
    with check_lock:
        pending_checks = len(widgets)
    if pending_checks == 0:
        start_global_countdown()
        return
    for w in widgets:
        w.trigger_check()

# UI Helpers
class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.default_color = kw.pop('default_color', CP_DIM)
        self.hover_color = kw.pop('hover_color', CP_RED)
        self.default_fg = kw.pop('default_fg', "#FFFFFF")
        self.hover_fg = kw.pop('hover_fg', "#000000")
        super().__init__(master, **kw)
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_color, fg=self.hover_fg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.default_color, fg=self.default_fg))
        self.configure(bg=self.default_color, fg=self.default_fg, bd=0, highlightthickness=0)

def quit_app():
    if tray_icon: tray_icon.stop()
    ROOT.quit()
    os._exit(0)

# Main Application Window
ROOT = tk.Tk()
ROOT.overrideredirect(True)
ROOT.configure(bg=CP_BG)

# Custom border
BORDER_FRAME = tk.Frame(ROOT, bg=CP_DIM, bd=0, highlightthickness=1, highlightbackground=CP_RED)
BORDER_FRAME.place(relwidth=1, relheight=1)

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg=CP_BG)
MAIN_FRAME.pack(pady=1, padx=2, expand=True, fill="both")

ROOT1 = tk.Frame(MAIN_FRAME, bg=CP_PANEL)
ROOT1.pack(side="left", pady=2, padx=5) # Removed fill="x"

def create_gui():
    for widget in ROOT1.winfo_children(): widget.destroy()
    sorted_items = sorted(commands.items(), key=lambda x: (x[1].get("index", 0), x[0]))

    for key, cfg in sorted_items:
        if not cfg.get("enabled", True): continue
        lbl = tk.Label(ROOT1, bg=CP_PANEL, text=cfg["label"], font=("JetBrainsMono NFP", 16, "bold"), fg="#555555", cursor="hand2")
        lbl.pack(side="left", padx=8)
        lbl.bind("<Button-1>", lambda event, c=cfg, k=key: on_label_click(event, c, k))
        lbl.bind("<Button-3>", lambda event, k=key: edit_command(k)) # Right-click to edit
        check_and_update_label(lbl, cfg)

    # Separator
    tk.Frame(ROOT1, width=2, bg=CP_DIM).pack(side="left", padx=5, fill="y", pady=5)

    # Control Buttons
    btn_add = HoverButton(ROOT1, text="\uf067", font=("JetBrainsMono NFP", 12), command=add_command, default_color=CP_PANEL, hover_color=CP_CYAN)
    btn_add.pack(side="left", padx=2)
    
    btn_reload = HoverButton(ROOT1, text="\uf021", font=("JetBrainsMono NFP", 12), command=lambda: os.execv(sys.executable, ['python'] + sys.argv), default_color=CP_PANEL)
    btn_reload.pack(side="left", padx=2)
    
    btn_close = HoverButton(ROOT1, text="\uf00d", font=("JetBrainsMono NFP", 12), command=quit_app, hover_color=CP_RED, default_color=CP_PANEL)
    btn_close.pack(side="left", padx=(2, 5))

    def adjust_width():
        ROOT.update_idletasks()
        # Calculate width: ROOT1 width + internal margins + outer border space
        # ROOT1 padx is 5 on both sides (10 total) + BORDER_FRAME highlight (2 total) + safety (2)
        w = ROOT1.winfo_reqwidth() + 14 
        ROOT.geometry(f"{w}x{app_settings['height']}+{app_settings['x'] or 100}+{app_settings['y'] or 100}")
    
    # Schedule multiple updates to catch rendering timing
    ROOT.after(10, adjust_width)
    ROOT.after(100, adjust_width)

# Dragging logic
drag_data = {"x": 0, "y": 0}
def start_drag(e): drag_data["x"], drag_data["y"] = e.x, e.y
def do_drag(e):
    x, y = (e.x - drag_data["x"] + ROOT.winfo_x(), e.y - drag_data["y"] + ROOT.winfo_y())
    ROOT.geometry(f"+{x}+{y}")
    app_settings["x"], app_settings["y"] = x, y
    save_settings(app_settings)

MAIN_FRAME.bind("<Button-1>", start_drag)
MAIN_FRAME.bind("<B1-Motion>", do_drag)

create_gui()
trigger_all_checks()
ROOT.mainloop()
