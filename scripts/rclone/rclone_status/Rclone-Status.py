#? https://pypi.org/project/pretty-errors/

import ctypes
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox
import json
from PIL import Image, ImageTk
import sys
from io import BytesIO
try:
    import cairosvg
except ImportError:
    cairosvg = None

# CYBERPUNK THEME PALETTE (From THEME_GUIDE.md)
CP_BG = "#050505"           # Main Window Background
CP_PANEL = "#111111"        # Panel/Input Background
CP_YELLOW = "#FCEE0A"       # Accent: Yellow
CP_CYAN = "#00F0FF"         # Accent: Cyan
CP_RED = "#FF003C"          # Accent: Red
CP_GREEN = "#00ff21"        # Accent: Green
CP_ORANGE = "#ff934b"       # Accent: Orange
CP_DIM = "#3a3a3a"          # Dimmed/Borders/Inactive
CP_TEXT = "#E0E0E0"         # Primary Text
CP_SUBTEXT = "#808080"      # Secondary Text

# SVG Resources
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
        "topmost": True
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

commands = load_commands()
app_settings = load_settings()
pending_checks = 0
check_lock = threading.Lock()

def get_svg_image(svg_data, size=(32, 32)):
    if cairosvg:
        try:
            png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), output_width=size[0], output_height=size[1])
            return ImageTk.PhotoImage(Image.open(BytesIO(png_data)))
        except: pass
    return None

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.default_color = kw.pop('default_color', CP_DIM)
        self.hover_color = kw.pop('hover_color', CP_YELLOW)
        self.default_fg = kw.pop('default_fg', "white")
        self.hover_fg = kw.pop('hover_fg', "black")
        super().__init__(master, **kw)
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_color, fg=self.hover_fg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.default_color, fg=self.default_fg))
        self.configure(bg=self.default_color, fg=self.default_fg, bd=0, highlightthickness=0, font=("Consolas", 10, "bold"), cursor="hand2")

class CyberEntry(tk.Entry):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.configure(bg=CP_PANEL, fg=CP_CYAN, insertbackground=CP_CYAN, bd=1, relief="solid", highlightthickness=1, highlightbackground=CP_DIM, highlightcolor=CP_CYAN, font=("Consolas", 10))

