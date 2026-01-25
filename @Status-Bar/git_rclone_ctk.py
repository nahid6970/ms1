import os
import json
import subprocess
import threading
import time
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "projects_config.json")
LOG_DIR = os.path.join(os.path.expanduser("~"), "script_output", "rclone")

# Theme Colors (Cyberpunkish)
BG_COLOR = "#0D0D0D"
CARD_COLOR = "#1A1A1A"
TEXT_COLOR = "#E0E0E0"
CYAN = "#00F0FF"
RED = "#FF003C"
GREEN = "#00FF21"
YELLOW = "#FCEE0A"

os.makedirs(LOG_DIR, exist_ok=True)

def resolve_path(path):
    """Resolve relative paths relative to SCRIPT_DIR."""
    if not path:
        return ""
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(SCRIPT_DIR, path))

def get_relative_path(path):
    """Try to get a relative path relative to SCRIPT_DIR."""
    try:
        rel = os.path.relpath(path, SCRIPT_DIR)
        if ".." in rel and len(rel.split("..")) > 2: # Don't go too far up
            return path
        return rel
    except:
        return path

class ProjectItem(ctk.CTkFrame):
    def __init__(self, master, project, p_type, on_delete, **kwargs):
        super().__init__(master, fg_color=CARD_COLOR, corner_radius=8, **kwargs)
        self.project = project
        self.p_type = p_type
        self.on_delete = on_delete
        self.path = resolve_path(project.get("path", ""))
        
        self.columnconfigure(1, weight=1)
        
        # Status indicator
        self.status_dot = ctk.CTkLabel(self, text="●", text_color="gray", font=("Arial", 20))
        self.status_dot.grid(row=0, column=0, padx=(10, 5), pady=5)
        
        # Label/Name
        label_text = project.get("label") or project.get("name")
        self.name_label = ctk.CTkLabel(self, text=label_text, font=("JetBrainsMono NFP", 14, "bold"), text_color=TEXT_COLOR)
        self.name_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=0, column=2, padx=10, pady=5)
        
        if self.p_type == "git":
            self.action_btn = ctk.CTkButton(self.btn_frame, text="GIT", width=60, height=24, fg_color="#333", hover_color=CYAN, command=self.run_git_action)
            self.action_btn.pack(side="left", padx=2)
        else:
            self.action_btn = ctk.CTkButton(self.btn_frame, text="SYNC", width=60, height=24, fg_color="#333", hover_color=GREEN, command=self.run_rclone_sync)
            self.action_btn.pack(side="left", padx=2)
            
        self.del_btn = ctk.CTkButton(self.btn_frame, text="×", width=30, height=24, fg_color="transparent", text_color=RED, hover_color="#300", command=lambda: self.on_delete(self))
        self.del_btn.pack(side="left", padx=2)
        
        # Tooltip-like behavior on click
        self.bind("<Button-1>", self.on_click)
        self.name_label.bind("<Button-1>", self.on_click)
        
        self.start_check()

    def on_click(self, event):
        # Ctrl + Click to open folder
        if event.state & 0x0004: # Control
            if os.path.exists(self.path):
                subprocess.Popen(f'explorer "{self.path}"', shell=True)
            return
            
        if self.p_type == "rclone":
            # Show log
            log_path = os.path.join(LOG_DIR, f"{self.project['name']}_check.log")
            if os.path.exists(log_path):
                subprocess.Popen(["powershell", "-NoExit", "-Command", f'edit "{log_path}"'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                messagebox.showinfo("Log", f"Log file not found at {log_path}")

    def run_git_action(self):
        # Open terminal for git status / gitter
        subprocess.Popen(f'start pwsh -NoExit -Command "cd \'{self.path}\' ; git status"', shell=True)

    def run_rclone_sync(self):
        # Check for Ctrl for reverse sync?
        # For simplicity, just run a sync push in a new window
        src = self.path
        dst = self.project.get("dst")
        cmd = self.project.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO")
        actual_cmd = cmd.replace("src", f'"{src}"').replace("dst", f'"{dst}"').replace("\\", "/") # Ensure forward slashes for rclone
        subprocess.Popen(f'start pwsh -NoExit -Command "{actual_cmd}"', shell=True)

    def start_check(self):
        threading.Thread(target=self.check_status, daemon=True).start()

    def check_status(self):
        while True:
            color = "gray"
            try:
                if self.p_type == "git":
                    if os.path.exists(self.path):
                        res = subprocess.run(["git", "status"], cwd=self.path, capture_output=True, text=True)
                        if "nothing to commit, working tree clean" in res.stdout:
                            color = GREEN
                        else:
                            color = RED
                else: # rclone
                    src = self.path
                    dst = self.project.get("dst")
                    pattern = self.project.get("cmd", "rclone check src dst --fast-list --size-only")
                    actual_cmd = pattern.replace("src", f'"{src}"').replace("dst", f'"{dst}"').replace("\\", "/") # Ensure forward slashes for rclone
                    log_file = os.path.join(LOG_DIR, f"{self.project['name']}_check.log")
                    with open(log_file, "w") as f:
                        res = subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
                    with open(log_file, "r") as f:
                        content = f.read()
                    if "ERROR" not in content and res.returncode == 0:
                        color = GREEN
                    else:
                        color = RED
            except Exception as e:
                print(f"Error checking status: {e}") # Log the error for debugging
                color = RED
            
            self.status_dot.configure(text_color=color)
            time.sleep(300) # Check every 5 mins

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Git & Rclone Manager")
        self.geometry("600x800")
        self.configure(fg_color=BG_COLOR)
        
        self.projects = {"git": [], "rclone": []}
        self.load_config()
        
        self.setup_ui()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.projects = json.load(f)

    def save_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.projects, f, indent=4)

    def setup_ui(self):
        # Header
        self.header = ctk.CTkLabel(self, text="PROJECT MONITOR", font=("JetBrainsMono NFP", 24, "bold"), text_color=CYAN)
        self.header.pack(pady=20)
        
        # Tabs or Scrollable areas
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.refresh_ui()
        
        # Footer Buttons
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=20, pady=20)
        
        self.add_git_btn = ctk.CTkButton(self.footer, text="+ GIT", fg_color=CARD_COLOR, hover_color=CYAN, command=lambda: self.add_dialog("git"))
        self.add_git_btn.pack(side="left", expand=True, padx=5)
        
        self.add_rclone_btn = ctk.CTkButton(self.footer, text="+ RCLONE", fg_color=CARD_COLOR, hover_color=GREEN, command=lambda: self.add_dialog("rclone"))
        self.add_rclone_btn.pack(side="left", expand=True, padx=5)

    def refresh_ui(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        # Git Section
        ctk.CTkLabel(self.scroll_frame, text="GIT REPOSITORIES", font=("Arial", 12, "bold"), text_color=YELLOW).pack(anchor="w", pady=(10, 5))
        for p in self.projects.get("git", []):
            ProjectItem(self.scroll_frame, p, "git", self.delete_project).pack(fill="x", pady=2)
            
        # Rclone Section
        ctk.CTkLabel(self.scroll_frame, text="RCLONE TASKS", font=("Arial", 12, "bold"), text_color=YELLOW).pack(anchor="w", pady=(20, 5))
        for p in self.projects.get("rclone", []):
            ProjectItem(self.scroll_frame, p, "rclone", self.delete_project).pack(fill="x", pady=2)

    def delete_project(self, item_widget):
        if messagebox.askyesno("Confirm", f"Delete {item_widget.project['name']}?"):
            self.projects[item_widget.p_type].remove(item_widget.project)
            self.save_config()
            self.refresh_ui()

    def add_dialog(self, p_type):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Add {p_type.upper()}")
        dialog.geometry("400x500")
        dialog.focus_set()
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=f"New {p_type} Project", font=("Arial", 16, "bold")).pack(pady=10)
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Name")
        name_entry.pack(fill="x", padx=20, pady=5)
        
        label_entry = ctk.CTkEntry(dialog, placeholder_text="UI Label (optional)")
        label_entry.pack(fill="x", padx=20, pady=5)
        
        path_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=5)
        path_entry = ctk.CTkEntry(path_frame, placeholder_text="Local Path")
        path_entry.pack(side="left", fill="x", expand=True)
        
        def browse():
            p = filedialog.askdirectory()
            if p:
                path_entry.delete(0, "end")
                path_entry.insert(0, p)
        
        ctk.CTkButton(path_frame, text="...", width=30, command=browse).pack(side="right", padx=5)
        
        dst_entry = None
        if p_type == "rclone":
            dst_entry = ctk.CTkEntry(dialog, placeholder_text="Remote Path (e.g. gu:/backups)")
            dst_entry.pack(fill="x", padx=20, pady=5)
            
        def save():
            name = name_entry.get()
            path = path_entry.get()
            if not name or not path:
                return
            
            # Convert to relative if possible
            path = get_relative_path(path)
            
            new_item = {
                "name": name,
                "path": path,
                "label": label_entry.get() or name
            }
            if p_type == "rclone":
                new_item["dst"] = dst_entry.get()
                new_item["cmd"] = "rclone check src dst --fast-list --size-only"
            
            self.projects[p_type].append(new_item)
            self.save_config()
            self.refresh_ui()
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="ADD PROJECT", command=save, fg_color=GREEN if p_type == "rclone" else CYAN, text_color="black").pack(pady=20)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
