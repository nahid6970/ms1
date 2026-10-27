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
    ├── com.delta.reveal_explorer.json     # Native messaging manifest
    ├── install_host.py                    # One-time Windows registry installer
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
  → Chrome spawns reveal_explorer/host.py via the registered native messaging host
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

1. **Register the native messaging host** (run once):
   ```
   python reveal_explorer/install_host.py <EXTENSION_ID>
   ```
   Find your extension ID at `chrome://extensions`.

2. **Reload the extension** in `chrome://extensions`.

3. **Enable "Allow access to file URLs"** — chrome://extensions → Details → toggle ON.

4. **Toggle "Reveal In Explorer" ON** in the popup.

5. **Test** — open a `file:///` URL, press Ctrl+Shift+F.

---

## Changing the Hotkey

The hotkey is defined in two places — update both:

1. **`manifest.json → commands.reveal-in-explorer.suggested_key.default`**
2. **`user_scripts/reveal_in_explorer.js`** — the keydown check

If using `f1_relay.py`, also update the `keyboard.send()` call.

Safe combos: `Ctrl+Shift+<letter>`. Avoid F1 (reserved), Alt+single-letter (Chrome menu shortcuts).
