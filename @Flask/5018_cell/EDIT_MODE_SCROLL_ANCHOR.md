# Feature: Edit Mode Scroll Anchor (No Jump on Click-to-Edit)

## Problem Description

In **Visual Mode** (markdown preview enabled), cells can contain rich content — rendered tables, lists, headings, etc. The cell height in preview mode is determined by the rendered HTML.

When the user **clicks a cell to enter edit mode**, the following happens:
1. The preview div switches from `parseMarkdown()` output (full rendered HTML with tables) to `highlightSyntax()` output (raw syntax text with visible markers like `**`, `|col|col|`)
2. Tables in particular collapse from multi-row rendered HTML into flat `|pipe|text|` lines — dramatically shrinking the cell height
3. This height change causes a **layout reflow** — all cells below shift upward
4. The content the user clicked on is now at a completely different screen position
5. The user loses their place

This affects **two scenarios**:

**Scenario A — clicking content inside a table (within the rendered table rows/cells):**
The user clicks on text inside a rendered table cell. Edit mode activates, the table collapses to raw `|pipe|` syntax, and the clicked table row is now far from the cursor.

**Scenario B — clicking content below a table in the same cell:**
The user clicks on normal text that appears after a table in the same cell. The table above it collapses, shrinking the cell, and the text the user clicked jumps upward — away from the cursor.

The same issue happens in reverse when **clicking out** (blur): the cell re-renders to full markdown, tables expand back out, and content shifts downward.

**Result:** Whatever line/word the user clicked on is no longer near the mouse cursor after edit mode activates. The user completely loses their place in the content.

---

## Desired Behavior

- When the user clicks **anywhere** in a cell to enter edit mode — whether clicking inside a rendered table row, or clicking text below a table — that **exact clicked content should remain at (or near) the mouse cursor's screen position** after the edit mode transition
- When the user clicks out of edit mode, the view should **not jump** — content should stay visually stable
- This applies to the entire cell content: tables, text before tables, text after tables, lists, etc.
- This is purely a scroll compensation — no content or layout changes, just adjust `tableContainer.scrollTop` to compensate for the reflow

---

## Architecture Context

### Key files
- `static/script.js` — all logic (~14k+ lines)
- The main function: `applyMarkdownFormatting(rowIndex, colIndex, value, inputElement)`
  - Located around line 2374
  - This is where the `preview` div is created and all its event listeners are attached

### Edit mode flow
1. User clicks preview div → `handlePreviewMouseDown` fires (assigned via `preview.onmousedown`, around line 2831)
2. `handlePreviewMouseDown` calls `preview.focus({ preventScroll: true })`
3. `focus` event fires on preview → switches innerHTML to `highlightSyntax()` output → calls `adjustCellHeightForMarkdown(cell)`
4. User clicks away → `blur` fires → switches innerHTML to `parseMarkdown()` output → calls `adjustCellHeightForMarkdown(cell)`

### Critical function: `adjustCellHeightForMarkdown(cell)`
- Located around line 14391 in `script.js`
- **Saves `tableContainer.scrollTop` at the start, restores it at the end** (synchronously)
- This is important — it fights any scroll corrections made before/during it

### Critical function: `handlePreviewMouseDown(e)`
- Located around line 1726
- Saves `scrollTop` before calling `preview.focus()`
- In a `requestAnimationFrame` after focus, **restores `scrollTop` to the saved value**
- This means ANY scroll correction made in the `focus` event handler gets overwritten by this rAF

### The scroll container
- `document.querySelector('.table-container')` — this is the scrollable div wrapping the table

---

## What Was Tried (and Why It Failed)

### Attempt 1: `getBoundingClientRect` anchor before/after focus handler
- Captured `cell.getBoundingClientRect().top` before `preview.innerHTML = highlightedHtml`
- After a `requestAnimationFrame`, measured the new top and applied drift correction to `scrollTop`
- **Failed because:** `handlePreviewMouseDown` runs its own rAF that restores `scrollTop` to the pre-click value, overwriting the correction

### Attempt 2: Click Y coordinate anchor via mousedown
- Added a `mousedown` listener to capture `e.clientY` and `e.clientY - cell.getBoundingClientRect().top` (offset within cell)
- On `focus`, after reflow: calculated `newCellTop + offsetInCell` to find where the clicked point moved, applied drift
- Used double `requestAnimationFrame` to wait for layout to settle
- **Failed because:** `preview.onmousedown = handlePreviewMouseDown` (around line 2831) **overwrites** the `onmousedown` property, so the capture listener set via `addEventListener` in capture phase may have been overridden. Additionally, `handlePreviewMouseDown`'s rAF still restored scroll.

