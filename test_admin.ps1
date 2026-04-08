$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "Running as Admin: YES" -ForegroundColor Green
} else {
    Write-Host "Running as Admin: NO" -ForegroundColor Red
}
Read-Host "Press Enter to exit"
