# Set the window title
$host.UI.RawUI.WindowTitle = "NetworkCondition"

# Define the applications to watch for and the mobile network interface
$appsToWatchFor = @(
    @{
        Name = "VALORANT"
    },
    @{
        Name = "Ethernet 2"
        IsNetwork = $true
    }
)

# Define the applications to manage
$appsToManage = @(
    @{
        Name = "qbittorrent"
        Path = "C:\Program Files\qBittorrent\qbittorrent.exe"
    },
    @{
        Name = "fdm"
        Path = "C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe"
    }
)

# Main loop
while ($true) {
    # Check if any of the apps to watch for are running or if the mobile network is connected
    $triggerActive = $false
    foreach ($app in $appsToWatchFor) {
        if ($app.ContainsKey("IsNetwork") -and $app.IsNetwork) {
            $network = Get-NetAdapter -Name $app.Name -ErrorAction SilentlyContinue
            if ($network -and $network.Status -eq "Up") {
                $triggerActive = $true
                break
            }
        } else {
            $process = Get-Process -Name $app.Name -ErrorAction SilentlyContinue
            if ($process) {
                $triggerActive = $true
                break
            }
        }
    }

    # Manage the applications based on the trigger condition
    foreach ($app in $appsToManage) {
        $appRunning = Get-Process -Name $app.Name -ErrorAction SilentlyContinue
        if ($triggerActive) {
            if ($appRunning) {
                Stop-Process -Name $app.Name
                Write-Host "$($app.Name) process closed." -BackgroundColor Red -ForegroundColor White
            }
        } else {
            if (-not $appRunning) {
                Start-Process -FilePath $app.Path -WindowStyle Minimized
                Write-Host "$($app.Name) started." -BackgroundColor Green -ForegroundColor Black
            }
        }
    }

    # Wait for 5 seconds before checking again
    Start-Sleep -Seconds 5
}










# $host.UI.RawUI.WindowTitle = "NetworkCondition"

# $valorantProcessName = "VALORANT"

# $qbittorrentProcessName = "qbittorrent"
# $qbittorrentExePath = "C:\Program Files\qBittorrent\qbittorrent.exe"

# $fdm_ProcessName = "fdm"
# $fdm_Path = "C:\Users\nahid\AppData\Local\Softdeluxe\Free Download Manager\fdm.exe"

# $mobileNetworkName = "Ethernet 2"  # Name of the mobile network interface


# #$rssowlnixProcessName = "RSSOwlnix"
# #$rssowlnixExePath = "C:\RSSOwlnix\RSSOwlnix.exe"


# while ($true) {
#     $valorantRunning = Get-Process -Name $valorantProcessName -ErrorAction SilentlyContinue
#     $qbittorrentRunning = Get-Process -Name $qbittorrentProcessName -ErrorAction SilentlyContinue
#     $fdmRunning = Get-Process -Name $fdm_ProcessName -ErrorAction SilentlyContinue
#     # $rssowlnixRunning = Get-Process -Name $rssowlnixProcessName -ErrorAction SilentlyContinue

#     # Check if mobile network is connected
#     $mobileNetwork = Get-NetAdapter -Name $mobileNetworkName -ErrorAction SilentlyContinue
#     $isMobileNetworkConnected = $mobileNetwork -and $mobileNetwork.Status -eq "Up"

#     if ($valorantRunning -or $isMobileNetworkConnected) {
#         if ($qbittorrentRunning) {
#             Stop-Process -Name $qbittorrentProcessName
#             Write-Host "$qbittorrentProcessName process closed." -BackgroundColor Red -ForegroundColor White
#         }

#         if ($fdmRunning) {
#             Stop-Process -Name $fdm_ProcessName
#             Write-Host "$fdm_ProcessName process closed." -BackgroundColor Red -ForegroundColor White
#         }
#     } else {
#         if (-not $qbittorrentRunning) {
#             Start-Process -FilePath $qbittorrentExePath
#             Write-Host "$qbittorrentProcessName started." -BackgroundColor Green -ForegroundColor Black
#         }

#         if (-not $fdmRunning) {
#             Start-Process -FilePath $fdm_Path -WindowStyle Minimized
#             Write-Host "$fdm_ProcessName started." -BackgroundColor Green -ForegroundColor Black
#         }
#     }

#     Start-Sleep -Seconds 5
# }
