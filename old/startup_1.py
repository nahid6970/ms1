import tkinter as tk
from tkinter import messagebox
import os
import shutil
import winshell

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Startup Manager")
        self.geometry("400x200")
        self.apps = [
            {"name": "Ditto", "path": "C:\\Users\\nahid\\scoop\\apps\\ditto\\current\\Ditto.exe"},
            {"name": "Radarr", "path": "C:\\ProgramData\\Radarr\\bin\\Radarr.exe"},
            # Add more apps in the same format if needed
        ]
        self.create_widgets()

    def create_widgets(self):
        for app in self.apps:
            frame = tk.Frame(self)
            frame.pack(fill=tk.X)

            label = tk.Label(frame, text=app["name"])
            label.pack(side=tk.LEFT)

            checkbox_var = tk.BooleanVar()
            checkbox = tk.Checkbutton(frame, variable=checkbox_var, command=lambda app=app, checkbox_var=checkbox_var, label=label: self.toggle_startup(app, checkbox_var, label))
            checkbox.pack(side=tk.LEFT)

            # Check if the app is already in startup
            startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{app["name"]}.lnk')
            checkbox_var.set(os.path.exists(startup_path))

            # Set initial label color based on checkbox state
            self.update_label_color(label, checkbox_var.get())

    def toggle_startup(self, app, checkbox_var, label):
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{app["name"]}.lnk')

        if checkbox_var.get():
            # Add app to startup
            try:
                winshell.CreateShortcut(
                    Path=os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{app["name"]}.lnk'),
                    Target=app["path"]
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add {app['name']} to startup: {e}")
                checkbox_var.set(False)
        else:
            # Remove app from startup
            try:
                os.remove(startup_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove {app['name']} from startup: {e}")

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
