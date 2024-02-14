	# Set the title of the PowerShell window
	$title = "Find-Size"
	$title = $title.PadRight($Host.UI.RawUI.WindowSize.Width - $title.Length)
	$title = " " + $title + " "
	$title = $title.PadRight($Host.UI.RawUI.WindowSize.Width - $title.Length)
	$Host.UI.RawUI.WindowTitle = $title
	# Define a function to search for files by size
	function Search-FilesBySize {
	# Prompt the user to enter a size option to search for
	Write-Host "Enter a size option to search for:" -ForegroundColor Green
	Write-Host "1. Files less than a certain size"
	Write-Host "2. Files between a certain size range"
	Write-Host "3. Files greater than a certain size"
	$sizeOption = Read-Host
	switch ($sizeOption) {
	1 {
	# Prompt the user to enter the maximum file size in MB
	Write-Host "Enter the maximum file size in MB:" -ForegroundColor Green
	$maxSizeMB = Read-Host
	# Get all files in the drives and filter by size
	Get-ChildItem -Path "D:\" -Recurse | Where-Object {$_.Length / 1MB -lt $maxSizeMB} | Select-Object FullName, @{Name="SizeMB";Expression={$_.Length / 1MB}} | ForEach-Object {
	Write-Output "$($_.FullName) - $($_.SizeMB.ToString('0.00')) MB"
	}
	}
	2 {
	# Prompt the user to enter the minimum and maximum file size in MB
	Write-Host "Enter the minimum file size in MB:" -ForegroundColor Green
	$minSizeMB = Read-Host
	Write-Host "Enter the maximum file size in MB:" -ForegroundColor Green
	$maxSizeMB = Read-Host
	# Get all files in the drives and filter by size
	Get-ChildItem -Path "D:\" -Recurse | Where-Object {$_.Length / 1MB -ge $minSizeMB -and $_.Length / 1MB -le $maxSizeMB} | Select-Object FullName, @{Name="SizeMB";Expression={$_.Length / 1MB}} | ForEach-Object {
	Write-Output "$($_.FullName) - $($_.SizeMB.ToString('0.00')) MB"
	}
	}
	3 {
	# Prompt the user to enter the minimum file size in MB
	Write-Host "Enter the minimum file size in MB:" -ForegroundColor Green
	$minSizeMB = Read-Host
	# Get all files in the drives and filter by size
	Get-ChildItem -Path "D:\" -Recurse | Where-Object {$_.Length / 1MB -gt $minSizeMB} | Select-Object FullName, @{Name="SizeMB";Expression={$_.Length / 1MB}} | ForEach-Object {
	Write-Output "$($_.FullName) - $($_.SizeMB.ToString('0.00')) MB"
	}
	}
	default {
	Write-Host "Invalid option selected. Please try again." -ForegroundColor Red
	}
	}
	}
	# Call the function to search for files by size
	while ($true) {
	Search-FilesBySize
}