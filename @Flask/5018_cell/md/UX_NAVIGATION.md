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
1. Text Formatting (Bold, Italic, H, H+, S, W, □, T, Code)
2. Utilities (Link, Search, Search+, Sort Lines, 📊, ➡️, ⬇️, 🎯, 🧹)
3. Advanced (Hide Text 👁️, Correct Answer ✓)
4. Math (Superscript, Subscript, Square Root, Fraction)
5. Text Case (abc, ABC, Abc)
6. Quick Highlights (Custom Syntaxes automatically added here)

## Search Word Under Cursor (F8)
**Purpose:** Speed up searching by adding a word to the search box via hover or cursor position.
**Features:**
- **Hover-Pick:** Hover over any word and press **F8** to add it to the search.
- **Auto-Cleanup:** Strips syntax markers (`**`, `!!`, etc.) automatically.
- **Cross-Mode:** Works perfectly in both Parsed and Raw viewing modes.
- **Implementation:** `handleKeyboardShortcuts` (F8).

## Toolbar Utilities
### Temporary Notepad (📝)
**Purpose:** A persistent scratchpad for quick notes that survive page refreshes but are not saved to the sheet.
**Features:**
- **Toggle:** Click 📝 icon in the toolbar.
- **Behavior:** Dedicated popup with resizeable textarea.
- **Persistence:** Autosaves to `localStorage`.
- **Interaction:** Closes when clicking outside or opening other popups.

### Bookmark / Recent Edits (🕒)
**Purpose:** View and jump to recently edited cells from other sheets.
**Features:**
- **Toggle:** Click 🕒 icon.
- **Direct Edit:** Edit cell content directly within the popup.
- **Sync:** Updates in real-time as data changes.

## Markdown View Modes (📝 & 👁️/✨)
**Purpose:** Switch between different levels of markdown rendering and syntax visibility.
**Modes:**
1.  **Raw Mode (📝):** Displays raw text including tags (e.g., `**text**`) in standard inputs.
2.  **Visual Mode:** Renders HTML. Click to cycle between:
    *   **Standard (👁️):** Focus reveals dimmed syntax markers.
    *   **Clean (✨):** Focus hides all syntax markers (True WYSIWYG).
**Behavior:**
- **Toggle Raw:** Click 📝 to switch to source code view.
- **Cycle Visual:** Click or Right-click to switch between Standard and Clean modes.
- **Indicators:** Icon changes (👁️ vs ✨) and Clean mode adds a magenta glow.
- **Tooltips:** Hover over buttons to see the current active mode name.
- **Persistence:** Remembers selection via `localStorage.markdownPreviewMode`.
- **See Also:** [Markdown View Modes](md/MARKDOWN_MODES.md) for technical details.

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
