# 1. Project DNA (Permanent)

Chrome extension using vanilla JavaScript, HTML, and CSS with popup/background/content-script architecture. Its primary goal is marking images, videos, and visual page elements with persistent review statuses.

# 2. Latest Implementation

- `content.js`: Expanded the toggle cycle to 5 states (off → green check → red cross → YouTube icon → waiting → off), with corresponding icons, colors, and persistence.
- `README.md`: Documented the behavior.
- `manifest.json`: Updated the description.

# 3. Critical Context

`itemStatuses` is authoritative and maps content IDs to `check` or `cross`; missing IDs mean off. Legacy `seenItems` is read only during startup migration so existing checks become green checks. Normal toggles write only `itemStatuses` to avoid storage-change races. `seenItems` remains an in-memory compatibility cache.

# 4. Pending Task

Test the extension in Chrome on representative image/video pages and verify repeated clicks consistently cycle through all three states.
