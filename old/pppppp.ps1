# Define the search string using fzf
$searchString = & fzf --query "" --preview "echo {}"

# Directories to search
$directories = @("C:\ms1\", "C:\ms2\")

# Define the file types to ignore
$ignoreFileTypes = @(".git", ".pyc")

# File extensions to search within
$fileExtensions = @("txt", "csv", "log", "md", "ps1")  # Add more extensions if needed

# Build the Ack command
$ackCommand = "ack $searchString"

# Append directories to search
foreach ($dir in $directories) {
    $ackCommand += " $dir"
}

# Append ignore file types
foreach ($type in $ignoreFileTypes) {
    $ackCommand += " --ignore-file=$type"
}

# Search inside files with specified extensions
foreach ($ext in $fileExtensions) {
    $ackCommand += " -G '\.$ext$'"
}

# Execute the Ack command
Invoke-Expression $ackCommand
