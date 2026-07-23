[CmdletBinding()]
param(
    [switch]$ListOnly,
    [switch]$Uninstall
)

$ErrorActionPreference = 'SilentlyContinue'

function Get-PythonCandidates {
    $found = @{}

    function Add-Candidate([string]$Path, [string]$Source) {
        if ([string]::IsNullOrWhiteSpace($Path)) { return }
        try { $Path = [IO.Path]::GetFullPath($Path) } catch { return }
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return }
        if ([IO.Path]::GetFileName($Path) -notin @('python.exe', 'python3.exe')) { return }
        if ($Path -like "$env:LOCALAPPDATA\Microsoft\WindowsApps\*") { return }

        # uv may expose the same installation through a junction such as
        # cpython-3.11-windows-x86_64-none. Keep only the real directory.
        $parent = Get-Item -LiteralPath (Split-Path -Parent $Path)
        if ($parent.LinkType -eq 'Junction' -and $parent.Target) {
            $Path = Join-Path ([string]$parent.Target) ([IO.Path]::GetFileName($Path))
        }

        $key = $Path.ToLowerInvariant()
        if (-not $found.ContainsKey($key)) {
            $version = & $Path --version 2>&1 | Select-Object -First 1
            $found[$key] = [PSCustomObject]@{
                Path    = $Path
                Version = ([string]$version -replace '^Python\s+', '').Trim()
                Source  = $Source
            }
        }
    }

    # The Python launcher knows about registered installations, including ones
    # that are not currently on PATH.
    $py = Get-Command py.exe -CommandType Application
    if ($py) {
        (& $py.Source -0p 2>$null) | ForEach-Object {
            if ($_ -match '^\s*-\d+(?:\.\d+)?\s+(.+python(?:3)?\.exe)\s*$') {
                Add-Candidate $Matches[1].Trim() 'Python launcher'
            }
        }
    }

    # Python installations registered by the official Windows installer.
    $registryRoots = @(
        'HKCU:\Software\Python\PythonCore',
        'HKLM:\Software\Python\PythonCore',
        'HKLM:\Software\WOW6432Node\Python\PythonCore'
    )
    foreach ($root in $registryRoots) {
        Get-ChildItem $root | ForEach-Object {
            $installPath = (Get-ItemProperty $_.PSPath).InstallPath
            if ($installPath) { Add-Candidate (Join-Path $installPath 'python.exe') 'Python registry' }
        }
    }

    # Common per-user locations used by uv, the Windows installer, and Scoop.
    $roots = @(
        "$env:LOCALAPPDATA\Programs\Python",
        "$env:LOCALAPPDATA\Python",
        "$env:USERPROFILE\.local\share\uv\python",
        "$env:APPDATA\uv\python",
        "$env:USERPROFILE\scoop\apps\python\current",
        "$env:USERPROFILE\scoop\apps\python311\current",
        "$env:USERPROFILE\scoop\apps\python312\current",
        "$env:USERPROFILE\scoop\apps\python313\current",
        "$env:USERPROFILE\scoop\apps\python314\current"
    )
    foreach ($root in $roots) {
        if (Test-Path -LiteralPath $root) {
            Add-Candidate (Join-Path $root 'python.exe') 'Common install location'
            Get-ChildItem -LiteralPath $root -Directory | ForEach-Object {
                Add-Candidate (Join-Path $_.FullName 'python.exe') 'Common install location'
            }
        }
    }

    # Current PATH entries catch custom installs and uv-managed shims.
    ($env:PATH -split ';') | Where-Object { $_ } | ForEach-Object {
        Add-Candidate (Join-Path $_ 'python.exe') 'PATH'
        Add-Candidate (Join-Path $_ 'python3.exe') 'PATH'
    }

    @($found.Values) | Sort-Object {
        try { [version](($_.Version -split '\s')[0]) } catch { [version]'0.0' }
    } -Descending
}

