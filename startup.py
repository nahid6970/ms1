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

# Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run #* Registry Start Path

    def load_items(self):
        # Define items with multiple potential paths
        return [
{"type": "Command","name": "ahk_v2"                           ,"paths": [r"C:\Users\nahid\ms\ms1\ahk_v2.ahk"]},
{"type": "Command","name": "ollama-chat"                      ,"paths": [r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"] , "Command": r"C:\Users\nahid\ms\ms1\ollama-chat-app\server.py"},
{"type": "Command","name": "Flask - 5001 - Text"              ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5001_share_text\\share_text.py"},
{"type": "Command","name": "Flask - 5002 - Share File"        ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5002_upload_files\\upload_files.py"},
{"type": "Command","name": "Flask - 5003 - Drive"             ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5003_Browse_PC_Files\\Browse_PC_Files.py"},
{"type": "Command","name": "Flask - 5005 - GameARR"           ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5005_GameARR\\GameARR.py"},
{"type": "Command","name": "Flask - 5006 - Run Commands"      ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5006_Run_Commands\\Run_Commands.py"},
{"type": "Command","name": "Flask - 5007 - ControlBy Android" ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5007_Controlby_Android\\Android_Control_PC.py"},
{"type": "Command","name": "Flask - 5008 - Valorant Match"    ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5008_esports_scheduler\\Esports_Match_Schedule.py"},
{"type": "Command","name": "Flask - 5009 - MCQ"               ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5009_MCQ\\app.py"},
{"type": "Command","name": "Flask - 5010 - CoC"               ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5010_coc\\Clash_of_Clans.py"},
{"type": "Command","name": "Clipboard"                        ,"paths": [r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe"] , "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\clipboard.py"},
{"type": "Command","name": "Komorebi"                         ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\Autohtokey\Command\komorebi.ahk"]},
{"type": "Command","name": "mypygui"                          ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\Autohtokey\Command\mypygui.ahk"]},
{"type": "Command","name": "Open WebUI"                       ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\Autohtokey\Command\openwebui.ahk"]},
{"type": "Command","name": "Remote Control"                   ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\Autohtokey\Command\remote_control.ahk"]},
{"type": "Command","name": "Square-Corner"                    ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\Autohtokey\Command\square_corner.ahk"]},
{"type": "Command","name": "SSHD"                             ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\Autohtokey\Command\sshd.ahk"]},
{"type": "Command","name": "Sync"                             ,"paths": [r"C:\\Users\\nahid\\ms\\ms1\\scripts\\sync.ps1"]},
{"type": "Command","name": "Syncthing"                        ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\Autohtokey\Command\syncthing.ahk"]},
{"type": "Command","name": "Virtual_Monitor"                  ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\Autohtokey\Command\virtual_monitor.ahk"]},
{"type": "Command","name": "Disable Defender"                 ,"paths": [r"C:\Users\nahid\ms\ms1\scripts\disable_defender.ps1"]},

# {"type": "Command","name": "arr_monitor"      ,"paths": "Start-Process 'C:/Users/nahid/ms/ms1/scripts/arr/arr_monitor.ps1' -WindowStyle Hidden"},
# {"type": "Command","name": "NetworkCondition" ,"paths": "Start-Process 'C:\\Users\\nahid\\ms\\ms1\\scripts\\NetworkCondition.ps1' -WindowStyle Hidden"},
# {"type": "Command","name": "Scheduled_Task"   ,"paths": "C:\\Users\\nahid\\ms\\ms1\\scripts\\scheduled.ps1"},

# {"type": "Command","name": "ahk_v1"           ,"paths": r"C:\Users\nahid\ms\ms1\scripts\@old\ahk_v1.ahk"},
# {"type": "Command","name": "MONITOR_SIZE"     ,"paths": "Start-Process 'powershell.exe' -ArgumentList '-File C:\\Users\\nahid\\ms\\ms1\\scripts\\monitor_size.ps1' -Verb RunAs -WindowStyle Hidden"},
# {"type": "Command","name": "Bazarr"           ,"paths": "Start-Process -FilePath 'C:\\ProgramData\\Bazarr\\WinPython\\python-3.10.0\\python.exe' -ArgumentList 'C:\\ProgramData\\Bazarr\\bazarr.py' -WindowStyle Hidden"},
# {"type": "Command","name": "Flaresolverr"     ,"paths": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\flaresolverr\\current\\flaresolverr.exe' -WindowStyle Hidden"},
# {"type": "Command","name": "GlazeWm"          ,"paths": "Start-Process 'glazewm.exe' -WindowStyle hidden"},
# {"type": "Command","name": "Open WebUI"       ,"paths": "Start-Process open-webui serve"},
# {"type": "Command","name": "Syncthing"        ,"paths": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\syncthing\\current\\syncthing.exe' -WindowStyle Hidden"},
# {"type": "Command","name": "whkd"             ,"paths": "Start-Process 'C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe' -WindowStyle Hidden"},
# {"type": "Command","name": "Yasb"             ,"paths": "Start-Process 'python.exe' -ArgumentList 'C:\\Users\\nahid\\ms\\ms1\\yasb\\main.py' -WindowStyle Hidden"},

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
        # Retrieve the first path and the command if it exists
        path = item["paths"][0]
        command = item.get("Command", "")
        
        # Format the full command as it would appear in the registry
        if command:
            full_command = f'"{path}" {command}'
        else:
            # Ensure the path is enclosed in quotes for safety
            if not path.startswith('"') and not path.endswith('"'):
                full_command = f'"{path}"'
            else:
                full_command = path
        try:
            # Execute the command using os.system
            os.system(f'start "" {full_command}')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {item['name']}: {e}")



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
