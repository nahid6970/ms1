import subprocess
import subprocess
import tkinter as tk
from tkinter import Canvas, Scrollbar
from tkinter import ttk
import os
import ctypes

from functionlist import *

# import sys
# sys.path.append('C:/ms1/')
# from functionlist import *




def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)
set_console_title("App List")

# Vaiables to track the position of the mouse when clicking​⁡
drag_data = {"x": 0, "y": 0}

def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def stop_drag(event):
    drag_data["x"] = None
    drag_data["y"] = None

def do_drag(event):
    if drag_data["x"] is not None and drag_data["y"] is not None:
        x, y = (event.x - drag_data["x"] + ROOT.winfo_x(), event.y - drag_data["y"] + ROOT.winfo_y())
        ROOT.geometry("+%s+%s" % (x, y))

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

# Create main window
ROOT = tk.Tk()
ROOT.title("Folder")
ROOT.attributes('-topmost', True)  # Set always on top
# ROOT.geometry("520x800")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)  # Remove default borders

# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Add bindings to make the window movable
ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width - 430
y = screen_height//2 - 600//2
ROOT.geometry(f"430x600+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=430, height=600) #!
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1)  # Add some padding at the top
MAIN_FRAME.pack(expand=True)


#! Close Window
def close_window(event=None):
    ROOT.destroy()

#!? Main ROOT BOX
ROOT1 = tk.Frame(ROOT, bg="#1d2027")
ROOT1.pack(side="right", anchor="ne", pady=(3,2),padx=(3,1))

def create_label(text, parent, bg, fg, width, height, relief, font, ht, htc, padx, pady, anchor, row, column, rowspan, columnspan):
    label = tk.Label(parent, text=text, bg=bg, fg=fg, width=width, height=height, relief=relief, font=font, highlightthickness=ht, highlightbackground=htc)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky=anchor, rowspan=rowspan, columnspan=columnspan)
    return label

label_properties = [
{"text": "r","parent": ROOT1,"bg": "#1d2027","fg": "#ff0000","width": 0  ,"height": "0","relief": "flat","font": ("Webdings",10,"bold")  ,"ht": 0,"htc": "#FFFFFF","padx": (0 ,2) ,"pady": (0,0),"anchor": "w","row": 1,"column": 1 ,"rowspan": 1,"columnspan": 1},#! LB_X alternative wingdings x
]
labels = [create_label(**prop) for prop in label_properties]
LB_XXX, = labels
LB_XXX.bind("<Button-1>", close_window)

#! Applist
LB_INITIALSPC = tk.Label(MAIN_FRAME, text="",  bg="#1d2027", fg="#fff", relief="flat", height=1, width=2, font=("calibri", 16, "bold"))
LB_INITIALSPC.pack(side="top", anchor="ne", padx=(0,0), pady=(0,0))

# # Create the search box label
# search_label = tk.Label(Page1, text="Search:", bg="#1d2027", fg="#fff", font=("calibri", 12, "bold"))
# search_label.pack(side="top", anchor="center", padx=(20, 0), pady=(10, 0))

# Create the search entry
search_entry = tk.Entry(MAIN_FRAME, font=("calibri", 12), bg="#FFFFFF", fg="#000000", insertbackground="#F00")
search_entry.pack(side="top", anchor="center", padx=(20, 0), pady=(0, 10))

def check_installation(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt):
    scoop_installed = os.path.exists(scoop_path)
    winget_installed = os.path.exists(winget_path)
    application_installed = scoop_installed or winget_installed
    chkbx_var.set(1 if application_installed else 0)

    # Change text color based on installation status if not already checked
    text_color = "green" if application_installed else "red"

    # Update the label with installation source
    installation_source = ""
    if scoop_installed:
        installation_source = "[S]"
        text_color = "#FFFFFF"  # Set color to white for [S]
    elif winget_installed:
        installation_source = "[W]"
        text_color = "#41abff"   # Set color to blue for [W]
    else:
        installation_source = "[X]"
        text_color = "#FF0000"    # Set color to red for [X]

    chkbox_bt.config(text=f"{app_name} {installation_source}", foreground=text_color)

