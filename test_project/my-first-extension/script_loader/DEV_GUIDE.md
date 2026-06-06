# Script Manager Extension — Developer Guide

## What This Extension Does

A Chrome extension that lets you toggle custom JavaScript scripts on/off per-page.
Scripts live in `user_scripts/` and auto-appear in the popup. Some scripts can talk to
local Python GUI apps via Chrome's Native Messaging API.

---

## Project Structure

```
script_loader/
├── manifest.json           # Extension config, permissions, background worker
├── background.js           # Service worker: tab injection, native messaging, message routing
├── popup.html              # Popup UI styles
├── popup.js                # Popup logic: script list, toggles, settings panels
├── page_bridge.js          # Content script injected on every page (for page↔extension comms)
├── user_scripts/           # Drop .js files here — they auto-appear in the popup
│   ├── yt_analyzer.js      # Example: F9 hotkey → launches Python GUI
│   └── ...
└── assets/icons/
```

---

## Adding a Simple Script (Most Common Case)

1. Create `user_scripts/your_script_name.js`
2. Write your JS — it runs on every `http/https` page when enabled
3. Reload the extension — it appears in the popup automatically
4. Toggle ON/OFF from the popup

**Guard against double-injection** (script may re-inject on navigation):
```js
if (window.__yourScriptLoaded) return;
window.__yourScriptLoaded = true;
// your code here
```

---

## Adding a Script with a Hotkey

```js
if (window.__yourScriptLoaded) return;
window.__yourScriptLoaded = true;

document.addEventListener('keydown', (e) => {
  if (e.key !== 'F8') return; // change key as needed
  e.preventDefault();
  // do something
});
```

---

## Adding a Script That Launches a Python GUI

**Step 1 — Create the Python app** somewhere on disk.  
Accept CLI args via `argparse` so the extension can pass data:
```python
parser = argparse.ArgumentParser()
parser.add_argument('--url', default='')
args = parser.parse_args()
```

**Step 2 — Create `host.py`** next to your Python app (copy from `yt_like_dislike/host.py`).  
Change the path to point to your app:
```python
app_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'your_app.py')
```

**Step 3 — Create a native messaging manifest** `com.delta.your_tool.json`:
```json
{
  "name": "com.delta.your_tool",
  "description": "Your tool description",
  "path": "C:\\path\\to\\host.py",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://YOUR_EXTENSION_ID/"]
}
```

**Step 4 — Register it in Windows registry** (run once):
```python
import winreg, json
key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
      r'Software\Google\Chrome\NativeMessagingHosts\com.delta.your_tool')
winreg.SetValueEx(key, '', 0, winreg.REG_SZ, r'C:\path\to\com.delta.your_tool.json')
```
Or copy `install_host.py` from `yt_like_dislike/` and adapt it.

**Step 5 — Add a handler in `background.js`**:
```js
if (message?.type === 'LAUNCH_YOUR_TOOL') {
  chrome.runtime.sendNativeMessage(
    'com.delta.your_tool',
    { url: message.url },
    (response) => { const err = chrome.runtime.lastError; sendResponse({ ok: !err }); }
  );
  return true;
}
```

**Step 6 — Create `user_scripts/your_tool.js`**:
```js
if (window.__yourToolLoaded) return;
window.__yourToolLoaded = true;

document.addEventListener('keydown', (e) => {
  if (e.key !== 'F8') return;
  e.preventDefault();
  chrome.runtime.sendMessage({ type: 'LAUNCH_YOUR_TOOL', url: location.href });
});
```

**Step 7** — Reload extension, toggle ON in popup, press your hotkey.

---

## Adding Per-Script Settings in the Popup

Pattern: show a collapsible panel below the script row with inputs.

**In `popup.js → createScriptItem()`**, add:
```js
const isYourScript = scriptPath === 'user_scripts/your_script.js';
```

Add a `SET` button to the actions row (same condition as other SET buttons).

Append a settings div inside `createScriptItem`:
```js
} else if (isYourScript) {
  const div = document.createElement('div');
  div.className = 'fallback-settings hidden';
  div.innerHTML = `
    <label class="settings-label">Your Setting</label>
    <input id="yourSettingInput" class="settings-input" type="text" value="${savedValue}">
  `;
  scriptItem.appendChild(div);
}
```

In `attachSettingsHandlers()`, query and save:
```js
const input = scriptItem.querySelector('#yourSettingInput');
if (input) {
  input.addEventListener('change', () => {
    chrome.storage.local.set({ yourSettingKey: input.value });
  });
}
```

In `loadScriptList()`, read from storage and pass into `createScriptItem`:
```js
chrome.storage.local.get([..., 'yourSettingKey'], (result) => {
  const yourValue = result.yourSettingKey || 'default';
  // pass to createScriptItem(...)
});
```

In your user script, read it:
```js
chrome.storage.local.get(['yourSettingKey'], (result) => {
  const val = result.yourSettingKey || 'default';
});
```

---

## Key Extension Concepts

| Concept | Where |
|---|---|
| Script toggle state | `chrome.storage.local → enabledScripts[scriptPath]` |
| Script injection on page load | `background.js → chrome.tabs.onUpdated` |
| Popup renders scripts | `popup.js → loadScriptList()` |
| Page ↔ Extension messaging | `page_bridge.js` + `chrome.runtime.sendMessage` |
| Extension ↔ Python app | Native Messaging via `background.js` |
| Permissions needed | Add to `manifest.json → permissions` |

---

## Adding a New Permission

Edit `manifest.json`:
```json
"permissions": ["storage", "scripting", "downloads", "tabs", "nativeMessaging", "YOUR_NEW_PERMISSION"]
```
Reload the extension after any `manifest.json` change.

---

## Theming

Popup uses VS Code dark theme (JetBrains Mono, `#1e1e1e` bg).  
Python GUIs use the Cyberpunk palette — see `C:\@delta\ms1\md\THEME_GUIDE.md`.
