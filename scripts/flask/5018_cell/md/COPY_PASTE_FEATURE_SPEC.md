# Copy/Paste & Import/Export Feature Implementation

## Overview
Add ability to copy/paste rows and columns, plus import/export data between sheets.

## Features to Implement

### Option 1: Context Menu Operations

#### A. Row Context Menu (Right-click on row number)
**Menu Items:**
- 📋 Copy Row
- 📥 Paste Rows

**Functions Needed:**
```javascript
// Location: static/script.js (add after line ~5085)

function showRowContextMenu(e, rowIndex) {
    // Create and show context menu at mouse position
    // Menu items: Copy Row, Paste Rows
}

function copyRow(rowIndex) {
    const row = tableData.sheets[currentSheet].rows[rowIndex];
    const tsvData = row.join('\t'); // Tab-separated values
    navigator.clipboard.writeText(tsvData);
    showToast('Row copied to clipboard', 'success');
}

function showPasteRowsModal() {
    // Show modal with textarea
    // User pastes TSV or CSV data
    // Parse and append to current sheet
}

function pasteRows(dataText) {
    const lines = dataText.trim().split('\n');
    lines.forEach(line => {
        // Detect delimiter (tab or comma)
        const delimiter = line.includes('\t') ? '\t' : ',';
        const cells = line.split(delimiter).map(c => c.trim());
        tableData.sheets[currentSheet].rows.push(cells);
    });
    renderTable();
    saveData();
}
```

#### B. Column Context Menu (Right-click on column header)
**Menu Items:**
- 📋 Copy Column

**Functions Needed:**
```javascript
function showColumnContextMenu(e, colIndex) {
    // Create and show context menu
    // Menu item: Copy Column
}

function copyColumn(colIndex) {
    const rows = tableData.sheets[currentSheet].rows;
    const columnData = rows.map(row => row[colIndex] || '').join('\n');
    navigator.clipboard.writeText(columnData);
    showToast('Column copied to clipboard', 'success');
}
```

### Option 2: Import/Export Buttons

#### A. Toolbar Buttons
**Add to toolbar (templates/index.html after existing buttons):**
```html
<button class="btn btn-secondary" onclick="showImportDataModal()" title="Import Data">
    📥 Import
</button>
<button class="btn btn-secondary" onclick="exportCurrentSheet()" title="Export Sheet">
    📤 Export
</button>
```

#### B. Import Modal
**Add to templates/index.html (before closing body tag):**
```html
<!-- Import Data Modal -->
<div id="importDataModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>📥 Import Data</h2>
            <span class="close" onclick="closeImportDataModal()">&times;</span>
        </div>
        <div style="padding: 24px;">
            <p>Paste your data below (tab-separated or comma-separated):</p>
            <textarea id="importDataText" style="width: 100%; height: 300px; font-family: monospace; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"></textarea>
            
            <div style="margin-top: 16px;">
                <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <input type="radio" name="importMode" value="append" checked>
                    <span>Append to current sheet</span>
                </label>
                <label style="display: flex; align-items: center; gap: 8px;">
                    <input type="radio" name="importMode" value="replace">
                    <span>Replace current sheet (⚠️ deletes existing data)</span>
                </label>
            </div>
            
            <div style="margin-top: 20px; display: flex; gap: 10px;">
                <button class="btn btn-primary" onclick="importData()">Import</button>
                <button class="btn btn-secondary" onclick="closeImportDataModal()">Cancel</button>
            </div>
        </div>
    </div>
</div>
```

