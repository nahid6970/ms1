param (
    [Parameter(Mandatory=$true)]
    [string]$videofolder
)
# Get the list of video files in the provided folder
$videoFiles = Get-ChildItem -Path $videofolder -Filter *.mp4
# Check if ffmpeg is installed
$ffmpegPath = "D:\software\@MustApp\ffmpeg\bin\ffmpeg.exe"
if (-not (Test-Path $ffmpegPath)) {
    Write-Host "ffmpeg not found. Please make sure ffmpeg is installed at 'C:/ffmpeg/bin/'."
    exit
}
# Set the output file path
$outputPath = Join-Path $videofolder "merged.mp4"
# Build the ffmpeg command
$command = "$ffmpegPath -y"
# Add input options for each video file
foreach ($file in $videoFiles) {
    $command += " -i `"$($file.FullName)`""
}
# Specify the filter_complex to concatenate the videos and audios
$command += " -filter_complex `"[0:v]concat=n=$($videoFiles.Count):v=1:a=1[outv][outa]`""
# Specify the lower frame rate
$command += " -map `[outv]` -map `[outa]` -r 30"
# Set the output codec and options
$command += " -c:v libx264 -c:a aac -preset veryfast -crf 18"
# Specify the output file path
$command += " `"$outputPath`""
# Execute the ffmpeg command
Write-Host "Merging videos..."
Invoke-Expression -Command $command
Write-Host "Videos merged successfully. Output file: $outputPath"