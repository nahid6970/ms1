# Path to the text file containing the package list
$packageListFile = "C:\Users\nahid\OneDrive\backup\installed_apps\python_scoop_list_fzf.txt"

# Path to a temporary file to store the last search term
$lastSearchFile = "C:\Users\nahid\OneDrive\backup\last_search_term.txt"

# Function to read the last search term from a file
function Get-LastSearchTerm {
    if (Test-Path $lastSearchFile) {
        return Get-Content $lastSearchFile
    } else {
        return ""
    }
}

# Function to save the last search term to a file
function Set-LastSearchTerm {
    param (
        [string]$searchTerm
    )
    Set-Content -Path $lastSearchFile -Value $searchTerm
}

# Set the window title
$host.UI.RawUI.WindowTitle = "scoop🔽"

while ($true) {
    # Get the last search term
    $lastSearchTerm = Get-LastSearchTerm

    # Use fzf to allow selection of multiple packages for installation, with the last search term applied
    $selectedPackages = Get-Content $packageListFile | fzf -i --multi --preview 'scoop info {1}' --query "$lastSearchTerm"

    # If packages were selected
    if ($selectedPackages) {
        $selectedPackagesArray = $selectedPackages -split "`n"  # Split into an array in case of multiple selections
        foreach ($package in $selectedPackagesArray) {
            $packageName = $package.Split()[0]

            # Open a new PowerShell window for each selected package installation
            Start-Process pwsh -ArgumentList "-NoExit", "-Command", "scoop install $packageName"
        }
    } else {
        # If no package was selected, exit the loop and close the window
        break
    }

    # Save the last search term for the next run
    $lastSearchTerm = $selectedPackages.Split("`n")[0].Trim()  # Save the first selected package name
    Set-LastSearchTerm -searchTerm $lastSearchTerm
}
