#Define Variables
$mx_src = "D:\mi9t\mx"
$mx_dst = "cgu:"

$song_src = "D:/song"
$song_dst = "gu:song"

$software_src = "D:/software"
$software_dst = "gu:/software"




$host.UI.RawUI.WindowTitle = "Sync"
for ($i = 1; ; $i++) {
    New-Variable -Name "var$i" -Value $i
    Get-Variable -Name "var$i" -ValueOnly
powershell Write-Host "STORAGE INFO" -ForegroundColor black -BackgroundColor green
    rclone about gu:
#backups of mx
powershell Write-Host "MX" -ForegroundColor black -BackgroundColor white
    rclone  sync $mx_src $mx_dst -P  --ignore-existing --transfers=1 --track-renames --exclude @ignore/ --track-renames-strategy=modtime --fast-list --max-size 1M --log-level ERROR  --log-level INFO --log-file="C:\Users\nahid\OneDrive\backup\rclone\mx.txt" #--order-by size,asc --stats-file-name-length "8"
    rclone  sync $mx_src $mx_dst -P  --ignore-existing --transfers=1 --track-renames --exclude @ignore/ --track-renames-strategy=modtime --fast-list                                  --log-level INFO --log-file="C:\Users\nahid\OneDrive\backup\rclone\mx.txt" #--order-by size,asc --stats-file-name-length "8"
#backups of song
powershell Write-Host "song" -ForegroundColor black -BackgroundColor white
    rclone sync $song_src $song_dst -P --check-first --transfers=1 --track-renames --fast-list --log-level INFO --log-file="C:\Users\nahid\OneDrive\backup\rclone\song.txt"
#backups of software
powershell Write-Host "software" -ForegroundColor black -BackgroundColor white
    rclone sync $software_src $software_dst -P --check-first --transfers=5 --track-renames --exclude @ignore/ --fast-list --max-size 1M --log-level INFO --log-file="C:\Users\nahid\OneDrive\backup\rclone\software.txt"
    rclone sync $software_src $software_dst -P --check-first --transfers=1 --track-renames --exclude @ignore/ --fast-list               --log-level INFO --log-file="C:\Users\nahid\OneDrive\backup\rclone\software.txt"
    
timeout /T 360 /NOBREAK
Clear-Host
}






#rkups of Backups
#powershell Write-Host "Backup" -ForegroundColor black -BackgroundColor white
#    rclone sync "C:\Users\nahid\OneDrive\backup"     "o0:\backup\"  -P --check-first --transfers=1 --track-renames --fast-list --stats-one-line                       # --log-level INFO  --log-file="D:\OneDrive\x.log"
#    rclone sync "C:\ms1\"   "o0:\Git\ms1\" -P --check-first --transfers=1 --track-renames --fast-list --stats-one-line      --exclude .git/  # --log-level INFO  --log-file="D:\OneDrive\x.log"
#    rclone sync "C:\ms2\"   "o0:\Git\ms2\" -P --check-first --transfers=1 --track-renames --fast-list --stats-one-line      --exclude .git/  # --log-level INFO  --log-file="D:\OneDrive\x.log"