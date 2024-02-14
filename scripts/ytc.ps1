# Prompt for download location
$download_location = Read-Host "Enter the download location (e.g., D:\):"
if (-not (Test-Path $download_location)) {
    Write-Output "The specified download location does not exist. Exiting script."
    exit
}

# Change to the download location
cd $download_location

# Update the options to remove --output
$options = "--no-mtime"

#################### Functions ####################

# Sets $format variable based on user-inputted choice, which is used in the final command as format-related parameters
function Set-Format {
    Switch ($choice) {
        1 {Write-Output $null}
        2 {Write-Output "-f best"}
        3 {Write-Output "-f bestvideo+bestaudio/best --merge-output-format mp4"}
        4 {Write-Output -f $format --merge-output-format mp4}
        5 {Write-Output -f $format}
    }
}

# Outputs a preview of the format for user approval
function Check-Format {
    Write-Host "Output will be: " 
    Write-Host (& yt-dlp.exe $format $URL --get-format)
    Read-Host "Ok? (Enter Y/N)"
}

# For choices that require manually selecting formats using format codes (Choices 4 & 5)
function Custom-Formats {
    if ($choice -eq 4) {
        Write-Host "INSTRUCTIONS: Choose the format codes for the video and audio quality you want from the list at the top. ffmpeg must be installed, and the location specified in the batch file."
        $videoFormat = Read-Host "Video Format Code"
        $audioFormat = Read-Host "Audio Format Code"
        $chosenFormat = ${videoFormat}+"+"+${audioFormat}
        Write-Output $chosenFormat # Returns this variable out of the function
    } else { 
        if ($choice -eq 5) {
            Write-Host "INSTRUCTIONS: Choose the format code for the video or audio quality you want from the list at the top."
            $chosenFormat = Read-Host "Format Code"
            Write-Output $chosenFormat # Returns this variable out of the function
        }
    }
}

# Updates yt-dlp (must be in the same directory as the script)
function Update-Program {
    & yt-dlp.exe --update
    exit
}

# =================================== Start Main Program ===================================
Write-Output ""
Write-Output '--------------------------------- Video Downloader Script ---------------------------------'
Write-Output ""
Write-Output 'REQUIRES the yt-dlp program from: https://github.com/yt-dlp/yt-dlp'
Write-Output 'Supported Video Sites: https://ytdl-org.github.io/youtube-dl/supportedsites.html'
Write-Output ""
$URL = Read-Host "Enter video URL here"

# Lists all formats for video
Write-Output ""
& yt-dlp.exe --list-formats $URL

# While loop until the user is satisfied with the output and confirms using the Check-Format function
while ($confirm -ne "y") {
    Write-Output ""
    Write-Output "---------------------------------------------------------------------------"
    Write-Output "Options:"
    Write-Output "1. Download automatically (default is the best video + audio muxed)"
    Write-Output "2. Download the best quality single file, no mux"
    Write-Output "3. Download the highest quality audio + video formats, attempt merge to mp4"
    Write-Output "4. Let me choose the video and audio formats to combine"
    Write-Output "5. Download ONLY audio or video"
    Write-Output "6. -UPDATE PROGRAM- (Admin May Be Required)"
    Write-Output ""

    $choice = Read-Host "Type your choice number" # Takes in choice from the user
    if (($choice -eq 4) -or ($choice -eq 5)) { $format = Custom-Formats }
    if ($choice -eq 6) {Update-Program}
    $format = Set-Format
    $confirm = Check-Format
}

# Final Run
Write-Output ""
Write-Output "Running Command:   ./yt-dlp.exe $format $URL '--%' $options"
& yt-dlp.exe $format $URL '--%' $options # Final full command used on yt-dlp. I have no idea why '--%' is required in there, but without it, it won't work. Got it from an obscure StackOverflow comment
cmd /c pause
