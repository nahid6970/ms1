param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Prepare', 'InstallKey', 'DisablePassword')]
    [string] $Action,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-zA-Z0-9._-]+$')]
    [string] $UserName,
    [string] $PublicKeyBase64 = '',
    [switch] $Elevated
)

$ErrorActionPreference = 'Stop'
$logPath = Join-Path $env:TEMP 'ssh-setup-wizard.log'
Set-Content -Path $logPath -Value '' -Encoding utf8

function Write-Log([string] $Message) {
    Add-Content -Path $logPath -Value $Message -Encoding utf8
}

$principal = [Security.Principal.WindowsPrincipal]::new(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $childArguments = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"",
        '-Action', $Action, '-UserName', $UserName, '-Elevated'
    )
    if ($PublicKeyBase64) {
        $childArguments += @('-PublicKeyBase64', $PublicKeyBase64)
    }
    try {
        $child = Start-Process -FilePath 'powershell.exe' -Verb RunAs -Wait -PassThru `
            -WindowStyle Hidden -ArgumentList ($childArguments -join ' ')
        exit $child.ExitCode
    } catch {
        Write-Log "Administrator approval was cancelled or failed: $($_.Exception.Message)"
        exit 1
    }
}

try {
    $sshConfig = Join-Path $env:ProgramData 'ssh\sshd_config'
    $sshDaemon = Join-Path $env:WINDIR 'System32\OpenSSH\sshd.exe'
    if (-not (Test-Path $sshDaemon)) {
        throw 'Windows OpenSSH Server was not found. Install the OpenSSH Server optional feature first.'
    }

    if ($Action -eq 'InstallKey') {
        if (-not $PublicKeyBase64) { throw 'No public key was provided.' }
        $publicKey = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($PublicKeyBase64)).Trim()
        if ($publicKey -notmatch '^(ssh-ed25519|ecdsa-sha2-nistp256|ssh-rsa)\s+[A-Za-z0-9+/=]+') {
            throw 'The supplied key does not look like a supported OpenSSH public key.'
        }

        $account = "$env:COMPUTERNAME\$UserName"
        $accountSid = ([Security.Principal.NTAccount]::new($account)).Translate(
            [Security.Principal.SecurityIdentifier]
        ).Value
        $adminSids = @(Get-LocalGroupMember -SID 'S-1-5-32-544' | ForEach-Object { $_.SID.Value })
        if ($adminSids -contains $accountSid) {
            $keyPath = Join-Path $env:ProgramData 'ssh\administrators_authorized_keys'
            New-Item -ItemType Directory -Path (Split-Path $keyPath) -Force | Out-Null
        } else {
            $profileKeyDir = (Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\$accountSid").ProfileImagePath
            $keyPath = Join-Path $profileKeyDir '.ssh\authorized_keys'
            New-Item -ItemType Directory -Path (Split-Path $keyPath) -Force | Out-Null
        }

        $existingKeys = if (Test-Path $keyPath) { Get-Content -Path $keyPath } else { @() }
        if ($existingKeys -notcontains $publicKey) {
            Add-Content -Path $keyPath -Value $publicKey -Encoding ascii
        }

        if ($keyPath -like '*administrators_authorized_keys') {
            & icacls.exe $keyPath /inheritance:r /grant '*S-1-5-32-544:F' /grant '*S-1-5-18:F' | Out-Null
        } else {
            & icacls.exe $keyPath /inheritance:r /grant "${account}:F" /grant '*S-1-5-18:F' | Out-Null
        }
        if ($LASTEXITCODE -ne 0) { throw 'Could not set secure permissions on the authorized key file.' }
        Write-Log "Installed the public key for $account."
    }

    if ($Action -eq 'DisablePassword') {
        if (-not (Test-Path $sshConfig)) { throw "SSH server config not found: $sshConfig" }
        $configLines = @(Get-Content -Path $sshConfig)
        $foundPasswordDirective = $false
        for ($i = 0; $i -lt $configLines.Count; $i++) {
            if ($configLines[$i] -match '^\s*#?\s*PasswordAuthentication\s+') {
                $configLines[$i] = 'PasswordAuthentication no'
                $foundPasswordDirective = $true
            }
        }
        if (-not $foundPasswordDirective) {
            $matchIndex = -1
            for ($i = 0; $i -lt $configLines.Count; $i++) {
                if ($configLines[$i] -match '^\s*Match\s+') { $matchIndex = $i; break }
            }
            if ($matchIndex -ge 0) {
                if ($matchIndex -eq 0) {
                    $configLines = @('PasswordAuthentication no') + @($configLines)
                } else {
                    $configLines = @($configLines[0..($matchIndex - 1)]) + @('PasswordAuthentication no') + @($configLines[$matchIndex..($configLines.Count - 1)])
                }
            } else {
                $configLines += 'PasswordAuthentication no'
            }
        }

        $backupPath = "$sshConfig.ssh-setup-wizard.bak"
        if (-not (Test-Path $backupPath)) { Copy-Item -Path $sshConfig -Destination $backupPath }
        [IO.File]::WriteAllLines($sshConfig, [string[]]$configLines, [Text.Encoding]::ASCII)
        & $sshDaemon -t
        if ($LASTEXITCODE -ne 0) {
            Copy-Item -Path $backupPath -Destination $sshConfig -Force
            throw 'OpenSSH rejected the config. The original sshd_config was restored from backup.'
        }
        Write-Log "SSH password authentication disabled. Backup: $backupPath"
    }

    if ($Action -in @('Prepare', 'InstallKey')) {
        $ruleName = 'SSHSetupWizard-In-TCP'
        $rule = Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue
        if ($null -eq $rule) {
            New-NetFirewallRule -Name $ruleName -DisplayName 'SSH Setup Wizard (local network)' `
                -Enabled True -Direction Inbound -Protocol TCP -LocalPort 22 `
                -Action Allow -Profile Any -RemoteAddress LocalSubnet | Out-Null
        } else {
            Set-NetFirewallRule -Name $ruleName -Enabled True -Profile Any | Out-Null
            $addressFilter = Get-NetFirewallAddressFilter -AssociatedNetFirewallRule $rule
            Set-NetFirewallAddressFilter -InputObject $addressFilter -RemoteAddress LocalSubnet
        }

        Set-Service -Name sshd -StartupType Automatic
        $service = Get-Service -Name sshd
        if ($service.Status -eq 'Running') { Restart-Service -Name sshd } else { Start-Service -Name sshd }
        Write-Log 'Windows SSH server is running. Inbound SSH is allowed from the local subnet.'
    }
    exit 0
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
