# Cell Features & Individual Styling

## Cell Complete Checkmark
**Access:** Right-click context menu → "Mark Complete"
**Visual:** Green checkmark (✓) in top-left corner via `.cell-complete::before`.
**Function:** `toggleCellComplete()`.

## Cell Sort Ranking
**Access:** Right-click context menu → "Set Sort Rank" (🏆)
**Visual:** Blue badge in top-right corner showing rank.
**Logic:** Ranked cells sort before unranked cells during column sort.
**Auto-Reranking:** When setting a rank (e.g., "1"), any existing cells with the same or higher rank are automatically incremented (e.g., 1 becomes 2, 2 becomes 3). This allows for easy "insertion" of new top-priority items.
**Batch Support:** Works with multiple selected cells.
**Function:** `setCellRank()`.

## Cell Color History
**Access:** Unified Color Picker (🎨) → Right sidebar panel.
**Tracking:** Top 10 frequently used color combinations are stored in `localStorage`.
**CSS:** `.color-history-sidebar`, `.cell-color-history-item`.
**Function:** `trackCellColorUsage(bg, fg)`.

## Single Row View Mode
**Purpose:** Focus on one row at a time.
**Controls:** 📖 Toggle, ⬅️ Previous, ➡️ Next buttons.
**Logic:** `renderTable()` filters for only one row index when active.

## Smart Textareas
**Purpose:** Ensures multiline and markdown content stays visible and editable.
**Behavior:** 
- Any cell containing **Markdown** markers or **Newlines** is automatically rendered using a **WYSIWYG ContentEditable** editor.
- This provides a "Hybrid" experience: styled text stays visible while you edit, and syntax markers (like `**`) appear in a subtle, faded style.
- These editors auto-resize as you type to match the content height.
- Global **Wrap (↩️)** settings are respected, but markdown always ensures data never gets squashed into a 1-line box.

## Raw Mode (Markdown Preview Toggle)
**Purpose:** View and edit raw text without markdown rendering.
**Toggle:** Markdown preview checkbox in toolbar.
**Behavior:**
- When disabled, markdown preview overlays are removed
- Cells show raw text with syntax markers visible
- Cell heights auto-adjust to show all content (no cutoff)
- `adjustCellHeightForMarkdown()` handles height in both modes
- `adjustAllMarkdownCells()` processes all textareas in raw mode
