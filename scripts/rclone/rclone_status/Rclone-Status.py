#? https://pypi.org/project/pretty-errors/

import ctypes
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox, colorchooser
import json
from PIL import Image, ImageTk
import sys
from io import BytesIO
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
CP_GREEN = "#00ff21"        
CP_ORANGE = "#ff934b"       
CP_DIM = "#3a3a3a"          
CP_TEXT = "#E0E0E0"         

JSON_PATH = os.path.join(os.path.dirname(__file__), "commands.json")
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
LOG_DIR = r"C:\Users\nahid\script_output\rclone"
os.makedirs(LOG_DIR, exist_ok=True)

def load_commands():
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def save_commands(cmds):
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(cmds, f, indent=4)
    except: pass

def load_settings():
    default = {
        "width": None, "height": 39, "x": 100, "y": 100, 
        "check_interval": 600, "topmost": True,
        "icon_l": "\uf100", "icon_r": "\uf101",
        "icon_size": 22,
        "color_l": "#ff934b", # CP_ORANGE default
        "color_r": "#00F0FF"  # CP_CYAN default
    }
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return {**default, **json.load(f)}
        except: pass
    return default

def save_settings(stg):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(stg, f, indent=4)
    except: pass

commands = load_commands()
app_settings = load_settings()
pending_checks = 0
check_lock = threading.Lock()

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.default_color = kw.pop('default_color', CP_DIM)
        self.hover_color = kw.pop('hover_color', CP_YELLOW)
        self.default_fg = kw.pop('default_fg', "white")
        self.hover_fg = kw.pop('hover_fg', "black")
        # Use passed font if available, otherwise use default
        btn_font = kw.pop('font', ("Consolas", 10, "bold"))
        super().__init__(master, **kw)
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_color, fg=self.hover_fg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.default_color, fg=self.default_fg))
        self.configure(bg=self.default_color, fg=self.default_fg, bd=0, highlightthickness=0, font=btn_font, cursor="hand2")

class CyberEntry(tk.Entry):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.configure(bg=CP_PANEL, fg=CP_CYAN, insertbackground=CP_CYAN, bd=1, relief="solid", highlightthickness=1, highlightbackground=CP_DIM, highlightcolor=CP_CYAN, font=("Consolas", 10))

