# Cell Features & Individual Styling

## Cell Complete Checkmark
**Access:** Right-click context menu → "Mark Complete"
**Visual:** 
- Green checkmark (✓) in top-left corner via `.cell-complete::before`
- Grid pattern overlay with vertical and horizontal gray lines (15px spacing)
- Grayed out background with reduced opacity
**Function:** `toggleCellComplete()`.

## Cell Sort Ranking
**Access:** Right-click context menu → "Set Sort Rank" (🏆)
**Visual:** Blue badge in top-right corner showing rank.
**Logic:** Ranked cells sort before unranked cells during column sort.
**Auto-Reranking:** When setting a rank (e.g., "1"), any existing cells with the same or higher rank are automatically incremented (e.g., 1 becomes 2, 2 becomes 3). This allows for easy "insertion" of new top-priority items.
**Normalization:** Ranks are globally normalized to a contiguous sequence (1, 2, 3...) upon app load and after every change, ensuring no gaps or duplicates.
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
**Logic:** 
- `renderTable()` filters for only one row index when active.
- **Per-Sheet Persistence**: Each sheet remembers its own "Single Row Mode" state (On/Off) and the last viewed row index. This allows you to browse one sheet row-by-row while keeping another in full table view.
- **State Management**: Saved to `localStorage` under `sheetSingleRowStates`.

## Smart Textareas
**Purpose:** Ensures multiline and markdown content stays visible and editable.
**Behavior:** 
- Any cell containing **Markdown** markers or **Newlines** is automatically rendered using a **WYSIWYG ContentEditable** editor.
- This provides a "Hybrid" experience: styled text stays visible while you edit, and syntax markers (like `**`) appear in a subtle, faded style.
- These editors auto-resize as you type to match the content height.
- Global **Wrap (↩️)** settings are respected, but markdown always ensures data never gets squashed into a 1-line box.

## Export Cell to PDF (Image)
**Access:** Right-click context menu → 📄 Export Cell to PDF (Image).
**Purpose:** Generates a professional PDF from a single cell's visual appearance.
**Features:**
- **Custom Width:** Prompts the user for a layout width (in pixels) before generating.
- **Visual Fidelity:** Uses `html2canvas` to capture exactly how the cell looks in the browser.
- **Professional Header:** Includes sheet name, column name, and row index.

## Print Cell (Selectable PDF)
**Access:** Right-click context menu → 🖨️ Print Cell (Selectable PDF).
**Purpose:** Generates a high-quality, searchable, and selectable PDF via the browser's print dialog.
**Features:**
- **Searchable Text:** Unlike the image export, text can be selected and searched.
- **Perfect Tables:** Custom CSS ensures complex markdown tables render correctly (no "line-by-line" collapse).
- **Vector Fonts:** Uses JetBrains Mono and Vrinda fonts for crisp text at any zoom level.
- **Math Support:** Full KaTeX math rendering support.
- **Documentation:** See [Cell PDF Export](md/CELL_PDF_EXPORT_FEATURE.md) for full details.

## Raw Mode (Markdown Preview Toggle)
**Purpose:** View and edit raw text without markdown rendering.
**Toggle:** Markdown preview checkbox in toolbar.
**Behavior:**
- When disabled, markdown preview overlays are removed
- Cells show raw text with syntax markers visible
- Cell heights auto-adjust to show all content (no cutoff)
- `adjustCellHeightForMarkdown()` handles height in both modes
- `adjustAllMarkdownCells()` processes all textareas in raw mode
