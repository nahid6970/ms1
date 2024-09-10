import tkinter as tk
from tkinter import messagebox
import os
import pyautogui

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Startup Manager")
        self.items = [
{"type": "Command","name": "AHKSCRIPT"           ,"command": "Start-Process 'C:\\ms1\\ahkscripts.ahk'"},
{"type": "Command","name": "MYPYGUI"             ,"command": "Start-Process  'C:\\ms1\\mypygui.py' -WindowStyle Hidden"},
{"type": "Command","name": "KOMOREBIC"           ,"command": "komorebic start"},
{"type": "Command","name": "2ndMonitor-Virtual"  ,"command": "cmd /c C:\\Users\\nahid\\OneDrive\\backup\\usbmmidd_v2\\2ndMonitor.bat"},
{"type": "Command","name": "1st Monitor"         ,"command": "cmd /c C:\\Users\\nahid\\OneDrive\\backup\\DisplaySwitch.exe /internal"},
{"type": "Command","name": "NetworkCondition"    ,"command": "Start-Process 'C:\\ms1\\utility\\NetworkCondition.ps1' -WindowStyle Hidden"},
{"type": "Command","name": "RoundedCornerDisable","command": "Start-Process 'C:\\Users\\nahid\\OneDrive\\backup\\win11-toggle-rounded-corners.exe' -ArgumentList '--disable' -Verb RunAs -WindowStyle Hidden"},
{"type": "Command","name": "SSHD"                ,"command": "Start-Process 'powershell.exe' -ArgumentList 'restart-Service sshd' -Verb RunAs -WindowStyle Hidden"},
{"type": "Command","name": "SCHEDULED"           ,"command": "Start-Process C:\\ms1\\scheduled.ps1"},
{"type": "Command","name": "Open WebUI"          ,"command": "Start-Process open-webui serve"},

{"type": "Command","name": "arr_monitor"         ,"command": "Start-Process 'C:\\ms1\\arr_monitor.ps1' -WindowStyle Hidden"},
{"type": "Command","name": "BAZARR"              ,"command": "Start-Process -FilePath 'C:\\ProgramData\\Bazarr\\WinPython\\python-3.10.0\\python.exe' -ArgumentList 'C:\\ProgramData\\Bazarr\\bazarr.py' -WindowStyle Hidden"},
{"type": "Command","name": "FLARESOLVER"         ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\flaresolverr\\current\\flaresolverr.exe' -WindowStyle Hidden"},
{"type": "Command","name": "GLAZE_WM"            ,"command": "Start-Process 'glazewm.exe' -WindowStyle hidden"},
{"type": "Command","name": "MONITOR_SIZE"        ,"command": "Start-Process 'powershell.exe' -ArgumentList '-File C:\\ms1\\scripts\\monitor_size.ps1' -Verb RunAs -WindowStyle Hidden"},
{"type": "Command","name": "SYNC"                ,"command": "Start-Process 'C:\\ms1\\sync.ps1'"},
{"type": "Command","name": "SYNCTHING"           ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\syncthing\\current\\syncthing.exe' -WindowStyle Hidden"},
{"type": "Command","name": "WHKD"                ,"command": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe' -WindowStyle Hidden"},
{"type": "Command","name": "YASB"                ,"command": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\yasb\\main.py' -WindowStyle Hidden"},

{"type": "App","name": "BijoyBayanno"      ,"path": "C:\\Program Files (x86)\\Ananda Computers\\BijoyBayanno\\BijoyBayanno.exe"},
{"type": "App","name": "Capture2Text"      ,"path": "C:\\Users\\nahid\\scoop\\apps\\capture2text\\current\\Capture2Text.exe"},
{"type": "App","name": "DesktopCoral"      ,"path": "C:\\Program Files (x86)\\DesktopCoral\\DesktopCoral.exe"},
{"type": "App","name": "Ditto"             ,"path": "C:\\Users\\nahid\\scoop\\apps\\ditto\\current\\Ditto.exe"},
{"type": "App","name": "Ollama"            ,"path": "C:\\Users\\nahid\\AppData\\Local\\Programs\\Ollama\\ollama app.exe"},
{"type": "App","name": "Prowlarr"          ,"path": "C:\\ProgramData\\Prowlarr\\bin\\Prowlarr.exe"},
{"type": "App","name": "Radarr"            ,"path": "C:\\ProgramData\\Radarr\\bin\\Radarr.exe"},
{"type": "App","name": "RssGuard"          ,"path": "C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\rssguard.exe"},
{"type": "App","name": "Sonarr"            ,"path": "C:\\ProgramData\\Sonarr\\bin\\Sonarr.exe"},
{"type": "App","name": "Cloudflare WARP"   ,"path": "C:\\Program Files\\Cloudflare\\Cloudflare WARP\\Cloudflare WARP.exe"},
        ]

        self.ps1_file_path = "C:\\ms1\\startup_commands.ps1"
        self.create_ps1_file()
        self.create_widgets()

    def create_ps1_file(self):
        if not os.path.exists(self.ps1_file_path):
            with open(self.ps1_file_path, 'w') as f:
                f.write('# PowerShell script for startup\n')

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)

        checked_commands = [item for item in self.items if item["type"] == "Command" and self.is_checked(item)]
        unchecked_commands = [item for item in self.items if item["type"] == "Command" and not self.is_checked(item)]
        checked_apps = [item for item in self.items if item["type"] == "App" and self.is_checked(item)]
        unchecked_apps = [item for item in self.items if item["type"] == "App" and not self.is_checked(item)]

        command_separator = tk.Label(self, text="Commands", font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        command_separator.grid(row=0, column=0, columnspan=5, pady=5, sticky="ew")
        command_row = 1
        command_col = 0

        for item in checked_commands + unchecked_commands:
            self.create_item_widget(item, command_row, command_col)
            command_col += 1
            if command_col > 4:
                command_col = 0
                command_row += 1

        app_separator = tk.Label(self, text="Apps", font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        app_separator.grid(row=command_row + 1, column=0, columnspan=5, pady=5, sticky="ew")
        app_row = command_row + 2
        app_col = 0

        for item in checked_apps + unchecked_apps:
            self.create_item_widget(item, app_row, app_col)
            app_col += 1
            if app_col > 4:
                app_col = 0
                app_row += 1

    def create_item_widget(self, item, row, col):
        frame = tk.Frame(self)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="w")

        name_label = tk.Label(frame, text=item["name"], font=("Jetbrainsmono nfp", 12, "bold"))
        checked = self.is_checked(item)
        
        icon_label = tk.Label(frame, text="\uf205" if checked else "\uf204", font=("Jetbrainsmono nfp", 12, "bold"), fg="blue" if checked else "gray")
        icon_label.bind("<Button-1>", lambda event, item=item, name_label=name_label, icon_label=icon_label: self.toggle_startup(item, name_label, icon_label))
        icon_label.pack(side=tk.LEFT, padx=0)

        name_label.bind("<Button-1>", lambda event, item=item: self.launch_command(item))
        name_label.pack(side=tk.LEFT)

        self.update_label_color(name_label, checked)

    def launch_command(self, item):
        if item["type"] == "App":
            os.system(f'start "" "{item["path"]}"')
        else:
            os.system(f'PowerShell -Command "{item["command"]}"')

    def is_checked(self, item):
        with open(self.ps1_file_path, 'r') as f:
            lines = f.readlines()
            if item["type"] == "App":
                return any(f"Start-Process -FilePath '{item['path']}'" in line for line in lines)
            else:
                return any(item["command"] in line for line in lines)

    def toggle_startup(self, item, name_label, icon_label):
        checked = self.is_checked(item)
        with open(self.ps1_file_path, 'r') as f:
            lines = f.readlines()

        with open(self.ps1_file_path, 'w') as f:
            for line in lines:
                if item["type"] == "App" and f"Start-Process -FilePath '{item['path']}'" in line:
                    checked = True
                elif item["type"] == "Command" and item["command"] in line:
                    checked = True
                else:
                    f.write(line)
            if not checked:
                if item["type"] == "App":
                    f.write(f"Start-Process -FilePath '{item['path']}'\n")
                else:
                    f.write(f"{item['command']}\n")

        self.update_label_color(name_label, not checked)
        icon_label.config(text="\uf205" if not checked else "\uf204", fg="blue" if not checked else "gray")

    def update_label_color(self, label, checked):
        if checked:
            label.config(fg="#0365c0")
        else:
            label.config(fg="red")

def center_and_press_alt_2(window):
    def center_window():
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    def press_alt_2():
        pyautogui.hotkey('alt', '2')
    center_window()
    window.after(25, press_alt_2)

if __name__ == "__main__":
    app = StartupManager()
    center_and_press_alt_2(app)
    app.mainloop()