#### C. Import/Export Functions
**Add to static/script.js:**
```javascript
function showImportDataModal() {
    document.getElementById('importDataModal').style.display = 'block';
    document.getElementById('importDataText').value = '';
    document.getElementById('importDataText').focus();
}

function closeImportDataModal() {
    document.getElementById('importDataModal').style.display = 'none';
}

function importData() {
    const dataText = document.getElementById('importDataText').value.trim();
    if (!dataText) {
        showToast('Please paste some data', 'warning');
        return;
    }
    
    const mode = document.querySelector('input[name="importMode"]:checked').value;
    const lines = dataText.split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
        showToast('No data to import', 'warning');
        return;
    }
    
    // Detect delimiter (tab or comma)
    const firstLine = lines[0];
    const delimiter = firstLine.includes('\t') ? '\t' : ',';
    
    // Parse data
    const newRows = lines.map(line => {
        return line.split(delimiter).map(cell => cell.trim());
    });
    
    // Apply based on mode
    if (mode === 'replace') {
        if (!confirm('This will delete all existing rows. Continue?')) {
            return;
        }
        tableData.sheets[currentSheet].rows = newRows;
    } else {
        // Append
        tableData.sheets[currentSheet].rows.push(...newRows);
    }
    
    renderTable();
    saveData();
    closeImportDataModal();
    showToast(`Imported ${newRows.length} rows`, 'success');
}

function exportCurrentSheet() {
    const rows = tableData.sheets[currentSheet].rows;
    const tsvData = rows.map(row => row.join('\t')).join('\n');
    
    navigator.clipboard.writeText(tsvData);
    showToast('Sheet exported to clipboard (TSV format)', 'success');
}
```

### Paste Rows Modal
**Add to templates/index.html:**
```html
<!-- Paste Rows Modal -->
<div id="pasteRowsModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>📥 Paste Rows</h2>
            <span class="close" onclick="closePasteRowsModal()">&times;</span>
        </div>
        <div style="padding: 24px;">
            <p>Paste row data below (tab-separated or comma-separated):</p>
            <textarea id="pasteRowsText" style="width: 100%; height: 200px; font-family: monospace; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"></textarea>
            
            <div style="margin-top: 20px; display: flex; gap: 10px;">
                <button class="btn btn-primary" onclick="executePasteRows()">Paste</button>
                <button class="btn btn-secondary" onclick="closePasteRowsModal()">Cancel</button>
            </div>
        </div>
    </div>
</div>
```

**Functions:**
```javascript
function closePasteRowsModal() {
    document.getElementById('pasteRowsModal').style.display = 'none';
}

function executePasteRows() {
    const dataText = document.getElementById('pasteRowsText').value.trim();
    if (!dataText) {
        showToast('Please paste some data', 'warning');
        return;
    }
    
    pasteRows(dataText);
    closePasteRowsModal();
}
```

### Row Context Menu HTML & CSS
**Add to templates/index.html:**
```html
<!-- Row Context Menu -->
<div id="rowContextMenu" class="context-menu" style="display: none;">
    <div class="context-menu-item" onclick="copyRowFromMenu()">
        📋 Copy Row
    </div>
    <div class="context-menu-item" onclick="showPasteRowsModal()">
        📥 Paste Rows
    </div>
</div>
```

**Add to static/style.css:**
```css
/* Row/Column Context Menu */
#rowContextMenu, #columnContextMenu {
    position: fixed;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    z-index: 10000;
    min-width: 150px;
}
```

## Implementation Steps

1. **Add Modal HTML** to templates/index.html
2. **Add Context Menu HTML** to templates/index.html
3. **Add CSS** to static/style.css
4. **Add JavaScript functions** to static/script.js
5. **Add toolbar buttons** to templates/index.html
6. **Test** copying/pasting between sheets
7. **Update DEVELOPER_GUIDE.md** with documentation

## Testing Checklist

- [ ] Copy single row
- [ ] Paste rows (TSV format)
- [ ] Paste rows (CSV format)
- [ ] Copy column
- [ ] Import data (append mode)
- [ ] Import data (replace mode)
- [ ] Export sheet to clipboard
- [ ] Test with special characters
- [ ] Test with empty cells
- [ ] Test with markdown syntax in cells

## Notes

- Use TSV (tab-separated) as primary format for better compatibility with Excel/Google Sheets
- CSV as fallback (auto-detect based on presence of tabs)
- All operations use clipboard API (`navigator.clipboard`)
- Toast notifications for user feedback
- Confirmation dialog for destructive operations (replace mode)

## Variable to Track
```javascript
let contextMenuRowIndex = null; // Store row index for context menu operations
```

## Next Session TODO
1. Start by adding the modal HTML
2. Then add JavaScript functions
3. Test each feature incrementally
4. Update documentation
