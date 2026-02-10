# Ask for input file location
if ($args[0]) { $inputFileLocation = $args[0].Replace('"', "").Trim() } else { $inputFileLocation = Read-Host "Enter the location of the input video file (e.g. C:\Videos\input.mp4)" }
# Remove any extra quotation marks from the input file path
$inputFileLocation = $inputFileLocation.Replace('"','').Trim()

# Ask for conversion parameters
$quality = Read-Host "Enter the desired video quality (e.g. 240p, 360p, 480p, 720p, 1080p)"
# Guide the user to use AMF codecs for GPU acceleration
$videoCodec = Read-Host "Enter the desired video codec (e.g. h264, vp9, h264_amf, hevc_amf for AMD GPU acceleration)"
$audioCodec = Read-Host "Enter the desired audio codec (e.g. aac, mp3)"
$frameRate = Read-Host "Enter the desired frame rate (e.g. 15, 20, 25, 30, 45, 60)"

# Get the name and path of the input file
$inputFileName = [System.IO.Path]::GetFileNameWithoutExtension($inputFileLocation)
$inputFilePath = [System.IO.Path]::GetDirectoryName($inputFileLocation)

# Set the output file location and name
$outputFileName = "$inputFileName-$quality-$videoCodec-$audioCodec-$frameRate.mp4"
$outputFileLocation = Join-Path $inputFilePath $outputFileName

# Construct the FFmpeg command
# -hwaccel d3d11va is added to try and enable hardware acceleration for decoding/processing
# For encoding, ensure you select 'h264_amf' or 'hevc_amf' when prompted for $videoCodec
$ffmpegCommand = "ffmpeg.exe -hwaccel d3d11va -i `"$inputFileLocation`" -c:v $videoCodec -c:a $audioCodec -vf `"scale=-2:$quality`" -r $frameRate `"$outputFileLocation`""

# Display the command before execution
Write-Host "Executing FFmpeg command: $ffmpegCommand"

# Execute the FFmpeg command
Invoke-Expression $ffmpegCommand

# Pause the script so the user can see the output
Pause