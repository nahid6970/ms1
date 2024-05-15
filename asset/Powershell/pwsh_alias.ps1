function killp  {
    $processName = (Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String | fzf) -split '\s{2,}' | Select-Object -First 1; if ($processName) { Stop-Process -Name $processName -Force; Write-Host "Process $processName terminated." } else { Write-Host "No process selected." }
}

function filterfzf {
    param(
        [string]$Command,
        [string]$Text
    )

    $output = Invoke-Expression "$Command" | Out-String
    $filteredOutput = $output -split "`n" | fzf --query="$Text"
    Write-Output $filteredOutput
}

function wget_install_fzf { winget search --exact "" | fzf --multi --preview 'winget show {1}' | ForEach-Object { winget install $_.split()[0] } }
function wget_uninstall_fzf { winget list  "" | fzf --multi --preview 'winget show {1}' | ForEach-Object { winget uninstall $_.split()[0] } }

function scoop_install_fzf { winget search  "" | fzf --multi --preview 'scoop info {1}' | ForEach-Object { scoop install $_.split()[0] } }
function scoop_uninstall_fzf { scoop list  "" | fzf --multi --preview 'scoop show {1}' | ForEach-Object { scoop uninstall $_.split()[0] } }


Set-Alias trim C:\ms1\scripts\ffmpeg\trim.ps1


function ms1  { Set-Location c:\ms1\ }
function ms2  { Set-Location c:\ms2\ }
function yt {yt-dlp}
function sync { c:\ms1\sync.ps1 }
function trim { C:\Users\nahid\OneDrive\Git\ms1\scripts\ffmpeg\trim.ps1 }
function prowlarr_stop { Stop-Process -Name prowlarr }
function prowlarr      { Start-Process -FilePath "C:\ProgramData\Prowlarr\bin\Prowlarr.exe" }
function sonarr        { Start-Process -FilePath "C:\ProgramData\Sonarr\bin\Sonarr.exe" }
function sonarr_stop   { Stop-Process -Name sonarr }
function radarr        { Start-Process -FilePath "C:\ProgramData\Radarr\bin\Radarr.exe" }
function radarr_stop   { Stop-Process -Name radarr }