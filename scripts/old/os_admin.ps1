# Check if the script is running with administrator privileges
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    # Relaunch the script with admin rights
    Start-Process powershell -ArgumentList "Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`"' -Verb RunAs" -Verb RunAs
    exit
}

# Run the target script as admin
& "C:\ms1\os.ps1"
