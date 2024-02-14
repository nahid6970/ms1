	# Prompt for video file location
	$videoPath = Read-Host "Enter the location of the video file"
	# Check if the video file exists
	if (-not (Test-Path $videoPath)) {
		Write-Host "The specified video file does not exist."
		exit
	}
	# Prompt for dimension options
	$dimensions = @()
	$dimensions += "1920x1080"  # Add suggested dimension option 1
	$dimensions += "1280x720"   # Add suggested dimension option 2
	$dimensions += "854x480"    # Add suggested dimension option 3
	Write-Host "Select the desired dimensions for the video:"
	for ($i = 0; $i -lt $dimensions.Count; $i++) {
		Write-Host "$($i + 1). $($dimensions[$i])"
	}
	# Prompt for dimension selection
	$selection = Read-Host "Enter the number corresponding to the desired dimensions"
	# Validate dimension selection
	if ($selection -lt 1 -or $selection -gt $dimensions.Count) {
		Write-Host "Invalid dimension selection. Exiting..."
		exit
	}
	# Get the selected dimensions
	$selectedDimensions = $dimensions[$selection - 1]
	# FFmpeg command to resize the video
	$ffmpegCommand = "ffmpeg -i `"$videoPath`" -vf `"`"scale=$selectedDimensions,setsar=1:1`"`" -c:a copy `"`"$outputPath`"`""
	# Generate output file path
	$outputPath = [System.IO.Path]::ChangeExtension($videoPath, "_resized.mp4")
	# FFmpeg path (assuming it's in the environment variable)
	$ffmpegPath = "ffmpeg"
	# Execute the FFmpeg command
	Invoke-Expression $ffmpegCommand
	Write-Host "Video conversion complete. Resized video saved to $outputPath"