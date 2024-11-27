# # if this is the first time run this script first C:\ms1\scripts\winget_scoop\scoop_list.py

# # Path to the text file containing the package list
# $packageListFile = "C:\Users\nahid\python_scoop_list_fzf.txt"

# # Set the window title
# $host.UI.RawUI.WindowTitle = "scoop🔽"

# # Keep running fzf selection until user exits (infinite loop)
# while ($true) {
#     # Use fzf to allow selection of multiple packages for installation
#     $selectedPackages = Get-Content $packageListFile | fzf -i --multi --preview 'scoop info {1}'

#     # If packages were selected
#     if ($selectedPackages) {
#         $selectedPackagesArray = $selectedPackages -split "`n"  # Split into an array in case of multiple selections
#         foreach ($package in $selectedPackagesArray) {
#             $packageName = $package.Split()[0]

#             # Open a new PowerShell window for each selected package installation
#             Start-Process pwsh -ArgumentList "-NoExit", "-Command", "scoop install $packageName"
#         }
#     } else {
#         # If no package was selected, exit the loop and close the window
#         break
#     }
# }




# Ensure the prerequisite script is run
$prerequisiteScript = "C:\ms1\scripts\winget_scoop\scoop_list.py"

# Check if the prerequisite script exists
if (Test-Path $prerequisiteScript) {
    Write-Host "Running prerequisite script: $prerequisiteScript"
    & python $prerequisiteScript
} else {
    Write-Host "Prerequisite script not found: $prerequisiteScript"
    exit 1
}

# Path to the text file containing the package list
$packageListFile = "C:\Users\nahid\python_scoop_list_fzf.txt"

# Check if the package list file exists
if (-not (Test-Path $packageListFile)) {
    Write-Host "Package list file not found: $packageListFile"
    exit 1
}

# Set the window title (use plain text to avoid encoding issues)
$host.UI.RawUI.WindowTitle = "scoop selection"

# Keep running fzf selection until user exits (infinite loop)
while ($true) {
    # Use fzf to allow selection of multiple packages for installation
    $selectedPackages = Get-Content $packageListFile | fzf -i --multi --preview 'scoop info {1}'

    # If packages were selected
    if ($selectedPackages) {
        $selectedPackagesArray = $selectedPackages -split "`n"  # Split into an array in case of multiple selections
        foreach ($package in $selectedPackagesArray) {
            $packageName = $package.Split()[0]

            # Open a new PowerShell window for each selected package installation
            Start-Process pwsh -ArgumentList "-NoExit", "-Command", "`"scoop install $packageName`""
        }
    } else {
        # If no package was selected, exit the loop and close the window
        break
    }
}
