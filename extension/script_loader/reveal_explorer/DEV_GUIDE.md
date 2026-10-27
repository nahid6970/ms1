# Reveal In Explorer — Developer Guide

## What This Tool Does

When you press **Ctrl+Shift+F** on a `file:///` page in Chrome, this tool opens Windows File Explorer with the file selected. An optional OS-level F1 relay can make F1 trigger the same action when Chrome is focused.

---

## Project Structure

```
script_loader/
├── manifest.json                          # Commands entry: Ctrl+Shift+F → "reveal-in-explorer"
├── background.js                          # commands.onCommand listener → native messaging
├── user_scripts/
│   └── reveal_in_explorer.js             # Content script fallback (Ctrl+Shift+F keydown)
└── reveal_explorer/                       # Native messaging host + utilities
    ├── host.py                            # Reads file:/// URL → runs explorer.exe /select
    ├── run_host.bat                       # Generated Windows launcher for host.py
    ├── com.delta.reveal_explorer.json     # Native messaging manifest
    ├── install_host.py                    # Windows registry installer called by run.py
    ├── f1_relay.py                        # OS-level F1 → Ctrl+Shift+F relay (optional)
    ├── requirements.txt                   # keyboard lib for f1_relay.py
    └── DEV_GUIDE.md                       # This file
```

---

## How Ctrl+Shift+F → File Explorer Works

```
file:// page (Ctrl+Shift+F pressed)
  → chrome.commands.onCommand fires in background.js (browser-level intercept)
  → background.js calls chrome.runtime.sendNativeMessage('com.delta.reveal_explorer', { url })
  → Chrome starts reveal_explorer/run_host.bat via the registered native messaging host
  → run_host.bat launches host.py with the Python interpreter used by run.py
  → host.py converts file:///C:/path/file.pdf → C:\path\file.pdf
  → host.py runs: explorer.exe /select,"C:\path\file.pdf"
  → File Explorer opens with the file highlighted
```

A content script (`reveal_in_explorer.js`) also listens for Ctrl+Shift+F as a fallback path — it sends a `REVEAL_IN_EXPLORER` message to the background, which calls the same native messaging host.

---

## F1 Relay (Optional)

Chrome hard-blocks F1 at the browser level — it always opens the Help page and no extension API can override it. The `f1_relay.py` script works around this:

- Uses the `keyboard` library to intercept F1 at the OS level
- Checks if the focused window is Chrome (class `Chrome_WidgetWin_1`)
- If Chrome is focused: suppresses F1 and sends Ctrl+Shift+F instead
- If Chrome is not focused: lets F1 through normally

**Run:**
```
pip install keyboard
pythonw reveal_explorer/f1_relay.py
```

---

## Setup

1. **Load this project folder** as an unpacked extension in `chrome://extensions`.

2. **Register the native messaging host** and open Chrome's extensions page:
   ```
   python run.py
   ```
   `run.py` finds the extension ID Chrome assigned to this exact project folder in its profiles, then registers the host for that ID.

3. **Reload the extension** in `chrome://extensions`.

4. **Enable "Allow access to file URLs"** — chrome://extensions → Details → toggle ON.

5. **Check the shortcut** — open `chrome://extensions/shortcuts` and ensure **Ctrl+Shift+F** is assigned to Reveal In Explorer.

6. **Test** — open a `file:///` URL and press Ctrl+Shift+F. If you move the project folder, load the new folder and run `python run.py` again.

---

## Changing the Hotkey

The hotkey is defined in two places — update both:

1. **`manifest.json → commands.reveal-in-explorer.suggested_key.default`**
2. **`user_scripts/reveal_in_explorer.js`** — the keydown check

If using `f1_relay.py`, also update the `keyboard.send()` call.

Safe combos: `Ctrl+Shift+<letter>`. Avoid F1 (reserved), Alt+single-letter (Chrome menu shortcuts).
