# Editing Extensions & Tools

## Multi-Term Search Feature
**Syntax:** `term1, term2, term3` (comma-separated)
**Purpose:** Search for multiple terms at once. Shows rows containing ANY of the search terms.
**Implementation:**
- **Search Logic:** In `searchTable()`, the search input is split by commas: `searchTerm.split(',').map(term => term.trim().toLowerCase())`
- **Matching:** Each cell is checked against all terms, and if any term matches, the row is shown.
- **Highlighting:** `highlightMultipleTermsInHtml()` manages merged/overlapping matches.
- **Overlay:** `createTextHighlightOverlayMulti()` for input/textarea elements.
- **Move Matches (⇅):** A special button appears in the search box when results are found. Clicking it performs dual-level grouping:
  - **Sheet Level:** All matching rows are moved to follow the first matched row's original position.
  - **Cell Level:** Within each matched row, all internal lines matching the search terms are moved to the top of that cell (following the cell's first match).
  - **Logic:** Requires at least 2 total matches (either 2+ rows or 2+ lines in a single cell) to activate. Automatically triggers a search refresh upon completion to show the updated layout.

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

## Search Word (F8)
**Purpose:** Speed up searching by automatically adding a word to the search box.
**Behavior:**
- **Hover Mode:** Simply hover your mouse over any word (in a cell or markdown preview) and press **F8**. The tool picks the word under the mouse pointer.
- **Edit Mode (No Selection):** Picks the word at the current text cursor position.
- **Selection Mode:** If text is selected (highlighted), that specific text is added.
- **Result:**
  - Adds the term to the existing search query (comma-separated).
  - Automatically triggers a search recalculation.
  - Focuses the search box.
- **Smart Recalculation:** Focusing the search box or using F8 forces a fresh search, ensuring results are always up-to-date with recent cell edits.

## Swap Word Position (F9)
**Purpose:** Quickly swap the position of two words or phrases separated by a delimiter.
**Behavior:**
- Select text containing two parts separated by a spacer (space, tab, or comma).
- Press **F9** to swap their positions while preserving the exact spacer in the middle.
- **Example:** `A , B` becomes `B , A`.
- **Note:** This is useful for reordering paired data or fixing word order.

## Literal Tab Insertion (Tab)
**Purpose:** Use the **Tab** key to insert actual tab characters within cells instead of moving focus.
**Behavior:**
- When editing a cell (Input or Textarea), pressing **Tab** inserts a `\t` character at the cursor position.
- This allows for precise alignment of text using the app's monospaced font support.
- Focus navigation between cells can still be done via mouse or other keyboard arrows/Enter keys.

## Move Lines Up/Down (Alt + Up / Down)
**Purpose:** Quickly reorder lines within a cell (Input or Textarea), similar to VS Code's `Alt + Up/Down` feature.
**Behavior:**
- **Single Line:** Moves the line containing the cursor up or down.
- **Selection:** Moves the entire block of selected lines up or down.
- **Logic:**
  - Swaps the selected lines with the line above (Alt+Up) or below (Alt+Down).
  - Preserves the cursor's horizontal position (offset) and the selection range.
  - Automatically triggers cell auto-resize if wrap mode is enabled.
