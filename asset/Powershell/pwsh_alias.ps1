function killp  {
    $processName = (Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String | fzf) -split '\s{2,}' | Select-Object -First 1; if ($processName) { Stop-Process -Name $processName -Force; Write-Host "Process $processName terminated." } else { Write-Host "No process selected." }
}

function filterfzf {
    param(
        [string]$Command,
        [string]$Text
    )

    $output = Invoke-Expression "$Command" | Out-String
    $filteredOutput = $output -split "`n" | fzf --query="$Text"
    Write-Output $filteredOutput
}