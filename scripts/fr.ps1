
# ███████╗ █████╗ ███╗   ███╗███████╗    ████████╗ █████╗ ██████╗
# ██╔════╝██╔══██╗████╗ ████║██╔════╝    ╚══██╔══╝██╔══██╗██╔══██╗
# ███████╗███████║██╔████╔██║█████╗         ██║   ███████║██████╔╝
# ╚════██║██╔══██║██║╚██╔╝██║██╔══╝         ██║   ██╔══██║██╔══██╗
# ███████║██║  ██║██║ ╚═╝ ██║███████╗       ██║   ██║  ██║██████╔╝
# ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═════╝
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

# Function to launch or run the selected file in the current session
function LaunchFile_currentTab {
    param (
        [string]$filePath
    )
    # Check the extension and run accordingly
    $extension = [System.IO.Path]::GetExtension($filePath).ToLower()
    if ($extension -eq ".ps1") {
        # Run PowerShell scripts
        Write-Host "Running PowerShell script: $filePath"
        & $filePath
    } elseif ($extension -eq ".bat" -or $extension -eq ".cmd") {
        # Run batch files
        Write-Host "Running batch file: $filePath"
        & cmd /c $filePath
    } elseif ($extension -eq ".exe") {
        # Run executable files
        Write-Host "Running executable: $filePath"
        & $filePath
    } else {
        # Default action for any other type of file
        Write-Host "Opening file: $filePath"
        & $filePath
    }
}

# # Function to launch or run the selected file
# function LaunchFile_newTab {
#     param (
#         [string]$filePath
#     )
#     Invoke-Item $filePath
# }

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
            LaunchFile_currentTab $_
        }
    }
}

# Call the main function
SearchDirectoriesAndFiles