
import tkinter as tk
from tkinter import messagebox
import os
import winshell

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Startup Manager")
        self.geometry("200x550")
        # self.configure(bg="#2c3235")

        self.items = [

            {"type": "App","name": "\uf444 Capture2Text","path": "C:\\Users\\nahid\\scoop\\apps\\capture2text\\current\\Capture2Text.exe"},
            {"type": "App","name": "\uf444 rssguard","path": "C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\rssguard.exe"},
            {"type": "App","name": "\uf444 DesktopCoral","path": "C:\\Program Files (x86)\\DesktopCoral\\DesktopCoral.exe"},
            {"type": "App","name": "\uf444 Ditto"       ,"path": "C:\\Users\\nahid\\scoop\\apps\\ditto\\current\\Ditto.exe"},

            {"type": "App","name": "\uf4c3 Prowlarr"    ,"path": "C:\\ProgramData\\Prowlarr\\bin\\Prowlarr.exe"},
            {"type": "App","name": "\uf4c3 Radarr"      ,"path": "C:\\ProgramData\\Radarr\\bin\\Radarr.exe"},
            {"type": "App","name": "\uf4c3 Sonarr"      ,"path": "C:\\ProgramData\\Sonarr\\bin\\Sonarr.exe"},

            {"type": "Command","name": "\uf445 ahkscript"     ,"command": "Start-Process 'C:\\ms1\\ahkscripts.ahk'"},
            {"type": "Command","name": "\uf445 arr_monitor"   ,"command": "Start-Process 'C:\\ms1\\scripts\\arr\\arr_monitor.ps1' -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 bazarr"        ,"command": "Start-Process -FilePath 'C:\\ProgramData\\Bazarr\\WinPython\\python-3.10.0\\python.exe' -ArgumentList 'C:\\ProgramData\\Bazarr\\bazarr.py' -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 flaresolver"   ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\flaresolverr\\current\\flaresolverr.exe' -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 monitor_size"  ,"command": "Start-Process 'powershell.exe' -ArgumentList '-File C:\\ms1\\scripts\\monitor_size.ps1' -Verb RunAs -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 mypygui"       ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\mypygui.py' -Verb RunAs -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 sync"          ,"command": "Start-Process 'C:\\ms1\\scripts\\sync.ps1'"},
            {"type": "Command","name": "\uf445 syncthing"     ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\syncthing\\current\\syncthing.exe' -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 ValoQbit"      ,"command": "Start-Process 'C:\\ms1\\scripts\\valorant\\valo_qbit.ps1' -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 Glaze_WM"      ,"command": "Start-Process 'glazewm.exe' -WindowStyle hidden"},
            {"type": "Command","name": "\uf445 whkd"          ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe' -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 yasb"          ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\yasb\\main.py' -WindowStyle Hidden"},
            {"type": "Command","name": "\uf445 komorebic"     ,"command": "komorebic start"},
            # Add more items in the same format if needed
        ]


        self.ps1_file_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', 'startup_commands.ps1')
        self.create_ps1_file()
        self.create_widgets()

    def create_ps1_file(self):
        if not os.path.exists(self.ps1_file_path):
            with open(self.ps1_file_path, 'w') as f:
                f.write('# PowerShell script for startup\n')

    def create_widgets(self):
        for item in self.items:
            frame = tk.Frame(self, bg="#fff")
            frame.pack(fill=tk.X)

            label = tk.Label(frame, text=item["name"], font=("jetbrainsmono nfp", 12, "bold"),bg="#fff" )

            checkbox_var = tk.BooleanVar()
            checkbox = tk.Checkbutton(frame, variable=checkbox_var, command=lambda item=item, checkbox_var=checkbox_var, label=label: self.toggle_startup(item, checkbox_var, label))

            checkbox.pack(side=tk.LEFT)
            label.pack(side=tk.LEFT)

            # Check if the item is already in startup
            if item["type"] == "App":
                startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{item["name"]}.lnk')
                checkbox_var.set(os.path.exists(startup_path))
            else:
                startup_path = self.ps1_file_path
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
                    with open(self.ps1_file_path, 'a') as f:
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
                    with open(self.ps1_file_path, 'r') as f:
                        lines = f.readlines()
                    with open(self.ps1_file_path, 'w') as f:
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
