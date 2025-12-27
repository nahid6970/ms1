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
        self.script_drag_data = {"index": None, "active": False, "ghost": None, "start_abs": (0, 0), "block_click": False}
        self.view_stack = [] # Stack of (folder_name, script_list_reference)
        
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
        # MIDDLE SECTION: Buttons Grid
        self.grid_scroll_container = tk.Frame(self.main_content, bg="#1d2027")
        self.grid_scroll_container.pack(fill="both", expand=True)
        
        self.grid_frame = tk.Frame(self.grid_scroll_container, bg="#1d2027")
        self.grid_frame.pack(fill="both", expand=True)

        self.refresh_grid()

    def refresh_grid(self):
        # Clear
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        cols = self.config["settings"]["columns"]
        # Determine current folder level
        if self.view_stack:
            folder_name, scripts = self.view_stack[-1]
            self.title_lbl.config(text=f" ❯ {folder_name.upper()}")
            self.back_btn.pack(side="left", padx=(0, 5))
        else:
            scripts = self.config["scripts"]
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
            
            font_spec = ctk.CTkFont(
                family=self.main_font,
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

            btn = ctk.CTkButton(
                self.grid_frame, 
                text=display_text,
                width=160 * c_span + (16 * (c_span - 1)), # Account for gaps
                height=45 * r_span + (16 * (r_span - 1)),
                corner_radius=corner_radius,
                fg_color=b_color, 
                text_color=t_color,
                hover=False, 
                font=font_spec,
                border_width=b_width,
                border_color=b_border_color
            )
            btn.grid(row=place_r, column=place_c, rowspan=r_span, columnspan=c_span, padx=8, pady=8, sticky="nsew")
            
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

    def handle_script_click(self, script):
        if script.get("type") == "folder":
            self.enter_folder(script)
        else:
            self.launch_script(script)

    def enter_folder(self, folder):
        if "scripts" not in folder:
            folder["scripts"] = []
        self.view_stack.append((folder["name"], folder["scripts"]))
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
            scripts = self.view_stack[-1][1] if self.view_stack else self.config["scripts"]
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

        # Figure out target index
        target_idx = None
        for i, child in enumerate(self.grid_frame.winfo_children()):
            if child == target_widget or any(target_widget == sub for sub in child.winfo_children()):
                target_idx = i
                break
        
        scripts = self.view_stack[-1][1] if self.view_stack else self.config["scripts"]
        if target_idx is not None and target_idx != self.script_drag_data["index"]:
            # Move item in current list
            item = scripts.pop(self.script_drag_data["index"])
            scripts.insert(target_idx, item)
            self.save_config()
            self.refresh_grid()

    def launch_script(self, script_obj):
        path = script_obj["path"]
        hide = script_obj.get("hide_terminal", False)
        
        # Determine creation flags
        # CREATE_NEW_CONSOLE (0x10) vs CREATE_NO_WINDOW (0x08000000)
        cflags = subprocess.CREATE_NEW_CONSOLE
        if hide:
            cflags = 0x08000000 # CREATE_NO_WINDOW
            
        try:
            # Handle expand vars like %USERPROFILE%
            path = os.path.expandvars(path)
            
            if path.endswith(".py"):
                python_exe = "pythonw" if hide else "python"
                subprocess.Popen([python_exe, path], creationflags=cflags)
            elif path.lower().endswith(".ps1"):
                # PowerShell execution
                ps_args = ["powershell", "-ExecutionPolicy", "Bypass", "-File", path]
                if hide:
                    # Additional flag for PS to stay quiet
                    ps_args = ["powershell", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-NoProfile", "-File", path]
                subprocess.Popen(ps_args, creationflags=cflags)
            else:
                # Use shell start for .exe, .bat, or generic files
                subprocess.Popen(f'start "" "{path}"', shell=True, creationflags=cflags)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch:\n{path}\n\n{e}")

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
        top = tk.Toplevel(self.root)
        top.overrideredirect(True)
        
        # Center the dialog
        width, height = 450, 650
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
        info_frame = tk.LabelFrame(dialog, text="   BASIC INFO   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
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
            
            # Hide Terminal Checkbox
            hide_var = tk.BooleanVar(value=script.get("hide_terminal", False))
            cb_hide = tk.Checkbutton(info_frame, text="Hide Terminal / Console", variable=hide_var, bg="#1d2027", fg="#aaaaaa", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white")
            cb_hide.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0,5))
            
            # Advanced Bindings
            tk.Label(info_frame, text="Ctrl+Left Cmd:", fg="white", bg="#1d2027", font=(self.main_font, 9)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
            ctrl_left_var = tk.StringVar(value=script.get("ctrl_left_cmd", ""))
            tk.Entry(info_frame, textvariable=ctrl_left_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0).grid(row=3, column=1, sticky="ew", padx=10, pady=5)

            tk.Label(info_frame, text="Ctrl+Right Cmd:", fg="white", bg="#1d2027", font=(self.main_font, 9)).grid(row=4, column=0, sticky="w", padx=10, pady=5)
            ctrl_right_var = tk.StringVar(value=script.get("ctrl_right_cmd", ""))
            tk.Entry(info_frame, textvariable=ctrl_right_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0).grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        else:
            path_var = None
            hide_var = None
            ctrl_left_var = None
            ctrl_right_var = None

        info_frame.grid_columnconfigure(1, weight=1)

        # --- Section 2: Typography ---
        typo_frame = tk.LabelFrame(dialog, text="   TYPOGRAPHY   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        typo_frame.pack(fill="x", padx=15, pady=5)
        
        # Font Size & Styles Row
        tk.Label(typo_frame, text="Size:", fg="white", bg="#1d2027").pack(side="left", padx=(10,5), pady=10)
        default_fs = self.config["settings"].get("font_size", 10)
        fsize_var = tk.StringVar(value=str(script.get("font_size", default_fs)))
        tk.Entry(typo_frame, textvariable=fsize_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=4).pack(side="left")
        
        v_bold = tk.BooleanVar(value=script.get("is_bold", False))
        tk.Checkbutton(typo_frame, text="Bold", variable=v_bold, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white").pack(side="left", padx=10)
        
        v_italic = tk.BooleanVar(value=script.get("is_italic", False))
        tk.Checkbutton(typo_frame, text="Italic", variable=v_italic, bg="#1d2027", fg="white", selectcolor="#2b2f38", activebackground="#1d2027", activeforeground="white").pack(side="left", padx=5)

        # --- Section 3: Colors ---
        color_frame = tk.LabelFrame(dialog, text="   COLORS   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
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
        shape_frame = tk.LabelFrame(dialog, text="   SHAPE & BORDERS   ", bg="#1d2027", fg="gray", font=(self.main_font, 10, "bold"), bd=1, relief="groove")
        shape_frame.pack(fill="x", padx=15, pady=5)

        # Radius & Width
        tk.Label(shape_frame, text="Radius:", fg="white", bg="#1d2027").pack(side="left", padx=(10, 5), pady=10)
        radius_var = tk.StringVar(value=str(script.get("corner_radius", 4)))
        tk.Entry(shape_frame, textvariable=radius_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=4).pack(side="left")

        tk.Label(shape_frame, text="Border W:", fg="white", bg="#1d2027").pack(side="left", padx=(15, 5))
        border_width_var = tk.StringVar(value=str(script.get("border_width", 0)))
        tk.Entry(shape_frame, textvariable=border_width_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=4).pack(side="left")
        
        # Border Color Picker
        cp5 = ctk.CTkButton(shape_frame, text="Color", fg_color=script.get("border_color", "#fe1616"), width=60, height=25, hover=False, command=lambda: pick_color("border_color", cp5))
        cp5.pack(side="right", padx=10)
        
        # Grid Spanning
        span_frame = tk.Frame(dialog, bg="#1d2027")
        span_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        tk.Label(span_frame, text="Column Span:", fg="gray", bg="#1d2027").pack(side="left", padx=(10, 5))
        col_span_var = tk.StringVar(value=str(script.get("col_span", 1)))
        tk.Entry(span_frame, textvariable=col_span_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=4).pack(side="left")
        
        tk.Label(span_frame, text="Row Span:", fg="gray", bg="#1d2027").pack(side="left", padx=(15, 5))
        row_span_var = tk.StringVar(value=str(script.get("row_span", 1)))
        tk.Entry(span_frame, textvariable=row_span_var, bg="#2b2f38", fg="white", insertbackground="white", bd=0, width=4).pack(side="left")

        def save_changes():
            script["name"] = name_var.get()
            if path_var:
                script["path"] = path_var.get()
            if hide_var is not None:
                script["hide_terminal"] = hide_var.get()
            if ctrl_left_var is not None:
                script["ctrl_left_cmd"] = ctrl_left_var.get()
            if ctrl_right_var is not None:
                script["ctrl_right_cmd"] = ctrl_right_var.get()
            try:
                script["font_size"] = int(fsize_var.get())
            except:
                script["font_size"] = self.config["settings"].get("font_size", 10)
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
            scripts = self.view_stack[-1][1] if self.view_stack else self.config["scripts"]
            scripts.remove(script)
            self.save_config()
            self.refresh_grid()
        self.root.attributes("-topmost", True)

    def add_script_dialog(self):
        self.root.attributes("-topmost", False)
        
        # Simple choice dialog
        choice_dialog = tk.Toplevel(self.root)
        choice_dialog.title("Add New")
        choice_dialog.geometry("250x150")
        choice_dialog.configure(bg="#1d2027")
        choice_dialog.attributes("-topmost", True)
        
        # Center choice dialog
        cx = (choice_dialog.winfo_screenwidth() // 2) - 125
        cy = (choice_dialog.winfo_screenheight() // 2) - 75
        choice_dialog.geometry(f"+{cx}+{cy}")

        tk.Label(choice_dialog, text="What to add?", fg="white", bg="#1d2027", font=(self.main_font, 10, "bold")).pack(pady=10)
        
        def start_add(t):
            choice_dialog.destroy()
            if t == "folder":
                name = simpledialog.askstring("Add Folder", "Enter folder name:", parent=self.root)
                if name:
                    scripts = self.view_stack[-1][1] if self.view_stack else self.config["scripts"]
                    scripts.append({"name": name, "type": "folder", "scripts": []})
                    self.save_config()
                    self.refresh_grid()
            else:
                name = simpledialog.askstring("Add Script", "Enter button label:", parent=self.root)
                if name:
                    path = filedialog.askopenfilename(title="Select Script or Executable", parent=self.root)
                    if path:
                        scripts = self.view_stack[-1][1] if self.view_stack else self.config["scripts"]
                        scripts.append({"name": name, "path": path, "type": "script"})
                        self.save_config()
                        self.refresh_grid()
            self.root.attributes("-topmost", True)

        ctk.CTkButton(choice_dialog, text="📄 Script", width=100, command=lambda: start_add("script")).pack(side="left", padx=20)
        ctk.CTkButton(choice_dialog, text="📁 Folder", width=100, command=lambda: start_add("folder")).pack(side="right", padx=20)

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
