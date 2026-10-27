"""
F1 Relay — intercepts F1 at the OS level and sends Ctrl+Shift+E instead
when Google Chrome is the focused window. This lets the extension's
"Reveal In Explorer" command work with F1, which Chrome normally reserves
for its Help page.

Run with:  pythonw f1_relay.py   (no console window)
       or  python  f1_relay.py   (with console, for debugging)

Requires: pip install keyboard
"""
import ctypes
import ctypes.wintypes
import sys
import os

user32 = ctypes.windll.user32

# ── Detect if Chrome is the focused window ────────────────────────────────────

def is_chrome_focused():
    """True if the foreground window belongs to Chrome (class Chrome_WidgetWin_1)."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value == 'Chrome_WidgetWin_1'


# ── Import keyboard (graceful error if missing) ──────────────────────────────

try:
    import keyboard
except ImportError:
    print('ERROR: "keyboard" library not installed.  Run:  pip install keyboard')
    sys.exit(1)


# ── Hook ─────────────────────────────────────────────────────────────────────

def on_key_event(e):
    """
    Called for every key event when suppress=True.
    Return True  → let the event through.
    Return False → suppress the event (system never sees it).
    """
    if e.name == 'f1':
        if is_chrome_focused():
            if e.event_type == keyboard.KEY_DOWN:
                keyboard.send('ctrl+shift+f')
            return False   # suppress F1 down AND up on Chrome
        return True        # let F1 through for non-Chrome apps
    return True            # let every other key through

keyboard.hook(on_key_event, suppress=True)

print('[F1 Relay] Running.  F1 → Ctrl+Shift+E when Chrome is focused.')
print('[F1 Relay] Press Ctrl+C to stop.')

keyboard.wait()
