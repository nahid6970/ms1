"""
explorer_tabs.py
Monitors for new File Explorer windows and merges them as tabs
into an existing Explorer window instead of opening separately.
Run in background: pythonw explorer_tabs.py
"""

import time
import urllib.parse
import win32gui
import win32con
import win32api
import comtypes.client

POLL_INTERVAL = 0.4   # seconds between checks
NEW_WIN_WAIT  = 0.6   # wait for new window to fully load


def get_explorer_windows():
    """Return {hwnd: set_of_paths} for all visible CabinetWClass windows."""
    result = {}
    try:
        shell = comtypes.client.CreateObject('Shell.Application')
        for w in shell.Windows():
            try:
                hwnd = w.HWND
                url  = w.LocationURL
                if not url:
                    continue
                path = urllib.parse.unquote(url.replace('file:///', '').replace('/', '\\'))
                result.setdefault(hwnd, set()).add(path)
            except Exception:
                pass
    except Exception:
        pass
    return result


def get_cabinet_hwnds():
    hwnds = set()
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == 'CabinetWClass':
            hwnds.add(hwnd)
    win32gui.EnumWindows(cb, None)
    return hwnds


def open_path_as_tab(target_hwnd, path):
    """
    Focus target_hwnd, open a new tab with Ctrl+T,
    then type the path into the address bar and navigate.
    """
    # Bring window to front
    win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(target_hwnd)
    time.sleep(0.15)

    # Ctrl+T → new tab
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord('T'), 0, 0, 0)
    win32api.keybd_event(ord('T'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

    # Alt+D → focus address bar
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
    win32api.keybd_event(ord('D'), 0, 0, 0)
    win32api.keybd_event(ord('D'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)

    # Type path and press Enter
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(path)
    win32clipboard.CloseClipboard()

    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord('V'), 0, 0, 0)
    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.4)


def close_window(hwnd):
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)


def main():
    known_hwnds = get_cabinet_hwnds()
    print(f"[explorer_tabs] Running. Tracking {len(known_hwnds)} window(s). Press Ctrl+C to stop.")

    while True:
        time.sleep(POLL_INTERVAL)
        current = get_cabinet_hwnds()
        new_hwnds = current - known_hwnds

        for new_hwnd in new_hwnds:
            # Wait for the window to finish loading
            time.sleep(NEW_WIN_WAIT)

            # Re-check it still exists
            if not win32gui.IsWindow(new_hwnd):
                continue

            # Find an existing Explorer window to merge into
            existing = current - new_hwnds - {new_hwnd}
            # Also re-check known_hwnds for still-alive windows
            for h in list(known_hwnds):
                if win32gui.IsWindow(h):
                    existing.add(h)

            if not existing:
                # No existing window — let this one become the main window
                print(f"[explorer_tabs] First window {new_hwnd}, keeping as-is.")
                known_hwnds.add(new_hwnd)
                continue

            # Get the path of the new window
            win_paths = get_explorer_windows()
            paths = win_paths.get(new_hwnd, set())

            if not paths:
                print(f"[explorer_tabs] Could not get path for {new_hwnd}, skipping.")
                known_hwnds.add(new_hwnd)
                continue

            path = next(iter(paths))
            target = next(iter(existing))

            print(f"[explorer_tabs] Merging {new_hwnd} ({path!r}) into {target}")
            open_path_as_tab(target, path)
            time.sleep(0.3)
            close_window(new_hwnd)

        # Update known set (remove closed windows, add new ones we decided to keep)
        known_hwnds = {h for h in (known_hwnds | current) if win32gui.IsWindow(h)}


if __name__ == '__main__':
    main()
