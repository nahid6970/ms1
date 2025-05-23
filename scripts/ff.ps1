# Start with an empty array
$directories = @()

# Add directories (comment any line freely without breaking syntax)
$directories += "C:\ms1"
$directories += "C:\ms2"
$directories += "C:\ms3"
# $directories += "D:\"
# $directories += "C:\Program Files\WindowsApps"
# $directories += "C:\Users\nahid"
$directories = $directories | Where-Object { $_ -ne "" -and $_ -ne $null }


# Ignore list
$ignoreList = @(".git", ".pyc")

# Shortcut list text for F1 display
$shortcutsText = @"
Shortcuts available:
  Enter   : Open selected file in VSCode
  Ctrl-o  : Open file location in Explorer
  Ctrl-c  : Copy full file path to clipboard
  Ctrl-r  : Run file with PowerShell Start-Process
  F1      : Show this shortcuts help window
"@

# Create a temp file with shortcuts text
$tempShortcutFile = [System.IO.Path]::GetTempFileName()
Set-Content -Path $tempShortcutFile -Value $shortcutsText -Encoding UTF8

# Main function
function SearchDirectoriesAndFiles {
    Get-ChildItem -Path $directories -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch ($ignoreList -join '|') } |
        ForEach-Object { "$($_.FullName)`t$($_.DirectoryName)" } |
        fzf `
            --multi `
            --with-nth=1 `
            --delimiter="`t" `
            --preview="highlight -O ansi -l {1}" `
            --preview-window=top:30% `
            --bind "enter:execute-silent(code {+1})" `
            --bind "ctrl-o:execute-silent(explorer.exe {+2})" `
            --bind "ctrl-c:execute-silent(cmd /c echo {+1} | clip)" `
            --bind "ctrl-r:execute-silent(powershell -command Start-Process '{+1}')" `
            --bind "f1:execute-silent(cmd /c start cmd /k type `"$tempShortcutFile`" & pause)"
}

# Call main
SearchDirectoriesAndFiles
