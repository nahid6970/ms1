
import tkinter as tk
from tkinter import messagebox
import os
import winshell

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Startup Manager")
        self.geometry("200x550")
        self.items = [
            {"type": "App","name": "Capture2Text","path": "C:\\Users\\nahid\\scoop\\apps\\capture2text\\current\\Capture2Text.exe"},
            {"type": "App","name": "rssguard"    ,"path": "C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\rssguard.exe"}        ,
            {"type": "App","name": "DesktopCoral","path": "C:\\Program Files (x86)\\DesktopCoral\\DesktopCoral.exe"}               ,
            {"type": "App","name": "Ditto"       ,"path": "C:\\Users\\nahid\\scoop\\apps\\ditto\\current\\Ditto.exe"}              ,

            {"type": "App","name": "Prowlarr"    ,"path": "C:\\ProgramData\\Prowlarr\\bin\\Prowlarr.exe"},
            {"type": "App","name": "Radarr"      ,"path": "C:\\ProgramData\\Radarr\\bin\\Radarr.exe"},
            {"type": "App","name": "Sonarr"      ,"path": "C:\\ProgramData\\Sonarr\\bin\\Sonarr.exe"},

            {"type": "Command","name": "ahkscript"     ,"command": "Start-Process 'C:\\ms1\\ahkscripts.ahk'"},
            {"type": "Command","name": "arr_monitor"   ,"command": "Start-Process 'C:\\ms1\\arr_monitor.ps1' -WindowStyle Hidden"},
            {"type": "Command","name": "bazarr"        ,"command": "Start-Process -FilePath 'C:\\ProgramData\\Bazarr\\WinPython\\python-3.10.0\\python.exe' -ArgumentList 'C:\\ProgramData\\Bazarr\\bazarr.py' -WindowStyle Hidden"},
            {"type": "Command","name": "flaresolver"   ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\flaresolverr\\current\\flaresolverr.exe' -WindowStyle Hidden"},
            {"type": "Command","name": "monitor_size"  ,"command": "Start-Process 'powershell.exe' -ArgumentList '-File C:\\ms1\\scripts\\monitor_size.ps1' -Verb RunAs -WindowStyle Hidden"},
            {"type": "Command","name": "mypygui"       ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\mypygui.py' -Verb RunAs -WindowStyle Hidden"},
            {"type": "Command","name": "sync"          ,"command": "Start-Process 'C:\\ms1\\sync.ps1'"},
            {"type": "Command","name": "syncthing"     ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\syncthing\\current\\syncthing.exe' -WindowStyle Hidden"},
            {"type": "Command","name": "ValoQbit"      ,"command": "Start-Process 'C:\\ms1\\scripts\\valorant\\valo_qbit.ps1' -WindowStyle Hidden"},
            {"type": "Command","name": "Glaze_WM"      ,"command": "Start-Process 'glazewm.exe' -WindowStyle hidden"},
            {"type": "Command","name": "whkd"          ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe' -WindowStyle Hidden"},
            {"type": "Command","name": "yasb"          ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\yasb\\main.py' -WindowStyle Hidden"},
            {"type": "Command","name": "komorebic"     ,"command": "komorebic start"},
            # Add more items in the same format if needed
        ]
        self.ps1_file_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', 'startup_commands.ps1')
        self.config_file_path = os.path.join(os.getenv('APPDATA'), 'startup_manager_config.txt')
        self.load_config()
        self.create_widgets()

    def load_config(self):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'r') as f:
                for line in f:
                    item_name, state = line.strip().split(':')
                    for item in self.items:
                        if item["name"] == item_name:
                            item["state"] = bool(int(state))

    def save_config(self):
        with open(self.config_file_path, 'w') as f:
            for item in self.items:
                if "state" in item:
                    f.write(f'{item["name"]}:{int(item["state"])}\n')

    def create_widgets(self):
        for item in self.items:
            frame = tk.Frame(self)
            frame.pack(fill=tk.X)

            label = tk.Label(frame, text=item["name"], font=("jetbrainsmono nfp", 12, "bold"))
            label.pack(side=tk.LEFT)

            checkbox_var = tk.BooleanVar(value=item.get("state", False))
            checkbox = tk.Checkbutton(frame, variable=checkbox_var, command=lambda item=item, checkbox_var=checkbox_var, label=label: self.toggle_startup(item, checkbox_var, label))
            checkbox.pack(side=tk.RIGHT)

            if item.get("state", False):
                self.apply_startup(item)

            # Set initial label color based on checkbox state
            self.update_label_color(label, checkbox_var.get())

    def toggle_startup(self, item, checkbox_var, label):
        if checkbox_var.get():
            try:
                self.apply_startup(item)
                item["state"] = True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add {item['name']} to startup: {e}")
                checkbox_var.set(False)
        else:
            try:
                self.remove_startup(item)
                del item["state"]
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove {item['name']} from startup: {e}")

        self.update_label_color(label, checkbox_var.get())
        self.save_config()

    def apply_startup(self, item):
        if item["type"] == "App":
            winshell.CreateShortcut(
                Path=os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{item["name"]}.lnk'),
                Target=item["path"]
            )
        else:
            with open(self.ps1_file_path, 'a') as f:
                f.write(f'{item["command"]}\n')

    def remove_startup(self, item):
        if item["type"] == "App":
            os.remove(os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{item["name"]}.lnk'))
        else:
            with open(self.ps1_file_path, 'r') as f:
                lines = f.readlines()
            with open(self.ps1_file_path, 'w') as f:
                for line in lines:
                    if item["command"] not in line:
                        f.write(line)

    def update_label_color(self, label, checked):
        if checked:
            label.config(fg="green")
        else:
            label.config(fg="red")

    def on_closing(self):
        self.save_config()
        self.destroy()

if __name__ == "__main__":
    app = StartupManager()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
