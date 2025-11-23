do {
    # Ask for input image file location
    $inputImageLocation = Read-Host "Enter the location of the input image file (e.g. C:\Images\icon.png)"
    
    # Check if user wants to exit
    if ([string]::IsNullOrWhiteSpace($inputImageLocation) -or $inputImageLocation.ToLower() -eq "exit") {
        Write-Host "Exiting script..."
        break
    }
    
    # Remove any extra quotation marks from the input image path
    $inputImageLocation = $inputImageLocation.Replace('"','').Trim()
    
    # Check if file exists
    if (-not (Test-Path $inputImageLocation)) {
        Write-Host "Error: File not found at specified location!" -ForegroundColor Red
        continue
    }
    
    # Get the directory of the input image
    $inputImagePath = [System.IO.Path]::GetDirectoryName($inputImageLocation)
    
    # Ask for output directory name
    $outputDirName = Read-Host "Enter the output directory name (default: Android_ICON)"
    if ([string]::IsNullOrWhiteSpace($outputDirName)) {
        $outputDirName = "Android_ICON"
    }
    
    # Create base output directory
    $baseOutputPath = Join-Path $inputImagePath $outputDirName
    
    # Define Android icon densities and sizes
    $iconSizes = @{
        "mipmap-mdpi"    = 48
        "mipmap-hdpi"    = 72
        "mipmap-xhdpi"   = 96
        "mipmap-xxhdpi"  = 144
        "mipmap-xxxhdpi" = 192
    }
    
    Write-Host "`nGenerating Android icon set..." -ForegroundColor Cyan
    Write-Host "Output directory: $baseOutputPath`n" -ForegroundColor Cyan
    
    # Create base directory if it doesn't exist
    if (-not (Test-Path $baseOutputPath)) {
        New-Item -ItemType Directory -Path $baseOutputPath | Out-Null
        Write-Host "Created directory: $baseOutputPath" -ForegroundColor Green
    }
    
    $successCount = 0
    $failCount = 0
    
    # Generate icons for each density
    foreach ($density in $iconSizes.Keys | Sort-Object) {
        $size = $iconSizes[$density]
        $densityPath = Join-Path $baseOutputPath $density
        
        # Create density folder
        if (-not (Test-Path $densityPath)) {
            New-Item -ItemType Directory -Path $densityPath | Out-Null
            Write-Host "Created directory: $densityPath" -ForegroundColor Green
        }
        
        # Set output file path
        $outputImageLocation = Join-Path $densityPath "ic_launcher.png"
        
        # Construct ImageMagick command
        $imageMagickCommand = "magick `"$inputImageLocation`" -resize ${size}x${size}! `"$outputImageLocation`""
        
        Write-Host "Generating ${density}: ${size}x${size}px..." -ForegroundColor Yellow
        
        try {
            # Execute the ImageMagick command
            Invoke-Expression $imageMagickCommand
            
            # Check if output file was created
            if (Test-Path $outputImageLocation) {
                Write-Host "  ✓ Success: $outputImageLocation" -ForegroundColor Green
                $successCount++
            } else {
                Write-Host "  ✗ Error: Output file was not created" -ForegroundColor Red
                $failCount++
            }
        }
        catch {
            Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
    
    # Summary
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Generation Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Success: $successCount icons" -ForegroundColor Green
    Write-Host "Failed: $failCount icons" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
    Write-Host "Output location: $baseOutputPath" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # Ask if user wants to process another image
    $processAnother = Read-Host "Do you want to generate another Android icon set? (y/n)"
    
} while ($processAnother.ToLower() -eq 'y' -or $processAnother.ToLower() -eq 'yes')

Write-Host "`nScript completed. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
