	# Define a function to write green text to the console
	function Write-GreenText {
		param($text)
		Write-Host $text -ForegroundColor Green
	}
	# Check if a file was passed as an argument
	if ($args.Count -gt 0) {
		# Retrieve the input file location from the argument
		$inputFileLocation = $args[0]
	}
	else {
		# Ask for input file location
		Write-GreenText "Enter the location of the input video file (e.g. C:\Videos\input.mp4)"
		$inputFileLocation = Read-Host
	}
	# Remove any extra quotation marks from the input file path
	$inputFileLocation = $inputFileLocation.Replace('"','').Trim()
	do {
		# Ask for trim parameters
		Write-GreenText "Enter the start time of the trimmed video in hh:mm:ss format"
		$startTime = Read-Host
		Write-GreenText "Enter the end time of the trimmed video in hh:mm:ss format"
		$endTime = Read-Host
		# Get the name and path of the input file
		$inputFileName = [System.IO.Path]::GetFileNameWithoutExtension($inputFileLocation)
		$inputFilePath = [System.IO.Path]::GetDirectoryName($inputFileLocation)
		# Generate a timestamp
		$timestamp = Get-Date -Format "yyyyMMddHHmmss"
		# Set the output file location and name with the timestamp
		$outputFileName = "$inputFileName-trimmed-$timestamp.mp4"
		$outputFileLocation = Join-Path $inputFilePath $outputFileName
		# Construct the FFmpeg command
		$ffmpegCommand = "ffmpeg.exe -i `"$inputFileLocation`" -ss $startTime -to $endTime -c copy `"$outputFileLocation`""
		# Execute the FFmpeg command
		Invoke-Expression $ffmpegCommand
	} while ($true)
	Pause