#* Update Winget Sources
Write-Host "############################################" -ForegroundColor Blue
Write-Host "########## Winget Update --Source ##########" -ForegroundColor Blue
Write-Host "############################################" -ForegroundColor Blue
winget upgrade --source msstore
winget upgrade --source winget

Get-ExecutionPolicy -list
Set-ExecutionPolicy RemoteSigned
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Host "###############################"
Write-Host "########## PWSH Core ##########"
Write-Host "###############################"
Winget install Microsoft.PowerShell

# ** Sonarr install/setup/mklink --first let all update/not necessary now
Write-Host "############################" -ForegroundColor Blue
Write-Host "########## Sonarr ##########" -ForegroundColor Blue
Write-Host "############################" -ForegroundColor Blue
Winget install TeamSonarr.Sonarr
$SonarrFAKE="C:\ProgramData\Sonarr\sonarr.db"
$SonarrSRC ="C:\Users\nahid\OneDrive\backup\@mklink\sonarr\sonarr.db"
$SonarrEXE ="C:\ProgramData\Sonarr\bin\Sonarr.exe"
Start-Process powershell "Stop-Process -Name 'Sonarr'" -Verb Runas -Wait
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
Start-Process powershell "Stop-Process -Name 'Radarr'" -Verb Runas -Wait
Remove-Item $RadarrFAKE
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
Start-Process powershell "Stop-Process -Name 'Prowlarr'" -Verb Runas -Wait
Remove-Item $ProwlarrFAKE
New-Item -ItemType SymbolicLink -Path $ProwlarrFAKE -Target $ProwlarrSRC -Force #[pwsh]
Start-Process $ProwlarrEXE

#* Scoop Setup / Add Bucket / Install Packages
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

    scoop install ack
    scoop install adb
    scoop install bat
    scoop install capture2text
    scoop install ditto
    scoop install ffmpeg
    scoop install fzf
    scoop install highlight
    scoop install komorebi
    scoop install oh-my-posh
    scoop install rclone
    scoop install rssguard
    scoop install rufus
    scoop install scoop-completion
    scoop install scoop-search
    scoop install ventoy
    scoop install winaero-tweaker
    scoop install yt-dlp

}
Install_Scoop
Add_Buckets
Install_Packages

#* Python Packages Install
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

#* Python Functionlist Mklink
Write-Host "################################################" 
Write-Host "########## Python Functionlist MKLINK ##########" 
Write-Host "################################################" 
New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\scoop\apps\python\current\Lib\functionlist.py" -Target "C:\ms1\functionlist.py" -Force #[pwsh]

#* Jackett Setup
Write-Host "###################################" -ForegroundColor Blue
Write-Host "########## Jackett Setup ##########" -ForegroundColor Blue
Write-Host "###################################" -ForegroundColor Blue
winget install Jackett.Jackett
$jacket_FAKE_DataProtection="C:\ProgramData\Jackett\DataProtection"
$jacket_FAKE_Indexers      ="C:\ProgramData\Jackett\Indexers"
$jacket_FAKE_ServerConfig  ="C:\ProgramData\Jackett\ServerConfig.json"

$jacket_SRC_DataProtection="C:\Users\nahid\OneDrive\backup\@mklink\jackett\DataProtection"
$jacket_SRC_Indexers      ="C:\Users\nahid\OneDrive\backup\@mklink\jackett\Indexers"
$jacket_SRC_ServerConfig  ="C:\Users\nahid\OneDrive\backup\@mklink\jackett\ServerConfig.json"

$jacket_EXE="C:\ProgramData\Jackett\JackettTray.exe"

Remove-Item $jacket_FAKE_DataProtection -Verbose -Recurse
Remove-Item $jacket_FAKE_Indexers       -Verbose -Recurse
Remove-Item $jacket_FAKE_ServerConfig   -Verbose -Recurse

New-Item -ItemType SymbolicLink -Path $jacket_FAKE_DataProtection -Target $jacket_SRC_DataProtection -Force #[pwsh]
New-Item -ItemType SymbolicLink -Path $jacket_FAKE_Indexers       -Target $jacket_SRC_Indexers       -Force #[pwsh]
New-Item -ItemType SymbolicLink -Path $jacket_FAKE_ServerConfig   -Target $jacket_SRC_ServerConfig   -Force #[pwsh]

Start-Process $jacket_EXE

#* qbittorrent Setup
Write-Host "#######################################" -ForegroundColor Blue
Write-Host "########## qBittorrent Setup ##########" -ForegroundColor Blue
Write-Host "#######################################" -ForegroundColor Blue
winget install qBittorrent.qBittorrent

$qbit_FAKE_Roaming="C:\Users\nahid\AppData\Roaming\qBittorrent"
$qbit_FAKE_Local  ="C:\Users\nahid\AppData\Local\qBittorrent"
$qbit_SRC_Roaming ="C:\Users\nahid\OneDrive\backup\@mklink\qbittorrent\qBittorrent_Roaming"
$qbit_SRC_Local   ="C:\Users\nahid\OneDrive\backup\@mklink\qbittorrent\qBittorrent_Local"