### Attempt 3: Full fix — `preserveScroll` flag + remove `handlePreviewMouseDown` scroll restore
- Added `preserveScroll = true` parameter to `adjustCellHeightForMarkdown` 
- Called it with `false` from focus/blur so it skips the scroll restore
- Modified `handlePreviewMouseDown` to only restore `scrollLeft`, not `scrollTop`
- **Result:** Still didn't work visually — possibly due to other scroll interactions or timing issues not yet identified

---

## Key Constraints for Any Solution

1. **`handlePreviewMouseDown`'s rAF must NOT restore `scrollTop`** — it will overwrite any correction
2. **`adjustCellHeightForMarkdown` must NOT restore `scrollTop`** when called from the focus/blur handler — it also overwrites corrections
3. The scroll correction must happen **after all layout/height changes are finalized**
4. The `preview.onmousedown` assignment (line ~2831) uses property assignment, not `addEventListener` — any listener added with `addEventListener` on mousedown in capture phase will still fire, but be aware of the order
5. The click Y position (`e.clientY`) is the ground truth for "where the user was looking"

## F8 Key — Relevant Technique

F8 already uses `document.caretRangeFromPoint(lastMouseX, lastMouseY)` to identify the exact DOM text node and character offset under the mouse cursor. The app also tracks `lastMouseX` / `lastMouseY` globally via a `mousemove` listener.

This is directly useful for the scroll anchor feature:

**Before the edit mode transition (in `handlePreviewMouseDown` or the `focus` handler):**
```js
const range = document.caretRangeFromPoint(e.clientX, e.clientY);
const targetNode = range?.startContainer; // the exact text node clicked
const targetElement = targetNode?.parentElement; // its parent element
const targetRectBefore = targetElement?.getBoundingClientRect();
const targetTopBefore = targetRectBefore?.top; // screen Y of clicked element
```

**After the reflow (in a rAF or setTimeout after innerHTML swap + height adjustment):**
```js
const targetRectAfter = targetElement?.getBoundingClientRect();
const drift = targetRectAfter.top - targetTopBefore;
tableContainer.scrollTop += drift;
```

**Why this is better than anchoring the cell top:**
- Instead of anchoring the whole cell's top edge, we anchor the **specific DOM element** (the table row, the paragraph, the span) that the user actually clicked on
- If the user clicks on text in row 5 of a rendered table, `targetElement` will be the `<td>` of that row — so we track exactly that row's position, not the cell top
- After the table collapses to `|pipe|` syntax, the `targetElement` no longer exists in the DOM — but we captured its pre-reflow screen position, and we know the cell's new top, so we can still compute the correct scroll offset

**The key challenge:** After `preview.innerHTML` is replaced, the DOM nodes captured by `caretRangeFromPoint` are detached — `getBoundingClientRect()` returns zeros. So we must capture `targetRectBefore.top` **before** the innerHTML swap, and then use `cell.getBoundingClientRect().top` after the swap to compute the relative offset.

**Refined approach:**
```js
// In mousedown (before focus):
const range = document.caretRangeFromPoint(e.clientX, e.clientY);
const clickedNode = range?.startContainer?.parentElement;
const cellRect = cell.getBoundingClientRect();
// How far from the cell top was the clicked element?
const clickedNodeOffsetInCell = clickedNode 
    ? clickedNode.getBoundingClientRect().top - cellRect.top 
    : e.clientY - cellRect.top;
const clickScreenY = e.clientY;

// After reflow (double-rAF, after adjustCellHeightForMarkdown with preserveScroll=false):
requestAnimationFrame(() => requestAnimationFrame(() => {
    // The clicked node is now gone (innerHTML replaced), but we know its offset within the cell
    // In the new raw view, that offset maps to a proportional position
    const newCellRect = cell.getBoundingClientRect();
    const newPointScreenY = newCellRect.top + clickedNodeOffsetInCell;
    const drift = newPointScreenY - clickScreenY;
    tableContainer.scrollTop += drift;
}));
```

This still needs `handlePreviewMouseDown` to NOT restore scrollTop, and `adjustCellHeightForMarkdown` to NOT restore scrollTop when called from focus/blur.

---

## Files to Modify

- `static/script.js`:
  - `handlePreviewMouseDown` (~line 1726) — remove/replace scroll restoration
  - `adjustCellHeightForMarkdown` (~line 14391) — make scroll restoration optional
  - `applyMarkdownFormatting` focus/blur handlers (~line 2660+) — add scroll correction
