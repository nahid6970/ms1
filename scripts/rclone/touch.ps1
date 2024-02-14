	# Define an array of rclone touch and delete commands
	$commands = @(
		"rclone touch g00:touch00.txt",
		"rclone touch g01:touch01.txt",
		"rclone touch g02:touch02.txt",
		"rclone touch g03:touch03.txt",
		"rclone touch g04:touch04.txt",
		"rclone touch g05:touch05.txt",
		"rclone touch g06:touch06.txt",
		"rclone touch g07:touch07.txt",
		"rclone touch g08:touch08.txt",
		"rclone touch g09:touch09.txt",
		"rclone touch g10:touch10.txt",
		"rclone touch g11:touch11.txt",
		"rclone touch g12:touch12.txt",
		"rclone touch g13:touch13.txt",
		"rclone touch g14:touch14.txt",
		"rclone touch g15:touch15.txt",
		"rclone delete g00:touch00.txt",
		"rclone delete g01:touch01.txt",
		"rclone delete g02:touch02.txt",
		"rclone delete g03:touch03.txt",
		"rclone delete g04:touch04.txt",
		"rclone delete g05:touch05.txt",
		"rclone delete g06:touch06.txt",
		"rclone delete g07:touch07.txt",
		"rclone delete g08:touch08.txt",
		"rclone delete g09:touch09.txt",
		"rclone delete g10:touch10.txt",
		"rclone delete g11:touch11.txt",
		"rclone delete g12:touch12.txt",
		"rclone delete g13:touch13.txt",
		"rclone delete g14:touch14.txt",
		"rclone delete g15:touch15.txt"
	)
	# Iterate through the list of commands and execute them
	foreach ($command in $commands) {
		$commandName = $command.Split(' ')[1]   # Extract the command name (e.g., 'touch' or 'delete')
		$outputColor = If ($commandName -eq 'touch') { 'Blue' } else { 'Red' }  # Set output color based on command

		Write-Host $command -ForegroundColor $outputColor
		Invoke-Expression $command  # Execute the command
}
pause