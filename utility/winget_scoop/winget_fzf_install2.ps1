# Function to search for packages using winget and fzf
function SearchPackages {
    $packageListFile = ".\package-list2.txt"

    # Check if the package list file exists and if it's older than 1 hour
    if (Test-Path $packageListFile) {
        $fileLastWriteTime = (Get-Item $packageListFile).LastWriteTime
        $currentTime = Get-Date
        $timeDifference = $currentTime - $fileLastWriteTime
        if ($timeDifference.TotalHours -gt 1) {
            # If the file is older than 1 hour, update the package list
            UpdatePackageList
        }
    } else {
        # If the file doesn't exist, update the package list
        UpdatePackageList
    }

    # Load the package list from the file
    $packages = Get-Content $packageListFile

    $selectedPackage = $packages | fzf #!--preview="winget show {1}" --preview-window="right:20%"

    if ($selectedPackage) {
        $packageName = ($selectedPackage -split '\s+')[0]
        $packageId = ($selectedPackage -split '\s+')[1]
        InstallPackage $packageName $packageId
    } else {
        Write-Host "No package selected."
    }
}

function UpdatePackageList {
    $packageListFile = ".\package-list2.txt"
    # Query winget search and filter out non-ASCII characters
    #!$packages = winget search "" | Where-Object { $_ -notmatch '[^\x00-\x7F]' }
    $packages = winget search " " | Where-Object { $_ -notmatch '[^\x00-\x7F]' }
    # Remove the first five rows
    $packages = $packages | Select-Object -Skip 8
    # Replace spaces with hyphens within the first 43 characters
    $packages = $packages -replace '^((?:.{1,53})\S*)', { $_.Groups[1].Value -replace '\s', '-' }
    $packages | Out-File $packageListFile -Encoding utf8
    Write-Host "Package list updated."
}


# function UpdatePackageList {
#     $packageListFile = ".\package-list2.txt"

#     $packages1 = winget search "" | Where-Object { $_ -notmatch '[^\x00-\x7F]' }
#     $packages1 = $packages1 -replace '^((?:.{1,43})\S*)', { $_.Groups[1].Value -replace '\s', '-' }

#     $packages2 = winget search " " | Where-Object { $_ -notmatch '[^\x00-\x7F]' }
#     $packages2 = $packages2 -replace '^((?:.{1,53})\S*)', { $_.Groups[1].Value -replace '\s', '-' }

#     $packages = $packages1 + $packages2
#     $packages = $packages | Select-Object -Skip 8
#     $packages | Out-File $packageListFile -Encoding utf8
#     Write-Host "Package list updated."
# }


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