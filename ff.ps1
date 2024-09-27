# Directories to search
$directories = @(
    # $HOME
    # "C:\",
    "C:\ms1",
    "C:\ms2",
    "C:\ms3",
    "D:\",
    "C:\Users\nahid",
    ""
) | Where-Object { $_ -ne "" } # Filter out empty strings

# Ignore list for directories or files
$ignoreList = @(".git", ".pyc")

# Function to open selected file in Visual Studio Code
function OpenFileInVSCode {
    param (
        [string]$filePath
    )
    Start-Process "code" $filePath
}

# Function to launch or run the selected file
function LaunchFile {
    param (
        [string]$filePath
    )
    Invoke-Item $filePath
}

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
            LaunchFile $_
        }
    }
}

# Call the main function
SearchDirectoriesAndFiles






# Main function to search directories and files using fzf
# function SearchDirectoriesAndFiles {
#     $selectedDirectory = ($directories | fzf -m)
#     #!$selectedDirectory = ($directories)
#     if ($selectedDirectory) {
#         $files = Get-ChildItem -Path $selectedDirectory -File -Recurse | Where-Object { $_.FullName -notmatch ($ignoreList -join '|') }
#         $selectedFile = ($files.FullName | fzf -m --preview "highlight -O ansi -l {}" --preview-window=top:50% )
#         if ($selectedFile) {
#             OpenFileInVSCode $selectedFile
#         }
#     }
# }
