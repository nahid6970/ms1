function Get-FolderSize {
    param (
        [string]$path
    )

    $size = 0
    $files = Get-ChildItem -File -Recurse -LiteralPath $path -ErrorAction SilentlyContinue

    foreach ($file in $files) {
        $size += $file.Length
    }

    return $size
}

function Format-Size {
    param (
        [int64]$size
    )

    $suffixes = "B", "KB", "MB", "GB", "TB"
    $index = 0

    while ($size -ge 1KB -and $index -lt $suffixes.Length) {
        $size /= 1KB
        $index++
    }

    return "{0:N3} {1}" -f $size, $suffixes[$index]
}

function Get-FolderSizes {
    param (
        [string]$path
    )

    function Show-FolderSizes {
        param (
            [string]$currentPath,
            [int]$indentLevel
        )

        $folders = Get-ChildItem -Directory -LiteralPath $currentPath -ErrorAction SilentlyContinue

        foreach ($folder in $folders) {
            $size = Get-FolderSize -path $folder.FullName
            $formattedSize = Format-Size -size $size
            $progressBar = "[{0}]" -f ("#" * [math]::Round(($size / $totalSize) * 10))
            $formattedPath = $folder.FullName.Substring($rootPath.Length + 1)

            Write-Output ("{0}{1} {2} {3}" -f (' ' * $indentLevel), $formattedSize, $progressBar, $formattedPath)

            Show-FolderSizes -currentPath $folder.FullName -indentLevel ($indentLevel + 2)
        }
    }

    $totalSize = Get-FolderSize -path $path
    $totalFormattedSize = Format-Size -size $totalSize

    Write-Output "`nTotal usage: $totalFormattedSize, Objects: 1"
    Show-FolderSizes -currentPath $path -indentLevel 0
}

# Usage example:
$rootPath = "D:\"
Get-FolderSizes -path $rootPath
Read-Host "Press Enter to exit"
