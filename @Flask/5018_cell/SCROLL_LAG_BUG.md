# Bug Report: Intermittent Scrollbar Drag Lag

## Status: Investigating (Partial Fix Applied)

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

### Remaining Hypotheses
1. **Layout Thrashing/Paint Heavy Elements:** Visual mode renders many small DOM nodes and SVGs. High-frequency scrolling might be triggering expensive repaints or layout recalculations (Reflows), especially if `position: sticky` headers are interacting with complex content.
2. **Main Thread vs. Compositor:** Mouse wheel scrolling is often handled by the browser's compositor thread (smooth), whereas scrollbar dragging depends on the main thread processing `scroll` events and updating the UI.
3. **SVG/KaTeX Complexity:** If many KaTeX formulas or Word Connectors are visible, the sheer number of elements might be hitting the browser's limit for smooth real-time repositioning during a drag.

### Files to Investigate
- `static/script.js`: Search for `tableContainer.addEventListener('scroll', ...)` (around line 105).
- `static/style.css`: Check for expensive properties like `backdrop-filter`, `box-shadow`, or `position: sticky` on headers.
