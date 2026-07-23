[CmdletBinding()]
param(
    [switch]$ListOnly
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

$candidates = @(Get-PythonCandidates)
Show-PythonCandidates $candidates
if ($ListOnly -or -not $candidates) { exit }

$selection = Read-Host "`nEnter the number to make default, or press Enter to exit"
if ([string]::IsNullOrWhiteSpace($selection)) { exit }
$index = 0
if (-not [int]::TryParse($selection, [ref]$index) -or $index -lt 1 -or $index -gt $candidates.Count) {
    Write-Host 'Invalid selection. No changes were made.' -ForegroundColor Red
    exit 1
}

$selected = $candidates[$index - 1]
Set-UserPathDefault $selected.Path
Write-Host ("`nDefault set to Python {0}. Open a new PowerShell window, then run: python --version" -f $selected.Version) -ForegroundColor Green
