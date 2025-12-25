# Cell Features & Individual Styling

## Cell Complete Checkmark
**Access:** Right-click context menu → "Mark Complete"
**Visual:** Green checkmark (✓) in top-left corner via `.cell-complete::before`.
**Function:** `toggleCellComplete()`.

## Cell Sort Ranking
**Access:** Right-click context menu → "Set Sort Rank" (🏆)
**Visual:** Blue badge in top-right corner showing rank.
**Logic:** Ranked cells sort before unranked cells during column sort.
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
