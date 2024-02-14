Write-Host "Example:name.*match1.*match2.*match3" -ForegroundColor black -BackgroundColor white
# Set the title of the PowerShell window
$title = "Find-Pattern"
$title = $title.PadRight($Host.UI.RawUI.WindowSize.Width - $title.Length)
$title = " " + $title + " "
$title = $title.PadRight($Host.UI.RawUI.WindowSize.Width - $title.Length)
$Host.UI.RawUI.WindowTitle = $title

# Define a function to search for files and directories
function Search-FilesAndDirectories {
    # Prompt the user to enter a search pattern
    Write-Host "Enter a search pattern to match against filenames" -ForegroundColor Green
    $searchPattern = Read-Host

    # Prompt the user to enter the drive to search
    Write-Host "Enter the drive to search" -ForegroundColor Green
    $drive = Read-Host

    # Get all files and directories in the specified drive and filter by matching names or full paths
    Get-ChildItem -Path $drive -Recurse | Where-Object { $_.Name -match $searchPattern -or $_.FullName -match $searchPattern } |
        ForEach-Object {
            Write-Output "$($_.FullName) - $($_.Length / 1MB) MB"
        }
}
# Call the function to search for files and directories
while ($true) {
    Search-FilesAndDirectories
}