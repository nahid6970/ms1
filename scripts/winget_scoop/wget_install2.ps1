function SearchPackages {
    $packageListFile = ".\package-list2.txt"
  
    # Check if the package list file exists and if it's older than 12 hours
    if (Test-Path $packageListFile) {
        $fileLastWriteTime = (Get-Item $packageListFile).LastWriteTime
        $currentTime = Get-Date
        $timeDifference = $currentTime - $fileLastWriteTime
        if ($timeDifference.TotalHours -gt 12) {
            # If the file is older than 12 hours, update the package list
            UpdatePackageList
        }
    } else {
        # If the file doesn't exist, update the package list
        UpdatePackageList
    }
  
    # Load the package list from the file
    $packages = Get-Content $packageListFile
  
    # Use fzf to search and select a package
    $selectedPackage = $packages | fzf # --preview="winget show {1}" --preview-window="right:20%"
  
    if ($selectedPackage) {
        # Split the selected package by spaces
        $parts = $selectedPackage -split '\s{2,}'  # Split based on two or more spaces
        $packageName = $parts[0]
        $packageId = $parts[1]
        InstallPackage $packageName $packageId
    } else {
        Write-Host "No package selected."
    }
  }
  
  function UpdatePackageList {
    $packageListFile = ".\package-list2.txt"
    # Delete the package list file if it exists
    if (Test-Path $packageListFile) {
        Remove-Item $packageListFile -Force
    }
  
    # Query winget search and filter out non-ASCII characters
    $packages = winget search " " | Where-Object { $_ -notmatch '[^\x00-\x7F]' }
    
    # Find the line where "Name" starts
    $startIndex = 2
    while ($packages[$startIndex] -notmatch "Name") {
        $startIndex++
        if ($startIndex -eq $packages.Count) {
            break
        }
    }
    
    # Skip the header lines
    $packages = $packages | Select-Object -Skip ($startIndex + 1)
  
    # Output the cleaned package list to a file
    $packages | Out-File $packageListFile -Encoding utf8
    Write-Host "Package list updated."
  }
  
  # Function to install a selected package
  function InstallPackage {
    param(
        [string]$packageName,
        [string]$packageId
    )
  
    Write-Host "Package name: $packageName"
    Write-Host "Package ID: $packageId"
    
    $confirm = Read-Host "Do you want to install this package? (Y/N)"
    if (-not $confirm -or $confirm -eq "Y" -or $confirm -eq "y") {
        $installCommand = "winget install --id $packageId"
        Invoke-Expression $installCommand
        Write-Host "Package installation initiated."
    } else {
        Write-Host "Package installation aborted."
    }
  }
  
  # Call the function to search for packages
  SearchPackages
  