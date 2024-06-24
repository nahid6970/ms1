# Set-Location C:\ms1
# git status
# git add .
# git commit -m "XX"
# git push
# Set-Location


# Set the location to the repository directory
Set-Location C:\ms1

# Check the status of the repository
git status

# Add all changes to the staging area
git add .

# Prompt for a commit message
$commitMessage = Read-Host "Enter commit message"

# Commit the changes with the provided message
git commit -m $commitMessage

# Push the changes to the remote repository
git push

# Optionally, set the location back to the original directory
Set-Location
