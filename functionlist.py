from tkinter import messagebox
import subprocess
import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, delay, font_size=10):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.font_size = font_size
        self.tooltip = None
        self.enter_id = None
        self.leave_id = None
        self.widget.bind("<Enter>", self.on_enter_widget)
        self.widget.bind("<Leave>", self.on_leave_widget)
    def on_enter_widget(self, event):
        self.widget.on_enter(event)
        self.on_enter(event)
    def on_leave_widget(self, event):
        self.widget.on_leave(event)
        self.on_leave(event)
    def on_enter(self, event):
        if self.enter_id is None:
            self.enter_id = self.widget.after(self.delay, self.show_tooltip)
    def on_leave(self, event):
        if self.enter_id:
            self.widget.after_cancel(self.enter_id)
            self.enter_id = None
        self.hide_tooltip()
    def show_tooltip(self):
        if self.tooltip is None:
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", borderwidth=1, font=("jetbrainsmono nfp", self.font_size))
            label.pack(ipadx=1)
    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.bg = kw.pop('bg', "#000000")
        self.h_bg = kw.pop('h_bg', "red")
        self.fg = kw.pop('fg', "#FFFFFF")
        self.h_fg = kw.pop('h_fg', "#000000")
        self.tooltip_text = kw.pop('tooltip_text', None)
        self.tooltip_delay = kw.pop('tooltip_delay', 500)  # Default delay
        self.tooltip_font_size = kw.pop('tooltip_font_size', 10)  # Default font size
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(bg=self.bg, fg=self.fg)
        if self.tooltip_text:
            ToolTip(self, self.tooltip_text, delay=self.tooltip_delay, font_size=self.tooltip_font_size)
    def on_enter(self, event):
        self.configure(bg=self.h_bg, fg=self.h_fg)
    def on_leave(self, event):
        self.configure(bg=self.bg, fg=self.fg)



