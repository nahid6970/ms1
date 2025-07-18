from tkinter import messagebox
import subprocess
import tkinter as tk

#! Path List
#*  ███████╗██╗██╗     ███████╗    ██████╗  █████╗ ████████╗██╗  ██╗
#*  ██╔════╝██║██║     ██╔════╝    ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║
#*  █████╗  ██║██║     █████╗      ██████╔╝███████║   ██║   ███████║
#*  ██╔══╝  ██║██║     ██╔══╝      ██╔═══╝ ██╔══██║   ██║   ██╔══██║
#*  ██║     ██║███████╗███████╗    ██║     ██║  ██║   ██║   ██║  ██║
#*  ╚═╝     ╚═╝╚══════╝╚══════╝    ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
# br_cf_dst        =r"C:\Users\nahid\OneDrive\backup\arr\bazarr\config.yaml"
# br_cf_src        =r"C:\ProgramData\Bazarr\data\config\config.yaml"
# br_db_dst        =r"C:\Users\nahid\OneDrive\backup\arr\bazarr\bazarr.db"
# br_db_src        =r"C:\ProgramData\Bazarr\data\db\bazarr.db"
# Sr_cf_dst        =r"C:\Users\nahid\OneDrive\backup\arr\sonarr\config.xml"
# Sr_cf_src        =r"C:\ProgramData\Sonarr\config.xml"
# Pr_cf_dst        =r"C:\Users\nahid\OneDrive\backup\arr\prowlarr\config.xml"
# Pr_cf_src        =r"C:\ProgramData\Prowlarr\config.xml"
# Rr_cf_dst        =r"C:\Users\nahid\OneDrive\backup\arr\radarr\config.xml"
# Rr_cf_src        =r"C:\ProgramData\Radarr\config.xml"
ProwlarrDB_dst     =r"C:\Users\nahid\OneDrive\backup\@mklink\prowlarr\prowlarr.db"
ProwlarrDB_src     =r"C:\ProgramData\Prowlarr\prowlarr.db"
RadarrDB_dst       =r"C:\Users\nahid\OneDrive\backup\@mklink\radarr\radarr.db"
RadarrDB_src       =r"C:\ProgramData\Radarr\radarr.db"
SonarrDB_dst       =r"C:\Users\nahid\OneDrive\backup\@mklink\sonarr\sonarr.db"
SonarrDB_src       =r"C:\ProgramData\Sonarr\sonarr.db"

Rss_cf_dst       =r"C:\Users\nahid\OneDrive\backup\rssguard\config\config.ini"
Rss_cf_src       =r"C:\Users\nahid\scoop\apps\rssguard\current\data4\config\config.ini"
Rss_db_dst       =r"C:\Users\nahid\OneDrive\backup\rssguard\database"
Rss_db_src       =r"C:\Users\nahid\scoop\apps\rssguard\current\data4\database"

glazewm_dst      =r"C:\ms1\asset\glazewm\.glaze-wm"
glazewm_src      =r"C:\Users\nahid\.glaze-wm"
komorebi_dst     =r"C:\ms1\asset\komorebi\komorebi.json"
komorebi_src     =r"C:\Users\nahid\komorebi.json"
Nilesoft_dst     =r"C:\ms1\asset\nilesoft_shell\imports"
Nilesoft_src     =r"C:\Program Files\Nilesoft Shell\imports"
pwsh_profile_dst =r"C:\ms1\asset\Powershell\Microsoft.PowerShell_profile.ps1"
pwsh_profile_src =r"C:\Users\nahid\OneDrive\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
pwshH_dst        =r"C:\Users\nahid\OneDrive\backup\ConsoleHost_history.txt"
pwshH_src        =r"C:\Users\nahid\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
rclone_dst       =r"C:\Users\nahid\OneDrive\backup\rclone\rclone.conf"
rclone_src       =r"C:\Users\nahid\scoop\apps\rclone\current\rclone.conf"
terminal_dst     =r"C:\ms1\asset\terminal\settings.json"
terminal_dst     =r"C:\ms1\asset\terminal\settings.json"
terminal_src     =r"C:\Users\nahid\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
terminal_src     =r"C:\Users\nahid\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
whkd_dst         =r"C:\ms1\asset\whkd\whkdrc\whkdrc"
whkd_src         =r"C:\Users\nahid\.config\whkdrc"

