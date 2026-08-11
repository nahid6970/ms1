# F10 Multi-Match Selection Fix

This document details the resolution of mapping and positioning issues encountered when using the **F10** shortcut on cells with multiple occurrences of the same word.

## 🚩 The Problem
When a cell contained multiple instances of a word (e.g., the word "কত" appearing 5 times), the F10 multi-match system exhibited the following bugs:
1.  **Index Mismatch:** Clicking a badge labeled `v3` would sometimes apply formatting to the `v2` or `v4` instance in the raw source.
2.  **Ghost Matches:** The system would occasionally count words that were hidden inside markdown syntax (e.g., a word inside a `{link:...}` tag), causing the version numbers to skip.
3.  **UI Obstruction:** The `vN` badges were rendered above the text, sometimes covering the word being edited.
4.  **Inconsistent Boundaries:** Words adjacent to markers like `¿¿` or `**` were sometimes detected as one unit in raw mode but separate units in preview mode.

## 🛠️ Root Causes

### 1. Loop Index Scoping
In the original loop creating the badges, the `index` variable was shared across all click listeners. This meant the last index in the loop often "leaked" into earlier badges, leading to the wrong version being selected upon clicking.

### 2. Differing "Word" Definitions
The logic scanning the **Raw Text** (source) and the **Rendered Preview** (HTML) used different regex rules for boundaries. 
*   **Raw View:** Included markdown markers as part of the search string.
*   **Preview View:** Only saw the final text.
This caused a count discrepancy (e.g., 5 matches found in source vs. 4 visible to the user).

### 3. Visibility Shadowing
The scanner previously counted every occurrence of a string in the source code, even if that string was part of a hidden URL or a color hex code, leading to "invisible" versions that shifted the count for the user.

## ✅ The Solution

### 1. Unified Boundary Logic
Created a strict `isBoundaryChar` function used by both the Raw and Rendered scanners.
*   **Definition:** A character is a boundary if it is NOT a letter or number (supports English `a-zA-Z0-9` and Bengali `\u0980-\u09FF`).
*   **Result:** Markers like `¿¿`, `**`, `[[`, and spaces are now treated identically as separators in both views.

### 2. Explicit Closure Binding
Inside the badge creation loop, the index is now captured using a constant:
const versionIndex = index;
badge.onclick = (e) => {
    e.stopPropagation();
    selectF10Match(versionIndex); // Hard-links the badge to the specific array index
};

### 3. Visibility Mapping
The Raw scanner now cross-references the `visibleToRawMap`. It only registers a match if the character at that position in the source code is actually mapped to a visible character in the preview. This eliminates "ghost matches" hidden inside syntax.

### 4. Strategic Positioning
Badges are now anchored to the **bottom-left** of the word (`rect.bottom` and `rect.left`) instead of the top-right. This prevents the badge from covering the word and ensures it stays aligned with the start of the word even if it wraps to a new line.

## 📄 Related Files
- `static/script.js`: Core logic for `findRawWordMatches`, `getRenderedWordOccurrences`, and `showF10MatchLabels`.
- `static/style.css`: Styling and Z-index management for `.f10-match-badge`.

## 💡 Usage Tip
When F10 is triggered on a word with multiple matches:
1.  **Floating Badges:** Appear below every instance of the word.
2.  **Consolidated Dropdown:** Appears near your mouse cursor, showing snippets of the surrounding text for each version to help you pick the right one instantly.
