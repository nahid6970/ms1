#! Autin History
# $PSReadLine = Get-Module PSReadLine
# $atuin = Get-Command atuin -ErrorAction Ignore

# if (!$PSReadLine -or !$atuin) {
#     Write-Host "PSReadLine and atuin are required"
#     return
# }
# $env:ATUIN_SESSION = atuin uuid
# $atuin_history_id = 0
# function PSConsoleHostReadLine {
#     ## This needs to be done as the first thing because any script run will flush $?.
#     $lastRunStatus = $?
#     if ($atuin_history_id -ne 0) {
#         $exitCode = if ($lastRunStatus) { 0 } elseif ($LASTEXITCODE) { $LASTEXITCODE } else { 1 }
#         $null = atuin history end --exit $exitCode -- $atuin_history_id
#     }
#     Microsoft.PowerShell.Core\Set-StrictMode -Off
#     $line = [Microsoft.PowerShell.PSConsoleReadLine]::ReadLine($host.Runspace, $ExecutionContext, $lastRunStatus)
#     $script:atuin_history_id = atuin history start -- $line
#     $line
# }
# Set-PSReadLineKeyHandler -Key Ctrl+r -ScriptBlock {
#     $line = $null
#     $cursor = $null
#     [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$line, [ref]$cursor)
#     $resultFile = New-TemporaryFile
#     Start-Process -Wait -NoNewWindow -RedirectStandardError $resultFile.FullName atuin -ArgumentList "search","-i"
#     $result = (Get-Content -Raw $resultFile).Trim()
#     Remove-Item $resultFile
#     [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
#     [Microsoft.PowerShell.PSConsoleReadLine]::Insert($result)
# }
# $MyInvocation.MyCommand.ScriptBlock.Module.OnRemove = {
#     Write-Host "To restore PSReadLine, run`n    Remove-Module PSReadLine`n    Import-Module PSReadLine"
# }
# Export-ModuleMember -Function PSConsoleHostReadLine
