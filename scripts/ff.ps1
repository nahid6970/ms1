#! ──────────────────────────────────────────────────────────────────────────────
#! Config
#! ──────────────────────────────────────────────────────────────────────────────
$directories = @(
    # $HOME
    # "C:\",
    "C:\ms1",
    "C:\ms2",
    "C:\ms3",
    "D:\",
    "C:\Program Files\WindowsApps",
    "C:\Users\nahid",
    ""
) | Where-Object { $_ -ne "" } # Filter out empty strings

# Ignore list for directories or files
$ignoreList = @(".git", ".pyc")

# Function to open selected file in Visual Studio Code
# function OpenFileInVSCode {
#     param (
#         [string]$filePath
#     )
#     Start-Process "code" $filePath
# }

function OpenFileInVSCode {
    param (
        [string]$filePath
    )
    # Surround the file path with double quotes
    Start-Process "code" "`"$filePath`""
}

#! ──────────────────────────────────────────────────────────────────────────────
#! Main
#! ──────────────────────────────────────────────────────────────────────────────

# Main function to search directories and files using fzf
function SearchDirectoriesAndFiles {
    $selectedDirectory = ($directories)
    if ($selectedDirectory) {
        # Stream files gradually to fzf using a pipeline
        Get-ChildItem -Path $selectedDirectory -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch ($ignoreList -join '|') } |
        ForEach-Object {
            $_.FullName # Print the file path to console
        } | fzf -m --preview "highlight -O ansi -l {}" --preview-window=top:30% | ForEach-Object {
            OpenFileInVSCode $_
        }
    }
}
# Call the main function
SearchDirectoriesAndFiles