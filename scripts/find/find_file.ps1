Set-Location C:\Users\

# Set the title of the PowerShell window
$title = "Find"
$title = $title.PadRight($Host.UI.RawUI.WindowSize.Width - $title.Length)
$title = " " + $title + " "
$title = $title.PadRight($Host.UI.RawUI.WindowSize.Width - $title.Length)
$Host.UI.RawUI.WindowTitle = $title
# Define a function to search for files and directories
function Search-FilesAndDirectories {
# Prompt the user to enter a filename or directory name to search for
Write-Host "Enter a filename or directory name to search for" -ForegroundColor Green
$searchTerm = Read-Host
# Prompt the user to enter the drive to search
Write-Host "Enter the drive to search" -ForegroundColor Green
$drive = Read-Host
# Get all files and directories in the specified drive and filter by matching names or full paths
Get-ChildItem -Path $drive -Recurse | Where-Object {$_.Name -like "*$searchTerm*" -or $_.FullName -like "*$searchTerm*"} | Sort-Object -Property FullName | Get-Unique -AsString | Select-Object FullName, @{Name="SizeMB";Expression={$_.Length / 1MB}} | ForEach-Object {
Write-Output "$($_.FullName) - $($_.SizeMB.ToString('0.00')) MB"
}
}
# Call the function to search for files and directories
while ($true) {
Search-FilesAndDirectories
}