class ProjectActionWindow(tk.Toplevel):
    def __init__(self, master, cfg, key):
        super().__init__(master)
        self.cfg = cfg
        self.key = key
        self.title(f"CYBER-SYNC: {key}")
        self.geometry("900x600")
        self.configure(bg=CP_BG)
        self.direction = "L2R" 
        self.img_r = get_svg_image(ARROW_RIGHT_SVG, (40, 40))
        self.img_l = get_svg_image(ARROW_LEFT_SVG, (40, 40))
        self.init_ui()

    def init_ui(self):
        header = tk.Frame(self, bg=CP_PANEL, height=2)
        header.pack(fill="x", side="top")
        
        title_lbl = tk.Label(self, text=f"// PROJECT_ID: {self.key.upper()}", bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 14, "bold"))
        title_lbl.pack(pady=15, padx=20, anchor="w")

        main_content = tk.Frame(self, bg=CP_BG)
        main_content.pack(fill="both", expand=True, padx=25)

        # Path Selection Group
        path_group = tk.LabelFrame(main_content, text=" DATA CHANNELS ", bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 9, "bold"), bd=1, relief="solid", labelanchor="nw")
        path_group.pack(fill="x", pady=10, ipady=15, padx=5)

        inner_path = tk.Frame(path_group, bg=CP_BG)
        inner_path.pack(fill="x", padx=15, pady=10)

        # Side A
        a_frame = tk.Frame(inner_path, bg=CP_BG)
        a_frame.pack(side="left", fill="both", expand=True)
        tk.Label(a_frame, text="SIDE_A", bg=CP_BG, fg=CP_CYAN, font=("Consolas", 8)).pack(anchor="w")
        self.side_a_ent = CyberEntry(a_frame)
        self.side_a_ent.insert(0, self.cfg["src"])
        self.side_a_ent.pack(fill="x", pady=5)

        # Middle (Arrow)
        mid_frame = tk.Frame(inner_path, bg=CP_BG)
        mid_frame.pack(side="left", padx=20)
        self.arrow_btn = tk.Button(mid_frame, image=self.img_r, bg=CP_BG, activebackground=CP_BG, bd=0, command=self.toggle_direction, cursor="hand2")
        self.arrow_btn.pack()

        # Side B
        b_frame = tk.Frame(inner_path, bg=CP_BG)
        b_frame.pack(side="left", fill="both", expand=True)
        tk.Label(b_frame, text="SIDE_B", bg=CP_BG, fg=CP_CYAN, font=("Consolas", 8)).pack(anchor="e")
        self.side_b_ent = CyberEntry(b_frame, justify="right")
        self.side_b_ent.insert(0, self.cfg["dst"])
        self.side_b_ent.pack(fill="x", pady=5)

        # Controls Group
        ctrl_group = tk.LabelFrame(main_content, text=" EXECUTION_PARAMETERS ", bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 9, "bold"), bd=1, relief="solid")
        ctrl_group.pack(fill="x", pady=10, ipady=10, padx=5)

        op_frame = tk.Frame(ctrl_group, bg=CP_BG)
        op_frame.pack(pady=5)
        self.op_var = tk.StringVar(value="sync")
        for op in ["sync", "copy", "check"]:
            rb = tk.Radiobutton(op_frame, text=op.upper(), variable=self.op_var, value=op, bg=CP_BG, fg=CP_TEXT, selectcolor=CP_PANEL, activebackground=CP_BG, activeforeground=CP_CYAN, font=("Consolas", 10, "bold"))
            rb.pack(side="left", padx=20)

        input_grid = tk.Frame(ctrl_group, bg=CP_BG)
        input_grid.pack(fill="x", padx=20, pady=10)
        
        tk.Label(input_grid, text="IGNORE_LIST:", bg=CP_BG, fg=CP_TEXT, font=("Consolas", 9)).grid(row=0, column=0, sticky="w")
        self.ignore_ent = CyberEntry(input_grid)
        self.ignore_ent.grid(row=0, column=1, sticky="ew", padx=(10,0))

        tk.Label(input_grid, text="FLAGS_EXT:", bg=CP_BG, fg=CP_TEXT, font=("Consolas", 9)).grid(row=1, column=0, sticky="w", pady=10)
        self.flags_ent = CyberEntry(input_grid)
        self.flags_ent.insert(0, "--fast-list -P --size-only")
        self.flags_ent.grid(row=1, column=1, sticky="ew", padx=(10,0), pady=10)
        input_grid.columnconfigure(1, weight=1)

        # Start Button
        self.action_btn = HoverButton(main_content, text="INITIALIZE TASK", bg=CP_DIM, default_color=CP_DIM, hover_color=CP_YELLOW, command=self.execute_task, pady=10)
        self.action_btn.pack(fill="x", pady=10)

        # Log
        self.log_text = tk.Text(main_content, height=10, bg=CP_PANEL, fg=CP_TEXT, font=("Consolas", 9), bd=1, relief="solid", highlightthickness=0)
        self.log_text.pack(fill="both", expand=True, pady=(10, 20))

    def toggle_direction(self):
        if self.direction == "L2R":
            self.direction = "R2L"
            self.arrow_btn.config(image=self.img_l)
            self.side_a_ent.config(highlightbackground=CP_RED)
            self.side_b_ent.config(highlightbackground=CP_CYAN)
        else:
            self.direction = "L2R"
            self.arrow_btn.config(image=self.img_r)
            self.side_a_ent.config(highlightbackground=CP_CYAN)
            self.side_b_ent.config(highlightbackground=CP_RED)

    def execute_task(self):
        op = self.op_var.get()
        side_a = self.side_a_ent.get()
        side_b = self.side_b_ent.get()
        ignore = self.ignore_ent.get()
        flags = self.flags_ent.get()

        src, dst = (side_a, side_b) if self.direction == "L2R" else (side_b, side_a)
        cmd = f'rclone {op} "{src}" "{dst}" {flags}'
        if ignore:
            for item in ignore.split(','): cmd += f' --exclude "{item.strip()}"'

        self.action_btn.config(state="disabled", text="PROCESSING...")
        self.log_text.insert("end", f"// INITIATING: {cmd}\n", "header")
        self.log_text.tag_config("header", foreground=CP_YELLOW)

        def run():
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.log_text.insert("end", f" > {line}")
                self.log_text.see("end")
            process.wait()
            self.action_btn.config(state="normal", text="INITIALIZE TASK")
            self.log_text.insert("end", f"// TASK_COMPLETE [CODE: {process.returncode}]\n\n", "header")
            trigger_all_checks()

        threading.Thread(target=run, daemon=True).start()

def add_command(): edit_command(None)

