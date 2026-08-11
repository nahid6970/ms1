# Scroll Anchor Issue — Edit Mode Enter/Exit

## Status: UNRESOLVED (as of 2026-07-04)

---

## The Problem

In **Visual Mode** (markdown preview enabled), the app uses a `div.markdown-preview[contenteditable=true]` as both the display surface and the editing surface.

**Two scenarios both fail:**

### Scenario A — Entering Edit Mode (click to edit)
1. User is scrolled to a position and clicks on some text in a cell to edit it
2. `handlePreviewMouseDown` fires → calls `preview.focus({ preventScroll: true })`
3. The `focus` event fires → `preview.innerHTML` switches from `parseMarkdown()` (rendered HTML) to `highlightSyntax()` (raw syntax with visible markers)
4. This causes a **layout reflow**: tables collapse from rendered HTML rows to `|pipe|text|` lines, images collapse from rendered `<img>` to `![alt](url)` text, the cell shrinks dramatically
5. The user's viewport jumps — the content they clicked is no longer near the cursor

### Scenario B — Exiting Edit Mode (click out / blur)
1. User clicks outside the cell (or presses Escape)
2. `blur` fires → `preview.innerHTML` switches back from `highlightSyntax()` to `parseMarkdown()`
3. Tables expand back to rendered HTML rows, images expand back to `<img>` tags, the cell grows
4. The user's viewport jumps — content shifts from where it was during editing

---

## Architecture Context

### Key functions (all in `static/script.js`)

**`handlePreviewMouseDown(e)`** (~line 1726)
- Fires when user clicks on a preview div
- Uses `caretRangeFromPoint` to find click position
- Calls `preview.focus({ preventScroll: true })`
- In a `requestAnimationFrame`, calls `setCaretPosition(preview, rawOffset)` to place cursor
- **Currently:** saves `scrollLeft` only; applies caret-drift correction in nested rAF

**`adjustCellHeightForMarkdown(cell, preserveScroll = true)`** (~line 14432)
- Resizes cell, input, and preview to fit content
- Saves `tableContainer.scrollTop` at start
- Has a **second-pass `requestAnimationFrame`** that re-measures after fonts/images load (to catch underestimated `scrollHeight`)
- Restores `tableContainer.scrollTop` synchronously at end of first pass (before the second-pass rAF)
- **This is a key timing issue** — the second-pass rAF fires AFTER the synchronous scroll restore, potentially causing a second layout shift

**`applyMarkdownFormatting(rowIndex, colIndex, value, inputElement)`** (~line 2374)
- Creates the `preview` div and attaches all event listeners
- **focus handler**: switches to `highlightSyntax()`, calls `adjustCellHeightForMarkdown(cell)`
- **blur handler**: switches to `parseMarkdown()`, calls `adjustCellHeightForMarkdown(cell)`, then tries to correct scroll drift

**`getCaretClientPosition()`** (~line 14418)
- Helper that returns the caret's screen `{x, y}` using `Range.getClientRects()`
- Falls back to inserting a zero-width space span if range has no rects

**`findVisibleOffsetFromRaw(rawInput, rawOffset)`**
- Maps a raw character offset to a visible character offset using `calculateVisibleToRawMap`

**`getCaretCharacterOffset(element)`**
- Returns caret position as character offset in contentEditable
- **MUST be called before `innerHTML` is replaced** — after replacement, DOM nodes are destroyed and it returns 0

### The scroll container
- `document.querySelector('.table-container')` — the scrollable div wrapping the table

---

## What Causes the Jump

### On focus (enter edit mode):
1. `preview.innerHTML = highlightSyntax(rawValue)` — tables collapse, images become text
2. `adjustCellHeightForMarkdown(cell)` — synchronously resizes and **restores `scrollTop` to pre-call value**
3. `adjustCellHeightForMarkdown` queues a second-pass rAF (for images/fonts)
4. `handlePreviewMouseDown`'s outer rAF fires → `setCaretPosition()`
5. `handlePreviewMouseDown`'s inner rAF fires → measures caret Y, computes drift from `e.clientY`, applies `scrollTop` correction
6. `adjustCellHeightForMarkdown`'s second-pass rAF fires → may expand cell further → **no scroll correction applied here** → scroll jumps again

