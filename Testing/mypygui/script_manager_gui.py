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
        "danger_color": "#fe1616"
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
        self.width = 900
        self.height = 500
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

        # TOP SECTION: Status Widgets
        self.status_container = tk.Frame(self.main_content, bg="#1d2027")
        self.status_container.pack(fill="x", pady=(0, 15))

        # GitHub Widget
        self.github_widget = tk.LabelFrame(
            self.status_container, text=" GitHub Status ", 
            labelanchor="nw", fg="#888888", bg="#1d2027",
            font=(self.main_font, 8, "bold"), bd=1, relief="flat", highlightthickness=1, highlightbackground="#333333"
        )
        self.github_widget.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.github_inner = tk.Frame(self.github_widget, bg="#1d2027")
        self.github_inner.pack(padx=10, pady=5)

        for repo in self.config["github_repos"]:
            r_frame = tk.Frame(self.github_inner, bg="#1d2027")
            r_frame.pack(side="left", padx=10)
            
            indicator = tk.Canvas(r_frame, width=10, height=10, bg="#1d2027", highlightthickness=0)
            indicator.pack(side="left", padx=(0, 5))
            circle = indicator.create_oval(2, 2, 8, 8, fill="#555555")
            
            lbl = tk.Label(r_frame, text=repo["name"], fg="white", bg="#1d2027", font=(self.main_font, 9))
            lbl.pack(side="left")
            
            self.repo_labels[repo["name"]] = {"lbl": lbl, "indicator": indicator, "circle": circle}

        # Rclone Widget
        self.rclone_widget = tk.LabelFrame(
            self.status_container, text=" Drive / Folder Status ", 
            labelanchor="nw", fg="#888888", bg="#1d2027",
            font=(self.main_font, 8, "bold"), bd=1, relief="flat", highlightthickness=1, highlightbackground="#333333"
        )
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
            
            # Click events
            lbl.bind("<Button-1>", lambda e, f=folder: self.on_rclone_click(e, f))
            lbl.bind("<Control-Button-1>", lambda e, f=folder: self.on_rclone_sync(e, f, "left"))
            lbl.bind("<Control-Button-3>", lambda e, f=folder: self.on_rclone_sync(e, f, "right"))
            
            self.folder_labels[folder["name"]] = {"lbl": lbl, "indicator": indicator, "circle": circle}

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
            
            btn = ctk.CTkButton(
                self.grid_frame, 
                text=script["name"],
                width=160, height=45, corner_radius=4,
                fg_color="#2b2f38", hover_color=self.config["settings"]["accent_color"],
                text_color="white",
                font=(self.main_font, 10),
                command=lambda p=script["path"]: self.launch_script(p)
            )
            btn.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            
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
        menu.add_command(label=f"Remove '{script['name']}'", command=lambda: self.remove_script(script))
        menu.post(event.x_root, event.y_root)

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
        dialog.geometry("300x200")
        dialog.configure(bg="#1d2027")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Buttons per Row:", fg="white", bg="#1d2027", font=(self.main_font, 10)).pack(pady=10)
        
        val_var = tk.StringVar(value=str(self.config["settings"]["columns"]))
        entry = tk.Entry(dialog, textvariable=val_var, width=10, justify="center")
        entry.pack()

        def save():
            try:
                n = int(val_var.get())
                if 1 <= n <= 10:
                    self.config["settings"]["columns"] = n
                    self.save_config()
                    self.refresh_grid()
                    dialog.destroy()
                    self.root.attributes("-topmost", True)
                else:
                    messagebox.showwarning("Invalid", "Please enter a number between 1 and 10", parent=dialog)
            except:
                messagebox.showerror("Error", "Please enter a valid number", parent=dialog)

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

    def status_monitor_thread(self):
        log_dir = r"C:\Users\nahid\script_output\rclone"
        os.makedirs(log_dir, exist_ok=True)

        while not self.stop_threads:
            # GitHub Check
            for repo in self.config["github_repos"]:
                # ... (keep existing github logic)
                path = repo["path"]
                status = "unknown"
                if os.path.exists(path):
                    try:
                        if os.path.isdir(os.path.join(path, ".git")):
                            res = subprocess.run(["git", "status", "--porcelain"], cwd=path, capture_output=True, text=True, timeout=3)
                            status = "clean" if not res.stdout.strip() else "dirty"
                        else: status = "no_git"
                    except: status = "error"
                else: status = "missing"
                self.root.after(0, lambda name=repo["name"], s=status: self.update_repo_status_ui(name, s))

            # Rclone Check (using 'rclone check' as in mypygui.py)
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

            time.sleep(600) # Update every 10 minutes as in mypygui.py

    def update_repo_status_ui(self, name, status):
        if name in self.repo_labels:
            ui = self.repo_labels[name]
            color = "#555555"
            if status == "clean": color = self.config["settings"]["success_color"]
            elif status == "dirty": color = "#ffcc00"
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
