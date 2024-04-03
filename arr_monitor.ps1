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

            # Define color codes based on event type
            switch ($event.SourceEventArgs.ChangeType) {
                "Created" { $color = "#00FF00" }
                "Deleted" { $color = "#FF0000" }
                "Renamed" { $color = "#475875" }
                "Changed" { $color = "#ffdb76" }
                default { $color = "#FFFFFF" }  # Default color
            }

            # Build log message
            $logLine = "$timestamp, $changeType $color, $path"

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
