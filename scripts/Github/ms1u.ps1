# Set-Location C:\ms1
# git status
# git add .
# git commit -m "XX"
# git push
# Set-Location


# # Set the location to the repository directory
# Set-Location C:\ms1
# # Check the status of the repository
# git status
# # Add all changes to the staging area
# git add .
# # Prompt for a commit message
# $commitMessage = Read-Host "Enter commit message"
# # Commit the changes with the provided message
# git commit -m $commitMessage
# # Push the changes to the remote repository
# git push
# # Optionally, set the location back to the original directory
# Set-Location


# # Set the location to the repository directory
# Set-Location C:\ms1
# # Check the status of the repository
# git status
# # Add all changes to the staging area
# git add .
# # Prompt for a commit message
# $commitMessage = Read-Host "Enter commit message"
# # If 'xx' is entered, generate a commit message with the list of changed files
# if ($commitMessage -eq "xx") {
#     # Get the list of changed files and extract only the file names
#     $changedFiles = git status --porcelain | ForEach-Object {
#         Split-Path $_ -Leaf  # Extract the file name from the output
#     }
#     # Join the file names into a single string
#     $fileList = $changedFiles -join ', '
#     # Create the new commit message
#     $commitMessage = "File Changed--->: $fileList"
# }
# # Commit the changes with the provided message
# git commit -m $commitMessage
# # Push the changes to the remote repository
# git push
# # Optionally, set the location back to the original directory
# Set-Location


# # Set the location to the repository directory
# Set-Location C:\ms1
# # Check the status of the repository
# git status
# # Add all changes to the staging area
# git add .
# # Prompt for a commit message
# $commitMessage = Read-Host "Enter commit message"
# # If 'xx' is entered, generate a commit message with the list of changed files
# if ($commitMessage -eq "xx") {
#     # Get the list of changed files and apply the appropriate emoji based on file extension
#     $changedFiles = git status --porcelain | ForEach-Object {
#         $fileName = Split-Path $_ -Leaf
#         # Add emoji based on file extension
#         switch -regex ($fileName) {
#             '\.py$' { "🐍 $fileName" }    # Python files
#             '\.ps1$' { " $fileName" }   # PowerShell files
#             '\.ahk$' { " $fileName" }  # AutoHotkey files
#             default { "📝 $fileName" }    # Other files
#         }
#     }
#     # Join the file names with emojis into a single string
#     $fileList = $changedFiles -join ', '

#     # Create the new commit message
#     $commitMessage = "$fileList"
# }
# # Commit the changes with the provided message
# git commit -m $commitMessage
# # Push the changes to the remote repository
# git push
# # Optionally, set the location back to the original directory
# Set-Location




# # Set the location to the repository directory
# Set-Location C:\ms1
# # Check the status of the repository
# git status
# # Add all changes to the staging area
# git add .
# # Prompt for a commit message
# $commitMessage = Read-Host "Enter commit message"
# # If 'xx' is entered, generate a commit message with the list of changed files
# if ($commitMessage -eq "xx") {
#     # Get the list of changed files and extract the filename (handle quotes and spaces)
#     $changedFiles = git status --porcelain | ForEach-Object {
#         # Regex to capture the filename part, skipping status indicators (like M, D, ??)
#         if ($_ -match '^[ MADRCU?]{2} "?(.+?)"?$') {
#             $fileName = $matches[1] # Extract the filename
#             # Add emoji based on file extension
#             switch -regex ($fileName) {
#                 '\.py$' { "🐍 $fileName" }    # Python files
#                 '\.ps1$' { "⚡ $fileName" }   # PowerShell files
#                 '\.ahk$' { "⌨️ $fileName" }  # AutoHotkey files
#                 default { "📝 $fileName" }    # Other files
#             }
#         }
#     }
#     # Join the file names with emojis into a single string
#     $fileList = $changedFiles -join ', '
#     # Create the new commit message
#     $commitMessage = "Changes made to the following files: $fileList"
# }
# # Commit the changes with the provided message
# git commit -m $commitMessage
# # Push the changes to the remote repository
# git push
# # Optionally, set the location back to the original directory
# Set-Location



