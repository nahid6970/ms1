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
- Current sheet highlight.
- Sub-sheet indicators: `Sheet Name [Parent Name]`.
- Cyberpunk styling (matching F1).
- **Functions:** `openF2Popup()`, `populateF2RecentSheets()`.

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
**Purpose:** Instantly add the word under the cursor (or selection) to the search box and focus it.
**Implementation:** `handleKeyboardShortcuts` (F8).

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
