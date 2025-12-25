# Editing Extensions & Tools

## Multi-Term Search Feature
**Syntax:** `term1, term2, term3` (comma-separated)
**Purpose:** Search for multiple terms at once. Shows rows containing ANY of the search terms.
**Implementation:**
- **Search Logic:** In `searchTable()`, the search input is split by commas: `searchTerm.split(',').map(term => term.trim().toLowerCase())`
- **Matching:** Each cell is checked against all terms, and if any term matches, the row is shown.
- **Highlighting:** `highlightMultipleTermsInHtml()` manages merged/overlapping matches.
- **Overlay:** `createTextHighlightOverlayMulti()` for input/textarea elements.

## Line Conversion Tools
**Implementation:**
- **Lines to Comma:** `linesToComma()`
- **Comma to Lines:** `commaToLines()`
- **Access:** F3 Quick Formatter Utility buttons.

## Text Case Conversion
**Available Cases:** UPPERCASE, lowercase, Proper Case.
**Access:** F3 Quick Formatter Text Case section.
**Function:** `changeTextCase(caseType, event)`.

## Multi-Cursor Selection (Ctrl+Shift+D)
**Purpose:** VS Code-like "Select Next Occurrence".
**Features:**
- Starts from current selection.
- Immediate activation after >1 instance selected.
- Partial selection support.
- Selective editing (only applies to explicitly selected matches).

## Sort Lines Feature
**Purpose:** Sorts selected lines while preserving parent-child relationships in lists.
**Sorting Priority:** No dashes > single dash `-` > double dash `--` > alphabetical/numerical.
**Smart Grouping:** Children stay with their parents during reordering.
**Function:** `sortLines()`.
