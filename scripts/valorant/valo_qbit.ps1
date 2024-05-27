$host.UI.RawUI.WindowTitle = "ValoQbit"


$valorantProcessName = "VALORANT"

$qbittorrentProcessName = "qbittorrent"
$qbittorrentExePath = "C:\Program Files\qBittorrent\qbittorrent.exe"

$fdm_ProcessName = "fdm"
$fdm_Path = "C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe"

$mobileNetworkName = "Ethernet 2"  # Name of the mobile network interface


#$rssowlnixProcessName = "RSSOwlnix"
#$rssowlnixExePath = "C:\RSSOwlnix\RSSOwlnix.exe"


while ($true) {
    $valorantRunning = Get-Process -Name $valorantProcessName -ErrorAction SilentlyContinue
    $qbittorrentRunning = Get-Process -Name $qbittorrentProcessName -ErrorAction SilentlyContinue
    $fdmRunning = Get-Process -Name $fdm_ProcessName -ErrorAction SilentlyContinue
    # $rssowlnixRunning = Get-Process -Name $rssowlnixProcessName -ErrorAction SilentlyContinue

    # Check if mobile network is connected
    $mobileNetwork = Get-NetAdapter -Name $mobileNetworkName -ErrorAction SilentlyContinue
    $isMobileNetworkConnected = $mobileNetwork -and $mobileNetwork.Status -eq "Up"

    if ($valorantRunning -or $isMobileNetworkConnected) {
        if ($qbittorrentRunning) {
            Stop-Process -Name $qbittorrentProcessName
            Write-Host "$qbittorrentProcessName process closed." -BackgroundColor Red -ForegroundColor White
        }

        if ($fdmRunning) {
            Stop-Process -Name $fdm_ProcessName
            Write-Host "$fdm_ProcessName process closed." -BackgroundColor Red -ForegroundColor White
        }
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
