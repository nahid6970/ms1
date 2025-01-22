import tkinter as tk
from tkinter import messagebox
import os
import winreg

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

class StartupManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide the window initially
        self.title("Startup Manager - Powershell")
        self.configure(bg="#2e2f3e")
        self.items = self.filter_existing_items(self.load_items())  # Load and filter items
        self.create_widgets()
        self.center_window()
        self.attributes('-topmost', True)  # Set always on top
        # self.overrideredirect(True)  # Remove default borders
        self.deiconify()  # Show the window after fully initializing

    def load_items(self):
        # Define items with multiple potential paths
        return [
{"type": "Command","name": "ahk_v2"           ,"paths": [r"C:\ms1\ahk_v2.ahk"]},
{"type": "Command","name": "Flask - Drive"    ,"paths": [r"C:\ms1\startup\Command\flask\flask_drive.ahk"]},
{"type": "Command","name": "Flask - File"     ,"paths": [r"C:\ms1\startup\Command\flask\flask_file.ahk"]},
{"type": "Command","name": "Flask - Text"     ,"paths": [r"C:\ms1\startup\Command\flask\flask_text.ahk"]},
{"type": "Command","name": "Komorebi"         ,"paths": [r"C:\ms1\startup\Command\komorebi.ahk"]},
{"type": "Command","name": "mypygui"          ,"paths": [r"C:\ms1\startup\Command\mypygui.ahk"]},
{"type": "Command","name": "Remote Control"   ,"paths": [r"C:\ms1\startup\Command\remote_control.ahk"]},
{"type": "Command","name": "Square-Corner"    ,"paths": [r"C:\ms1\startup\Command\square_corner.ahk"]},
{"type": "Command","name": "SSHD"             ,"paths": [r"C:\ms1\startup\Command\sshd.ahk"]},
{"type": "Command","name": "Virtual_Monitor"  ,"paths": [r"C:\ms1\startup\Command\virtual_monitor.ahk"]},

# {"type": "Command","name": "arr_monitor"      ,"paths": "Start-Process 'C:/ms1/arr_monitor.ps1' -WindowStyle Hidden"},
# {"type": "Command","name": "NetworkCondition" ,"paths": "Start-Process 'C:\\ms1\\utility\\NetworkCondition.ps1' -WindowStyle Hidden"},
# {"type": "Command","name": "Scheduled_Task"   ,"paths": "C:\\ms1\\scheduled.ps1"},
# {"type": "Command","name": "Sync"             ,"paths": "Start-Process 'C:\\ms1\\sync.ps1'"},

# {"type": "Command","name": "ahk_v1"           ,"paths": r"C:\ms1\ahk_v1.ahk"},
# {"type": "Command","name": "MONITOR_SIZE"     ,"paths": "Start-Process 'powershell.exe' -ArgumentList '-File C:\\ms1\\scripts\\monitor_size.ps1' -Verb RunAs -WindowStyle Hidden"},
# {"type": "Command","name": "Bazarr"           ,"paths": "Start-Process -FilePath 'C:\\ProgramData\\Bazarr\\WinPython\\python-3.10.0\\python.exe' -ArgumentList 'C:\\ProgramData\\Bazarr\\bazarr.py' -WindowStyle Hidden"},
# {"type": "Command","name": "Flaresolverr"     ,"paths": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\flaresolverr\\current\\flaresolverr.exe' -WindowStyle Hidden"},
# {"type": "Command","name": "GlazeWm"          ,"paths": "Start-Process 'glazewm.exe' -WindowStyle hidden"},
# {"type": "Command","name": "Open WebUI"       ,"paths": "Start-Process open-webui serve"},
# {"type": "Command","name": "Syncthing"        ,"paths": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\syncthing\\current\\syncthing.exe' -WindowStyle Hidden"},
# {"type": "Command","name": "whkd"             ,"paths": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe' -WindowStyle Hidden"},
# {"type": "Command","name": "Yasb"             ,"paths": "Start-Process 'python.exe' -ArgumentList 'C:\\ms1\\yasb\\main.py' -WindowStyle Hidden"},

{"type": "App","name": "AMDNoiseSuppression"    ,"paths": [r"C:\WINDOWS\system32\AMD\ANR\AMDNoiseSuppression.exe"]},
{"type": "App","name": "BijoyBayanno"           ,"paths": [r"C:\Program Files (x86)\Ananda Computers\BijoyBayanno\BijoyBayanno.exe"]},
{"type": "App","name": "Capture2Text"           ,"paths": [r"C:\Users\nahid\scoop\apps\capture2text\current\Capture2Text.exe"]},
{"type": "App","name": "Cloudflare WARP"        ,"paths": [r"C:\Program Files\Cloudflare\Cloudflare WARP\Cloudflare WARP.exe"]},
{"type": "App","name": "DesktopCoral"           ,"paths": [r"C:\Program Files (x86)\DesktopCoral\DesktopCoral.exe"]},
{"type": "App","name": "Ditto"                  ,"paths": [r"C:\Users\nahid\scoop\apps\ditto\current\Ditto.exe"]},
{"type": "App","name": "Flow.Launcher"          ,"paths": [r"C:\Users\nahid\AppData\Local\FlowLauncher\app-1.19.4\Flow.Launcher.exe"]},
{"type": "App","name": "Free Download Manager"  ,"paths": [r"C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe"], "Command": "--hidden"},
{"type": "App","name": "Ollama"                 ,"paths": [r"C:\Users\nahid\AppData\Local\Programs\Ollama\ollama app.exe"]},
{"type": "App","name": "Prowlarr"               ,"paths": [r"C:\ProgramData\Prowlarr\bin\Prowlarr.exe"]},
{"type": "App","name": "qBittorrent"            ,"paths": [r"C:\Program Files\qBittorrent\qbittorrent.exe"], "Command": '"--profile=" "--configuration="'},
{"type": "App","name": "Radarr"                 ,"paths": [r"C:\ProgramData\Radarr\bin\Radarr.exe"]},
{"type": "App","name": "RssGuard"               ,"paths": [r"C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe"]},
{"type": "App","name": "Sonarr"                 ,"paths": [r"C:\ProgramData\Sonarr\bin\Sonarr.exe"]},
{"type": "App","name": "Text-Grab"              ,"paths": [r"C:\Users\nahid\scoop\apps\text-grab\current\Text-Grab.exe"]},

{"type": "App","name": "GoogleChromeAutoLaunch_2ABF856BE97FD219EC4C9BF1EB18E55A", "paths": [r"C:\Program Files\Google\Chrome\Application\chrome.exe"], "Command": "--no-startup-window /prefetch:5"},
{"type": "App","name": "MicrosoftEdgeAutoLaunch_A85A975CFCA9AFD77D01E7227175D0CA", "paths": [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"], "Command": "--no-startup-window --win-session-start"},
        ]

    def filter_existing_items(self, items):
        """Filter out items with no valid paths."""
        filtered_items = []
        for item in items:
            for path in item["paths"]:
                if os.path.exists(path):
                    filtered_items.append({
                        "type": item["type"],
                        "name": item["name"],
                        "paths": [path],  # Use a list for compatibility
                        "Command": item.get("Command", ""),  # Include the Command field
                    })
                    break  # Stop after the first valid path
        return filtered_items

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        # Separate commands and apps
        commands = [item for item in self.items if item["type"] == "Command"]
        apps = [item for item in self.items if item["type"] == "App"]
        # Commands Section
        self.create_section("Commands", commands, column=0)
        # Vertical Separator
        separator = tk.Frame(self, width=2, bg="#4a4b5a")  # Create a thin vertical line
        separator.grid(row=1, column=1, rowspan=max(len(commands), len(apps)) + 1, sticky="ns")  # Stretch vertically
        # Apps Section
        self.create_section("Apps", apps, column=2)

    def create_section(self, section_name, items, column):
        separator = tk.Label(self, text=section_name, font=("Helvetica", 10, "bold"), bg="#3a3c49", fg="#ffffff")
        separator.grid(row=0, column=column, pady=5, sticky="ew")

        row = 1
        for item in items:
            self.create_item_widget(item, row, column)
            row += 1

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
            # Retrieve the first path and the command if it exists
            path = item["paths"][0]
            command = item.get("Command", "")
            
            # Format the launch command
            if command:
                # If a command exists, append it to the path
                # os.system(f'start "" "{path}" {command}')
                os.system(f'start "" "{path}"')
            else:
                # If no command, only use the path
                os.system(f'start "" "{path}"')
        else:
            # Fallback for other types
            os.system(f'start "" "{item["paths"][0]}"')


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
                    path = item["paths"][0]  # Use the first path in the list
                    command = item.get("Command", "")  # Get the command or an empty string
                    # Combine the path and command
                    if command:
                        path = f'"{path}" {command}'  # Append the command after the quoted path
                    else:
                        # Enclose the path in quotes if it's not already enclosed
                        if not path.startswith('"') and not path.endswith('"'):
                            path = f'"{path}"'
                    
                    winreg.SetValueEx(reg_key, item["name"], 0, winreg.REG_SZ, path)
                    name_label.config(fg="green")
                    icon_label.config(text="\uf205", fg="#9ef959")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify {item['name']} in startup: {e}")


    def update_label_color(self, label, checked):
        if checked:
            label.config(fg="#63dbff")
        else:
            label.config(fg="red")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    app = StartupManager()
    app.mainloop()