#*  █████╗ ██████╗ ██████╗     ██████╗  █████╗ ████████╗██╗  ██╗
#* ██╔══██╗██╔══██╗██╔══██╗    ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║
#* ███████║██████╔╝██████╔╝    ██████╔╝███████║   ██║   ███████║
#* ██╔══██║██╔═══╝ ██╔═══╝     ██╔═══╝ ██╔══██║   ██║   ██╔══██║
#* ██║  ██║██║     ██║         ██║     ██║  ██║   ██║   ██║  ██║
#* ╚═╝  ╚═╝╚═╝     ╚═╝         ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

Ack_scoop_path             =r"C:\Users\nahid\scoop\apps\ack\current\ack.bat"
Adb_scoop_path             =r"C:\Users\nahid\scoop\apps\adb\current\platform-tools\adb.exe"
Alacritty_scoop_path       =r"C:\Users\nahid\scoop\apps\alacritty\current\alacritty.exe"
Alacritty_winget_path      =r"C:\Program Files\Alacritty\alacritty.exe"
Aria2_scoop_path           =r"C:\Users\nahid\scoop\apps\aria2\current\aria2c.exe"
Aria2_winget_path          =r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\aria2c.exe"
AudioRelay_winget_path     =r"C:\Program Files (x86)\AudioRelay\AudioRelay.exe"
AutoHotkeyv1_scoop_path    =r"C:\Users\nahid\scoop\apps\autohotkey1.1\current\AutoHotkeyU64.exe"
AutoHotkeyv1_winget_path   =r"C:\Users\nahid\AppData\Local\Microsoft\WindowsApps\AutoHotkeyU64.exe"
AutoHotkeyv2_winget_path   =r"C:\Users\nahid\AppData\Local\Programs\AutoHotkey\v2\AutoHotkey64.exe"
Autoruns_winget_path       =r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\Microsoft.Sysinternals.Autoruns_Microsoft.Winget.Source_8wekyb3d8bbwe\autoruns.exe"
BareGrep_scoop_path        =r"C:\Users\nahid\scoop\apps\baregrep\current\baregrep.exe"
Bat_scoop_path             =r"C:\Users\nahid\scoop\apps\bat\current\bat.exe"
Bazarr_winget_path         =r"C:\Bazarr\bazarr.py"
Bitwarden_winget_path      =r"C:\Users\nahid\AppData\Local\Programs\Bitwarden\Bitwarden.exe"
btop_scoop_path            =r"C:\Users\nahid\scoop\apps\btop\current\btop.exe"
BulkUninstall_winget_path  =r"C:\Program Files\BCUninstaller\BCUninstaller.exe"
Capture2Text_scoop_path    =r"C:\Users\nahid\scoop\apps\capture2text\current\Capture2Text.exe"
CheatEngine_scoop_path     =r"C:\Users\nahid\scoop\apps\cheat-engine\current\Cheat Engine.exe"
clink_scoop_path           =r"C:\Users\nahid\scoop\apps\clink\current\clink_x64.exe"
Cmder_scoop_path           =r"C:\Users\nahid\scoop\apps\cmder\current\Cmder.exe"
CPUZ_scoop_path            =r"C:\Users\nahid\scoop\apps\cpu-z\current\cpuz_x64.exe"
CrystalDiskInfo_scoop_path =r"C:\Users\nahid\scoop\apps\crystaldiskinfo\current\DiskInfo64.exe"
Ditto_scoop_path           =r'C:\Users\nahid\scoop\apps\ditto\current\Ditto.exe'
dotnet6_wp                 =r'C:\Program Files\dotnet\shared\Microsoft.NETCore.App\6.0.29\createdump.exe'
DotNet8_wp                 =r"C:\Program Files\dotnet\dotnet.exe"
eza_sp                     =r'C:\Users\nahid\scoop\apps\eza\current\eza.exe'
fastfetch_sp               =r'C:\Users\nahid\scoop\apps\fastfetch\current\fastfetch.exe'
ffmpeg_sp                  =r'C:\Users\nahid\scoop\apps\ffmpeg\current\bin\ffmpeg.exe'
FFmpegBatch_sp             =r'C:\Users\nahid\scoop\apps\ffmpeg-batch\current\FFBatch.exe'
FileConverter_wp           =r"C:\Program Files\File Converter\FileConverter.exe"
filezillaServer_sp         =r'C:\Users\nahid\scoop\apps\filezilla-server\current\filezilla-server.exe'
flaresolverr_sp            =r'C:\Users\nahid\scoop\apps\flaresolverr\current\flaresolverr.exe'
FreeDownloadManager_wp     =r"C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe"
fzf_sp                     =r'C:\Users\nahid\scoop\apps\fzf\current\fzf.exe'
git_sp                     =r'C:\Users\nahid\scoop\apps\git\current\cmd\git.exe'
GitHubDesktop_sp           =r'C:\Users\nahid\scoop\apps\github\current\GitHubDesktop.exe'
GlazeWM_scoop_path         =r"C:\Users\nahid\scoop\apps\glazewm\current\GlazeWM.exe"
grep_sp                    =r'C:\Users\nahid\scoop\apps\grep\current\grep.exe'
highlight_sp               =r'C:\Users\nahid\scoop\apps\highlight\current\highlight.exe'
imagemagick_sp             =r'C:\Users\nahid\scoop\apps\imagemagick\current\magick.exe'
Inkscape_wp                =r"C:\Program Files\Inkscape\bin\inkscape.exe"
Jackett_wp                 =r"C:\ProgramData\Jackett\JackettTray.exe"
JavaRuntimeEnvironment_wp  =r"C:\Program Files (x86)\Common Files\Oracle\Java\javapath\java.exe"
komorebi_scoop_path        =r"C:\Users\nahid\scoop\apps\komorebi\current\komorebi.exe"
lazygit_sp                 =r'C:\Users\nahid\scoop\apps\lazygit\current\lazygit.exe'
less_sp                    =r'C:\Users\nahid\scoop\apps\less\current\less.exe'
localsend_sp               =r'C:\Users\nahid\scoop\apps\localsend\current\localsend_app.exe'
meld_wp                    =r'C:\Program Files\Meld\Meld.exe'
node_sp                    =r'C:\Users\nahid\scoop\apps\nodejs\current\node.exe'
notepadplusplus_sp         =r'C:\Users\nahid\scoop\apps\notepadplusplus\current\notepad++.exe'
notepadplusplus_winget_path=r"C:\Program Files\Notepad++\notepad++.exe"
obsstudio_wp               =r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
ohmyposh_sp                =r'C:\Users\nahid\scoop\apps\oh-my-posh\current\oh-my-posh.exe'
pandoc_sp                  =r'C:\Users\nahid\scoop\apps\pandoc\current\pandoc.exe'
perl_sp                    =r'C:\Users\nahid\scoop\apps\perl\current\perl\bin\perl.exe'
php_sp                     =r'C:\Users\nahid\scoop\apps\php\current\php.exe'
PotPlayer_wp               =r"C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe"
PowerShell_wp              =r"C:\Program Files\PowerShell\7\pwsh.exe"
PowerToys_sp               =r'C:\Users\nahid\scoop\apps\PowerToys\current\PowerToys.exe'
PowerToys_wp               =r"C:\Users\nahid\AppData\Local\PowerToys\PowerToys.exe"
Prowlarr_wp                =r"C:\ProgramData\Prowlarr\bin\Prowlarr.exe"
python_sp                  =r'C:\Users\nahid\scoop\apps\python\current\python.exe'
qBittorrent_wp             =r"C:\Program Files\qBittorrent\qbittorrent.exe"
Radarr_wp                  =r"C:\ProgramData\Radarr\bin\Radarr.exe"
Rclone_sp                  =r'C:\Users\nahid\scoop\apps\rclone\current\rclone.exe'
Rclone_wp                  =r'C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\rclone.exe'
ReIcon_sp                  =r'C:\Users\nahid\scoop\apps\reicon\current\ReIcon.exe'
ripgrep_scoop_path         =r"C:\Users\nahid\scoop\apps\ripgrep\current\rg.exe"
ripgrep_winget_path        =r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\BurntSushi.ripgrep.MSVC_Microsoft.Winget.Source_8wekyb3d8bbwe\ripgrep-14.1.0-x86_64-pc-windows-msvc\rg.exe"
rssguard_sp                =r'C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe'
Ruffle_sp                  =r'C:\Users\nahid\scoop\apps\ruffle-nightly\current\ruffle.exe'
Rufus_sp                   =r'C:\Users\nahid\scoop\apps\rufus\current\rufus.exe'
Rufus_wp                   =r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\rufus.exe"
scoopCompletion_sp         =r'C:\Users\nahid\scoop\apps\scoop-completion\current\scoop-completion.psm1'
scoopSearch_sp             =r'C:\Users\nahid\scoop\apps\scoop-search\current\scoop-search.exe'
scrcpy_sp                  =r'C:\Users\nahid\scoop\apps\scrcpy\current\scrcpy.exe'
scrcpyplus_wp              =r"C:\Users\nahid\AppData\Local\Programs\scrcpy-plus\scrcpy+.exe"
Sonarr_wp                  =r"C:\ProgramData\Sonarr\bin\Sonarr.exe"
steam_wp                   =r"C:\Program Files (x86)\Steam\steam.exe"
Syncthing_sp               =r'C:\Users\nahid\scoop\apps\syncthing\current\syncthing.exe'
tldr_sp                    =r'C:\Users\nahid\scoop\apps\tldr\current\tldr.exe'
VCredistAIO_sp             =r'C:\Users\nahid\scoop\apps\vcredist-aio\current\VisualCppRedist_AIO_x86_x64.exe'
ventoy_sp                  =r'C:\Users\nahid\scoop\apps\ventoy\current\altexe\Ventoy2Disk_X64.exe'
VirtualBox_sp              =r'C:\Users\nahid\scoop\apps\virtualbox-with-extension-pack-np\current\VirtualBox.exe'
vscode_wp                  =r"C:\Users\nahid\AppData\Local\Programs\Microsoft VS Code\Code.exe"
VSCodium_winget_path       =r"C:\Users\nahid\AppData\Local\Programs\VSCodium\VSCodium.exe"
whatsapp_wp                =r"C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_2.2407.10.0_x64__cv1g1gvanyjgm\WhatsApp.exe"
whkd_scoop_path            =r"C:\Users\nahid\scoop\apps\whkd\current\whkd.exe"
WinaeroTweaker_sp          =r'C:\Users\nahid\scoop\apps\winaero-tweaker\current\WinaeroTweaker.exe'
windirstat_sp              =r'C:\Users\nahid\scoop\apps\windirstat\current\windirstat.exe'
winget_sp                  =r'C:\Users\nahid\scoop\apps\winget\current\winget.exe'
WinToy_winget_path         =r"C:\Program Files\WindowsApps\11413PtruceanBogdan.Wintoys_1.3.0.0_x64__ankwhmsh70gj6\Wintoys.exe"
WizTree_sp                 =r'C:\Users\nahid\scoop\apps\wiztree\current\WizTree64.exe'
WPUninstall_wp             =r"C:\Program Files (x86)\Wise\Wise Program Uninstaller\WiseProgramUninstaller.exe"
wsapacman_sp               =r'C:\Users\nahid\scoop\apps\wsa-pacman\current\WSA-pacman.exe'
WSUtilities_sp             =r'C:\Users\nahid\scoop\apps\workspaceutilities\current\WorkspaceUtilities.exe'
X_mousebutton_winget_path  =r"C:\Program Files\Highresolution Enterprises\X-Mouse Button Control\XMouseButtonControl.exe"
ytdlp_sp                   =r'C:\Users\nahid\scoop\apps\yt-dlp\current\yt-dlp.exe'
Zoxide_scoop_path          =r"C:\Users\nahid\scoop\apps\zoxide\current\zoxide.exe"
winfsp_sp                  =r'C:\Users\nahid\scoop\apps\winfsp-np\current\setup.msi_'
TigerVncServer_wg          =r'C:\Program Files\TightVNC\tvnserver.exe'
mingw_msvcrt               =r"C:\Users\nahid\scoop\apps\mingw-msvcrt\current\bin\mingw32-make.exe"
sudo_sp                    =r'C:\Users\nahid\scoop\apps\sudo\current\sudo.ps1'











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
        self.on_enter(event)

    def on_leave_widget(self, event):
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
            y += self.widget.winfo_rooty() - 25  # Position above the button
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", borderwidth=1, font=("JetBrains Mono", self.font_size))
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
# def start_bar_1(event):
#     subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\python\\bar_1.py", "-WindowStyle", "Hidden"], shell=True)
# def edit_bar_1(event):
#     subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\scripts\\python\\bar_1.py", "-WindowStyle", "Hidden"], shell=True)