def setup_custom_window(win, title, width, height):
    win.overrideredirect(True)
    # Center window on screen
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    center_x = (sw // 2) - (width // 2)
    center_y = (sh // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{center_x}+{center_y}")
    win.configure(bg=CP_BG)
    
    border = tk.Frame(win, bg=CP_DIM, bd=0, highlightthickness=1, highlightbackground=CP_CYAN)
    border.place(relwidth=1, relheight=1)
    
    title_bar = tk.Frame(border, bg=CP_PANEL, height=30)
    title_bar.pack(fill="x")
    
    tk.Label(title_bar, text=f"// {title}", bg=CP_PANEL, fg=CP_YELLOW, font=("Consolas", 9, "bold")).pack(side="left", padx=10)
    
    close_btn = tk.Button(title_bar, text="\uf00d", font=("JetBrainsMono NFP", 10), bg=CP_PANEL, fg=CP_DIM, activebackground=CP_RED, activeforeground="white", bd=0, command=win.destroy, cursor="hand2")
    close_btn.pack(side="right", padx=5)
    close_btn.bind("<Enter>", lambda e: close_btn.config(fg="white", bg=CP_RED))
    close_btn.bind("<Leave>", lambda e: close_btn.config(fg=CP_DIM, bg=CP_PANEL))

    def start_move(e): win.x, win.y = e.x, e.y
    def do_move(e):
        x, y = (e.x - win.x + win.winfo_x(), e.y - win.y + win.winfo_y())
        win.geometry(f"+{x}+{y}")
        
    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)
    return border

class ProjectActionWindow(tk.Toplevel):
    def __init__(self, master, cfg, key):
        super().__init__(master)
        self.cfg = cfg
        self.key = key
        self.direction = cfg.get("last_dir", "L2R")
        self.op_mode = cfg.get("last_op", "sync")
        
        self.container = setup_custom_window(self, f"TASK_RUNNER: {key.upper()}", 900, 600)
        self.init_ui()

    def init_ui(self):
        content = tk.Frame(self.container, bg=CP_BG)
        content.pack(fill="both", expand=True, padx=25, pady=10)

        path_group = tk.LabelFrame(content, text=" I/O_CHANNELS ", bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 9, "bold"), bd=1, relief="solid", labelanchor="nw")
        path_group.pack(fill="x", pady=5, ipady=5)

        inner = tk.Frame(path_group, bg=CP_BG)
        inner.pack(fill="x", padx=15, pady=5)

        self.side_a_ent = CyberEntry(inner)
        self.side_a_ent.insert(0, self.cfg["src"])
        self.side_a_ent.pack(side="left", fill="x", expand=True)

        # Styled Switcher using settings icons
        self.arrow_btn = HoverButton(inner, text=app_settings["icon_r"] if self.direction == "L2R" else app_settings["icon_l"], 
                                     font=("JetBrainsMono NFP", app_settings.get("icon_size", 22)), width=3, height=1, 
                                     default_color=CP_BG, hover_color=CP_CYAN, hover_fg="black")
        self.arrow_btn.default_fg = app_settings.get("color_r", CP_CYAN) if self.direction == "L2R" else app_settings.get("color_l", CP_ORANGE)
        self.arrow_btn.configure(fg=self.arrow_btn.default_fg)
        self.arrow_btn.config(command=self.toggle_direction)
        self.arrow_btn.pack(side="left", padx=25)

        self.side_b_ent = CyberEntry(inner, justify="right")
        self.side_b_ent.insert(0, self.cfg["dst"])
        self.side_b_ent.pack(side="left", fill="x", expand=True)

        mode_outer = tk.Frame(content, bg=CP_BG)
        mode_outer.pack(fill="x", pady=5)
        
        mode_frame = tk.Frame(mode_outer, bg=CP_BG)
        mode_frame.pack(anchor="center") 
        
        self.mode_btns = {}
        for m in ["sync", "copy", "check"]:
            btn = HoverButton(mode_frame, text=m.upper(), width=14, pady=5)
            btn.config(command=lambda mode=m: self.set_mode(mode))
            btn.pack(side="left", padx=10)
            self.mode_btns[m] = btn
        
        self.set_mode(self.op_mode)

        opt_group = tk.LabelFrame(content, text=" CONFIG_OVERRIDE ", bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 9, "bold"), bd=1, relief="solid")
        opt_group.pack(fill="x", pady=10, ipady=10)
        
        grid = tk.Frame(opt_group, bg=CP_BG)
        grid.pack(fill="x", padx=20, pady=5)
        
        tk.Label(grid, text="EXCLUSIONS:", bg=CP_BG, fg=CP_TEXT, font=("Consolas", 9)).grid(row=0, column=0, sticky="w")
        self.ignore_var = tk.StringVar(value=self.cfg.get("last_ignore", ""))
        self.ignore_ent = CyberEntry(grid, textvariable=self.ignore_var)
        self.ignore_ent.grid(row=0, column=1, sticky="ew", padx=(10,0))
        
        placeholder = "e.g. *.jpg, dir/**, C:/path/ignore.txt"
        self.ph_label = tk.Label(self.ignore_ent, text=placeholder, bg=CP_PANEL, fg="#007a7a", font=("Consolas", 10), cursor="xterm")
        
        def check_ph(*args):
            if not self.ignore_var.get():
                self.ph_label.place(x=4, y=0, relheight=1)
            else:
                self.ph_label.place_forget()
                
        self.ignore_var.trace_add("write", check_ph)
        self.ph_label.bind("<Button-1>", lambda e: self.ignore_ent.focus_set())
        check_ph()

        tk.Label(grid, text="RUNTIME_FLAGS:", bg=CP_BG, fg=CP_TEXT, font=("Consolas", 9)).grid(row=1, column=0, sticky="w", pady=10)
        self.flags_ent = CyberEntry(grid)
        self.flags_ent.insert(0, self.cfg.get("last_flags", "--fast-list -P --size-only"))
        self.flags_ent.grid(row=1, column=1, sticky="ew", padx=(10,0), pady=10)
        grid.columnconfigure(1, weight=1)

        self.action_btn = HoverButton(content, text="EXECUTE_CMD", bg=CP_DIM, hover_color=CP_GREEN, command=self.run_task, pady=10)
        self.action_btn.pack(fill="x", pady=5)

        self.log_text = tk.Text(content, height=10, bg=CP_PANEL, fg=CP_TEXT, font=("Consolas", 9), bd=0)
        self.log_text.pack(fill="both", expand=True, pady=10)
        self.update_ui_state()

    def set_mode(self, m):
        self.op_mode = m
        for k, b in self.mode_btns.items():
            if k == m:
                b.default_color, b.default_fg = CP_YELLOW, "black"
                b.configure(bg=CP_YELLOW, fg="black")
            else:
                b.default_color, b.default_fg = CP_PANEL, CP_TEXT
                b.configure(bg=CP_PANEL, fg=CP_TEXT)

    def toggle_direction(self):
        self.direction = "R2L" if self.direction == "L2R" else "L2R"
        self.arrow_btn.config(text=app_settings["icon_r"] if self.direction == "L2R" else app_settings["icon_l"],
                              font=("JetBrainsMono NFP", app_settings.get("icon_size", 22)))
        if self.direction == "L2R":
            self.arrow_btn.default_fg = app_settings.get("color_r", CP_CYAN)
            self.arrow_btn.configure(fg=self.arrow_btn.default_fg)
        else:
            self.arrow_btn.default_fg = app_settings.get("color_l", CP_ORANGE)
            self.arrow_btn.configure(fg=self.arrow_btn.default_fg)
        self.update_ui_state()

    def update_ui_state(self):
        self.side_a_ent.config(highlightbackground=CP_CYAN if self.direction == "L2R" else CP_RED)
        self.side_b_ent.config(highlightbackground=CP_RED if self.direction == "L2R" else CP_CYAN)

    def run_task(self):
        self.cfg["src"], self.cfg["dst"] = self.side_a_ent.get(), self.side_b_ent.get()
        self.cfg["last_dir"], self.cfg["last_op"] = self.direction, self.op_mode
        self.cfg["last_ignore"], self.cfg["last_flags"] = self.ignore_ent.get(), self.flags_ent.get()
        save_commands(commands)

        src, dst = (self.cfg["src"], self.cfg["dst"]) if self.direction == "L2R" else (self.cfg["dst"], self.cfg["src"])
        flags = self.cfg.get("last_flags", "")
        cmd = f'rclone {self.op_mode} "{src}" "{dst}" {flags}'
        
        if self.cfg["last_ignore"]:
            for item in self.cfg["last_ignore"].split(','):
                item = item.strip()
                if not item: continue
                check_path = item if os.path.isabs(item) else os.path.join(os.path.dirname(__file__), item)
                if os.path.isfile(check_path) and item.lower().endswith('.txt'):
                    try:
                        with open(check_path, "r", encoding="utf-8") as ef:
                            for line in ef:
                                line = line.strip()
                                if line: cmd += f' --exclude "{line}"'
                    except: pass
                else:
                    cmd += f' --exclude "{item}"'

        self.action_btn.config(state="disabled", text="BUSY...")
        # Show shortened command (hide long exclude lists)
        exclude_count = cmd.count('--exclude')
        if exclude_count > 3:
            short_cmd = cmd[:cmd.index('--exclude')] + f'[{exclude_count} exclusions]'
        else:
            short_cmd = cmd
        self.log_text.insert("end", f"// RUNNING: {short_cmd}\n", "yellow")
        self.log_text.tag_config("yellow", foreground=CP_YELLOW)

        def worker():
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
            
            self.log_text.mark_set("out", "end-1c")
            self.log_text.mark_gravity("out", "left")
            
            perm = []
            prog = []
            
            def refresh():
                self.log_text.delete("out", "end")
                for l in perm:
                    self.log_text.insert("end", l)
                for l in prog:
                    self.log_text.insert("end", l)
                self.log_text.see("end")
            
            for raw_line in iter(p.stdout.readline, ''):
                # Split by \r in case rclone uses it (take last segment only)
                line = raw_line.split('\r')[-1].strip()
                if not line: continue
                
                is_p = any(k in line for k in ["Transferred:", "Checks:", "Elapsed time:", "Transferring:", "Checking:", "  * ", "  *\t", " *\t", " * "])
                
                if is_p:
                    # Detect start of new progress block: byte-count line has "ETA"
                    if "Transferred:" in line and "ETA" in line and prog:
                        prog.clear()
                    prog.append(f" > {line}\n")
                    # Only refresh on block-ending line for less flicker
                    if "Elapsed time:" in line:
                        refresh()
                else:
                    perm.append(f" > {line}\n")
                    prog.clear()
                    refresh()
            
            p.wait()
            refresh()
            self.action_btn.config(state="normal", text="EXECUTE_CMD")
            trigger_all_checks()
        threading.Thread(target=worker, daemon=True).start()

