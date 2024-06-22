Start-Process 'python.exe' -ArgumentList 'C:\ms1\mypygui.py' -WindowStyle Hidden
Start-Process 'C:\ms1\ahkscripts.ahk'
komorebic start
Start-Process 'C:\Users\nahid\OneDrive\backup\win11-toggle-rounded-corners.exe' -ArgumentList '--disable' -Verb RunAs -WindowStyle Hidden
Start-Process -FilePath 'C:\Users\nahid\scoop\apps\ditto\current\Ditto.exe'
Start-Process -FilePath 'C:\ProgramData\Prowlarr\bin\Prowlarr.exe'
Start-Process -FilePath 'C:\ProgramData\Radarr\bin\Radarr.exe'
Start-Process -FilePath 'C:\ProgramData\Sonarr\bin\Sonarr.exe'
Start-Process -FilePath 'C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe'
Start-Process -FilePath 'C:\Users\nahid\scoop\apps\capture2text\current\Capture2Text.exe'
Start-Process 'C:\ms1\utility\NetworkCondition.ps1' -WindowStyle Hidden
cmd /c C:\Users\nahid\OneDrive\backup\usbmmidd_v2\2ndMonitor.bat
Start-Process C:\ms1\scheduled.ps1
