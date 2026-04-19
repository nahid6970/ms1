# Quick Sidebar Pro

A Chrome extension (MV3) for a fast, customizable link sidebar with Convex cloud backup.

## Features

- Add, edit, delete, and reorder links via drag-and-drop
- Per-link color, solid fill, and new-line options
- Cyberpunk-styled edit modal (dark + green neon theme)
- Right-click context menu on any page to add links
- Settings panel: items per row, icon size, border radius, opacity

## Convex Backup

- **Save** — manually push all local storage to Convex
- **Restore** — clears local storage and replaces it fully with server data (no stale cache merge)
- Auto-backup on storage change is **disabled** — sync is manual only

## Performance

Popup uses a two-layer cache:

1. `chrome.storage.session` — in-memory, renders instantly on open
2. `chrome.storage.local` — disk, loaded in background to refresh session cache

This keeps the sidebar fast even under heavy network/disk load (e.g. active downloads).

## Files

| File | Purpose |
|------|---------|
| `popup.html` | Popup UI shell |
| `popup.js` | Popup logic, render, Convex sync |
| `popup.css` | Popup styles |
| `content.js` | Injected modal for add/edit/settings |
| `content.css` | Modal styles (cyberpunk theme) |
| `background.js` | Convex HTTP client, context menu, favicon logic |
| `manifest.json` | MV3 manifest |

## Permissions

- `storage` — local + session cache
- `sessionStorage` — fast in-memory cache
- `contextMenus` — right-click "Add to Quick Sidebar"

## Setup

1. Go to `chrome://extensions` → Enable Developer Mode
2. Load unpacked → select this `SideBar` folder
3. Set your Convex URL in `background.js` (`CONVEX_URL`)
4. Run `npx convex dev` in your Convex project
