# Windows Customization & qBittorrent Setup Guide (AI Agent SOP)

This guide documents the exact procedures to configure qBittorrent dark themes, disable Windows transparency/glassy effects, and disable Windows 11 rounded window corners permanently at startup.

---

## 🎨 1. qBittorrent Dark Theme Setup

### Environment Detection
- **Scoop Config Path**: `C:\Users\nahid\scoop\persist\qbittorrent\profile\qBittorrent\config\qBittorrent.ini`
- **Themes Folder**: `C:\Users\nahid\scoop\persist\qbittorrent\themes\`
- **Executable**: `C:\Users\nahid\scoop\shims\qbittorrent.exe`

### Pre-Downloaded Qt6 Dark Themes
- `catppuccin-mocha.qbtheme` *(Currently Active)*
- `catppuccin-macchiato.qbtheme`
- `dracula.qbtheme`
- `dark.qbtheme` *(Minimal Dark)*
- `gruvbox-dark.qbtheme`
- `solarized-dark.qbtheme`
- `breeze-dark.qbtheme`
- `mumble-dark.qbtheme`

### INI Configuration Reference
In `qBittorrent.ini`, under the `[Preferences]` section:
```ini
[Preferences]
General\UseCustomUITheme=true
General\CustomUIThemePath=C:/Users/nahid/scoop/persist/qbittorrent/themes/catppuccin-mocha.qbtheme
```

---

## 🪟 2. Windows Transparency / Glassy Effects Disabling

Disabling transparency turns off the glassy/acrylic background blur on the taskbar, Start Menu, settings, and window borders, saving GPU/CPU resources (`dwm.exe`).

### Registry Setting
- **Key Path**: `HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize`
- **Value Name**: `EnableTransparency`
- **Value**: `0` (Disabled) / `1` (Enabled)

### PowerShell Command
```powershell
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0
```

---

## 📐 3. Windows 11 Disable Rounded Window Corners (Startup Task)

Windows 11 hardcodes rounded window corners in `uDWM.dll`. The open-source utility `win11-toggle-rounded-corners` memory-patches `dwm.exe` to enforce square window corners.

### Installer Location
- Downloaded installer: `C:\Users\nahid\Downloads\win11-toggle-rounded-corners-setup.exe`
- GitHub Repository: `https://github.com/rich-ayr/win11-toggle-rounded-corners`

### Setup & Startup Persistence
1. Run `win11-toggle-rounded-corners-setup.exe`.
2. Completing the installer registers a Windows Scheduled Task (`Win11ToggleRoundedCorners`) that runs automatically at Windows logon/startup with highest privileges.
3. This ensures square window corners persist across system reboots and logons automatically.
