function Write-GreenText {
    param([string]$Text)
    Write-Host $Text -ForegroundColor Green
}

$ffmpegPath = "D:\software\@MustApp\ffmpeg\bin\ffmpeg.exe"
if (-not (Test-Path -LiteralPath $ffmpegPath)) {
    # Fall back to ffmpeg on PATH so the script can also run on another machine.
    $ffmpegCommand = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
    if ($ffmpegCommand) {
        $ffmpegPath = $ffmpegCommand.Source
    }
    else {
        Write-Host "ffmpeg.exe was not found at '$ffmpegPath' or on PATH." -ForegroundColor Red
        Pause
        exit 1
    }
}

# Accept an optional starting folder, like trim.ps1 accepts an optional file.
$folder = if ($args.Count -gt 0) { $args[0] } else { "" }
$folder = $folder.Replace('"', '').Trim()

do {
    if (-not $folder) {
        Write-GreenText "Enter the folder containing the MP4 videos to merge"
        $folder = (Read-Host).Replace('"', '').Trim()
    }

    if (-not (Test-Path -LiteralPath $folder -PathType Container)) {
        Write-Host "Folder not found: $folder" -ForegroundColor Red
    }
    else {
        # Exclude the previous output so rerunning the script won't merge it again.
        $videoFiles = @(
            Get-ChildItem -LiteralPath $folder -File -Filter *.mp4 |
                Where-Object { $_.Name -ne "merged.mp4" } |
                Sort-Object Name
        )

        if ($videoFiles.Count -lt 2) {
            Write-Host "Please provide at least two MP4 files in the folder." -ForegroundColor Yellow
        }
        else {
            $outputPath = Join-Path $folder "merged.mp4"
            $ffmpegArgs = @("-y")
            foreach ($file in $videoFiles) {
                $ffmpegArgs += @("-i", $file.FullName)
            }

            # Reset each clip's timestamps before joining. OBS clips can have
            # timestamps that restart at zero, which breaks stream-copy joins.
            $filterParts = @()
            for ($i = 0; $i -lt $videoFiles.Count; $i++) {
                $filterParts += "[$($i):v:0]setpts=PTS-STARTPTS,format=yuv420p[v$i]"
                $filterParts += "[$($i):a:0]aresample=async=1:first_pts=0,asetpts=PTS-STARTPTS[a$i]"
            }
            $concatInputs = ""
            for ($i = 0; $i -lt $videoFiles.Count; $i++) {
                $concatInputs += "[v$i][a$i]"
            }
            $filterParts += "${concatInputs}concat=n=$($videoFiles.Count):v=1:a=1[outv][outa]"
            $filter = $filterParts -join ";"

            $videoEncoderArgs = @("-c:v", "libx264", "-preset", "veryfast", "-crf", "18")
            Write-Host "Using libx264 software encoding after correcting clip timestamps."

            $ffmpegArgs += @("-filter_complex", $filter, "-map", "[outv]", "-map", "[outa]")
            $ffmpegArgs += $videoEncoderArgs
            $ffmpegArgs += @("-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", $outputPath)

            Write-Host "Merging $($videoFiles.Count) videos from '$folder' with corrected timestamps..."
            & $ffmpegPath @ffmpegArgs
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Videos merged successfully. Output file: $outputPath" -ForegroundColor Green
            }
            else {
                Write-Host "FFmpeg failed with exit code $LASTEXITCODE." -ForegroundColor Red
            }
        }
    }

    Write-GreenText "Enter another folder to merge, or press Enter to finish"
    $folder = (Read-Host).Replace('"', '').Trim()
} while ($folder)

Pause