def open_settings():
    win = tk.Toplevel(ROOT)
    container = setup_custom_window(win, "GLOBAL_SETTINGS", 480, 520)
    body = tk.Frame(container, bg=CP_BG); body.pack(fill="both", expand=True, padx=25, pady=20)

    def color_pick_field(label, icon_val, color_val):
        f = tk.Frame(body, bg=CP_BG); f.pack(fill="x", pady=8)
        tk.Label(f, text=label, bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 8, "bold")).pack(anchor="w")
        row = tk.Frame(f, bg=CP_BG); row.pack(fill="x", pady=2)
        
        # Icon char entry
        e_icon = CyberEntry(row, width=5); e_icon.insert(0, icon_val); e_icon.pack(side="left")
        
        # Color hex entry
        e_color = CyberEntry(row, width=12); e_color.insert(0, color_val); e_color.pack(side="left", padx=(10, 0))
        
        # Color Preview Square
        preview = tk.Frame(row, width=24, height=24, bg=color_val, bd=1, relief="solid", highlightthickness=1, highlightbackground=CP_DIM)
        preview.pack(side="left", padx=(10, 0))
        preview.pack_propagate(False)

        def pick_color():
            _, hex_c = colorchooser.askcolor(initialcolor=e_color.get(), title=f"Select {label}")
            if hex_c:
                e_color.delete(0, "end"); e_color.insert(0, hex_c.upper())
                preview.configure(bg=hex_c)

        # Eyedropper Button
        pick_btn = HoverButton(row, text="\uf1fb", font=("JetBrainsMono NFP", 10), width=3, command=pick_color, default_color=CP_PANEL)
        pick_btn.pack(side="left", padx=(5, 0))

        # Auto-update preview on typing
        def sync_preview(*args):
            val = e_color.get()
            if len(val) == 7 and val.startswith("#"):
                try: preview.configure(bg=val)
                except: pass
        e_color.bind("<KeyRelease>", sync_preview)

        return e_icon, e_color

    def s_field(label, val):
        f = tk.Frame(body, bg=CP_BG); f.pack(fill="x", pady=8)
        tk.Label(f, text=label, bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 8, "bold")).pack(anchor="w")
        e = CyberEntry(f); e.insert(0, val); e.pack(fill="x", pady=2)
        return e

    l_icon_e, l_color_e = color_pick_field("LEFT_CHANNEL (ICON | COLOR)", app_settings["icon_l"], app_settings.get("color_l", "#ff934b"))
    r_icon_e, r_color_e = color_pick_field("RIGHT_CHANNEL (ICON | COLOR)", app_settings["icon_r"], app_settings.get("color_r", "#00F0FF"))
    size_e = s_field("ICON_FONT_SIZE", app_settings.get("icon_size", 22))
    interval_e = s_field("CHECK_INTERVAL_SEC", app_settings["check_interval"])

    def save_stg():
        try:
            app_settings["icon_l"], app_settings["icon_r"] = l_icon_e.get(), r_icon_e.get()
            app_settings["color_l"], app_settings["color_r"] = l_color_e.get(), r_color_e.get()
            app_settings["icon_size"] = int(size_e.get())
            app_settings["check_interval"] = int(interval_e.get())
            save_settings(app_settings); win.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric value.")
    
    HoverButton(body, text="APPLY_CHANGES", command=save_stg, hover_color=CP_GREEN, pady=8).pack(fill="x", pady=20)

