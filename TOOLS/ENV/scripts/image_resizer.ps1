# Image Resizer (CLI Version)
$filePath = ""

if ($args[0]) {
    $filePath = $args[0].Replace('"', "").Trim()
} else {
    $filePath = Read-Host "Enter the location of the image file"
}

if ([string]::IsNullOrWhiteSpace($filePath) -or -not (Test-Path $filePath)) {
    Write-Host "Error: Invalid file path or file not found." -ForegroundColor Red
    Pause
    exit
}

Write-Host "Target Image: $filePath" -ForegroundColor Cyan

Write-Host "`nRESIZE MODES:"
Write-Host "1. Scale by Percentage (e.g., 50%)"
Write-Host "2. Resize to Specific Dimensions (e.g., 1920x1080)"
$mode = Read-Host "Select mode (1 or 2)"

$extension = [System.IO.Path]::GetExtension($filePath)
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($filePath)
$directory = [System.IO.Path]::GetDirectoryName($filePath)

if ($mode -eq "1") {
    $percent = Read-Host "Enter percentage (e.g., 50)"
    $percent = $percent.Replace("%", "")
    $outputPath = Join-Path $directory "$baseName`_scaled_$percent$extension"
    $magickCmd = "magick `"$filePath`" -resize $percent% `"$outputPath`""
} 
elseif ($mode -eq "2") {
    $dims = Read-Host "Enter dimensions (WidthxHeight, e.g., 800x600)"
    $outputPath = Join-Path $directory "$baseName`_resized_$dims$extension"
    # Use ! to ignore aspect ratio if requested, otherwise it preserves it by default
    $magickCmd = "magick `"$filePath`" -resize $dims `"$outputPath`""
}
else {
    Write-Host "Invalid selection." -ForegroundColor Red
    Pause
    exit
}

Write-Host "`nProcessing..." -ForegroundColor Yellow
try {
    Invoke-Expression $magickCmd
    if (Test-Path $outputPath) {
        Write-Host "Successfully saved to: $outputPath" -ForegroundColor Green
    } else {
        Write-Host "Failed to generate output file." -ForegroundColor Red
    }
}
catch {
    Write-Host "Error occurred: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
