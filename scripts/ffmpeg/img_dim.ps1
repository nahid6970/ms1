	# # Ask for input image file location
	# $inputImageLocation = Read-Host "Enter the location of the input image file (e.g. C:\Images\input.jpg)"
	# # Remove any extra quotation marks from the input image path
	# $inputImageLocation = $inputImageLocation.Replace('"','').Trim()
	# # Ask for output image width and height
	# $outputWidth = Read-Host "Enter the desired output image width"
	# $outputHeight = Read-Host "Enter the desired output image height"
	# # Get the name and path of the input image
	# $inputImageName = [System.IO.Path]::GetFileNameWithoutExtension($inputImageLocation)
	# $inputImagePath = [System.IO.Path]::GetDirectoryName($inputImageLocation)
	# # Get the extension of the input image
	# $inputImageExtension = [System.IO.Path]::GetExtension($inputImageLocation)
	# # Set the output image location and name
	# $outputImageName = "$inputImageName-${outputWidth}x${outputHeight}$inputImageExtension"
	# $outputImageLocation = Join-Path $inputImagePath $outputImageName
	# # Construct the ImageMagick command
	# $imageMagickCommand = "magick `"$inputImageLocation`" -resize ${outputWidth}x${outputHeight} `"$outputImageLocation`""
	# # Execute the ImageMagick command
	# Invoke-Expression $imageMagickCommand
	# Pause


	# Ask for input image file location
$inputImageLocation = Read-Host "Enter the location of the input image file (e.g. C:\Images\input.jpg)"
# Remove any extra quotation marks from the input image path
$inputImageLocation = $inputImageLocation.Replace('"','').Trim()
# Ask for output image width and height
$outputWidth = Read-Host "Enter the desired output image width"
$outputHeight = Read-Host "Enter the desired output image height"
# Get the name and path of the input image
$inputImageName = [System.IO.Path]::GetFileNameWithoutExtension($inputImageLocation)
$inputImagePath = [System.IO.Path]::GetDirectoryName($inputImageLocation)
# Get the extension of the input image
$inputImageExtension = [System.IO.Path]::GetExtension($inputImageLocation)
# Set the output image location and name
$outputImageName = "$inputImageName-${outputWidth}x${outputHeight}$inputImageExtension"
$outputImageLocation = Join-Path $inputImagePath $outputImageName
# Construct the ImageMagick command with the "!" for forced stretching
$imageMagickCommand = "magick `"$inputImageLocation`" -resize ${outputWidth}x${outputHeight}! `"$outputImageLocation`""
# Execute the ImageMagick command
Invoke-Expression $imageMagickCommand
Pause
