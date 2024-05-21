import tkinter as tk
from tkinter import messagebox
import os
import winshell

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Startup Manager")
        self.geometry("300x650")
        # self.configure(bg="#2c3235")
        self.items = [
            {"type": "App","name": "Capture2Text","path": "C:\\Users\\nahid\\scoop\\apps\\capture2text\\current\\Capture2Text.exe"},
            # {"type": "App","name": "DesktopCoral","path": "C:\\Program Files (x86)\\DesktopCoral\\DesktopCoral.exe"}               ,
            # {"type": "App","name": "Ditto"       ,"path": "C:\\Users\\nahid\\scoop\\apps\\ditto\\current\\Ditto.exe"}              ,
            # {"type": "App","name": "Prowlarr"    ,"path": "C:\\ProgramData\\Prowlarr\\bin\\Prowlarr.exe"}                          ,
            # {"type": "App","name": "Radarr"      ,"path": "C:\\ProgramData\\Radarr\\bin\\Radarr.exe"}                              ,
            # {"type": "App","name": "RssGuard"    ,"path": "C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\rssguard.exe"}        ,
            # {"type": "App","name": "Sonarr"      ,"path": "C:\\ProgramData\\Sonarr\\bin\\Sonarr.exe"}                              ,
            

            # {"type": "Command","name": "ahkscript"     ,"command": "Start-Process 'C:\\ms1\\ahkscripts.ahk'"},
            # {"type": "Command","name": "arr_monitor"   ,"command": "Start-Process 'C:\\ms1\\arr_monitor.ps1' -WindowStyle Hidden"},
            # {"type": "Command","name": "bazarr"        ,"command": "Start-Process -FilePath 'C:\\ProgramData\\Bazarr\\WinPython\\python-3.10.0\\python.exe' -ArgumentList 'C:\\ProgramData\\Bazarr\\bazarr.py' -WindowStyle Hidden"},
            # {"type": "Command","name": "flaresolver"   ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\flaresolverr\\current\\flaresolverr.exe' -WindowStyle Hidden"},
            # {"type": "Command","name": "Glaze_WM"      ,"command": "Start-Process 'glazewm.exe' -WindowStyle hidden"},
            # {"type": "Command","name": "komorebic"     ,"command": "komorebic start"},
            # {"type": "Command","name": "monitor_size"  ,"command": "Start-Process 'powershell.exe' -ArgumentList '-File C:\\ms1\\scripts\\monitor_size.ps1' -Verb RunAs -WindowStyle Hidden"},
            # {"type": "Command","name": "mypygui"       ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\mypygui.py' -Verb RunAs -WindowStyle Hidden"},
            # {"type": "Command","name": "sync"          ,"command": "Start-Process 'C:\\ms1\\sync.ps1'"},
            # {"type": "Command","name": "syncthing"     ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\syncthing\\current\\syncthing.exe' -WindowStyle Hidden"},
            # {"type": "Command","name": "ValoQbit"      ,"command": "Start-Process 'C:\\ms1\\scripts\\valorant\\valo_qbit.ps1' -WindowStyle Hidden"},
            # {"type": "Command","name": "whkd"          ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe' -WindowStyle Hidden"},
            # {"type": "Command","name": "yasb"          ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\yasb\\main.py' -WindowStyle Hidden"},

{"type": "Command","name": "ahkscript"           ,"command": "Start-Process 'C:\\ms1\\ahkscripts.ahk'"}                                                                                                                       ,
{"type": "Command","name": "arr_monitor"         ,"command": "Start-Process 'C:\\ms1\\arr_monitor.ps1' -WindowStyle Hidden"}                                                                                                  ,
{"type": "Command","name": "bazarr"              ,"command": "Start-Process -FilePath 'C:\\ProgramData\\Bazarr\\WinPython\\python-3.10.0\\python.exe' -ArgumentList 'C:\\ProgramData\\Bazarr\\bazarr.py' -WindowStyle Hidden"},
{"type": "Command","name": "DesktopCoral"        ,"command": 'Start "C:\\Program Files (x86)\\DesktopCoral\\DesktopCoral.exe"'}                                                                                               ,
{"type": "Command","name": "Ditto"               ,"command": "C:\\Users\\nahid\\scoop\\apps\\ditto\\current\\Ditto.exe"}                                                                                                      ,
{"type": "Command","name": "flaresolver"         ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\flaresolverr\\current\\flaresolverr.exe' -WindowStyle Hidden"}                                                    ,
{"type": "Command","name": "Glaze_WM"            ,"command": "Start-Process 'glazewm.exe' -WindowStyle hidden"}                                                                                                               ,
{"type": "Command","name": "komorebic"           ,"command": "komorebic start"}                                                                                                                                               ,
{"type": "Command","name": "monitor_size"        ,"command": "Start-Process 'powershell.exe' -ArgumentList '-File C:\\ms1\\scripts\\monitor_size.ps1' -Verb RunAs -WindowStyle Hidden"}                                       ,
{"type": "Command","name": "mypygui"             ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\mypygui.py' -WindowStyle Hidden"}                                                                            ,
{"type": "Command","name": "Prowlarr"            ,"command": "C:\\ProgramData\\Prowlarr\\bin\\Prowlarr.exe"}                                                                                                                  ,
{"type": "Command","name": "Radarr"              ,"command": "C:\\ProgramData\\Radarr\\bin\\Radarr.exe"}                                                                                                                      ,
{"type": "Command","name": "RoundedCornerDisable","command": "Start-Process 'C:\\Users\\nahid\\OneDrive\\backup\\win11-toggle-rounded-corners.exe' -ArgumentList '--disable' -Verb RunAs -WindowStyle Hidden"}                ,
{"type": "Command","name": "RssGuard"            ,"command": "C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\rssguard.exe"}                                                                                                ,
{"type": "Command","name": "Sonarr"              ,"command": "C:\\ProgramData\\Sonarr\\bin\\Sonarr.exe"}                                                                                                                      ,
{"type": "Command","name": "sync"                ,"command": "Start-Process 'C:\\ms1\\sync.ps1'"}                                                                                                                             ,
{"type": "Command","name": "syncthing"           ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\syncthing\\current\\syncthing.exe' -WindowStyle Hidden"}                                                          ,
{"type": "Command","name": "ValoQbit"            ,"command": "Start-Process 'C:\\ms1\\scripts\\valorant\\valo_qbit.ps1' -WindowStyle Hidden"}                                                                                 ,
{"type": "Command","name": "whkd"                ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe' -WindowStyle Hidden"}                                                                    ,
{"type": "Command","name": "yasb"                ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\yasb\\main.py' -WindowStyle Hidden"}                                                                         ,
            # Add more items in the same format if needed
        ]
        self.ps1_file_path = "C:\\ms1\\startup_commands.ps1"
        self.create_ps1_file()
        self.create_widgets()


    def create_ps1_file(self):
        if not os.path.exists(self.ps1_file_path):
            with open(self.ps1_file_path, 'w') as f:
                f.write('# PowerShell script for startup\n')

    def create_widgets(self):
        # Sort items based on checked status
        checked_items = []
        unchecked_items = []
        for item in self.items:
            if self.is_checked(item):
                checked_items.append(item)
            else:
                unchecked_items.append(item)

        sorted_items = checked_items + unchecked_items

        app_separator = tk.Label(self, text="Apps", font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        app_separator.pack(fill=tk.X, pady=5)

        for item in sorted_items:
            if item["type"] == "App":
                self.create_item_widget(item)

        command_separator = tk.Label(self, text="Commands", font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        command_separator.pack(fill=tk.X, pady=5)

        for item in sorted_items:
            if item["type"] == "Command":
                self.create_item_widget(item)

    def create_item_widget(self, item):
        frame = tk.Frame(self)
        frame.pack(fill=tk.X)

        name_label = tk.Label(frame, text=item["name"], font=("Jetbrainsmono nfp", 12, "bold"))
        checked = self.is_checked(item)
        label = tk.Label(frame, text="\uf205" if checked else "\uf204", font=("Jetbrainsmono nfp", 12, "bold"), fg="blue" if checked else "gray")
        label.bind("<Button-1>", lambda event, item=item, name_label=name_label, label=label: self.toggle_startup(item, name_label, label))

        label.pack(side=tk.LEFT, padx=10)
        name_label.pack(side=tk.LEFT)

        # Set initial label color based on checked state
        self.update_label_color(name_label, checked)

    def is_checked(self, item):
        if item["type"] == "App":
            shortcut_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', f'{item["name"]}.lnk')
            return os.path.exists(shortcut_path)
        else:
            with open(self.ps1_file_path, 'r') as f:
                lines = f.readlines()
                return any(item["command"] in line for line in lines)

    def toggle_startup(self, item, name_label, icon_label):
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')

        if item["type"] == "App":
            shortcut_path = os.path.join(startup_path, f'{item["name"]}.lnk')
            checked = os.path.exists(shortcut_path)
            if checked:
                try:
                    os.remove(shortcut_path)
                    name_label.config(fg="red")
                    icon_label.config(text="\uf204", fg="gray")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove {item['name']} from startup: {e}")
            else:
                try:
                    winshell.CreateShortcut(Path=shortcut_path, Target=item["path"])
                    name_label.config(fg="green")
                    icon_label.config(text="\uf205", fg="blue")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add {item['name']} to startup: {e}")
        else:
            checked = False
            with open(self.ps1_file_path, 'r') as f:
                lines = f.readlines()
            with open(self.ps1_file_path, 'w') as f:
                for line in lines:
                    if item["command"] in line:
                        checked = True
                    else:
                        f.write(line)
                if not checked:
                    f.write(f'{item["command"]}\n')

            name_label.config(fg="green" if not checked else "red")
            icon_label.config(text="\uf205" if not checked else "\uf204", fg="blue" if not checked else "gray")

    def update_label_color(self, label, checked):
        if checked:
            label.config(fg="green")
        else:
            label.config(fg="red")

if __name__ == "__main__":
    app = StartupManager()
    app.mainloop()
