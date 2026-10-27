# Project Handoff

## 1. Project DNA (Permanent)
Manifest V3 Chrome extension written in vanilla JavaScript and HTML. The popup manages enabled user scripts; a service worker injects them from `user_scripts/` to make custom browser automation easy to toggle. Some scripts use Chrome's Native Messaging API to launch local Python tools.

## 2. Latest Implementation
- `user_scripts/reveal_in_explorer.js` — Press **Ctrl+Shift+F** on a `file:///` page to open File Explorer with the file selected. Chrome launches `reveal_explorer/run_host.bat`, which starts `host.py` through Python. Optional `f1_relay.py` intercepts F1 at the OS level and sends Ctrl+Shift+F when Chrome is focused.

## 3. Critical Context
- Chrome intercepts F1 at the browser level — neither content scripts nor the `commands` API can override it. F1 only works via the OS-level `f1_relay.py` relay script.
- The `commands` API in `manifest.json` rejects reserved keys (F1) but accepts combos like `Ctrl+Shift+F`.
- Script injection now includes `file://` pages (added to `content_scripts.matches` and `background.js` injection condition). "Allow access to file URLs" must be enabled in chrome://extensions → Details.
- `page_bridge.js` content script runs on `file://` pages too, enabling page↔extension messaging on local files.

## 4. Setup / Troubleshooting
- Load this project folder as an unpacked extension, then run `python run.py`. It finds the extension ID for this folder from Chrome profile records and registers the native host for it.
- Reload the extension, enable "Allow access to file URLs", and check the shortcut assignment at `chrome://extensions/shortcuts`.
- Test Ctrl+Shift+F on a `file:///` URL. If the folder moves, load the new location and rerun `python run.py` because Chrome can assign a different ID to unpacked extensions at different paths.