def install_application(app_name, scoop_name, scoop_path, winget_name, winget_path, chkbx_var, chkbox_bt):
    install_options = []
    if winget_path:
        install_options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'winget install {winget_name}')})
    if scoop_path:
        install_options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'pwsh -Command "scoop install {scoop_name}"')})
    show_options(install_options)

def uninstall_application(app_name, scoop_name, scoop_path, winget_name, winget_path, chkbx_var, chkbox_bt):
    uninstall_options = []
    if winget_path:
        uninstall_options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'winget uninstall {winget_name}')})
    if scoop_path:
        uninstall_options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'pwsh -Command "scoop uninstall {scoop_name}"')})
    show_options(uninstall_options)

def open_file_location(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt):
    options = []
    if winget_path:
        options.append({"text": "Winget", "command": lambda: subprocess.Popen(f'explorer /select,"{winget_path}"')})
    if scoop_path:
        options.append({"text": "Scoop", "command": lambda: subprocess.Popen(f'explorer /select,"{scoop_path}"')})
    show_options(options)

def show_options(options):
    top = tk.Toplevel()
    top.title("Select Source")
    top.geometry("300x100")
    top.configure(bg="#282c34")
    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = 800
    top.geometry(f"300x100+{x}+{y}")

    frame = tk.Frame(top, bg="#1d2027")
    frame.pack(side="top", expand=True, fill="none", anchor="center")

    for option in options:
        # Set background color based on the source type
        if "Winget" in option["text"]:
            bg_color = "#0078D7"
            fg_color = "#FFFFFF"
        elif "Scoop" in option["text"]:
            bg_color = "#FFFFFF"
            fg_color = "#000000"
        else:
            bg_color = "#1d2027"
            fg_color = "#000000"

        btn = tk.Button(frame, text=option["text"], command=option["command"], background=bg_color, foreground=fg_color, padx=10, pady=5, borderwidth=2, relief="raised")
        btn.pack(side="left", padx=5, pady=5, anchor="center")

