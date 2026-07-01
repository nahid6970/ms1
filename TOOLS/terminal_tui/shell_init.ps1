$script:stateFile = "C:\@delta\ms1\TOOLS\terminal_tui\active_project.json"
$script:lastProject = ""

# Load last active project on shell startup
if (Test-Path $script:stateFile) {
    try {
        $state = Get-Content $script:stateFile -Raw | ConvertFrom-Json
        if ($state.path -and (Test-Path $state.path)) {
            $script:lastProject = $state.path
            Set-Location $state.path
        }
    } catch {}
}

# Override prompt to check for sidebar state changes and automatically switch directories
function prompt {
    if (Test-Path $script:stateFile) {
        try {
            $state = Get-Content $script:stateFile -Raw | ConvertFrom-Json
            $activeProjPath = $state.path
            if ($activeProjPath -and $activeProjPath -ne $script:lastProject -and (Test-Path $activeProjPath)) {
                $script:lastProject = $activeProjPath
                Set-Location $activeProjPath
                Write-Host "`n[Workspace switched to: $activeProjPath]" -ForegroundColor Cyan
            }
        } catch {}
    }
    
    # Update window title
    $host.ui.RawUI.WindowTitle = "Workspace: $((Get-Location).Path)"
    
    # Format path for prompt display
    $path = (Get-Location).Path
    $homePath = [System.Environment]::GetFolderPath('UserProfile')
    if ($path.StartsWith($homePath)) {
        $path = "~" + $path.Substring($homePath.Length).Replace("\", "/")
    } else {
        $path = $path.Replace("\", "/")
    }
    
    # Show active git branch if available
    $branch = ""
    if (Test-Path ".git") {
        try {
            $branch = (git branch --show-current 2>$null).Trim()
        } catch {}
    }
    
    $branchStr = ""
    if ($branch) {
        $branchStr = " [Branch: $branch]"
    }
    
    Write-Host "`nDir: $path$branchStr" -ForegroundColor Gray
    "➜ "
}

# Clear and show welcome message
Clear-Host
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Native Shell Connected to Workspace TUI    " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Selecting a workspace in the sidebar will switch directories here." -ForegroundColor Gray
Write-Host "Every interactive tool (Gemini, Codex, Git) is fully supported." -ForegroundColor Gray
Write-Host ""
