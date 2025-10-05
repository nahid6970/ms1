# PowerShell script to create symbolic link for Neovim config
# This links the current init.lua to the Neovim config directory

$currentDir = Get-Location
$sourceFile = Join-Path $currentDir "init.lua"
$nvimConfigDir = "C:\Users\nahid\AppData\Local\nvim"
$targetFile = Join-Path $nvimConfigDir "init.lua"

Write-Host "Setting up Neovim configuration symbolic link..." -ForegroundColor Green

# Check if source file exists
if (-not (Test-Path $sourceFile)) {
    Write-Host "Error: init.lua not found in current directory!" -ForegroundColor Red
    Write-Host "Current directory: $currentDir" -ForegroundColor Yellow
    exit 1
}

# Create nvim config directory if it doesn't exist
if (-not (Test-Path $nvimConfigDir)) {
    Write-Host "Creating Neovim config directory: $nvimConfigDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $nvimConfigDir -Force | Out-Null
}

# Remove existing init.lua if it exists (backup first)
if (Test-Path $targetFile) {
    $backupFile = "$targetFile.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "Backing up existing init.lua to: $backupFile" -ForegroundColor Yellow
    Move-Item $targetFile $backupFile
}

# Create symbolic link
try {
    New-Item -ItemType SymbolicLink -Path $targetFile -Target $sourceFile -Force | Out-Null
    Write-Host "✓ Successfully created symbolic link!" -ForegroundColor Green
    Write-Host "  Source: $sourceFile" -ForegroundColor Cyan
    Write-Host "  Target: $targetFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your Neovim config is now linked! Start nvim to use the new configuration." -ForegroundColor Green
} catch {
    Write-Host "Error creating symbolic link: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Try running PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}