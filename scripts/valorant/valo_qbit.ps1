$host.UI.RawUI.WindowTitle = "ValoQbit"


$valorantProcessName = "VALORANT"

$qbittorrentProcessName = "qbittorrent"
$qbittorrentExePath = "C:\Program Files\qBittorrent\qbittorrent.exe"

$mobileNetworkName = "Ethernet 2"  # Name of the mobile network interface
$mobileNetworkMacAddress = "AE-DE-5C-48-14-F8"  # MAC address of the mobile network interface


#$rssowlnixProcessName = "RSSOwlnix"
#$rssowlnixExePath = "C:\RSSOwlnix\RSSOwlnix.exe"


while ($true) {
    $valorantRunning = Get-Process -Name $valorantProcessName -ErrorAction SilentlyContinue
    $qbittorrentRunning = Get-Process -Name $qbittorrentProcessName -ErrorAction SilentlyContinue
    # $rssowlnixRunning = Get-Process -Name $rssowlnixProcessName -ErrorAction SilentlyContinue

    # Check if mobile network is connected
    $mobileNetwork = Get-NetAdapter -Name $mobileNetworkName -ErrorAction SilentlyContinue
    $isMobileNetworkConnected = $mobileNetwork -and $mobileNetwork.Status -eq "Up"

    if ($valorantRunning -or $isMobileNetworkConnected) {
        if ($qbittorrentRunning) {
            Stop-Process -Name $qbittorrentProcessName
            Write-Host "$qbittorrentProcessName process closed." -BackgroundColor Red -ForegroundColor White
        }

        # if ($rssowlnixRunning) {
        #     Stop-Process -Name $rssowlnixProcessName
        #     Write-Host "$rssowlnixProcessName process closed." -BackgroundColor Red -ForegroundColor White
        # }
    } else {
        if (-not $qbittorrentRunning) {
            Start-Process -FilePath $qbittorrentExePath
            Write-Host "$qbittorrentProcessName started." -BackgroundColor Green -ForegroundColor Black
        }

        # if (-not $rssowlnixRunning) {
        #     Start-Process -FilePath $rssowlnixExePath -WindowStyle Minimized
        #     Write-Host "$rssowlnixProcessName started." -BackgroundColor Green -ForegroundColor Black
        # }
    }

    Start-Sleep -Seconds 5
}
