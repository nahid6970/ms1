$Host.UI.RawUI.WindowTitle = "Script-List"

function List-Scripts {
    param (
        [string]$Folder
    )

    $scripts = Get-ChildItem -Path $Folder -Recurse -Include *.ps1, *.bat, *.ahk | Select-Object -ExpandProperty FullName
    return $scripts
}

function Display-Scripts {
    param (
        [array]$Scripts
    )

    Write-Host "`e[32mAvailable scripts:`e[0m"  # Set text color to green and reset
    for ($i = 0; $i -lt $Scripts.Count; $i++) {
        $scriptName = Split-Path -Path $Scripts[$i] -Leaf
        Write-Host "$($i + 1). $scriptName"
    }
}

function Select-Script {
    param (
        [array]$Scripts
    )

    while ($true) {
        $choice = Read-Host "Enter the number of the script you want to run (or 'q' to quit):"

        if ($choice.ToLower() -eq 'q') {
            return $null
        }

        try {
            $scriptIndex = [int]$choice - 1
            if ($scriptIndex -ge 0 -and $scriptIndex -lt $Scripts.Count) {
                return $Scripts[$scriptIndex]
            } else {
                Write-Host "Invalid choice. Please enter a valid number."
            }
        } catch {
            Write-Host "Invalid input. Please enter a number or 'q' to quit."
        }
    }
}

$scriptDirectory = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$folderPath = $scriptDirectory

while ($true) {
    $allScripts = List-Scripts -Folder $folderPath

    if ($allScripts.Count -gt 0) {
        Display-Scripts -Scripts $allScripts
    } else {
        Write-Host "No scripts found in the specified folder."
        break
    }

    $selectedScript = Select-Script -Scripts $allScripts

    if ($selectedScript) {
        $selectedScriptName = Split-Path -Path $selectedScript -Leaf

        if ($selectedScript -match "\.ahk$") {
            Write-Host "Opening AutoHotkey script: $($selectedScriptName)"
            Start-Process -FilePath $selectedScript
        } else {
            Write-Host "Running script: $($selectedScriptName)"
            Start-Process -FilePath $selectedScript -Wait
        }
    } else {
        break
    }
}
