# C++ Implementation Plan

## Why C++ over C#
- `WINEVENT_INCONTEXT` — hook fires **synchronously inside Explorer's thread**, before any paint. True zero-flash, no race condition.
- No runtime dependency — standalone ~50KB exe
- SDK headers already define `IShellWindows`, `IWebBrowser2`, no manual interface declarations
- Faster startup (~5ms vs ~200ms)

---

## Project structure
```
cpp/
  ExplorerTabs.sln
  ExplorerTabs/
    ExplorerTabs.vcxproj   ← main exe (WinMain, message pump, hook setup)
  HookDll/
    HookDll.vcxproj        ← injected DLL (the actual INCONTEXT hook)
    HookDll.def            ← exports: InstallHook, UninstallHook
```

The DLL is required because `WINEVENT_INCONTEXT` hooks must live in a DLL that gets loaded into the target process (Explorer).

---

## HookDll — the injected DLL

### What it does
- Exports `InstallHook()` and `UninstallHook()`
- Registers a `WH_CBT` hook (or `WinEventHook` with `WINEVENT_INCONTEXT`) on `HCBT_CREATEWND`
- When a `CabinetWClass` window is created, immediately calls `SetLayeredWindowAttributes(alpha=0)` before returning — this runs inside Explorer's thread, before the first paint

### Key code sketch
```cpp
// HookDll.cpp
#include <windows.h>
#include <shlobj.h>

static HHOOK g_hook = nullptr;
static HWINEVENTHOOK g_winHook = nullptr;
HWND g_newHwnd = nullptr;  // shared memory or named pipe to notify main exe

LRESULT CALLBACK CBTProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HCBT_CREATEWND) {
        HWND hwnd = (HWND)wParam;
        wchar_t cls[64];
        RealGetWindowClassW(hwnd, cls, 64);
        if (wcscmp(cls, L"CabinetWClass") == 0) {
            // Set layered + alpha=0 BEFORE window is shown
            LONG ex = GetWindowLongW(hwnd, GWL_EXSTYLE);
            SetWindowLongW(hwnd, GWL_EXSTYLE, ex | WS_EX_LAYERED);
            SetLayeredWindowAttributes(hwnd, 0, 0, LWA_ALPHA);
            // Notify main exe via PostMessage or named pipe
            PostMessageW(g_mainHwnd, WM_APP + 1, (WPARAM)hwnd, 0);
        }
    }
    return CallNextHookEx(g_hook, nCode, wParam, lParam);
}

extern "C" __declspec(dllexport)
void InstallHook(HWND mainHwnd) {
    g_mainHwnd = mainHwnd;
    g_hook = SetWindowsHookExW(WH_CBT, CBTProc, g_hModule, 0); // 0 = all threads
}

extern "C" __declspec(dllexport)
void UninstallHook() {
    if (g_hook) { UnhookWindowsHookEx(g_hook); g_hook = nullptr; }
}
```

> `WH_CBT` with threadId=0 injects the DLL into every process. Use `HCBT_CREATEWND` to intercept window creation.

---

## Main exe — ExplorerTabs.exe

### What it does
- Loads `HookDll.dll` and calls `InstallHook(hwndMessage)`
- Runs a message pump
- Receives `WM_APP+1` notifications from the DLL with the new HWND
- Spawns an STA thread to: wait for `ShellTabWindowClass` title, get path via `Shell.Application` COM, call `WM_COMMAND 0xA21B` + `IWebBrowser2::Navigate2`, close the new window

### Key code sketch
```cpp
// main.cpp
#include <windows.h>
#include <shlobj.h>
#include <exdisp.h>   // IWebBrowser2
#include <shlguid.h>  // CLSID_ShellWindows

typedef void (*InstallHookFn)(HWND);
typedef void (*UninstallHookFn)();

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {
    CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);

    HMODULE dll = LoadLibraryW(L"HookDll.dll");
    auto install   = (InstallHookFn)GetProcAddress(dll, "InstallHook");
    auto uninstall = (UninstallHookFn)GetProcAddress(dll, "UninstallHook");

    // Create a message-only window to receive notifications
    HWND msgWnd = CreateWindowExW(0, L"STATIC", nullptr, 0, 0,0,0,0,
                                   HWND_MESSAGE, nullptr, nullptr, nullptr);
    // Subclass to handle WM_APP+1
    // ...

    install(msgWnd);

    MSG msg;
    while (GetMessageW(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    uninstall();
    FreeLibrary(dll);
    CoUninitialize();
}
```

### Getting path + opening tab (same logic as C#)
```cpp
// Get path via IShellWindows
IShellWindows* sw;
CoCreateInstance(CLSID_ShellWindows, nullptr, CLSCTX_ALL, IID_PPV_ARGS(&sw));
// iterate sw->Item(i) → QI to IWebBrowser2 → check HWND + LocationURL

// Open new tab
SendMessage(tabHwnd, WM_COMMAND, 0xA21B, 0);
Sleep(500);
// find blank tab, call Navigate2
```

---

## Build setup
- Visual Studio 2022 with "Desktop development with C++" workload
- Or: `cl.exe` from VS Build Tools (free)
- Target: x64, Release, `/O2`
- Link: `user32.lib ole32.lib oleaut32.lib shell32.lib`
- HookDll must be built as a DLL (`/LD`), same bitness as Explorer (x64)

---

## IPC between DLL and main exe
Options (simplest to most robust):
1. **`PostMessage` to a known HWND** — simplest, works fine since both are same-session
2. **Named pipe** — if you need more data than fits in wParam/lParam
3. **Shared memory** — for high-frequency events

For this use case, `PostMessage(mainHwnd, WM_APP+1, (WPARAM)newHwnd, 0)` is sufficient.

---

## What stays the same from C#
- `WM_COMMAND 0xA21B` to open new tab
- `IWebBrowser2::Navigate2` to navigate the blank tab
- `ShellTabWindowClass` title polling to detect when folder is loaded
- `WS_EX_LAYERED` + `LWA_ALPHA=0` for transparency (set in DLL hook, not main exe)
- `IWebBrowser2::Quit()` to close the merged window

---

## What improves over C#
| | C# | C++ |
|---|---|---|
| Flash elimination | `WS_EX_LAYERED` set async (small race) | Set synchronously inside `HCBT_CREATEWND` before first paint |
| Runtime | .NET 9 required | None |
| Exe size | ~150KB + runtime | ~50KB standalone |
| COM interfaces | Manual declarations + `dynamic` | SDK headers (`exdisp.h`, `shlguid.h`) |
