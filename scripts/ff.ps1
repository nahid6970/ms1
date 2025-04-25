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
          --bind "ctrl-c:execute-silent(cmd /c echo {+1} | clip)"
}


# Call main
SearchDirectoriesAndFiles
