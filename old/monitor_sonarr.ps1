$folderPath = "D:\Downloads\@Sonarr"
$logFile = "C:\Users\nahid\OneDrive\Desktop\Sonarr_Changes.log"

# Create the FileSystemWatcher object
$watcher = New-Object System.IO.FileSystemWatcher $folderPath

# Include subdirectories
$watcher.IncludeSubdirectories = $true

# Filter specific file types (optional)
#$watcher.Filter = "*.*"

# Register events to monitor
$events = @("Created", "Deleted", "Renamed")
foreach ($event in $events) {
  Register-ObjectEvent $watcher $event -Action {
    # Extract information about the event
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType

    # Remove the prefix from the path and any leading backslashes
    $relativePath = $path -replace [regex]::Escape($folderPath), '' -replace '^\\'

    # Get timestamp in 12-hour format
    $timestamp = Get-Date -Format "yyyy-MM-dd hh:mm:ss tt"

    # Build log message
    $logLine = "$timestamp, $changeType, $relativePath"

    # Read existing content and add the new log message at the beginning
    $existingContent = Get-Content -Path $logFile -Raw
    $newContent = "$logLine`r`n$existingContent"
    Set-Content -Path $logFile -Value $newContent
  }
}

# Start monitoring
$watcher.EnableRaisingEvents = $true

# Keep the script running
while ($true) {
  Start-Sleep -Seconds 10
}