def edit_command(key):
    is_edit = key is not None
    cfg = commands.get(key, {"label": "NEW", "src": "C:/", "dst": "remote:/", "cmd": "rclone check src dst --size-only", "index": len(commands), "enabled": True})
    
    dialog = tk.Toplevel(ROOT)
    dialog.title("SECURE_CONFIG")
    dialog.geometry("500x580")
    dialog.configure(bg=CP_BG)

    def create_field(parent, label, val):
        f = tk.Frame(parent, bg=CP_BG)
        f.pack(fill="x", pady=8, padx=20)
        tk.Label(f, text=label, bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 8, "bold")).pack(anchor="w")
        e = CyberEntry(f)
        e.insert(0, str(val))
        e.pack(fill="x", pady=2)
        return e

    name_e = create_field(dialog, "REGISTRY_KEY", key if key else f"proj_{len(commands)}")
    label_e = create_field(dialog, "UI_LABEL", cfg["label"])
    src_e = create_field(dialog, "SOURCE_PATH", cfg["src"])
    dst_e = create_field(dialog, "DEST_PATH", cfg["dst"])
    cmd_e = create_field(dialog, "CHECK_CMD", cfg["cmd"])
    idx_e = create_field(dialog, "SORT_PRIORITY", cfg["index"])

    def save():
        new_key = name_e.get()
        if is_edit and new_key != key: del commands[key]
        commands[new_key] = {"label": label_e.get(), "src": src_e.get(), "dst": dst_e.get(), "cmd": cmd_e.get(), "index": int(idx_e.get()), "enabled": True}
        save_commands(commands)
        create_gui()
        dialog.destroy()
        trigger_all_checks()

    btn_f = tk.Frame(dialog, bg=CP_BG)
    btn_f.pack(pady=20)
    HoverButton(btn_f, text="SAVE", command=save, width=15, hover_color=CP_GREEN).pack(side="left", padx=5)
    if is_edit:
        HoverButton(btn_f, text="DELETE", command=lambda: [commands.pop(key), save_commands(commands), create_gui(), dialog.destroy()], width=15, hover_color=CP_RED).pack(side="left", padx=5)
    HoverButton(btn_f, text="EXIT", command=dialog.destroy, width=15).pack(side="left", padx=5)

def check_and_update_label(label, cfg):
    def run_check():
        actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
        try:
            res = subprocess.run(actual_cmd, shell=True, capture_output=True, text=True)
            label.config(fg=CP_GREEN if "0 differences found" in res.stdout and "ERROR" not in res.stdout else CP_RED)
        finally: mark_check_complete()
    label.trigger_check = lambda: threading.Thread(target=run_check, daemon=True).start()

def mark_check_complete():
    global pending_checks
    with check_lock:
        pending_checks -= 1
        if pending_checks <= 0: ROOT.after(app_settings.get("check_interval", 600) * 1000, trigger_all_checks)

def trigger_all_checks():
    global pending_checks
    widgets = [w for w in ROOT1.winfo_children() if hasattr(w, 'trigger_check')]
    with check_lock: pending_checks = len(widgets)
    if not widgets: ROOT.after(60000, trigger_all_checks); return
    for w in widgets: w.trigger_check()

# Main UI
ROOT = tk.Tk()
ROOT.overrideredirect(True)
ROOT.configure(bg=CP_BG)
ROOT.attributes("-topmost", app_settings["topmost"])

BORDER_FRAME = tk.Frame(ROOT, bg=CP_DIM, bd=0, highlightthickness=1, highlightbackground=CP_RED)
BORDER_FRAME.place(relwidth=1, relheight=1)

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg=CP_BG)
MAIN_FRAME.pack(pady=1, padx=2, expand=True, fill="both")

ROOT1 = tk.Frame(MAIN_FRAME, bg=CP_PANEL)
ROOT1.pack(side="left", pady=2, padx=5)

def create_gui():
    for widget in ROOT1.winfo_children(): widget.destroy()
    sorted_items = sorted(commands.items(), key=lambda x: (x[1].get("index", 0), x[0]))

    for key, cfg in sorted_items:
        if not cfg.get("enabled", True): continue
        lbl = tk.Label(ROOT1, bg=CP_PANEL, text=cfg["label"], font=("JetBrainsMono NFP", 16, "bold"), fg=CP_DIM, cursor="hand2")
        lbl.pack(side="left", padx=10)
        lbl.bind("<Button-1>", lambda e, c=cfg, k=key: ProjectActionWindow(ROOT, c, k))
        lbl.bind("<Button-3>", lambda e, k=key: edit_command(k))
        check_and_update_label(lbl, cfg)

    tk.Frame(ROOT1, width=1, bg=CP_DIM).pack(side="left", padx=8, fill="y", pady=8)

    HoverButton(ROOT1, text="\uf067", command=add_command, default_color=CP_PANEL, hover_color=CP_CYAN).pack(side="left", padx=2)
    HoverButton(ROOT1, text="\uf021", command=lambda: os.execv(sys.executable, ['python'] + sys.argv), default_color=CP_PANEL).pack(side="left", padx=2)
    HoverButton(ROOT1, text="\uf00d", command=lambda: sys.exit(0), hover_color=CP_RED, default_color=CP_PANEL).pack(side="left", padx=(2, 8))

    def adjust_width():
        ROOT.update_idletasks()
        w = ROOT1.winfo_reqwidth() + 14 
        ROOT.geometry(f"{w}x{app_settings['height']}+{app_settings['x'] or 100}+{app_settings['y'] or 100}")
    ROOT.after(50, adjust_width)

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
