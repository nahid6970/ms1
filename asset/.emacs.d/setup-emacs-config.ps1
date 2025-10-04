# PowerShell script to symlink Emacs config to AppData/Roaming/.emacs.d
# Run this script as Administrator for symlink creation

param(
    [switch]$Force = $false
)

# Get current directory and target paths
$currentDir = Get-Location
$sourceFile = Join-Path $currentDir "init.el"
$emacsDir = Join-Path $env:APPDATA ".emacs.d"
$targetFile = Join-Path $emacsDir "init.el"

Write-Host "=== Emacs Configuration Symlink Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if source file exists
if (-not (Test-Path $sourceFile)) {
    Write-Host "ERROR: init.el not found in current directory!" -ForegroundColor Red
    Write-Host "Current directory: $currentDir" -ForegroundColor Yellow
    exit 1
}

Write-Host "Source file: $sourceFile" -ForegroundColor Green
Write-Host "Target location: $targetFile" -ForegroundColor Green
Write-Host ""

# Create .emacs.d directory if it doesn't exist
if (-not (Test-Path $emacsDir)) {
    Write-Host "Creating .emacs.d directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $emacsDir -Force | Out-Null
    Write-Host "Created: $emacsDir" -ForegroundColor Green
} else {
    Write-Host ".emacs.d directory already exists" -ForegroundColor Green
}

# Check if target file already exists
if (Test-Path $targetFile) {
    if ($Force) {
        Write-Host "Removing existing init.el..." -ForegroundColor Yellow
        Remove-Item $targetFile -Force
    } else {
        Write-Host "WARNING: init.el already exists at target location!" -ForegroundColor Yellow
        Write-Host "Target: $targetFile" -ForegroundColor Yellow
        $response = Read-Host "Do you want to replace it? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-Host "Operation cancelled." -ForegroundColor Yellow
            exit 0
        }
        Remove-Item $targetFile -Force
    }
}

# Create symbolic link
try {
    Write-Host "Creating symbolic link..." -ForegroundColor Yellow
    
    # Use New-Item to create symlink (requires PowerShell 5.0+)
    New-Item -ItemType SymbolicLink -Path $targetFile -Target $sourceFile -Force | Out-Null
    
    Write-Host "SUCCESS: Symbolic link created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Emacs configuration is now linked:" -ForegroundColor Cyan
    Write-Host "  Source: $sourceFile" -ForegroundColor White
    Write-Host "  Target: $targetFile" -ForegroundColor White
    Write-Host ""
    Write-Host "Any changes to init.el in this directory will automatically" -ForegroundColor Gray
    Write-Host "be reflected in your Emacs configuration." -ForegroundColor Gray
    
} catch {
    Write-Host "ERROR: Failed to create symbolic link!" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "1. Run PowerShell as Administrator" -ForegroundColor White
    Write-Host "2. Enable Developer Mode in Windows Settings" -ForegroundColor White
    Write-Host "3. Use copy instead of symlink (fallback option below)" -ForegroundColor White
    Write-Host ""
    
    # Fallback: offer to copy instead
    $fallback = Read-Host "Would you like to copy the file instead? (y/N)"
    if ($fallback -eq 'y' -or $fallback -eq 'Y') {
        Copy-Item $sourceFile $targetFile -Force
        Write-Host "File copied successfully!" -ForegroundColor Green
        Write-Host "Note: You'll need to manually copy changes in the future." -ForegroundColor Yellow
    }
    exit 1
}

Write-Host ""
Write-Host "Setup complete! You can now start Emacs and it will use this configuration." -ForegroundColor Green