import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
import json
import os
import subprocess
import threading
import time
from datetime import datetime
import psutil

# Configuration
CONFIG_FILE = "script_launcher_config.json"
DEFAULT_CONFIG = {
    "settings": {
        "columns": 5,
        "font_family": "JetBrainsMono NFP",
        "font_size": 10,
        "bg_color": "#1d2027",
        "border_color": "#fe1616",
        "accent_color": "#26b2f3",
        "success_color": "#00ff21",
        "danger_color": "#fe1616",
        "show_github": True,
        "show_rclone": True,
        "show_system_stats": True
    },
    "scripts": [
        {"name": "Explorer", "path": "explorer.exe"},
        {"name": "Task Mgr", "path": "taskmgr.exe"}
    ],
    "github_repos": [
        {"name": "ms1", "path": r"C:\Users\nahid\ms\ms1"},
        {"name": "db", "path": r"C:\Users\nahid\ms\db"},
        {"name": "test", "path": r"C:\Users\nahid\ms\test"}
    ],
    "rclone_folders": [
        {
            "name": "ms1",
            "src": "C:/Users/nahid/ms/ms1/",
            "dst": "o0:/ms1/",
            "label": "ms1",
            "cmd": 'rclone check src dst --fast-list --size-only --exclude ".git/**" --exclude "__pycache__/**"',
            "left_click_cmd": "rclone sync src dst -P --fast-list --exclude \".git/**\" --exclude \"__pycache__/**\"  --log-level INFO",
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        },
        {
            "name": "Photos",
            "src": "C:/Users/nahid/Pictures/",
            "dst": "o0:/Pictures/",
            "label": "\uf03e",
            "cmd": 'rclone check src dst --fast-list --size-only --exclude \".globalTrash/**\" --exclude \".stfolder/**\" --exclude \".stfolder (1)/**\"',
            "left_click_cmd": "rclone sync src dst -P --fast-list --track-renames --exclude \".globalTrash/**\" --exclude \".stfolder/**\" --log-level INFO",
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        },
        {
            "name": "msBackups",
            "label": "\udb85\ude32",
            "src": "C:/Users/nahid/ms/msBackups",
            "dst": "o0:/msBackups",
            "cmd": "rclone check src dst --fast-list --size-only"
        },
        {
            "name": "software",
            "label": "\uf40e",
            "src": "D:/software",
            "dst": "gu:/software",
            "cmd": "rclone check src dst --fast-list --size-only"
        },
        {
            "name": "song",
            "label": "\uec1b",
            "src": "D:/song",
            "dst": "gu:/song",
            "cmd": "rclone check src dst --fast-list --size-only"
        }
    ]
}

class ScriptLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Antigravity Script Manager")
        self.root.overrideredirect(True)
        self.root.configure(bg="#1d2027")
        self.root.attributes("-topmost", True)
        
        self.load_config()
        
        # UI state
        self.repo_labels = {}
        self.folder_labels = {}
        self.drag_data = {"x": 0, "y": 0}
        
        # Window sizing
        self.width = 950
        self.height = 650
        self.setup_window()
        
        self.setup_fonts()
        self.init_ui()
        
        # Start background threads
        self.stop_threads = False
        threading.Thread(target=self.status_monitor_thread, daemon=True).start()

    def setup_fonts(self):
        # Fallback fonts logic
        try:
            from tkinter import font
            available = font.families()
            preferred = ["JetBrainsMono NFP", "JetBrainsMono Nerd Font", "JetBrains Mono", "Consolas", "Courier New"]
            self.main_font = "Consolas"
            for f in preferred:
                if f in available:
                    self.main_font = f
                    break
            print(f"Using font: {self.main_font}")
        except:
            self.main_font = "Arial"

    def load_config(self):
        loaded_config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded_config = json.load(f)
            except:
                loaded_config = {}
        
        # Merge loaded config with defaults to ensure all keys exist
        self.config = DEFAULT_CONFIG.copy()
        
        # Helper to merge nested dicts
        def merge(target, source):
            for k, v in source.items():
                if k in target and isinstance(target[k], dict) and isinstance(v, dict):
                    merge(target[k], v)
                else:
                    target[k] = v
        
        merge(self.config, loaded_config)
        self.save_config()

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def setup_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def init_ui(self):
        # Premium Border
        self.border_frame = tk.Frame(
            self.root, 
            bg=self.config["settings"]["bg_color"],
            highlightthickness=2, 
            highlightbackground=self.config["settings"]["border_color"]
        )
        self.border_frame.pack(fill="both", expand=True)

        # Draggable Header
        self.header = tk.Frame(self.border_frame, bg="#1d2027", height=40)
        self.header.pack(fill="x")
        self.header.bind("<ButtonPress-1>", self.start_drag)
        self.header.bind("<B1-Motion>", self.do_drag)

        # Title
        self.title_lbl = tk.Label(
            self.header, 
            text=" SCRIPT MANAGER 🚀", 
            fg=self.config["settings"]["accent_color"], 
            bg="#1d2027",
            font=(self.main_font, 12, "bold")
        )
        self.title_lbl.pack(side="left", padx=15)
        self.title_lbl.bind("<ButtonPress-1>", self.start_drag)
        self.title_lbl.bind("<B1-Motion>", self.do_drag)

        # Control Buttons (Right aligned)
        self.close_btn = tk.Button(
            self.header, text="✕", command=self.root.destroy,
            bg="#1d2027", fg="#555555", bd=0, font=("Calibri", 14),
            activebackground="#fe1616", activeforeground="white",
            padx=10, cursor="hand2"
        )
        self.close_btn.pack(side="right")
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(fg="white", bg="#fe1616"))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(fg="#555555", bg="#1d2027"))

        # Main Content Area
        self.main_content = tk.Frame(self.border_frame, bg="#1d2027")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=5)

        # TOP SECTION: Status Widgets Container
        self.status_container = tk.Frame(self.main_content, bg="#1d2027")
        if self.config["settings"].get("show_github", True) or self.config["settings"].get("show_rclone", True):
            self.status_container.pack(fill="x", pady=(0, 15))

        # GitHub Widget
        self.github_widget = tk.LabelFrame(
            self.status_container, text=" GitHub Status ", 
            labelanchor="nw", fg="#888888", bg="#1d2027",
            font=(self.main_font, 8, "bold"), bd=1, relief="flat", highlightthickness=1, highlightbackground="#333333"
        )
        if self.config["settings"].get("show_github", True):
            self.github_widget.pack(side="left", fill="both", expand=True, padx=(0, 10))
            self.github_inner = tk.Frame(self.github_widget, bg="#1d2027")
            self.github_inner.pack(padx=10, pady=5)
            for repo in self.config["github_repos"]:
                r_frame = tk.Frame(self.github_inner, bg="#1d2027")
                r_frame.pack(side="left", padx=10)
                indicator = tk.Canvas(r_frame, width=10, height=10, bg="#1d2027", highlightthickness=0)
                indicator.pack(side="left", padx=(0, 5))
                circle = indicator.create_oval(2, 2, 8, 8, fill="#555555")
                lbl = tk.Label(r_frame, text=repo["name"], fg="white", bg="#1d2027", font=(self.main_font, 12, "bold"), cursor="hand2")
                lbl.pack(side="left")
                repo_path = repo["path"]
                lbl.bind("<Button-1>", lambda e, p=repo_path: self.on_git_click(e, p, "gitter"))
                lbl.bind("<Control-Button-1>", lambda e, p=repo_path: self.on_git_click(e, p, "explorer"))
                lbl.bind("<Button-3>", lambda e, p=repo_path: self.on_git_click(e, p, "lazygit"))
                lbl.bind("<Control-Button-3>", lambda e, p=repo_path: self.on_git_click(e, p, "restore"))
                self.repo_labels[repo["name"]] = {"lbl": lbl, "indicator": indicator, "circle": circle}

        # Rclone Widget
        self.rclone_widget = tk.LabelFrame(
            self.status_container, text=" Drive / Folder Status ", 
            labelanchor="nw", fg="#888888", bg="#1d2027",
            font=(self.main_font, 8, "bold"), bd=1, relief="flat", highlightthickness=1, highlightbackground="#333333"
        )
        if self.config["settings"].get("show_rclone", True):
            self.rclone_widget.pack(side="left", fill="both", expand=True)
            self.rclone_inner = tk.Frame(self.rclone_widget, bg="#1d2027")
            self.rclone_inner.pack(padx=10, pady=5)
            for folder in self.config["rclone_folders"]:
                f_frame = tk.Frame(self.rclone_inner, bg="#1d2027")
                f_frame.pack(side="left", padx=10)
                indicator = tk.Canvas(f_frame, width=10, height=10, bg="#1d2027", highlightthickness=0)
                indicator.pack(side="left", padx=(0, 5))
                circle = indicator.create_oval(2, 2, 8, 8, fill="#555555")
                lbl_text = folder.get("label", folder["name"])
                lbl = tk.Label(f_frame, text=lbl_text, fg="white", bg="#1d2027", font=(self.main_font, 12, "bold"), cursor="hand2")
                lbl.pack(side="left")
                lbl.bind("<Button-1>", lambda e, f=folder: self.on_rclone_click(e, f))
                lbl.bind("<Control-Button-1>", lambda e, f=folder: self.on_rclone_sync(e, f, "left"))
                lbl.bind("<Control-Button-3>", lambda e, f=folder: self.on_rclone_sync(e, f, "right"))
                self.folder_labels[folder["name"]] = {"lbl": lbl, "indicator": indicator, "circle": circle}
        
        # --- SECOND ROW: System Stats ---
        self.sys_stats_container = tk.Frame(self.main_content, bg="#1d2027")
        if self.config["settings"].get("show_system_stats", True):
            self.sys_stats_container.pack(fill="x", pady=(0, 10))
            # CPU Widget
            self.cpu_frame = self.create_stat_frame(self.sys_stats_container, " CPU ", 180)
            self.cpu_usage_lbl = tk.Label(self.cpu_frame, text="0%", fg="#14bcff", bg="#1d2027", font=(self.main_font, 10, "bold"))
            self.cpu_usage_lbl.pack(side="left", padx=5)
            self.cpu_bar = ctk.CTkProgressBar(self.cpu_frame, width=80, height=8, fg_color="#333333", progress_color="#14bcff")
            self.cpu_bar.pack(side="left", padx=5)
            self.cpu_bar.set(0)
            self.cores_frame = tk.Frame(self.cpu_frame, bg="#1d2027")
            self.cores_frame.pack(side="left", padx=5)
            self.core_canvases = []
            num_cores = psutil.cpu_count()
            for _ in range(num_cores):
                c = tk.Canvas(self.cores_frame, width=4, height=20, bg="#1d2027", highlightthickness=0)
                c.pack(side="left", padx=1)
                self.core_canvases.append(c)
            # RAM Widget
            self.ram_frame = self.create_stat_frame(self.sys_stats_container, " RAM ", 130)
            self.ram_usage_lbl = tk.Label(self.ram_frame, text="0%", fg="#ff934b", bg="#1d2027", font=(self.main_font, 10, "bold"))
            self.ram_usage_lbl.pack(side="left", padx=5)
            self.ram_bar = ctk.CTkProgressBar(self.ram_frame, width=70, height=8, fg_color="#333333", progress_color="#ff934b")
            self.ram_bar.pack(side="left", padx=5)
            self.ram_bar.set(0)
            # Disk Widgets
            self.disk_c_frame = self.create_stat_frame(self.sys_stats_container, " Disk C ", 110)
            self.disk_c_lbl = tk.Label(self.disk_c_frame, text="0%", fg="white", bg="#1d2027", font=(self.main_font, 9))
            self.disk_c_lbl.pack(side="left", padx=5)
            self.disk_c_bar = ctk.CTkProgressBar(self.disk_c_frame, width=50, height=8, fg_color="#333333", progress_color="#044568")
            self.disk_c_bar.pack(side="left", padx=5)
            self.disk_c_bar.set(0)
            self.disk_d_frame = self.create_stat_frame(self.sys_stats_container, " Disk D ", 110)
            self.disk_d_lbl = tk.Label(self.disk_d_frame, text="0%", fg="white", bg="#1d2027", font=(self.main_font, 9))
            self.disk_d_lbl.pack(side="left", padx=5)
            self.disk_d_bar = ctk.CTkProgressBar(self.disk_d_frame, width=50, height=8, fg_color="#333333", progress_color="#044568")
            self.disk_d_bar.pack(side="left", padx=5)
            self.disk_d_bar.set(0)
            # Network
            self.net_frame = self.create_stat_frame(self.sys_stats_container, " Net Speed ", 150)
            self.up_lbl = tk.Label(self.net_frame, text="▲ 0.0", fg="#00ff21", bg="#1d2027", font=(self.main_font, 9))
            self.up_lbl.pack(side="left", padx=5)
            self.down_lbl = tk.Label(self.net_frame, text="▼ 0.0", fg="#26b2f3", bg="#1d2027", font=(self.main_font, 9))
            self.down_lbl.pack(side="left", padx=5)
            self.last_net_sent = psutil.net_io_counters().bytes_sent
            self.last_net_recv = psutil.net_io_counters().bytes_recv

        self.init_ui_continued()

    def create_stat_frame(self, parent, title, min_width):
        frame = tk.LabelFrame(
            parent, text=title, 
            labelanchor="nw", fg="#666666", bg="#1d2027",
            font=(self.main_font, 7, "bold"), bd=1, relief="flat", highlightthickness=1, highlightbackground="#333333"
        )
        frame.pack(side="left", fill="both", expand=True, padx=2)
        inner = tk.Frame(frame, bg="#1d2027")
        inner.pack(padx=2, pady=2)
        return inner

    def init_ui_continued(self):
        # MIDDLE SECTION: Buttons Grid
        self.grid_scroll_container = tk.Frame(self.main_content, bg="#1d2027")
        self.grid_scroll_container.pack(fill="both", expand=True)
        
        self.grid_frame = tk.Frame(self.grid_scroll_container, bg="#1d2027")
        self.grid_frame.pack(fill="both", expand=True)

        self.refresh_grid()

        # BOTTOM SECTION: Controls
        self.footer = tk.Frame(self.border_frame, bg="#1d2027", height=50)
        self.footer.pack(fill="x", side="bottom", padx=20, pady=10)

        self.add_btn = ctk.CTkButton(
            self.footer, text="+ ADD SCRIPT", 
            width=140, height=35, corner_radius=5,
            fg_color="#10b153", hover_color="#0d8c42",
            font=(self.main_font, 10, "bold"),
            command=self.add_script_dialog
        )
        self.add_btn.pack(side="left")

        self.settings_btn = ctk.CTkButton(
            self.footer, text="⚙ SETTINGS", 
            width=120, height=35, corner_radius=5,
            fg_color="#3a3f4b", hover_color="#4e5563",
            font=(self.main_font, 10, "bold"),
            command=self.open_settings
        )
        self.settings_btn.pack(side="right")

    def refresh_grid(self):
        # Clear
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        cols = self.config["settings"]["columns"]
        scripts = self.config["scripts"]

        for i, script in enumerate(scripts):
            r = i // cols
            c = i % cols
            
            # Retrieve all style properties with defaults
            b_color = script.get("color", "#2b2f38")
            h_color = script.get("hover_color", self.config["settings"]["accent_color"])
            t_color = script.get("text_color", "white")
            ht_color = script.get("hover_text_color", "white")
            f_size = script.get("font_size", 10)
            
            btn = ctk.CTkButton(
                self.grid_frame, 
                text=script["name"],
                width=160, height=45, corner_radius=4,
                fg_color=b_color, 
                text_color=t_color,
                hover=False, # Disable CTk built-in hover to use manual bindings
                font=(self.main_font, f_size),
                command=lambda p=script["path"]: self.launch_script(p)
            )
            btn.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            
            # Manual hover implementation for better reliability
            def on_enter(e, b=btn, hc=h_color, htc=ht_color):
                b.configure(fg_color=hc, text_color=htc)
            
            def on_leave(e, b=btn, bc=b_color, tc=t_color):
                b.configure(fg_color=bc, text_color=tc)

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            # Context menu binding
            btn.bind("<Button-3>", lambda e, s=script: self.show_context_menu(e, s))

        # Equal weight for columns
        for i in range(cols):
            self.grid_frame.grid_columnconfigure(i, weight=1)

    def launch_script(self, path):
        try:
            # Handle expand vars like %USERPROFILE%
            path = os.path.expandvars(path)
            if path.endswith(".py"):
                subprocess.Popen(["python", path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(path, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch:\n{path}\n\n{e}")

    def show_context_menu(self, event, script):
        menu = tk.Menu(self.root, tearoff=0, bg="#2b2f38", fg="white", activebackground=self.config["settings"]["accent_color"])
        menu.add_command(label=f"Edit / Stylize", command=lambda: self.open_edit_dialog(script))
        menu.add_command(label="Duplicate", command=lambda: self.duplicate_script(script))
        menu.add_separator()
        menu.add_command(label=f"Delete", command=lambda: self.remove_script(script))
        menu.post(event.x_root, event.y_root)

    def duplicate_script(self, script):
        new_script = script.copy()
        new_script["name"] = f"{script['name']} (Copy)"
        self.config["scripts"].append(new_script)
        self.save_config()
        self.refresh_grid()

    def open_edit_dialog(self, script):
        self.root.attributes("-topmost", False)
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit {script['name']}")
        
        # Center the dialog on screen
        width, height = 400, 550
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        dialog.configure(bg="#1d2027")
        dialog.attributes("-topmost", True)
        dialog.transient(self.root)
        dialog.grab_set()

        def pick_color(key, btn):
            from tkinter import colorchooser
            curr = script.get(key, "#2b2f38")
            color = colorchooser.askcolor(initialcolor=curr, parent=dialog)
            if color[1]:
                script[key] = color[1]
                # Update preview button immediate appearance
                if key in ["color", "hover_color"]: 
                    btn.configure(fg_color=color[1], hover_color=color[1])
                elif key in ["text_color", "hover_text_color"]: 
                    btn.configure(text_color=color[1])

        # Form Layout
        tk.Label(dialog, text="BUTTON SETTINGS", fg=self.config["settings"]["accent_color"], bg="#1d2027", font=(self.main_font, 12, "bold")).pack(pady=15)
        
        # Name
        tk.Label(dialog, text="Label:", fg="gray", bg="#1d2027").pack(anchor="w", padx=30)
        name_var = tk.StringVar(value=script["name"])
        tk.Entry(dialog, textvariable=name_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0).pack(fill="x", padx=30, pady=5)

        # Path
        tk.Label(dialog, text="Path / Command:", fg="gray", bg="#1d2027").pack(anchor="w", padx=30, pady=(10, 0))
        path_frame = tk.Frame(dialog, bg="#1d2027")
        path_frame.pack(fill="x", padx=30)
        path_var = tk.StringVar(value=script["path"])
        tk.Entry(path_frame, textvariable=path_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0).pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="...", command=lambda: path_var.set(filedialog.askopenfilename() or path_var.get()), bg="#3a3f4b", fg="white").pack(side="right", padx=5)

        # Font Size
        tk.Label(dialog, text="Font Size:", fg="gray", bg="#1d2027").pack(anchor="w", padx=30, pady=(10, 0))
        fsize_var = tk.StringVar(value=str(script.get("font_size", 10)))
        tk.Entry(dialog, textvariable=fsize_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=10).pack(anchor="w", padx=30, pady=5)

        # Color Pickers with improved previews and centered layout
        colors_frame = tk.Frame(dialog, bg="#1d2027")
        colors_frame.pack(fill="x", padx=30, pady=20)
        colors_frame.grid_columnconfigure(0, weight=1)
        colors_frame.grid_columnconfigure(1, weight=1)

        # Row 1: Button BG & Text Color (Paired styles)
        cp1 = ctk.CTkButton(colors_frame, text="Button BG", fg_color=script.get("color", "#2b2f38"), hover=False, width=120, command=lambda: pick_color("color", cp1))
        cp1.grid(row=0, column=0, padx=5, pady=5)
        
        cp3 = ctk.CTkButton(colors_frame, text="Text Color", text_color=script.get("text_color", "white"), fg_color="#2b2f38", hover=False, width=120, command=lambda: pick_color("text_color", cp3))
        cp3.grid(row=0, column=1, padx=5, pady=5)

        # Row 2: Hover BG & Hover Text (Paired hover states)
        cp2 = ctk.CTkButton(colors_frame, text="Hover BG", fg_color=script.get("hover_color", "#26b2f3"), hover=False, width=120, command=lambda: pick_color("hover_color", cp2))
        cp2.grid(row=1, column=0, padx=5, pady=5)
        
        cp4 = ctk.CTkButton(colors_frame, text="Hover Text", text_color=script.get("hover_text_color", "white"), fg_color="#2b2f38", hover=False, width=120, command=lambda: pick_color("hover_text_color", cp4))
        cp4.grid(row=1, column=1, padx=5, pady=5)

        def save_changes():
            script["name"] = name_var.get()
            script["path"] = path_var.get()
            try:
                script["font_size"] = int(fsize_var.get())
            except:
                script["font_size"] = 10
            self.save_config()
            self.refresh_grid()
            dialog.destroy()
            self.root.attributes("-topmost", True)

        ctk.CTkButton(dialog, text="APPLY CHANGES", fg_color="#10b153", hover_color="#0d8c42", command=save_changes).pack(pady=20)
        
        def on_close():
            dialog.destroy()
            self.root.attributes("-topmost", True)
        dialog.protocol("WM_DELETE_WINDOW", on_close)

    def remove_script(self, script):
        self.root.attributes("-topmost", False)
        if messagebox.askyesno("Confirm", f"Remove script '{script['name']}'?", parent=self.root):
            self.config["scripts"].remove(script)
            self.save_config()
            self.refresh_grid()
        self.root.attributes("-topmost", True)

    def add_script_dialog(self):
        self.root.attributes("-topmost", False)
        name = simpledialog.askstring("Add Script", "Enter button label:", parent=self.root)
        if name:
            path = filedialog.askopenfilename(title="Select Script or Executable", parent=self.root)
            if path:
                self.config["scripts"].append({"name": name, "path": path})
                self.save_config()
                self.refresh_grid()
        self.root.attributes("-topmost", True)

    def open_settings(self):
        self.root.attributes("-topmost", False)
        dialog = tk.Toplevel(self.root)
        dialog.attributes("-topmost", True)
        dialog.title("Settings")
        
        # Center the settings dialog
        width, height = 300, 350
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        dialog.configure(bg="#1d2027")
        dialog.transient(self.root)
        dialog.grab_set()

        # Grid settings
        tk.Label(dialog, text="Grid Settings:", fg=self.config["settings"]["accent_color"], bg="#1d2027", font=(self.main_font, 10, "bold")).pack(pady=(10, 5))
        tk.Label(dialog, text="Buttons per Row:", fg="white", bg="#1d2027", font=(self.main_font, 9)).pack()
        val_var = tk.StringVar(value=str(self.config["settings"]["columns"]))
        tk.Entry(dialog, textvariable=val_var, width=10, justify="center").pack(pady=5)

        # Widget Toggles
        tk.Label(dialog, text="Toggle Widgets:", fg=self.config["settings"]["accent_color"], bg="#1d2027", font=(self.main_font, 10, "bold")).pack(pady=(15, 5))
        
        v_github = tk.BooleanVar(value=self.config["settings"].get("show_github", True))
        cb_github = tk.Checkbutton(dialog, text="GitHub Status", variable=v_github, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
        cb_github.pack(anchor="w", padx=50)

        v_rclone = tk.BooleanVar(value=self.config["settings"].get("show_rclone", True))
        cb_rclone = tk.Checkbutton(dialog, text="Rclone Status", variable=v_rclone, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
        cb_rclone.pack(anchor="w", padx=50)

        v_stats = tk.BooleanVar(value=self.config["settings"].get("show_system_stats", True))
        cb_stats = tk.Checkbutton(dialog, text="System Stats", variable=v_stats, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
        cb_stats.pack(anchor="w", padx=50)

        def save():
            try:
                n = int(val_var.get())
                if 1 <= n <= 10:
                    self.config["settings"]["columns"] = n
                    self.config["settings"]["show_github"] = v_github.get()
                    self.config["settings"]["show_rclone"] = v_rclone.get()
                    self.config["settings"]["show_system_stats"] = v_stats.get()
                    self.save_config()
                    
                    # Apply grid changes immediately (safe)
                    self.refresh_grid()
                    
                    messagebox.showinfo("Success", "Settings saved!\nWidget visibility changes will take effect on the next start.", parent=dialog)
                    
                    dialog.destroy()
                    self.root.attributes("-topmost", True)
                else:
                    messagebox.showwarning("Invalid", "Please enter a number between 1 and 10", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {e}", parent=dialog)

        def on_close():
            dialog.destroy()
            self.root.attributes("-topmost", True)

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        ctk.CTkButton(dialog, text="SAVE", command=save, width=100, fg_color="#10b153").pack(pady=20)

    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_data["x"])
        y = self.root.winfo_y() + (event.y - self.drag_data["y"])
        self.root.geometry(f"+{x}+{y}")

    # --- Rclone Action Handlers ---
    def on_rclone_click(self, event, cfg):
        # Open log (mimicking 'edit' command in new shell)
        log_path = os.path.join(r"C:\Users\nahid\script_output\rclone", f"{cfg['name']}_check.log")
        if os.path.exists(log_path):
            try:
                subprocess.Popen(["powershell", "-NoExit", "-Command", f'edit "{log_path}"'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            except:
                os.startfile(log_path) # Fallback

    def on_rclone_sync(self, event, cfg, side):
        cmd_key = "left_click_cmd" if side == "left" else "right_click_cmd"
        default_cmd = "rclone sync src dst -P --fast-list" if side == "left" else "rclone sync dst src -P --fast-list"
        raw_cmd = cfg.get(cmd_key, default_cmd)
        
        actual_cmd = raw_cmd.replace("src", cfg["src"]).replace("dst", cfg["dst"])
        try:
            subprocess.Popen(f'start pwsh -NoExit -Command "{actual_cmd}"', shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run sync:\n{e}")

    # --- Git Action Handlers ---
    def on_git_click(self, event, path, action):
        try:
            if action == "gitter":
                cmd = f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; cd {path.replace(os.sep, '/')} ; gitter}}"
                subprocess.Popen(["Start", "pwsh", "-NoExit", "-Command", cmd], shell=True)
            elif action == "explorer":
                subprocess.Popen(f'explorer "{path}"', shell=True)
            elif action == "lazygit":
                subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=path, shell=True)
            elif action == "restore":
                cmd = f"& {{$host.UI.RawUI.WindowTitle='Git Restore' ; cd {path.replace(os.sep, '/')} ; git restore . }}"
                subprocess.Popen(["Start", "pwsh", "-NoExit", "-Command", cmd], shell=True)
        except Exception as e:
            print(f"Git action error: {e}")

    def status_monitor_thread(self):
        log_dir = r"C:\Users\nahid\script_output\rclone"
        os.makedirs(log_dir, exist_ok=True)

        # Separate threads for different update rates
        threading.Thread(target=self.github_monitor_loop, daemon=True).start()
        threading.Thread(target=self.rclone_monitor_loop, args=(log_dir,), daemon=True).start()
        threading.Thread(target=self.system_stats_loop, daemon=True).start()

    def system_stats_loop(self):
        while not self.stop_threads:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                disk_c = psutil.disk_usage('C:').percent
                disk_d = psutil.disk_usage('D:').percent if os.path.exists('D:') else 0
                
                # Network
                net_io = psutil.net_io_counters()
                up = (net_io.bytes_sent - self.last_net_sent) / (1024 * 1024)
                down = (net_io.bytes_recv - self.last_net_recv) / (1024 * 1024)
                self.last_net_sent = net_io.bytes_sent
                self.last_net_recv = net_io.bytes_recv
                
                # Cores
                cores = psutil.cpu_percent(percpu=True)
                
                self.root.after(0, lambda: self.update_sys_ui(cpu, ram, disk_c, disk_d, up, down, cores))
            except:
                pass
            time.sleep(1)

    def update_sys_ui(self, cpu, ram, disk_c, disk_d, up, down, cores):
        # Update Labels
        self.cpu_usage_lbl.config(text=f"{int(cpu)}%", fg=self.get_stat_color(cpu))
        self.cpu_bar.set(cpu / 100)
        
        self.ram_usage_lbl.config(text=f"{int(ram)}%", fg=self.get_stat_color(ram))
        self.ram_bar.set(ram / 100)
        
        self.disk_c_lbl.config(text=f"{int(disk_c)}%")
        self.disk_c_bar.set(disk_c / 100)
        
        self.disk_d_lbl.config(text=f"{int(disk_d)}%")
        self.disk_d_bar.set(disk_d / 100)
        
        self.up_lbl.config(text=f"▲ {up:.1f}")
        self.down_lbl.config(text=f"▼ {down:.1f}")
        
        # Update Core Micro Bars
        for i, usage in enumerate(cores):
            if i < len(self.core_canvases):
                canv = self.core_canvases[i]
                canv.delete("all")
                h = (usage / 100) * 20
                color = self.get_stat_color(usage)
                # Draw from bottom
                canv.create_rectangle(0, 20-h, 4, 20, fill=color, outline="")

    def get_stat_color(self, val):
        if val > 90: return "#fe1616"  # Red
        if val > 70: return "#ff934b"  # Orange
        return "#14bcff" # Blue/Cyan

    def github_monitor_loop(self):
        while not self.stop_threads:
            for repo in self.config["github_repos"]:
                path = repo["path"]
                status = "unknown"
                if os.path.exists(path):
                    try:
                        if os.path.isdir(os.path.join(path, ".git")):
                            res = subprocess.run(["git", "status", "--porcelain"], cwd=path, capture_output=True, text=True, timeout=2)
                            status = "clean" if not res.stdout.strip() else "dirty"
                        else: status = "no_git"
                    except: status = "error"
                else: status = "missing"
                self.root.after(0, lambda name=repo["name"], s=status: self.update_repo_status_ui(name, s))
            time.sleep(1) # GitHub updates every 1 second

    def rclone_monitor_loop(self, log_dir):
        while not self.stop_threads:
            for folder in self.config["rclone_folders"]:
                name = folder["name"]
                cfg_cmd = folder.get("cmd", "rclone check src dst --fast-list --size-only")
                actual_cmd = cfg_cmd.replace("src", folder["src"]).replace("dst", folder["dst"])
                log_file = os.path.join(log_dir, f"{name}_check.log")
                
                try:
                    with open(log_file, "w") as f:
                        subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f, timeout=30)
                    
                    with open(log_file, "r") as f:
                        content = f.read()
                    
                    is_ok = "ERROR" not in content and "differences found" not in content.lower()
                    self.root.after(0, lambda n=name, ok=is_ok: self.update_folder_status_ui(n, ok))
                except Exception as e:
                    self.root.after(0, lambda n=name: self.update_folder_status_ui(n, False))
            
            time.sleep(600) # Rclone updates every 10 minutes

    def update_repo_status_ui(self, name, status):
        if name in self.repo_labels:
            ui = self.repo_labels[name]
            color = "#555555"
            if status == "clean": color = self.config["settings"]["success_color"]
            elif status == "dirty": color = self.config["settings"]["danger_color"]
            elif status in ["error", "missing", "no_git"]: color = self.config["settings"]["danger_color"]
            
            ui["indicator"].itemconfig(ui["circle"], fill=color)

    def update_folder_status_ui(self, name, exists):
        if name in self.folder_labels:
            ui = self.folder_labels[name]
            color = self.config["settings"]["success_color"] if exists else self.config["settings"]["danger_color"]
            ui["indicator"].itemconfig(ui["circle"], fill=color)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = tk.Tk()
    app = ScriptLauncherApp(root)
    root.mainloop()
