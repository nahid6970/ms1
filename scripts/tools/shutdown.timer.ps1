$timer = Read-Host "Enter the timer (e.g., 5s, 5m, 5h)"
$unit = $timer[-1]
$value = $timer[0..($timer.Length-2)] -join ''

$seconds = switch ($unit) {
    "s" { [int]$value }
    "m" { [int]$value * 60 }
    "h" { [int]$value * 3600 }
    default { throw "Invalid unit specified" }
}

Write-Host "Shutting down in $seconds seconds..."

for ($i = $seconds; $i -gt 0; $i--) {
    Write-Host "$i seconds remaining..."
    Start-Sleep -Seconds 1
}

Write-Host "Shutting down..."
Stop-Computer -Force