def edit_command(key):
    is_edit = key is not None
    cfg = commands.get(key, {"label": "NEW", "src": "C:/", "dst": "remote:/", "cmd": "rclone check src dst --size-only", "index": len(commands), "enabled": True})
    win = tk.Toplevel(ROOT); container = setup_custom_window(win, "REGISTRY_EDITOR", 500, 600)
    body = tk.Frame(container, bg=CP_BG); body.pack(fill="both", expand=True, padx=20, pady=10)

    def field(label, val):
        f = tk.Frame(body, bg=CP_BG); f.pack(fill="x", pady=8)
        tk.Label(f, text=label, bg=CP_BG, fg=CP_YELLOW, font=("Consolas", 8, "bold")).pack(anchor="w")
        e = CyberEntry(f); e.insert(0, str(val)); e.pack(fill="x", pady=2)
        return e

    name_e = field("ID_KEY", key if key else f"p_{len(commands)}")
    label_e = field("DISPLAY_LABEL", cfg["label"])
    src_e = field("PATH_A", cfg["src"])
    dst_e = field("PATH_B", cfg["dst"])
    cmd_e = field("VALIDATION_CMD", cfg["cmd"])
    idx_e = field("Z_INDEX", cfg.get("index", 0))

    def save():
        new_key = name_e.get()
        if is_edit and new_key != key: del commands[key]
        commands[new_key] = {"label": label_e.get(), "src": src_e.get(), "dst": dst_e.get(), "cmd": cmd_e.get(), "index": int(idx_e.get()), "enabled": True}
        save_commands(commands); create_gui(); win.destroy(); trigger_all_checks()

    btn_f = tk.Frame(body, bg=CP_BG); btn_f.pack(pady=20)
    HoverButton(btn_f, text="SAVE", command=save, width=12, hover_color=CP_GREEN).pack(side="left", padx=5)
    if is_edit: HoverButton(btn_f, text="DELETE", command=lambda: [commands.pop(key), save_commands(commands), create_gui(), win.destroy()], width=12, hover_color=CP_RED).pack(side="left", padx=5)
    HoverButton(btn_f, text="EXIT", command=win.destroy, width=12).pack(side="left", padx=5)