# def start_shortcut(event):
#     subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\shortcut.py", "-WindowStyle", "Hidden"], shell=True)

# def start_backup(event):
#     subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='GiTSync' ; C:\\ms1\\scripts\\backup.ps1 ; C:\\ms1\\scripts\\Github\\ms1u.ps1 ; C:\\ms1\\scripts\\Github\\ms2u.ps1 ; cd ~}"], shell=True)


def start_fzf_c():
    subprocess.Popen(["powershell", "-Command", 'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; fzf --preview=\'highlight -O ansi -l {}\'"'], shell=True)

def start_fzf_d():
    subprocess.Popen(["powershell", "-Command", 'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; fzf --preview=\'bat {}\'"'], shell=True)

# def start_ack_c():
#     input_text = insert_input()  # Assuming insert_input() is a function that returns the desired input
#     subprocess.Popen(["powershell", "-Command", f'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; ack {input_text}"'], shell=True)

# def start_ack_d():
#     input_text = insert_input()  # Assuming insert_input() is a function that returns the desired input
#     subprocess.Popen(["powershell", "-Command", f'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; ack {input_text}"'], shell=True)

def start_find_file():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_file.ps1"])
def start_find_pattern():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_file.ps1"])
def start_find_size():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_size.ps1"])

# def start_tools(event):
#     subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\mypygui_import\\tools.py", "-WindowStyle", "Hidden"], shell=True)

