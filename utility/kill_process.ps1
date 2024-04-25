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





# # Get a list of running processes with CPU usage and select one using fzf
# $processes = Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String
# $selectedProcess = $processes | fzf

# # Extract the process name from the selected string
# $processName = $selectedProcess -split '\s{2,}' | Select-Object -First 1

# # If user selects a process, kill it
# if ($processName) {
#     Stop-Process -Name $processName -Force
#     Write-Host "Process $processName terminated."
# } else {
#     Write-Host "No process selected."
# }



Set-Location
$processName = (Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String | fzf) -split '\s{2,}' | Select-Object -First 1; if ($processName) { Stop-Process -Name $processName -Force; Write-Host "Process $processName terminated." } else { Write-Host "No process selected." }
