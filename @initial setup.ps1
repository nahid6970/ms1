Write-Host "############################################" -ForegroundColor Blue
Write-Host "########## Winget Update --Source ##########" -ForegroundColor Blue
Write-Host "############################################" -ForegroundColor Blue
winget upgrade --source msstore
winget upgrade --source winget


# ** Sonarr install/setup/mklink --first let all update/not necessary now
Write-Host "############################" -ForegroundColor Blue
Write-Host "########## Sonarr ##########" -ForegroundColor Blue
Write-Host "############################" -ForegroundColor Blue
Winget install TeamSonarr.Sonarr
$SonarrFAKE="C:\ProgramData\Sonarr\sonarr.db"
$SonarrSRC ="C:\Users\nahid\OneDrive\backup\@mklink\sonarr\sonarr.db"
$SonarrEXE ="C:\ProgramData\Sonarr\bin\Sonarr.exe"
Stop-Process -Name "Sonarr"
Remove-Item $SonarrFAKE
New-Item -ItemType SymbolicLink -Path $SonarrFAKE -Target $SonarrSRC -Force #[pwsh]
Start-Process $SonarrEXE

# ** Radarr install/setup/mklink --first let all update/not necessary now
Write-Host "############################" -ForegroundColor Blue
Write-Host "########## Radarr ##########" -ForegroundColor Blue
Write-Host "############################" -ForegroundColor Blue
Winget install TeamRadarr.Radarr
$RadarrFAKE="C:\ProgramData\Radarr\radarr.db"
$RadarrSRC ="C:\Users\nahid\OneDrive\backup\@mklink\radarr\radarr.db"
$RadarrEXE ="C:\ProgramData\Radarr\bin\Radarr.exe"
Stop-Process -Name "Radarr"
New-Item -ItemType SymbolicLink -Path $RadarrFAKE -Target $RadarrSRC -Force #[pwsh]
Start-Process $RadarrEXE

# ** Prowlarr install/setup/mklink --first let all update/not necessary now
Write-Host "############################" -ForegroundColor Blue
Write-Host "######### Prowlarr #########" -ForegroundColor Blue
Write-Host "############################" -ForegroundColor Blue
Winget install TeamProwlarr.Prowlarr
$ProwlarrFAKE="C:\ProgramData\Prowlarr\prowlarr.db"
$ProwlarrSRC ="C:\Users\nahid\OneDrive\backup\@mklink\prowlarr\prowlarr.db"
$ProwlarrEXE ="C:\ProgramData\Prowlarr\bin\Prowlarr.exe"
Stop-Process -Name "Prowlarr"
New-Item -ItemType SymbolicLink -Path $ProwlarrFAKE -Target $ProwlarrSRC -Force #[pwsh]
Start-Process $ProwlarrEXE


Write-Host "#################################" -ForegroundColor Green
Write-Host "########## Scoop Setup ##########" -ForegroundColor Green
Write-Host "#################################" -ForegroundColor Green
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
function Install_Scoop {
    if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
        Invoke-Expression (New-Object Net.WebClient).DownloadString('https://get.scoop.sh')
    } else {
        Write-Host "Scoop is already installed. Skipping installation." -ForegroundColor Yellow
    }}
function Add_Buckets {
    scoop bucket add main
    scoop bucket add extras
    scoop bucket add versions
    scoop bucket add nonportable
    scoop config cache_path D:\@install\scoop\cache
}
function Install_Packages {
    scoop install git
    scoop install python

    scoop install rclone
    scoop install fzf
    scoop install winaero-tweaker
    scoop install scoop-search
    scoop install scoop-completion
    scoop install komorebi
    scoop install ditto
    scoop install ack
    scoop install ffmpeg
    scoop install adb
    scoop install bat
    scoop install highlight
    scoop install yt-dlp
    scoop install yt-dlp
    scoop install ventoy
    scoop install rufus
    scoop install rssguard
    scoop install oh-my-posh
    scoop install capture2text
}
Install_Scoop
Add_Buckets
Install_Packages


Write-Host "#####################################"
Write-Host "########## Python Packages ##########"
Write-Host "#####################################"
function pip_install {
    pip install cryptography
    pip install customtkinter
    pip install importlib
    pip install keyboard
    pip install pillow
    pip install psutil
    pip install pyadl
    pip install pyautogui
    pip install pycryptodomex
    pip install PyDictionary
    pip install pywin32
    pip install screeninfo
    pip install winshell
}
pip_install

# ** functionlist mklink
New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\scoop\apps\python\current\Lib\functionlist.py" -Target "C:\ms1\functionlist.py" -Force #[pwsh]


# ** ! dont doesnt work to change cmd admin password
# net user
# whoami
# net user Administrator 182358

# * Update all packages first from ms store

# * install first for error management
# powershell
# scoop-search
# scoop-completion (reset bucket or rm for error)
# Set-PsFzfOption (comment out)
# zoxide

# *** use wine-aero to get access of C:\Users\nahid\AppData\Local\Packages\

# run mypygui using powershell or pwsh not cmd for file path not found error

# **  grouppolicy for startup powershell XXX
#     add using reg run  and dont use ahk script to go to that directory just use it to copy regrun path 
#     then open regigry edit and copy path and add startup_command.ps1

# ** Command_history
# New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -Target "C:\Users\nahid\OneDrive\backup\ConsoleHost_history.txt" -Force #[pwsh]

#* jacket backup settings
#! https://github.com/Jackett/Jackett/issues/2576
#* qbittorrent setting
#* Ditto setting

# ** RssGUard (delete files first of rssguard)
# cmd /c mklink /d C:\Users\nahid\scoop\apps\rssguard\current\data4\database C:\Users\nahid\OneDrive\backup\rssguard\database
# New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\scoop\apps\rssguard\current\data4\config\config.ini" -Target "C:\Users\nahid\OneDrive\backup\rssguard\config\config.ini" -Force



# pip required packages
# pip install pillow importlib pyadl customtkinter keyboard psutil pyautogui pywin32 winshell PyDictionary cryptography pycryptodomex
# pip install pillow screeninfo


# *** Komorebi
# cant directly restore first need to use 'komorebic quickstart' for init file then restore

# ** inbound and outbound
# 	glasswire - block it in both inbound and outbound no need for host config
# 	ldplayer  - only outbound maybe