Stop-Process -Name "qbittorrent"

Remove-Item $qbit_FAKE_Local   -Recurse -Force
Remove-Item $qbit_FAKE_Roaming -Recurse

New-Item -ItemType SymbolicLink -Path $qbit_FAKE_Local   -Target $qbit_SRC_Local   -Force
New-Item -ItemType SymbolicLink -Path $qbit_FAKE_Roaming -Target $qbit_SRC_Roaming -Force

#* RssGuard Setup
Write-Host "####################################"
Write-Host "########## RssGuard Setup ##########"
Write-Host "####################################"
$RssGuard_SRC_DB     ="C:\Users\nahid\OneDrive\backup\@mklink\rssguard\database"
$RssGuard_SRC_Config ="C:\Users\nahid\OneDrive\backup\@mklink\rssguard\config"
$RssGuard_FAKE_DB    ="C:\Users\nahid\scoop\apps\rssguard\current\data4\database"
$RssGuard_FAKE_Config="C:\Users\nahid\scoop\apps\rssguard\current\data4\config"
Stop-Process -Name "rssguard"
Remove-Item $RssGuard_FAKE_DB     -Recurse
Remove-Item $RssGuard_FAKE_Config -Recurse
New-Item -ItemType SymbolicLink -Path $RssGuard_FAKE_Config -Target $RssGuard_SRC_Config -Force
New-Item -ItemType SymbolicLink -Path $RssGuard_FAKE_DB     -Target $RssGuard_SRC_DB     -Force
Start-Process "C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe"

#* Install Font Jetbrainsmono
Start-Process powershell "oh-my-posh font install" -Verb Runas -Wait

#* Potplayer Register Settings
# Define the base path where your folders are located
$basePath = "C:\ms1\asset\potplayer"
# Get the most recent folder by ordering the folders by their creation time in descending order and selecting the first one
$latestFolder = Get-ChildItem -Path $basePath | Where-Object { $_.PSIsContainer } | Sort-Object CreationTime -Descending | Select-Object -First 1
# Construct the path to the .reg file within the latest folder
$regFilePath = Join-Path -Path $latestFolder.FullName -ChildPath "PotPlayerMini64.reg"
# Start the process to open the .reg file
Start-Process $regFilePath -Verbose

#* Add startup_command to run folder of Registry Editor
# Define the registry path and the value details
$registryPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
$valueName = "StartUps"
$valuePath = "C:\ms1\startup_commands.ps1"
# Add the new string value to the registry
Start-Process powershell "New-ItemProperty -Path $registryPath -Name $valueName -Value $valuePath -PropertyType String -Force" -Verb Runas -Wait
Write-Output "Registry entry created: $registryPath\$valueName with value $valuePath"

Write-Host "####################################"
Write-Host "########## Komorebi Setup ##########"
Write-Host "####################################"
Komorebic quickstart
Remove-Item "C:\Users\nahid\komorebi.json"
New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\komorebi.json" -Target "C:\ms1\asset\komorebi\komorebi.json" -Force #[pwsh]

# ** ! dont doesnt work to change cmd admin password
# net user
# whoami
# net user Administrator 182358

#// * Update all packages first from ms store

# * install first for error management
# powershell
#// scoop-search
#// scoop-completion (reset bucket or rm for error)
#// Set-PsFzfOption (comment out)
#// zoxide


# *** use wine-aero to get access of C:\Users\nahid\AppData\Local\Packages\

# run mypygui using powershell or pwsh not cmd for file path not found error

# **  grouppolicy for startup powershell XXX
#     add using reg run  and dont use ahk script to go to that directory just use it to copy regrun path 
#     then open regigry edit and copy path and add startup_command.ps1

# ** Command_history
# New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -Target "C:\Users\nahid\OneDrive\backup\ConsoleHost_history.txt" -Force #[pwsh]

#// jacket backup settings
#// https://github.com/Jackett/Jackett/issues/2576
#// qbittorrent setting
#* Ditto setting

#// *** Komorebi
#// cant directly restore first need to use 'komorebic quickstart' for init file then restore

# ** inbound and outbound
# 	glasswire - block it in both inbound and outbound no need for host config
# 	ldplayer  - only outbound maybe


<#
██╗  ██╗███████╗██╗     ██████╗ ███████╗██╗   ██╗██╗
██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██║   ██║██║
███████║█████╗  ██║     ██████╔╝█████╗  ██║   ██║██║
██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██║   ██║██║
██║  ██║███████╗███████╗██║     ██║     ╚██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝      ╚═════╝ ╚══════╝
#>

# pip install --upgrade wheel
# C:\Users\nahid\scoop\apps\python\current\python.exe -m pip install Module_Name