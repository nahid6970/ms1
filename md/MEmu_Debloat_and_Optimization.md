# MEmu debloat and startup notes

Updated: 2026-11-03

## Instance

- MEmu instance 0, ADB serial `127.0.0.1:21503`
- MEmu Android 9
- MEmu installation: `D:\Program Files\Microvirt\MEmu`

## Changes applied

1. Started MEmu instance 0 and connected with MEmu's bundled `adb.exe`.
2. Installed Projectivy Launcher 4.54 from the APK link in `MEmu_Remove_Ads_Bloat_Guide.md` and confirmed its package is `com.spocky.projengmenu`.
3. Disabled the two Android cutout emulation packages:
   - `com.android.internal.display.cutout.emulation.corner`
   - `com.android.internal.display.cutout.emulation.double`
4. Removed MEmu's stock launcher for Android user 0 with `pm uninstall -k --user 0 com.microvirt.launcher2`.
5. Started Projectivy and enabled its accessibility service. Both settings are needed for the service to run:
   - `enabled_accessibility_services` = `com.spocky.projengmenu/com.spocky.projengmenu.services.ProjectivyAccessibilityService`
   - `accessibility_enabled` = `1`
6. In Projectivy, enabled **Settings → General → Override current launcher**.
7. Restarted the emulator and verified Projectivy became the active home screen. After the accessibility service and override were set, the home screen appeared promptly; the earlier delay was associated with incomplete launcher setup.

## Commands to reapply after a MEmu update

Run these from PowerShell:

```powershell
$adb = 'D:\Program Files\Microvirt\MEmu\adb.exe'
& $adb -s 127.0.0.1:21503 shell pm disable-user --user 0 com.android.internal.display.cutout.emulation.corner
& $adb -s 127.0.0.1:21503 shell pm disable-user --user 0 com.android.internal.display.cutout.emulation.double
& $adb -s 127.0.0.1:21503 shell settings put secure enabled_accessibility_services com.spocky.projengmenu/com.spocky.projengmenu.services.ProjectivyAccessibilityService
& $adb -s 127.0.0.1:21503 shell settings put secure accessibility_enabled 1
```

If Projectivy is missing, reinstall the APK first. Also confirm **Override current launcher** remains enabled in Projectivy's settings, then restart the instance. Other MEmu instances use different ADB ports.

## Admin-only items not applied

- The Windows hosts file edit was denied because this session was not elevated. The guide's ad-domain entries were not added.
- The optional Windows Firewall IP rules were not added; they also require administrator access.
- The guide's `MemuSVC` startup change was not made because administrator access was unavailable.

No root-level system folders or additional Android packages were removed. Private DNS and an in-emulator ad blocker were not configured.

## Restore MEmu's stock launcher if needed

From an ADB shell, run:

```sh
cmd package install-existing --user 0 com.microvirt.launcher2
```

Then select the desired home app in Android/Projectivy settings.
