$exeName = "cyber_editor.exe"
$hives = @("HKCU:\Software\Classes\Applications", "HKLM:\Software\Classes\Applications")

foreach ($hive in $hives) {
    $targetPath = Join-Path -Path $hive -ChildPath $exeName
    if (Test-Path $targetPath) {
        Remove-Item -Path $targetPath -Recurse -Force
        Write-Host "Removed $targetPath"
    } else {
        Write-Host "Not found in $hive"
    }
}
Write-Host "Registry cleanup complete. You can now use 'Open With' and browse to the new location."
