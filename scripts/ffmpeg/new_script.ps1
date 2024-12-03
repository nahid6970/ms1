# Ask for input image file location
$inputImageLocation = Read-Host "Enter the location of the input image file (e.g. C:\Images\input.jpg)"
# Remove any extra quotation marks from the input image path
$inputImageLocation = $inputImageLocation.Replace('"', '').Trim()
# Ask for desired quality percentage (lower value = smaller file size, less quality)
$quality = Read-Host "Enter the desired quality percentage (e.g., 85 for 85%)"
# Get the name and path of the input image
$inputImageName = [System.IO.Path]::GetFileNameWithoutExtension($inputImageLocation)
$inputImagePath = [System.IO.Path]::GetDirectoryName($inputImageLocation)
# Get the extension of the input image
$inputImageExtension = [System.IO.Path]::GetExtension($inputImageLocation)
# Set the output image location and name
$outputImageName = "$inputImageName-optimized$inputImageExtension"
$outputImageLocation = Join-Path $inputImagePath $outputImageName
# Construct the ImageMagick command
$imageMagickCommand = "magick `"$inputImageLocation`" -quality $quality `"$outputImageLocation`""
# Execute the ImageMagick command
Invoke-Expression $imageMagickCommand
# Inform the user about the output file location
Write-Host "Optimized image saved at: $outputImageLocation"
Pause
