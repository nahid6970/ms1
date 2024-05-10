import tkinter as tk
from tkinter import messagebox
import os
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
            {"type": "Command", "name": "Dir C:\\", "command": "dir C:\\"},
            # Add more items in the same format if needed
        ]
        self.batch_file_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', 'startup_commands.bat')
        self.create_batch_file()
        self.create_widgets()

    def create_batch_file(self):
        if not os.path.exists(self.batch_file_path):
            with open(self.batch_file_path, 'w') as f:
                f.write('@echo off\n')

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
                startup_path = self.batch_file_path
                with open(startup_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if item["command"] in line:
                            checkbox_var.set(True)
                            break
                    else:
                        checkbox_var.set(False)

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
                    with open(self.batch_file_path, 'r') as f:
                        lines = f.readlines()
                    with open(self.batch_file_path, 'a') as f:
                        for line in lines:
                            if item["command"] in line:
                                break
                        else:
                            f.write(f'{item["command"]}\n')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add {item['name']} to startup: {e}")
                checkbox_var.set(False)
        else:
            # Remove item from startup
            try:
                if item["type"] == "App":
                    os.remove(os.path.join(startup_path, f'{item["name"]}.lnk'))
                else:
                    with open(self.batch_file_path, 'r') as f:
                        lines = f.readlines()
                    with open(self.batch_file_path, 'w') as f:
                        for line in lines:
                            if item["command"] in line:
                                continue
                            else:
                                f.write(line)
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