### On blur (exit edit mode):
1. `rawOffset = getCaretCharacterOffset(preview)` — captured synchronously ✓
2. `caretPosBefore = getCaretClientPosition()` — captured synchronously ✓
3. `preview.innerHTML = parseMarkdown(newRawValue)` — tables expand, images render
4. `adjustCellHeightForMarkdown(cell)` — synchronously resizes, restores scroll to pre-call value
5. `adjustCellHeightForMarkdown` queues second-pass rAF
6. Blur's triple-rAF fires → tries to correct by placing caret at `visOffset`, measuring new Y, computing drift
7. `adjustCellHeightForMarkdown`'s second-pass rAF fires → may expand cell further → **scroll jumps again**

**The core race condition:** The second-pass rAF inside `adjustCellHeightForMarkdown` fires at an unpredictable time relative to the correction rAFs in focus/blur handlers. When it expands the cell after the correction has already been applied, the scroll position becomes wrong again.

---

## Content That Causes The Jump

These elements cause large height differences between preview mode and edit mode:

1. **Markdown tables** (`|col|col|` syntax) — rendered as HTML grid, collapses to flat pipe-separated lines in edit mode. **Major height change.**

2. **Images** (`![alt](url)` syntax) — rendered as `<img>` with full dimensions, collapses to single line of text in edit mode. **Largest height change. Also loads asynchronously.**

3. **Headings** (`##heading##` or `**heading**`) — rendered with larger font and margins, collapses to inline text in edit mode.

4. **Bullet lists** (`- item`) — rendered with indentation and spacing, collapses to raw text.

5. **Custom color syntax** (various markers) — adds/removes inline spans with padding.

6. **Zoom level** (font size scale stored in `localStorage` as `fontSizeScale`) — affects all measurements. If zoom is not 100%, `scrollHeight` values will be proportionally different. May affect `getCaretClientPosition()` accuracy.

7. **Row wrap mode** — when enabled, cells can be taller. May affect measurement stability.

8. **KaTeX math** (`$$...$$`) — rendered as math symbols with MathJax/KaTeX sizing, may load async.

---

## Attempts Made (All Failed)

### Attempt 1: Simple `getBoundingClientRect` anchor (before/after)
- Captured `cell.top` before `innerHTML` swap, measured drift after in a rAF
- **Failed:** `handlePreviewMouseDown`'s rAF restored `scrollTop` to original value, overwriting correction

### Attempt 2: Click Y coordinate via mousedown capture
- Stored `e.clientY` and `e.clientY - cell.top` on `mousedown`, used in focus handler
- **Failed:** `preview.onmousedown = handlePreviewMouseDown` assignment ran after `addEventListener`, and `handlePreviewMouseDown`'s rAF still overwrote scroll

### Attempt 3: `preserveScroll=false` flag on `adjustCellHeightForMarkdown`
- Added parameter to skip scroll restore inside `adjustCellHeightForMarkdown`
- Called with `false` from focus/blur, applied own correction in rAF
- **Failed:** Without scroll restore, `scrollHeight` measurements inside `adjustCellHeightForMarkdown` were unreliable (layout not settled), causing cell to be undersized → content bleeding into adjacent rows

### Attempt 4: `_blurDriftCallback` on cell element
- Queued drift callback on `cell._blurDriftCallback`, executed inside second-pass rAF
- **Failed:** Still had timing issues with image loading and the callback firing before final height

### Attempt 5: AI Studio fix — capture `rawOffset` synchronously + double-rAF
- `rawOffset = getCaretCharacterOffset(preview)` captured before `innerHTML` replace
- `caretPosBefore = getCaretClientPosition()` captured before replace
- Double-rAF to let layout settle, then measure caret Y drift
- **Partially worked** but still failed for cells with images (image loads after rAF)
- Also broke focus path in some cases

### Attempt 6: Triple-rAF + image `onload` re-adjust
- Upgraded to triple-rAF (3 nested rAFs instead of 2)
- Added `img.addEventListener('load', () => adjustCellHeightForMarkdown(cell))` on preview creation
- **Failed:** Triple-rAF still fires before image `onload` in many cases. The `onload` then adjusts height again without correcting scroll.

