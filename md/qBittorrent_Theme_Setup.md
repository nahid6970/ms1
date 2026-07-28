# qBittorrent Theme Setup Guide (AI Agent SOP)

This guide documents the exact procedure to detect, download, configure, and apply custom Qt6 `.qbtheme` files for qBittorrent on Windows (supporting both standard AppData and Scoop installations).

---

## 📌 Environment Detection

1. **Config File Paths**:
   - **Scoop Installation**: `C:\Users\nahid\scoop\persist\qbittorrent\profile\qBittorrent\config\qBittorrent.ini`
   - **Standard AppData**: `%APPDATA%\qBittorrent\qBittorrent.ini`

2. **Executable Paths**:
   - **Scoop**: `C:\Users\nahid\scoop\shims\qbittorrent.exe`
   - **Standard**: `C:\Program Files\qBittorrent\qbittorrent.exe`

3. **Themes Storage Location**:
   - `C:\Users\nahid\scoop\persist\qbittorrent\themes\`

---

## 📦 Theme Sources (Qt6 / qBittorrent v5.x+)

Direct GitHub Releases containing compiled `.qbtheme` bundle files:
- **Catppuccin** (`mocha`, `macchiato`, `frappe`):  
  `https://github.com/catppuccin/qbittorrent/releases/latest`
- **MahdiMirzadeh** (`dracula`, `dark`, `gruvbox-dark`, `solarized-dark`):  
  `https://github.com/MahdiMirzadeh/qbittorrent/releases/latest`
- **JagannathArjun** (`mumble-dark`, `breeze-dark`):  
  `https://github.com/jagannatharjun/qbt-theme/releases/latest`

---

## ⚙️ Automated Execution Workflow

When modifying qBittorrent configuration via script, always terminate the running process first. Otherwise, qBittorrent will overwrite `qBittorrent.ini` upon exit.

```powershell
# 1. Gracefully terminate qBittorrent
Stop-Process -Name "qbittorrent" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# 2. Ensure themes directory exists
$themeDir = "C:\Users\nahid\scoop\persist\qbittorrent\themes"
if (!(Test-Path $themeDir)) { New-Item -ItemType Directory -Path $themeDir | Out-Null }

# 3. Download themes if missing (e.g. Catppuccin Mocha)
$mochaUrl = "https://github.com/catppuccin/qbittorrent/releases/download/v2.0.1/catppuccin-mocha.qbtheme"
$mochaPath = Join-Path $themeDir "catppuccin-mocha.qbtheme"
if (!(Test-Path $mochaPath)) {
    Invoke-WebRequest -Uri $mochaUrl -OutFile $mochaPath -UserAgent "Mozilla/5.0"
}

# 4. Update qBittorrent.ini
$iniPath = "C:\Users\nahid\scoop\persist\qbittorrent\profile\qBittorrent\config\qBittorrent.ini"
$content = Get-Content $iniPath
$cleanContent = $content | Where-Object { 
    $_ -notmatch "General\\UseCustomUITheme=" -and $_ -notmatch "General\\CustomUIThemePath=" 
}

$prefIndex = $cleanContent.IndexOf("[Preferences]")
if ($prefIndex -ge 0) {
    $formattedPath = "C:/Users/nahid/scoop/persist/qbittorrent/themes/catppuccin-mocha.qbtheme"
    $firstPart = $cleanContent[0..$prefIndex]
    $secondPart = $cleanContent[($prefIndex + 1)..($cleanContent.Count - 1)]
    $inserted = @(
        "General\UseCustomUITheme=true",
        "General\CustomUIThemePath=$formattedPath"
    )
    $finalContent = $firstPart + $inserted + $secondPart
    $finalContent | Set-Content $iniPath -Encoding UTF8
}

# 5. Relaunch qBittorrent
Start-Process "C:\Users\nahid\scoop\shims\qbittorrent.exe"
```

---

## 🛠️ INI Settings Reference

In `qBittorrent.ini`, under the `[Preferences]` section:

```ini
[Preferences]
General\UseCustomUITheme=true
General\CustomUIThemePath=C:/Users/nahid/scoop/persist/qbittorrent/themes/catppuccin-mocha.qbtheme
```

---

## 🖥️ Manual GUI Switch Method

1. Open **qBittorrent**.
2. Go to **Tools** > **Options** (`Alt + O`).
3. Navigate to **Behavior** > **Interface**.
4. Check **Use custom UI theme**.
5. Click `...` and pick any file from `C:\Users\nahid\scoop\persist\qbittorrent\themes\`.
6. Click **Apply** and restart qBittorrent.
