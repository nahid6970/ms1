# Get a list of running processes with CPU usage and select one or more using fzf
$processes = Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String
$selectedProcesses = $processes | fzf -m

# Extract the process names from the selected strings
$processNames = $selectedProcesses -split '\r?\n' | ForEach-Object {
    $_ -split '\s{2,}' | Select-Object -First 1
}

# If user selects one or more processes, kill them
if ($processNames) {
    foreach ($processName in $processNames) {
        if ($processName) {
            Stop-Process -Name $processName -Force
            Write-Host "Process $processName terminated."
        }
    }
} else {
    Write-Host "No processes selected."
}




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