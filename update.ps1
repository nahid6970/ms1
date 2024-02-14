$host.UI.RawUI.WindowTitle = "Update"

Clear-Host

Write-Host -ForegroundColor blue ' ██╗   ██╗██████╗ ██████╗  █████╗ ████████╗███████╗ '
Write-Host -ForegroundColor blue ' ██║   ██║██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔════╝ '
Write-Host -ForegroundColor blue ' ██║   ██║██████╔╝██║  ██║███████║   ██║   █████╗   '
Write-Host -ForegroundColor blue ' ██║   ██║██╔═══╝ ██║  ██║██╔══██║   ██║   ██╔══╝   '
Write-Host -ForegroundColor blue ' ╚██████╔╝██║     ██████╔╝██║  ██║   ██║   ███████╗ '
Write-Host -ForegroundColor blue '  ╚═════╝ ╚═╝     ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝ '

scoop status
scoop update
Write-Host "Scoop Status & Bucked Updated ☑️"

#Close processes for updating
#Start-Process powershell -ArgumentList "Stop-Process -Name 'PowerToys'" -Verb RunAs
#Start-Process powershell -ArgumentList "Stop-Process -Name 'simplewall'" -Verb RunAs
#Start-Process powershell -ArgumentList "Stop-Process -Name 'JackettConsole'" -Verb RunAs
# Stop-Process -Name JackettConsole
Write-Host "Apps Closed for Update ☑️"

scoop update *
scoop export > C:\Users\nahid\OneDrive\backup\installed_apps\list_scoop.txt
Write-Host "scoop updated ☑️"

#Start closed processes again
#Start-Process "C:\Users\nahid\scoop\apps\powertoys\current\PowerToys.exe"
#Start-Process "C:\Users\nahid\scoop\apps\simplewall\current\simplewall.exe"
#Start-Process "C:\Users\nahid\scoop\apps\jackett\current\JackettTray.exe"
Write-Host "Start Closed Apps ☑️"

scoop cleanup *
Write-Host "Scoop Cleanedup ☑️"

#winget source reset --force #in admin mode if faced issues
#winget source update # run as adim
#winget source update --name winget
winget upgrade --all --include-unknown
winget export C:\Users\nahid\OneDrive\backup\installed_apps\list_winget.txt > C:\Users\nahid\OneDrive\backup\installed_apps\ex_wingetlist.txt
Write-Host "Winget Upgraded ☑️"

Start-Process powershell -ArgumentList "choco upgrade all -y" -Verb RunAs 
Write-Host "Choco Upgraded ☑️"

Set-Location

Write-Host "Script Ended 🎯🎯🎯"
#Pause





# End of script message
Write-Host -ForegroundColor Blue "Script Ended 🎯🎯🎯 [Q to Exit]"

# Directly exit if 'q' key is pressed
while ($true) {
    $key = [System.Console]::ReadKey($true).Key
    if ($key -eq 'Q') {
        Write-Host "Exiting..."
        exit
    }
}
