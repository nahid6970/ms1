import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import time
from pathlib import Path
import pystray
from PIL import Image, ImageDraw
from datetime import datetime

class RcloneTrayManager:
    def __init__(self):
        self.config_file = "rclone_tray_config.json"
        self.config = self.load_config()
        self.root = None
        self.tray_icon = None
        self.labels = {}
        self.timers = {}
        self.running = True
        
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "settings": {
                "minimize_to_tray": True,
                "log_directory": "C:/Users/nahid/script_output/rclone"
            },
            "projects": []
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        return default_config
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, indent=4, fp=f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def create_tray_icon(self):
        """Create system tray icon"""
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color='#1d2027')
        dc = ImageDraw.Draw(image)
        dc.rectangle([16, 16, 48, 48], fill='#06de22')
        
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Settings", self.open_settings),
            pystray.MenuItem("Exit", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("rclone_manager", image, "Rclone Manager", menu)
    
    def show_window(self, icon=None, item=None):
        """Show the main window"""
        if self.root:
            self.root.deiconify()
            self.root.lift()
    
    def hide_window(self):
        """Hide window to tray"""
        if self.config["settings"]["minimize_to_tray"]:
            self.root.withdraw()
        else:
            self.root.iconify()
    
    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        if self.root:
            self.root.quit()
    
    def run_command(self, cmd):
        """Run rclone command in a new PowerShell window"""
        try:
            subprocess.Popen(
                ["powershell", "-NoExit", "-Command", cmd],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        except Exception as e:
            print(f"Error running command: {e}")
    
    def on_label_click(self, event, project):
        """Open log file when label is clicked"""
        try:
            log_file = project["log"]
            subprocess.Popen([
                "powershell", "-NoExit", "-Command", f'edit "{log_file}"'
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            print(f"Error opening log file: {e}")
    
    def ctrl_left_click(self, event, project):
        """Ctrl+Left Click: Sync src to dst"""
        if event.state & 0x0004:  # Ctrl key mask
            cmd = project.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
            actual_cmd = cmd.replace("src", project["src"]).replace("dst", project["dst"])
            self.run_command(actual_cmd)
            # Reset timer if auto-sync is enabled
            if project.get("auto_sync_enabled", False):
                self.schedule_auto_sync(project)
    
    def ctrl_right_click(self, event, project):
        """Ctrl+Right Click: Sync dst to src"""
        if event.state & 0x0004:  # Ctrl key mask
            cmd = project.get("right_click_cmd", "rclone sync dst src -P --fast-list")
            actual_cmd = cmd.replace("src", project["src"]).replace("dst", project["dst"])
            self.run_command(actual_cmd)

    def check_and_update(self, label, project):
        """Periodically check rclone status"""
        def run_check():
            while self.running:
                try:
                    log_dir = self.config["settings"]["log_directory"]
                    os.makedirs(log_dir, exist_ok=True)
                    
                    actual_cmd = project["cmd"].replace("src", project["src"]).replace("dst", project["dst"])
                    with open(project["log"], "w") as f:
                        subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
                    
                    with open(project["log"], "r") as f:
                        content = f.read()
                    
                    if "ERROR" not in content:
                        label.config(fg="#06de22")
                    else:
                        label.config(fg="red")
                except Exception as e:
                    print(f"Error checking {project['name']}: {e}")
                    label.config(fg="orange")
                
                # Wait for check interval (default 10 minutes)
                check_interval = project.get("check_interval", 600)
                time.sleep(check_interval)
        
        threading.Thread(target=run_check, daemon=True).start()
    
    def auto_sync_task(self, project):
        """Auto-sync task that runs periodically"""
        while self.running and project.get("auto_sync_enabled", False):
            interval = project.get("auto_sync_interval", 3600)  # Default 1 hour
            time.sleep(interval)
            
            if project.get("auto_sync_enabled", False):
                cmd = project.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
                actual_cmd = cmd.replace("src", project["src"]).replace("dst", project["dst"])
                self.run_command(actual_cmd)
                print(f"Auto-sync executed for {project['name']} at {datetime.now()}")
    
    def schedule_auto_sync(self, project):
        """Schedule or reschedule auto-sync for a project"""
        project_id = project["name"]
        
        # Stop existing timer if any
        if project_id in self.timers:
            # Timer will stop when auto_sync_enabled is False
            project["auto_sync_enabled"] = False
            time.sleep(0.1)
        
        # Start new timer if enabled
        if project.get("auto_sync_enabled", False):
            timer_thread = threading.Thread(target=self.auto_sync_task, args=(project,), daemon=True)
            timer_thread.start()
            self.timers[project_id] = timer_thread

    def create_gui(self):
        """Create the main GUI"""
        self.root = tk.Tk()
        self.root.title("Rclone Manager")
        self.root.configure(bg="#1d2027")
        self.root.geometry("800x400")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#1d2027")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(
            main_frame,
            text="Rclone Manager",
            bg="#1d2027",
            fg="#06de22",
            font=("JetBrainsMono NFP", 20, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Rclone section
        rclone_frame = tk.LabelFrame(
            main_frame,
            text="Rclone Projects",
            bg="#1d2027",
            fg="#06de22",
            font=("JetBrainsMono NFP", 14, "bold")
        )
        rclone_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Rclone projects container
        rclone_container = tk.Frame(rclone_frame, bg="#1d2027")
        rclone_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create labels for each project
        for project in self.config["projects"]:
            lbl = tk.Label(
                rclone_container,
                text=project.get("label", project["name"]),
                bg="#1d2027",
                fg="#06de22",
                font=("JetBrainsMono NFP", 16, "bold"),
                cursor="hand2"
            )
            lbl.pack(side="left", padx=5)
            
            # Event bindings
            lbl.bind("<Button-1>", lambda e, p=project: self.on_label_click(e, p))
            lbl.bind("<Control-Button-1>", lambda e, p=project: self.ctrl_left_click(e, p))
            lbl.bind("<Control-Button-3>", lambda e, p=project: self.ctrl_right_click(e, p))
            
            self.labels[project["name"]] = lbl
            
            # Start status checking
            self.check_and_update(lbl, project)
            
            # Start auto-sync if enabled
            if project.get("auto_sync_enabled", False):
                self.schedule_auto_sync(project)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#1d2027")
        button_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(
            button_frame,
            text="Add Project",
            command=self.add_project_dialog,
            bg="#06de22",
            fg="#1d2027",
            font=("JetBrainsMono NFP", 12, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Settings",
            command=self.open_settings,
            bg="#06de22",
            fg="#1d2027",
            font=("JetBrainsMono NFP", 12, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Manage Projects",
            command=self.manage_projects_dialog,
            bg="#06de22",
            fg="#1d2027",
            font=("JetBrainsMono NFP", 12, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=5)

    def add_project_dialog(self):
        """Dialog to add a new project"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Rclone Project")
        dialog.configure(bg="#1d2027")
        dialog.geometry("600x700")
        
        fields = {}
        
        # Project Name
        tk.Label(dialog, text="Project Name:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["name"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["name"].pack(pady=5)
        
        # Label
        tk.Label(dialog, text="Display Label:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["label"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["label"].pack(pady=5)
        
        # Source
        tk.Label(dialog, text="Source Path:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["src"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["src"].pack(pady=5)
        
        # Destination
        tk.Label(dialog, text="Destination Path:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["dst"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["dst"].pack(pady=5)
        
        # Check Command
        tk.Label(dialog, text="Check Command:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["cmd"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["cmd"].insert(0, "rclone check src dst --fast-list --size-only")
        fields["cmd"].pack(pady=5)
        
        # Left Click Command
        tk.Label(dialog, text="Sync Command (Ctrl+Left):", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["left_click_cmd"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["left_click_cmd"].insert(0, "rclone sync src dst -P --fast-list --log-level INFO")
        fields["left_click_cmd"].pack(pady=5)
        
        # Right Click Command
        tk.Label(dialog, text="Reverse Sync (Ctrl+Right):", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["right_click_cmd"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["right_click_cmd"].insert(0, "rclone sync dst src -P --fast-list")
        fields["right_click_cmd"].pack(pady=5)
        
        # Auto-sync enabled
        auto_sync_var = tk.BooleanVar()
        tk.Checkbutton(
            dialog,
            text="Enable Auto-Sync",
            variable=auto_sync_var,
            bg="#1d2027",
            fg="#06de22",
            selectcolor="#1d2027",
            font=("JetBrainsMono NFP", 12)
        ).pack(pady=5)
        
        # Auto-sync interval
        tk.Label(dialog, text="Auto-Sync Interval (seconds):", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["auto_sync_interval"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["auto_sync_interval"].insert(0, "3600")
        fields["auto_sync_interval"].pack(pady=5)
        
        def save_project():
            log_dir = self.config["settings"]["log_directory"]
            project = {
                "name": fields["name"].get(),
                "label": fields["label"].get() or fields["name"].get(),
                "src": fields["src"].get(),
                "dst": fields["dst"].get(),
                "cmd": fields["cmd"].get(),
                "left_click_cmd": fields["left_click_cmd"].get(),
                "right_click_cmd": fields["right_click_cmd"].get(),
                "log": f"{log_dir}/{fields['name'].get()}_check.log",
                "auto_sync_enabled": auto_sync_var.get(),
                "auto_sync_interval": int(fields["auto_sync_interval"].get()),
                "check_interval": 600
            }
            
            self.config["projects"].append(project)
            self.save_config()
            dialog.destroy()
            messagebox.showinfo("Success", "Project added! Restart the app to see changes.")
        
        tk.Button(
            dialog,
            text="Save",
            command=save_project,
            bg="#06de22",
            fg="#1d2027",
            font=("JetBrainsMono NFP", 12, "bold")
        ).pack(pady=20)

    def manage_projects_dialog(self):
        """Dialog to manage existing projects"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Projects")
        dialog.configure(bg="#1d2027")
        dialog.geometry("700x500")
        
        # Listbox with scrollbar
        frame = tk.Frame(dialog, bg="#1d2027")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(
            frame,
            yscrollcommand=scrollbar.set,
            bg="#2d3037",
            fg="#06de22",
            font=("JetBrainsMono NFP", 12),
            selectmode=tk.SINGLE
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        for project in self.config["projects"]:
            auto_sync_status = "✓" if project.get("auto_sync_enabled", False) else "✗"
            listbox.insert(tk.END, f"{project['name']} | Auto-Sync: {auto_sync_status}")
        
        def edit_project():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a project")
                return
            
            idx = selection[0]
            project = self.config["projects"][idx]
            self.edit_project_dialog(project, idx)
        
        def delete_project():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a project")
                return
            
            idx = selection[0]
            project = self.config["projects"][idx]
            
            if messagebox.askyesno("Confirm", f"Delete project '{project['name']}'?"):
                self.config["projects"].pop(idx)
                self.save_config()
                listbox.delete(idx)
                messagebox.showinfo("Success", "Project deleted! Restart to see changes.")
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="#1d2027")
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Edit",
            command=edit_project,
            bg="#06de22",
            fg="#1d2027",
            font=("JetBrainsMono NFP", 12, "bold")
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="Delete",
            command=delete_project,
            bg="#cc5907",
            fg="#1d2027",
            font=("JetBrainsMono NFP", 12, "bold")
        ).pack(side="left", padx=5)

    def edit_project_dialog(self, project, idx):
        """Dialog to edit an existing project"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Project: {project['name']}")
        dialog.configure(bg="#1d2027")
        dialog.geometry("600x700")
        
        fields = {}
        
        # Project Name (read-only)
        tk.Label(dialog, text="Project Name:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        name_label = tk.Label(dialog, text=project["name"], bg="#1d2027", fg="white", font=("JetBrainsMono NFP", 10))
        name_label.pack(pady=5)
        
        # Label
        tk.Label(dialog, text="Display Label:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["label"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["label"].insert(0, project.get("label", project["name"]))
        fields["label"].pack(pady=5)
        
        # Source
        tk.Label(dialog, text="Source Path:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["src"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["src"].insert(0, project["src"])
        fields["src"].pack(pady=5)
        
        # Destination
        tk.Label(dialog, text="Destination Path:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["dst"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["dst"].insert(0, project["dst"])
        fields["dst"].pack(pady=5)
        
        # Check Command
        tk.Label(dialog, text="Check Command:", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["cmd"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["cmd"].insert(0, project["cmd"])
        fields["cmd"].pack(pady=5)
        
        # Left Click Command
        tk.Label(dialog, text="Sync Command (Ctrl+Left):", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["left_click_cmd"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["left_click_cmd"].insert(0, project.get("left_click_cmd", ""))
        fields["left_click_cmd"].pack(pady=5)
        
        # Right Click Command
        tk.Label(dialog, text="Reverse Sync (Ctrl+Right):", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["right_click_cmd"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["right_click_cmd"].insert(0, project.get("right_click_cmd", ""))
        fields["right_click_cmd"].pack(pady=5)
        
        # Auto-sync enabled
        auto_sync_var = tk.BooleanVar(value=project.get("auto_sync_enabled", False))
        tk.Checkbutton(
            dialog,
            text="Enable Auto-Sync",
            variable=auto_sync_var,
            bg="#1d2027",
            fg="#06de22",
            selectcolor="#1d2027",
            font=("JetBrainsMono NFP", 12)
        ).pack(pady=5)
        
        # Auto-sync interval
        tk.Label(dialog, text="Auto-Sync Interval (seconds):", bg="#1d2027", fg="#06de22", font=("JetBrainsMono NFP", 12)).pack(pady=5)
        fields["auto_sync_interval"] = tk.Entry(dialog, width=50, font=("JetBrainsMono NFP", 10))
        fields["auto_sync_interval"].insert(0, str(project.get("auto_sync_interval", 3600)))
        fields["auto_sync_interval"].pack(pady=5)
        
        def save_changes():
            project["label"] = fields["label"].get()
            project["src"] = fields["src"].get()
            project["dst"] = fields["dst"].get()
            project["cmd"] = fields["cmd"].get()
            project["left_click_cmd"] = fields["left_click_cmd"].get()
            project["right_click_cmd"] = fields["right_click_cmd"].get()
            project["auto_sync_enabled"] = auto_sync_var.get()
            project["auto_sync_interval"] = int(fields["auto_sync_interval"].get())
            
            self.config["projects"][idx] = project
            self.save_config()
            dialog.destroy()
            messagebox.showinfo("Success", "Project updated! Restart to see changes.")
        
        tk.Button(
            dialog,
            text="Save Changes",
            command=save_changes,
            bg="#06de22",
            fg="#1d2027",
            font=("JetBrainsMono NFP", 12, "bold")
        ).pack(pady=20)
