Start-Process 'C:\ms1\ahkscripts.ahk'
Start-Process  'C:\ms1\mypygui.py' -WindowStyle Hidden
komorebic start
Start-Process 'C:\ms1\utility\NetworkCondition.ps1' -WindowStyle Hidden
Start-Process 'C:\Users\nahid\OneDrive\backup\win11-toggle-rounded-corners.exe' -ArgumentList '--disable' -Verb RunAs -WindowStyle Hidden
Start-Process C:\ms1\scheduled.ps1
Start-Process -FilePath 'C:\Users\nahid\scoop\apps\ditto\current\Ditto.exe'
Start-Process -FilePath 'C:\ProgramData\Prowlarr\bin\Prowlarr.exe'
Start-Process -FilePath 'C:\ProgramData\Radarr\bin\Radarr.exe'
Start-Process -FilePath 'C:\Users\nahid\scoop\apps\rssguard\current\rssguard.exe'
Start-Process -FilePath 'C:\ProgramData\Sonarr\bin\Sonarr.exe'