def check_and_update_label(label, cfg):
    def run():
        # Build command using the validation template and proper quoting
        src, dst = cfg["src"], cfg["dst"]
        cmd = cfg["cmd"].replace("src", f'"{src}"').replace("dst", f'"{dst}"')
        
        # Apply exclusions to background status check
        if cfg.get("last_ignore"):
            for item in cfg["last_ignore"].split(','):
                item = item.strip()
                if not item: continue
                # Resolve relative path for ignore files (relative to script dir)
                check_path = item if os.path.isabs(item) else os.path.join(os.path.dirname(__file__), item)
                if os.path.isfile(check_path) and item.lower().endswith('.txt'):
                    cmd += f' --exclude-from "{check_path}"'
                else:
                    cmd += f' --exclude "{item}"'
        
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
            label.config(fg=CP_GREEN if "0 differences found" in res.stdout and "ERROR" not in res.stdout else CP_RED)
        finally: mark_check_complete()
    label.trigger_check = lambda: threading.Thread(target=run, daemon=True).start()

def mark_check_complete():
    global pending_checks
    with check_lock:
        pending_checks -= 1
        if pending_checks <= 0: ROOT.after(app_settings.get("check_interval", 600) * 1000, trigger_all_checks)

def trigger_all_checks():
    global pending_checks
    widgets = [w for w in ROOT1.winfo_children() if hasattr(w, 'trigger_check')]
    with check_lock: pending_checks = len(widgets)
    if not widgets: ROOT.after(30000, trigger_all_checks); return
    for w in widgets: w.trigger_check()

