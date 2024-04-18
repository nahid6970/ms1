$wifiSSID = 'Mi 9T'
$blockedProcesses = @('qbittorrent', 'fdm')
$ruleName = 'BlockInternet'

# Create a firewall rule to block internet access for the specified processes
foreach ($process in $blockedProcesses) {
    New-NetFirewallRule -DisplayName "${ruleName}_${process}" -Direction Outbound -Program $process -Action Block
}

$previousConnection = Get-NetConnectionProfile

while ($true) {
    Start-Sleep -Seconds 5  # Adjust the sleep interval as needed

    $currentConnection = Get-NetConnectionProfile

    if ($currentConnection.InterfaceAlias -ne $previousConnection.InterfaceAlias) {
        # Network connection changed
        if ($currentConnection.InterfaceAlias -eq 'Wi-Fi' -and $currentConnection.SSID -eq $wifiSSID) {
            # Enable the firewall rules when connected to Wi-Fi with the specified SSID
            foreach ($process in $blockedProcesses) {
                Set-NetFirewallRule -DisplayName "${ruleName}_${process}" -Enabled True
            }
        } else {
            # Disable the firewall rules when not connected to the specified Wi-Fi or on a different network
            foreach ($process in $blockedProcesses) {
                Set-NetFirewallRule -DisplayName "${ruleName}_${process}" -Enabled False
            }
        }

        # Update the previous connection
        $previousConnection = $currentConnection
    }
}
