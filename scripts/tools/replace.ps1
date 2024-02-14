# Prompt for the folder location
$folderLocation = Read-Host "Enter the folder location:"

# Get all files in the folder
$files = Get-ChildItem -Path $folderLocation

# Prompt for characters to replace
$charactersToReplace = Read-Host "Enter the characters to replace (e.g., space):"

# Prompt for replacement characters
$replacementCharacters = Read-Host "Enter the replacement characters (e.g., underscore):"

# Iterate through each file
foreach ($file in $files) {
    # Check if the file name contains the characters to replace
    if ($file.Name -match $charactersToReplace) {
        # Generate the new file name by replacing characters with the replacement characters
        $newFileName = $file.Name -replace $charactersToReplace, $replacementCharacters
        
        # Construct the new file path
        $newFilePath = Join-Path -Path $folderLocation -ChildPath $newFileName
        
        # Rename the file
        Rename-Item -Path $file.FullName -NewName $newFileName -Force
        
        Write-Host "Renamed file: $($file.Name) -> $newFileName"
    }
}

Write-Host "File renaming complete."