# # Set the location to the repository directory
# Set-Location C:\ms1
# # Check the status of the repository
# git status
# # Add all changes to the staging area
# git add .
# # Prompt for a commit message
# $commitMessage = Read-Host "Enter commit message"
# # If 'xx' is entered, generate a commit message with the list of changed files
# if ($commitMessage -eq "xx") {
#     # Get the list of changed files and extract only the file name (handle quotes and spaces)
#     $changedFiles = git status --porcelain | ForEach-Object {
#         # Regex to capture the filename part, skipping status indicators (like M, D, ??)
#         if ($_ -match '^[ MADRCU?]{2} "?(.+?)"?$') {
#             $fullPath = $matches[1]
#             # Use Split-Path with -Leaf to get only the file name, no path
#             $fileName = Split-Path $fullPath -Leaf
#             # Add emoji based on file extension
#             switch -regex ($fileName) {
#                 '\.py$' { "🐍 $fileName" }    # Python files
#                 '\.ps1$' { " $fileName" }   # PowerShell files
#                 '\.ahk$' { " $fileName" }  # AutoHotkey files
#                 default { "📝 $fileName" }    # Other files
#             }
#         }
#     }
#     # Join the file names with emojis into a single string
#     $fileList = $changedFiles -join ', '
#     # Create the new commit message
#     $commitMessage = "$fileList"
# }
# # Commit the changes with the provided message
# git commit -m $commitMessage
# # Push the changes to the remote repository
# git push
# # Optionally, set the location back to the original directory
# Set-Location




# # Set the location to the repository directory
# Set-Location C:\ms1
# # Check the status of the repository
# git status
# # Add all changes to the staging area
# git add .
# # Prompt for a commit message
# $commitMessage = Read-Host "Enter commit message"
# # Check if 'xx' is part of the commit message
# if ($commitMessage -like "xx*") {
#     # Get the list of changed files and extract only the file name (handle quotes and spaces)
#     $changedFiles = git status --porcelain | ForEach-Object {
#         # Regex to capture the filename part, skipping status indicators (like M, D, ??)
#         if ($_ -match '^[ MADRCU?]{2} "?(.+?)"?$') {
#             $fullPath = $matches[1]
#             # Use Split-Path with -Leaf to get only the file name, no path
#             $fileName = Split-Path $fullPath -Leaf
            
#             # Add emoji based on file extension
#             switch -regex ($fileName) {
#                 '\.py$' { "🐍 $fileName" }    # Python files
#                 '\.ps1$' { " $fileName" }   # PowerShell files
#                 '\.ahk$' { " $fileName" }  # AutoHotkey files
#                 default { "📝 $fileName" }    # Other files
#             }
#         }
#     }
#     # Join the file names with emojis into a single string
#     $fileList = $changedFiles -join ', '
#     # Remove 'xx' from the original commit message and append the file list
#     $commitMessage = $commitMessage -replace '^xx', ''
#     $commitMessage = "$commitMessage 🎯FilesChanged🎯: $fileList"
# }
# # Commit the changes with the provided message
# git commit -m $commitMessage
# # Push the changes to the remote repository
# git push
# # Optionally, set the location back to the original directory
# Set-Location


# Set the location to the repository directory
Set-Location C:\ms1

# Check the status of the repository
git status

# Add all changes to the staging area
git add .

# Prompt for a commit message
$commitMessage = Read-Host "Enter commit message"

# Handle special "xx" commit message logic
if ($commitMessage -like "xx*") {
    $changedFiles = git status --porcelain | ForEach-Object {
        if ($_ -match '^[ MADRCU?]{2} "?(.+?)"?$') {
            $fullPath = $matches[1]
            $fileName = Split-Path $fullPath -Leaf
            switch -regex ($fileName) {
                '\.py$' { "🐍 $fileName" }
                '\.ps1$' { " $fileName" }
                '\.ahk$' { " $fileName" }
                default { "📝 $fileName" }
            }
        }
    }
    $fileList = $changedFiles -join ', '
    $extraComment = $commitMessage -replace '^xx', ''
    $commitMessage = if ($extraComment -ne '') { "󰅿 $extraComment $fileList" } else { "$fileList" }
}

# Commit the changes with the provided message
git commit -m $commitMessage

# Check for upstream branch configuration
$remoteBranchExists = git remote show origin | Select-String -Pattern "main tracked" -Quiet

if (-not $remoteBranchExists) {
    # Set upstream branch if not configured
    git push --set-upstream origin main
} else {
    # Attempt to pull changes before pushing
    try {
        git pull origin main
    } catch {
        # Handle divergence errors
        Write-Host "Divergent branches detected. How do you want to resolve this?"
        Write-Host "1. Merge (default)"
        Write-Host "2. Rebase"
        Write-Host "3. Fast-forward only"
        $choice = Read-Host "Enter your choice (1/2/3)"
        
        switch ($choice) {
            "2" {
                Write-Host "Rebasing..."
                git pull --rebase origin main
            }
            "3" {
                Write-Host "Fast-forwarding..."
                git pull --ff-only origin main
            }
            default {
                Write-Host "Merging..."
                git pull --no-rebase origin main
            }
        }
    }
}

# Push the changes to the remote repository
git push

Set-Location C:\ms1