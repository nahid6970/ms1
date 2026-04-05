# Bug Report: Intermittent Scrollbar Drag Lag

## Status: ✅ FIXED (2026-04-05)

### Symptom
Intermittent lag/stuttering occurs when **manually dragging the scrollbar** with the mouse.
- **Affected Mode:** Visual Mode (Standard/Clean WYSIWYG).
- **Unaffected:** Mouse wheel scrolling is smooth.
- **Unaffected:** Edit mode (when a cell is active/focused) is smooth.

### Technical Context
The application renders a large grid/table where cells contain complex markdown (KaTeX math, SVG word connectors, custom color syntax). Scrollbar dragging fires `scroll` events at a much higher frequency than mouse wheel scrolling, putting more pressure on the browser's main thread.

### What has been tried
1. **Debounced Scroll Listener:** The `tableContainer` scroll event listener (which saves scroll positions to `localStorage`) was debounced to 500ms. This prevents heavy `JSON.stringify` and `localStorage.setItem` calls from firing hundreds of times per second during a drag.
2. **Removed Debug Logging:** Removed `console.log` from the scroll event path to reduce overhead.
3. **Audit of Listeners:** Verified that no other heavy `scroll` or `wheel` listeners are active on the `window` or `document`.

### Fix Applied (2026-04-05)

**`static/style.css` — `.table-container`**
- Added `will-change: scroll-position` — promotes the scroll container to its own GPU layer ahead of time, preventing main-thread repaints during drag.
- Added `contain: strict` — isolates layout/paint of the container from the rest of the page, eliminating cross-page reflow on every scroll event.

**`static/style.css` — `th` (sticky header)**
- Added `transform: translateZ(0)` and `will-change: transform` — promotes each sticky header to its own compositor layer. The `position: sticky` + scroll interaction was the primary source of expensive repaints during scrollbar drag.

**`static/script.js` — scroll event listener**
- Added `{ passive: true }` to `tableContainer.addEventListener('scroll', ...)` — signals to the browser that `preventDefault()` will never be called, allowing scroll events to be processed on the compositor thread instead of blocking the main thread.

### Root Cause Summary
The lag was caused by three compounding issues:
1. `position: sticky` on `th` elements forced the browser to recalculate layout on every scroll event (main thread).
2. No GPU layer promotion meant sticky headers were repainted from scratch each frame.
3. The scroll listener lacked `passive: true`, forcing the browser to wait for the main thread before compositing each scroll frame.
