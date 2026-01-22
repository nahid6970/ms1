# Click-to-Edit Cursor Positioning

## Overview

When users click on a markdown preview cell to enter edit mode, the cursor should appear at the exact position where they clicked. This is challenging because the preview shows rendered text (without markdown syntax), but the edit mode shows raw text (with syntax like `**bold**`, `@@italic@@`, etc.).

## Current Status: RESOLVED

The feature is now fully implemented and working correctly.

## The Solution: Range-Based Visibility Mapping

We implemented a robust `calculateVisibleToRawMap(rawInput)` function that maps every visible character offset to its corresponding raw input offset.

### Logic
1.  **Identify Hidden Ranges:**
    - The function iterates through all supported markdown regex patterns (e.g., `##(.+?)##`, `**(.+?)**`).
    - For each match, it calculates which parts of the string are "syntax" (hidden) and which are "content" (visible).
    - Example: `##Title##` -> Matches `##Title##` (indices 0-9). Group 1 is `Title` (indices 2-7). Hidden ranges are `[0, 2)` and `[7, 9)`.

2.  **Merge Ranges:**
    - Overlapping or adjacent hidden ranges are merged to handle complex cases (though rare in simple markdown).
    - Example: `[0, 2)` and `[2, 4)` become `[0, 4)`.

3.  **Build Map:**
    - We iterate through the raw string from 0 to length.
    - If an index is NOT in a hidden range, it counts as a visible character.
    - We map `visibleIndex -> rawIndex`.

### Why It Works
Unlike the previous approach (using `stripMarkdown` on partial strings), this approach:
- Operates on the *full* string, ensuring regexes match correctly.
- Specifically identifies *what* is hidden, rather than trying to reverse-engineer it from output.
- Handles all standard and custom syntax patterns defined in the application.

## Example

**Input:** `##Title##`
**Hidden Ranges:** `[0, 2)` (`##`), `[7, 9)` (`##`)
**Mapping Loop:**
- Raw 0: Hidden
- Raw 1: Hidden
- Raw 2: Visible (Visible 0 -> Raw 2) ('T')
- Raw 3: Visible (Visible 1 -> Raw 3) ('i')
- ...
- Raw 6: Visible (Visible 4 -> Raw 6) ('e')
- Raw 7: Hidden
- Raw 8: Hidden
- Raw 9: End

**Result:** Clicking before 'T' (visible 0) places cursor at raw 2. Clicking after 'e' (visible 5) places cursor at raw 9 (end).

## Files Modified
- `static/script.js`: Added `calculateVisibleToRawMap` and updated `handlePreviewMouseDown`.