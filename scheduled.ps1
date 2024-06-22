$dateTime = Get-Date -Format "yyyy-MM-dd hh:mm:ss"

Add-Content -Path C:\ms1\FileTree.txt -Value "#########################################"
Add-Content -Path C:\ms1\FileTree.txt -Value "########## $dateTime ##########"
Add-Content -Path C:\ms1\FileTree.txt -Value "#########################################"

rclone tree 'D:\Downloads\@Sonarr' >> C:\ms1\FileTree.txt
rclone tree 'D:\Downloads\@Radarr' >> C:\ms1\FileTree.txt
