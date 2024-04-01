$host.UI.RawUI.WindowTitle = "Backup"
Clear-Host

Write-Host -ForegroundColor green ' ██████╗  █████╗  ██████╗██╗  ██╗██╗   ██╗██████╗  '
Write-Host -ForegroundColor green ' ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██║   ██║██╔══██╗ '
Write-Host -ForegroundColor green ' ██████╔╝███████║██║     █████╔╝ ██║   ██║██████╔╝ '
Write-Host -ForegroundColor green ' ██╔══██╗██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝  '
Write-Host -ForegroundColor green ' ██████╔╝██║  ██║╚██████╗██║  ██╗╚██████╔╝██║      '
Write-Host -ForegroundColor green ' ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝      '

$FGC = [System.ConsoleColor]::green
$BGC = [System.ConsoleColor]::blue

#Installed-Apps-Backup
    # moved to update.ps1 scoop export > C:\ms1\asset\installedApps\list_scoop.txt
    # moved to update.ps1 winget export C:\ms1\asset\installedApps\list_winget.txt > C:\ms1\asset\installedApps\ex_wingetlist.txt
   # Start-Process -FilePath "winget" -ArgumentList "export C:\ms1\asset\installedApps\winget_apps.txt" -RedirectStandardOutput "C:\ms1\asset\installedApps\winget_unknown.txt" -WindowStyle Hidden #-Wait -NoNewWindow
    #winget list > C:\ms1\asset\installedApps\winget_list.txt
    #C:\ms1\scripts\scoop\scoop_list.ps1
    #Start-Process -FilePath "winget" -ArgumentList "export C:\ms1\asset\installedApps\winget_apps.txt" -RedirectStandardOutput "C:\ms1\asset\installedApps\winget_unknown.txt" #-Wait -NoNewWindow  
    #[-Wait = will wait before anyother command can be executed in the same script]
    #[-NoNewWindow = wont create any new window]
    #[-WindowStyle Hidden/minimized/maximized/normal]
Write-Host "Appslist Export ✔️" -ForegroundColor $FGC

#OrgDoc Convert to html
    pandoc -s C:\ms2\Files\MyOrg.org  -o C:\ms2\OrgDoc.html --toc
Write-Host "Pandoc Myorg ✔️" -ForegroundColor $FGC

#$emacs_src    = @( "C:\Users\nahid\AppData\Roaming\.emacs.d\config.org", "C:\Users\nahid\AppData\Roaming\.emacs.d\init.el", "C:\Users\nahid\AppData\Roaming\.emacs.d\early-init.el" )
#$nvim_src     = "C:\Users\nahid\AppData\Local\nvim\init.lua"

#$emacs_dst    = "C:\ms1\asset\emacs\"
#$nvim_dst     = "C:\ms1\asset\neovim\init.lua"


function Create_DirectoryIfNotExists { param( [string]$Path ) if (-not (Test-Path $Path -PathType Container)) { New-Item -ItemType Directory -Force -Path $Path } }

function nilesoft_shell {
    $nilesoftshell_src = @( "C:\Program Files\Nilesoft Shell\shell.nss" , "C:\Program Files\Nilesoft Shell\imports" )
    $nilesoftshell_dst = "C:\ms1\asset\nilesoft_shell"
    Create_DirectoryIfNotExists -Path $nilesoftshell_dst
    $nilesoftshell_src | ForEach-Object { Copy-Item -Path $_ -Destination $nilesoftshell_dst -Recurse -Force }
}

function Command_History {
    $history_src = "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
    $history_dst = "C:\Users\nahid\OneDrive\backup\"
    Create_DirectoryIfNotExists -Path $history_dst
    Copy-Item -Path $history_src -Destination $history_dst
}


function terminal {
    $terminal_src = "C:\Users\nahid\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
    $terminal_dst = "C:\ms1\asset\terminal\settings.json"
    Create_DirectoryIfNotExists -Path $terminal_dst
    Copy-Item -Path $terminal_src -Destination $terminal_dst
}

function rclone_config {
    $rclone_src    = "C:\Users\nahid\scoop\apps\rclone\current\rclone.conf"
    $rclone_dst    = "C:\Users\nahid\OneDrive\backup\rclone\"
    Create_DirectoryIfNotExists -Path $rclone_dst
    Copy-Item -Path $rclone_src -Destination $rclone_dst
}

function pwsh_profile  {
    $pwsh_src      = "C:\Users\nahid\OneDrive\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
    $pwsh_dst      = "C:\ms1\asset\Powershell\Microsoft.PowerShell_profile.ps1"
    # Create_DirectoryIfNotExists -Path $pwsh_dst
    Copy-Item -Path $pwsh_src -Destination $pwsh_dst
}

