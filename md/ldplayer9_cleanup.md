# LDPlayer 9 Ad Cleanup Guide

> Date: 2026-10-22
> LDPlayer install path: `C:\LDPlayer\LDPlayer9`
> Ad cache path: `%AppData%\XuanZhi9\cache`

## What was causing the ads

LDPlayer 9 injects ads through multiple channels:

1. **Ad cache folder** (`%AppData%\XuanZhi9\cache`) — stores downloaded ad wallpapers and promo images from `ldrescdn.com`
2. **`ldplayerpartner.exe`** — the ad/partner delivery module bundled with LDPlayer
3. **Ad domains** — `res.ldrescdn.com`, `cdn.ldplayer.net`, `en.ldplayer.net`, `ldmnq.com`, `www.ldmnq.com` serve ad assets
4. **In-emulator LD apps** — `com.android.ld.appstore` can provide LDPlayer promotions; disabling it removed the reported ad issue

---

## Layer 1 — Cleaned ad cache files

Deleted 9 ad files from `%AppData%\XuanZhi9\cache`:

- `cpt_ad.data`
- `.bmp.curl`
- `httpsres_ldrescdn_comrmsuploadadfiln09qmm7i-1770619933_jpg.webp`
- `httpsres_ldrescdn_comrmsuploadadhh5o45pm2an-1792577923_jpg.webp`
- `httpsres_ldrescdn_comrmsuploadadhh5o45pm2an-1792577923_jpg.webp.png`
- `httpsres_ldrescdn_comrmsuploadadx98ifbtown8-1792578067_png.webp`
- `httpsres_ldrescdn_comrmsuploadadyt7bic1wyji-1792578128_png.webp`
- `httpsres_ldrescdn_comrmsuploadadyt7bic1wyji-1792578128_png.webp.png`
- `httpsres_ldrescdn_comrmsuploaden3c2f4tlfszg-1778318860_png.png`

Then locked the cache folder to **read-only** (disabled inheritance, removed all write permissions) so LDPlayer cannot re-download ad images.

### To undo

Right-click `%AppData%\XuanZhi9\cache` → Properties → Security → Advanced → Enable inheritance → Apply.

---

## Layer 2 — Blocked ad domains in Windows hosts file

Added the following entries to `C:\Windows\System32\drivers\etc\hosts`:

```
0.0.0.0 res.ldrescdn.com
0.0.0.0 cdn.ldplayer.net
0.0.0.0 en.ldplayer.net
0.0.0.0 ldmnq.com
0.0.0.0 www.ldmnq.com
```

Flushed DNS cache with `ipconfig /flushdns`.

### To undo

Open `C:\Windows\System32\drivers\etc\hosts` in Notepad (as admin) and delete those 5 lines.

---

## Layer 3 — Disabled ad partner module

- Renamed `C:\LDPlayer\LDPlayer9\ldplayerpartner.exe` → `ldplayerpartner.exe.bak`
- Added Windows Firewall outbound block rule: `LDPlayer Ad Block - ldplayerpartner`

### To undo

```cmd
ren "C:\LDPlayer\LDPlayer9\ldplayerpartner.exe.bak" "ldplayerpartner.exe"
powershell -Command "Remove-NetFirewallRule -DisplayName 'LDPlayer Ad Block - ldplayerpartner'"
```

---

## Layer 4 — Remove the LDPlayer TOP UP promotion

### A) Enable local ADB debugging

1. Close instance 0.
2. Back up `C:\LDPlayer\LDPlayer9\vms\config\leidian0.config`.
3. Set `basicSettings.adbDebug` to `1` in that config.
4. Start instance 0 again.


### B) Disable the LD App Store

Run:

```cmd
C:\LDPlayer\LDPlayer9\ldconsole.exe adb --index 0 --command "shell pm disable-user --user 0 com.android.ld.appstore"
```

### C) Refresh the launcher so the promoted tile disappears

```cmd
C:\LDPlayer\LDPlayer9\ldconsole.exe adb --index 0 --command "shell am force-stop com.ldmnq.launcher3"
C:\LDPlayer\LDPlayer9\ldconsole.exe adb --index 0 --command "shell monkey -p com.ldmnq.launcher3 1"
```

The launcher restarts to the home screen. Restarting the LDPlayer instance also refreshes it.

### To undo

```cmd
C:\LDPlayer\LDPlayer9\ldconsole.exe adb --index 0 --command "shell pm enable com.android.ld.appstore"
```

Leave the launcher enabled; only disable the LD App Store.
---
## Optional — Block in-app ads

Inside LDPlayer, go to **Settings → Network & Internet → Private DNS** and set:

```
dns.adguard-dns.com
```

This blocks ads inside regular Android apps too (separate from LDPlayer's own ads).

---

## Sources

- [Kill ads on LDPlayer — Full Guide (GitHub Gist)](https://gist.github.com/minanagehsalalma/e6497ad1db67929593ce8af7d5688a13)
- [LDPlayer_Debloater (GitHub)](https://github.com/Red0Hood/LDPlayer_Debloater)
- [Block-ads-for-LDplayer (GitHub)](https://github.com/HideCM/Block-ads-for-LDplayer)








