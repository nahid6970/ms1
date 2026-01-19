import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
import shutil
import json
import os
import subprocess
import threading
import time
from datetime import datetime
import psutil

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_launcher_config.json")
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
        "show_system_stats": True,
        "always_on_top": True
    },
    "scripts": [
        {"name": "Explorer", "path": "explorer.exe"},
        {"name": "Task Mgr", "path": "taskmgr.exe"}
    ],
    "github_repos": [
        {"name": "ms1", "path": r"C:\@delta\ms1"},
        {"name": "db", "path": r"C:\Users\nahid\ms\db"},
        {"name": "test", "path": r"C:\Users\nahid\ms\test"}
    ],
    "rclone_folders": [
        {
            "name": "ms1",
            "src": "C:/@delta/ms1/",
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
        self.root.title("Script Manager")
        # Re-enable window frame for taskbar visibility
        # self.root.overrideredirect(True)
        self.root.configure(bg="#1d2027")
        self.root.attributes("-topmost", True)
        
        # Set window icon from SVG
        self.set_window_icon()
        
        self.load_config()
        
        # UI state
        self.repo_labels = {}
        self.folder_labels = {}
        self.drag_data = {"x": 0, "y": 0}
        self.script_drag_data = {"index": None, "active": False, "ghost": None, "start_abs": (0, 0), "block_click": False}
        self.script_drag_data = {"index": None, "active": False, "ghost": None, "start_abs": (0, 0), "block_click": False}
        self.view_stack = [] # Stack of (folder_name, script_list_reference)
        self.clipboard_script = None # For Cut/Paste
        
        # Window sizing
        self.width = 950
        self.height = 650
        self.setup_window()
        
        self.setup_fonts()
        self.init_ui()
        
        # Start background threads
        self.stop_threads = False
        threading.Thread(target=self.status_monitor_thread, daemon=True).start()

    def set_window_icon(self):
        """Create and set window icon from SVG code"""
        try:
            from PIL import Image, ImageDraw, ImageTk
            import io
            
            # SVG rocket icon code
            svg_code = '''
            <svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="grad1" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style="stop-color:#26b2f3;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#0d8c42;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <!-- Rocket body -->
                <ellipse cx="32" cy="40" rx="12" ry="20" fill="url(#grad1)"/>
                <!-- Rocket nose -->
                <path d="M 32 10 L 20 25 L 44 25 Z" fill="#fe1616"/>
                <!-- Window -->
                <circle cx="32" cy="35" r="5" fill="#1d2027"/>
                <circle cx="32" cy="35" r="3" fill="#26b2f3" opacity="0.7"/>
                <!-- Left fin -->
                <path d="M 20 45 L 15 55 L 20 50 Z" fill="#fe1616"/>
                <!-- Right fin -->
                <path d="M 44 45 L 49 55 L 44 50 Z" fill="#fe1616"/>
                <!-- Flame -->
                <ellipse cx="32" cy="62" rx="8" ry="6" fill="#ff934b" opacity="0.8"/>
                <ellipse cx="32" cy="60" rx="6" ry="4" fill="#ffd700" opacity="0.9"/>
            </svg>
            '''
            
            # Try to render SVG using cairosvg if available
            try:
                import cairosvg
                png_data = cairosvg.svg2png(bytestring=svg_code.encode('utf-8'), output_width=64, output_height=64)
                image = Image.open(io.BytesIO(png_data))
            except ImportError:
                # Fallback: Create a simple icon using PIL
                image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(image)
                
                # Draw rocket body (ellipse)
                draw.ellipse([20, 20, 44, 60], fill='#26b2f3', outline='#0d8c42', width=2)
                
                # Draw rocket nose (triangle approximation)
                draw.polygon([32, 10, 20, 25, 44, 25], fill='#fe1616')
                
                # Draw window
                draw.ellipse([27, 30, 37, 40], fill='#1d2027')
                draw.ellipse([29, 32, 35, 38], fill='#26b2f3')
                
                # Draw fins
                draw.polygon([20, 45, 15, 55, 20, 50], fill='#fe1616')
                draw.polygon([44, 45, 49, 55, 44, 50], fill='#fe1616')
                
                # Draw flame
                draw.ellipse([24, 56, 40, 64], fill='#ff934b')
                draw.ellipse([26, 56, 38, 62], fill='#ffd700')
            
            # Convert to PhotoImage and set as icon
            photo = ImageTk.PhotoImage(image)
            self.root.iconphoto(True, photo)
            
            # Keep a reference to prevent garbage collection
            self.icon_photo = photo
            
        except Exception as e:
            print(f"Could not set window icon: {e}")
            # Continue without icon

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
        
        # Apply startup settings
        self.root.attributes("-topmost", self.config["settings"].get("always_on_top", True))

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

        # Title & Breadcrumb
        self.title_frame = tk.Frame(self.header, bg="#1d2027")
        self.title_frame.pack(side="left", padx=15)
        
        self.back_btn = tk.Button(
            self.title_frame, text=" ❮ ", command=self.exit_folder,
            bg="#1d2027", fg="#fe1616", bd=0, font=("Segoe UI Symbol", 10, "bold"),
            activebackground="#fe1616", activeforeground="white", cursor="hand2"
        )
        # Not packed initially
        
        self.title_lbl = tk.Label(
            self.title_frame, 
            text=" SCRIPT MANAGER 🚀", 
            fg=self.config["settings"]["accent_color"], 
            bg="#1d2027",
            font=(self.main_font, 12, "bold")
        )
        self.title_lbl.pack(side="left")
        
        for widget in [self.header, self.title_lbl, self.title_frame]:
            widget.bind("<ButtonPress-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.do_drag)

        # Control Buttons Container (Right aligned)
        self.controls_container = tk.Frame(self.header, bg="#1d2027")
        self.controls_container.pack(side="right")

        self.close_btn = tk.Button(
            self.controls_container, text="✕", command=self.root.destroy,
            bg="#1d2027", fg="#555555", bd=0, font=("Calibri", 12),
            activebackground="#fe1616", activeforeground="white",
            padx=10, cursor="hand2"
        )
        self.close_btn.pack(side="right")
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(fg="white", bg="#fe1616"))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(fg="#555555", bg="#1d2027"))

        self.settings_btn = tk.Button(
            self.controls_container, text="⚙", command=self.open_settings,
            bg="#1d2027", fg="#888888", bd=0, font=("Segoe UI Symbol", 12),
            activeforeground="white", activebackground="#3a3f4b",
            padx=10, cursor="hand2"
        )
        self.settings_btn.pack(side="right")
        self.settings_btn.bind("<Enter>", lambda e: self.settings_btn.config(fg="white", bg="#3a3f4b"))
        self.settings_btn.bind("<Leave>", lambda e: self.settings_btn.config(fg="#888888", bg="#1d2027"))

        self.add_btn = tk.Button(
            self.controls_container, text="+", command=self.add_script_dialog,
            bg="#1d2027", fg="#888888", bd=0, font=("Segoe UI Symbol", 12, "bold"),
            activeforeground="white", activebackground="#10b153",
            padx=10, cursor="hand2"
        )
        self.add_btn.pack(side="right")
        self.add_btn.bind("<Enter>", lambda e: self.add_btn.config(fg="white", bg="#10b153"))
        self.add_btn.bind("<Leave>", lambda e: self.add_btn.config(fg="#888888", bg="#1d2027"))

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
        # MIDDLE SECTION: Buttons Grid (Scrollable)
        self.grid_scroll_container = tk.Frame(self.main_content, bg="#1d2027")
        self.grid_scroll_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.grid_scroll_container, bg="#1d2027", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.grid_scroll_container, orientation="vertical", command=self.canvas.yview)
        
        self.grid_frame = tk.Frame(self.canvas, bg="#1d2027")
        
        self.grid_frame.bind("<Configure>", self._on_frame_configure)
        
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw", tags="grid_frame_win")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        # self.scrollbar.pack(side="right", fill="y") # Hidden per request
        
        # Ensure frame fills canvas width
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig("grid_frame_win", width=e.width))

        self.refresh_grid()
        
        # Bind scrolling on Enter AND Motion to ensure it catches initial state
        self.grid_scroll_container.bind("<Enter>", self._bound_to_mousewheel)
        self.grid_scroll_container.bind("<Motion>", self._bound_to_mousewheel)
        self.grid_scroll_container.bind("<Leave>", self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        # Bind unconditionally, the check happens in _on_mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if self.canvas.winfo_height() < self.grid_frame.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def refresh_grid(self):
        # Clear
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Determine current context and settings
        if self.view_stack:
            current_folder = self.view_stack[-1]
            folder_name = current_folder["name"]
            scripts = current_folder["scripts"]
            
            # Folder-specific columns rule
            c = current_folder.get("grid_columns", 0)
            cols = c if c > 0 else self.config["settings"]["columns"]
            
            # Folder-specific child dimensions
            def_w = current_folder.get("child_width", 0)
            def_h = current_folder.get("child_height", 0)
            
            self.title_lbl.config(text=f" ❯ {folder_name.upper()}")
            self.back_btn.pack(side="left", padx=(0, 5))
        else:
            scripts = self.config["scripts"]
            cols = self.config["settings"]["columns"]
            def_w, def_h = 0, 0
            
            self.title_lbl.config(text=" SCRIPT MANAGER 🚀")
            self.back_btn.pack_forget()

        # Initialize grid map for span logic
        self.grid_occupied = set() # Stores (row, col) tuples

        for i, script in enumerate(scripts):
            is_folder = script.get("type") == "folder"
            
            # Retrieve all style properties with defaults
            default_bg = "#2b2f38" if not is_folder else "#1a1c23"
            b_color = script.get("color", default_bg)
            h_color = script.get("hover_color", self.config["settings"]["accent_color"])
            t_color = script.get("text_color", "white" if not is_folder else "#ffd700")
            ht_color = script.get("hover_text_color", "white")
            f_size = script.get("font_size", self.config["settings"].get("font_size", 10))
            
            # Border settings
            b_width = script.get("border_width", 0)
            b_border_color = script.get("border_color", "#fe1616")

            display_text = script["name"]
            
            corner_radius = script.get("corner_radius", 4)
            
            # Font styling
            is_bold = script.get("is_bold", False) or is_folder
            is_italic = script.get("is_italic", False)
            
            # Get font family - use script-specific, fallback to global, then main_font
            font_family = script.get("font_family", self.config["settings"].get("font_family", self.main_font))
            
            font_spec = ctk.CTkFont(
                family=font_family,
                size=f_size,
                weight="bold" if is_bold else "normal",
                slant="italic" if is_italic else "roman"
            )

            # Determine grid position with spanning logic
            c_span = script.get("col_span", 1)
            r_span = script.get("row_span", 1)
            
            # Find first available spot
            place_r, place_c = 0, 0
            found = False
            
            # Search limit to avoid infinite loops
            for search_r in range(100): 
                for search_c in range(cols):
                    # Check if this cell is free
                    if (search_r, search_c) in self.grid_occupied:
                        continue
                        
                    # Check if the entire span fits
                    fits = True
                    for sr in range(r_span):
                        for sc in range(c_span):
                            # Boundary check (columns only, rows extend infinitely)
                            if search_c + sc >= cols:
                                fits = False
                                break
                            # Occupancy check
                            if (search_r + sr, search_c + sc) in self.grid_occupied:
                                fits = False
                                break
                        if not fits: break
                    
                    if fits:
                        place_r, place_c = search_r, search_c
                        found = True
                        break
                if found: break
            
            # Mark occupied
            for sr in range(r_span):
                for sc in range(c_span):
                    self.grid_occupied.add((place_r + sr, place_c + sc))

            # Determine dimensions
            custom_w = script.get("width", 0)
            custom_h = script.get("height", 0)
            
            # Use folder-level child defaults if custom dimensions not set
            if custom_w == 0 and def_w > 0:
                final_w = def_w
            else:
                final_w = custom_w if custom_w > 0 else (160 * c_span + (16 * (c_span - 1)))
            
            if custom_h == 0 and def_h > 0:
                final_h = def_h
            else:
                final_h = custom_h if custom_h > 0 else (45 * r_span + (16 * (r_span - 1)))

            btn = ctk.CTkButton(
                self.grid_frame, 
                text=display_text,
                width=final_w,
                height=final_h,
                corner_radius=corner_radius,
                fg_color=b_color, 
                text_color=t_color,
                hover=False, 
                font=font_spec,
                border_width=b_width,
                border_color=b_border_color
            )
            btn.grid(row=place_r, column=place_c, rowspan=r_span, columnspan=c_span, padx=8, pady=8, sticky="new")
            
            # Manual hover implementation for better reliability
            def on_enter(e, b=btn, hc=h_color, htc=ht_color):
                b.configure(fg_color=hc, text_color=htc)
            
            def on_leave(e, b=btn, bc=b_color, tc=t_color):
                b.configure(fg_color=bc, text_color=tc)

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            # Context menu binding
            btn.bind("<Button-3>", lambda e, s=script: self.show_context_menu(e, s))
            
            # Ctrl+Right Click binding
            btn.bind("<Control-Button-3>", lambda e, s=script: self.handle_ctrl_right_click(e, s))

            # Drag & Drop bindings for sorting
            btn.bind("<ButtonPress-1>", lambda e, i=i, s=script: self.start_script_drag(e, i, s), add="+")
            btn.bind("<B1-Motion>", self.do_script_drag, add="+")
            btn.bind("<ButtonRelease-1>", self.stop_script_drag, add="+")

        # Equal weight for columns
        for i in range(cols):
            self.grid_frame.grid_columnconfigure(i, weight=1)

        # Ensure consistent row heights
        if self.grid_occupied:
            max_r = max(r for r, c in self.grid_occupied)
            for r in range(max_r + 2): # +2 to cover current and maybe next empty row
                self.grid_frame.grid_rowconfigure(r, minsize=61)

    def handle_script_click(self, script):
        if script.get("type") == "folder":
            self.enter_folder(script)
        else:
            self.launch_script(script)

    def enter_folder(self, folder):
        if "scripts" not in folder:
            folder["scripts"] = []
        self.view_stack.append(folder)
        self.refresh_grid()

    def exit_folder(self):
        if self.view_stack:
            self.view_stack.pop()
            self.refresh_grid()

    # --- Drag & Drop Sorting Logic ---
    def start_script_drag(self, event, index, script):
        self.script_drag_data["index"] = index
        self.script_drag_data["active"] = False
        self.script_drag_data["script"] = script
        self.script_drag_data["start_abs"] = (event.x_root, event.y_root)

    def do_script_drag(self, event):
        dx = abs(event.x_root - self.script_drag_data["start_abs"][0])
        dy = abs(event.y_root - self.script_drag_data["start_abs"][1])
        
        if not self.script_drag_data["active"] and (dx > 10 or dy > 10):
            self.script_drag_data["active"] = True
            # Create a ghost label for visual feedback
            scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
            script = scripts[self.script_drag_data["index"]]
            self.script_drag_data["ghost"] = tk.Label(
                self.root, text=script["name"], 
                bg=self.config["settings"]["accent_color"], fg="white",
                font=(self.main_font, 10, "bold"), padx=10, pady=5,
                relief="flat", highlightthickness=1, highlightbackground="white"
            )
            self.script_drag_data["ghost"].place(x=event.x_root - self.root.winfo_rootx(), y=event.y_root - self.root.winfo_rooty())
            self.root.config(cursor="fleur")

        if self.script_drag_data["active"] and self.script_drag_data["ghost"]:
            self.script_drag_data["ghost"].place(x=event.x_root - self.root.winfo_rootx() + 10, y=event.y_root - self.root.winfo_rooty() + 10)

    def stop_script_drag(self, event):
        self.root.config(cursor="")
        if self.script_drag_data["ghost"]:
            self.script_drag_data["ghost"].destroy()
            self.script_drag_data["ghost"] = None

        was_dragging = self.script_drag_data["active"]
        self.script_drag_data["active"] = False
        
        if not was_dragging:
            # IT WAS A CLICK
            script = self.script_drag_data.get("script")
            if script:
                # Check for Ctrl+Left Click (State 4 is Ctrl)
                if event.state & 0x0004 and script.get("ctrl_left_cmd"):
                     # We can reuse launch_script by passing a temporary object or just the command
                     # Let's create a temp script object to reuse logic
                     temp_script = script.copy()
                     temp_script["path"] = script["ctrl_left_cmd"]
                     # You might want to force hide or inherit? Let's inherit normal hide settings or assume normal
                     self.launch_script(temp_script)
                else:
                    self.handle_script_click(script)
            return 
        
        # Find widget at drop position
        target_widget = self.grid_frame.winfo_containing(event.x_root, event.y_root)
        if not target_widget:
            return

        # Figure out target index using coordinate-based hit testing
        # This is more robust than widget hierarchy for composite controls like CTkButton
        target_idx = None
        buttons = self.grid_frame.winfo_children()
        
        for i, btn in enumerate(buttons):
            # Check if event coords are inside this button's bounding box
            bx = btn.winfo_rootx()
            by = btn.winfo_rooty()
            bw = btn.winfo_width()
            bh = btn.winfo_height()
            
            if bx <= event.x_root <= (bx + bw) and by <= event.y_root <= (by + bh):
                target_idx = i
                break
        
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        if target_idx is not None and target_idx != self.script_drag_data["index"]:
            target_script = scripts[target_idx]
            
            # Feature: Drag ONTO a folder -> Move Into
            if target_script.get("type") == "folder":
                # Check if we dropped essentially "on" it? 
                # For now, let's assume if you drop on a folder, you mean to move in.
                # To distinguish reorder vs move-in, usually UI highlights. 
                # Simplification: If target is folder, move in. Reordering folders requires dragging to non-folder or specific edge?
                # Let's say: If target is folder, we move IN. (User request)
                # But wait, how to reorder folders then? 
                # Let's check dx/dy to see if we are 'centered' on it? No, winfo_containing is precise.
                # Let's just implement explicit Move In.
                
                # Check for recursion (can't move folder into itself)
                if script == target_script:
                    return # Can't happen due to index check usually, but safely ignore
                
                if messagebox.askyesno("Move Item", f"Move '{script['name']}' into '{target_script['name']}'?", parent=self.root):
                    item = scripts.pop(self.script_drag_data["index"])
                    if "scripts" not in target_script:
                        target_script["scripts"] = []
                    target_script["scripts"].append(item)
                    self.save_config()
                    self.refresh_grid()
                    return

            # Normal Reorder
            item = scripts.pop(self.script_drag_data["index"])
            scripts.insert(target_idx, item)
            self.save_config()
            self.refresh_grid()

    def launch_script(self, script_obj):
        hide = script_obj.get("hide_terminal", False)
        keep_open = script_obj.get("keep_open", False)
        
        # Check if using inline script
        if script_obj.get("use_inline", False) and script_obj.get("inline_script"):
            self.launch_inline_script(script_obj)
            return
        
        path = script_obj["path"]
        
        # Determine creation flags
        # CREATE_NEW_CONSOLE (0x10) vs CREATE_NO_WINDOW (0x08000000)
        cflags = subprocess.CREATE_NEW_CONSOLE
        if hide:
            cflags = 0x08000000 # CREATE_NO_WINDOW
            
        try:
            # Handle expand vars like %USERPROFILE%
            path = os.path.expandvars(path)
            script_dir = os.path.dirname(path) if os.path.isfile(path) else None
            
            # Check if it is a file we should handle intelligently
            if os.path.isfile(path):
                if path.endswith(".py"):
                    python_exe = "pythonw" if hide else "python"
                    if not hide and keep_open:
                         # Use quote-safe approach
                         subprocess.Popen(f'start "" cmd /k {python_exe} "{path}"', shell=True, cwd=script_dir, creationflags=cflags)
                    else:
                        subprocess.Popen([python_exe, path], cwd=script_dir, creationflags=cflags)
                elif path.lower().endswith(".ps1"):
                    # PowerShell execution
                    ps_bin = "pwsh" if shutil.which("pwsh") else "powershell"
                    
                    if hide:
                        # Hidden: Use direct Popen list (no window)
                        ps_args = [ps_bin, "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-NoProfile", "-File", path]
                        subprocess.Popen(ps_args, cwd=script_dir, creationflags=cflags)
                    else:
                        # Visible: Use 'start' to ensure correct window environment
                        no_exit = "-NoExit" if keep_open else ""
                        # Use -Command "& 'path'" syntax which is often more robust for interactive scripts
                        cmd_str = f'start "" "{ps_bin}" {no_exit} -ExecutionPolicy Bypass -Command "& \\"{path}\\""'
                        subprocess.Popen(cmd_str, shell=True, cwd=script_dir, creationflags=cflags)
                else:
                    # Use shell start for .exe, .bat, or generic files
                    if not hide and keep_open:
                         # Try to keep cmd open
                         subprocess.Popen(f'start "" cmd /k "{path}"', shell=True, cwd=script_dir, creationflags=cflags)
                    else:
                         subprocess.Popen(f'start "" "{path}"', shell=True, cwd=script_dir, creationflags=cflags)
            else:
                # It's likely a command (e.g. 'code .', 'npm start')
                # Run it directly in shell with no specific cwd
                if not hide and keep_open:
                     subprocess.Popen(f'start "" cmd /k "{path}"', shell=True, creationflags=cflags)
                else:
                     subprocess.Popen(path, shell=True, creationflags=cflags)
            
            # Kill main window if requested
            if script_obj.get("kill_window", False):
                self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch:\\n{path}\\n\\n{e}")

    def launch_inline_script(self, script_obj):
        """Execute an inline script by creating a temporary file"""
        import tempfile
        
        inline_script = script_obj.get("inline_script", "")
        inline_type = script_obj.get("inline_type", "cmd")
        hide = script_obj.get("hide_terminal", False)
        keep_open = script_obj.get("keep_open", False)
        
        cflags = subprocess.CREATE_NEW_CONSOLE
        if hide:
            cflags = 0x08000000
        
        try:
            # Create temp file with appropriate extension
            ext_map = {"cmd": ".bat", "pwsh": ".ps1", "powershell": ".ps1"}
            ext = ext_map.get(inline_type, ".bat")
            
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as f:
                f.write(inline_script)
                temp_path = f.name
            
            # Execute based on type
            if inline_type in ["pwsh", "powershell"]:
                ps_bin = "pwsh" if inline_type == "pwsh" and shutil.which("pwsh") else "powershell"
                
                if hide:
                    ps_args = [ps_bin, "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-NoProfile", "-File", temp_path]
                    subprocess.Popen(ps_args, creationflags=cflags)
                else:
                    no_exit = "-NoExit" if keep_open else ""
                    cmd_str = f'start "" "{ps_bin}" {no_exit} -ExecutionPolicy Bypass -Command "& \\"{temp_path}\\""'
                    subprocess.Popen(cmd_str, shell=True, creationflags=cflags)
            else:  # cmd
                if not hide and keep_open:
                    subprocess.Popen(f'start "" cmd /k "{temp_path}"', shell=True, creationflags=cflags)
                else:
                    subprocess.Popen(f'start "" cmd /c "{temp_path}"', shell=True, creationflags=cflags)
                    
            if script_obj.get("kill_window", False):
                self.root.destroy()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute inline script:\\n\\n{e}")

    def handle_ctrl_right_click(self, event, script):
        cmd = script.get("ctrl_right_cmd")
        if cmd:
            temp_script = script.copy()
            temp_script["path"] = cmd
            self.launch_script(temp_script)
            return "break" # Attempt to prevent context menu

    def show_context_menu(self, event, script):
        # If Ctrl is held, don't show menu (handled by ctrl_right_click, but safety check)
        if event.state & 0x0004:
            return

        menu = tk.Menu(self.root, tearoff=0, bg="#2b2f38", fg="white", activebackground=self.config["settings"]["accent_color"])
        menu.add_command(label=f"Edit / Stylize", command=lambda: self.open_edit_dialog(script))
        menu.add_command(label=f"Edit / Stylize", command=lambda: self.open_edit_dialog(script))
        menu.add_command(label="Duplicate", command=lambda: self.duplicate_script(script))
        menu.add_command(label="Cut", command=lambda: self.cut_script(script))
        
        # Move Out Option (if inside a folder)
        if self.view_stack:
             menu.add_command(label="Move Up / Out", command=lambda: self.move_script_out(script))

        menu.add_separator()
        menu.add_command(label=f"Delete", command=lambda: self.remove_script(script))
        menu.post(event.x_root, event.y_root)

    def move_script_out(self, script):
        if not self.view_stack:
            return

        # Current container
        current_list = self.view_stack[-1]["scripts"]
        
        # Parent container
        if len(self.view_stack) > 1:
            parent_list = self.view_stack[-2]["scripts"]
        else:
            parent_list = self.config["scripts"]
            
        if script in current_list:
            current_list.remove(script)
            parent_list.append(script)
            self.save_config()
            self.refresh_grid()

    def cut_script(self, script):
        self.clipboard_script = script.copy()
        # Remove from current location
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        if script in scripts:
            scripts.remove(script)
            self.save_config()
            self.refresh_grid()
            
    def paste_script(self):
        if not self.clipboard_script:
            return
        
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        scripts.append(self.clipboard_script.copy()) # Copy again to avoid ref issues if pasted multiple times
        self.save_config()
        self.refresh_grid()
        self.root.attributes("-topmost", True)

    def duplicate_script(self, script):
        new_script = script.copy()
        new_script["name"] = f"{script['name']} (Copy)"
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        scripts.append(new_script)
        self.save_config()
        self.refresh_grid()

    def open_edit_dialog(self, script):
        self.root.attributes("-topmost", False)
        top = tk.Toplevel(self.root)
        top.overrideredirect(True)
        
        # Center the dialog - WIDER for side-by-side layout
        # Adjust width based on type: folders are narrower
        width = 500 if script.get("type") == "folder" else 900
        height = 750
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f"{width}x{height}+{x}+{y}")
        
        # Ensure dialog is visible above everything
        top.attributes("-topmost", True)
        
        # Force focus
        top.focus_force()

        # Custom Border Frame
        border_color = self.config["settings"].get("border_color", "#fe1616")
        border_frame = tk.Frame(top, bg=border_color)
        border_frame.pack(fill="both", expand=True)

        # Content Frame (Inner)
        dialog = tk.Frame(border_frame, bg="#1d2027")
        dialog.pack(fill="both", expand=True, padx=2, pady=2)

        # Custom Header
        header = tk.Frame(dialog, bg="#1d2027", height=30)
        header.pack(fill="x", padx=10, pady=5)
        
        # Header Title
        tk.Label(header, text=f"Edit {script['name']}", fg=self.config["settings"]["accent_color"], bg="#1d2027", font=(self.main_font, 12, "bold")).pack(side="left")
        
        # Window Dragging Logic
        def start_move(event):
            top.x = event.x
            top.y = event.y

        def do_move(event):
            deltax = event.x - top.x
            deltay = event.y - top.y
            x = top.winfo_x() + deltax
            y = top.winfo_y() + deltay
            top.geometry(f"+{x}+{y}")

        header.bind("<ButtonPress-1>", start_move)
        header.bind("<B1-Motion>", do_move)
        # Also bind to the title label so dragging works there too
        for child in header.winfo_children():
            child.bind("<ButtonPress-1>", start_move)
            child.bind("<B1-Motion>", do_move)

        def on_close():
            top.destroy()
            self.root.attributes("-topmost", True)

        # Close Button
        ctk.CTkButton(header, text="✕", width=30, height=30, fg_color="transparent", hover_color="#c42b1c", text_color="white", command=on_close).pack(side="right")

        # Main Content Container - Side by Side Layout
        content_container = tk.Frame(dialog, bg="#1d2027")
        content_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left Panel - Main Edit Controls
        left_panel = tk.Frame(content_container, bg="#1d2027")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Only show right panel for scripts (not folders)
        if script.get("type") != "folder":
            # Separator
            separator = tk.Frame(content_container, bg="#10b153", width=2)
            separator.pack(side="left", fill="y", padx=5)
            
            # Right Panel - Inline Script Editor (slightly shorter, centered)
            right_panel = tk.Frame(content_container, bg="#1d2027", width=400)
            right_panel.pack(side="right", fill="y", pady=30)
            right_panel.pack_propagate(False)
        else:
            right_panel = None

        def pick_color(key, btn):
            from tkinter import colorchooser
            curr = script.get(key, "#2b2f38")
            color = colorchooser.askcolor(initialcolor=curr, parent=top)
            if color[1]:
                script[key] = color[1]
                # Update preview button immediate appearance
                if key in ["color", "hover_color"]: 
                    btn.configure(fg_color=color[1], hover_color=color[1])
                elif key in ["text_color", "hover_text_color"]: 
                    btn.configure(text_color=color[1])

        # --- Section 1: Basic Info ---
        info_frame = tk.LabelFrame(left_panel, text="   BASIC INFO   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # Label Input
        tk.Label(info_frame, text="Label Name:", fg="white", bg="#1d2027", font=(self.main_font, 9)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        name_var = tk.StringVar(value=script["name"])
        tk.Entry(info_frame, textvariable=name_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0).grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # Path Input (if not folder)
        if script.get("type") != "folder":
            tk.Label(info_frame, text="Script Path:", fg="white", bg="#1d2027", font=(self.main_font, 9)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
            path_cnt = tk.Frame(info_frame, bg="#1d2027")
            path_cnt.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
            path_var = tk.StringVar(value=script.get("path", ""))
            tk.Entry(path_cnt, textvariable=path_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0).pack(side="left", fill="x", expand=True)
            tk.Button(path_cnt, text="..", command=lambda: path_var.set(filedialog.askopenfilename() or path_var.get()), bg="#3a3f4b", fg="white", width=2).pack(side="right", padx=(5,0))
            
            # Checkboxes Frame
            cb_frame = tk.Frame(info_frame, bg="#1d2027")
            cb_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0,5))
            
            hide_var = tk.BooleanVar(value=script.get("hide_terminal", False))
            cb_hide = tk.Checkbutton(cb_frame, text="Hide Terminal", variable=hide_var, bg="#1d2027", fg="#aaaaaa", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
            cb_hide.pack(side="left", padx=(0, 10))
            
            keep_open_var = tk.BooleanVar(value=script.get("keep_open", False))
            cb_keep = tk.Checkbutton(cb_frame, text="No Exit Terminal", variable=keep_open_var, bg="#1d2027", fg="#aaaaaa", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
            cb_keep.pack(side="left", padx=(0, 10))

            kill_window_var = tk.BooleanVar(value=script.get("kill_window", False))
            cb_kill = tk.Checkbutton(cb_frame, text="Kill Main Window", variable=kill_window_var, bg="#1d2027", fg="#aaaaaa", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
            cb_kill.pack(side="left")
            
            # Advanced Bindings
            tk.Label(info_frame, text="Ctrl+Left Cmd:", fg="white", bg="#1d2027", font=(self.main_font, 9)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
            ctrl_left_var = tk.StringVar(value=script.get("ctrl_left_cmd", ""))
            tk.Entry(info_frame, textvariable=ctrl_left_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0).grid(row=3, column=1, sticky="ew", padx=10, pady=5)

            tk.Label(info_frame, text="Ctrl+Right Cmd:", fg="white", bg="#1d2027", font=(self.main_font, 9)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
            ctrl_right_var = tk.StringVar(value=script.get("ctrl_right_cmd", ""))
            tk.Entry(info_frame, textvariable=ctrl_right_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0).grid(row=4, column=1, sticky="ew", padx=10, pady=5)
            
            # --- INLINE SCRIPT SECTION ---
            if right_panel:  # Only show if right panel exists (not folder)
                inline_frame = tk.LabelFrame(right_panel, text="   INLINE SCRIPT EDITOR   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
                inline_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Execution Mode
            use_inline_var = tk.StringVar(value="inline" if script.get("use_inline", False) else "file")
            mode_frame = tk.Frame(inline_frame, bg="#1d2027")
            mode_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Radiobutton(mode_frame, text="Execute File Path", variable=use_inline_var, value="file", bg="#1d2027", fg="#aaaaaa", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white").pack(side="left", padx=(0, 15))
            tk.Radiobutton(mode_frame, text="Execute Inline Script", variable=use_inline_var, value="inline", bg="#1d2027", fg="#aaaaaa", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white").pack(side="left")
            
            # Script Type Selector
            type_frame = tk.Frame(inline_frame, bg="#1d2027")
            type_frame.pack(fill="x", padx=10, pady=5)
            tk.Label(type_frame, text="Script Type:", fg="white", bg="#1d2027", font=(self.main_font, 9)).pack(side="left", padx=(0, 10))
            
            inline_type_var = tk.StringVar(value=script.get("inline_type", "cmd"))
            type_dropdown = ctk.CTkOptionMenu(type_frame, variable=inline_type_var, values=["cmd", "pwsh", "powershell"], width=120, fg_color="#2b2f38", button_color="#3a3f4b", button_hover_color="#4a4f5b")
            type_dropdown.pack(side="left")
            
            # Script Editor
            tk.Label(inline_frame, text="Script Content:", fg="white", bg="#1d2027", font=(self.main_font, 9)).pack(anchor="w", padx=10, pady=(5, 2))
            
            editor_container = tk.Frame(inline_frame, bg="#2b2f38")
            editor_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            inline_script_text = tk.Text(editor_container, bg="#2b2f38", fg="white", insertbackground="white", font=(self.main_font, 10), wrap="none", bd=0, height=12)
            inline_script_text.pack(side="left", fill="both", expand=True)
            
            editor_scrollbar = tk.Scrollbar(editor_container, command=inline_script_text.yview)
            editor_scrollbar.pack(side="right", fill="y")
            inline_script_text.config(yscrollcommand=editor_scrollbar.set)
            
            # Load existing inline script
            if script.get("inline_script"):
                inline_script_text.insert("1.0", script["inline_script"])
        else:
            path_var = None
            hide_var = None
            keep_open_var = None
            kill_window_var = None
            ctrl_left_var = None
            ctrl_right_var = None
            use_inline_var = None
            inline_type_var = None
            inline_script_text = None

        info_frame.grid_columnconfigure(1, weight=1)

        # --- Section 1.5: Folder Settings (If Folder) ---
        if script.get("type") == "folder":
            f_grid_frame = tk.LabelFrame(left_panel, text="   FOLDER GRID SETTINGS   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
            f_grid_frame.pack(fill="x", padx=15, pady=5)
            f_grid_frame.grid_columnconfigure(1, weight=1)
            f_grid_frame.grid_columnconfigure(3, weight=1)

            # Folder Columns
            tk.Label(f_grid_frame, text="Grid Cols:", fg="gray", bg="#1d2027").grid(row=0, column=0, sticky="w", padx=(10, 5), pady=5)
            f_cols_var = tk.StringVar(value=str(script.get("grid_columns", 0)))
            tk.Entry(f_grid_frame, textvariable=f_cols_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
            tk.Label(f_grid_frame, text="(0 = Global)", fg="#666666", bg="#1d2027", font=(self.main_font, 8)).grid(row=0, column=2, sticky="w", padx=5)

            # Child Defaults
            tk.Label(f_grid_frame, text="Child W:", fg="gray", bg="#1d2027").grid(row=1, column=0, sticky="w", padx=(10, 5), pady=5)
            f_cw_var = tk.StringVar(value=str(script.get("child_width", 0)))
            tk.Entry(f_grid_frame, textvariable=f_cw_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

            tk.Label(f_grid_frame, text="Child H:", fg="gray", bg="#1d2027").grid(row=1, column=2, sticky="w", padx=(10, 5), pady=5)
            f_ch_var = tk.StringVar(value=str(script.get("child_height", 0)))
            tk.Entry(f_grid_frame, textvariable=f_ch_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        else:
            f_cols_var = None
            f_cw_var = None
            f_ch_var = None

        # --- Section 2: Typography ---
        typo_frame = tk.LabelFrame(left_panel, text="   TYPOGRAPHY   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        typo_frame.pack(fill="x", padx=15, pady=5)
        
        # Font Family Row
        font_family_row = tk.Frame(typo_frame, bg="#1d2027")
        font_family_row.pack(fill="x", padx=10, pady=(10, 5))
        
        tk.Label(font_family_row, text="Font:", fg="white", bg="#1d2027").pack(side="left", padx=(0, 5))
        
        # Get available fonts
        from tkinter import font as tkfont
        available_fonts = sorted(list(set(tkfont.families())))
        # Add common fonts to the top if they exist
        priority_fonts = ["JetBrainsMono NFP", "JetBrainsMono Nerd Font", "JetBrains Mono", "Consolas", "Courier New", "Arial", "Segoe UI", "Calibri"]
        font_list = [f for f in priority_fonts if f in available_fonts] + [f for f in available_fonts if f not in priority_fonts]
        
        current_font = script.get("font_family", self.config["settings"].get("font_family", self.main_font))
        font_family_var = tk.StringVar(value=current_font)
        
        # Create custom styled combobox
        from tkinter import ttk
        
        # Configure style for better appearance
        combo_style = ttk.Style()
        combo_style.theme_use('clam')
        
        combo_style.configure('Dark.TCombobox',
                             fieldbackground='#2b2f38',
                             background='#2b2f38',
                             foreground='white',
                             arrowcolor='white',
                             bordercolor='#3a3f4b',
                             lightcolor='#2b2f38',
                             darkcolor='#2b2f38',
                             borderwidth=1,
                             relief='flat')
        
        combo_style.map('Dark.TCombobox',
                       fieldbackground=[('readonly', '#2b2f38'), ('disabled', '#1d2027')],
                       foreground=[('readonly', 'white'), ('disabled', '#666666')],
                       background=[('readonly', '#2b2f38')],
                       bordercolor=[('focus', '#26b2f3')])
        
        # Dropdown list styling
        top.option_add('*TCombobox*Listbox.background', '#2b2f38')
        top.option_add('*TCombobox*Listbox.foreground', 'white')
        top.option_add('*TCombobox*Listbox.selectBackground', '#26b2f3')
        top.option_add('*TCombobox*Listbox.selectForeground', 'white')
        top.option_add('*TCombobox*Listbox.font', (self.main_font, 9))
        
        font_combo = ttk.Combobox(
            font_family_row,
            textvariable=font_family_var,
            values=font_list,
            state="normal",  # Allow typing to search
            width=25,
            height=15,
            style='Dark.TCombobox'
        )
        font_combo.pack(side="left", padx=5)
        
        # Bind events for type-to-search functionality
        def on_keypress(event):
            typed = event.char.lower()
            if typed and typed.isprintable():
                current_val = font_family_var.get()
                # Find first font starting with typed character
                for font in font_list:
                    if font.lower().startswith(typed):
                        font_combo.set(font)
                        # Scroll to show the selected item
                        try:
                            idx = font_list.index(font)
                            font_combo.current(idx)
                        except:
                            pass
                        break
                return "break"  # Prevent default behavior
        
        font_combo.bind("<KeyPress>", on_keypress)
        
        # Prevent manual editing, only allow selection
        def validate_selection(event):
            if font_family_var.get() not in font_list:
                # Reset to current font if invalid
                font_combo.set(current_font)
        
        font_combo.bind("<FocusOut>", validate_selection)
        
        # Font Size & Styles Row
        size_style_row = tk.Frame(typo_frame, bg="#1d2027")
        size_style_row.pack(fill="x", padx=10, pady=(5, 10))
        
        tk.Label(size_style_row, text="Size:", fg="white", bg="#1d2027").pack(side="left", padx=(0, 5))
        default_fs = self.config["settings"].get("font_size", 10)
        fsize_var = tk.StringVar(value=str(script.get("font_size", default_fs)))
        tk.Entry(size_style_row, textvariable=fsize_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=4).pack(side="left")
        
        v_bold = tk.BooleanVar(value=script.get("is_bold", False))
        tk.Checkbutton(size_style_row, text="Bold", variable=v_bold, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white").pack(side="left", padx=10)
        
        v_italic = tk.BooleanVar(value=script.get("is_italic", False))
        tk.Checkbutton(size_style_row, text="Italic", variable=v_italic, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white").pack(side="left", padx=5)

        # --- Section 3: Colors ---
        color_frame = tk.LabelFrame(left_panel, text="   COLORS   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        color_frame.pack(fill="x", padx=15, pady=10)
        color_frame.grid_columnconfigure(0, weight=1)
        color_frame.grid_columnconfigure(1, weight=1)
        
        cp1 = ctk.CTkButton(color_frame, text="Button BG", fg_color=script.get("color", "#2b2f38"), height=30, hover=False, command=lambda: pick_color("color", cp1))
        cp1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        cp3 = ctk.CTkButton(color_frame, text="Text Color", text_color=script.get("text_color", "white"), fg_color="#2b2f38", height=30, hover=False, command=lambda: pick_color("text_color", cp3))
        cp3.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        cp2 = ctk.CTkButton(color_frame, text="Hover BG", fg_color=script.get("hover_color", "#26b2f3"), height=30, hover=False, command=lambda: pick_color("hover_color", cp2))
        cp2.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        
        cp4 = ctk.CTkButton(color_frame, text="Hover Text", text_color=script.get("hover_text_color", "white"), fg_color="#2b2f38", height=30, hover=False, command=lambda: pick_color("hover_text_color", cp4))
        cp4.grid(row=1, column=1, padx=10, pady=(0,10), sticky="ew")

        # --- Section 4: Shape & Borders ---
        # --- Section 4: Layout & Borders ---
        layout_frame = tk.LabelFrame(left_panel, text="   LAYOUT & APPEARANCE   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        layout_frame.pack(fill="x", padx=15, pady=5)
        
        # Use Grid layout for alignment
        layout_frame.grid_columnconfigure(1, weight=1)
        layout_frame.grid_columnconfigure(3, weight=1)
        
        # Row 1: Dimensions
        tk.Label(layout_frame, text="Width:", fg="gray", bg="#1d2027").grid(row=0, column=0, sticky="w", padx=(10, 5), pady=5)
        width_var = tk.StringVar(value=str(script.get("width", 0)))
        tk.Entry(layout_frame, textvariable=width_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        tk.Label(layout_frame, text="Height:", fg="gray", bg="#1d2027").grid(row=0, column=2, sticky="w", padx=(15, 5), pady=5)
        height_var = tk.StringVar(value=str(script.get("height", 0)))
        tk.Entry(layout_frame, textvariable=height_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Row 2: Spanning
        tk.Label(layout_frame, text="Col Span:", fg="gray", bg="#1d2027").grid(row=1, column=0, sticky="w", padx=(10, 5), pady=5)
        col_span_var = tk.StringVar(value=str(script.get("col_span", 1)))
        tk.Entry(layout_frame, textvariable=col_span_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        tk.Label(layout_frame, text="Row Span:", fg="gray", bg="#1d2027").grid(row=1, column=2, sticky="w", padx=(15, 5), pady=5)
        row_span_var = tk.StringVar(value=str(script.get("row_span", 1)))
        tk.Entry(layout_frame, textvariable=row_span_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        # Row 3: Borders
        tk.Label(layout_frame, text="Radius:", fg="gray", bg="#1d2027").grid(row=2, column=0, sticky="w", padx=(10, 5), pady=(5, 10))
        radius_var = tk.StringVar(value=str(script.get("corner_radius", 4)))
        tk.Entry(layout_frame, textvariable=radius_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=2, column=1, sticky="ew", padx=5, pady=(5, 10))

        tk.Label(layout_frame, text="Border W:", fg="gray", bg="#1d2027").grid(row=2, column=2, sticky="w", padx=(15, 5), pady=(5, 10))
        border_width_var = tk.StringVar(value=str(script.get("border_width", 0)))
        tk.Entry(layout_frame, textvariable=border_width_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=5).grid(row=2, column=3, sticky="ew", padx=5, pady=(5, 10))
        
        cp5 = ctk.CTkButton(layout_frame, text="Border Color", fg_color=script.get("border_color", "#fe1616"), width=100, height=24, hover=False, command=lambda: pick_color("border_color", cp5))
        cp5.grid(row=3, column=0, columnspan=4, pady=(0, 10), sticky="ew", padx=10)

        def save_changes():
            script["name"] = name_var.get()
            if path_var:
                script["path"] = path_var.get()
            if hide_var is not None:
                script["hide_terminal"] = hide_var.get()
            if keep_open_var is not None:
                script["keep_open"] = keep_open_var.get()
            if kill_window_var is not None:
                script["kill_window"] = kill_window_var.get()
            if ctrl_left_var is not None:
                script["ctrl_left_cmd"] = ctrl_left_var.get()
            if ctrl_right_var is not None:
                script["ctrl_right_cmd"] = ctrl_right_var.get()
            
            # Save inline script settings
            if use_inline_var is not None:
                script["use_inline"] = (use_inline_var.get() == "inline")
            if inline_type_var is not None:
                script["inline_type"] = inline_type_var.get()
            if inline_script_text is not None:
                script["inline_script"] = inline_script_text.get("1.0", "end-1c")
            
            # Save folder settings
            if f_cols_var is not None:
                try: script["grid_columns"] = int(f_cols_var.get())
                except: script["grid_columns"] = 0
            if f_cw_var is not None:
                try: script["child_width"] = int(f_cw_var.get())
                except: script["child_width"] = 0
            if f_ch_var is not None:
                try: script["child_height"] = int(f_ch_var.get())
                except: script["child_height"] = 0
                
            try:
                script["font_size"] = int(fsize_var.get())
            except:
                script["font_size"] = self.config["settings"].get("font_size", 10)
            
            # Save font family
            script["font_family"] = font_family_var.get()
            
            try:
                script["border_width"] = int(border_width_var.get())
            except:
                script["border_width"] = 0
            try:
                script["corner_radius"] = int(radius_var.get())
            except:
                script["corner_radius"] = 4
                
            try:
                script["col_span"] = max(1, int(col_span_var.get()))
            except:
                script["col_span"] = 1
                
            try:
                script["row_span"] = max(1, int(row_span_var.get()))
            except:
                script["row_span"] = 1
                
            try:
                script["width"] = int(width_var.get())
            except:
                script["width"] = 0
            
            try:
                script["height"] = int(height_var.get())
            except:
                script["height"] = 0
            
            script["is_bold"] = v_bold.get()
            script["is_italic"] = v_italic.get()
            
            self.save_config()
            self.refresh_grid()
            on_close()

        ctk.CTkButton(dialog, text="Save", width=200, height=50, fg_color="#10b153", hover_color="#0d8c42", font=(self.main_font, 13, "bold"), command=save_changes).pack(pady=20)
        
        # No WM protocol for overrideredirect, but keep cleanup separate
        # dialog.protocol("WM_DELETE_WINDOW", on_close) not needed

    def remove_script(self, script):
        self.root.attributes("-topmost", False)
        if messagebox.askyesno("Confirm", f"Remove script '{script['name']}'?", parent=self.root):
            scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
            scripts.remove(script)
            self.save_config()
            self.refresh_grid()
        self.root.attributes("-topmost", True)

    def add_script_dialog(self):
        self.root.attributes("-topmost", False)
        
        # Styled choice dialog
        choice_dialog = tk.Toplevel(self.root)
        choice_dialog.overrideredirect(True) # Borderless
        choice_dialog.configure(bg="#1d2027")
        choice_dialog.attributes("-topmost", True)
        
        # Dimensions
        w = 300
        h = 220 if self.clipboard_script else 150
        cx = (choice_dialog.winfo_screenwidth() // 2) - (w // 2)
        cy = (choice_dialog.winfo_screenheight() // 2) - (h // 2)
        choice_dialog.geometry(f"{w}x{h}+{cx}+{cy}")

        # --- Custom UI Structure ---
        border_color = self.config["settings"].get("border_color", "#fe1616")
        border_frame = tk.Frame(choice_dialog, bg=border_color)
        border_frame.pack(fill="both", expand=True)

        # Header
        header_frame = tk.Frame(border_frame, bg="#1d2027")
        header_frame.pack(fill="x", pady=(1,0))
        
        tk.Label(header_frame, text="ADD NEW", fg="gray", bg="#1d2027", font=(self.main_font, 10, "bold")).pack(side="left", padx=10)
        
        def close_win():
            self.root.attributes("-topmost", True)
            choice_dialog.destroy()
            
        close_btn = tk.Button(header_frame, text="✕", bg="#1d2027", fg="gray", activebackground="#ff605c", activeforeground="white", bd=0, width=4, command=close_win)
        close_btn.pack(side="right", padx=5, pady=5)

        # Drag Logic
        def start_move(event):
            choice_dialog.x = event.x
            choice_dialog.y = event.y

        def do_move(event):
            deltax = event.x - choice_dialog.x
            deltay = event.y - choice_dialog.y
            x = choice_dialog.winfo_x() + deltax
            y = choice_dialog.winfo_y() + deltay
            choice_dialog.geometry(f"+{x}+{y}")

        header_frame.bind("<ButtonPress-1>", start_move)
        header_frame.bind("<B1-Motion>", do_move)
        
        # Content
        content_frame = tk.Frame(border_frame, bg="#1d2027")
        content_frame.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(content_frame, text="Select Item Type:", fg="white", bg="#1d2027", font=(self.main_font, 10)).pack(pady=(15, 10))
        
        def start_add(t):
            choice_dialog.destroy()
            if t == "folder":
                name = self.show_custom_input("NEW FOLDER", "Enter folder name:")
                if name:
                    scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
                    scripts.append({"name": name, "type": "folder", "scripts": []})
                    self.save_config()
                    self.refresh_grid()
            else:
                name = self.show_custom_input("NEW SCRIPT", "Enter button label:")
                if name:
                    path = filedialog.askopenfilename(title="Select Script or Executable", parent=self.root)
                    if path:
                        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
                        scripts.append({"name": name, "path": path, "type": "script"})
                        self.save_config()
                        self.refresh_grid()
            self.root.attributes("-topmost", True)

        # Button Container
        btn_frame = tk.Frame(content_frame, bg="#1d2027")
        btn_frame.pack(pady=5)

        ctk.CTkButton(btn_frame, text="📄 Script", width=100, command=lambda: start_add("script")).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="📁 Folder", width=100, command=lambda: start_add("folder")).pack(side="left", padx=10)
        
        if self.clipboard_script:
            ctk.CTkButton(content_frame, text=f"📋 Paste '{self.clipboard_script['name']}'", fg_color="#e69138", hover_color="#b45f06", width=220, command=lambda: [choice_dialog.destroy(), self.paste_script()]).pack(side="bottom", pady=20)

    def open_settings(self):
        self.root.attributes("-topmost", False)
        top = tk.Toplevel(self.root)
        top.overrideredirect(True)
        
        # Center the settings dialog
        width, height = 400, 500
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f"{width}x{height}+{x}+{y}")
        
        # Ensure dialog is visible above everything
        top.attributes("-topmost", True)
        top.focus_force()

        # Custom Border Frame
        border_color = self.config["settings"].get("border_color", "#fe1616")
        border_frame = tk.Frame(top, bg=border_color)
        border_frame.pack(fill="both", expand=True)

        # Content Frame
        dialog = tk.Frame(border_frame, bg="#1d2027")
        dialog.pack(fill="both", expand=True, padx=2, pady=2)

        # Custom Header
        header = tk.Frame(dialog, bg="#1d2027", height=30)
        header.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header, text="SETTINGS", fg=self.config["settings"]["accent_color"], bg="#1d2027", font=(self.main_font, 12, "bold")).pack(side="left")

        # Window Dragging Logic
        def start_move(event):
            top.x = event.x
            top.y = event.y

        def do_move(event):
            deltax = event.x - top.x
            deltay = event.y - top.y
            x = top.winfo_x() + deltax
            y = top.winfo_y() + deltay
            top.geometry(f"+{x}+{y}")

        header.bind("<ButtonPress-1>", start_move)
        header.bind("<B1-Motion>", do_move)
        for child in header.winfo_children():
            child.bind("<ButtonPress-1>", start_move)
            child.bind("<B1-Motion>", do_move)

        def on_close():
            top.destroy()
            self.root.attributes("-topmost", True)

        ctk.CTkButton(header, text="✕", width=30, height=30, fg_color="transparent", hover_color="#c42b1c", text_color="white", command=on_close).pack(side="right")

        # --- Section 1: Grid Config ---
        grid_frame = tk.LabelFrame(dialog, text="   GRID CONFIGURATION   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        grid_frame.pack(fill="x", padx=15, pady=10)

        # Row 1: Columns
        row1 = tk.Frame(grid_frame, bg="#1d2027")
        row1.pack(pady=5, anchor="w", padx=10)
        tk.Label(row1, text="Buttons per Row:  ", fg="white", bg="#1d2027", font=(self.main_font, 9)).pack(side="left")
        val_var = tk.StringVar(value=str(self.config["settings"]["columns"]))
        tk.Entry(row1, textvariable=val_var, width=5, justify="center", bg="#2b2f38", fg="white", insertbackground="white", bd=0).pack(side="left")
        
        # Row 2: Default Font Size
        row2 = tk.Frame(grid_frame, bg="#1d2027")
        row2.pack(pady=5, anchor="w", padx=10)
        tk.Label(row2, text="Default Font Size: ", fg="white", bg="#1d2027", font=(self.main_font, 9)).pack(side="left")
        f_size_var = tk.StringVar(value=str(self.config["settings"].get("font_size", 10)))
        tk.Entry(row2, textvariable=f_size_var, width=5, justify="center", bg="#2b2f38", fg="white", insertbackground="white", bd=0).pack(side="left")

        # --- Section 2: Window Behavior ---
        win_frame = tk.LabelFrame(dialog, text="   WINDOW BEHAVIOR   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        win_frame.pack(fill="x", padx=15, pady=5)
        
        v_topmost = tk.BooleanVar(value=self.config["settings"].get("always_on_top", True))
        cb_topmost = tk.Checkbutton(win_frame, text="Always on Top", variable=v_topmost, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
        cb_topmost.pack(anchor="w", padx=10, pady=5)

        # --- Section 3: Widgets ---
        widget_frame = tk.LabelFrame(dialog, text="   WIDGET TOGGLES   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        widget_frame.pack(fill="x", padx=15, pady=10)
        
        v_github = tk.BooleanVar(value=self.config["settings"].get("show_github", True))
        cb_github = tk.Checkbutton(widget_frame, text="GitHub Status Monitoring", variable=v_github, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
        cb_github.pack(anchor="w", padx=10, pady=2)

        v_rclone = tk.BooleanVar(value=self.config["settings"].get("show_rclone", True))
        cb_rclone = tk.Checkbutton(widget_frame, text="Rclone Status Monitoring", variable=v_rclone, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
        cb_rclone.pack(anchor="w", padx=10, pady=2)

        v_stats = tk.BooleanVar(value=self.config["settings"].get("show_system_stats", True))
        cb_stats = tk.Checkbutton(widget_frame, text="System Stats Widget", variable=v_stats, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
        cb_stats.pack(anchor="w", padx=10, pady=2)

        def save():
            try:
                n = int(val_var.get())
                fs = int(f_size_var.get())
                if 1 <= n <= 10:
                    self.config["settings"]["columns"] = n
                    self.config["settings"]["font_size"] = fs
                    self.config["settings"]["show_github"] = v_github.get()
                    self.config["settings"]["show_rclone"] = v_rclone.get()
                    self.config["settings"]["show_system_stats"] = v_stats.get()
                    self.config["settings"]["always_on_top"] = v_topmost.get()
                    self.save_config()
                    
                    # Apply topmost immediately
                    self.root.attributes("-topmost", self.config["settings"]["always_on_top"])
                    
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
            top.destroy()
            self.root.attributes("-topmost", True)

        # dialog.protocol("WM_DELETE_WINDOW", on_close) # Not needed for frame/overrideredirect
        ctk.CTkButton(dialog, text="SAVE SETTINGS", command=save, width=150, height=40, fg_color="#10b153", hover_color="#0d8c42", font=(self.main_font, 12, "bold")).pack(pady=20)

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

        # Start all monitoring loops immediately
        threading.Thread(target=self.system_stats_loop, daemon=True).start()
        threading.Thread(target=self.github_monitor_loop, daemon=True).start()
        threading.Thread(target=self.rclone_monitor_loop, args=(log_dir,), daemon=True).start()

    def system_stats_loop(self):
        while not self.stop_threads:
            if not self.config["settings"].get("show_system_stats", True):
                time.sleep(1)
                continue
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
            if not self.config["settings"].get("show_github", True):
                time.sleep(1)
                continue
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
            
            time.sleep(2) # GitHub check interval

    def rclone_monitor_loop(self, log_dir):
        def run_single_check(folder):
            name = folder["name"]
            cfg_cmd = folder.get("cmd", "rclone check src dst --fast-list --size-only")
            actual_cmd = cfg_cmd.replace("src", folder["src"]).replace("dst", folder["dst"])
            log_file = os.path.join(log_dir, f"{name}_check.log")
            try:
                with open(log_file, "w") as f:
                    subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f, timeout=60)
                with open(log_file, "r") as f:
                    content = f.read()
                is_ok = "ERROR" not in content
                self.root.after(0, lambda n=name, ok=is_ok: self.update_folder_status_ui(n, ok))
            except:
                self.root.after(0, lambda n=name: self.update_folder_status_ui(n, False))

        while not self.stop_threads:
            if not self.config["settings"].get("show_rclone", True):
                time.sleep(5)
                continue
            
            # Start all checks in parallel threads
            for folder in self.config["rclone_folders"]:
                threading.Thread(target=run_single_check, args=(folder,), daemon=True).start()
            
            time.sleep(600) # Wait 10 minutes before triggering next batch of parallel checks

    def update_repo_status_ui(self, name, status):
        if name in self.repo_labels:
            ui = self.repo_labels[name]
            color = "#555555"
            text = "Unknown"
            if status == "clean": color, text = "#1fb141", "Clean"
            elif status == "dirty": color, text = "#e2b528", "Dirty"
            elif status == "error": color, text = "#fe1616", "Error"
            elif status == "no_git": color, text = "#666666", "Not Git"
            
            ui["status"].configure(text=text, fg=color)
            ui["circle"].configure(fg=color)

    def update_folder_status_ui(self, name, is_ok):
        if name in self.folder_labels:
            ui = self.folder_labels[name]
            color = "#1fb141" if is_ok else "#fe1616"
            text = "Synced" if is_ok else "Error"
            ui["status"].configure(text=text, fg=color)
            ui["circle"].configure(fg=color)

    def show_custom_input(self, title, prompt):
        result = [None]
        
        # Disable main window
        self.root.attributes("-topmost", False)
        
        dlg = tk.Toplevel(self.root)
        dlg.overrideredirect(True)
        dlg.configure(bg="#1d2027")
        dlg.attributes("-topmost", True)
        
        # Center
        w, h = 320, 180
        cx = (dlg.winfo_screenwidth() // 2) - (w // 2)
        cy = (dlg.winfo_screenheight() // 2) - (h // 2)
        dlg.geometry(f"{w}x{h}+{cx}+{cy}")
        
        border_color = self.config["settings"].get("border_color", "#fe1616")
        border = tk.Frame(dlg, bg=border_color)
        border.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(border, bg="#1d2027")
        header.pack(fill="x", pady=(1,0))
        tk.Label(header, text=title, fg="gray", bg="#1d2027", font=(self.main_font, 10, "bold")).pack(side="left", padx=10)
        
        # Dragging
        def start_move(event):
            dlg.x = event.x
            dlg.y = event.y
        def do_move(event):
            x = dlg.winfo_x() + (event.x - dlg.x)
            y = dlg.winfo_y() + (event.y - dlg.y)
            dlg.geometry(f"+{x}+{y}")
        header.bind("<ButtonPress-1>", start_move)
        header.bind("<B1-Motion>", do_move)
        
        # Content
        content = tk.Frame(border, bg="#1d2027")
        content.pack(fill="both", expand=True, padx=1, pady=1)
        
        tk.Label(content, text=prompt, fg="white", bg="#1d2027", font=(self.main_font, 10)).pack(pady=(20, 5))
        
        entry = tk.Entry(content, bg="#2b2f38", fg="white", font=(self.main_font, 11), insertbackground="white", bd=0, justify="center")
        entry.pack(fill="x", padx=30, pady=5)
        entry.focus()
        
        def on_ok(e=None):
            val = entry.get().strip()
            if val:
                result[0] = val
            dlg.destroy()
            
        def on_cancel():
            dlg.destroy()
            
        entry.bind("<Return>", on_ok)
        entry.bind("<Escape>", lambda e: on_cancel())
        
        btn_frame = tk.Frame(content, bg="#1d2027")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(btn_frame, text="OK", width=80, height=30, command=on_ok, fg_color="#10b153", hover_color="#0d8c42").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", width=80, height=30, command=on_cancel, fg_color="#555555", hover_color="#333333").pack(side="left", padx=5)
        
        self.root.wait_window(dlg)
        self.root.attributes("-topmost", True)
        return result[0]

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = tk.Tk()
    app = ScriptLauncherApp(root)
    root.mainloop()
