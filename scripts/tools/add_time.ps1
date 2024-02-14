while ($true) {
    # Get user input for days, hours, and minutes
    $daysInput = Read-Host -Prompt "⚡➡️days (0 if none, 'q' to quit, 'c' to copy)"
    
    # Check if the user wants to quit
    if ($daysInput -eq 'q') {
        break
    }

    $hoursInput = Read-Host -Prompt "⚡➡️hours (0 if none)"
    $minutesInput = Read-Host -Prompt "⚡➡️minutes (0 if none)"

    # Convert input to integers
    $days = [int]$daysInput
    $hours = [int]$hoursInput
    $minutes = [int]$minutesInput

    # Get the current date and time
    $currentDateTime = Get-Date

    # Calculate the new date and time
    $newDateTime = $currentDateTime.AddMinutes($minutes).AddHours($hours).AddDays($days)

    # Display the result with colors in 12-hour format
    Write-Host "Current Date and Time: $($currentDateTime.ToString('yyyy-MM-dd hh:mm:ss tt'))" -ForegroundColor Yellow
    Write-Host "Added Time: +$days days, +$hours hours, +$minutes minutes" -ForegroundColor Yellow
    Write-Host "New Date and Time: $($newDateTime.ToString('yyyy-MM-dd hh:mm:ss tt'))" -ForegroundColor Green
    Write-Host "Press 'c' to copy the new date and time, 'q' to quit, or Enter to continue..." -ForegroundColor Cyan

    # Wait for user input
    $key = $Host.UI.RawUI.ReadKey("IncludeKeyDown,NoEcho").Character

    # Handle user input
    switch ($key) {
        'c' {
            # Copy the new date and time to the clipboard
            $newDateTime.ToString('yyyy-MM-dd hh:mm:ss tt') | Set-Clipboard
            Write-Host "New date and time copied to clipboard." -ForegroundColor Magenta
        }
        'q' {
            # Quit the loop if 'q' is pressed
            break
        }
    }

    Clear-Host
}
