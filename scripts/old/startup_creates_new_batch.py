import tkinter as tk
from tkinter import messagebox
import os
import shutil
import winshell

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Startup Manager")
        self.geometry("400x300")
        self.items = [
            {"type": "App", "name": "Ditto", "path": "C:\\ProgramData\\Radarr\\bin\\Radarr.exe"},
            {"type": "App", "name": "AnotherApp", "path": "C:\\path\\to\\AnotherApp.exe"},
            {"type": "Command", "name": "Echo Hello", "command": "echo Hello"},
            {"type": "Command", "name": "Dir C", "command": "start C:\\Users\\nahid\\OneDrive\\Desktop\\songlist.dpl"},
            # Add more items in the same format if needed
        ]
        self.create_widgets()

    def create_widgets(self):
        for item in self.items:
            frame = tk.Frame(self)
            frame.pack(fill=tk.X)

            label = tk.Label(frame, text=item["name"])
            label.pack(side=tk.LEFT)

            checkbox_var = tk.BooleanVar()
            checkbox = tk.Checkbutton(frame, variable=checkbox_var, command=lambda item=item, checkbox_var=checkbox_var, label=label: self.toggle_startup(item, checkbox_var, label))
            checkbox.pack(side=tk.RIGHT)

            # Check if the item is already in startup
            if item["type"] == "App":
                startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{item["name"]}.lnk')
            else:
                startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{item["name"]}.bat')
            checkbox_var.set(os.path.exists(startup_path))

            # Set initial label color based on checkbox state
            self.update_label_color(label, checkbox_var.get())

    def toggle_startup(self, item, checkbox_var, label):
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')

        if checkbox_var.get():
            # Add item to startup
            try:
                if item["type"] == "App":
                    winshell.CreateShortcut(
                        Path=os.path.join(startup_path, f'{item["name"]}.lnk'),
                        Target=item["path"]
                    )
                else:
                    with open(os.path.join(startup_path, f'{item["name"]}.bat'), 'w') as f:
                        f.write(item["command"])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add {item['name']} to startup: {e}")
                checkbox_var.set(False)
        else:
            # Remove item from startup
            try:
                if item["type"] == "App":
                    os.remove(os.path.join(startup_path, f'{item["name"]}.lnk'))
                else:
                    os.remove(os.path.join(startup_path, f'{item["name"]}.bat'))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove {item['name']} from startup: {e}")

        # Update label color based on checkbox state
        self.update_label_color(label, checkbox_var.get())

    def update_label_color(self, label, checked):
        if checked:
            label.config(fg="green")
        else:
            label.config(fg="red")

if __name__ == "__main__":
    app = StartupManager()
    app.mainloop()
