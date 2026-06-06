# YT Like/Dislike Analyzer — Developer Guide

## Project Structure

```
yt_like_dislike/
├── app.py                      # Main PyQt6 GUI
├── host.py                     # Native messaging host (launched by Chrome)
├── install_host.py             # One-time Windows registry installer
├── com.delta.yt_analyzer.json  # Native messaging manifest
├── settings.json               # Persisted user settings (auto-created)
├── requirements.txt
└── DEV_GUIDE.md

extension/script_loader/
├── user_scripts/
│   └── yt_analyzer.js          # F9 hotkey listener, sends URL to background
├── background.js               # Routes LAUNCH_YT_ANALYZER → native messaging
├── popup.js                    # Renders script list + settings panels
└── popup.html                  # Styles for the popup UI
```

---

## How the F9 → GUI Flow Works

```
YouTube page (F9 pressed)
  → yt_analyzer.js sends chrome.runtime.sendMessage({ type: 'LAUNCH_YT_ANALYZER', url })
  → background.js receives it, calls chrome.runtime.sendNativeMessage('com.delta.yt_analyzer', { url })
  → Chrome spawns host.py via the registered native messaging host
  → host.py reads the message, runs: python app.py --url <url>
  → app.py launches GUI pre-filled with the URL and auto-fetches
```

---

## Adding a New Python GUI Tool

1. **Create the tool** in its own folder under `C:\@delta\ms1\TOOLS\`
2. Accept a `--url` or similar CLI arg via `argparse` so the extension can pass data to it
3. **Create a `host.py`** (copy from `yt_like_dislike/host.py`, change the `app.py` path)
4. **Create a native messaging manifest** (copy `com.delta.yt_analyzer.json`, change `name` and `path`)
5. **Run `install_host.py`** with the extension ID to register the host in the Windows registry
6. **Create a `user_scripts/your_tool.js`** that sends `chrome.runtime.sendMessage({ type: 'LAUNCH_YOUR_TOOL', ... })`
7. **Add a handler in `background.js`**:
   ```js
   if (message?.type === 'LAUNCH_YOUR_TOOL') {
     chrome.runtime.sendNativeMessage('com.delta.your_tool', { url: message.url }, ...);
     return true;
   }
   ```

---

## Adding a New User Script (No Native App)

Just drop a `.js` file in `extension/script_loader/user_scripts/`.  
It auto-appears in the popup. The extension injects it on every `http/https` page load when enabled.

---

## Adding Per-Script Settings in the Popup

Pattern used by `yt_analyzer.js` (hotkey) and `local_server_fallback.js` (URLs):

1. In `popup.js → createScriptItem()`, add an `isYourScript` check:
   ```js
   const isYourScript = scriptPath === 'user_scripts/your_script.js';
   ```
2. Add a `SET` button to the actions row (same condition)
3. Append a settings panel div with inputs after the main div
4. In `attachSettingsHandlers()`, query the input and save to `chrome.storage.local` on `change`/`keydown`
5. In `loadScriptList()`, read the stored value and pass it into `createScriptItem()`
6. In your `user_scripts/your_script.js`, read it with `chrome.storage.local.get([...])` on each trigger

---

## Persisting Python GUI Settings

Settings are stored in `settings.json` next to `app.py`.

- **Load**: `load_settings()` returns a dict (empty if file missing)
- **Save**: `save_settings(dict)` writes the full dict back
- **Pattern**: read in `App.__init__`, apply flags/state, save in the relevant toggle handler

To add a new setting:
```python
# Load
self._settings = load_settings()
some_value = self._settings.get('your_key', default_value)

# Save (inside the toggle/change handler)
self._settings['your_key'] = new_value
save_settings(self._settings)
```

---

## Data Sources

| Field    | Source                              | Accuracy         |
|----------|-------------------------------------|------------------|
| Title    | YouTube oEmbed API                  | Exact            |
| Views    | Return YouTube Dislike API (RYD)    | Accurate         |
| Likes    | RYD (crowdsourced + extrapolated)   | Estimated        |
| Dislikes | RYD (crowdsourced + extrapolated)   | Estimated        |
| Rating   | Derived: `1 + (likes/(likes+dislikes)) * 4` | Same as likes/dislikes |

YouTube removed public dislike counts in Dec 2021. There is no official API for them.

---

## Theme

All PyQt6 GUIs use the Cyberpunk palette defined in `C:\@delta\ms1\md\THEME_GUIDE.md`.  
Copy `GLOBAL_QSS` and the color constants from `app.py` to bootstrap a new tool.