# def start_bar_1(event):
#     subprocess.Popen(["cmd /c start C:\\ms1\\scripts\\python\\bar_1.py"], shell=True)
def start_bar_1(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\python\\bar_1.py", "-WindowStyle", "Hidden"], shell=True)
def edit_bar_1(event):
    subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\scripts\\python\\bar_1.py", "-WindowStyle", "Hidden"], shell=True)

def start_shortcut(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\shortcut.py", "-WindowStyle", "Hidden"], shell=True)

def start_backup(event):
    subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='GiTSync' ; C:\\ms1\\backup.ps1 ; C:\\ms1\\scripts\\Github\\ms1u.ps1 ; C:\\ms1\\scripts\\Github\\ms2u.ps1 ; cd ~}"], shell=True)

def start_fzf_c():
    subprocess.Popen(["powershell", "-Command", 'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; fzf --preview=\'highlight -O ansi -l {}\'"'], shell=True)

def start_fzf_d():
    subprocess.Popen(["powershell", "-Command", 'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; fzf --preview=\'bat {}\'"'], shell=True)

def start_ack_c():
    input_text = insert_input()  # Assuming insert_input() is a function that returns the desired input
    subprocess.Popen(["powershell", "-Command", f'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; ack {input_text}"'], shell=True)

def start_ack_d():
    input_text = insert_input()  # Assuming insert_input() is a function that returns the desired input
    subprocess.Popen(["powershell", "-Command", f'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; ack {input_text}"'], shell=True)

def start_find_file():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_file.ps1"])

def start_find_pattern():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_file.ps1"])

def start_find_size():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_size.ps1"])

def start_tools(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\tools.py", "-WindowStyle", "Hidden"], shell=True)

def start_applist(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\applist.py"], shell=True)
def edit_applist(event):
    subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\mypygui_import\\applist.py"], shell=True)

def start_appstore(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\app_store.py"], shell=True)
def edit_appstore(event):
    subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\mypygui_import\\app_store.py"], shell=True)

def start_folder(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\folder.py", "-WindowStyle", "Hidden"], shell=True)
def Edit_folder(event):
    subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\mypygui_import\\folder.py", "-WindowStyle", "Hidden"], shell=True)

def start_process(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\process.py"], shell=True)
def Edit_process(event):
    subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\mypygui_import\\process.py"], shell=True)

def start_script_list(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\script_list.py", "-WindowStyle", "Hidden"], shell=True)
def edit_script_list(event):
    subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\mypygui_import\\script_list.py", "-WindowStyle", "Hidden"], shell=True)


def force_shutdown(event):
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to shutdown?")
    if confirmed:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
def force_restart(event):
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to restart?")
    if confirmed:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])

def open_backup(event=None):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\backup.ps1"], shell=True)
def edit_backup(event=None):
    subprocess.Popen(["powershell", "start","code", "C:\\ms1\\backup.ps1"], shell=True)

def open_update(event=None):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\update.ps1"],  shell=True)
def edit_update(event=None):
    subprocess.Popen(["powershell", "start","code", "C:\\ms1\\update.ps1"],  shell=True)

def c_size(event=None):
    subprocess.run(["powershell", "Start-Process rclone -ArgumentList 'ncdu c:\\' "])
def d_size(event=None):
    subprocess.run(["powershell", "Start-Process rclone -ArgumentList 'ncdu d:\\' "])

def start_trim():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\trim.ps1"])
def start_convert():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\convert.ps1"])
def start_dimension():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\dimension.ps1"])
def start_imgdimension():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\imgdim.ps1"])
def start_merge():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\ffmpeg\\merge.ps1"])

def Backup_Restore(event):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\utility\\BackupRestore.py"])
def editBackup_Restore(event):
    subprocess.Popen(["powershell", "start","code", "C:\\ms1\\utility\\BackupRestore.py"])

def fzf_search(event):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\utility\\find_files.ps1"])
def edit_fzfSearch(event):
    subprocess.Popen(["powershell", "start","code", "C:\\ms1\\utility\\find_files.ps1"])

def launch_LockBox(event=None):
    subprocess.Popen('cmd /c  "C:\\Program Files\\My Lockbox\\mylbx.exe"')

def kill_proces(event):
    subprocess.Popen(["powershell", "start", "C:\\ms1\\utility\\kill_process.ps1"])


#! Path List
rclone_src = "C:/Users/nahid/scoop/apps/rclone/current/rclone.conf"
rclone_dst = "C:/Users/nahid/OneDrive/backup/rclone/rclone.conf"

glazewm_src = "C:/Users/nahid/.glaze-wm"
glazewm_dst = "C:/ms1/asset/glazewm/.glaze-wm"

komorebi_src = "C:/Users/nahid/komorebi.json"
komorebi_dst = "C:/ms1/asset/komorebi/komorebi.json"

Nilesoft_src = "C:/Program Files/Nilesoft Shell/imports"
Nilesoft_dst = "C:/ms1/asset/nilesoft_shell/imports"

whkd_src = "C:/Users/nahid/.config/whkdrc"
whkd_dst = "C:/ms1/asset/whkd/whkdrc/whkdrc"

pwshH_src = "C:/Users/nahid/AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"
pwshH_dst = "C:/Users/nahid/OneDrive/backup/ConsoleHost_history.txt"

terminal_src = "C:/Users/nahid/AppData/Local/Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState/settings.json"
terminal_dst = "C:/ms1/asset/terminal/settings.json/settings.json"

pwsh_profile_src = "C:/Users/nahid/OneDrive/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
pwsh_profile_dst = "C:/ms1/asset/Powershell/Microsoft.PowerShell_profile.ps1"

Sr_db_src = "C:/ProgramData/Sonarr/sonarr.db"
Sr_db_dst = "C:/Users/nahid/OneDrive/backup/arr/sonarr/sonarr.db"

Sr_cf_src = "C:/ProgramData/Sonarr/config.xml"
Sr_cf_dst = "C:/Users/nahid/OneDrive/backup/arr/sonarr/config.xml"

Rr_db_src = "C:/ProgramData/Radarr/radarr.db"
Rr_db_dst = "C:/Users/nahid/OneDrive/backup/arr/radarr/radarr.db"

Rr_cf_src = "C:/ProgramData/Radarr/config.xml"
Rr_cf_dst = "C:/Users/nahid/OneDrive/backup/arr/radarr/config.xml"

Pr_db_src = "C:/ProgramData/Prowlarr/prowlarr.db"
Pr_db_dst = "C:/Users/nahid/OneDrive/backup/arr/prowlarr/prowlarr.db"

Pr_cf_src = "C:/ProgramData/Prowlarr/config.xml"
Pr_cf_dst = "C:/Users/nahid/OneDrive/backup/arr/prowlarr/config.xml"

br_db_src = "C:/ProgramData/Bazarr/data/db/bazarr.db"
br_db_dst = "C:/Users/nahid/OneDrive/backup/arr/bazarr/bazarr.db"

br_cf_src = "C:/ProgramData/Bazarr/data/config/config.yaml"
br_cf_dst = "C:/Users/nahid/OneDrive/backup/arr/bazarr/config.yaml"

Rss_db_src = "C:/Users/nahid/scoop/apps/rssguard/current/data4/database"
Rss_db_dst = "C:/Users/nahid/OneDrive/backup/rssguard/database"

Rss_cf_src = "C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\config\\config.ini"
Rss_cf_dst = "C:\\Users\\nahid\\OneDrive\\backup\\rssguard\\config\\config.ini"




#! App Path
Zoxide_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\zoxide\\current\\zoxide.exe"

ripgrep_winget_path = "C:\\Users\\nahid\\AppData\\Local\\Microsoft\\WinGet\\Packages\\BurntSushi.ripgrep.MSVC_Microsoft.Winget.Source_8wekyb3d8bbwe\\ripgrep-14.1.0-x86_64-pc-windows-msvc\\rg.exe"
ripgrep_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\ripgrep\\current\\rg.exe"

WinToy_winget_path = "C:\\Program Files\\WindowsApps\\11413PtruceanBogdan.Wintoys_1.3.0.0_x64__ankwhmsh70gj6\\Wintoys.exe"

VSCodium_winget_path = "C:\\Users\\nahid\\AppData\\Local\\Programs\\VSCodium\\VSCodium.exe"

whkd_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\whkd\\current\\whkd.exe"

komorebi_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\komorebi\\current\\komorebi.exe"

GlazeWM_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\glazewm\\current\\GlazeWM.exe"

X_mousebutton_winget_path = "C:\\Program Files\\Highresolution Enterprises\\X-Mouse Button Control\\XMouseButtonControl.exe"

BulkUninstall_winget_path = "C:\\Program Files\\BCUninstaller\\BCUninstaller.exe"

Ack_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\ack\\current\\ack.bat"

Adb_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\adb\\current\\platform-tools\\adb.exe"

Alacritty_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\alacritty\\current\\alacritty.exe"
Alacritty_winget_path = "C:\\Program Files\\Alacritty\\alacritty.exe"

Aria2_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\aria2\\current\\aria2c.exe"
Aria2_winget_path = "C:\\Users\\nahid\\AppData\\Local\\Microsoft\\WinGet\\Links\\aria2c.exe"

AudioRelay_winget_path = "C:\\Program Files (x86)\\AudioRelay\\AudioRelay.exe"

AutoHotkeyv1_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\autohotkey1.1\\current\\AutoHotkeyU64.exe"
AutoHotkeyv1_winget_path = "C:\\Users\\nahid\\AppData\\Local\\Microsoft\\WindowsApps\\AutoHotkeyU64.exe"

AutoHotkeyv2_winget_path = "C:\\Users\\nahid\\AppData\\Local\\Programs\\AutoHotkey\\v2\\AutoHotkey64.exe"

Autoruns_winget_path="C:\\Users\\nahid\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Microsoft.Sysinternals.Autoruns_Microsoft.Winget.Source_8wekyb3d8bbwe\\autoruns.exe"

BareGrep_scoop_path="C:\\Users\\nahid\\scoop\\apps\\baregrep\\current\\baregrep.exe"

Bat_scoop_path = "C:\\Users\\nahid\\scoop\\apps\\bat\\current\\bat.exe"

Bazarr_winget_path = "C:\\Bazarr\\bazarr.py"

Bitwarden_winget_path="C:\\Users\\nahid\\AppData\\Local\\Programs\\Bitwarden\\Bitwarden.exe"

btop_scoop_path="C:\\Users\\nahid\\scoop\\apps\\btop\\current\\btop.exe"

Capture2Text_scoop_path="C:\\Users\\nahid\\scoop\\apps\\capture2text\\current\\Capture2Text.exe"

CheatEngine_scoop_path ="C:\\Users\\nahid\\scoop\\apps\\cheat-engine\\current\\Cheat Engine.exe"

clink_scoop_path="C:\\Users\\nahid\\scoop\\apps\\clink\\current\\clink_x64.exe"

Cmder_scoop_path="C:\\Users\\nahid\\scoop\\apps\\cmder\\current\\Cmder.exe"

CPUZ_scoop_path="C:\\Users\\nahid\\scoop\\apps\\cpu-z\\current\\cpuz_x64.exe"

CrystalDiskInfo_scoop_path="C:\\Users\\nahid\\scoop\\apps\\crystaldiskinfo\\current\\DiskInfo64.exe"