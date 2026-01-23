# UX & Navigation Improvements

## F1 Quick Navigation Window
**Purpose:** Reorder categories and sheets via a cyberpunk-themed modal.
**Features:**
- Category context menus (Rename, Delete, Add).
- Sheet context menus (Rename, Move to Category, Delete).
- Drag and drop reorganization.
- Search modes (🔍 Category, * All Sheets, # Content).
- **CSS:** `.f1-popup`, `.f1-search-mode-toggle`, `.f1-category-title`.

## Recent Sheets Popup (F2)
**Purpose:** Quick navigation to recently viewed sheets.
**Features:**
- Recency-based sorting.
- Filter by **Sheet Name** or **Nickname**.
- Current sheet highlight.
- Sub-sheet indicators: `Sheet Name [Parent Name]`.
- Cyberpunk styling (matching F1).
- **Functions:** `openF2Popup()`, `populateF2RecentSheets()`, `filterF2Sheets()`.

## Quick Formatter (F3)
**Purpose:** Instant text formatting for selected text in cells.
**Layout Groups:**
1. Text Formatting (Bold, Italic, etc.)
2. Special Formatting (Super/Subscript)
3. Utilities (Link, Search, Sort Lines, Conversion)
4. Advanced (Select All Matching, Hidden Content)
5. Text Case
6. Quick Highlights (Custom Syntaxes automatically added here)

## Search Word Under Cursor (F8)
**Purpose:** Speed up searching by adding a word to the search box via hover or cursor position.
**Features:**
- **Hover-Pick:** Hover over any word and press **F8** to add it to the search.
- **Auto-Cleanup:** Strips syntax markers (`**`, `!!`, etc.) automatically.
- **Cross-Mode:** Works perfectly in both Parsed and Raw viewing modes.
- **Implementation:** `handleKeyboardShortcuts` (F8).

## Markdown Preview Toggle (📝)
**Purpose:** Switch between rendered HTML and raw editable text.
**Behavior:**
- **Parsed Mode:** Standard rendered markdown visuals.
- **Raw Mode:** Displays raw text including tags (e.g., `**text**`).
- **Syntax Highlighting:** Raw mode still shows **Custom Syntax colors** to aid readability.
- **No Layout Collapse:** Cells maintain their full height and wrap settings in both modes.
- **Refresh:** Toggling auto-refreshes the table to update all views.

## Swap Position (F9)
**Purpose:** Swap two words/phrases separated by a delimiter (space, tab, comma) while preserving alignment.
**Implementation:** `handleKeyboardShortcuts` (F9).

## Sub-Sheet Hierarchy
**Purpose:** Organize sheets in a parent-child structure.
**UI Elements:**
- Horizontal sub-sheet bar below toolbar.
- Parent tab always first, followed by sub-sheets.
- Right-click tabs to manage.
- Deletion cascade (Parent -> Children).

## Scroll Position Memory
**Purpose:** Remembers scroll position for each sheet.
**Implementation:**
- Stores to `localStorage.sheetScrollPositions`.
- Saves in `switchSheet()` before switch.
- Restores in `switchSheet()` after render (with `setTimeout`).

## Navigation & Sidebar
- **Tree View Sidebar:** Collapsible category folders with CSS-based tree lines.
- **Toggle:** Hamburger button (☰) in top-left.
- **Click-Outside-to-Close:** Context menus automatically close on outside clicks.