ROOT = tk.Tk(); ROOT.overrideredirect(True); ROOT.configure(bg=CP_BG); ROOT.attributes("-topmost", True)
BORDER = tk.Frame(ROOT, bg=CP_DIM, bd=0, highlightthickness=1, highlightbackground=CP_RED); BORDER.place(relwidth=1, relheight=1)
MAIN = tk.Frame(BORDER, bg=CP_BG); MAIN.pack(pady=1, padx=2, expand=True, fill="both")
ROOT1 = tk.Frame(MAIN, bg=CP_PANEL); ROOT1.pack(side="left", pady=2, padx=5)

def create_gui():
    for w in ROOT1.winfo_children(): w.destroy()
    items = sorted(commands.items(), key=lambda x: (x[1].get("index", 0), x[0]))
    for key, cfg in items:
        if not cfg.get("enabled", True): continue
        lbl = tk.Label(ROOT1, bg=CP_PANEL, text=cfg["label"], font=("JetBrainsMono NFP", 16, "bold"), fg=CP_DIM, cursor="hand2")
        lbl.pack(side="left", padx=10); lbl.bind("<Button-1>", lambda e, c=cfg, k=key: ProjectActionWindow(ROOT, c, k))
        lbl.bind("<Button-3>", lambda e, k=key: edit_command(k)); check_and_update_label(lbl, cfg)
    tk.Frame(ROOT1, width=1, bg=CP_DIM).pack(side="left", padx=8, fill="y", pady=8)
    HoverButton(ROOT1, text="\uf067", command=lambda: edit_command(None), default_color=CP_PANEL, hover_color=CP_CYAN).pack(side="left", padx=2)
    HoverButton(ROOT1, text="\uf013", command=open_settings, default_color=CP_PANEL, hover_color=CP_YELLOW).pack(side="left", padx=2)
    HoverButton(ROOT1, text="\uf021", command=lambda: os.execv(sys.executable, ['python'] + sys.argv), default_color=CP_PANEL).pack(side="left", padx=2)
    HoverButton(ROOT1, text="\uf00d", command=lambda: sys.exit(0), hover_color=CP_RED, default_color=CP_PANEL).pack(side="left", padx=(2, 8))
    def adjust():
        ROOT.update_idletasks(); w = ROOT1.winfo_reqwidth() + 14 
        ROOT.geometry(f"{w}x{app_settings['height']}+{app_settings['x']}+{app_settings['y']}")
    ROOT.after(50, adjust)

def start_drag(e): ROOT.x, ROOT.y = e.x, e.y
def do_drag(e):
    x, y = (e.x - ROOT.x + ROOT.winfo_x(), e.y - ROOT.y + ROOT.winfo_y())
    ROOT.geometry(f"+{x}+{y}"); app_settings["x"], app_settings["y"] = x, y; save_settings(app_settings)

MAIN.bind("<Button-1>", start_drag); MAIN.bind("<B1-Motion>", do_drag)
create_gui(); trigger_all_checks(); ROOT.mainloop()
