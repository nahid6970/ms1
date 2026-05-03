"""
explorer_tabs.py
Monitors for new File Explorer windows and merges them as tabs
into an existing Explorer window using Windows API (no keyboard simulation).

Uses:
  - WM_COMMAND 0xA21B  → opens a new tab in an existing Explorer window
  - IWebBrowser2.Navigate2 via Shell.Application COM → navigates the new tab
  - IShellBrowser.BrowseObject (via Shell COM) → closes the new window

Run silently: pythonw explorer_tabs.py
"""

import time
import ctypes
import urllib.parse
import win32gui
import win32con
import comtypes.client
import comtypes.automation

POLL_INTERVAL = 0.3
NEW_WIN_WAIT  = 0.5

WM_COMMAND    = 0x0111
NEW_TAB_CMD   = 0xA21B


def get_cabinet_hwnds():
    hwnds = set()
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == 'CabinetWClass':
            hwnds.add(hwnd)
    win32gui.EnumWindows(cb, None)
    return hwnds


def get_shell_windows():
    """Return list of IWebBrowser2 dispatch objects from Shell.Application."""
    try:
        shell = comtypes.client.CreateObject('Shell.Application')
        return list(shell.Windows())
    except Exception:
        return []


def get_hwnd_paths(hwnd):
    """Return set of URL strings for all tabs in a given CabinetWClass hwnd."""
    paths = set()
    for w in get_shell_windows():
        try:
            if w.HWND == hwnd and w.LocationURL:
                paths.add(w.LocationURL)
        except Exception:
            pass
    return paths


def get_first_tab_hwnd(cabinet_hwnd):
    """Return the first ShellTabWindowClass child of a CabinetWClass window."""
    result = []
    def cb(hwnd, _):
        if win32gui.GetClassName(hwnd) == 'ShellTabWindowClass':
            result.append(hwnd)
            return False
    try:
        win32gui.EnumChildWindows(cabinet_hwnd, cb, None)
    except Exception:
        pass
    return result[0] if result else None


def open_as_tab(target_cabinet_hwnd, path):
    """
    Open `path` as a new tab in `target_cabinet_hwnd`.
    1. Send WM_COMMAND 0xA21B to ShellTabWindowClass → creates blank tab
    2. Find the blank tab via Shell.Application
    3. Navigate2 to path
    """
    tab_hwnd = get_first_tab_hwnd(target_cabinet_hwnd)
    if not tab_hwnd:
        return False

    # Snapshot existing shell window objects before opening new tab
    before = {id(w) for w in get_shell_windows()}

    ctypes.windll.user32.SendMessageW(tab_hwnd, WM_COMMAND, NEW_TAB_CMD, 0)
    time.sleep(0.5)

    # Find the new blank tab (LocationURL == '')
    blank = None
    for w in get_shell_windows():
        try:
            if w.HWND == target_cabinet_hwnd and w.LocationURL == '':
                blank = w
                break
        except Exception:
            pass

    if not blank:
        # Fallback: find any new entry not in before snapshot
        for w in get_shell_windows():
            try:
                if id(w) not in before and w.HWND == target_cabinet_hwnd:
                    blank = w
                    break
            except Exception:
                pass

    if not blank:
        return False

    v = comtypes.automation.VARIANT()
    v.vt = comtypes.automation.VT_BSTR
    v.value = path
    try:
        blank.Navigate2(v)
    except Exception:
        return False

    return True


def close_shell_window(hwnd):
    """Close all shell windows (tabs) belonging to a CabinetWClass hwnd."""
    for w in get_shell_windows():
        try:
            if w.HWND == hwnd:
                w.Quit()
                return
        except Exception:
            pass
    # Fallback: WM_CLOSE
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)


def main():
    known_hwnds = get_cabinet_hwnds()
    print(f"[explorer_tabs] Running. Tracking {len(known_hwnds)} window(s). Ctrl+C to stop.")

    while True:
        time.sleep(POLL_INTERVAL)

        current = get_cabinet_hwnds()
        new_hwnds = current - known_hwnds

        for new_hwnd in new_hwnds:
            # Hide immediately to eliminate the visible flash
            win32gui.ShowWindow(new_hwnd, win32con.SW_HIDE)
            time.sleep(NEW_WIN_WAIT)

            if not win32gui.IsWindow(new_hwnd):
                continue

            # Existing windows (excluding the new one)
            existing = {h for h in (known_hwnds | current) - {new_hwnd} if win32gui.IsWindow(h)}

            if not existing:
                print(f"[explorer_tabs] First window {new_hwnd}, keeping.")
                known_hwnds.add(new_hwnd)
                continue

            # Get path of new window
            paths = get_hwnd_paths(new_hwnd)
            if not paths:
                print(f"[explorer_tabs] No path for {new_hwnd}, skipping.")
                known_hwnds.add(new_hwnd)
                continue

            path = next(iter(paths))
            # Decode file:/// URL to a plain path
            plain_path = urllib.parse.unquote(path.replace('file:///', '').replace('/', '\\'))
            target = next(iter(existing))

            print(f"[explorer_tabs] Merging {new_hwnd} ({plain_path!r}) → {target}")

            if open_as_tab(target, plain_path):
                time.sleep(0.3)
                close_shell_window(new_hwnd)
            else:
                print(f"[explorer_tabs] Failed to open tab, leaving window as-is.")
                known_hwnds.add(new_hwnd)
                continue

        known_hwnds = {h for h in (known_hwnds | current) if win32gui.IsWindow(h)}


if __name__ == '__main__':
    main()
