<#
.SYNOPSIS
    Unified App Manager for Winget and Scoop with FZF integration.
.DESCRIPTION
    Allows searching, installing, uninstalling, and viewing info for packages
    using Winget and Scoop. Cleanly handles output and provides a unified interface.
#>

# --- Configuration ---
$ScoopBucketsPath = "$env:USERPROFILE\scoop\buckets"
$ScoopListCache = "$env:TEMP\scoop_pkg_list.txt"

# --- Helper Functions ---

function Get-Fzf {
    # Check if fzf is available
    if (-not (Get-Command fzf -ErrorAction SilentlyContinue)) {
        Write-Error "FZF is not installed or not in PATH."
        return $null
    }
    return (Get-Command fzf).Source
}

function Clean-WingetOutput {
    param([string[]]$Lines)
    foreach ($line in $Lines) {
        # Skip headers and separator lines (robust matching)
        if ($line -match "^\s*Name\s+Id\s+Version") { continue }
        if ($line -match "^\s*-{3,}") { continue }
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        
        # Output clean line
        $line
    }
}

function Parse-WingetLine {
    param([string]$Line)
    # Winget output layout is fixed-width-ish, but variable.
    # Usually: Name (Variable) | Id (Variable) | Version (Variable)
    # We split by multiple spaces.
    $parts = $Line -split '\s{2,}'
    if ($parts.Count -ge 2) {
        return @{
            Name = $parts[0].Trim()
            Id = $parts[1].Trim()
        }
    }
    return $null
}

function Get-ScoopPackagesAll {
    Write-Host "Scanning Scoop buckets..." -ForegroundColor Cyan
    $packages = @()
    if (Test-Path $ScoopBucketsPath) {
        $files = Get-ChildItem -Path $ScoopBucketsPath -Recurse -Filter "*.json"
        foreach ($file in $files) {
            $packages += $file.BaseName
        }
    }
    return $packages | Sort-Object -Unique
}

function Get-ScoopPackagesInstalled {
    $list = scoop list
    # Skip header
    # Installed apps:
    #   Name (Version)
    # output varies. We rely on line parsing.
    $cleanList = @()
    foreach ($line in $list) {
        if ($line -match "^\s*([a-zA-Z0-9\-\_\.]+)\s+\(") {
            $cleanList += $matches[1]
        }
    }
    return $cleanList
}

function Run-AppManager {
    $fzf = Get-Fzf
    if (-not $fzf) { return }

    while ($true) {
        Clear-Host
        Write-Host "=== Unified App Manager ===" -ForegroundColor Green
        Write-Host "1. Scoop: Install (Search All)"
        Write-Host "2. Scoop: Uninstall / Info (Installed)"
        Write-Host "3. Winget: Install (Search Online)"
        Write-Host "4. Winget: Uninstall / Info (Installed)"
        Write-Host "Q. Quit"
        
        $choice = Read-Host "Select an option"
        
        switch ($choice) {
            "1" { Action-Scoop-Install }
            "2" { Action-Scoop-Installed }
            "3" { Action-Winget-Install }
            "4" { Action-Winget-Installed }
            "Q" { return }
            "q" { return }
        }
    }
}

function Action-Scoop-Install {
    $pkgs = Get-ScoopPackagesAll
    if (-not $pkgs) { Write-Warning "No packages found."; Pause; return }
    
    $selection = $pkgs | fzf --prompt="Scoop Install> " --preview="scoop info {}" --multi
    
    if ($selection) {
        foreach ($pkg in $selection) {
            Write-Host "Installing $pkg..." -ForegroundColor Yellow
            scoop install $pkg
        }
        Pause
    }
}

function Action-Scoop-Installed {
    $pkgs = Get-ScoopPackagesInstalled
    if (-not $pkgs) { Write-Warning "No installed packages found."; Pause; return }
    
    # We need a custom preview that handles local info vs remote info logic if needed, 
    # but 'scoop info' works for installed too.
    # We might want ACTIONS: Info, Uninstall.
    # Let's verify selection first.
    
    $selection = $pkgs | fzf --prompt="Scoop Installed> " --preview="scoop info {}" --expect=ctrl-u,ctrl-i
    # Expect: ctrl-u (uninstall), ctrl-i (info - merely keeps looking?), enter (default)
    
    # fzf with --expect returns 2 lines: key, then selection.
    $key = $selection[0]
    $pkg = $selection[1]
    
    if ($pkg) {
        if ($key -eq "ctrl-u") {
            $confirm = Read-Host "Uninstall $pkg? (y/n)"
            if ($confirm -eq 'y') {
                scoop uninstall $pkg
                Pause
            }
        } else {
            # Default or Info
            scoop info $pkg
            Pause
        }
    }
}

function Action-Winget-Install {
    Write-Host "Enter search query (leave empty for broad search, but it might be incomplete):"
    $query = Read-Host "Query"
    
    Write-Host "Searching Winget (this may take a moment)..." -ForegroundColor Cyan
    # winget search outputs table.
    # We capture all output.
    # Note: 'winget search ""' might truncate.
    
    if ([string]::IsNullOrWhiteSpace($query)) {
        # 'winget search' without arguments lists help in some versions, 
        # but 'winget search ""' or 'winget search -q ""' attempts to list all.
        $raw = winget search -q ""
    } else {
        $raw = winget search "$query"
    }

    $clean = Clean-WingetOutput -Lines $raw | Sort-Object -Unique
    
    if (-not $clean) { Write-Warning "No results."; Pause; return }
    
    # Use 2+ spaces as delimiter for column separation to handle names with single spaces correctly.
    # {2} should capture the ID column if we split by 2+ spaces.
    # Note: Regex delimiter in fzf requires --delimiter.
    $selection = $clean | fzf --prompt="Winget Install> " --delimiter='\s{2,}' --preview='winget show {2}' --preview-window='right:50%'
    
    if ($selection) {
        # Parse the selected line using the same helper
        $parsed = Parse-WingetLine -Line $selection
        if ($parsed) {
            $id = $parsed.Id
            $name = $parsed.Name
            $confirm = Read-Host "Install $name ($id)? (y/n)"
            if ($confirm -eq 'y') {
                winget install --id $id
                Pause
            }
        }
    }
}

function Action-Winget-Installed {
    Write-Host "Fetching installed Winget packages..." -ForegroundColor Cyan
    $raw = winget list
    $clean = Clean-WingetOutput -Lines $raw
    
    $selection = $clean | fzf --prompt="Winget Installed> " --preview="winget show {2}" --expect=ctrl-u
    
    $key = $selection[0]
    $line = $selection[1]
    
    if ($line) {
        $parsed = Parse-WingetLine -Line $line
        if ($parsed) {
            $id = $parsed.Id
            if ($key -eq "ctrl-u") {
                $confirm = Read-Host "Uninstall $($parsed.Name)? (y/n)"
                if ($confirm -eq 'y') {
                    winget uninstall --id $id
                    Pause
                }
            } else {
                winget show --id $id
                Pause
            }
        }
    }
}

# --- Entry Point ---
Run-AppManager
