# 1. Project DNA (Permanent)
Chrome Manifest V3 extension built with vanilla JavaScript, an MV3 background service worker, content script, and popup. Its goal is to capture Google Meet session names/times/durations and keep timesheet records locally with Convex sync.

# 2. Latest Implementation
- `manifest.json`: permissions, Meet content script, popup, and Convex host access.
- `content.js`: watches Meet UI; stabilizes start detection for 4 seconds and end detection for 12 seconds to avoid UI flicker splitting sessions.
- `background.js`: tracks per-tab active calls, finalizes on call end/tab close, records timestamps/duration, syncs and restores through shared Convex API, and merges overlapping/near-adjacent duplicate intervals for identical Meet URLs.
- `popup.html`, `popup.css`, `popup.js`: history/live status, live row with seconds-updating timer, completed durations with seconds, Sync/Restore/Clear controls; Clear confirms then empties local and Convex records.
- `README.md`: unpacked install and sync instructions.

# 3. Critical Context
Convex uses the shared `functions:save`/`functions:get` endpoints and extension key `google_meet_timesheet`; configured URL is `https://joyous-stingray-672.convex.cloud`. The shared API stores one dataset per extension, so syncing replaces this extension's entire `{ meetings: [...] }` dataset. Meet title and call-state detection rely on DOM labels/selectors and fallback to the Meet URL/code. No dependencies or build step.

# 4. Pending Task
Validate capture against current Google Meet DOM in Chrome, especially call-state transitions and meeting-name extraction; refine selectors if needed.
