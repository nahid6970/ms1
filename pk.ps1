# Get a list of processes with structured output for fzf
$processes = Get-Process | ForEach-Object {
    # Create a formatted string: "Id Name CPU Memory"
    "{0,-8} {1,-25} {2,-10:N2} {3,-10:N2}" -f $_.Id, $_.Name, $_.CPU, ($_.PM / 1MB)
}

# Use fzf to allow the user to select a process
$selectedProcess = $processes | fzf -i --multi

# Extract the process name from the selected line (second column)
if ($selectedProcess) {
    # Use regex to capture the name from the formatted line
    if ($selectedProcess -match '^\d+\s+(\S+)\s') {
        $processName = $matches[1]

        # Kill the selected process by name
        try {
            Stop-Process -Name $processName -Force
            Write-Host "Process with name '$processName' has been terminated."
        } catch {
            Write-Host "Failed to terminate process: $_"
        }
    } else {
        Write-Host "Invalid process selection. No valid process name found."
    }
} else {
    Write-Host "No process selected."
}



# #! kill with id
# $processes = Get-Process | ForEach-Object {
#     # Create a formatted string: "Id Name CPU Memory"
#     "{0,-8} {1,-25} {2,-10:N2} {3,-10:N2}" -f $_.Id, $_.Name, $_.CPU, ($_.PM / 1MB)
# }

# # Use fzf to allow the user to select a process
# $selectedProcess = $processes | fzf --header="Id       Name                     CPU        Memory" --preview "echo {}" --preview-window=up:10

# # Extract the process ID from the selected line (first column)
# if ($selectedProcess) {
#     # Use a regex to extract the numeric ID from the start of the line
#     if ($selectedProcess -match '^(\d+)\s') {
#         $processId = $matches[1] -as [int]

#         # Kill the selected process
#         try {
#             Stop-Process -Id $processId -Force
#             Write-Host "Process with ID $processId has been terminated."
#         } catch {
#             Write-Host "Failed to terminate process: $_"
#         }
#     } else {
#         Write-Host "Invalid process selection. No valid process ID found."
#     }
# } else {
#     Write-Host "No process selected."
# }




# #! Get all processes with additional details (Name, CPU, CommandLine) // slower
# $processes = Get-Process | ForEach-Object {
#     $commandLine = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
#     [PSCustomObject]@{
#         Name        = $_.Name
#         CPU         = $_.CPU
#         CommandLine = $commandLine
#     }
# } | Sort-Object CPU -Descending

# # Format processes for display
# $processDisplay = $processes | Format-Table Name, CPU, CommandLine -AutoSize | Out-String

# # Skip the first two lines (header and separator) and then allow selection via fzf
# $filteredProcesses = $processDisplay -split "`n" | Select-Object -Skip 3
# $selectedProcesses = $filteredProcesses | fzf -m

# # Extract the process names from the selected strings
# $processNames = $selectedProcesses -split '\r?\n' | ForEach-Object {
#     ($_ -split '\s{2,}')[0]
# }

# # If user selects one or more processes, kill them
# if ($processNames) {
#     foreach ($processName in $processNames) {
#         if ($processName) {
#             try {
#                 Stop-Process -Name $processName -Force
#                 Write-Host "Process $processName terminated."
#             } catch {
#                 Write-Host "Failed to terminate process $processName. Error: $_"
#             }
#         }
#     }
# } else {
#     Write-Host "No processes selected."
# }





# # Get all processes with additional details (Name, CPU, CommandLine)
# $processes = Get-Process | ForEach-Object {
#     # Retrieve the CommandLine and clean it up by removing unwanted characters
#     $commandLine = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine
#     $cleanedCommandLine = $commandLine -replace '[\r\u00b9\u00b2\u00b3\u2070\u2074\u2075\u2076\u2077\u2078\u2079\u00ae\u2122]', '' # Remove unwanted chars
#     [PSCustomObject]@{
#         Name        = $_.Name
#         CPU         = $_.CPU
#         CommandLine = $cleanedCommandLine
#     }
# } | Sort-Object CPU -Descending

# # Format processes for display
# $processDisplay = $processes | Format-Table Name, CPU, CommandLine -AutoSize | Out-String

# # Skip the first two lines (header and separator) and then allow selection via fzf
# $filteredProcesses = $processDisplay -split "`n" | Select-Object -Skip 3
# $selectedProcesses = $filteredProcesses | fzf -m

# # Extract the process names from the selected strings
# $processNames = $selectedProcesses -split '\r?\n' | ForEach-Object {
#     ($_ -split '\s{2,}')[0]
# }

# # If user selects one or more processes, kill them
# if ($processNames) {
#     foreach ($processName in $processNames) {
#         if ($processName) {
#             try {
#                 Stop-Process -Name $processName -Force
#                 Write-Host "Process $processName terminated."
#             } catch {
#                 Write-Host "Failed to terminate process $processName. Error: $_"
#             }
#         }
#     }
# } else {
#     Write-Host "No processes selected."
# }




# # Use old PowerShell and prevent loading the profile
# $psCommand = {
#     $processes = Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String
#     $selectedProcesses = $processes | fzf -m

#     # Extract the process names from the selected strings
#     $processNames = $selectedProcesses -split '\r?\n' | ForEach-Object {
#         $_ -split '\s{2,}' | Select-Object -First 1
#     }

#     # If user selects one or more processes, kill them
#     if ($processNames) {
#         foreach ($processName in $processNames) {
#             if ($processName) {
#                 Stop-Process -Name $processName -Force
#                 Write-Host "Process $processName terminated."
#             }
#         }
#     } else {
#         Write-Host "No processes selected."
#     }
# }

# # Invoke the old PowerShell without loading the profile
# Start-Process "powershell.exe" -ArgumentList "-NoProfile", "-Command", $psCommand








# # Get a list of running processes and select one using fzf
# $processName = Get-Process | Select-Object -ExpandProperty Name | fzf
# # If user selects a process, confirm and kill it
# if ($processName) {
#     $confirm = Read-Host "Are you sure you want to terminate process $processName? (Y/N)"
#     if ($confirm -eq "Y" -or $confirm -eq "y") {
#         Stop-Process -Name $processName -Force
#         Write-Host "Process $processName terminated."
#     } else {
#         Write-Host "Process termination aborted."
#     }
# } else {
#     Write-Host "No process selected."
# }



# Set-Location
# $processName = (Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String | fzf -m) -split '\s{2,}' | Select-Object -First 1; if ($processName) { Stop-Process -Name $processName -Force; Write-Host "Process $processName terminated." } else { Write-Host "No process selected." }