function Show-PythonCandidates($Candidates) {
    if (-not $Candidates) {
        Write-Host 'No Python installations were found.' -ForegroundColor Yellow
        return
    }

    $current = (Get-Command python.exe -CommandType Application).Source
    Write-Host "`nInstalled Python versions:`n" -ForegroundColor Cyan
    for ($i = 0; $i -lt $Candidates.Count; $i++) {
        $marker = if ($Candidates[$i].Path -ieq $current) { ' (current python)' } else { '' }
        Write-Host ("[{0}] Python {1}{2}" -f ($i + 1), $Candidates[$i].Version, $marker)
        Write-Host ("    {0} [{1}]" -f $Candidates[$i].Path, $Candidates[$i].Source) -ForegroundColor DarkGray
    }
}

function Set-UserPathDefault([string]$PythonPath) {
    $pythonDir = Split-Path -Parent $PythonPath
    $scriptsDir = Join-Path $pythonDir 'Scripts'
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $entries = @($userPath -split ';' | Where-Object { $_ -and $_.Trim() })

    # Remove existing entries for Python installs and put the selected install
    # and its Scripts directory first. Unrelated PATH entries are preserved.
    $entries = @($entries | Where-Object {
        $normalized = $_.Trim().TrimEnd('\')
        $normalized -ine $pythonDir.TrimEnd('\') -and
        $normalized -ine $scriptsDir.TrimEnd('\') -and
        $normalized -notmatch '\\Python(?:3\d+)?(?:\\Scripts)?$'
    })
    $newPath = (@($pythonDir, $scriptsDir) + $entries) -join ';'
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')

    # Update this process too, so the verification below reflects the choice.
    $env:PATH = $newPath + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
}

function Remove-UserPathEntries([string]$PythonPath) {
    $pythonDir = Split-Path -Parent $PythonPath
    $scriptsDir = Join-Path $pythonDir 'Scripts'
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $entries = @($userPath -split ';' | Where-Object { $_ -and $_.Trim() })
    $entries = @($entries | Where-Object {
        $normalized = $_.Trim().TrimEnd('\')
        $normalized -ine $pythonDir.TrimEnd('\') -and
        $normalized -ine $scriptsDir.TrimEnd('\')
    })
    [Environment]::SetEnvironmentVariable('Path', ($entries -join ';'), 'User')
}

function Remove-PipPackages([string]$PythonPath) {
    $pipCheck = & $PythonPath -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'pip is not installed for this interpreter; skipping pip packages.' -ForegroundColor Yellow
        return
    }

    $packages = @(& $PythonPath -m pip freeze --local 2>$null | Where-Object {
        $_ -and $_ -notmatch '^\s*#' -and $_ -notmatch '^(-e|--editable)\s+'
    })
    if (-not $packages) {
        Write-Host 'No pip-installed packages were found.'
        return
    }

    Write-Host "`nPackages that will be removed:" -ForegroundColor Yellow
    $packages | ForEach-Object { Write-Host "  $_" }
    $answer = Read-Host "Remove these packages from Python $(& $PythonPath --version 2>&1)? (yes/no)"
    if ($answer -notmatch '^(y|yes)$') {
        Write-Host 'Package removal skipped.'
        return
    }

    $requirementsFile = Join-Path $env:TEMP ("python-uninstall-{0}.txt" -f ([guid]::NewGuid()))
    try {
        $packages | Set-Content -LiteralPath $requirementsFile
        & $PythonPath -m pip uninstall --yes --requirement $requirementsFile
        if ($LASTEXITCODE -ne 0) { Write-Host 'pip reported an error while removing packages.' -ForegroundColor Red }
    }
    finally {
        Remove-Item -LiteralPath $requirementsFile -Force -ErrorAction SilentlyContinue
    }
}

function Uninstall-Python([PSCustomObject]$Candidate) {
    if ($Candidate.Path -like "$env:LOCALAPPDATA\hermes\*") {
        Write-Host 'This Python belongs to Hermes and is not an independent installation.' -ForegroundColor Yellow
        Write-Host 'It was not changed because removing its packages would likely break Hermes.'
        Write-Host 'Use Hermes'' own uninstaller if you want to remove Hermes completely.'
        return
    }

    $pythonDir = Split-Path -Parent $Candidate.Path
    $processPaths = @($pythonDir)
    $uvParent = Split-Path -Parent $pythonDir
    if ($pythonDir -like "$env:APPDATA\uv\python\*" -or $pythonDir -like "$env:USERPROFILE\.local\share\uv\python\*") {
        Get-ChildItem -LiteralPath $uvParent -Directory | ForEach-Object {
            $item = Get-Item -LiteralPath $_.FullName
            if ($item.LinkType -eq 'Junction' -and [string]$item.Target -ieq $pythonDir) {
                $processPaths += $_.FullName
            }
        }
    }
    $running = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $process = $_
        $process.Path -and ($processPaths | Where-Object { $process.Path -like "$($_)\*" })
    })
    if ($running) {
        Write-Host 'This Python is currently running:' -ForegroundColor Red
        $running | Select-Object Id,ProcessName,Path | Format-Table -AutoSize
        Write-Host 'Close the listed applications/processes and run the uninstall again.' -ForegroundColor Yellow
        return
    }

    Remove-PipPackages $Candidate.Path
    Remove-UserPathEntries $Candidate.Path

    $uvInstallDir = $null
    if ($pythonDir -like "$env:APPDATA\uv\python\*" -or $pythonDir -like "$env:USERPROFILE\.local\share\uv\python\*") {
        $uvInstallDir = Split-Path -Parent $pythonDir
    }

    if ($uvInstallDir -and (Get-Command uv.exe -ErrorAction SilentlyContinue)) {
        $target = Split-Path -Leaf $pythonDir
        Write-Host "Removing uv-managed Python installation: $target" -ForegroundColor Cyan
        & uv.exe python uninstall --install-dir $uvInstallDir $target
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'uv could not remove this installation. No interpreter files were deleted.' -ForegroundColor Red
            return
        }
        Write-Host 'uv-managed Python installation removed.' -ForegroundColor Green
        return
    }

    $uninstaller = Join-Path $pythonDir 'uninstall.exe'
    if (Test-Path -LiteralPath $uninstaller -PathType Leaf) {
        Write-Host 'Starting the Python uninstaller...' -ForegroundColor Cyan
        Start-Process -FilePath $uninstaller -Wait
        Write-Host 'Python uninstaller finished.' -ForegroundColor Green
        return
    }

    Write-Host "No uninstaller was found for $pythonDir. The interpreter was not deleted." -ForegroundColor Yellow
    Write-Host 'PATH entries were removed; uninstall it from Windows Settings or reinstall it with an official installer.'
}

$candidates = @(Get-PythonCandidates)
Show-PythonCandidates $candidates
if ($ListOnly -or -not $candidates) { exit }

$doUninstall = [bool]$Uninstall
if (-not $Uninstall) {
    Write-Host "`nWhat would you like to do?" -ForegroundColor Cyan
    Write-Host '[1] Make default'
    Write-Host '[2] Uninstall'
    $action = Read-Host 'Enter 1 or 2, or press Enter to exit'
    if ([string]::IsNullOrWhiteSpace($action)) { exit }
    if ($action -eq '2') {
        $doUninstall = $true
    }
    elseif ($action -ne '1') {
        Write-Host 'Invalid selection. No changes were made.' -ForegroundColor Red
        exit 1
    }
}

$selectionPrompt = if ($doUninstall) { "`nEnter the number to uninstall, or press Enter to exit" } else { "`nEnter the number to make default, or press Enter to exit" }
$selection = Read-Host $selectionPrompt
if ([string]::IsNullOrWhiteSpace($selection)) { exit }
$index = 0
if (-not [int]::TryParse($selection, [ref]$index) -or $index -lt 1 -or $index -gt $candidates.Count) {
    Write-Host 'Invalid selection. No changes were made.' -ForegroundColor Red
    exit 1
}

$selected = $candidates[$index - 1]
if ($doUninstall) {
    Write-Host "`nWARNING: this removes the selected interpreter's pip packages and then uninstalls the interpreter." -ForegroundColor Red
    $confirm = Read-Host ("Type REMOVE to continue uninstalling Python {0}" -f $selected.Version)
    if ($confirm -ne 'REMOVE') {
        Write-Host 'Cancelled. No changes were made.'
        exit
    }
    Uninstall-Python $selected
    Write-Host "`nUninstall operation finished. Open a new PowerShell window to refresh PATH." -ForegroundColor Green
}
else {
    Set-UserPathDefault $selected.Path
    Write-Host ("`nDefault set to Python {0}. Open a new PowerShell window, then run: python --version" -f $selected.Version) -ForegroundColor Green
}