# def start_applist(event):
#     subprocess.Popen(["cmd /c start C:\\ms1\\scripts\\mypygui_import\\applist.py"], shell=True)
# def edit_applist(event):
#     subprocess.Popen(["cmd /c code C:\\ms1\\scripts\\mypygui_import\\applist.py"], shell=True)

# def start_appstore(event):
#     subprocess.Popen(["cmd /c start C:\\ms1\\scripts\\mypygui_import\\app_store.py"], shell=True)
# def edit_appstore(event):
#     subprocess.Popen(["cmd /c code C:\\ms1\\scripts\\mypygui_import\\app_store.py"], shell=True)

# def start_folder(event):
#     subprocess.Popen(["cmd /c C:\\ms1\\scripts\\mypygui_import\\folder.py"], shell=True)
# def Edit_folder(event):
#     subprocess.Popen(["cmd /c code C:\\ms1\\scripts\\mypygui_import\\folder.py"], shell=True)

# def start_process(event):
#     subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\mypygui_import\\process.py"], shell=True)
# def Edit_process(event):
#     subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\scripts\\mypygui_import\\process.py"], shell=True)

# def start_script_list(event):
#     subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\mypygui_import\\script_list.py", "-WindowStyle", "Hidden"], shell=True)
# def edit_script_list(event):
#     subprocess.Popen(["powershell", "start-process","code", "C:\\ms1\\scripts\\mypygui_import\\script_list.py", "-WindowStyle", "Hidden"], shell=True)


