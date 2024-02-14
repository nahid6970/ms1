# Specify the folder paths you want to monitor
$folderPaths = @("C:\ProgramData\GlassWire", "C:\Program Files (x86)\GlassWire")

# Set the output file path
$outputFilePath = "C:\size.txt"

# Add initial spacing
Add-Content -Path $outputFilePath -Value "`r`n"

# Infinite loop to run continuously
while ($true) {
    # Get current date and time in 12-hour format
    $timestamp = Get-Date -Format "yyyy-MM-dd hh:mm:ss tt"

    # Get folder sizes and format the output
    $folderSizes = $folderPaths | ForEach-Object {
        $folderPath = $_
        $folderSize = Get-ChildItem -Path $folderPath -Recurse | Measure-Object -Property Length -Sum
        "$timestamp - $($folderPath): $([math]::Round($folderSize.Sum / 1MB, 2)) MB"
    }

    # Write folder sizes to the output file
    $folderSizes | Out-File -FilePath $outputFilePath -Append

    # Sleep for 1 hour (3600 seconds)
    Start-Sleep -Seconds 10

    # Add three spaces before writing the new information
    Add-Content -Path $outputFilePath -Value "`r`n"
}
