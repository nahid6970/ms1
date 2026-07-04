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

## Suggested Approach for Next Attempt

The cleanest solution is probably a **global click-anchor mechanism**:

1. Add a **single `mousedown` listener on `.table-container`** (or `document`) that records `e.clientY` and the element's `scrollTop` at click time — before anything changes
2. After the focus transition is fully complete (perhaps `setTimeout(..., 0)` which runs after all pending rAFs), compute the drift between current `scrollTop` and the scroll needed to keep the clicked point at `e.clientY`
3. Apply the correction as the **last thing** — after `handlePreviewMouseDown`'s rAF and after `adjustCellHeightForMarkdown`

Alternatively, refactor `handlePreviewMouseDown` to accept a target scroll position and apply it as the final step instead of restoring the original scroll.

---

## Files to Modify

- `static/script.js`:
  - `handlePreviewMouseDown` (~line 1726) — remove/replace scroll restoration
  - `adjustCellHeightForMarkdown` (~line 14391) — make scroll restoration optional
  - `applyMarkdownFormatting` focus/blur handlers (~line 2660+) — add scroll correction
