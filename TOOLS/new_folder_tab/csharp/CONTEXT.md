# ExplorerTabs — C# Implementation

## What it does
Background process that intercepts new File Explorer windows and merges them as tabs into an existing Explorer window. The new window is never visible to the user.

## Files
- `Program.cs` — entire implementation, single file, no dependencies beyond .NET 9
- `ExplorerTabs.csproj` — WinExe, net9.0-windows, no NuGet packages
- `start_explorer_tabs.bat` — silent launcher (`start "" ExplorerTabs.exe`)

## How it works

### 1. Detection — `SetWinEventHook`
Hooks `EVENT_OBJECT_CREATE` through `EVENT_OBJECT_SHOW` with `WINEVENT_OUTOFCONTEXT`.  
Fires on every window creation system-wide. Filters to `CabinetWClass` (File Explorer windows).  
Tracks known HWNDs in `_knownHwnds` (HashSet). New = not in set.

### 2. Instant hide — `MakeInvisible`
Called **synchronously in the hook callback** (message pump thread) before spawning the worker.  
Sets `WS_EX_LAYERED` + `SetLayeredWindowAttributes(alpha=0)` → window is fully transparent at the compositor level. Explorer can paint freely, nothing is visible.  
**Do not use `SW_HIDE` here** — it allows one paint cycle before hiding, causing a flash.

### 3. Wait for path — `WaitForTabTitle`
Worker thread (STA) polls `ShellTabWindowClass` child window title every 50ms.  
Title starts as `"File Explorer"`, changes to the actual folder name (~600ms) when loaded.  
Once title is set, queries `Shell.Application.Windows()` via COM for the full `LocationURL`.

**Why STA thread:** `Shell.Application` COM object requires STA apartment. ThreadPool threads are MTA and will fail with `E_NOINTERFACE`.

**Why `dynamic` for Shell.Application:** `GetTypeFromCLSID(CLSID_ShellWindows)` creates an object that doesn't QI to `IShellWindows` directly. Using `GetTypeFromProgID("Shell.Application")` + `dynamic` dispatch works correctly.

### 4. Open as tab — `OpenAsTab`
1. Find `ShellTabWindowClass` child of the target `CabinetWClass` window
2. `SendMessage(tabHwnd, WM_COMMAND, 0xA21B, 0)` — undocumented but stable command that opens a new blank tab in Explorer
3. Wait 500ms for the blank tab to appear in `Shell.Application.Windows()` (identified by empty `LocationURL`)
4. Call `IWebBrowser2.Navigate2(path)` on the blank tab to navigate it

### 5. Cleanup
- `IWebBrowser2.Quit()` on the new (hidden) window to close it
- `ShowWindow(target, SW_RESTORE)` + `SetForegroundWindow(target)` to bring the merged window forward

## Key constants / magic values
| Name | Value | Purpose |
|---|---|---|
| `NEW_TAB_CMD` | `0xA21B` (41499) | Undocumented WM_COMMAND to open new Explorer tab |
| `EVENT_OBJECT_CREATE` | `0x8000` | WinEvent: window created |
| `EVENT_OBJECT_SHOW` | `0x8002` | WinEvent: window shown |
| `WS_EX_LAYERED` | `0x80000` | Extended style for transparent windows |
| `LWA_ALPHA` | `0x2` | Flag for alpha-based transparency |
| `GWL_EXSTYLE` | `-20` | Index for `GetWindowLong` extended style |

## Window class hierarchy (Explorer)
```
CabinetWClass                  ← top-level Explorer window (one per window, not per tab)
  ShellTabWindowClass          ← one per tab, title = folder name
  ShellTabWindowClass
  Microsoft.UI.Content.DesktopChildSiteBridge
  InputSiteWindowClass
```

## Known limitations
- `WINEVENT_OUTOFCONTEXT` is asynchronous — the hook fires via the message queue, not inline. `MakeInvisible` is called as fast as possible but there is a theoretical race on very slow machines.
- `WM_COMMAND 0xA21B` is undocumented. It has been stable across Windows 11 22H2–26H2 but could break in a future update.
- The 500ms sleep in `OpenAsTab` after sending `WM_COMMAND` is needed for Explorer to create the blank tab. Reducing it may cause `FindBlankTab` to return null.

## Build & run
```powershell
dotnet build -c Release
.\bin\Release\net9.0-windows\ExplorerTabs.exe
```
Requires .NET 9 runtime and Windows 11 22H2+ (Explorer tabs feature).
