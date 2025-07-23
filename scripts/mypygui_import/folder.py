import subprocess
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Dragging data
drag_data = {"x": 0, "y": 0}

# Utility Functions
def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def stop_drag(event):
    drag_data["x"] = None
    drag_data["y"] = None

def do_drag(event):
    if drag_data["x"] is not None and drag_data["y"] is not None:
        x = event.x - drag_data["x"] + root.winfo_x()
        y = event.y - drag_data["y"] + root.winfo_y()
        root.geometry(f"+{x}+{y}")

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# Main App Class
class FolderLauncherApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_title_bar()
        self.create_main_frame()
        self.populate_folders()

    def setup_window(self):
        self.root.title("Folder Launcher")
        self.root.geometry("700x700")
        self.root.configure(bg="#282c34")
        self.root.overrideredirect(True)
        self.root.bind("<ButtonPress-1>", start_drag)
        self.root.bind("<ButtonRelease-1>", stop_drag)
        self.root.bind("<B1-Motion>", do_drag)

    def create_title_bar(self):
        title_bar = tk.Frame(self.root, bg="#1d2027", height=30)
        title_bar.pack(fill="x")

        close_btn = tk.Label(title_bar, text="✕", bg="#1d2027", fg="red", font=("Arial", 14, "bold"), cursor="hand2")
        close_btn.pack(side="right", padx=5, pady=2)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg="#1D2027")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.scroll_canvas = tk.Canvas(self.main_frame, bg="#1D2027", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollable_frame = tk.Frame(self.scroll_canvas, bg="#1D2027")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )

        self.scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def populate_folders(self):
        items = [
            ("#204892", "#ffffff", "\uf07c AppData", {"command": "explorer C:\\Users\\nahid\\AppData"}),
            ("#204892", "#ffffff", "\uf07c AppsFolder", {"command": "explorer shell:AppsFolder"}),
            ("#204892", "#ffffff", "\uf07c Packages", {"command": "explorer C:\\Users\\nahid\\AppData\\Local\\Packages"}),
            ("#33405a", "#ffffff", "\uf07c ProgramData", {"command": "explorer C:\\ProgramData"}),
            ("#33405a", "#ffffff", "\uf07c Python Lib", {"command": "explorer C:\\Users\\nahid\\scoop\\apps\\python\\current\\Lib"}),
            ("#204892", "#ffffff", "\uf07c Scoop", {"command": "explorer C:\\Users\\nahid\\scoop"}),
            ("#204892", "#ffffff", "\uf07c Software", {"command": "explorer D:\\software"}),
            ("#204892", "#ffffff", "\uf07c Song", {"command": "explorer D:\\song"}),
            ("#204892", "#ffffff", "\uf07c Startup-System", {"command": "explorer C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"}),
            ("#204892", "#ffffff", "\uf07c Startup-User", {"command": "explorer C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"}),
            ("#204892", "#ffffff", "\uf07c Temp-AppDate", {"command": "explorer C:\\Users\\nahid\\AppData\\Local\\Temp"}),
            ("#204892", "#ffffff", "\uf07c Temp-Windows", {"command": "explorer C:\\Windows\\Temp"}),
            ("#204892", "#ffffff", "\uf07c WindowsApp", {"command": "explorer C:\\Program Files\\WindowsApps"}),
            ("#204892", "#ffffff", "\uf07c Send To", {"command": "explorer C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\SendTo"}),
            ("#204892", "#ffffff", "\uf07c Host", {"command": "explorer C:\\Windows\\System32\\drivers\\etc"}),
            ("#204892", "#ffffff", "\uf07c PowerToys New+", {"command": "explorer C:\\Users\\nahid\\AppData\\Local\\Microsoft\\PowerToys\\NewPlus\\Templates"}),
            ("#d63a13", "#ffffff", "\uf07c Registry Run", {'command': 'sudo C:\\Users\\nahid\\OneDrive\\backup\\sysinternals\\regjump.exe HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'}),
        ]

        items.sort(key=lambda x: x[2])  # Sort alphabetically by label

        columns = 3
        rows_per_column = 15

        for index, (bg, fg, text, cmd_dict) in enumerate(items):
            row = index % rows_per_column
            col = index // rows_per_column

            label = tk.Label(
                self.scrollable_frame,
                text=text,
                font=("JetBrainsMono NFP", 12, "bold"),
                bg=bg,
                fg=fg,
                padx=10,
                pady=5,
                cursor="hand2"
            )
            label.grid(row=row, column=col, sticky="w", padx=5, pady=2)

            label.bind("<Button-1>", lambda e, cmd=cmd_dict["command"], l=label, bg=bg, fg=fg: self.on_click(e, cmd, l, bg, fg))

    def on_click(self, event, command, label, bg, fg):
        label.config(bg="#ffffff", fg="#204892")
        try:
            subprocess.Popen(command, shell=True)
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to execute: {ex}")
        self.root.after(100, lambda: label.config(bg=bg, fg=fg))


# Run Application
if __name__ == "__main__":
    root = tk.Tk()
    app = FolderLauncherApp(root)
    center_window(root)
    root.mainloop()