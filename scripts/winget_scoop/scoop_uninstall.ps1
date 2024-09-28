# Set the path to the package list file (you don't need this for uninstall as you'll directly use `scoop list`)
$packageListFile = "C:\Users\nahid\OneDrive\backup\installed_apps\python_scoop_list_fzf.txt"

# Set the window title
$host.UI.RawUI.WindowTitle = "scoop🔽"

# Keep running fzf selection until the user exits (infinite loop)
while ($true) {
    # Use fzf to list and allow selection of multiple packages for uninstallation
    $selectedPackages = scoop list | fzf -i --multi --preview 'scoop info {1}'

    # If packages were selected
    if ($selectedPackages) {
        $selectedPackagesArray = $selectedPackages -split "`n"  # Split into an array in case of multiple selections
        foreach ($package in $selectedPackagesArray) {
            $packageName = $package.Split()[0]

            # Open a new PowerShell window for each selected package uninstallation
            Start-Process pwsh -ArgumentList "-NoExit", "-Command", "scoop uninstall $packageName"
        }
    } else {
        # If no package was selected, exit the loop and close the window
        break
    }
}
