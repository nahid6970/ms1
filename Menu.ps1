# Define colors
$green = "`e[32m"
$yellow = "`e[33m"
$red = "`e[31m"
$reset = "`e[0m"

# Define menu items (label, function name)
$menuItems = @(
    @{ Label = "Git Pull [ms1]";             Action = "Update-MS1" },
    @{ Label = "Copy Files";                Action = "Copy-Files" },
    @{ Label = "Fix LDPlayer Corrupted VM";Action = "Fix_ldplayer_vmp" },
    @{ Label = "Font Setup";                Action = "Install-Fonts" },
    @{ Label = "Desktop Environment";       Action = "Setup-Desktop" },
    @{ Label = "YAY Setup";                 Action = "Setup-YAY" },
    @{ Label = "Bottles";                   Action = "Setup-Bottles" },
    @{ Label = "Wine";                      Action = "Setup-Wine" },
    @{ Label = "Lutris";                    Action = "Setup-Lutris" },
    @{ Label = "Steam";                     Action = "Setup-Steam" },
    @{ Label = "About";                     Action = "Show-About" },
    @{ Label = "GPU Drivers";              Action = "Check-GPU" },
    @{ Label = "Heroic Games Launcher";     Action = "Install-Heroic" },
    @{ Label = "Hyprland";                  Action = "Setup-Hyprland" },
    @{ Label = "SDDM Theme";                Action = "Setup-SDDM" },
    @{ Label = "Disable Bell";              Action = "Disable-Bell" },
    @{ Label = "Hyprland Config";           Action = "Config-Hyprland" },
    @{ Label = "Neovim Config";             Action = "Config-Neovim" },
    @{ Label = "TTY Autologin";             Action = "Enable-AutoLogin" }
)

# Define hotkeys
$hotkeys = @{
    "c" = "Close-Script"
    "e" = "Exit-Script"
    "x" = "Test-Function"
}

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "$yellow Select an option:$reset"

    for ($i = 0; $i -lt $menuItems.Count; $i++) {
        $item = $menuItems[$i]
        Write-Host "$green$($i + 1)) $($item.Label)$reset"
    }

    Write-Host "$red c) Close"
    Write-Host " e) Exit"
    Write-Host " x) Test$reset"
    Write-Host ""
}

# Example dummy functions (implement these yourself)
function Update-MS1         { cmd /c start rclone ncdu d: }
function Copy-Files         { 
    Start-Process powershell -ArgumentList 'rclone ncdu d:'
    Start-Process powershell -ArgumentList 'rclone ncdu c:'

}
function Fix_ldplayer_vmp   { 
    Set-Location "C:\Program Files (x86)\VMware\VMware Workstation"
    .\vmware-vdiskmanager.exe -R "C:\LDPlayer\LDPlayer9\vms\leidian0\data.vmdk"
 }
 
function Install-Fonts      { Write-Host "Setting up fonts..." }
function Setup-Desktop      { Write-Host "Installing desktop environment..." }
function Setup-YAY          { Write-Host "Setting up YAY..." }
function Setup-Bottles      { Write-Host "Installing Bottles..." }
function Setup-Wine         { Write-Host "Installing Wine..." }
function Setup-Lutris       { Write-Host "Installing Lutris..." }
function Setup-Steam        { Write-Host "Installing Steam..." }
function Show-About         { Write-Host "Showing about info..." }
function Check-GPU          { Write-Host "Checking GPU drivers..." }
function Install-Heroic     { Write-Host "Installing Heroic Games Launcher..." }
function Setup-Hyprland     { Write-Host "Setting up Hyprland..." }
function Setup-SDDM         { Write-Host "Applying SDDM theme..." }
function Disable-Bell       { Write-Host "Disabling system bell..." }
function Config-Hyprland    { Write-Host "Configuring Hyprland..." }
function Config-Neovim      { Write-Host "Configuring Neovim..." }
function Enable-AutoLogin   { Write-Host "Enabling TTY Autologin..." }

# Hotkey functions
function Close-Script       { Write-Host "Closing script..." }
function Exit-Script        { exit }
function Test-Function      { Write-Host "Test function triggered." }

# Main loop
while ($true) {
    Show-Menu
    $choice = Read-Host "Enter choice"

    if ($choice -match '^\d+$' -and [int]$choice -le $menuItems.Count) {
        $index = [int]$choice - 1
        $action = $menuItems[$index].Action
        Invoke-Command -ScriptBlock (Get-Command $action).ScriptBlock
    }
    elseif ($hotkeys.ContainsKey($choice)) {
        $func = $hotkeys[$choice]
        Invoke-Command -ScriptBlock (Get-Command $func).ScriptBlock
    }
    else {
        Write-Host "$red Invalid option. Please try again. $reset"
    }
}
