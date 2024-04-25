# Directories to search
$directories = @("C:\ms1", "C:\ms2")

# Ignore list for directories or files
$ignoreList = @(".git", ".pyc")

# Function to open selected file in Visual Studio Code
function OpenFileInVSCode {
    param (
        [string]$filePath
    )
    Start-Process "code" $filePath
}

# Main function to search directories and files using fzf
function SearchDirectoriesAndFiles {
    $selectedDirectory = ($directories | fzf)
    if ($selectedDirectory) {
        $files = Get-ChildItem -Path $selectedDirectory -File -Recurse | Where-Object { $_.FullName -notmatch ($ignoreList -join '|') }
        $selectedFile = ($files.FullName | fzf)
        if ($selectedFile) {
            OpenFileInVSCode $selectedFile
        }
    }
}

# Call the main function
SearchDirectoriesAndFiles
