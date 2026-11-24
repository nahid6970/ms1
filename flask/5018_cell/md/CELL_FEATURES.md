# Cell Features & Individual Styling

## AI Cell Instructions
Each cell's **✨** button stays visible beneath the sticky table header while scrolling through its cell. It opens an instruction box below the button that floats over the cell without pushing the content down. The editor includes microphone dictation and a text area that grows to show multiline instructions. Opening it does not jump the page. The selected Gemini model applies the instruction to the cell's existing content and replaces that same cell. Configure the API key and test/select a working model under **Settings → AI Cell Instructions**.

Successful instructions are saved as recent prompts in this browser. Select one to reuse it, pin it to keep it at the top, or remove it with **×**. It keeps up to 20 unpinned prompts; pinned prompts do not count toward that limit.

See [AI Cell Instructions](AI_CELL_INSTRUCTIONS.md) for setup, behavior, search limitations, and restart requirements.

### CLI Agent Review
The cell AI editor's **Copy CLI task** button copies a stable cell reference and instructions for a CLI agent. The agent reads the cell and the app's live syntax guidance, asks what should change, then submits a proposal. The app shows a rendered preview and source diff; changes are saved only after approval. See [AI Cell Instructions](AI_CELL_INSTRUCTIONS.md) and the [AI API reference](../AI_API.md).

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

## Cell Font Family
**Access:** Right-click a cell → **Font Family**.
**Behavior:** Search the available font list, then choose a font for one cell or the current multi-cell selection. The choice is stored in that sheet's `cellStyles` entry and saved with the sheet data. **Use column/default font** removes the cell override.
**Installed fonts:** Use **Load installed system fonts** when the browser supports the Local Font Access API and grants access. Otherwise the picker offers common fonts detected by the browser; this fallback cannot enumerate every installed font.
**Rendering:** Applies to regular and merged cell editors. Markdown previews inherit the editor's font. Existing column fonts and the Vrinda/JetBrains fallback stack remain in use when the cell override is cleared.

## Cell Color History
**Access:** Unified Color Picker (🎨) → Right sidebar panel.
**Tracking:** Top 10 frequently used color combinations are stored in `localStorage`.
**CSS:** `.color-history-sidebar`, `.cell-color-history-item`.
**Function:** `trackCellColorUsage(bg, fg)`.

## Single Row View Mode
**Purpose:** Focus on one row at a time via a distraction-free interface.
**Controls:** 
- **Icons:** ⬅️ Previous, ➡️ Next buttons.
- **Counter:** A clickable number pad (e.g., `6/29`) appears between the navigation buttons.
**Logic:** 
- `renderTable()` filters for only one row index when active.
- **Interactivity:** Click the **Row Counter** directly to exit Single Row Mode and return to the full table.
- **Streamlined UI:** The primary "📖 Toggle" icon is automatically hidden while the mode is active to reduce header clutter.
- **Per-Sheet Persistence**: Each sheet remembers its own "Single Row Mode" state (On/Off) and the last viewed row index.
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
