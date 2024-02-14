	# Define an array of drive names and their corresponding paths
	$drives = @(
		@{Name = "m0"; Path = "m0:"},
		@{Name = "g00"; Path = "g00:"},
		@{Name = "g01"; Path = "g01:"},
		@{Name = "g02"; Path = "g02:"},
		@{Name = "g03"; Path = "g03:"},
		@{Name = "g04"; Path = "g04:"},
		@{Name = "g05"; Path = "g05:"},
		@{Name = "g06"; Path = "g06:"},
		@{Name = "g07"; Path = "g07:"},
		@{Name = "g08"; Path = "g08:"},
		@{Name = "g09"; Path = "g09:"},
		@{Name = "g10"; Path = "g10:"},
		@{Name = "g11"; Path = "g11:"},
		@{Name = "g12"; Path = "g12:"},
		@{Name = "g13"; Path = "g13:"},
		@{Name = "g14"; Path = "g14:"},
		@{Name = "g15"; Path = "g15:"}
	)
	# Iterate through the list of drives and execute the 'rclone about' command
	foreach ($drive in $drives) {
		$driveName = $drive.Name
		$drivePath = $drive.Path
		Write-Host ("Checking $driveName...") -ForegroundColor Green
		rclone about $drivePath
	}
	pause