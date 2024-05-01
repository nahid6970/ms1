from tkinter import messagebox
import subprocess



# def start_bar_1(event):
#     subprocess.Popen(["cmd /c start C:\\ms1\\scripts\\python\\bar_1.py"], shell=True)
def start_bar_1(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\python\\bar_1.py", "-WindowStyle", "Hidden"], shell=True)

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

def start_appstore(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\mypygui_import\\app_store.py"], shell=True)

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