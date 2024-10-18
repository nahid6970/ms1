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


# Set the location to the repository directory
Set-Location C:\ms1

# Check the status of the repository
git status

# Add all changes to the staging area
git add .

# Prompt for a commit message
$commitMessage = Read-Host "Enter commit message"

# If 'xx' is entered, generate a commit message with the list of changed files
if ($commitMessage -eq "xx") {
    # Get the list of changed files and apply the appropriate emoji based on file extension
    $changedFiles = git status --porcelain | ForEach-Object {
        $fileName = Split-Path $_ -Leaf
        
        # Add emoji based on file extension
        switch -regex ($fileName) {
            '\.py$' { "🎯 $fileName" }    # Python files
            '\.ps1$' { "󰨊 $fileName" }   # PowerShell files
            '\.ahk$' { "🌪️ $fileName" }  # AutoHotkey files
            default { "📝 $fileName" }    # Other files
        }
    }
    
    # Join the file names with emojis into a single string
    $fileList = $changedFiles -join ', '

    # Create the new commit message
    $commitMessage = "Changes made to the following files: $fileList"
}

# Commit the changes with the provided message
git commit -m $commitMessage

# Push the changes to the remote repository
git push

# Optionally, set the location back to the original directory
Set-Location
