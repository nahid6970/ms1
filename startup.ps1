Start-Sleep -Seconds 5

  

function ahkscripts            { Start-Process "D:\@git\ms1\ahkscripts.ahk" }
function aria2c_rpc            { Start-Process -FilePath "aria2c" -ArgumentList "--enable-rpc", "--rpc-listen-all" -WindowStyle Hidden }
function bazarr                { Start-Process -FilePath "C:\ProgramData\Bazarr\WinPython\python-3.10.0\python.exe" -ArgumentList "C:\ProgramData\Bazarr\bazarr.py" -WindowStyle Hidden }
function capture2text          { Start-Process "C:\Users\nahid\scoop\apps\capture2text\current\Capture2Text.exe" }
function flaresolver           { Start-Process "C:\Users\nahid\scoop\apps\flaresolverr\current\flaresolverr.exe" -WindowStyle Hidden }
function free_download_manager { Start-Process 'C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe' -WindowStyle Minimized }
function monitor_size          { Start-Process "powershell.exe" -ArgumentList "-File D:\@git\ms1\scripts\monitor_size.ps1" -Verb RunAs -WindowStyle Hidden }
function powertoys { if (Test-Path "C:\Program Files\PowerToys\PowerToys.exe") { Start-Process "C:\Program Files\PowerToys\PowerToys.exe" } elseif (Test-Path "C:\Users\nahid\scoop\apps\PowerToys\current\PowerToys.exe") { Start-Process "C:\Users\nahid\scoop\apps\PowerToys\current\PowerToys.exe" } else { Write-Warning "PowerToys not found in either expected location." } }
function prowlarr              { C:\ProgramData\Prowlarr\bin\Prowlarr.exe }
function radarr                { C:\ProgramData\Radarr\bin\Radarr.exe }
function radarr_monitor        { Start-Process "D:\@git\ms1\scripts\arr\radarr.ps1" -WindowStyle Hidden }
function rssowl                { Start-Process "C:\RSSOwlnix\RSSOwlnix.exe" -WindowStyle Minimized }
function sonarr                { C:\ProgramData\Sonarr\bin\Sonarr.exe }
function sonarr_monitor        { Start-Process "D:\@git\ms1\scripts\arr\sonarr.ps1" -WindowStyle Hidden }
function sync                  { Start-Process "D:\@git\ms1\sync.ps1" }
function syncthing             { Start-Process "C:\Users\nahid\scoop\apps\syncthing\current\syncthing.exe" -WindowStyle Hidden }
function valo_qbit             { Start-Process "D:\@git\ms1\scripts\valorant\valo_qbit.ps1" -WindowStyle Hidden }

<# function FunctionName  {  } #>





#  APPS  #
# aria2c_rpc
# free_download_manager
# rssowl
bazarr
capture2text
# flaresolver
powertoys
prowlarr
radarr
sonarr
syncthing



#  SCRIPT  #
# monitor_size
# valo_qbit
ahkscripts
radarr_monitor
sonarr_monitor
sync