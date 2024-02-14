while ($true) {
    Write-Host -ForegroundColor Yellow "Enter the directory path (type 'exit' to quit):"

    # Get user input for directory path
    $directoryPath = Read-Host

    # Check if the user wants to exit
    if ($directoryPath -eq 'exit') {
        break
    }

    Write-Host -ForegroundColor Green "Enter the string to match in file names:"

    # Get user input for the specific string to match
    $inputString = Read-Host

    # Get the list of files in the specified directory and its subdirectories containing the input string
    $files = Get-ChildItem -Path $directoryPath -Recurse | Where-Object { $_.Name -like "*$inputString*" }

    # Display the matching files
    if ($files.Count -eq 0) {
        Write-Output "No matching files found."
    } else {
        Write-Output "Matching files:"
        $files | ForEach-Object { Write-Output $_.FullName }
    }
}