# Define applications and their information
applications = [
# {"name": "AppName","scoop_name": "ScoopName","scoop_path": r'xx',"winget_name": "WingetName","winget_path": r"xx"} ,
{"name":"Ack [Find]"               ,"scoop_name":"ack"                               ,"scoop_path":Ack_scoop_path            ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"Adb"                      ,"scoop_name":"adb"                               ,"scoop_path":Adb_scoop_path            ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"Alacritty [Terminal]"     ,"scoop_name":"alacritty"                         ,"scoop_path":Alacritty_scoop_path      ,"winget_name":"Alacritty.Alacritty"                    ,"winget_path":Alacritty_winget_path}       ,
{"name":"Aria2"                    ,"scoop_name":"aria2"                             ,"scoop_path":Aria2_scoop_path          ,"winget_name":"aria2.aria2"                            ,"winget_path":Aria2_winget_path}           ,
{"name":"AudioRelay"               ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"AsaphaHalifa.AudioRelay"                ,"winget_path":AudioRelay_winget_path}      ,
{"name":"AutoHotkey v1"            ,"scoop_name":"autohotkey1.1"                     ,"scoop_path":AutoHotkeyv1_scoop_path   ,"winget_name":"9NQ8Q8J78637"                           ,"winget_path":AutoHotkeyv1_winget_path}    ,
{"name":"AutoHotkey v2"            ,"scoop_name":"autohotkey"                        ,"scoop_path":r''                       ,"winget_name":"AutoHotkey.AutoHotkey"                  ,"winget_path":AutoHotkeyv2_winget_path}    ,
{"name":"Autoruns"                 ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"Microsoft.Sysinternals.Autoruns"        ,"winget_path":Autoruns_winget_path}        ,
{"name":"BareGrep [Find]"          ,"scoop_name":"baregrep"                          ,"scoop_path":BareGrep_scoop_path       ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"Bat [Text-View]"          ,"scoop_name":"bat"                               ,"scoop_path":Bat_scoop_path            ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"Bazarr"                   ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"Morpheus.Bazarr"                        ,"winget_path":Bazarr_winget_path}          ,
{"name":"Bitwarden"                ,"scoop_name":"bitwarden"                         ,"scoop_path":r''                       ,"winget_name":"Bitwarden.Bitwarden"                    ,"winget_path":Bitwarden_winget_path}       ,
{"name":"btop [Sys-Monitor]"       ,"scoop_name":"btop"                              ,"scoop_path":btop_scoop_path           ,"winget_name":"aristocratos.btop4win"                  ,"winget_path":r""}                         ,
{"name":"Bulk Crap Uninstaller"    ,"scoop_name":"bulk-crap-uninstaller"             ,"scoop_path":r''                       ,"winget_name":"BCUninstaller"                          ,"winget_path":BulkUninstall_winget_path}   ,
{"name":"Capture2Text"             ,"scoop_name":"Capture2Text"                      ,"scoop_path":Capture2Text_scoop_path   ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"Cheat Engine [7.4]"       ,"scoop_name":"cheat-engine"                      ,"scoop_path":CheatEngine_scoop_path    ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"clink [Terminal]"         ,"scoop_name":"clink"                             ,"scoop_path":clink_scoop_path          ,"winget_name":"chrisant996.Clink"                      ,"winget_path":r""}                         ,
{"name":"Cmder [Terminal]"         ,"scoop_name":"Cmder"                             ,"scoop_path":Cmder_scoop_path          ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"CPU-Z"                    ,"scoop_name":"cpu-z"                             ,"scoop_path":CPUZ_scoop_path           ,"winget_name":"CPUID.CPU-Z"                            ,"winget_path":r""}                         ,
{"name":"Crystal DiskInfo"         ,"scoop_name":"crystaldiskinfo"                   ,"scoop_path":CrystalDiskInfo_scoop_path,"winget_name":"CrystalDewWorld.CrystalDiskInfo"        ,"winget_path":r""}                         ,
{"name":"Ditto"                    ,"scoop_name":"ditto"                             ,"scoop_path":Ditto_scoop_path          ,"winget_name":"Ditto.Ditto"                            ,"winget_path":r""}                         ,
{"name":"DotNet DesktopRuntime 8"  ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"Microsoft.DotNet.DesktopRuntime.8"      ,"winget_path":DotNet8_wp}                  ,
{"name":"ExplorerPatcher"          ,"scoop_name":"ScoopName"                         ,"scoop_path":r''                       ,"winget_name":"ExplorerPatcher"                        ,"winget_path":r""}                         ,
{"name":"eza [ls]"                 ,"scoop_name":"eza"                               ,"scoop_path":eza_sp                    ,"winget_name":"eza-community.eza"                      ,"winget_path":r""}                         ,
{"name":"FFmpeg-Batch"             ,"scoop_name":"ffmpeg-batch"                      ,"scoop_path":FFmpegBatch_sp            ,"winget_name":"eibol.FFmpegBatchAVConverter"           ,"winget_path":r""}                         ,
{"name":"ffmpeg"                   ,"scoop_name":"ffmpeg"                            ,"scoop_path":ffmpeg_sp                 ,"winget_name":"Gyan.FFmpeg"                            ,"winget_path":r""}                         ,
{"name":"FileConverter"            ,"scoop_name":"file-converter-np"                 ,"scoop_path":r''                       ,"winget_name":"AdrienAllard.FileConverter"             ,"winget_path":FileConverter_wp }           ,
{"name":"filezilla-server"         ,"scoop_name":"filezilla-server"                  ,"scoop_path":filezillaServer_sp        ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"flaresolverr"             ,"scoop_name":"flaresolverr"                      ,"scoop_path":flaresolverr_sp           ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"FreeDownloadManager"      ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"SoftDeluxe.FreeDownloadManager"         ,"winget_path":FreeDownloadManager_wp}      ,
{"name":"fzf"                      ,"scoop_name":"fzf"                               ,"scoop_path":fzf_sp                    ,"winget_name":"junegunn.fzf"                           ,"winget_path":r""}                         ,
{"name":"git"                      ,"scoop_name":"git"                               ,"scoop_path":git_sp                    ,"winget_name":"Git.Git"                                ,"winget_path":""}                          ,
{"name":"GitHubDesktop"            ,"scoop_name":"github"                            ,"scoop_path":GitHubDesktop_sp          ,"winget_name":"GitHub.GitHubDesktop"                   ,"winget_path":""}                          ,
{"name":"GlazeWM"                  ,"scoop_name":"glazewm"                           ,"scoop_path":GlazeWM_scoop_path        ,"winget_name":"GlazeWM"                                ,"winget_path":r""}                         ,
{"name":"grep [Find]"              ,"scoop_name":"grep"                              ,"scoop_path":grep_sp                   ,"winget_name":""                                       ,"winget_path":""}                          ,
{"name":"highlight [Text-View]"    ,"scoop_name":"highlight"                         ,"scoop_path":highlight_sp              ,"winget_name":""                                       ,"winget_path":""}                          ,
{"name":"imagemagick"              ,"scoop_name":"imagemagick"                       ,"scoop_path":imagemagick_sp            ,"winget_name":"ImageMagick.ImageMagick"                ,"winget_path":""}                          ,
{"name":"Inkscape"                 ,"scoop_name":"inkscape"                          ,"scoop_path":r''                       ,"winget_name":"Inkscape.Inkscape"                      ,"winget_path":Inkscape_wp}                 ,
{"name":"Jackett"                  ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"Jackett.Jackett"                        ,"winget_path":Jackett_wp}                  ,
{"name":"Java Runtime Environment" ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"Oracle.JavaRuntimeEnvironment"          ,"winget_path":JavaRuntimeEnvironment_wp}   ,
{"name":"komorebi"                 ,"scoop_name":"komorebi"                          ,"scoop_path":komorebi_scoop_path       ,"winget_name":"WingetName"                             ,"winget_path":r""}                         ,
{"name":"lazygit"                  ,"scoop_name":"lazygit"                           ,"scoop_path":lazygit_sp                ,"winget_name":"JesseDuffield.lazygit"                  ,"winget_path":""}                          ,
{"name":"less [Text-View]"         ,"scoop_name":"less"                              ,"scoop_path":less_sp                   ,"winget_name":"jftuga.less"                            ,"winget_path":""}                          ,
{"name":"localsend"                ,"scoop_name":"localsend"                         ,"scoop_path":localsend_sp              ,"winget_name":"LocalSend.LocalSend"                    ,"winget_path":""}                          ,
{"name":"Meld"                     ,"scoop_name":"meld"                              ,"scoop_path":r''                       ,"winget_name":"Meld.Meld"                              ,"winget_path":meld_wp}                     ,
{"name":"Nilesoft Shell"           ,"scoop_name":"nilesoft-shell"                    ,"scoop_path":r''                       ,"winget_name":"nilesoft.shell"                         ,"winget_path":r""}                         ,
{"name":"node"                     ,"scoop_name":"nodejs"                            ,"scoop_path":node_sp                   ,"winget_name":"OpenJS.NodeJS"                          ,"winget_path":""}                          ,
{"name":"notepad++"                ,"scoop_name":"notepadplusplus"                   ,"scoop_path":notepadplusplus_sp        ,"winget_name":"Notepad++.Notepad++"                    ,"winget_path":notepadplusplus_winget_path} ,
{"name":"OBS Studio"               ,"scoop_name":"obs-studio"                        ,"scoop_path":r''                       ,"winget_name":"OBSProject.OBSStudio"                   ,"winget_path":obsstudio_wp }               ,
{"name":"oh-my-posh"               ,"scoop_name":"oh-my-posh"                        ,"scoop_path":ohmyposh_sp               ,"winget_name":"JanDeDobbeleer.OhMyPosh"                ,"winget_path":""}                          ,
{"name":"pandoc"                   ,"scoop_name":"pandoc"                            ,"scoop_path":pandoc_sp                 ,"winget_name":"JohnMacFarlane.Pandoc"                  ,"winget_path":""}                          ,
{"name":"perl [Language]"          ,"scoop_name":"perl"                              ,"scoop_path":perl_sp                   ,"winget_name":"StrawberryPerl.StrawberryPerl"          ,"winget_path":""}                          ,
{"name":"php [Language]"           ,"scoop_name":"php"                               ,"scoop_path":php_sp                    ,"winget_name":""                                       ,"winget_path":""}                          ,
{"name":"PotPlayer"                ,"scoop_name":"potplayer"                         ,"scoop_path":r''                       ,"winget_name":"Daum.PotPlayer"                         ,"winget_path":PotPlayer_wp}                ,
{"name":"PowerShell"               ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"Microsoft.PowerShell"                   ,"winget_path":PowerShell_wp}               ,
{"name":"PowerToys"                ,"scoop_name":"powertoys"                         ,"scoop_path":PowerToys_sp              ,"winget_name":"Microsoft.PowerToys"                    ,"winget_path":PowerToys_wp}                ,
{"name":"ProcessExplorer"          ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"Microsoft.Sysinternals.ProcessExplorer" ,"winget_path":ProcessExplorer_wp}          ,
{"name":"Prowlarr"                 ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"TeamProwlarr.Prowlarr"                  ,"winget_path":Prowlarr_wp}                 ,
{"name":"Python"                   ,"scoop_name":"python"                            ,"scoop_path":python_sp                 ,"winget_name":"Python.Python.3.12"                     ,"winget_path":""}                          ,
{"name":"qBittorrent"              ,"scoop_name":"qbittorrent"                       ,"scoop_path":r''                       ,"winget_name":"qBittorrent.qBittorrent"                ,"winget_path":qBittorrent_wp}              ,
{"name":"Radarr"                   ,"scoop_name":"ScoopName"                         ,"scoop_path":r''                       ,"winget_name":"TeamRadarr.Radarr"                      ,"winget_path":Radarr_wp}                   ,
{"name":"Rclone"                   ,"scoop_name":"rclone"                            ,"scoop_path":Rclone_sp                 ,"winget_name":"Rclone.Rclone"                          ,"winget_path":Rclone_wp}                   ,
{"name":"ReIcon"                   ,"scoop_name":"ReIcon"                            ,"scoop_path":ReIcon_sp                 ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"ripgrep [rg]"             ,"scoop_name":"ripgrep"                           ,"scoop_path":ripgrep_scoop_path        ,"winget_name":"BurntSushi.ripgrep.MSVC"                ,"winget_path":ripgrep_winget_path}         ,
{"name":"Rss Guard"                ,"scoop_name":"rssguard"                          ,"scoop_path":rssguard_sp               ,"winget_name":"martinrotter.RSSGuard"                  ,"winget_path":""}                          ,
{"name":"Ruffle"                   ,"scoop_name":"ruffle-nightly"                    ,"scoop_path":Ruffle_sp                 ,"winget_name":""                                       ,"winget_path":""}                          ,
{"name":"Rufus"                    ,"scoop_name":"rufus"                             ,"scoop_path":Rufus_sp                  ,"winget_name":"Rufus.Rufus"                            ,"winget_path":Rufus_wp}                    ,
{"name":"scoop-completion"         ,"scoop_name":"scoop-completion"                  ,"scoop_path":scoopCompletion_sp        ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"scoop-search"             ,"scoop_name":"scoop-search"                      ,"scoop_path":scoopSearch_sp            ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"scrcpy"                   ,"scoop_name":"scrcpy"                            ,"scoop_path":scrcpy_sp                 ,"winget_name":"Genymobile.scrcpy"                      ,"winget_path":""}                          ,
{"name":"scrcpy+"                  ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"Frontesque.scrcpy+"                     ,"winget_path":scrcpyplus_wp}               ,
{"name":"Sonarr"                   ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"TeamSonarr.Sonarr"                      ,"winget_path":Sonarr_wp}                   ,
{"name":"Steam"                    ,"scoop_name":"steam"                             ,"scoop_path":r''                       ,"winget_name":"Valve.Steam"                            ,"winget_path":steam_wp}                    ,
{"name":"Syncthing"                ,"scoop_name":"syncthing"                         ,"scoop_path":Syncthing_sp              ,"winget_name":"Syncthing.Syncthing"                    ,"winget_path":""}                          ,
{"name":"tldr"                     ,"scoop_name":"tldr"                              ,"scoop_path":tldr_sp                   ,"winget_name":"tldr-pages.tlrc"                        ,"winget_path":""}                          ,
{"name":"VCredist-aio"             ,"scoop_name":"vcredist-aio"                      ,"scoop_path":VCredistAIO_sp            ,"winget_name":"abbodi1406.vcredist"                    ,"winget_path":""}                          ,
{"name":"VirtualBox"               ,"scoop_name":"virtualbox-with-extension-pack-np" ,"scoop_path":VirtualBox_sp             ,"winget_name":"Oracle.VirtualBox"                      ,"winget_path":""}                          ,
{"name":"VSCode"                   ,"scoop_name":"vscode"                            ,"scoop_path":r''                       ,"winget_name":"Microsoft.VisualStudioCode"             ,"winget_path":vscode_wp}                   ,
{"name":"VSCodium"                 ,"scoop_name":"vscodium"                          ,"scoop_path":r''                       ,"winget_name":"VSCodium"                               ,"winget_path":VSCodium_winget_path}        ,
{"name":"WhatsApp"                 ,"scoop_name":"whatsapp"                          ,"scoop_path":r''                       ,"winget_name":"9NKSQGP7F2NH"                           ,"winget_path":whatsapp_wp}                 ,
{"name":"whkd"                     ,"scoop_name":"whkd"                              ,"scoop_path":whkd_scoop_path           ,"winget_name":"WingetName"                             ,"winget_path":r""}                         ,
{"name":"WinaeroTweaker"           ,"scoop_name":"winaero-tweaker"                   ,"scoop_path":WinaeroTweaker_sp         ,"winget_name":""                                       ,"winget_path":""}                          ,
{"name":"windirstat"               ,"scoop_name":"windirstat"                        ,"scoop_path":windirstat_sp             ,"winget_name":"WinDirStat.WinDirStat"                  ,"winget_path":""}                          ,
{"name":"winget"                   ,"scoop_name":"winget"                            ,"scoop_path":winget_sp                 ,"winget_name":""                                       ,"winget_path":r""}                         ,
{"name":"WinToy"                   ,"scoop_name":"ScoopName"                         ,"scoop_path":r''                       ,"winget_name":"wintoy"                                 ,"winget_path":WinToy_winget_path}          ,
{"name":"Wise Program Uninstaller" ,"scoop_name":""                                  ,"scoop_path":r''                       ,"winget_name":"WiseCleaner.WiseProgramUninstaller"     ,"winget_path":WPUninstall_wp}              ,
{"name":"WizTree"                  ,"scoop_name":"WizTree"                           ,"scoop_path":WizTree_sp                ,"winget_name":"AntibodySoftware.WizTree"               ,"winget_path":""}                          ,
{"name":"Workspace Utilities"      ,"scoop_name":"workspaceutilities"                ,"scoop_path":WSUtilities_sp            ,"winget_name":"WingetName"                             ,"winget_path":r""}                         ,
{"name":"WSA-pacman"               ,"scoop_name":"wsa-pacman"                        ,"scoop_path":wsapacman_sp              ,"winget_name":"alesimula.wsa_pacman"                   ,"winget_path":""}                          ,
{"name":"X-Mouse Button Control"   ,"scoop_name":"xmousebuttoncontrol"               ,"scoop_path":r''                       ,"winget_name":"Highresolution.X-MouseButtonControl"    ,"winget_path":X_mousebutton_winget_path}   ,
{"name":"yt-dlp"                   ,"scoop_name":"yt-dlp"                            ,"scoop_path":ytdlp_sp                  ,"winget_name":"yt-dlp.yt-dlp"                          ,"winget_path":""}                          ,
{"name":"Zoxide"                   ,"scoop_name":"zoxide"                            ,"scoop_path":Zoxide_scoop_path         ,"winget_name":"WingetName"                             ,"winget_path":r""}                         ,
]

