
# ** Sonarr install/setup/mklink first let all update
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

# ** Radarr install/setup/mklink first let all update
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

# ** Prowlarr install/setup/mklink
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

# *** use wine aero to get access of C:\Users\nahid\AppData\Local\Packages\

# run mypygui using powershell or pwsh not cmd for file path not found error

# **  grouppolicy for startup powershell XXX
#     add using reg run  and dont use ahk script to go to that directory just use it to copy regrun path 
#     then open regigry edit and copy path and add startup_command.ps1

# *** mklink
# New-Item -ItemType SymbolicLink -Path "fake" -Target "main" -Force #[pwsh]

# ** functionlist
# New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\scoop\apps\python\current\Lib\functionlist.py" -Target "C:\ms1\functionlist.py" -Force #[pwsh]

# ** Command_history
# New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" -Target "C:\Users\nahid\OneDrive\backup\ConsoleHost_history.txt" -Force #[pwsh]


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