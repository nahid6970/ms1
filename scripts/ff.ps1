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
            --preview-window '~3' `
            --border `
            --layout reverse `
            --color 'bg:#1e1e2e,bg+:#313244,fg:#cdd6f4,fg+:#f5e0dc,hl:#f38ba8,hl+:#f9e2af,info:#89b4fa,prompt:#a6e3a1,pointer:#f38ba8,marker:#f9e2af,spinner:#94e2d5,header:#89b4fa,preview-bg:#1e1e2e,border:#74c7ec' `
            --bind "enter:execute-silent(code {+1})" `
            --bind "ctrl-o:execute-silent(explorer.exe /select,{+1})" `
            --bind "ctrl-c:execute-silent(cmd /c echo {+1} | clip)" `
            --bind "ctrl-r:execute-silent(powershell -command Start-Process '{+1}')" `
            --bind "f1:execute-silent(cmd /c start cmd /k type `"$tempShortcutFile`" & pause)"
}

# Call main
SearchDirectoriesAndFiles
