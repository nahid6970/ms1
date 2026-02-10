# Android Icon Generator Script
$inputImageLocation = ""
$isBatch = $false

if ($args[0]) {
    $inputImageLocation = $args[0].Replace('"', "").Trim()
    $isBatch = $true
}

do {
    if (-not $isBatch -or -not $inputImageLocation) {
        $inputImageLocation = Read-Host "Enter the location of the input image file (e.g. C:\Images\icon.png)"
    }
    
    if ([string]::IsNullOrWhiteSpace($inputImageLocation) -or $inputImageLocation.ToLower() -eq "exit") {
        break
    }

    $inputImageLocation = $inputImageLocation.Replace('"','').Trim()

    if (-not (Test-Path $inputImageLocation)) {
        Write-Host "Error: File not found at specified location!" -ForegroundColor Red
        if ($isBatch) { break }
        continue
    }

    $inputImagePath = [System.IO.Path]::GetDirectoryName($inputImageLocation)
    if ([string]::IsNullOrWhiteSpace($inputImagePath)) { $inputImagePath = "." }

    if ($isBatch) {
        $outputDirName = "Android_ICON"
    } else {
        $outputDirName = Read-Host "Enter the output directory name (default: Android_ICON)"
        if ([string]::IsNullOrWhiteSpace($outputDirName)) { $outputDirName = "Android_ICON" }
    }

    $baseOutputPath = Join-Path $inputImagePath $outputDirName
    $iconSizes = @{
        "mipmap-mdpi"    = 48
        "mipmap-hdpi"    = 72
        "mipmap-xhdpi"   = 96
        "mipmap-xxhdpi"  = 144
        "mipmap-xxxhdpi" = 192
    }

    Write-Host "`nGenerating Android icon set..." -ForegroundColor Cyan
    if (-not (Test-Path $baseOutputPath)) {
        New-Item -ItemType Directory -Path $baseOutputPath | Out-Null
    }

    $successCount = 0
    foreach ($density in $iconSizes.Keys | Sort-Object) {
        $size = $iconSizes[$density]
        $densityPath = Join-Path $baseOutputPath $density
        if (-not (Test-Path $densityPath)) {
            New-Item -ItemType Directory -Path $densityPath | Out-Null
        }
        $outputImageLocation = Join-Path $densityPath "ic_launcher.png"
        $imageMagickCommand = "magick `"$inputImageLocation`" -resize ${size}x${size}! `"$outputImageLocation`""
        Write-Host "Generating ${density}: ${size}x${size}px..." -ForegroundColor Yellow
        try {
            Invoke-Expression $imageMagickCommand
            if (Test-Path $outputImageLocation) { $successCount++ }
        } catch { }
    }

    Write-Host "`nGeneration Complete! Success: $successCount icons" -ForegroundColor Green
    
    if ($isBatch) { 
        $processAnother = "n"
    } else {
        $processAnother = Read-Host "Do you want to generate another Android icon set? (y/n)"
    }
} while ($processAnother.ToLower() -eq 'y' -or $processAnother.ToLower() -eq 'yes')

Write-Host "`nScript completed. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
