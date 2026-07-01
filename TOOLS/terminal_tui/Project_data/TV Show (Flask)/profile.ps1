Import-Module PSReadLine -ErrorAction SilentlyContinue
Write-Host "$([char]0x1b)[2J$([char]0x1b)[H" -NoNewline
