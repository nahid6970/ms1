# 1. Project DNA (Permanent)
Chrome Manifest V3 extension built with vanilla JavaScript, HTML, and CSS. It captures YouTube subtitles, manages reusable AI Studio prompts, and sends subtitles plus a selected prompt to Google AI Studio.

# 2. Latest Implementation
- `options.js`: Load and migrate prompts between legacy sync storage and local storage; save prompt data locally and viewer preference in sync storage; surface storage errors; safely render prompt text as text; restore Convex backups with prompts in local storage.
- `popup.js`: Load prompts from local storage and retain last selected prompt in sync storage.

# 3. Critical Context
Long prompt bodies can exceed Chrome sync storage quotas. Prompts now live under `chrome.storage.local` key `prompts`; small preferences remain in `chrome.storage.sync`. Older prompts are migrated from sync on options page load. Prompt preview must use `textContent` because Markdown can contain HTML-like characters.

# 4. Pending Task
Manually reload the extension and verify saving/reopening a long multiline prompt, popup dropdown loading, and Convex backup/restore.
