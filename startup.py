import tkinter as tk
from tkinter import messagebox
import os
import winreg

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Startup Manager - Powershell")
        self.configure(bg="#2e2f3e")
        self.items = self.load_items()  # Load items dynamically or define them here
        self.create_widgets()

    def load_items(self):
        # Define your items here, now using "App2" instead of "Command"
        return [

{"type": "App2","name": "Komorebi"         ,"path": r"C:\ms1\startup\Command\komorebi.ahk"},
{"type": "App2","name": "mypygui"          ,"path": r"C:\ms1\startup\Command\mypygui.ahk"},
{"type": "App2","name": "Square-Corner"    ,"path": "Start-Process C:\\msBackups\\Display\\win11-toggle-rounded-corners.exe -ArgumentList --disable -Verb RunAs -WindowStyle Hidden"},
{"type": "App2","name": "Text-[Share]"     ,"path": "Start-Process C:\\ms1\\flask\\share_text\\share_text.py -WindowStyle Hidden"},
{"type": "App2","name": "File-[Share]"     ,"path": "Start-Process C:\\ms1\\flask\\upload_files.py -WindowStyle Hidden"},
{"type": "App2","name": "Drive-[Share]"    ,"path": "Start-Process C:\\ms1\\flask\\Browse_PC_Files\\Browse_PC_Files.py -WindowStyle Hidden"},

{"type": "App2","name": "arr_monitor"      ,"path": "Start-Process 'C:/ms1/arr_monitor.ps1' -WindowStyle Hidden"},
{"type": "App2","name": "Remote Control"   ,"path": "Start-Process 'C:\\ms1\\Rclone_Remote.py' -WindowStyle Hidden"},
{"type": "App2","name": "NetworkCondition" ,"path": "Start-Process 'C:\\ms1\\utility\\NetworkCondition.ps1' -WindowStyle Hidden"},
{"type": "App2","name": "Scheduled_Task"   ,"path": "C:\\ms1\\scheduled.ps1"},
{"type": "App2","name": "sshd"             ,"path": "Start-Process 'powershell.exe' -ArgumentList 'restart-Service sshd' -Verb RunAs -WindowStyle Hidden"},
{"type": "App2","name": "Sync"             ,"path": "Start-Process 'C:\\ms1\\sync.ps1'"},
{"type": "App2","name": "Virtual_Monitor"  ,"path": "cmd /c 'C:\\msBackups\\Display\\usbmmidd_v2\\2ndMonitor.bat'; cmd /c 'C:\\msBackups\\Display\\DisplaySwitch.exe /internal'"},
# {"type": "App2","name": "MONITOR_SIZE"   ,"path": "Start-Process 'powershell.exe' -ArgumentList '-File C:\\ms1\\scripts\\monitor_size.ps1' -Verb RunAs -WindowStyle Hidden"},
# {"type": "App2","name": "Bazarr"         ,"path": "Start-Process -FilePath 'C:\\ProgramData\\Bazarr\\WinPython\\python-3.10.0\\python.exe' -ArgumentList 'C:\\ProgramData\\Bazarr\\bazarr.py' -WindowStyle Hidden"},
# {"type": "App2","name": "Flaresolverr"   ,"path": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\flaresolverr\\current\\flaresolverr.exe' -WindowStyle Hidden"},
# {"type": "App2","name": "GlazeWm"        ,"path": "Start-Process 'glazewm.exe' -WindowStyle hidden"},
# {"type": "App2","name": "Open WebUI"     ,"path": "Start-Process open-webui serve"},
# {"type": "App2","name": "Syncthing"      ,"path": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\syncthing\\current\\syncthing.exe' -WindowStyle Hidden"},
# {"type": "App2","name": "whkd"           ,"path": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe' -WindowStyle Hidden"},
# {"type": "App2","name": "Yasb"           ,"path": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\yasb\\main.py' -WindowStyle Hidden"},

{"type": "App","name": "ahk_v2"            ,"path": r"C:\ms1\ahk_v2.ahk"},
{"type": "App","name": "ahk_v1"            ,"path": r"C:\ms1\ahk_v1.ahk"},
{"type": "App","name": "BijoyBayanno"      ,"path": r"C:\Program Files (x86)\Ananda Computers\BijoyBayanno\BijoyBayanno.exe"},
{"type": "App","name": "Capture2Text"      ,"path": r"C:\Users\nahid\scoop\apps\capture2text\current\Capture2Text.exe"},
{"type": "App","name": "Cloudflare WARP"   ,"path": r"C:\Program Files\Cloudflare\Cloudflare WARP\Cloudflare WARP.exe"},
{"type": "App","name": "DesktopCoral"      ,"path": r"C:\Program Files (x86)\DesktopCoral\DesktopCoral.exe"},
{"type": "App","name": "Ditto"             ,"path": r"C:\Users\nahid\scoop\apps\ditto\current\Ditto.exe"},
{"type": "App","name": "Ollama"            ,"path": r"C:\Users\nahid\AppData\Local\Programs\Ollama\ollama app.exe"},
{"type": "App","name": "Prowlarr"          ,"path": r"C:\ProgramData\Prowlarr\bin\Prowlarr.exe"},
{"type": "App","name": "Radarr"            ,"path": r"C:\ProgramData\Radarr\bin\Radarr.exe"},
{"type": "App","name": "RssGuard"          ,"path": r"C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe"},
{"type": "App","name": "Sonarr"            ,"path": r"C:\ProgramData\Sonarr\bin\Sonarr.exe"},
        ]

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Separate App2 and Apps
        checked_app2 = [item for item in self.items if item["type"] == "App2" and self.is_checked(item)]
        unchecked_app2 = [item for item in self.items if item["type"] == "App2" and not self.is_checked(item)]
        checked_apps = [item for item in self.items if item["type"] == "App" and self.is_checked(item)]
        unchecked_apps = [item for item in self.items if item["type"] == "App" and not self.is_checked(item)]

        # App2 Section
        app2_separator = tk.Label(self, text="Command", font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        app2_separator.grid(row=0, column=0, pady=5, sticky="ew")

        app2_row = 1
        for item in checked_app2 + unchecked_app2:
            self.create_item_widget(item, app2_row, 0)
            app2_row += 1

        # Add vertical separator
        separator = tk.Frame(self, width=2, bg="#4a4b5a")
        separator.grid(row=1, column=1, rowspan=max(len(checked_app2) + len(unchecked_app2), len(checked_apps) + len(unchecked_apps)), sticky="ns")

        # Apps Section
        app_separator = tk.Label(self, text="Apps", font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        app_separator.grid(row=0, column=2, pady=5, sticky="ew")

        app_row = 1
        for item in checked_apps + unchecked_apps:
            self.create_item_widget(item, app_row, 2)
            app_row += 1

    def create_item_widget(self, item, row, col):
        frame = tk.Frame(self, bg="#2e2f3e")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="w")

        name_label = tk.Label(frame, text=item["name"], font=("Jetbrainsmono nfp", 12, "bold"), bg="#2e2f3e")
        checked = self.is_checked(item)

        icon_label = tk.Label(frame, text="\uf205" if checked else "\uf204", font=("Jetbrainsmono nfp", 12, "bold"), fg="#9ef959" if checked else "gray", bg="#2e2f3e")
        icon_label.bind("<Button-1>", lambda event, item=item, name_label=name_label, icon_label=icon_label: self.toggle_startup(item, name_label, icon_label))
        icon_label.pack(side=tk.LEFT, padx=0)

        name_label.bind("<Button-1>", lambda event, item=item: self.launch_command(item))
        name_label.pack(side=tk.LEFT)

        self.update_label_color(name_label, checked)

    def launch_command(self, item):
        if item["type"] == "App":
            os.system(f'start "" "{item["path"]}"')
        elif item["type"] == "App2":
            # Launch App2 (no command needed)
            os.system(f'start "" "{item["path"]}"')

    def is_checked(self, item):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ) as reg_key:
                try:
                    winreg.QueryValueEx(reg_key, item["name"])
                    return True
                except FileNotFoundError:
                    return False
        except WindowsError:
            return False

    def toggle_startup(self, item, name_label, icon_label):
        reg_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        try:
            if self.is_checked(item):
                # Remove from startup
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    winreg.DeleteValue(reg_key, item["name"])
                    name_label.config(fg="red")
                    icon_label.config(text="\uf204", fg="gray")
            else:
                # Add to startup
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    if item["type"] == "App":
                        winreg.SetValueEx(reg_key, item["name"], 0, winreg.REG_SZ, f'pythonw -c "import subprocess; subprocess.run([\'powershell\', \'-WindowStyle\', \'Hidden\', \'-Command\', \'{item["path"]}\'], shell=True)"')
                    elif item["type"] == "App2":
                        winreg.SetValueEx(reg_key, item["name"], 0, winreg.REG_SZ, f'pythonw -c "import subprocess; subprocess.run([\'powershell\', \'-WindowStyle\', \'Hidden\', \'-Command\', \'{item["path"]}\'], shell=True)"')
                    name_label.config(fg="green")
                    icon_label.config(text="\uf205", fg="#9ef959")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify {item['name']} in startup: {e}")

    def update_label_color(self, label, checked):
        if checked:
            label.config(fg="#63dbff")
        else:
            label.config(fg="red")


def Center_Window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    app = StartupManager()
    Center_Window(app)
    app.mainloop()