# def get_appinfo(event):
#     subprocess.Popen(["cmd /c C:\\ms1\\scripts\\info.py"], shell=True)
# def edit_appinfo(event):
#     subprocess.Popen(["cmd /c code C:\\ms1\\scripts\\info.py"], shell=True)


def force_shutdown(event):
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to shutdown?")
    if confirmed:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
        # subprocess.run(["shutdown", "/s", "/t", "0"])
def force_restart(event):
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to restart?")
    if confirmed:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])
        # subprocess.run(["shutdown", "/r", "/t", "0"])

# def open_backup(event=None):
#     subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\backup.ps1"], shell=True)
# def edit_backup(event=None):
#     subprocess.Popen(["powershell", "start","code", "C:\\ms1\\scripts\\backup.ps1"], shell=True)

# def open_update(event=None):
#     subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\update.ps1"],  shell=True)
# def edit_update(event=None):
#     subprocess.Popen(["powershell", "start","code", "C:\\ms1\\scripts\\update.ps1"],  shell=True)

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

# def Backup_Restore(event):
#     subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\BackupRestore.py"])
# def editBackup_Restore(event):
#     subprocess.Popen(["powershell", "start","code", "C:\\ms1\\scripts\\BackupRestore.py"])

def fzf_search(event):
    subprocess.Popen(["cmd /c start C:\\ms1\\scripts\\ff.ps1"], shell=True)
def edit_fzfSearch(event):
    subprocess.Popen(["cmd /c code C:\\ms1\\scripts\\ff.ps1"],shell=True)

# def launch_LockBox(event=None):
#     subprocess.Popen('cmd /c  "C:\\Program Files\\My Lockbox\\mylbx.exe"')

# def kill_proces(event):
#     subprocess.Popen(["cmd /c start C:\\ms1\\utility\\kill_process.ps1"], shell=True)
