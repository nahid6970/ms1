import subprocess
import subprocess
import tkinter as tk
from tkinter import Canvas, Scrollbar
from tkinter import ttk
import os



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
# {"name": "MiniConda","scoop_name": "miniconda3","scoop_path": r'xx',"winget_name": "Anaconda.Miniconda3","winget_path": r"xx"} ,
# {"name": "AnaConda","scoop_name": "anaconda3","scoop_path": r'xx',"winget_name": "Anaconda.Anaconda3","winget_path": r"xx"} ,
{"name": "Ack [Find]"               ,"scoop_name": "ack"                               ,"scoop_path": r'C:\Users\nahid\scoop\apps\ack\current\ack.bat'                                      ,"winget_name": ""                                       ,"winget_path": r""                                                                                                                                                      } ,
{"name": "Adb"                      ,"scoop_name": "adb"                               ,"scoop_path": r'C:\Users\nahid\scoop\apps\adb\current\platform-tools\adb.exe'                       ,"winget_name": ""                                       ,"winget_path": r""                                                                                                                                                      } ,
{"name": "Alacritty [Terminal]"     ,"scoop_name": "alacritty"                         ,"scoop_path": r'C:\Users\nahid\scoop\apps\alacritty\current\alacritty.exe'                          ,"winget_name": "Alacritty.Alacritty"                    ,"winget_path": r'C:\Program Files\Alacritty\alacritty.exe'                                                                                                                } ,
{"name": "Aria2"                    ,"scoop_name": "aria2"                             ,"scoop_path": r'C:\Users\nahid\scoop\apps\aria2\current\aria2c.exe'         ,"winget_name": "aria2.aria2"                            ,"winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\aria2c.exe"                                                                                          } ,
{"name": "AudioRelay"               ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "AsaphaHalifa.AudioRelay"                ,"winget_path": r"C:\Program Files (x86)\AudioRelay\AudioRelay.exe"                                                                                                        } ,
{"name": "AutoHotkey v1"            ,"scoop_name": "autohotkey1.1"                     ,"scoop_path": r'C:\Users\nahid\scoop\apps\autohotkey1.1\current\AutoHotkeyU64.exe'                                                                                 ,"winget_name": "9NQ8Q8J78637"                           ,"winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WindowsApps\AutoHotkeyU64.exe"                                                                                    } ,
{"name": "AutoHotkey v2"            ,"scoop_name": "autohotkey"                        ,"scoop_path": r'xx'                                                                                 ,"winget_name": "AutoHotkey.AutoHotkey"                  ,"winget_path": r"C:\Users\nahid\AppData\Local\Programs\AutoHotkey\v2\AutoHotkey64.exe"                                                                                    } ,
{"name": "Autoruns"                 ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "Microsoft.Sysinternals.Autoruns"        ,"winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\Microsoft.Sysinternals.Autoruns_Microsoft.Winget.Source_8wekyb3d8bbwe\autoruns.exe"               } ,
{"name": "BareGrep [Find]"          ,"scoop_name": "baregrep"                          ,"scoop_path": r'C:\Users\nahid\scoop\apps\baregrep\current\baregrep.exe'                            ,"winget_name": "xx"                                     ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "Bat [Text-View]"          ,"scoop_name": "bat"                               ,"scoop_path": r'C:\Users\nahid\scoop\apps\bat\current\bat.exe'                                      ,"winget_name": ""                                       ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "Bazarr"                   ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "Morpheus.Bazarr"                        ,"winget_path": r"C:\Bazarr\bazarr.py"                                                                                                                                     } ,
{"name": "Bitwarden"                ,"scoop_name": "bitwarden"                         ,"scoop_path": r'xx'                                                                                 ,"winget_name": "Bitwarden.Bitwarden"                    ,"winget_path": r"C:\Users\nahid\AppData\Local\Programs\Bitwarden\Bitwarden.exe"                                                                                           } ,
{"name": "btop [Sys-Monitor]"       ,"scoop_name": "btop"                              ,"scoop_path": r'C:\Users\nahid\scoop\apps\btop\current\btop.exe'                                    ,"winget_name": "aristocratos.btop4win"                  ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "Capture2Text"             ,"scoop_name": "Capture2Text"                      ,"scoop_path": r'C:\Users\nahid\scoop\apps\capture2text\current\Capture2Text.exe'                    ,"winget_name": "xx"                                     ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "Cheat Engine [7.4]"       ,"scoop_name": "cheat-engine"                      ,"scoop_path": r'C:\Users\nahid\scoop\apps\cheat-engine\current\Cheat Engine.exe'                    ,"winget_name": ""                                       ,"winget_path": r""                                                                                                                                                        } ,
{"name": "clink [Terminal]"         ,"scoop_name": "clink"                             ,"scoop_path": r'C:\Users\nahid\scoop\apps\clink\current\clink_x64.exe'                              ,"winget_name": "chrisant996.Clink"                      ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "Cmder [Terminal]"         ,"scoop_name": "Cmder"                             ,"scoop_path": r'C:\Users\nahid\scoop\apps\cmder\current\Cmder.exe'                                  ,"winget_name": "xx"                                     ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "CPU-Z"                    ,"scoop_name": "cpu-z"                             ,"scoop_path": r'C:\Users\nahid\scoop\apps\cpu-z\current\cpuz_x64.exe'                               ,"winget_name": "CPUID.CPU-Z"                            ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "Crystal DiskInfo"         ,"scoop_name": "crystaldiskinfo"                   ,"scoop_path": r'C:\Users\nahid\scoop\apps\crystaldiskinfo\current\DiskInfo64.exe'                   ,"winget_name": "CrystalDewWorld.CrystalDiskInfo"        ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "Ditto"                    ,"scoop_name": "ditto"                             ,"scoop_path": r'C:\Users\nahid\scoop\apps\ditto\current\Ditto.exe'                                  ,"winget_name": "Ditto.Ditto"                            ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "DotNet DesktopRuntime 8"  ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "Microsoft.DotNet.DesktopRuntime.8"      ,"winget_path": r"C:\Program Files\dotnet\dotnet.exe"                                                                                                                      } ,
{"name": "eza [ls]"                 ,"scoop_name": "eza"                               ,"scoop_path": r'C:\Users\nahid\scoop\apps\eza\current\eza.exe'                                      ,"winget_name": "eza-community.eza"                      ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "FFmpeg-Batch"             ,"scoop_name": "ffmpeg-batch"                      ,"scoop_path": r'C:\Users\nahid\scoop\apps\ffmpeg-batch\current\FFBatch.exe'                         ,"winget_name": "eibol.FFmpegBatchAVConverter"           ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "ffmpeg"                   ,"scoop_name": "ffmpeg"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\ffmpeg\current\bin\ffmpeg.exe'                            ,"winget_name": "Gyan.FFmpeg"                            ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "FileConverter"            ,"scoop_name": "file-converter-np"                 ,"scoop_path": r'xx'                                                                                 ,"winget_name": "AdrienAllard.FileConverter"             ,"winget_path": r"C:\Program Files\File Converter\FileConverter.exe"                                                                                                       } ,
{"name": "filezilla-server"         ,"scoop_name": "filezilla-server"                  ,"scoop_path": r'C:\Users\nahid\scoop\apps\filezilla-server\current\filezilla-server.exe'            ,"winget_name": "xx"                                     ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "flaresolverr"             ,"scoop_name": "flaresolverr"                      ,"scoop_path": r'C:\Users\nahid\scoop\apps\flaresolverr\current\flaresolverr.exe'                    ,"winget_name": "xx"                                     ,"winget_path": r""                                                                                                                                                        } ,
{"name": "FreeDownloadManager"      ,"scoop_name": "ScoopName"                         ,"scoop_path": r'xx'                                                                                 ,"winget_name": "SoftDeluxe.FreeDownloadManager"         ,"winget_path": r"C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe"                                                                                   } ,
{"name": "fzf"                      ,"scoop_name": "fzf"                               ,"scoop_path": r'C:\Users\nahid\scoop\apps\fzf\current\fzf.exe'                                      ,"winget_name": "junegunn.fzf"                           ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "git"                      ,"scoop_name": "git"                               ,"scoop_path": r'C:\Users\nahid\scoop\apps\git\current\cmd\git.exe'                                  ,"winget_name": "Git.Git"                                ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "GitHubDesktop"            ,"scoop_name": "github"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\github\current\GitHubDesktop.exe'                         ,"winget_name": "GitHub.GitHubDesktop"                   ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "grep [Find]"              ,"scoop_name": "grep"                              ,"scoop_path": r'C:\Users\nahid\scoop\apps\grep\current\grep.exe'                                    ,"winget_name": "xx"                                     ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "highlight [Text-View]"    ,"scoop_name": "highlight"                         ,"scoop_path": r'C:\Users\nahid\scoop\apps\highlight\current\highlight.exe'                          ,"winget_name": "xx"                                     ,"winget_path": ""                                                                                                                                                         } ,
{"name": "imagemagick"              ,"scoop_name": "imagemagick"                       ,"scoop_path": r'C:\Users\nahid\scoop\apps\imagemagick\current\magick.exe'                           ,"winget_name": "ImageMagick.ImageMagick"                ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "Inkscape"                 ,"scoop_name": "inkscape"                          ,"scoop_path": r'xx'                                                                                 ,"winget_name": "Inkscape.Inkscape"                      ,"winget_path": r"C:\Program Files\Inkscape\bin\inkscape.exe"                                                                                                              } ,
{"name": "Jackett"                  ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "Jackett.Jackett"                        ,"winget_path": r"C:\ProgramData\Jackett\JackettTray.exe"                                                                                                                  } ,
{"name": "Java Runtime Environment" ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "Oracle.JavaRuntimeEnvironment"          ,"winget_path": r"C:\Program Files (x86)\Common Files\Oracle\Java\javapath\java.exe"                                                                                       } ,
{"name": "lazygit"                  ,"scoop_name": "lazygit"                           ,"scoop_path": r'C:\Users\nahid\scoop\apps\lazygit\current\lazygit.exe'                              ,"winget_name": "JesseDuffield.lazygit"                  ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "less [Text-View]"         ,"scoop_name": "less"                              ,"scoop_path": r'C:\Users\nahid\scoop\apps\less\current\less.exe'                                    ,"winget_name": "jftuga.less"                            ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "localsend"                ,"scoop_name": "localsend"                         ,"scoop_path": r'C:\Users\nahid\scoop\apps\localsend\current\localsend_app.exe'                      ,"winget_name": "LocalSend.LocalSend"                    ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "Nilesoft Shell"           ,"scoop_name": "nilesoft-shell"                    ,"scoop_path": r'xx'                                                                                 ,"winget_name": "nilesoft.shell"                         ,"winget_path": r"xx"                                                                                                                                                      } ,
{"name": "node"                     ,"scoop_name": "nodejs"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\nodejs\current\node.exe'                                  ,"winget_name": "OpenJS.NodeJS"                          ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "notepad++"                ,"scoop_name": "notepadplusplus"                   ,"scoop_path": r'C:\Users\nahid\scoop\apps\notepadplusplus\current\notepad++.exe'                    ,"winget_name": "Notepad++.Notepad++"                    ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "OBS Studio"               ,"scoop_name": "obs-studio"                        ,"scoop_path": r'xx'                                                                                 ,"winget_name": "OBSProject.OBSStudio"                   ,"winget_path": r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"                                                                                                         } ,
{"name": "oh-my-posh"               ,"scoop_name": "oh-my-posh"                        ,"scoop_path": r'C:\Users\nahid\scoop\apps\oh-my-posh\current\oh-my-posh.exe'                        ,"winget_name": "JanDeDobbeleer.OhMyPosh"                ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "pandoc"                   ,"scoop_name": "pandoc"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\pandoc\current\pandoc.exe'                                ,"winget_name": "JohnMacFarlane.Pandoc"                  ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "perl [Language]"          ,"scoop_name": "perl"                              ,"scoop_path": r'C:\Users\nahid\scoop\apps\perl\current\perl\bin\perl.exe'                           ,"winget_name": "StrawberryPerl.StrawberryPerl"          ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "php [Language]"           ,"scoop_name": "php"                               ,"scoop_path": r'C:\Users\nahid\scoop\apps\php\current\php.exe'                                      ,"winget_name": ""                                       ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "PotPlayer"                ,"scoop_name": "potplayer"                         ,"scoop_path": r'xx'                                                                                 ,"winget_name": "Daum.PotPlayer"                         ,"winget_path": r"C:\Program Files\PotPlayer\PotPlayerMini64.exe"                                                                                                          } ,
{"name": "PowerShell"               ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "Microsoft.PowerShell"                   ,"winget_path": r"C:\Program Files\PowerShell\7\pwsh.exe"                                                                                                                  } ,
{"name": "PowerToys"                ,"scoop_name": "powertoys"                         ,"scoop_path": r'C:\Users\nahid\scoop\apps\PowerToys\current\PowerToys.exe'                          ,"winget_name": "Microsoft.PowerToys"                    ,"winget_path": r"C:\Users\nahid\AppData\Local\PowerToys\PowerToys.exe"                                                                                                    } ,
{"name": "ProcessExplorer"          ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "Microsoft.Sysinternals.ProcessExplorer" ,"winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Packages\Microsoft.Sysinternals.ProcessExplorer_Microsoft.Winget.Source_8wekyb3d8bbwe\process-explorer.exe"} ,
{"name": "Prowlarr"                 ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "TeamProwlarr.Prowlarr"                  ,"winget_path": r"C:\ProgramData\Prowlarr\bin\Prowlarr.exe"                                                                                                                } ,
{"name": "Python"                   ,"scoop_name": "python"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\python\current\python.exe'                                ,"winget_name": "Python.Python.3.12"                     ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "qBittorrent"              ,"scoop_name": "qbittorrent"                       ,"scoop_path": r'xx'                                                                                 ,"winget_name": "qBittorrent.qBittorrent"                ,"winget_path": r"C:\Program Files\qBittorrent\qbittorrent.exe"                                                                                                            } ,
{"name": "Radarr"                   ,"scoop_name": "ScoopName"                         ,"scoop_path": r'xx'                                                                                 ,"winget_name": "TeamRadarr.Radarr"                      ,"winget_path": r"C:\ProgramData\Radarr\bin\Radarr.exe"                                                                                                                    } ,
{"name": "Rclone"                   ,"scoop_name": "rclone"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\rclone\current\rclone.exe'                                ,"winget_name": "Rclone.Rclone"                          ,"winget_path": r'C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\rclone.exe'                                                                                          } ,
{"name": "ReIcon"                   ,"scoop_name": "ReIcon"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\reicon\current\ReIcon.exe'                                ,"winget_name": ""                                       ,"winget_path": r""                                                                                                                                                        } ,
{"name": "Rss Guard"                ,"scoop_name": "rssguard"                          ,"scoop_path": r'C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe'                            ,"winget_name": "martinrotter.RSSGuard"                  ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "Ruffle"                   ,"scoop_name": "ruffle-nightly"                    ,"scoop_path": r'C:\Users\nahid\scoop\apps\ruffle-nightly\current\ruffle.exe'                        ,"winget_name": "xx"                                     ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "Rufus"                    ,"scoop_name": "rufus"                             ,"scoop_path": r'C:\Users\nahid\scoop\apps\rufus\current\rufus.exe'                                  ,"winget_name": "Rufus.Rufus"                            ,"winget_path": r"C:\Users\nahid\AppData\Local\Microsoft\WinGet\Links\rufus.exe"                                                                                           } ,
{"name": "scoop-completion"         ,"scoop_name": "scoop-completion"                  ,"scoop_path": r'C:\Users\nahid\scoop\apps\scoop-completion\current\scoop-completion.psm1'           ,"winget_name": ""                                       ,"winget_path": r""                                                                                                                                                        } ,
{"name": "scoop-search"             ,"scoop_name": "scoop-search"                      ,"scoop_path": r'C:\Users\nahid\scoop\apps\scoop-search\current\scoop-search.exe'                    ,"winget_name": ""                                       ,"winget_path": r""                                                                                                                                                        } ,
{"name": "scrcpy"                   ,"scoop_name": "scrcpy"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\scrcpy\current\scrcpy.exe'                                ,"winget_name": "Genymobile.scrcpy"                      ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "scrcpy+"                  ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "Frontesque.scrcpy+"                     ,"winget_path": r"C:\Users\nahid\AppData\Local\Programs\scrcpy-plus\scrcpy+.exe"                                                                                           } ,
{"name": "Sonarr"                   ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "TeamSonarr.Sonarr"                      ,"winget_path": r"C:\ProgramData\Sonarr\bin\Sonarr.exe"                                                                                                                    } ,
{"name": "Steam"                    ,"scoop_name": "steam"                             ,"scoop_path": r'xx'                                                                                 ,"winget_name": "Valve.Steam"                            ,"winget_path": r"C:\Program Files (x86)\Steam\steam.exe"                                                                                                                  } ,
{"name": "Syncthing"                ,"scoop_name": "syncthing"                         ,"scoop_path": r'C:\Users\nahid\scoop\apps\syncthing\current\syncthing.exe'                          ,"winget_name": "Syncthing.Syncthing"                    ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "tldr"                     ,"scoop_name": "tldr"                              ,"scoop_path": r'C:\Users\nahid\scoop\apps\tldr\current\tldr.exe'                                    ,"winget_name": "tldr-pages.tlrc"                        ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "VCredist-aio"             ,"scoop_name": "vcredist-aio"                      ,"scoop_path": r'C:\Users\nahid\scoop\apps\vcredist-aio\current\VisualCppRedist_AIO_x86_x64.exe'     ,"winget_name": "abbodi1406.vcredist"                    ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "VirtualBox"               ,"scoop_name": "virtualbox-with-extension-pack-np" ,"scoop_path": r'C:\Users\nahid\scoop\apps\virtualbox-with-extension-pack-np\current\VirtualBox.exe' ,"winget_name": "Oracle.VirtualBox"                      ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "VSCode"                   ,"scoop_name": "vscode"                            ,"scoop_path": r''                                                                                   ,"winget_name": "Microsoft.VisualStudioCode"             ,"winget_path": r"C:\Users\nahid\AppData\Local\Programs\Microsoft VS Code\Code.exe"                                                                                        } ,
{"name": "WhatsApp"                 ,"scoop_name": "whatsapp"                          ,"scoop_path": r'xx'                                                                                 ,"winget_name": "9NKSQGP7F2NH"                           ,"winget_path": r"C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_2.2407.10.0_x64__cv1g1gvanyjgm\WhatsApp.exe"                                                       } ,
{"name": "WinaeroTweaker"           ,"scoop_name": "winaero-tweaker"                   ,"scoop_path": r'C:\Users\nahid\scoop\apps\winaero-tweaker\current\WinaeroTweaker.exe'               ,"winget_name": ""                                       ,"winget_path": "r"                                                                                                                                                        } ,
{"name": "windirstat"               ,"scoop_name": "windirstat"                        ,"scoop_path": r'C:\Users\nahid\scoop\apps\windirstat\current\windirstat.exe'                        ,"winget_name": "WinDirStat.WinDirStat"                  ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "winget"                   ,"scoop_name": "winget"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\winget\current\winget.exe'                                ,"winget_name": ""                                       ,"winget_path": r""                                                                                                                                                        } ,
{"name": "Wise Program Uninstaller" ,"scoop_name": ""                                  ,"scoop_path": r''                                                                                   ,"winget_name": "WiseCleaner.WiseProgramUninstaller"     ,"winget_path": r"C:\Program Files (x86)\Wise\Wise Program Uninstaller\WiseProgramUninstaller.exe"                                                                         } ,
{"name": "WizTree"                  ,"scoop_name": "WizTree"                           ,"scoop_path": r'C:\Users\nahid\scoop\apps\wiztree\current\WizTree64.exe'                            ,"winget_name": "AntibodySoftware.WizTree"               ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "WSA-pacman"               ,"scoop_name": "wsa-pacman"                        ,"scoop_path": r'C:\Users\nahid\scoop\apps\wsa-pacman\current\WSA-pacman.exe'                        ,"winget_name": "alesimula.wsa_pacman"                   ,"winget_path": "xx"                                                                                                                                                       } ,
{"name": "yt-dlp"                   ,"scoop_name": "yt-dlp"                            ,"scoop_path": r'C:\Users\nahid\scoop\apps\yt-dlp\current\yt-dlp.exe'                                ,"winget_name": "yt-dlp.yt-dlp"                          ,"winget_path": "xx"                                                                                                                                                       } ,
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
scrollbar = ttk.Scrollbar(MAIN_FRAME, orient="vertical", style="Custom.Vertical.TScrollbar")
scrollbar.pack(side="right", fill="y")

# Configure canvas to use the scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

# Configure the style of the scrollbar
style = ttk.Style()
style.theme_use("default")

# Set the background color of the scrollbar to red
style.configure("Custom.Vertical.TScrollbar", background="#c3d7ff", troughcolor="#626c80", width=25)

# Set the thickness of the outside bar to 10 pixels
style.map("Custom.Vertical.TScrollbar",
    background=[("active", "#c3d7ff")],  # Changed from blue to red
)

# Set the thickness of the inside bar to 5 pixels
style.map("Custom.Vertical.TScrollbar",
    troughcolor=[("active", "#626c80")],  # Changed from blue to red
)
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