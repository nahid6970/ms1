# Specify the source folder path
$sourceFolderPath = "C:\Users\nahid\scoop\apps\"

# Specify the destination text file path
$destinationFilePath = "C:\git\ms1\asset\installedApps\scoop_apps.txt"

# Get the list of folder names in the source folder, excluding "scoop"
$folderNames = Get-ChildItem -Path $sourceFolderPath -Directory | Where-Object { $_.Name -ne 'scoop' } | Select-Object -ExpandProperty Name

# Wrap the first and last folder name with double quotes
$wrappedFolderNames = '"' + ($folderNames -join '" "') + '"'

# Create a time and date stamp
$timeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Create the command with "scoop install"
$scoopInstallCommand = "scoop install " + $wrappedFolderNames

# Create the string with 5 blank lines, time and date stamp, and the command
$appendContent = "`r`n" * 5 + "Timestamp: $timeStamp`r`n" + $scoopInstallCommand

# Append the string to the destination text file
$appendContent | Out-File -FilePath $destinationFilePath -Append

# Display a message indicating success
Write-Host "Command appended to $destinationFilePath"
