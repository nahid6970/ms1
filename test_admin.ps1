$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Host "Running as Admin: $isAdmin" -ForegroundColor ($isAdmin ? "Green" : "Red")
Read-Host "Press Enter to exit"
