# Custom PowerShell Profile for project: Default
# Everything here is loaded when you select this project workspace dashboard.

# Force import PSReadLine in case it is disabled due to screen reader detection in PTY
Import-Module PSReadLine -ErrorAction SilentlyContinue

# Set custom project command history file
if (Get-Command Set-PSReadLineOption -ErrorAction SilentlyContinue) {
    Set-PSReadLineOption -HistorySavePath "C:/@delta/ms1/TOOLS/terminal_tui/Project_data/Default/history.txt"
}

# Clear screen cleanly to start with a clean prompt and hide startup warnings
Write-Host "$([char]0x1b)[2J$([char]0x1b)[H" -NoNewline

# Add your custom project aliases, functions, and environment variables below:
# Example:
# Set-Alias ll Get-ChildItem