---

## Current Code State (after last revert)

The code currently has:
- `getCaretClientPosition()` helper function
- `findVisibleOffsetFromRaw()` helper function  
- `adjustCellHeightForMarkdown(cell, preserveScroll = true)` with `preserveScroll` parameter
- Second-pass rAF inside `adjustCellHeightForMarkdown` for undersize correction
- `cell.style.height = 'auto'` (not fixed height) on td — fixes cell overlap bug ✓
- `handlePreviewMouseDown` using cell-top fallback anchor (no `savedScrollTop` restore)
- Blur handler capturing `rawOffset` and `caretPosBefore` synchronously before `innerHTML` replacement

---

## Suggested Approaches for Next Attempt

### Option A: ResizeObserver (most reliable)
Use a `ResizeObserver` on the cell to detect when the height has **fully settled** (no more changes), then apply the scroll correction exactly once:

```js
// On blur, after adjustCellHeightForMarkdown:
const cellTopBefore = cell.getBoundingClientRect().top;
let lastHeight = 0;
let debounceTimer = null;
const ro = new ResizeObserver(() => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        ro.disconnect();
        const drift = cell.getBoundingClientRect().top - cellTopBefore;
        if (Math.abs(drift) > 1) tableContainer.scrollTop += drift;
    }, 50); // wait 50ms of no height change
});
ro.observe(cell);
```

**Why this works:** `ResizeObserver` fires whenever the element's size changes, including after image loads. The debounce ensures we only apply correction once the cell has stopped growing. No rAF counting needed.

### Option B: Wait for all images to load
On blur, before applying scroll correction, wait for all images in the preview to finish loading:

```js
const images = Array.from(preview.querySelectorAll('img'));
const pendingImages = images.filter(img => !img.complete);
if (pendingImages.length === 0) {
    applyDriftCorrection();
} else {
    let loaded = 0;
    pendingImages.forEach(img => {
        img.addEventListener('load', () => {
            if (++loaded === pendingImages.length) applyDriftCorrection();
        });
        img.addEventListener('error', () => {
            if (++loaded === pendingImages.length) applyDriftCorrection();
        });
    });
    // Safety timeout in case some images never fire load
    setTimeout(applyDriftCorrection, 500);
}
```

### Option C: Override `adjustCellHeightForMarkdown` scroll restore
Instead of fighting `adjustCellHeightForMarkdown`'s scroll restore, pass it the DESIRED final `scrollTop` as a parameter, and have it set that instead of restoring the saved value:

```js
adjustCellHeightForMarkdown(cell, true, desiredScrollTop);
// Inside adjustCellHeightForMarkdown's second-pass rAF:
// tableContainer.scrollTop = desiredScrollTop (instead of savedScrollTop)
```

---

## Git History

All attempted fixes are preserved in git history. Run the following to inspect them:

```bash
# See all relevant commits
git log --oneline

# Key commits to inspect:
# 7e9c7bfd - 🔧 Fix extractRawText node checking logic (TR rows) + scroll anchor attempt by Google AI Studio
# 90eb8e7b - fix scroll anchor fallback - cell-top anchor in handlePreviewMouseDown
# 0f1d8220 - fix cell overflow/bleed - height:auto on td (this one WORKED - keep it)
# 56ebd607 - fix occasional cell undersize - second-pass rAF in adjustCellHeightForMarkdown
# 7b60419b - docs: RECENT.md and PROBLEMS_AND_FIXES.md updates

# See full diff of what Google AI Studio changed (the most complete attempt):
git show 7e9c7bfd

# See diff between current state and before any scroll anchor attempts:
git diff 631771a9 HEAD -- static/script.js

# See all changes to script.js across recent commits:
git log --oneline -- static/script.js
```

**Important:** Commit `0f1d8220` (height:auto on td) fixed the cell overlap/bleed bug and should be kept regardless of what approach is used for scroll anchoring.

---

## Files to Modify

- `static/script.js`:
  - `handlePreviewMouseDown` (~line 1726)
  - `adjustCellHeightForMarkdown` (~line 14432)
  - `applyMarkdownFormatting` focus/blur handlers (~line 2660+)
  - Potentially add `ResizeObserver` helper
