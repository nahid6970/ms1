	# Ask for input file location
	$inputFileLocation = Read-Host "Enter the location of the input video file (e.g. C:\Videos\input.mp4)"
	# Remove any extra quotation marks from the input file path
	$inputFileLocation = $inputFileLocation.Replace('"','').Trim()
	# Ask for conversion parameters
	$quality = Read-Host "Enter the desired video quality (e.g. 240p, 360p, 480p, 720p, 1080p)"
	$videoCodec = Read-Host "Enter the desired video codec (e.g. h264, vp9)"
	$audioCodec = Read-Host "Enter the desired audio codec (e.g. aac, mp3)"
	$frameRate = Read-Host "Enter the desired frame rate (e.g. 15, 20, 25, 30, 45, 60)"
	# Get the name and path of the input file
	$inputFileName = [System.IO.Path]::GetFileNameWithoutExtension($inputFileLocation)
	$inputFilePath = [System.IO.Path]::GetDirectoryName($inputFileLocation)
	# Set the output file location and name
	$outputFileName = "$inputFileName-$quality-$videoCodec-$audioCodec-$frameRate.mp4"
	$outputFileLocation = Join-Path $inputFilePath $outputFileName
	# Construct the FFmpeg command
	$ffmpegCommand = "ffmpeg.exe -i `"$inputFileLocation`" -c:v $videoCodec -c:a $audioCodec -vf `scale=-2:$quality` -r $frameRate `"$outputFileLocation`""
	# Execute the FFmpeg command
	Invoke-Expression $ffmpegCommand
	Pause