function sonarr {
    $sonar_src = @( "C:\ProgramData\Sonarr\sonarr.db" , "C:\ProgramData\Sonarr\config.xml" )
    $sonar_dst = "D:\software\@MustApp\@ARR\sonar_backup\"
    Create_DirectoryIfNotExists -Path $sonar_dst
    Copy-Item -Path $sonar_src -Destination $sonar_dst
}

function radarr {
    $radar_src = @( "C:\ProgramData\Radarr\radarr.db" , "C:\ProgramData\Radarr\config.xml" )
    $radar_dst = "D:\software\@MustApp\@ARR\radar_backup\"
    Create_DirectoryIfNotExists -Path $radar_dst
    Copy-Item -Path $radar_src -Destination $radar_dst
}

function prowlarr {
    $prowlar_src = @( "C:\ProgramData\Prowlarr\prowlarr.db" , "C:\ProgramData\Prowlarr\config.xml" )
    $prowlar_dst = "D:\software\@MustApp\@ARR\prowlar_backup\"
    Create_DirectoryIfNotExists -Path $prowlar_dst
    Copy-Item -Path $prowlar_src -Destination $prowlar_dst
}

function bazarr {
    $bazarr_src = @( "C:\ProgramData\Bazarr\data\db" , "C:\ProgramData\Bazarr\data\config" )
    $bazarr_dst = "D:\software\@MustApp\@ARR\bazarr_backup\"
    Create_DirectoryIfNotExists -Path $bazarr_dst
    $bazarr_src | ForEach-Object { Copy-Item -Path $_ -Destination $bazarr_dst -Recurse -Force }
}

function rssguard {
    $rssguard_src = @( "C:\Users\nahid\scoop\apps\rssguard\current\data4\config" , "C:\Users\nahid\scoop\apps\rssguard\current\data4\database" )
    $rssguard_dst = "C:\Users\nahid\OneDrive\backup\rssguard"
    Create_DirectoryIfNotExists -Path $rssguard_dst
    $rssguard_src | ForEach-Object { Copy-Item -Path $_ -Destination $rssguard_dst -Recurse -Force }
}

function espanso {
    $espanso_src = @( "C:\Users\nahid\AppData\Roaming\espanso\config\default.yml" , "C:\Users\nahid\AppData\Roaming\espanso\match\base.yml" )
    $espanso_dst = "C:\Users\nahid\OneDrive\backup\espanso\"
    Create_DirectoryIfNotExists -Path $espanso_dst
    Copy-Item -Path $espanso_src -Destination $espanso_dst -Force
}

function whisparr {
    $whisparr_src = @( "C:\ProgramData\Whisparr\config.xml" , "C:\ProgramData\Whisparr\whisparr2.db" )
    $whisparr_dst = "D:\software\@MustApp\@ARR\whisparr_backup\"
    Create_DirectoryIfNotExists -Path $whisparr_dst
    Copy-Item -Path $whisparr_src -Destination $whisparr_dst
}

function jellyfin {
    $jellyfin_src = @( "C:\ProgramData\Jellyfin\Server\config" , "C:\ProgramData\Jellyfin\Server\data\jellyfin.db" , "C:\ProgramData\Jellyfin\Server\data\library.db" )
    $jellyfin_dst = "D:\software\@MustApp\@ARR\jellyfin_backup\"
    Create_DirectoryIfNotExists -Path $jellyfin_dst
    Copy-Item -Path $jellyfin_src -Destination $jellyfin_dst -Force
}

function filezilla {
    $filezilla_src = @( "C:\ProgramData\filezilla-server\users.xml" , "C:\ProgramData\filezilla-server\allowed_ips.xml" , "C:\ProgramData\filezilla-server\disallowed_ips.xml" , "C:\ProgramData\filezilla-server\groups.xml" , "C:\ProgramData\filezilla-server\settings.xml" )
    $filezilla_dst = "C:\Users\nahid\OneDrive\backup\filezilla_server\"
    Create_DirectoryIfNotExists -Path $filezilla_dst
    Copy-Item -Path $filezilla_src -Destination $filezilla_dst -Force
}

# espanso
# filezilla
# jellyfin
# whisparr
bazarr
Command_History
prowlarr
radarr
rssguard
sonarr
pwsh_profile
rclone_config
terminal
nilesoft_shell

Write-Host "Database & configs backedup ☑️." -ForegroundColor Blue






# Git-Run
#     C:\ms1\scripts\Github\ms1u.ps1
# Write-Host "Git ms1u Update ✅" -ForegroundColor $FGC
#     C:\ms1\scripts\Github\ms2u.ps1
# Write-Host "Git ms2u Update ✅" -ForegroundColor $FGC



Set-Location
#Pause







# End of script message
Write-Host -ForegroundColor Blue "Script Ended 🎯🎯🎯 [Q to Exit]"

# Directly exit if 'q' key is pressed
while ($true) {
    $key = [System.Console]::ReadKey($true).Key
    if ($key -eq 'Q') {
        Write-Host "Exiting..."
        exit
    }
}