#!this is for winget direct silent install --accept-package-agreements
# Create canvas and scrollbar
canvas = Canvas(MAIN_FRAME, bg="#1d2027", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

#! scrollbar Start
def on_mousewheel(event):
    # Check if the mouse is over the scrollbar
    if event.widget == scrollbar:
        canvas.yview_scroll(-5 * (event.delta // 120), "units")  # Increase scroll speed
    else:
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

# Create a vertical scrollbar
# scrollbar = ttk.Scrollbar(MAIN_FRAME, orient="vertical", style="Custom.Vertical.TScrollbar", )
# scrollbar.pack(side="right", fill="y")
# canvas.configure(yscrollcommand=scrollbar.set)



scrollbar = ttk.Scrollbar(MAIN_FRAME, orient="vertical", style="Custom.Vertical.TScrollbar")
scrollbar.pack(side="right", fill="y")
# Configure the style of the scrollbar
style = ttk.Style()
style.theme_use("default")
# Set the background color of the scrollbar to red
style.configure("Custom.Vertical.TScrollbar", background="#FF0000", troughcolor="#25072c")
# Set the thickness of the outside bar to 10 pixels
style.map("Custom.Vertical.TScrollbar",
    background=[("active", "#72a9ec")],  # Changed from blue to red
)
# Set the thickness of the inside bar to 25 pixels
style.map("Custom.Vertical.TScrollbar",
    troughcolor=[("active", "#25072c")],  # Changed from blue to red
    width=[("active", 10)]
)
canvas.configure(yscrollcommand=scrollbar.set)

#! scrollbar End

# Create a frame inside the canvas
frame = tk.Frame(canvas, bg="#1d2027")
canvas.create_window((0, 0), window=frame, anchor="nw")

# Update the applications dictionary to store the row number for each app
for app in applications:
    app["frame"] = tk.Frame(frame, bg="#1d2027")
row_number = 0

# Create and pack checkboxes, check buttons, install buttons, and uninstall buttons for each application inside the frame
for app in applications:
    app["chkbx_var"] = tk.IntVar()  # Create IntVar for each application
    app_frame = app["frame"]
    app_frame.grid(row=row_number, column=0, padx=(10,0), pady=(0,0), sticky="ew")  # Adjusted sticky parameter
    row_number += 1

    app_name = app["name"]
    scoop_name = app["scoop_name"]
    scoop_path = app["scoop_path"]
    winget_name = app["winget_name"]
    winget_path = app["winget_path"]
    chkbx_var = app["chkbx_var"]

    chkbox_bt = tk.Checkbutton(app_frame, text=app_name, variable=chkbx_var, font=("JetBrainsMono NF", 12, "bold"), foreground="green", background="#1d2027", activebackground="#1d2027", selectcolor="#1d2027", padx=10, pady=1, borderwidth=2, relief="flat")
    chkbox_bt.configure(command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: check_installation(name, scoop, winget, var, cb))
    chk_bt = tk.Button(app_frame, text=f"Check", foreground="green", background="#1d2027", command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: check_installation(name, scoop, winget, var, cb))
    ins_bt = tk.Button(app_frame, text=f"n", foreground="#00FF00", background="#1d2027", font=("webdings", 5), relief="flat", command=lambda name=app_name, scoop=scoop_name, scoop_path=scoop_path, winget=winget_name, winget_path=winget_path, var=chkbx_var, cb=chkbox_bt: install_application(name, scoop, scoop_path, winget, winget_path, var, cb))
    unins_bt = tk.Button(app_frame, text=f"n", foreground="#FF0000",  background="#1d2027", font=("webdings", 5), relief="flat", command=lambda name=app_name, scoop=scoop_name, scoop_path=scoop_path, winget=winget_name, winget_path=winget_path, var=chkbx_var, cb=chkbox_bt: uninstall_application(name, scoop, scoop_path, winget, winget_path, var, cb))
    open_bt = tk.Button(app_frame, text=f"n", foreground="#eac353", background="#1d2027", font=("webdings", 5), relief="flat", command=lambda name=app_name, scoop=scoop_path, winget=winget_path, var=chkbx_var, cb=chkbox_bt: open_file_location(name, scoop, winget, var, cb))

    chkbox_bt.grid(row=0, column=0, padx=(0,0), pady=(0,0))
    ins_bt.grid(row=0, column=1, padx=(0,0), pady=(0,0))
    unins_bt.grid(row=0, column=2, padx=(0,0), pady=(0,0))
    open_bt.grid(row=0, column=3, padx=(0, 0), pady=(0, 0))

    check_installation(app_name, scoop_path, winget_path, chkbx_var, chkbox_bt)

def filter_apps(event=None):
    search_query = search_entry.get().lower()
    for app in applications:
        app_name = app["name"]
        app_frame = app["frame"]
        if search_query in app_name.lower():
            app_frame.grid()
        else:
            app_frame.grid_remove()

# Bind the filtering function to the KeyRelease event of the search entry
search_entry.bind("<KeyRelease>", filter_apps)

# Update scroll region
frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

#! Ending
MAIN_FRAME.pack()
ROOT.mainloop()
