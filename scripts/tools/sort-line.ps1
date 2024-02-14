# Initialize an empty array to store the input lines
$lines = @()

# Read lines of input until the user enters a blank line (just presses Enter)
while ($true) {
    $line = Read-Host "Enter lines"
    if ([string]::IsNullOrWhiteSpace($line)) {
        break
    }
    $lines += $line
}

# Sort the input lines in ascending order
$sortedLines = $lines | Sort-Object

# Define ANSI escape code for green color (32)
$greenColor = [char]27 + "[32m"

# Define ANSI escape code to reset color (0)
$resetColor = [char]27 + "[0m"

# Display the sorted output with color formatting
Write-Host "Sorted output (ascending order):"
$sortedLines | ForEach-Object {
    # Replace double spaces with a placeholder before applying color
    $formattedLine = $_ -replace "  ", "##DOUBLE_SPACE##"
    Write-Host "$greenColor$formattedLine$resetColor"
}

pause
