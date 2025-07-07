# Get the directory where the script is located
$scriptDirectory = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

# Define the HTML file path relative to the script directory
$htmlFilePath = Join-Path -Path $scriptDirectory -ChildPath "1.html"

# Read in the HTML file
$html = Get-Content -Path $htmlFilePath -Raw

# Replace the tags and attributes in the HTML
$html = $html -replace "<DL><p>", "" `
             -replace "</DL><p>", "</div></div>" `
             -replace "<DT><H3>", '<div class="flex-container"><div class="box"> <H3>' `

# Write the modified HTML back to the file
Set-Content -Path $htmlFilePath -Value $html -Encoding utf8


# Get the directory where the script is located
$scriptDirectory = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
# Define the file path relative to the script directory
$filePath = Join-Path -Path $scriptDirectory -ChildPath "1.html"
# Read the file content
$fileContent = Get-Content -Path $filePath
# Remove the first 9 lines and store the rest
$remainingContent = $fileContent | Select-Object -Skip 9
# Write the remaining content back to the file
$remainingContent | Set-Content -Path $filePath -Encoding utf8


# Get the directory where the script is located
$scriptDirectory = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
# Define the file path relative to the script directory
$filePath = Join-Path -Path $scriptDirectory -ChildPath "1.html"
# Define the lines to be added at the top
$newLines = @(
    '<!DOCTYPE html>',
    '<html>',
    '<head>',
    '<title>HomePage</title>',
    '<link rel="shortcut icon" href="https://cdn-icons-png.flaticon.com/512/4021/4021539.png" type="image/x-icon">',
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    '<link rel="stylesheet"  href="style//style1.css" ;>',
    '</head>',
    '<body>',
    '<div class="flex-container">',
    '<div class="break">',  
    '<b><p>Bookmarks</p></b>',
    '</div>'
)
# Read the existing content of the file
$existingContent = Get-Content -Path $filePath
# Combine the new lines and existing content
$newContent = $newLines + $existingContent
# Write the combined content back to the file
$newContent | Set-Content -Path $filePath -Encoding utf8


# Get the directory where the script is located
$scriptDirectory = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
# Define the HTML file path relative to the script directory
$htmlFilePath = Join-Path -Path $scriptDirectory -ChildPath "1.html"
# Read in the HTML file
$html = Get-Content -Path $htmlFilePath -Raw
# Replace the ICON attribute with <img> tag
$html = $html -replace 'ICON="([^"]+)"', '> <img src="$1" '
#$html = $html -replace 'ICON="([^"]+)"', '> <img src="$1" />'
# Write the modified HTML back to the file
Set-Content -Path $htmlFilePath -Value $html -Encoding utf8



<# # Read in the HTML file
$html = Get-Content -Path $htmlFilePath -Raw

# Replace the ICON attribute with <img> tag
$html = $html -replace 'ICON="([^"]+)"', '> <img src="$1" '

# Convert <h3> and 2 dots <H3>.. into <details><summary>
$html = $html -replace '<H3>\.\.', '<details><summary>'

# Convert 2 dots and </h3> ..</H3> into </summary>
$html = $html -replace '\.\.</H3>', '</summary>'

# Write the modified HTML back to the file
Set-Content -Path $htmlFilePath -Value $html -Encoding utf8 #>






Pause





