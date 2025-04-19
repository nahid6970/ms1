$dateTime = Get-Date -Format "yyyy-MM-dd hh:mm:ss"

Add-Content -Path C:\Users\nahid\OneDrive\backup\FileListing\SonarrList.txt -Value "#########################################"
Add-Content -Path C:\Users\nahid\OneDrive\backup\FileListing\SonarrList.txt -Value "########## $dateTime ##########"
Add-Content -Path C:\Users\nahid\OneDrive\backup\FileListing\SonarrList.txt -Value "#########################################"
rclone tree 'D:\Downloads\@Sonarr' >> C:\Users\nahid\OneDrive\backup\FileListing\SonarrList.txt
Add-Content -Path C:\Users\nahid\OneDrive\backup\FileListing\SonarrList.txt -Value ("`n" * 10)


Add-Content -Path C:\Users\nahid\OneDrive\backup\FileListing\RadarrList.txt -Value "#########################################"
Add-Content -Path C:\Users\nahid\OneDrive\backup\FileListing\RadarrList.txt -Value "########## $dateTime ##########"
Add-Content -Path C:\Users\nahid\OneDrive\backup\FileListing\RadarrList.txt -Value "#########################################"
rclone tree 'D:\Downloads\@Radarr' >> C:\Users\nahid\OneDrive\backup\FileListing\RadarrList.txt
Add-Content -Path C:\Users\nahid\OneDrive\backup\FileListing\RadarrList.txt -Value ("`n" * 10)
