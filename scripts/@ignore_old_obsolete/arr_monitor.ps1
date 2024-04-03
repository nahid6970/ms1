$folderPaths = @("D:\Downloads\@Sonarr", "D:\Downloads\@Radarr")
$logFile = "C:\Users\nahid\OneDrive\Desktop\Changes.log"

foreach ($folderPath in $folderPaths) {
    # Create the FileSystemWatcher object
    $watcher = New-Object System.IO.FileSystemWatcher $folderPath

    # Include subdirectories
    $watcher.IncludeSubdirectories = $true

    # Filter specific file types (optional)
    #$watcher.Filter = "*.*"

    # Register events to monitor
    $events = @("Created", "Deleted", "Renamed", "Changed")  # Added "Changed" event
    foreach ($event in $events) {
        Register-ObjectEvent $watcher $event -Action {
            # Extract information about the event
            $path = $Event.SourceEventArgs.FullPath
            $changeType = $Event.SourceEventArgs.ChangeType

            # Get timestamp in 12-hour format
            $timestamp = Get-Date -Format "yyyy-MM-dd hh:mm:ss tt"

            # Log message for renaming
            if ($event.SourceEventArgs.ChangeType -eq 'Renamed') {
                $oldPath = $Event.SourceEventArgs.OldFullPath
                $logLine = "$timestamp, $changeType, $oldPath -> $path"
            }
            else {
                # Build log message for other events
                $logLine = "$timestamp, $changeType, $path"
            }

            # Read existing content and add the new log message at the beginning
            $existingContent = Get-Content -Path $logFile -Raw
            $newContent = "$logLine`r`n$existingContent"
            Set-Content -Path $logFile -Value $newContent
        }
    }

    # Start monitoring
    $watcher.EnableRaisingEvents = $true
}

# Keep the script running
while ($true) {
    Start-Sleep -Seconds 10
}
