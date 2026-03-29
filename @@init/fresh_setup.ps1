# Self-elevate
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Fix execution policy
Write-Host "`n[*] Fixing execution policy..." -ForegroundColor Cyan
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Step 1: Winget
Write-Host "`n[1/4] Updating winget sources..." -ForegroundColor Cyan
winget source update
winget upgrade --id Microsoft.AppInstaller --silent --accept-source-agreements --accept-package-agreements

# Step 2: PowerShell 7
Write-Host "`n[2/4] Installing PowerShell 7..." -ForegroundColor Cyan
winget install --id Microsoft.PowerShell --silent --accept-source-agreements --accept-package-agreements

# Step 3: Scoop
Write-Host "`n[3/4] Setting up Scoop..." -ForegroundColor Cyan
if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
    Invoke-RestMethod https://get.scoop.sh | Invoke-Expression
} else {
    Write-Host "Scoop already installed." -ForegroundColor Yellow
}
scoop bucket add main
scoop bucket add extras
scoop bucket add versions

# Step 4: Packages
Write-Host "`n[4/4] Installing packages..." -ForegroundColor Cyan
$pkgs = @(
    "git", "python",
    "fzf", "bat", "ripgrep", "fd", "eza",
    "oh-my-posh", "scoop-search", "scoop-completion",
    "ffmpeg", "yt-dlp", "rclone",
    "7zip", "curl", "wget", "jq",
    "neovim"
)
foreach ($pkg in $pkgs) {
    scoop install $pkg
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host " Done! Restart your terminal to use all installed tools." -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Green
Read-Host "Press Enter to exit"
