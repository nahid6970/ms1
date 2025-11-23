do {
    # Ask for input image file location
    $inputImageLocation = Read-Host "Enter the location of the input image file (e.g. C:\Images\input.jpg)"
    
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
    
    do {
        # Ask for output image width and height
        $outputWidth = Read-Host "Enter the desired output image width"
        $outputHeight = Read-Host "Enter the desired output image height"
        
        # Validate input
        if (-not ($outputWidth -match '^\d+$') -or -not ($outputHeight -match '^\d+$')) {
            Write-Host "Error: Please enter valid numeric values for width and height!" -ForegroundColor Red
            continue
        }
        
        # Get the name and path of the input image
        $inputImageName = [System.IO.Path]::GetFileNameWithoutExtension($inputImageLocation)
        $inputImagePath = [System.IO.Path]::GetDirectoryName($inputImageLocation)
        
        # Get the extension of the input image
        $inputImageExtension = [System.IO.Path]::GetExtension($inputImageLocation)
        
        # Ask for output format
        Write-Host "`nCurrent format: $inputImageExtension"
        Write-Host "Available formats: .jpg, .png, .bmp, .gif, .tiff, .ico, .webp"
        $outputFormat = Read-Host "Enter desired output format (press Enter to keep current format)"
        
        # Set output format
        if ([string]::IsNullOrWhiteSpace($outputFormat)) {
            $outputFormat = $inputImageExtension
        } else {
            # Ensure format starts with a dot
            if (-not $outputFormat.StartsWith('.')) {
                $outputFormat = ".$outputFormat"
            }
        }
        
        # Set the output image location and name
        $outputImageName = "$inputImageName-${outputWidth}x${outputHeight}$outputFormat"
        $outputImageLocation = Join-Path $inputImagePath $outputImageName
        
        # Construct the ImageMagick command with the "!" for forced stretching
        $imageMagickCommand = "magick `"$inputImageLocation`" -resize ${outputWidth}x${outputHeight}! `"$outputImageLocation`""
        
        Write-Host "`nExecuting command: $imageMagickCommand" -ForegroundColor Yellow
        
        try {
            # Execute the ImageMagick command
            Invoke-Expression $imageMagickCommand
            
            # Check if output file was created
            if (Test-Path $outputImageLocation) {
                Write-Host "Success! Image saved as: $outputImageLocation" -ForegroundColor Green
            } else {
                Write-Host "Error: Output file was not created. Please check ImageMagick installation." -ForegroundColor Red
            }
        }
        catch {
            Write-Host "Error executing ImageMagick command: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        # Ask if user wants to resize the same image again
        $resizeAgain = Read-Host "`nDo you want to resize the same image with different dimensions? (y/n)"
        
    } while ($resizeAgain.ToLower() -eq 'y' -or $resizeAgain.ToLower() -eq 'yes')
    
    # Ask if user wants to process another image
    $processAnother = Read-Host "`nDo you want to process another image? (y/n)"
    
} while ($processAnother.ToLower() -eq 'y' -or $processAnother.ToLower() -eq 'yes')

Write-Host "`nScript completed. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")