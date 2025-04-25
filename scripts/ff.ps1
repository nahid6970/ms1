# Directories to search
$directories = @(
    "C:\ms1",
    "C:\ms2",
    "C:\ms3",
    "D:\",
    "C:\Program Files\WindowsApps",
    "C:\Users\nahid"
) | Where-Object { $_ -ne "" }

# Ignore list
$ignoreList = @(".git", ".pyc")

# Open in VS Code
function OpenFileInVSCode {
    param ([string]$filePath)
    Start-Process "code" "`"$filePath`""
}

# Open in Explorer
function OpenContainingFolder {
    param ([string]$filePath)
    $folderPath = Split-Path -Parent $filePath
    Start-Process "explorer.exe" "`"$folderPath`""
}

# Main function
function SearchDirectoriesAndFiles {
    $selectedDirectory = $directories
    if ($selectedDirectory) {
        Get-ChildItem -Path $selectedDirectory -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch ($ignoreList -join '|') } |
        ForEach-Object {
            "$($_.FullName)`t$($_.DirectoryName)"
        } | fzf --with-nth=1 --delimiter "`t" --preview "highlight -O ansi -l {1}" --preview-window=top:30% `
               --bind "ctrl-o:execute-silent(explorer.exe {2})" | ForEach-Object {
            $selected = ($_ -split "`t")[0]
            if ($selected) {
                OpenFileInVSCode $selected
            }
        }
    }
}

# Call main
SearchDirectoriesAndFiles
