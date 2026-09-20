# Project DNA (Permanent)

Flask-based web app with a vanilla JavaScript/CSS frontend (`static/script.js` is the core engine) and JSON-backed spreadsheet persistence. Its primary goal is a markdown-enabled spreadsheet with rich preview/editing and keyboard-driven text formatting.

# Latest Implementation

- `static/script.js` — Improved F3 outside-edit selection: visible selection movement now skips hidden Markdown syntax; Shift+Left/Right extends the correct rendered edge; unmodified arrows contract from the inside edge; typing, Backspace, Delete, Shift+Enter, and Tab edit the selected range directly; F3 edits pass the live input through `updateCell()` so previews refresh.

# Critical Context

- F3 outside-edit state is stored in the legacy `f10FormatterAnchor` object; do not rename it casually because the formatter and overlay paths depend on it.
- The underlying input/textarea remains the source of truth; `.markdown-preview` is regenerated from it.
- Selection has two coordinate systems: rendered visible offsets for highlighting and raw offsets for edits. Keep them separate because Markdown markers can distort raw-to-visible mapping.
- `md/RECENT.md` and problem documentation are maintained only when the user explicitly requests a commit.

# Pending Task

Manually verify F3 selection and replacement in the browser, especially words inside bold, highlight, link, or other Markdown spans, and correct any remaining raw/visible offset mismatch.
