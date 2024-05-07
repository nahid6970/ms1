Start-Sleep -Seconds 5



function ahkscripts            {Start-Process "C:\ms1\ahkscripts.ahk" }
function aria2c_rpc            {Start-Process -FilePath "aria2c" -ArgumentList "--enable-rpc", "--rpc-listen-all" -WindowStyle Hidden }
function capture2text          {Start-Process "C:\Users\nahid\scoop\apps\capture2text\current\Capture2Text.exe" }
function free_download_manager {Start-Process 'C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe' -WindowStyle Minimized }
function monitor_size          {Start-Process "powershell.exe" -ArgumentList "-File C:\ms1\scripts\monitor_size.ps1" -Verb RunAs -WindowStyle Hidden }
function mypygui               {Start-Process "python.exe" -ArgumentList "C:\ms1\mypygui.py" -Verb RunAs -WindowStyle Hidden }
function powertoys             {if (Test-Path "C:\Users\nahid\AppData\Local\PowerToys\PowerToys.exe") { Start-Process "C:\Users\nahid\AppData\Local\PowerToys\PowerToys.exe" } elseif (Test-Path "C:\Users\nahid\scoop\apps\PowerToys\current\PowerToys.exe") { Start-Process "C:\Users\nahid\scoop\apps\PowerToys\current\PowerToys.exe" } else { Write-Warning "PowerToys not found in either expected location." } }
function rssguard              {Start-Process "C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe" }
function rssowl                {Start-Process "C:\RSSOwlnix\RSSOwlnix.exe" -WindowStyle Minimized }
function sync                  {Start-Process "C:\ms1\sync.ps1" }
function syncthing             {Start-Process "C:\Users\nahid\scoop\apps\syncthing\current\syncthing.exe" -WindowStyle Hidden }
function valo_qbit             {Start-Process "C:\ms1\scripts\valorant\valo_qbit.ps1" -WindowStyle Hidden }

function arr_monitor           {Start-Process "C:\ms1\arr_monitor.ps1" -WindowStyle Hidden }
function bazarr                {Start-Process -FilePath "C:\ProgramData\Bazarr\WinPython\python-3.10.0\python.exe" -ArgumentList "C:\ProgramData\Bazarr\bazarr.py" -WindowStyle Hidden }
function flaresolver           {Start-Process "C:\Users\nahid\scoop\apps\flaresolverr\current\flaresolverr.exe" -WindowStyle Hidden }
function prowlarr              {C:\ProgramData\Prowlarr\bin\Prowlarr.exe }
function radarr                {C:\ProgramData\Radarr\bin\Radarr.exe }
function sonarr                {C:\ProgramData\Sonarr\bin\Sonarr.exe }

function Glaze_WM              {Start-Process 'glazewm.exe' -WindowStyle hidden }
function whkd                  {Start-Process "C:\Users\nahid\scoop\apps\whkd\current\whkd.exe" -WindowStyle Hidden }
function yasb                  {Start-Process "python.exe" -ArgumentList "C:\ms1\yasb\main.py" -WindowStyle Hidden }



# aria2c_rpc
# flaresolver
# free_download_manager
# monitor_size
# mypygui
# rssowl
# sync
# syncthing
# valo_qbit
rssguard
arr_monitor
capture2text
powertoys

# bazarr
prowlarr
radarr
sonarr

ahkscripts
# yasb
# Glaze_WM
# whkd
komorebic start

Start-Process "C:\Users\nahid\scoop\apps\workspaceutilities\current\WorkspaceUtilities.exe"
Start-Process "C:\Users\nahid\scoop\apps\ditto\current\Ditto.exe"