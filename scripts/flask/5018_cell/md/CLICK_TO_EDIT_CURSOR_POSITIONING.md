# Click-to-Edit Cursor Positioning

## Overview

When users click on a markdown preview cell to enter edit mode, the cursor should appear at the exact position where they clicked. This is challenging because the preview shows rendered text (without markdown syntax), but the edit mode shows raw text (with syntax like `**bold**`, `@@italic@@`, etc.).

## Current Status: UNRESOLVED

The feature is partially implemented but not working correctly. The cursor positioning is off when clicking on text that has markdown syntax at the beginning.

## The Challenge

**Example:**
- Raw input: `##This Text Is Big Text## This Is Normal Text`
- Rendered preview: `This Text Is Big Text This Is Normal Text` (heading formatting applied, `##` syntax hidden)
- User clicks after "This Text Is Big Te" (19 visible characters)
- Expected cursor position: Raw offset 21 (2 for opening `##` + 19 visible chars)
- Actual cursor position: Raw offset 19 (incorrect, ignoring the `##` markers)

The system must map the visible offset (19) to the correct raw offset (21).

## Problem Analysis

### What Works
- `stripMarkdown()` function correctly removes all markdown syntax
- Test: `stripMarkdown("##This Text Is Big Text##")` returns `"This Text Is Big Text"` (25→21 characters) ✓
- Click detection and visible offset calculation works correctly ✓

### What Doesn't Work
- The mapping from visible offset to raw offset produces 1:1 correspondence
- Expected mapping: `{visible 0: 2, visible 1: 3, visible 2: 4, ..., visible 19: 21}`
- Actual mapping: `{visible 0: 0, visible 1: 1, visible 2: 2, ..., visible 19: 19}` ✗

### Root Cause
The character-by-character mapping loop finds the FIRST raw position where `stripMarkdown(substring).length === visiblePos`, which is always equal to `visiblePos` itself. This is because:
- For visible position 0: Raw position 0 gives `stripMarkdown("") = ""` (length 0) ✓ Match found, stops
- For visible position 1: Raw position 1 gives `stripMarkdown("#") = ""` (length 0) ✗ No match, continues...
  - But wait, this should work! The issue might be that `stripMarkdown("#")` is NOT returning `""` as expected

## Attempted Solutions

### 1. Binary Search Approach (Failed)
```javascript
// Find raw position where stripMarkdown(substring) gives target visible length
while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const strippedSubstr = stripMarkdown(rawInput.substring(0, mid));
    if (strippedSubstr.length === visibleOffset) {
        rawOffset = mid;
        left = mid + 1; // Keep searching right
    } else if (strippedSubstr.length < visibleOffset) {
        left = mid + 1;
    } else {
        right = mid - 1;
    }
}
```
**Problem:** Found a position with correct visible length, but it was inside the visible content, not after markdown syntax.

### 2. Fine-Tuning Loop (Failed)
```javascript
// Move forward to skip markdown syntax
while (rawOffset < rawInput.length) {
    const currentStripped = stripMarkdown(rawInput.substring(0, rawOffset));
    const nextStripped = stripMarkdown(rawInput.substring(0, rawOffset + 1));
    if (currentStripped.length === visibleOffset && nextStripped.length === visibleOffset) {
        rawOffset++; // Next char is syntax, keep moving
    } else {
        break;
    }
}
```
**Problem:** Logic couldn't distinguish between being inside visible content vs. being in markdown syntax.

### 3. Character-by-Character Mapping (Failed)
```javascript
for (let visiblePos = 0; visiblePos <= strippedInput.length; visiblePos++) {
    for (let rawPos = 0; rawPos <= rawInput.length; rawPos++) {
        const strippedSubstr = stripMarkdown(rawInput.substring(0, rawPos));
        if (strippedSubstr.length === visiblePos) {
            visibleToRawMap[visiblePos] = rawPos;
            break; // Found first match
        }
    }
}
```
**Problem:** Produces 1:1 mapping. The issue is that it finds the FIRST raw position with matching visible length, which is always the same as the visible position.

## Potential Solutions to Try

### Option A: Reverse Mapping
Instead of mapping visible→raw, map raw→visible, then invert:
```javascript
const rawToVisibleMap = [];
for (let rawPos = 0; rawPos <= rawInput.length; rawPos++) {
    const stripped = stripMarkdown(rawInput.substring(0, rawPos));
    rawToVisibleMap[rawPos] = stripped.length;
}
// Then invert: for each visible position, find the LAST raw position with that visible length
```

### Option B: Incremental Tracking
Walk through raw input once, track when visible length increases:
```javascript
let visibleCount = 0;
let prevStripped = "";
for (let rawPos = 0; rawPos <= rawInput.length; rawPos++) {
    const stripped = stripMarkdown(rawInput.substring(0, rawPos));
    if (stripped.length > prevStripped.length) {
        // Visible length increased, map all new visible positions to this raw position
        while (visibleCount < stripped.length) {
            visibleToRawMap[visibleCount] = rawPos;
            visibleCount++;
        }
    }
    prevStripped = stripped;
}
```

### Option C: Parse Markdown Patterns Directly
Instead of using `stripMarkdown`, parse markdown patterns and calculate offset adjustments:
```javascript
// Find all markdown syntax patterns before the visible offset
const patterns = [/\*\*(.+?)\*\*/g, /##(.+?)##/g, /@@(.+?)@@/g, ...];
let syntaxCharsBeforeOffset = 0;
// For each pattern match before visible offset, add syntax length to offset
```

### Option D: Debug stripMarkdown Behavior
The 1:1 mapping suggests `stripMarkdown` might not be working as expected on partial strings. Test:
```javascript
console.log(stripMarkdown("#"));      // Should be ""
console.log(stripMarkdown("##"));     // Should be ""
console.log(stripMarkdown("##T"));    // Should be "T"
console.log(stripMarkdown("##Te"));   // Should be "Te"
```

## Markdown Patterns to Handle

The `stripMarkdown` function handles these patterns:
- `**bold**` → bold
- `@@italic@@` → italic
- `__underline__` → underline
- `~~strikethrough~~` → strikethrough
- `==highlight==` → highlight
- `!!red!!` → red background
- `??blue??` → blue background
- `` `code` `` → code
- `^sup^` → superscript
- `~sub~` → subscript
- `##heading##` → heading
- `..small..` → small text
- `[[correct]]` → correct answer marker
- `{fg:#fff;bg:#000}text{/}` → colored text
- `{link:url}text{/}` → link
- `url[text]` → link

## Related Functions

- `handlePreviewMouseDown()` - Main click handler (~line 1402)
- `extractRawTextBeforeCaret()` - Gets visible text before click position
- `stripMarkdown()` - Removes all markdown syntax (~line 7040)
- `setCaretPosition()` - Sets cursor in contentEditable element
- `highlightSyntax()` - Renders markdown with visible syntax in edit mode

## Files Involved

- `static/script.js` - Main implementation
- `md/PROBLEMS_AND_FIXES.md` - Issue tracking
- `md/CLICK_TO_EDIT_CURSOR_POSITIONING.md` - This file

