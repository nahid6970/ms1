let tableData = { sheets: [], activeSheet: 0, categories: [], sheetCategories: {} };
let currentSheet = 0;
let currentCategory = null; // null means "Uncategorized"
let contextMenuCell = null;
let selectedCells = []; // Array of {row, col, td} objects for multi-cell operations
let isSelecting = false;
let sheetHistory = []; // Track recently visited sheets for Alt+M toggle
let singleRowMode = false;
let singleRowIndex = 0;

/**
 * MULTI-CELL OPERATION PATTERN:
 * When adding new context menu operations, use this pattern to support multiple cells:
 * 
 * if (selectedCells.length > 0) {
 *     selectedCells.forEach(cell => {
 *         const cellInput = cell.td.querySelector('input, textarea');
 *         // Apply operation to cell.row, cell.col, cellInput
 *     });
 *     showToast(`Operation applied to ${selectedCells.length} cells`, 'success');
 * } else {
 *     // Apply operation to single cell (contextMenuCell)
 * }
 */

// Load data on page load
window.onload = function () {
    const loadStartTime = performance.timing.navigationStart;

    initializeApp();
};

function initializeApp() {
    // Set up form handlers
    document.getElementById('columnForm').onsubmit = handleColumnFormSubmit;
    document.getElementById('renameForm').onsubmit = handleRenameFormSubmit;

    // Set up keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // Prevent scroll jump on Enter, Cut, and other operations in textareas
    document.addEventListener('beforeinput', e => {
        const ta = e.target;
        if (ta.tagName !== 'TEXTAREA') return;

        // Handle operations that might cause scroll jump
        const scrollTriggeringOps = [
            'insertLineBreak',           // Enter key
            'deleteByCut',               // Cut operation
            'deleteContentBackward',     // Backspace
            'deleteContentForward'       // Delete key
        ];

        if (!scrollTriggeringOps.includes(e.inputType)) return;

        // Prevent the container from scrolling
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            const savedScrollTop = tableContainer.scrollTop;
            const savedScrollLeft = tableContainer.scrollLeft;

            // Use multiple requestAnimationFrame to ensure scroll is locked
            requestAnimationFrame(() => {
                tableContainer.scrollTop = savedScrollTop;
                tableContainer.scrollLeft = savedScrollLeft;

                // Only call keepCursorCentered for Enter key
                if (e.inputType === 'insertLineBreak') {
                    keepCursorCentered(ta);
                }

                requestAnimationFrame(() => {
                    tableContainer.scrollTop = savedScrollTop;
                    tableContainer.scrollLeft = savedScrollLeft;

                    requestAnimationFrame(() => {
                        tableContainer.scrollTop = savedScrollTop;
                        tableContainer.scrollLeft = savedScrollLeft;
                    });
                });
            });
        } else if (e.inputType === 'insertLineBreak') {
            requestAnimationFrame(() => {
                keepCursorCentered(ta);
            });
        }
    });

    // Save scroll position on scroll
    const tableContainer = document.querySelector('.table-container');
    if (tableContainer) {
        tableContainer.addEventListener('scroll', () => {
            localStorage.setItem('scrollTop', tableContainer.scrollTop);
            localStorage.setItem('scrollLeft', tableContainer.scrollLeft);
        });
    }



    // Set up color picker sync for background color
    const colorInput = document.getElementById('columnColor');
    const colorText = document.getElementById('columnColorText');

    colorInput.addEventListener('input', (e) => {
        colorText.value = e.target.value.toUpperCase();
    });

    // Set up color picker sync for text color
    const textColorInput = document.getElementById('columnTextColor');
    const textColorText = document.getElementById('columnTextColorText');

    textColorInput.addEventListener('input', (e) => {
        textColorText.value = e.target.value.toUpperCase();
    });

    // Set up color picker sync for header background color
    const headerBgInput = document.getElementById('headerBgColor');
    const headerBgText = document.getElementById('headerBgColorText');

    headerBgInput.addEventListener('input', (e) => {
        headerBgText.value = e.target.value.toUpperCase();
    });

    // Set up color picker sync for header text color
    const headerTextInput = document.getElementById('headerTextColor');
    const headerTextText = document.getElementById('headerTextColorText');

    headerTextInput.addEventListener('input', (e) => {
        headerTextText.value = e.target.value.toUpperCase();
    });

    // Set up grid line color picker (will be initialized when settings modal opens)
    // Apply saved grid line color on page load
    const savedGridColor = localStorage.getItem('gridLineColor') || '#dddddd';
    document.documentElement.style.setProperty('--grid-line-color', savedGridColor);

    // Clear old localStorage values and set new defaults
    localStorage.removeItem('actionsWidth');
    localStorage.removeItem('rownumWidth');

    // Load initial data
    loadData();

    // Restore wrap toggle state
    const wrapEnabled = localStorage.getItem('rowWrapEnabled') === 'true';
    const wrapToggle = document.getElementById('wrapToggle');
    if (wrapToggle) {
        wrapToggle.checked = wrapEnabled;
        if (wrapEnabled) {
            const table = document.getElementById('dataTable');
            if (table) {
                table.classList.add('wrap-enabled');
            }
        }
    }

    // Restore row numbers toggle state
    const rowNumbersVisible = localStorage.getItem('rowNumbersVisible') !== 'false'; // Default true
    const rowToggle = document.getElementById('rowToggle');
    if (rowToggle) {
        rowToggle.checked = rowNumbersVisible;
        if (!rowNumbersVisible) {
            const table = document.getElementById('dataTable');
            if (table) {
                table.classList.add('hide-row-numbers');
            }
        }
    }

    // Restore markdown preview toggle state
    const markdownPreviewEnabled = localStorage.getItem('markdownPreviewEnabled') !== 'false'; // Default true
    const markdownToggle = document.getElementById('markdownToggle');
    if (markdownToggle) {
        markdownToggle.checked = markdownPreviewEnabled;
        if (!markdownPreviewEnabled) {
            const table = document.getElementById('dataTable');
            if (table) {
                table.classList.add('hide-markdown-preview');
            }
        }
    }

    // Initialize font size scale
    setTimeout(() => {
        applyFontSizeScale();
    }, 100);

    // Initialize Vrinda font setting
    const vrindaEnabled = localStorage.getItem('vrindaFontEnabled') !== 'false'; // Default true
    const table = document.getElementById('dataTable');
    if (!vrindaEnabled && table) {
        table.classList.add('disable-vrinda');
    }
    // Restore hidden text toggle state
    const hiddenTextVisible = localStorage.getItem('hiddenTextVisible') === 'true';
    const hiddenTextToggle = document.getElementById('hiddenTextToggle');
    if (hiddenTextToggle) {
        hiddenTextToggle.checked = hiddenTextVisible;
        if (hiddenTextVisible) {
            document.body.classList.add('show-hidden-text');
        }
    }
}

function loadColumnWidths() {
    const actionsWidth = localStorage.getItem('actionsWidth') || '75px';
    const rownumWidth = localStorage.getItem('rownumWidth') || '75px';

    document.documentElement.style.setProperty('--actions-width', actionsWidth);
    document.documentElement.style.setProperty('--rownum-width', rownumWidth);
}

let fontSizeScale = parseFloat(localStorage.getItem('fontSizeScale')) || 1.0;

function adjustFontSize(delta) {
    fontSizeScale += delta * 0.1;
    fontSizeScale = Math.max(0.5, Math.min(2.0, fontSizeScale)); // Limit between 50% and 200%

    localStorage.setItem('fontSizeScale', fontSizeScale);

    // Update display
    document.getElementById('fontSizeDisplay').textContent = Math.round(fontSizeScale * 100) + '%';

    // Apply to all inputs and textareas in cells
    const table = document.getElementById('dataTable');
    if (table) {
        const cells = table.querySelectorAll('td:not(.row-number) input, td:not(.row-number) textarea');
        cells.forEach(cell => {
            const currentFontSize = parseFloat(window.getComputedStyle(cell).fontSize);
            const baseFontSize = currentFontSize / (parseFloat(cell.dataset.fontScale) || 1.0);
            cell.style.fontSize = (baseFontSize * fontSizeScale) + 'px';
            cell.dataset.fontScale = fontSizeScale;

            // Auto-resize textareas if wrap is enabled
            if (cell.tagName === 'TEXTAREA' && table.classList.contains('wrap-enabled')) {
                autoResizeTextarea(cell);
            }
        });

        // Also apply to markdown previews
        const previews = table.querySelectorAll('.markdown-preview');
        previews.forEach(preview => {
            const currentFontSize = parseFloat(window.getComputedStyle(preview).fontSize);
            const baseFontSize = currentFontSize / (parseFloat(preview.dataset.fontScale) || 1.0);
            preview.style.fontSize = (baseFontSize * fontSizeScale) + 'px';
            preview.dataset.fontScale = fontSizeScale;
        });
    }
}

function applyFontSizeScale() {
    const table = document.getElementById('dataTable');
    if (table && fontSizeScale !== 1.0) {
        const cells = table.querySelectorAll('td:not(.row-number) input, td:not(.row-number) textarea');
        cells.forEach(cell => {
            const currentFontSize = parseFloat(window.getComputedStyle(cell).fontSize);
            if (currentFontSize) {
                cell.style.fontSize = (currentFontSize * fontSizeScale) + 'px';
                cell.dataset.fontScale = fontSizeScale;

                // Auto-resize textareas if wrap is enabled
                if (cell.tagName === 'TEXTAREA' && table.classList.contains('wrap-enabled')) {
                    autoResizeTextarea(cell);
                }
            }
        });

        const previews = table.querySelectorAll('.markdown-preview');
        previews.forEach(preview => {
            const currentFontSize = parseFloat(window.getComputedStyle(preview).fontSize);
            if (currentFontSize) {
                preview.style.fontSize = (currentFontSize * fontSizeScale) + 'px';
                preview.dataset.fontScale = fontSizeScale;
            }
        });
    }
    document.getElementById('fontSizeDisplay').textContent = Math.round(fontSizeScale * 100) + '%';
}



function handleKeyboardShortcuts(e) {
    // Ctrl+S or Cmd+S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();

        // Blur the currently focused element to trigger onchange
        if (document.activeElement && (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA')) {
            document.activeElement.blur();
        }

        // Small delay to ensure onchange fires before saving
        setTimeout(() => {
            saveData();
        }, 50);
    }

    // Ctrl+F or Cmd+F to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    // Escape to clear search
    if (e.key === 'Escape' && document.activeElement.id === 'searchInput') {
        clearSearch();
    }

    // Enter to next match
    if (e.key === 'Enter' && document.activeElement.id === 'searchInput') {
        e.preventDefault();
        nextSearchMatch();
    }

    // F1 to open quick navigation popup
    if (e.key === 'F1') {
        e.preventDefault();
        openF1Popup();
    }

    // Escape to close F1 popup
    if (e.key === 'Escape' && document.getElementById('f1Popup').classList.contains('show')) {
        closeF1Popup();
    }

    // F2 to open recent sheets popup
    if (e.key === 'F2') {
        e.preventDefault();
        openF2Popup();
    }

    // Escape to close F2 popup
    if (e.key === 'Escape' && document.getElementById('f2Popup') && document.getElementById('f2Popup').classList.contains('show')) {
        closeF2Popup();
    }

    // F3 to open quick markdown formatter
    if (e.key === 'F3') {
        e.preventDefault();
        const activeElement = document.activeElement;
        if ((activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA') &&
            activeElement.selectionStart !== activeElement.selectionEnd) {
            showQuickFormatter(activeElement);
        }
    }

    // Escape to close quick formatter
    if (e.key === 'Escape') {
        const formatter = document.getElementById('quickFormatter');
        if (formatter && formatter.style.display === 'block') {
            closeQuickFormatter();
        }
    }

    // F4 to toggle top ribbons
    if (e.key === 'F4') {
        e.preventDefault();
        toggleTopRibbons();
    }

    // Ctrl+Shift+D to select next occurrence (multi-cursor simulation)
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        const activeElement = document.activeElement;
        if (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA') {
            e.preventDefault();
            selectNextOccurrence(activeElement);
        }
    }

    // Ctrl+Alt+Down to add cursor below (multi-line cursor)
    if (e.ctrlKey && e.altKey && e.key === 'ArrowDown') {
        const activeElement = document.activeElement;
        if (activeElement.tagName === 'TEXTAREA') {
            e.preventDefault();
            addCursorBelow(activeElement);
        }
    }

    // Ctrl+Alt+Up to add cursor above (multi-line cursor)
    if (e.ctrlKey && e.altKey && e.key === 'ArrowUp') {
        const activeElement = document.activeElement;
        if (activeElement.tagName === 'TEXTAREA') {
            e.preventDefault();
            addCursorAbove(activeElement);
        }
    }

    // Alt+N to add new row
    if (e.altKey && e.key === 'n') {
        e.preventDefault();
        addRow();
    }

    // Alt+M to toggle between most recent 2 sheets
    if (e.altKey && e.key === 'm') {
        e.preventDefault();
        toggleRecentSheets();
    }

    // Handle Enter key in textareas when wrap is enabled
    if (e.key === 'Enter' && document.activeElement.tagName === 'TEXTAREA') {
        const textarea = document.activeElement;
        // Check if it's not a merged cell textarea (those already handle Enter properly)
        if (!textarea.closest('td.merged-cell')) {
            // Allow Enter to create new line in wrapped cells
            // The default behavior is what we want, so we don't prevent it
            // Just trigger auto-resize after a short delay
            setTimeout(() => {
                autoResizeTextarea(textarea);
            }, 10);
        }
    }
}

async function loadData() {
    try {
        const response = await fetch('/api/data');
        tableData = await response.json();
        currentSheet = tableData.activeSheet || 0;

        // Set currentCategory to match the active sheet's category
        const sheetCategory = tableData.sheetCategories[currentSheet] || tableData.sheetCategories[String(currentSheet)] || null;
        currentCategory = sheetCategory;

        // Restore sheet history from localStorage for Alt+M toggle
        const savedHistory = localStorage.getItem('sheetHistory');
        if (savedHistory) {
            try {
                sheetHistory = JSON.parse(savedHistory);
            } catch (e) {
                sheetHistory = [];
            }
        }

        initializeCategories();
        renderCategoryTabs();
        renderSheetTabs();
        renderTable();

        // Display load time after everything is rendered
        requestAnimationFrame(() => {
            // performance.now() gives time in milliseconds since page load started
            const totalLoadTime = performance.now();
            const seconds = (totalLoadTime / 1000).toFixed(2);
            const loadTimeElement = document.getElementById('loadTimeValue');
            if (loadTimeElement) {
                loadTimeElement.textContent = `${seconds}s`;
            }
        });
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

async function saveData() {
    try {
        tableData.activeSheet = currentSheet;
        const response = await fetch('/api/data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tableData)
        });
        const result = await response.json();
        if (result.success) {
            showToast('Data saved successfully!', 'success');
        }
    } catch (error) {
        console.error('Error saving data:', error);
        showToast('Error saving data!', 'error');
    }
}



function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Auto-save active sheet when switching
async function autoSaveActiveSheet() {
    try {
        tableData.activeSheet = currentSheet;
        await fetch('/api/data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tableData)
        });
    } catch (error) {
        console.error('Error auto-saving:', error);
    }
}

function addColumn() {
    document.getElementById('editingColumnIndex').value = '-1';
    document.getElementById('columnModalTitle').textContent = 'Add Column';
    document.getElementById('columnSubmitBtn').textContent = 'Add Column';
    document.getElementById('columnForm').reset();
    document.getElementById('columnColor').value = '#ffffff';
    document.getElementById('columnColorText').value = '#FFFFFF';
    document.getElementById('columnTextColor').value = '#000000';
    document.getElementById('columnTextColorText').value = '#000000';
    document.getElementById('columnFontSize').value = '18';
    document.getElementById('headerBgColor').value = '#f8f9fa';
    document.getElementById('headerBgColorText').value = '#F8F9FA';
    document.getElementById('headerTextColor').value = '#333333';
    document.getElementById('headerTextColorText').value = '#333333';
    document.getElementById('headerBold').checked = true;
    document.getElementById('headerItalic').checked = false;
    document.getElementById('headerCenter').checked = false;
    document.getElementById('columnModal').style.display = 'block';
}

function editColumn(index) {
    const sheet = tableData.sheets[currentSheet];
    const col = sheet.columns[index];

    document.getElementById('editingColumnIndex').value = index;
    document.getElementById('columnModalTitle').textContent = 'Edit Column';
    document.getElementById('columnSubmitBtn').textContent = 'Update Column';
    document.getElementById('columnName').value = col.name;
    document.getElementById('columnType').value = col.type;
    document.getElementById('columnWidth').value = col.width;
    document.getElementById('columnColor').value = col.color;
    document.getElementById('columnColorText').value = col.color.toUpperCase();
    document.getElementById('columnTextColor').value = col.textColor || '#000000';
    document.getElementById('columnTextColorText').value = (col.textColor || '#000000').toUpperCase();
    document.getElementById('columnFont').value = col.font || '';
    document.getElementById('columnFontSize').value = col.fontSize || '18';

    // Load header styling
    document.getElementById('headerBgColor').value = col.headerBgColor || '#f8f9fa';
    document.getElementById('headerBgColorText').value = (col.headerBgColor || '#f8f9fa').toUpperCase();
    document.getElementById('headerTextColor').value = col.headerTextColor || '#333333';
    document.getElementById('headerTextColorText').value = (col.headerTextColor || '#333333').toUpperCase();
    document.getElementById('headerBold').checked = col.headerBold !== false; // Default true
    document.getElementById('headerItalic').checked = col.headerItalic || false;
    document.getElementById('headerCenter').checked = col.headerCenter || false;

    document.getElementById('columnModal').style.display = 'block';
}

function closeColumnModal() {
    document.getElementById('columnModal').style.display = 'none';
    document.getElementById('columnForm').reset();
}

function closeRenameModal() {
    document.getElementById('renameModal').style.display = 'none';
    document.getElementById('renameForm').reset();
}

function closeSettingsModal() {
    document.getElementById('settingsModal').style.display = 'none';
}

function showMarkdownGuide() {
    closeSettingsModal();
    document.getElementById('markdownGuideModal').style.display = 'block';
}

function closeMarkdownGuide() {
    document.getElementById('markdownGuideModal').style.display = 'none';
}

function getExcelColumnName(index) {
    // Convert 0-based index to Excel-style column name (A, B, C, ... Z, AA, AB, ...)
    let name = '';
    index++; // Make it 1-based
    while (index > 0) {
        index--;
        name = String.fromCharCode(65 + (index % 26)) + name;
        index = Math.floor(index / 26);
    }
    return name;
}

async function handleColumnFormSubmit(e) {
    e.preventDefault();

    const editingIndex = parseInt(document.getElementById('editingColumnIndex').value);
    let columnName = document.getElementById('columnName').value.trim();

    // Auto-generate column name if empty (only for new columns)
    if (!columnName && editingIndex < 0) {
        const sheet = tableData.sheets[currentSheet];
        columnName = getExcelColumnName(sheet.columns.length);
    }

    const column = {
        name: columnName,
        type: document.getElementById('columnType').value,
        width: document.getElementById('columnWidth').value,
        color: document.getElementById('columnColor').value,
        textColor: document.getElementById('columnTextColor').value,
        font: document.getElementById('columnFont').value,
        fontSize: document.getElementById('columnFontSize').value,
        headerBgColor: document.getElementById('headerBgColor').value,
        headerTextColor: document.getElementById('headerTextColor').value,
        headerBold: document.getElementById('headerBold').checked,
        headerItalic: document.getElementById('headerItalic').checked,
        headerCenter: document.getElementById('headerCenter').checked
    };

    const sheet = tableData.sheets[currentSheet];

    if (editingIndex >= 0) {
        // Update existing column
        sheet.columns[editingIndex] = column;
        renderTable();
        closeColumnModal();
        showToast('Column updated successfully!', 'success');
    } else {
        // Add new column
        try {
            const response = await fetch('/api/columns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ column, sheetIndex: currentSheet })
            });

            if (response.ok) {
                sheet.columns.push(column);
                sheet.rows.forEach(row => row.push(''));
                renderTable();
                closeColumnModal();
                showToast('Column added successfully!', 'success');
            }
        } catch (error) {
            console.error('Error adding column:', error);
            showToast('Error adding column!', 'error');
        }
    }
}

async function handleRenameFormSubmit(e) {
    e.preventDefault();

    const newName = document.getElementById('sheetName').value;
    const newNickname = document.getElementById('sheetNickname').value.trim();

    try {
        const response = await fetch(`/api/sheets/${currentSheet}/rename`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName, nickname: newNickname })
        });

        if (response.ok) {
            tableData.sheets[currentSheet].name = newName;
            tableData.sheets[currentSheet].nickname = newNickname;
            renderSheetTabs();
            closeRenameModal();
        }
    } catch (error) {
        console.error('Error renaming sheet:', error);
    }
}

async function deleteColumn(index) {
    if (!confirm('Delete this column?')) return;

    try {
        const response = await fetch(`/api/columns/${currentSheet}/${index}`, { method: 'DELETE' });
        if (response.ok) {
            const sheet = tableData.sheets[currentSheet];
            sheet.columns.splice(index, 1);
            sheet.rows.forEach(row => row.splice(index, 1));
            renderTable();
        }
    } catch (error) {
        console.error('Error deleting column:', error);
    }
}

async function addRow(count = 1) {
    try {
        const sheet = tableData.sheets[currentSheet];
        const rowsToAdd = [];

        for (let i = 0; i < count; i++) {
            rowsToAdd.push(new Array(sheet.columns.length).fill(''));
        }

        // Add all rows at once via API
        for (let i = 0; i < count; i++) {
            const response = await fetch('/api/rows', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sheetIndex: currentSheet })
            });
            if (response.ok) {
                sheet.rows.push(new Array(sheet.columns.length).fill(''));
            }
        }

        const newRowIndex = sheet.rows.length - 1;
        renderTable();

        // Scroll to and focus on the first new row
        setTimeout(() => {
            const table = document.getElementById('dataTable');
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            const newRow = rows[newRowIndex - count + 1]; // First of the new rows

            if (newRow) {
                // Scroll the row into view
                newRow.scrollIntoView({ behavior: 'smooth', block: 'center' });

                // Focus on the first input/textarea in the new row
                const firstInput = newRow.querySelector('td:not(.row-number) input, td:not(.row-number) textarea');
                if (firstInput) {
                    firstInput.focus();
                }
            }
        }, 100);

        if (count > 1) {
            showToast(`Added ${count} rows`, 'success');
        }
    } catch (error) {
        console.error('Error adding row:', error);
    }
}

async function addRowWithPrompt() {
    const count = prompt('How many rows do you want to add?', '1');
    if (count === null) return; // User cancelled

    const numRows = parseInt(count);
    if (isNaN(numRows) || numRows < 1) {
        showToast('Please enter a valid number', 'warning');
        return;
    }

    if (numRows > 100) {
        if (!confirm(`Are you sure you want to add ${numRows} rows? This might take a moment.`)) {
            return;
        }
    }

    await addRow(numRows);
}

async function deleteRow(index) {
    if (!confirm('Delete this row?')) return;

    try {
        const response = await fetch(`/api/rows/${currentSheet}/${index}`, { method: 'DELETE' });
        if (response.ok) {
            tableData.sheets[currentSheet].rows.splice(index, 1);
            renderTable();
        }
    } catch (error) {
        console.error('Error deleting row:', error);
    }
}

// Helper function to reindex cell styles and merged cells after row deletion
function reindexCellStylesAfterRowDeletion(sheet, deletedRowIndices) {
    if (!sheet.cellStyles) return;

    const newCellStyles = {};
    const newMergedCells = {};

    // Sort deleted indices for easier checking
    const sortedDeleted = [...deletedRowIndices].sort((a, b) => a - b);

    // Process each cell style
    Object.keys(sheet.cellStyles).forEach(key => {
        const [oldRow, col] = key.split('-').map(Number);

        // Skip if this row was deleted
        if (sortedDeleted.includes(oldRow)) {
            return;
        }

        // Calculate how many rows were deleted before this row
        const rowsDeletedBefore = sortedDeleted.filter(idx => idx < oldRow).length;
        const newRow = oldRow - rowsDeletedBefore;

        // Store with new key
        newCellStyles[`${newRow}-${col}`] = sheet.cellStyles[key];
    });

    // Process merged cells if they exist
    if (sheet.mergedCells) {
        Object.keys(sheet.mergedCells).forEach(key => {
            const [oldRow, col] = key.split('-').map(Number);

            // Skip if this row was deleted
            if (sortedDeleted.includes(oldRow)) {
                return;
            }

            // Calculate how many rows were deleted before this row
            const rowsDeletedBefore = sortedDeleted.filter(idx => idx < oldRow).length;
            const newRow = oldRow - rowsDeletedBefore;

            // Store with new key
            newMergedCells[`${newRow}-${col}`] = sheet.mergedCells[key];
        });

        sheet.mergedCells = newMergedCells;
    }

    sheet.cellStyles = newCellStyles;
}

async function deleteEmptyRows() {
    const sheet = tableData.sheets[currentSheet];

    // Find all empty rows (rows where all cells are empty or whitespace)
    const emptyRowIndices = [];
    sheet.rows.forEach((row, index) => {
        const isEmpty = row.every(cell => !cell || cell.trim() === '');
        if (isEmpty) {
            emptyRowIndices.push(index);
        }
    });

    if (emptyRowIndices.length === 0) {
        showToast('No empty rows found', 'info');
        return;
    }

    if (!confirm(`Delete ${emptyRowIndices.length} empty row${emptyRowIndices.length !== 1 ? 's' : ''}?`)) {
        return;
    }

    try {
        // Delete rows in reverse order to maintain correct indices
        for (let i = emptyRowIndices.length - 1; i >= 0; i--) {
            const rowIndex = emptyRowIndices[i];
            const response = await fetch(`/api/rows/${currentSheet}/${rowIndex}`, { method: 'DELETE' });
            if (response.ok) {
                sheet.rows.splice(rowIndex, 1);
            }
        }

        // Reindex cell styles and merged cells after deletion
        reindexCellStylesAfterRowDeletion(sheet, emptyRowIndices);

        renderTable();
        showToast(`Deleted ${emptyRowIndices.length} empty row${emptyRowIndices.length !== 1 ? 's' : ''}`, 'success');
    } catch (error) {
        console.error('Error deleting empty rows:', error);
        showToast('Error deleting empty rows', 'error');
    }
}

function updateCell(rowIndex, colIndex, value) {
    const sheet = tableData.sheets[currentSheet];
    if (!sheet.cellStyles) {
        sheet.cellStyles = {};
    }

    // Store value - ensure line breaks are preserved
    sheet.rows[rowIndex][colIndex] = value;

    // Apply markdown-style formatting to the cell
    applyMarkdownFormatting(rowIndex, colIndex, value);

    // Auto-save after a short delay to preserve changes
    clearTimeout(window.autoSaveTimeout);
    window.autoSaveTimeout = setTimeout(() => {
        saveData();
    }, 1000);
}

/**
 * Apply markdown formatting to a cell
 * 
 * IMPORTANT: When adding new markdown syntax:
 * 1. Add the detection pattern here in checkHasMarkdown function
 * 2. Add the parsing logic in parseMarkdown() function
 * 3. Update the Markdown Guide modal in templates/index.html
 * 4. Add CSS styling if needed in static/style.css
 * 
 * Note: renderTable() automatically calls applyMarkdownFormatting(), so no update needed there.
 */
function checkHasMarkdown(value) {
    if (!value && value !== 0) return false;
    const str = String(value);
    return (
        str.includes('||') ||
        str.includes('[[') ||
        str.includes('**') ||
        str.includes('__') ||
        str.includes('@@') ||
        str.includes('##') ||
        str.includes('..') ||
        str.includes('```') ||
        str.includes('`') ||
        str.includes('~~') ||
        str.includes('==') ||
        str.includes('!!') ||
        str.includes('??') ||
        str.includes('^') ||
        str.includes('~') ||
        str.includes('{fg:') ||
        str.includes('{bg:') ||
        str.includes('{link:') ||
        str.includes('{{') ||
        str.includes('\n- ') ||
        str.includes('\n-- ') ||
        str.trim().startsWith('- ') ||
        str.trim().startsWith('-- ') ||
        str.match(/(?:^|\n)Table\*\d+/i) ||
        str.trim().startsWith('|') ||
        str.includes('\\(') ||
        str.match(/^-{5,}$/m) ||
        (str.includes('|') && str.split('|').length >= 2)
    );
}

function applyMarkdownFormatting(rowIndex, colIndex, value, inputElement = null) {
    let cell;

    if (inputElement) {
        cell = inputElement.closest('td');
    } else {
        // Find the cell element (fallback for single updates)
        const table = document.getElementById('dataTable');
        if (!table) return;

        const rows = table.querySelectorAll('tbody tr');
        if (!rows[rowIndex]) return;

        const cells = rows[rowIndex].querySelectorAll('td:not(.row-number)');
        if (!cells[colIndex]) return;

        cell = cells[colIndex];
        inputElement = cell.querySelector('input, textarea');
    }

    if (!inputElement) return;

    // Parse markdown-style formatting
    const hasMarkdown = checkHasMarkdown(value);

    // Remove existing preview
    const existingPreview = cell.querySelector('.markdown-preview');
    if (existingPreview) {
        existingPreview.remove();
    }

    if (hasMarkdown) {
        // Store the formatted HTML in a data attribute
        const formattedHTML = parseMarkdown(value);
        inputElement.dataset.formattedHtml = formattedHTML;

        // Apply visual indicator
        inputElement.classList.add('has-markdown');

        // Create preview overlay
        const preview = document.createElement('div');
        preview.className = 'markdown-preview';
        preview.innerHTML = formattedHTML;
        preview.style.whiteSpace = 'pre-wrap'; // Preserve newlines and spaces

        // Copy styles from input/textarea (use inline styles to avoid reflows)
        preview.style.color = inputElement.style.color;
        preview.style.fontFamily = inputElement.style.fontFamily;
        preview.style.fontSize = inputElement.style.fontSize;
        preview.style.fontWeight = inputElement.style.fontWeight;
        preview.style.fontStyle = inputElement.style.fontStyle;
        preview.style.textAlign = inputElement.style.textAlign;

        // Copy background from cell
        preview.style.backgroundColor = cell.style.backgroundColor;

        cell.style.position = 'relative';
        cell.appendChild(preview);
    } else {
        delete inputElement.dataset.formattedHtml;
        inputElement.classList.remove('has-markdown');
    }
}

/* ----------  COMMA-TABLE → CSS-GRID  ---------- */
function parseCommaTable(cols, text, borderColor, borderWidth) {
    const items = text.split(',').map(c => c.trim());

    let gridStyle = `--cols:${cols};`;

    // Explicitly calculate border style to ensure it applies
    const bColor = borderColor || '#ced4da';
    const bWidth = borderWidth || '1px';
    const cellStyle = `border: ${bWidth} solid ${bColor} !important;`;

    let html = `<div class="md-grid" style="${gridStyle}">`;
    items.forEach((item, i) => {
        // Skip empty last item if it's just a trailing comma
        if (i === items.length - 1 && item === '') return;

        html += `<div class="md-cell" style="${cellStyle}">${parseMarkdownInline(item)}</div>`;
    });
    html += '</div>';
    return html;
}

/* ----------  PIPE-TABLE → CSS-GRID  ---------- */
function parseGridTable(lines) {
    const rows = lines.map(l =>
        l.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim()));
    const cols = rows[0].length;

    // Process each cell and check for alignment markers
    const grid = rows.map(r =>
        r.map(c => {
            let align = 'left';
            let content = c;

            // Check for center alignment :text:
            if (content.startsWith(':') && content.endsWith(':') && content.length > 2) {
                align = 'center';
                content = content.slice(1, -1).trim();
            }
            // Check for right alignment text:
            else if (content.endsWith(':') && !content.startsWith(':')) {
                align = 'right';
                content = content.slice(0, -1).trim();
            }

            return {
                content: parseMarkdownInline(content),
                align: align
            };
        })
    );

    /*  build a single <div> that looks like a table  */
    let html = `<div class="md-grid" style="--cols:${cols}">`;
    grid.forEach((row, i) => {
        row.forEach(cell => {
            const alignStyle = cell.align !== 'left' ? ` style="text-align: ${cell.align}"` : '';
            // Check if cell content is only "-" (empty cell marker)
            const isEmpty = cell.content.trim() === '-';
            const emptyClass = isEmpty ? ' md-empty' : '';
            html += `<div class="md-cell ${i ? '' : 'md-header'}${emptyClass}"${alignStyle}>${cell.content}</div>`;
        });
    });
    html += '</div>';
    return html;
}

/*  inline parser for table cells - supports all markdown except lists  */
function parseMarkdownInline(text) {
    let formatted = text;

    // Math: \( ... \) -> KaTeX (process first to avoid conflicts)
    if (window.katex) {
        formatted = formatted.replace(/\\\((.*?)\\\)/g, (match, math) => {
            try {
                return katex.renderToString(math, {
                    throwOnError: false,
                    displayMode: false
                });
            } catch (e) {
                return match;
            }
        });
    }

    // Links: {link:url}text{/} -> <a href="url">text</a>
    formatted = formatted.replace(/\{link:([^}]+)\}(.+?)\{\/\}/g, (match, url, text) => {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
    });

    // Custom colors: {fg:color;bg:color}text{/} or {fg:color}text{/} or {bg:color}text{/}
    formatted = formatted.replace(/\{((?:fg:[^;}\s]+)?(?:;)?(?:bg:[^;}\s]+)?)\}(.+?)\{\/\}/g, (match, styles, text) => {
        const styleObj = {};
        const parts = styles.split(';').filter(p => p.trim());
        let hasBg = false;
        parts.forEach(part => {
            const [key, value] = part.split(':').map(s => s.trim());
            if (key === 'fg') styleObj.color = value;
            if (key === 'bg') {
                styleObj.backgroundColor = value;
                hasBg = true;
            }
        });
        // Only add padding and border-radius if there's a background
        if (hasBg) {
            styleObj.padding = '1px 6px';
            styleObj.borderRadius = '4px';
            styleObj.display = 'inline-block';
            styleObj.verticalAlign = 'baseline';
            styleObj.marginTop = '-1px';
        }
        // Only use extra spacing if there's a background color
        styleObj.lineHeight = hasBg ? '1.3' : '1.3';
        styleObj.boxDecorationBreak = 'clone';
        styleObj.WebkitBoxDecorationBreak = 'clone';
        const styleStr = Object.entries(styleObj).map(([k, v]) => {
            const cssKey = k.replace(/([A-Z])/g, '-$1').toLowerCase();
            return `${cssKey}: ${v}`;
        }).join('; ');
        return `<span style="${styleStr}">${text}</span>`;
    });

    // Heading: ##text## -> larger text
    formatted = formatted.replace(/##(.+?)##/g, '<span style="font-size: 1.3em; font-weight: 600;">$1</span>');

    // Small text: ..text.. -> smaller text
    formatted = formatted.replace(/\.\.(.+?)\.\./g, '<span style="font-size: 0.75em;">$1</span>');

    // Horizontal separator: ----- (5 or more dashes on a line) -> separator div
    formatted = formatted.replace(/^-{5,}$/gm, '<div class="md-separator"></div>');

    // Bold: **text** -> <strong>text</strong>
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic: @@text@@ -> <em>text</em>
    formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

    // Underline: __text__ -> <u>text</u>
    formatted = formatted.replace(/__(.+?)__/g, '<u>$1</u>');

    // Strikethrough: ~~text~~ -> <del>text</del>
    formatted = formatted.replace(/~~(.+?)~~/g, '<del>$1</del>');

    // Superscript: ^text^ -> <sup>text</sup>
    formatted = formatted.replace(/\^(.+?)\^/g, '<sup>$1</sup>');

    // Subscript: ~text~ -> <sub>text</sub>
    formatted = formatted.replace(/~(.+?)~/g, '<sub>$1</sub>');

    // Inline code: `text` -> <code>text</code>
    formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');

    // Highlight: ==text== -> <mark>text</mark>
    formatted = formatted.replace(/==(.+?)==/g, '<mark>$1</mark>');

    // Correct Answer: [[text]] -> text with hidden green highlight
    formatted = formatted.replace(/\[\[(.+?)\]\]/g, '<span class="correct-answer">$1</span>');

    return formatted;
}

/**
 * Parse markdown syntax and convert to HTML
 */
function parseMarkdown(text) {
    if (!text) return '';

    // Table*N detection (allow text before table)
    const tableRegex = /(?:^|\n)Table\*(\d+)(?:\s*_\s*([^\s\n,]+))?(?:\s*_\s*([^\s\n,]+))?(?:[\n\s,]+)([\s\S]*)/i;
    const tableMatch = text.match(tableRegex);
    if (tableMatch) {
        // Render text before the table
        let preText = '';
        if (tableMatch.index > 0) {
            const textBefore = text.substring(0, tableMatch.index);
            preText = oldParseMarkdownBody(textBefore.split('\n'));
        }

        const cols = parseInt(tableMatch[1]);
        const param1 = tableMatch[2];
        const param2 = tableMatch[3];
        const content = tableMatch[4];

        let borderColor = null;
        let borderWidth = null;

        // Helper to check if string is a size (ends in px, em, rem, %)
        const isSize = (s) => s && /^\d+(?:px|em|rem|%)$/i.test(s);

        if (param1) {
            if (isSize(param1)) borderWidth = param1;
            else borderColor = param1;
        }
        if (param2) {
            if (isSize(param2)) borderWidth = param2;
            else if (!borderColor) borderColor = param2;
        }

        // Check for explicit table end: Table*end
        // Only consume the marker and optional immediate newline, preserving subsequent empty lines
        const endRegex = /(?:^|\n)Table\*end[ \t]*(?:\n)?/i;
        const endMatch = content.match(endRegex);

        if (endMatch) {
            const splitIndex = endMatch.index;
            const currentTableContent = content.substring(0, splitIndex);
            // The remaining content starts AFTER the "Table*end" marker
            const remainingContent = content.substring(splitIndex + endMatch[0].length);

            const currentTableHtml = parseCommaTable(cols, currentTableContent, borderColor, borderWidth);

            // Recursively parse the rest
            return preText + currentTableHtml + parseMarkdown(remainingContent);
        }

        // Check if there's another table definition in the content (fallback)
        const nextTableMatch = content.match(tableRegex);
        if (nextTableMatch) {
            const splitIndex = nextTableMatch.index;
            const currentTableContent = content.substring(0, splitIndex);
            const remainingContent = content.substring(splitIndex);

            const currentTableHtml = parseCommaTable(cols, currentTableContent, borderColor, borderWidth);

            return preText + currentTableHtml + parseMarkdown(remainingContent);
        }

        return preText + parseCommaTable(cols, content, borderColor, borderWidth);
    }

    /* -----  GRID-TABLE DETECTION  ----- */
    const lines = text.split('\n');

    // Detect table lines: either starts with | or contains | (for inline format like "Name | Age")
    const isTableLine = (line) => {
        const trimmed = line.trim();
        return trimmed.startsWith('|') || (trimmed.includes('|') && trimmed.split('|').length >= 2);
    };

    const hasGrid = lines.some(l => isTableLine(l));

    if (hasGrid) {
        const blocks = [];
        let cur = [], inGrid = false;

        lines.forEach(l => {
            const isGrid = isTableLine(l);
            if (isGrid !== inGrid) {
                if (cur.length) blocks.push({ grid: inGrid, lines: cur });
                cur = [];
                inGrid = isGrid;
            }
            cur.push(l);
        });
        if (cur.length) blocks.push({ grid: inGrid, lines: cur });

        return blocks.map(b =>
            b.grid ? parseGridTable(b.lines) : oldParseMarkdownBody(b.lines)
        ).join('\n');
    }

    // If no grid table, process as normal markdown
    return oldParseMarkdownBody(lines);
}

function oldParseMarkdownBody(lines) {
    /* copy the *body* of the existing parser (bold, italic, lists …)
       but skip the table-splitting logic we just added. */
    let txt = lines.join('\n');

    // Handle code blocks first (multiline)
    let inCodeBlock = false;
    const codeLines = txt.split('\n');
    const formattedLines = codeLines.map(line => {
        let formatted = line;

        // Code block: ```text``` -> <code>text</code>
        if (formatted.trim() === '```') {
            inCodeBlock = !inCodeBlock;
            return ''; // Remove the ``` markers
        }

        if (inCodeBlock) {
            return `<code>${formatted}</code>`;
        }

        // Math: \( ... \) -> KaTeX (process first to avoid conflicts)
        if (window.katex) {
            formatted = formatted.replace(/\\\((.*?)\\\)/g, (match, math) => {
                try {
                    return katex.renderToString(math, {
                        throwOnError: false,
                        displayMode: false
                    });
                } catch (e) {
                    return match;
                }
            });
        }

        // Links: {link:url}text{/} -> <a href="url">text</a>
        formatted = formatted.replace(/\{link:([^}]+)\}(.+?)\{\/\}/g, (match, url, text) => {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
        });

        // Custom colors: {fg:color;bg:color}text{/} or {fg:color}text{/} or {bg:color}text{/}
        formatted = formatted.replace(/\{((?:fg:[^;}\s]+)?(?:;)?(?:bg:[^;}\s]+)?)\}(.+?)\{\/\}/g, (match, styles, text) => {
            const styleObj = {};
            const parts = styles.split(';').filter(p => p.trim());
            let hasBg = false;
            parts.forEach(part => {
                const [key, value] = part.split(':').map(s => s.trim());
                if (key === 'fg') styleObj.color = value;
                if (key === 'bg') {
                    styleObj.backgroundColor = value;
                    hasBg = true;
                }
            });
            // Only add padding and border-radius if there's a background
            if (hasBg) {
                styleObj.padding = '1px 6px';
                styleObj.borderRadius = '4px';
                styleObj.display = 'inline-block';
                styleObj.verticalAlign = 'baseline';
                styleObj.marginTop = '-1px';
            }
            // Only use extra spacing if there's a background color
            styleObj.lineHeight = hasBg ? '1.3' : '1.3';
            styleObj.boxDecorationBreak = 'clone';
            styleObj.WebkitBoxDecorationBreak = 'clone';
            const styleStr = Object.entries(styleObj).map(([k, v]) => {
                const cssKey = k.replace(/([A-Z])/g, '-$1').toLowerCase();
                return `${cssKey}: ${v}`;
            }).join('; ');
            return `<span style="${styleStr}">${text}</span>`;
        });

        // Heading: ##text## -> larger text
        formatted = formatted.replace(/##(.+?)##/g, '<span style="font-size: 1.3em; font-weight: 600;">$1</span>');

        // Small text: ..text.. -> smaller text
        formatted = formatted.replace(/\.\.(.+?)\.\./g, '<span style="font-size: 0.75em;">$1</span>');

        // Horizontal separator: ----- (5 or more dashes on a line) -> separator div
        formatted = formatted.replace(/^-{5,}$/gm, '<div class="md-separator"></div>');

        // Bold: **text** -> <strong>text</strong>
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic: @@text@@ -> <em>text</em>
        formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

        // Underline: __text__ -> <u>text</u>
        formatted = formatted.replace(/__(.+?)__/g, '<u>$1</u>');

        // Strikethrough: ~~text~~ -> <del>text</del>
        formatted = formatted.replace(/~~(.+?)~~/g, '<del>$1</del>');

        // Superscript: ^text^ -> <sup>text</sup>
        formatted = formatted.replace(/\^(.+?)\^/g, '<sup>$1</sup>');

        // Subscript: ~text~ -> <sub>text</sub>
        formatted = formatted.replace(/~(.+?)~/g, '<sub>$1</sub>');

        // Sublist: -- item -> ◦ item with more indent (white circle)
        if (formatted.trim().startsWith('-- ')) {
            const content = formatted.replace(/^(\s*)-- (.+)$/, '$2');
            formatted = formatted.replace(/^(\s*)-- .+$/, '$1<span style="display: inline-flex; align-items: baseline; width: 100%; margin-left: 1em;"><span style="margin-right: 0.5em; flex-shrink: 0; position: relative; top: 0.1em;">◦</span><span style="flex: 1;">◦CONTENT◦</span></span>');
            formatted = formatted.replace('◦CONTENT◦', content);
        }
        // Bullet list: - item -> • item with hanging indent (black circle)
        else if (formatted.trim().startsWith('- ')) {
            const content = formatted.replace(/^(\s*)- (.+)$/, '$2');
            formatted = formatted.replace(/^(\s*)- .+$/, '$1<span style="display: inline-flex; align-items: baseline; width: 100%;"><span style="margin-right: 0.5em; flex-shrink: 0; position: relative; top: 0.1em;">•</span><span style="flex: 1;">•CONTENT•</span></span>');
            formatted = formatted.replace('•CONTENT•', content);
        }

        // Numbered list: 1. item -> 1. item with hanging indent
        if (/^\d+\.\s/.test(formatted.trim())) {
            const match = formatted.match(/^(\s*)(\d+\.\s)(.+)$/);
            if (match) {
                const spaces = match[1];
                const number = match[2];
                const content = match[3];
                formatted = `${spaces}<span style="display: inline-flex; align-items: baseline; width: 100%;"><span style="margin-right: 0.5em; flex-shrink: 0;">${number}</span><span style="flex: 1;">NUMCONTENT</span></span>`;
                formatted = formatted.replace('NUMCONTENT', content);
            }
        }

        // Inline code: `text` -> <code>text</code>
        formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');

        // Highlight: ==text== -> <mark>text</mark>
        formatted = formatted.replace(/==(.+?)==/g, '<mark>$1</mark>');

        // Red highlight: !!text!! -> red background with white text
        formatted = formatted.replace(/!!(.+?)!!/g, '<span style="background: #ff0000; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline-block; vertical-align: baseline; margin-top: -1px; line-height: 1.3;">$1</span>');

        // Blue highlight: ??text?? -> blue background with white text
        formatted = formatted.replace(/\?\?(.+?)\?\?/g, '<span style="background: #0000ff; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline-block; vertical-align: baseline; margin-top: -1px; line-height: 1.3;">$1</span>');

        // Collapsible text: {{text}} -> hidden text with toggle button
        formatted = formatted.replace(/\{\{(.+?)\}\}/g, (match, content) => {
            const id = 'collapse-' + Math.random().toString(36).substr(2, 9);
            return `<span class="collapsible-wrapper">
                <button class="collapsible-toggle" onclick="toggleCollapsible('${id}')" title="Click to show/hide">👁️</button>
                <span id="${id}" class="collapsible-content" style="display: none;">${content}</span>
            </span>`;
        });

        // Correct Answer: [[text]] -> text with hidden green highlight
        formatted = formatted.replace(/\[\[(.+?)\]\]/g, '<span class="correct-answer">$1</span>');

        return formatted;
    });

    return formattedLines.reduce((acc, line, i) => {
        if (i === 0) return line;
        const prev = formattedLines[i - 1];
        // Check for separator to avoid double line breaks (newline + block element break)
        const isSeparator = line.includes('class="md-separator"');
        const prevIsSeparator = prev.includes('class="md-separator"');

        if (isSeparator || prevIsSeparator) {
            return acc + line;
        }
        return acc + '\n' + line;
    }, '');
}

function getCellKey(rowIndex, colIndex) {
    return `${rowIndex}-${colIndex}`;
}

function getCellStyle(rowIndex, colIndex) {
    const sheet = tableData.sheets[currentSheet];
    if (!sheet.cellStyles) {
        sheet.cellStyles = {};
    }
    const key = getCellKey(rowIndex, colIndex);
    const style = sheet.cellStyles[key] || {};
    console.log('Get cell style:', key, style);
    return style;
}

function setCellStyle(rowIndex, colIndex, styleProperty, value) {
    const sheet = tableData.sheets[currentSheet];
    if (!sheet.cellStyles) {
        sheet.cellStyles = {};
    }
    const key = getCellKey(rowIndex, colIndex);
    if (!sheet.cellStyles[key]) {
        sheet.cellStyles[key] = {};
    }
    sheet.cellStyles[key][styleProperty] = value;
}

function showCellContextMenu(e, rowIndex, colIndex, inputElement) {
    e.preventDefault();

    contextMenuCell = { rowIndex, colIndex, inputElement };

    const menu = document.getElementById('cellContextMenu');
    const style = getCellStyle(rowIndex, colIndex);

    // Update checkmarks
    document.getElementById('ctxBold').classList.toggle('checked', style.bold === true);
    document.getElementById('ctxItalic').classList.toggle('checked', style.italic === true);
    document.getElementById('ctxCenter').classList.toggle('checked', style.center === true);

    // Position menu
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    menu.classList.add('show');
}

function toggleCellBold() {
    if (!contextMenuCell) return;

    const { rowIndex, colIndex, inputElement } = contextMenuCell;
    const style = getCellStyle(rowIndex, colIndex);
    const newValue = !style.bold;

    // Apply to multiple cells if selected
    if (selectedCells.length > 0) {
        selectedCells.forEach(cell => {
            const cellInput = cell.td.querySelector('input, textarea');
            setCellStyle(cell.row, cell.col, 'bold', newValue);
            if (cellInput) {
                cellInput.style.fontWeight = newValue ? 'bold' : 'normal';
                // Update markdown preview if exists
                const preview = cell.td.querySelector('.markdown-preview');
                if (preview) {
                    preview.style.fontWeight = newValue ? 'bold' : 'normal';
                }
            }
        });
        showToast(`Bold ${newValue ? 'applied' : 'removed'} for ${selectedCells.length} cells`, 'success');
    } else {
        // Apply to single cell
        setCellStyle(rowIndex, colIndex, 'bold', newValue);
        inputElement.style.fontWeight = newValue ? 'bold' : 'normal';
        // Update markdown preview if exists
        const cell = inputElement.closest('td');
        const preview = cell ? cell.querySelector('.markdown-preview') : null;
        if (preview) {
            preview.style.fontWeight = newValue ? 'bold' : 'normal';
        }
    }

    document.getElementById('ctxBold').classList.toggle('checked', newValue);
}

function toggleCellItalic() {
    if (!contextMenuCell) return;

    const { rowIndex, colIndex, inputElement } = contextMenuCell;
    const style = getCellStyle(rowIndex, colIndex);
    const newValue = !style.italic;

    // Apply to multiple cells if selected
    if (selectedCells.length > 0) {
        selectedCells.forEach(cell => {
            const cellInput = cell.td.querySelector('input, textarea');
            setCellStyle(cell.row, cell.col, 'italic', newValue);
            if (cellInput) {
                cellInput.style.fontStyle = newValue ? 'italic' : 'normal';
                // Update markdown preview if exists
                const preview = cell.td.querySelector('.markdown-preview');
                if (preview) {
                    preview.style.fontStyle = newValue ? 'italic' : 'normal';
                }
            }
        });
        showToast(`Italic ${newValue ? 'applied' : 'removed'} for ${selectedCells.length} cells`, 'success');
    } else {
        // Apply to single cell
        setCellStyle(rowIndex, colIndex, 'italic', newValue);
        inputElement.style.fontStyle = newValue ? 'italic' : 'normal';
        // Update markdown preview if exists
        const cell = inputElement.closest('td');
        const preview = cell ? cell.querySelector('.markdown-preview') : null;
        if (preview) {
            preview.style.fontStyle = newValue ? 'italic' : 'normal';
        }
    }

    document.getElementById('ctxItalic').classList.toggle('checked', newValue);
}

function toggleCellCenter() {
    if (!contextMenuCell) return;

    const { rowIndex, colIndex, inputElement } = contextMenuCell;
    const style = getCellStyle(rowIndex, colIndex);
    const newValue = !style.center;

    // Apply to multiple cells if selected
    if (selectedCells.length > 0) {
        selectedCells.forEach(cell => {
            const cellInput = cell.td.querySelector('input, textarea');
            setCellStyle(cell.row, cell.col, 'center', newValue);
            if (cellInput) {
                cellInput.style.textAlign = newValue ? 'center' : 'left';
            }
        });
        showToast(`Center align ${newValue ? 'applied' : 'removed'} for ${selectedCells.length} cells`, 'success');
    } else {
        // Apply to single cell
        setCellStyle(rowIndex, colIndex, 'center', newValue);
        inputElement.style.textAlign = newValue ? 'center' : 'left';
    }

    document.getElementById('ctxCenter').classList.toggle('checked', newValue);
}

// Border options will be handled by unified border modal

function showCellContextMenu(e, rowIndex, colIndex, inputElement, tdElement) {
    e.preventDefault();

    contextMenuCell = { rowIndex, colIndex, inputElement, tdElement };

    const menu = document.getElementById('cellContextMenu');
    const style = getCellStyle(rowIndex, colIndex);
    const mergeInfo = getCellMerge(rowIndex, colIndex);

    // Update checkmarks
    document.getElementById('ctxBold').classList.toggle('checked', style.bold === true);
    document.getElementById('ctxItalic').classList.toggle('checked', style.italic === true);
    document.getElementById('ctxCenter').classList.toggle('checked', style.center === true);

    // Show/hide merge options
    const isMerged = mergeInfo && (mergeInfo.colspan || mergeInfo.rowspan || mergeInfo.hidden);
    const showMerge = selectedCells.length >= 2;
    const showUnmerge = isMerged;

    document.getElementById('ctxMerge').style.display = showMerge ? 'flex' : 'none';
    document.getElementById('ctxUnmerge').style.display = showUnmerge ? 'flex' : 'none';

    // Hide the separator before merge options if both are hidden
    const mergeSeparators = document.querySelectorAll('.context-menu-separator');
    if (mergeSeparators.length >= 2) {
        mergeSeparators[1].style.display = (showMerge || showUnmerge) ? 'block' : 'none';
    }

    // Position menu with boundary detection
    menu.classList.add('show'); // Show first to get dimensions

    const menuRect = menu.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let left = e.pageX;
    let top = e.pageY;

    // Adjust horizontal position if menu would go off-screen
    if (left + menuRect.width > viewportWidth) {
        left = viewportWidth - menuRect.width - 10; // 10px margin
    }

    // Adjust vertical position if menu would go off-screen
    if (top + menuRect.height > viewportHeight) {
        top = viewportHeight - menuRect.height - 10; // 10px margin
    }

    // Ensure menu doesn't go above or to the left of viewport
    left = Math.max(10, left);
    top = Math.max(10, top);

    menu.style.left = left + 'px';
    menu.style.top = top + 'px';
}

function closeCellContextMenu() {
    document.getElementById('cellContextMenu').classList.remove('show');
    contextMenuCell = null;
}

function startCellSelection(rowIndex, colIndex, td) {
    isSelecting = true;
    clearSelection();
    selectedCells = [{ row: rowIndex, col: colIndex, td: td }];
    td.classList.add('selected-cell');
    showToast('Hold Shift and drag to select more cells', 'info');
}

function addToSelection(rowIndex, colIndex, td) {
    const exists = selectedCells.find(c => c.row === rowIndex && c.col === colIndex);
    if (!exists) {
        selectedCells.push({ row: rowIndex, col: colIndex, td: td });
        td.classList.add('selected-cell');
    }
}

function clearSelection() {
    selectedCells.forEach(cell => {
        if (cell.td) cell.td.classList.remove('selected-cell');
    });
    selectedCells = [];
}

document.addEventListener('mouseup', () => {
    isSelecting = false;
});

function getCellMerge(rowIndex, colIndex) {
    const sheet = tableData.sheets[currentSheet];
    if (!sheet.mergedCells) return null;
    return sheet.mergedCells[`${rowIndex}-${colIndex}`];
}

function setCellMerge(rowIndex, colIndex, info) {
    const sheet = tableData.sheets[currentSheet];
    if (!sheet.mergedCells) sheet.mergedCells = {};
    sheet.mergedCells[`${rowIndex}-${colIndex}`] = info;
}

function mergeCells() {
    if (selectedCells.length < 2) {
        showToast('Select at least 2 cells to merge', 'error');
        return;
    }

    let minRow = Math.min(...selectedCells.map(c => c.row));
    let maxRow = Math.max(...selectedCells.map(c => c.row));
    let minCol = Math.min(...selectedCells.map(c => c.col));
    let maxCol = Math.max(...selectedCells.map(c => c.col));

    const colspan = maxCol - minCol + 1;
    const rowspan = maxRow - minRow + 1;

    // Set main cell
    setCellMerge(minRow, minCol, { colspan, rowspan });

    // Hide other cells
    for (let r = minRow; r <= maxRow; r++) {
        for (let c = minCol; c <= maxCol; c++) {
            if (r !== minRow || c !== minCol) {
                setCellMerge(r, c, { hidden: true, mainRow: minRow, mainCol: minCol });
            }
        }
    }

    clearSelection();
    renderTable();
    closeCellContextMenu();
    showToast('Cells merged', 'success');
}

function unmergeCell() {
    if (!contextMenuCell) return;

    let { rowIndex, colIndex } = contextMenuCell;
    let mergeInfo = getCellMerge(rowIndex, colIndex);

    if (!mergeInfo) return;

    // Find main cell
    if (mergeInfo.hidden) {
        rowIndex = mergeInfo.mainRow;
        colIndex = mergeInfo.mainCol;
        mergeInfo = getCellMerge(rowIndex, colIndex);
    }

    if (!mergeInfo) return;

    const colspan = mergeInfo.colspan || 1;
    const rowspan = mergeInfo.rowspan || 1;

    // Remove all merge info
    const sheet = tableData.sheets[currentSheet];
    for (let r = rowIndex; r < rowIndex + rowspan; r++) {
        for (let c = colIndex; c < colIndex + colspan; c++) {
            delete sheet.mergedCells[`${r}-${c}`];
        }
    }

    renderTable();
    closeCellContextMenu();
    showToast('Cell unmerged', 'success');
}

function showUnifiedColorPicker() {
    if (!contextMenuCell) return;
    showUnifiedColorPickerModal();
    closeCellContextMenu();
}

// Unified color picker state
let currentColorType = 'background'; // 'background' or 'text'
let selectedBgColor = null;
let selectedTextColor = null;
let colorPickerElements = { tdElement: null, inputElement: null };

function showUnifiedColorPickerModal() {
    const { rowIndex, colIndex, tdElement, inputElement } = contextMenuCell;

    // Store elements for later use
    colorPickerElements = { tdElement, inputElement };

    // Get current colors
    const currentStyle = getCellStyle(rowIndex, colIndex);
    selectedBgColor = currentStyle.bgColor || tdElement.style.backgroundColor || '#ffffff';
    selectedTextColor = currentStyle.textColor || inputElement.style.color || '#000000';

    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'color-picker-overlay';
    overlay.id = 'unifiedColorPickerOverlay';

    // Create color picker popup
    const popup = document.createElement('div');
    popup.className = 'color-picker-popup';
    popup.id = 'unifiedColorPickerPopup';

    const title = document.createElement('h3');
    const cellCount = selectedCells.length > 0 ? selectedCells.length : 1;
    title.textContent = cellCount > 1 ? `Cell Colors (${cellCount} cells selected)` : 'Cell Colors';
    popup.appendChild(title);

    // Radio buttons for color type selection
    const radioContainer = document.createElement('div');
    radioContainer.className = 'color-type-selector';
    radioContainer.style.display = 'flex';
    radioContainer.style.gap = '15px';
    radioContainer.style.marginBottom = '15px';
    radioContainer.style.justifyContent = 'center';

    const bgRadioLabel = document.createElement('label');
    bgRadioLabel.style.display = 'flex';
    bgRadioLabel.style.alignItems = 'center';
    bgRadioLabel.style.gap = '5px';
    bgRadioLabel.style.cursor = 'pointer';
    bgRadioLabel.innerHTML = '<input type="radio" name="colorType" value="background" checked> Background';

    const textRadioLabel = document.createElement('label');
    textRadioLabel.style.display = 'flex';
    textRadioLabel.style.alignItems = 'center';
    textRadioLabel.style.gap = '5px';
    textRadioLabel.style.cursor = 'pointer';
    textRadioLabel.innerHTML = '<input type="radio" name="colorType" value="text"> Text';

    radioContainer.appendChild(bgRadioLabel);
    radioContainer.appendChild(textRadioLabel);
    popup.appendChild(radioContainer);

    // Preview area
    const previewContainer = document.createElement('div');
    previewContainer.className = 'color-preview';
    previewContainer.style.margin = '15px 0';
    previewContainer.style.padding = '15px';
    previewContainer.style.borderRadius = '6px';
    previewContainer.style.border = '1px solid #ddd';
    previewContainer.style.backgroundColor = selectedBgColor;
    previewContainer.style.color = selectedTextColor;
    previewContainer.style.fontWeight = 'bold';
    previewContainer.style.textAlign = 'center';
    previewContainer.textContent = 'Preview Text';
    previewContainer.id = 'colorPreviewArea';
    popup.appendChild(previewContainer);

    // Preset colors
    const presetColors = [
        '#FFFFFF', '#F8F9FA', '#E9ECEF', '#DEE2E6', '#CED4DA', '#ADB5BD', '#6C757D', '#495057', '#343A40', '#212529',
        '#FFE5E5', '#FFB3B3', '#FF8080', '#FF4D4D', '#FF1A1A', '#E60000', '#B30000', '#800000', '#4D0000', '#1A0000',
        '#FFF4E5', '#FFE0B3', '#FFCC80', '#FFB84D', '#FFA31A', '#E68A00', '#B36B00', '#804D00', '#4D2E00', '#1A0F00',
        '#FFFBE5', '#FFF7B3', '#FFF380', '#FFEF4D', '#FFEB1A', '#E6D400', '#B3A500', '#807600', '#4D4700', '#1A1800',
        '#F0FFE5', '#D9FFB3', '#C2FF80', '#ABFF4D', '#94FF1A', '#7AE600', '#5FB300', '#448000', '#294D00', '#0F1A00',
        '#E5FFF4', '#B3FFE0', '#80FFCC', '#4DFFB8', '#1AFFA3', '#00E68A', '#00B36B', '#00804D', '#004D2E', '#001A0F',
        '#E5F9FF', '#B3EFFF', '#80E5FF', '#4DDBFF', '#1AD1FF', '#00BCE6', '#0093B3', '#006A80', '#00404D', '#00171A',
        '#E5F0FF', '#B3D9FF', '#80C2FF', '#4DABFF', '#1A94FF', '#007AE6', '#005FB3', '#004480', '#00294D', '#000F1A',
        '#F0E5FF', '#D9B3FF', '#C280FF', '#AB4DFF', '#941AFF', '#7A00E6', '#5F00B3', '#440080', '#29004D', '#0F001A',
        '#FFE5F9', '#FFB3EF', '#FF80E5', '#FF4DDB', '#FF1AD1', '#E600BC', '#B30093', '#80006A', '#4D0040', '#1A0017'
    ];

    const colorsGrid = document.createElement('div');
    colorsGrid.className = 'color-picker-grid';

    presetColors.forEach(color => {
        const colorSwatch = document.createElement('div');
        colorSwatch.className = 'color-swatch';
        colorSwatch.style.backgroundColor = color;
        colorSwatch.title = color;
        colorSwatch.onclick = () => selectColor(color);
        colorsGrid.appendChild(colorSwatch);
    });

    popup.appendChild(colorsGrid);

    // Custom color section
    const customSection = document.createElement('div');
    customSection.className = 'color-picker-custom';
    customSection.style.marginTop = '20px';
    customSection.style.paddingTop = '15px';
    customSection.style.borderTop = '1px solid #e0e0e0';

    const customLabel = document.createElement('span');
    customLabel.textContent = 'Custom Color:';
    customLabel.style.marginRight = '10px';

    const customInput = document.createElement('input');
    customInput.type = 'color';
    customInput.className = 'custom-color-input';
    customInput.id = 'customColorInput';
    customInput.value = rgbToHex(selectedBgColor); // Start with background color

    customInput.onchange = (e) => selectColor(e.target.value);

    const customBtn = document.createElement('button');
    customBtn.className = 'btn btn-primary';
    customBtn.textContent = 'Pick Custom';
    customBtn.style.marginLeft = '10px';
    customBtn.onclick = () => customInput.click();

    customSection.appendChild(customLabel);
    customSection.appendChild(customInput);
    customSection.appendChild(customBtn);

    popup.appendChild(customSection);

    // OK button
    const okBtn = document.createElement('button');
    okBtn.className = 'btn btn-primary';
    okBtn.textContent = 'OK';
    okBtn.style.marginTop = '20px';
    okBtn.style.width = '100%';
    okBtn.onclick = () => applyUnifiedColors(rowIndex, colIndex);

    popup.appendChild(okBtn);

    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'color-picker-close';
    closeBtn.textContent = '×';
    closeBtn.onclick = () => document.body.removeChild(overlay);

    popup.appendChild(closeBtn);
    overlay.appendChild(popup);
    document.body.appendChild(overlay);

    // Set up radio button event listeners
    const bgRadio = bgRadioLabel.querySelector('input');
    const textRadio = textRadioLabel.querySelector('input');

    bgRadio.addEventListener('change', updateColorPickerState);
    textRadio.addEventListener('change', updateColorPickerState);

    // Close on overlay click
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    };

    // Initialize the color picker state
    updateColorPickerState();
}

function updateColorPickerState() {
    const bgRadio = document.querySelector('input[name="colorType"][value="background"]');
    const textRadio = document.querySelector('input[name="colorType"][value="text"]');
    const customInput = document.getElementById('customColorInput');
    const previewArea = document.getElementById('colorPreviewArea');

    if (bgRadio && bgRadio.checked) {
        currentColorType = 'background';
        if (customInput) customInput.value = rgbToHex(selectedBgColor);
    } else if (textRadio && textRadio.checked) {
        currentColorType = 'text';
        if (customInput) customInput.value = rgbToHex(selectedTextColor);
    }

    // Update preview
    if (previewArea) {
        previewArea.style.backgroundColor = selectedBgColor;
        previewArea.style.color = selectedTextColor;
    }
}

function selectColor(color) {
    if (currentColorType === 'background') {
        selectedBgColor = color;
    } else {
        selectedTextColor = color;
    }

    updateColorPickerState();
}

function applyUnifiedColors(rowIndex, colIndex) {
    // Check if multiple cells are selected
    if (selectedCells.length > 0) {
        // Apply colors to all selected cells
        selectedCells.forEach(cell => {
            const cellTd = cell.td;
            const cellInput = cellTd.querySelector('input, textarea');

            // Apply background color
            setCellStyle(cell.row, cell.col, 'bgColor', selectedBgColor);
            cellTd.style.backgroundColor = selectedBgColor;

            // Apply text color
            if (cellInput) {
                setCellStyle(cell.row, cell.col, 'textColor', selectedTextColor);
                cellInput.style.color = selectedTextColor;
            }

            // Update markdown preview if exists
            const preview = cellTd.querySelector('.markdown-preview');
            if (preview) {
                preview.style.backgroundColor = selectedBgColor;
                preview.style.color = selectedTextColor;
            }
        });

        showToast(`Colors updated for ${selectedCells.length} cells`, 'success');
    } else {
        // Apply to single cell
        const { tdElement, inputElement } = colorPickerElements;

        // Apply background color
        setCellStyle(rowIndex, colIndex, 'bgColor', selectedBgColor);
        tdElement.style.backgroundColor = selectedBgColor;

        // Apply text color
        setCellStyle(rowIndex, colIndex, 'textColor', selectedTextColor);
        inputElement.style.color = selectedTextColor;

        // Update markdown preview if exists
        const preview = tdElement.querySelector('.markdown-preview');
        if (preview) {
            preview.style.backgroundColor = selectedBgColor;
            preview.style.color = selectedTextColor;
        }

        showToast('Colors updated', 'success');
    }

    // Close the picker

    const overlay = document.getElementById('unifiedColorPickerOverlay');

    if (overlay) {

        document.body.removeChild(overlay);

    }

}



// Unified border options modal

function showUnifiedBorderOptions() {

    if (!contextMenuCell) return;

    showUnifiedBorderOptionsModal();

    closeCellContextMenu();

}



// Unified border options state

let selectedBorderWidth = '1px';

let selectedBorderStyle = 'solid';

let selectedBorderColor = '#000000';



function showUnifiedBorderOptionsModal() {

    const { rowIndex, colIndex, tdElement } = contextMenuCell;

    // Store the cell info for later use since contextMenuCell will be null when button is clicked
    const cellInfo = { rowIndex, colIndex, tdElement };



    // Get current border settings

    const currentStyle = getCellStyle(rowIndex, colIndex);

    selectedBorderWidth = currentStyle.borderWidth || '1px';

    selectedBorderStyle = currentStyle.borderStyle || 'solid';

    selectedBorderColor = currentStyle.borderColor || '#000000';



    // Create modal overlay

    const overlay = document.createElement('div');

    overlay.className = 'color-picker-overlay';

    overlay.id = 'unifiedBorderOptionsOverlay';



    // Create border options popup

    const popup = document.createElement('div');

    popup.className = 'color-picker-popup';

    popup.id = 'unifiedBorderOptionsPopup';



    const title = document.createElement('h3');

    const cellCount = selectedCells.length > 0 ? selectedCells.length : 1;

    title.textContent = cellCount > 1 ? `Border Options (${cellCount} cells selected)` : 'Border Options';

    popup.appendChild(title);



    // Border toggle

    const toggleContainer = document.createElement('div');

    toggleContainer.style.display = 'flex';

    toggleContainer.style.alignItems = 'center';

    toggleContainer.style.marginBottom = '15px';

    toggleContainer.style.justifyContent = 'center';



    const toggleLabel = document.createElement('span');

    toggleLabel.textContent = 'Border: ';

    toggleLabel.style.marginRight = '10px';

    toggleLabel.style.fontWeight = '500';



    const toggleInput = document.createElement('input');

    toggleInput.type = 'checkbox';

    toggleInput.id = 'borderToggle';

    // Check if border is actually applied - only check if border is explicitly true AND has border properties
    const hasBorder = currentStyle.border === true && (currentStyle.borderWidth || currentStyle.borderStyle || currentStyle.borderColor);
    toggleInput.checked = hasBorder;

    toggleInput.style.transform = 'scale(1.3)';



    toggleContainer.appendChild(toggleLabel);

    toggleContainer.appendChild(toggleInput);

    popup.appendChild(toggleContainer);



    // Border width options

    const widthContainer = document.createElement('div');

    widthContainer.style.marginBottom = '15px';



    const widthLabel = document.createElement('label');

    widthLabel.textContent = 'Border Width:';

    widthLabel.style.display = 'block';

    widthLabel.style.marginBottom = '8px';

    widthLabel.style.fontWeight = '500';

    widthLabel.style.textAlign = 'center';



    const widthSelect = document.createElement('select');

    widthSelect.id = 'borderWidthSelect';

    widthSelect.style.width = '100%';

    widthSelect.style.padding = '8px';

    widthSelect.style.borderRadius = '6px';

    widthSelect.style.border = '1px solid #ced4da';



    const widthOptions = ['1px', '2px', '3px', '4px', '5px'];

    widthOptions.forEach(width => {

        const option = document.createElement('option');

        option.value = width;

        option.textContent = width;

        if (width === selectedBorderWidth) {

            option.selected = true;

        }

        widthSelect.appendChild(option);

    });



    widthContainer.appendChild(widthLabel);

    widthContainer.appendChild(widthSelect);

    popup.appendChild(widthContainer);



    // Border style options

    const styleContainer = document.createElement('div');

    styleContainer.style.marginBottom = '15px';



    const styleLabel = document.createElement('label');

    styleLabel.textContent = 'Border Style:';

    styleLabel.style.display = 'block';

    styleLabel.style.marginBottom = '8px';

    styleLabel.style.fontWeight = '500';

    styleLabel.style.textAlign = 'center';



    const styleSelect = document.createElement('select');

    styleSelect.id = 'borderStyleSelect';

    styleSelect.style.width = '100%';

    styleSelect.style.padding = '8px';

    styleSelect.style.borderRadius = '6px';

    styleSelect.style.border = '1px solid #ced4da';



    const styleOptions = ['solid', 'dashed', 'dotted', 'double'];

    styleOptions.forEach(style => {

        const option = document.createElement('option');

        option.value = style;

        option.textContent = style.charAt(0).toUpperCase() + style.slice(1);

        if (style === selectedBorderStyle) {

            option.selected = true;

        }

        styleSelect.appendChild(option);

    });



    styleContainer.appendChild(styleLabel);

    styleContainer.appendChild(styleSelect);

    popup.appendChild(styleContainer);



    // Border color picker

    const colorContainer = document.createElement('div');

    colorContainer.style.marginBottom = '20px';



    const colorLabel = document.createElement('label');

    colorLabel.textContent = 'Border Color:';

    colorLabel.style.display = 'block';

    colorLabel.style.marginBottom = '8px';

    colorLabel.style.fontWeight = '500';

    colorLabel.style.textAlign = 'center';



    const colorInput = document.createElement('input');

    colorInput.type = 'color';

    colorInput.id = 'borderColorInput';

    colorInput.value = selectedBorderColor;

    colorInput.style.width = '100%';

    colorInput.style.height = '40px';

    colorInput.style.borderRadius = '6px';

    colorInput.style.border = '1px solid #ced4da';



    colorContainer.appendChild(colorLabel);

    colorContainer.appendChild(colorInput);

    popup.appendChild(colorContainer);



    // Preview area

    const previewContainer = document.createElement('div');

    previewContainer.className = 'color-preview';

    previewContainer.style.margin = '15px 0';

    previewContainer.style.padding = '15px';

    previewContainer.style.borderRadius = '6px';

    previewContainer.style.border = '1px solid #ddd';

    previewContainer.style.backgroundColor = '#f8f9fa';

    previewContainer.style.fontWeight = 'bold';

    previewContainer.style.textAlign = 'center';

    previewContainer.textContent = 'Border Preview';

    previewContainer.id = 'borderPreviewArea';

    popup.appendChild(previewContainer);



    // Update preview when options change

    toggleInput.addEventListener('change', updateBorderPreview);

    widthSelect.addEventListener('change', updateBorderPreview);

    styleSelect.addEventListener('change', updateBorderPreview);

    colorInput.addEventListener('input', updateBorderPreview);



    // Initialize preview

    updateBorderPreview();



    function updateBorderPreview() {

        const preview = document.getElementById('borderPreviewArea');

        if (preview) {

            const isEnabled = toggleInput.checked;

            if (isEnabled) {

                const width = widthSelect.value;

                const style = styleSelect.value;

                const color = colorInput.value;

                preview.style.border = `${width} ${style} ${color}`;

            } else {

                preview.style.border = '1px solid #ddd';

            }

        }

    }



    // OK button

    const okBtn = document.createElement('button');

    okBtn.className = 'btn btn-primary';

    okBtn.textContent = 'Apply';

    okBtn.style.marginTop = '10px';

    okBtn.style.width = '100%';

    okBtn.style.padding = '10px 20px';

    okBtn.style.backgroundColor = '#007bff';

    okBtn.style.color = 'white';

    okBtn.style.border = 'none';

    okBtn.style.borderRadius = '4px';

    okBtn.style.cursor = 'pointer';

    okBtn.style.fontSize = '14px';

    okBtn.style.zIndex = '9999';

    okBtn.style.pointerEvents = 'auto';

    okBtn.style.position = 'relative';

    okBtn.onclick = () => {
        applyUnifiedBorderOptions(cellInfo.rowIndex, cellInfo.colIndex, cellInfo.tdElement);
    };

    okBtn.onmouseover = () => {
        okBtn.style.backgroundColor = '#0056b3';
    };

    okBtn.onmouseout = () => {
        okBtn.style.backgroundColor = '#007bff';
    };



    popup.appendChild(okBtn);



    // Close button

    const closeBtn = document.createElement('button');

    closeBtn.className = 'color-picker-close';

    closeBtn.textContent = '×';

    closeBtn.onclick = () => document.body.removeChild(overlay);



    popup.appendChild(closeBtn);

    overlay.appendChild(popup);

    document.body.appendChild(overlay);



    // Close on overlay click

    overlay.onclick = (e) => {

        if (e.target === overlay) {

            document.body.removeChild(overlay);

        }

    };

}



function applyUnifiedBorderOptions(rowIndex, colIndex, tdElement) {

    const toggleInput = document.getElementById('borderToggle');

    const widthSelect = document.getElementById('borderWidthSelect');

    const styleSelect = document.getElementById('borderStyleSelect');

    const colorInput = document.getElementById('borderColorInput');



    const isEnabled = toggleInput.checked;

    const width = widthSelect.value;

    const style = styleSelect.value;

    const color = colorInput.value;



    // Update state variables

    selectedBorderWidth = width;

    selectedBorderStyle = style;

    selectedBorderColor = color;



    // Apply to selected cells or single cell

    if (selectedCells.length > 0) {

        selectedCells.forEach(cell => {

            const cellTd = cell.td;



            if (isEnabled) {

                setCellStyle(cell.row, cell.col, 'border', true);

                setCellStyle(cell.row, cell.col, 'borderWidth', width);

                setCellStyle(cell.row, cell.col, 'borderStyle', style);

                setCellStyle(cell.row, cell.col, 'borderColor', color);



                if (cellTd) {

                    cellTd.style.border = `${width} ${style} ${color}`;

                }

            } else {

                setCellStyle(cell.row, cell.col, 'border', false);

                if (cellTd) {

                    cellTd.style.border = `1px solid ${getGridLineColor()}`;

                }

            }

        });

        showToast(`Border options applied to ${selectedCells.length} cells`, 'success');

    } else {

        if (isEnabled) {

            setCellStyle(rowIndex, colIndex, 'border', true);

            setCellStyle(rowIndex, colIndex, 'borderWidth', width);

            setCellStyle(rowIndex, colIndex, 'borderStyle', style);

            setCellStyle(rowIndex, colIndex, 'borderColor', color);



            if (tdElement) {

                tdElement.style.border = `${width} ${style} ${color}`;

            }

        } else {

            setCellStyle(rowIndex, colIndex, 'border', false);

            if (tdElement) {

                tdElement.style.border = `1px solid ${getGridLineColor()}`;

            }

        }

        showToast('Border options applied', 'success');

    }



    // Close the modal

    const overlay = document.getElementById('unifiedBorderOptionsOverlay');

    if (overlay) {

        document.body.removeChild(overlay);

    }

}



// Helper function to convert RGB to Hex

function rgbToHex(color) {
    // If already hex, return it
    if (color.startsWith('#')) {
        return color.length === 7 ? color : '#000000';
    }

    // If rgb/rgba format
    const rgbMatch = color.match(/\d+/g);
    if (rgbMatch && rgbMatch.length >= 3) {
        const r = parseInt(rgbMatch[0]).toString(16).padStart(2, '0');
        const g = parseInt(rgbMatch[1]).toString(16).padStart(2, '0');
        const b = parseInt(rgbMatch[2]).toString(16).padStart(2, '0');
        return `#${r}${g}${b}`;
    }

    // Default fallback
    return '#000000';
}

function setCellFontSize() {
    if (!contextMenuCell) return;

    const { rowIndex, colIndex, inputElement } = contextMenuCell;
    const currentSize = inputElement.style.fontSize || '14px';

    const size = prompt('Enter font size (e.g., 16px, 20px):', currentSize);
    if (size) {
        // Apply to multiple cells if selected
        if (selectedCells.length > 0) {
            selectedCells.forEach(cell => {
                const cellInput = cell.td.querySelector('input, textarea');
                setCellStyle(cell.row, cell.col, 'fontSize', size);
                if (cellInput) {
                    cellInput.style.fontSize = size;
                }
            });
            closeCellContextMenu();
            showToast(`Font size updated for ${selectedCells.length} cells`, 'success');
        } else {
            // Apply to single cell
            setCellStyle(rowIndex, colIndex, 'fontSize', size);
            inputElement.style.fontSize = size;
            closeCellContextMenu();
            showToast('Font size updated', 'success');
        }
    }
}

function clearCellFormatting() {
    if (!contextMenuCell) return;

    const { rowIndex, colIndex, tdElement, inputElement } = contextMenuCell;

    // Apply to multiple cells if selected
    if (selectedCells.length > 0) {
        selectedCells.forEach(cell => {
            const cellTd = cell.td;
            const cellInput = cellTd.querySelector('input, textarea');
            const sheet = tableData.sheets[currentSheet];
            const col = sheet.columns[cell.col];

            // Remove all cell-specific styles
            const cellKey = `${cell.row}-${cell.col}`;
            if (sheet.cellStyles && sheet.cellStyles[cellKey]) {
                delete sheet.cellStyles[cellKey];
            }

            // Reset to column defaults
            if (cellInput) {
                cellInput.style.fontWeight = 'normal';
                cellInput.style.fontStyle = 'normal';
                cellInput.style.textAlign = 'left';
                cellInput.style.fontSize = '';
                cellInput.style.color = col.textColor || '#000000';
            }

            if (cellTd) {
                cellTd.style.backgroundColor = col.color || '#ffffff';
                cellTd.style.border = '';
            }
        });
        closeCellContextMenu();
        showToast(`Formatting cleared for ${selectedCells.length} cells`, 'success');
    } else {
        // Apply to single cell
        const sheet = tableData.sheets[currentSheet];
        const col = sheet.columns[colIndex];

        // Remove all cell-specific styles
        const cellKey = `${rowIndex}-${colIndex}`;
        if (sheet.cellStyles && sheet.cellStyles[cellKey]) {
            delete sheet.cellStyles[cellKey];
        }

        // Reset to column defaults
        inputElement.style.fontWeight = 'normal';
        inputElement.style.fontStyle = 'normal';
        inputElement.style.textAlign = 'left';
        inputElement.style.fontSize = '';
        inputElement.style.color = col.textColor || '#000000';

        tdElement.style.backgroundColor = col.color || '#ffffff';
        tdElement.style.border = '';

        closeCellContextMenu();
        showToast('Cell formatting cleared', 'success');
    }
}

async function addSheet() {
    const sheetName = prompt('Enter sheet name:', `Sheet${tableData.sheets.length + 1}`);
    if (!sheetName) return;

    try {
        const response = await fetch('/api/sheets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: sheetName })
        });

        if (response.ok) {
            const result = await response.json();
            tableData.sheets.push({ name: sheetName, columns: [], rows: [] });
            currentSheet = result.sheetIndex;

            // Auto-assign to current category if one is selected
            if (currentCategory !== null) {
                initializeCategories();
                tableData.sheetCategories[currentSheet] = currentCategory;
                await saveData();
                showToast(`Sheet added to "${currentCategory}" category`, 'success');
            }

            renderCategoryTabs();
            renderSheetTabs();
            renderTable();
        }
    } catch (error) {
        console.error('Error adding sheet:', error);
    }
}

async function moveSheetUp(index) {
    // Get current sheet's category
    const currentSheetCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)] || null;

    // Find the previous sheet in the same category
    let prevIndex = -1;
    for (let i = index - 1; i >= 0; i--) {
        const sheetCategory = tableData.sheetCategories[i] || tableData.sheetCategories[String(i)] || null;
        if (sheetCategory === currentSheetCategory) {
            prevIndex = i;
            break;
        }
    }

    if (prevIndex === -1) {
        showToast('Sheet is already at the top of this category', 'info');
        return;
    }

    // Swap sheets
    const temp = tableData.sheets[index];
    tableData.sheets[index] = tableData.sheets[prevIndex];
    tableData.sheets[prevIndex] = temp;

    // Swap category assignments so they follow the sheets
    const tempCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)];
    const prevCategory = tableData.sheetCategories[prevIndex] || tableData.sheetCategories[String(prevIndex)];

    // Clear old entries
    delete tableData.sheetCategories[index];
    delete tableData.sheetCategories[String(index)];
    delete tableData.sheetCategories[prevIndex];
    delete tableData.sheetCategories[String(prevIndex)];

    // Swap: sheet at index goes to prevIndex, sheet at prevIndex goes to index
    if (tempCategory) {
        tableData.sheetCategories[prevIndex] = tempCategory;
    }
    if (prevCategory) {
        tableData.sheetCategories[index] = prevCategory;
    }

    // Update current sheet index if needed
    if (currentSheet === index) {
        currentSheet = prevIndex;
    } else if (currentSheet === prevIndex) {
        currentSheet = index;
    }

    // Save and re-render
    await saveData();
    renderCategoryTabs();
    renderSheetTabs();
    renderTable();
    showToast('Sheet moved up', 'success');
}

async function moveSheetDown(index) {
    // Get current sheet's category
    const currentSheetCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)] || null;

    // Find the next sheet in the same category
    let nextIndex = -1;
    for (let i = index + 1; i < tableData.sheets.length; i++) {
        const sheetCategory = tableData.sheetCategories[i] || tableData.sheetCategories[String(i)] || null;
        if (sheetCategory === currentSheetCategory) {
            nextIndex = i;
            break;
        }
    }

    if (nextIndex === -1) {
        showToast('Sheet is already at the bottom of this category', 'info');
        return;
    }

    // Swap sheets
    const temp = tableData.sheets[index];
    tableData.sheets[index] = tableData.sheets[nextIndex];
    tableData.sheets[nextIndex] = temp;

    // Swap category assignments so they follow the sheets
    const tempCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)];
    const nextCategory = tableData.sheetCategories[nextIndex] || tableData.sheetCategories[String(nextIndex)];

    // Clear old entries
    delete tableData.sheetCategories[index];
    delete tableData.sheetCategories[String(index)];
    delete tableData.sheetCategories[nextIndex];
    delete tableData.sheetCategories[String(nextIndex)];

    // Swap: sheet at index goes to nextIndex, sheet at nextIndex goes to index
    if (tempCategory) {
        tableData.sheetCategories[nextIndex] = tempCategory;
    }
    if (nextCategory) {
        tableData.sheetCategories[index] = nextCategory;
    }

    // Update current sheet index if needed
    if (currentSheet === index) {
        currentSheet = nextIndex;
    } else if (currentSheet === nextIndex) {
        currentSheet = index;
    }

    // Save and re-render
    await saveData();
    renderCategoryTabs();
    renderSheetTabs();
    renderTable();
    showToast('Sheet moved down', 'success');
}

async function deleteSheet(index) {
    if (tableData.sheets.length <= 1) {
        alert('Cannot delete the last sheet!');
        return;
    }

    const sheetName = tableData.sheets[index].name;
    if (!confirm(`Delete sheet "${sheetName}"?`)) return;

    try {
        const response = await fetch(`/api/sheets/${index}`, { method: 'DELETE' });
        if (response.ok) {
            tableData.sheets.splice(index, 1);

            // Reindex sheetCategories after deletion
            const newSheetCategories = {};
            Object.keys(tableData.sheetCategories).forEach(key => {
                const sheetIndex = parseInt(key);
                if (sheetIndex < index) {
                    // Sheets before deleted sheet keep their index
                    newSheetCategories[sheetIndex] = tableData.sheetCategories[key];
                } else if (sheetIndex > index) {
                    // Sheets after deleted sheet shift down by 1
                    newSheetCategories[sheetIndex - 1] = tableData.sheetCategories[key];
                }
                // Skip the deleted sheet (sheetIndex === index)
            });
            tableData.sheetCategories = newSheetCategories;

            if (currentSheet >= tableData.sheets.length) {
                currentSheet = tableData.sheets.length - 1;
            }
            renderSheetTabs();
            renderTable();
            autoSaveActiveSheet();
        }
    } catch (error) {
        console.error('Error deleting sheet:', error);
    }
}

function switchSheet(index) {
    // Track sheet history for Alt+M toggle and F2 recent sheets
    if (currentSheet !== index) {
        // Remove the index if it already exists in history
        sheetHistory = sheetHistory.filter(i => i !== index);
        // Add current sheet to history before switching
        if (sheetHistory[sheetHistory.length - 1] !== currentSheet) {
            sheetHistory.push(currentSheet);
        }
        // Keep last 20 sheets in history (for F2 popup)
        if (sheetHistory.length > 20) {
            sheetHistory.shift();
        }
        // Save to localStorage for persistence across page refreshes
        localStorage.setItem('sheetHistory', JSON.stringify(sheetHistory));
    }

    currentSheet = index;

    // Update currentCategory to match the sheet's category
    const sheetCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)] || null;
    currentCategory = sheetCategory;

    renderCategoryTabs();
    renderSheetTabs();
    renderTable();
    autoSaveActiveSheet();
}

function showRenameModal(index) {
    currentSheet = index;
    const sheet = tableData.sheets[index];
    document.getElementById('sheetName').value = sheet.name;
    document.getElementById('sheetNickname').value = sheet.nickname || '';
    document.getElementById('renameModal').style.display = 'block';
}



function renderSheetTabs() {
    initializeCategories();

    // Update current sheet name
    const currentSheetNameEl = document.getElementById('currentSheetName');
    if (tableData.sheets[currentSheet]) {
        currentSheetNameEl.textContent = tableData.sheets[currentSheet].name;
    }

    // Render sheet list (filtered by category)
    const sheetList = document.getElementById('sheetList');
    sheetList.innerHTML = '';

    tableData.sheets.forEach((sheet, index) => {
        // Filter by category - handle both string and numeric keys
        const sheetCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)] || null;

        // When viewing "Uncategorized", only show sheets without a category
        if (currentCategory === null && sheetCategory) {
            return; // Skip sheets that have a category
        }

        // When viewing a specific category, only show sheets in that category
        if (currentCategory !== null && sheetCategory !== currentCategory) {
            return; // Skip sheets not in current category
        }

        const item = document.createElement('div');
        item.className = `sheet-item ${index === currentSheet ? 'active' : ''}`;

        const nameSpan = document.createElement('span');
        nameSpan.className = 'sheet-item-name';
        nameSpan.textContent = sheet.name;

        nameSpan.onclick = () => {
            switchSheet(index);
            toggleSheetList();
        };

        item.appendChild(nameSpan);
        sheetList.appendChild(item);
    });
}

function toggleSheetList() {
    const sheetList = document.getElementById('sheetList');
    sheetList.classList.toggle('show');
}

function openSettings() {
    // Load current grid line color
    const savedColor = localStorage.getItem('gridLineColor') || '#dddddd';
    document.getElementById('gridLineColor').value = savedColor;
    document.getElementById('gridLineColorText').value = savedColor.substring(1).toUpperCase(); // Remove # prefix

    // Load Vrinda font toggle state
    const vrindaEnabled = localStorage.getItem('vrindaFontEnabled') !== 'false'; // Default true
    document.getElementById('vrindaFontToggle').checked = vrindaEnabled;

    document.getElementById('settingsModal').style.display = 'block';
}

function toggleVrindaFont(enabled) {
    localStorage.setItem('vrindaFontEnabled', enabled);

    const table = document.getElementById('dataTable');
    if (enabled) {
        table.classList.remove('disable-vrinda');
        showToast('Vrinda font enabled for Bangla', 'success');
    } else {
        table.classList.add('disable-vrinda');
        showToast('Vrinda font disabled', 'success');
    }
}

function syncGridLineColor(value) {
    // Handle input with or without # prefix
    let colorValue = value;
    if (!colorValue.startsWith('#')) {
        colorValue = '#' + colorValue;
    }

    // Validate hex color
    if (/^#[0-9A-Fa-f]{6}$/.test(colorValue) || /^#[0-9A-Fa-f]{3}$/.test(colorValue)) {
        document.getElementById('gridLineColor').value = colorValue;
        document.getElementById('gridLineColorText').value = colorValue.substring(1).toUpperCase();
        applyGridLineColor(colorValue);
    }
}

function applyGridLineColor(color) {
    // Apply the color to CSS variables
    document.documentElement.style.setProperty('--grid-line-color', color);
    localStorage.setItem('gridLineColor', color);

    // Re-render table to apply new color to all cells
    renderTable();
}

function getGridLineColor() {
    return getComputedStyle(document.documentElement).getPropertyValue('--grid-line-color').trim() || '#dddddd';
}

function resetGridLineColor() {
    const defaultColor = '#dddddd';
    document.getElementById('gridLineColor').value = defaultColor;
    document.getElementById('gridLineColorText').value = defaultColor.substring(1).toUpperCase();
    applyGridLineColor(defaultColor);
    showToast('Grid line color reset to default', 'success');
}

// Category Management Functions
function toggleCategoryList(event) {
    if (event) {
        event.stopPropagation();
    }

    const categoryList = document.getElementById('categoryList');
    const isShowing = categoryList.classList.toggle('show');

    if (isShowing) {
        // Add click-outside handler when opening with longer delay
        setTimeout(() => {
            document.addEventListener('click', closeCategoryListOnClickOutside);
        }, 100);
    } else {
        // Remove handler when closing
        document.removeEventListener('click', closeCategoryListOnClickOutside);
    }
}

function closeCategoryListOnClickOutside(e) {
    const categoryList = document.getElementById('categoryList');
    const categorySelector = document.querySelector('.category-selector');

    // Check if click is outside the category selector
    if (categorySelector && !categorySelector.contains(e.target)) {
        categoryList.classList.remove('show');
        document.removeEventListener('click', closeCategoryListOnClickOutside);
    }
}

function showAddCategoryModal() {
    document.getElementById('categoryName').value = '';
    document.getElementById('addCategoryModal').style.display = 'block';
}

function closeAddCategoryModal() {
    document.getElementById('addCategoryModal').style.display = 'none';
}

function showRenameCategoryModal() {
    if (!currentCategory) {
        showToast('Select a category to rename (not Uncategorized)', 'error');
        return;
    }
    document.getElementById('newCategoryName').value = currentCategory;
    document.getElementById('renameCategoryModal').style.display = 'block';
}

function closeRenameCategoryModal() {
    document.getElementById('renameCategoryModal').style.display = 'none';
}

function showMoveToCategoryModal(sheetIndex) {
    const select = document.getElementById('targetCategory');
    select.innerHTML = '<option value="">Uncategorized</option>';

    // Populate with existing categories
    if (tableData.categories) {
        tableData.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            select.appendChild(option);
        });
    }

    // Set current category if exists
    const currentCat = tableData.sheetCategories?.[sheetIndex] || '';
    select.value = currentCat;

    document.getElementById('moveToCategoryModal').style.display = 'block';
}

function closeMoveToCategoryModal() {
    document.getElementById('moveToCategoryModal').style.display = 'none';
}

// Initialize category data structure if not exists
function initializeCategories() {
    if (!tableData.categories) {
        tableData.categories = [];
    }
    if (!tableData.sheetCategories) {
        tableData.sheetCategories = {};
    }
}

// Add category form handler
document.getElementById('addCategoryForm').onsubmit = async function (e) {
    e.preventDefault();
    const categoryName = document.getElementById('categoryName').value.trim();

    if (!categoryName) return;

    initializeCategories();

    if (tableData.categories.includes(categoryName)) {
        showToast('Category already exists', 'warning');
        return;
    }

    tableData.categories.push(categoryName);
    await saveData();
    renderCategoryTabs();
    closeAddCategoryModal();
    showToast(`Category "${categoryName}" added`, 'success');
};

// Rename category form handler
document.getElementById('renameCategoryForm').onsubmit = async function (e) {
    e.preventDefault();
    const newName = document.getElementById('newCategoryName').value.trim();
    const oldName = currentCategory;

    if (!newName || !oldName) return;

    if (tableData.categories.includes(newName)) {
        showToast('Category name already exists', 'warning');
        return;
    }

    // Update category name in categories array
    const index = tableData.categories.indexOf(oldName);
    if (index !== -1) {
        tableData.categories[index] = newName;
    }

    // Update all sheets that use this category
    Object.keys(tableData.sheetCategories).forEach(sheetIndex => {
        if (tableData.sheetCategories[sheetIndex] === oldName) {
            tableData.sheetCategories[sheetIndex] = newName;
        }
    });

    currentCategory = newName;
    await saveData();
    renderCategoryTabs();
    closeRenameCategoryModal();
    showToast(`Category renamed to "${newName}"`, 'success');
};

// Move to category form handler
document.getElementById('moveToCategoryForm').onsubmit = async function (e) {
    e.preventDefault();
    const targetCategory = document.getElementById('targetCategory').value;

    initializeCategories();

    if (targetCategory) {
        tableData.sheetCategories[currentSheet] = targetCategory;
    } else {
        delete tableData.sheetCategories[currentSheet];
    }

    await saveData();
    renderCategoryTabs();
    renderSheetTabs();
    closeMoveToCategoryModal();
    showToast('Sheet moved to category', 'success');
};

function renderCategoryTabs() {
    initializeCategories();

    const currentCategoryNameEl = document.getElementById('currentCategoryName');
    currentCategoryNameEl.textContent = currentCategory || 'Uncategorized';

    const categoryList = document.getElementById('categoryList');
    categoryList.innerHTML = '';

    // Add "Uncategorized" option
    const uncategorizedCount = tableData.sheets.filter((sheet, index) => {
        return !tableData.sheetCategories[index] && !tableData.sheetCategories[String(index)];
    }).length;

    const allItem = document.createElement('div');
    allItem.className = `category-item ${currentCategory === null ? 'active' : ''}`;

    const allName = document.createElement('span');
    allName.className = 'category-item-name';
    allName.textContent = 'Uncategorized';
    allName.onclick = () => {
        currentCategory = null;

        // Switch to first uncategorized sheet
        const firstUncategorized = tableData.sheets.findIndex((sheet, index) => {
            return !tableData.sheetCategories[index] && !tableData.sheetCategories[String(index)];
        });

        if (firstUncategorized !== -1) {
            currentSheet = firstUncategorized;
        }

        renderCategoryTabs();
        renderSheetTabs();
        renderTable();
        toggleCategoryList();
    };

    const allCount = document.createElement('span');
    allCount.className = 'category-item-count';
    allCount.textContent = uncategorizedCount;

    allItem.appendChild(allName);
    allItem.appendChild(allCount);
    categoryList.appendChild(allItem);

    // Add each category
    tableData.categories.forEach(category => {
        const count = Object.values(tableData.sheetCategories).filter(c => c === category).length;

        const item = document.createElement('div');
        item.className = `category-item ${currentCategory === category ? 'active' : ''}`;

        const nameSpan = document.createElement('span');
        nameSpan.className = 'category-item-name';
        nameSpan.textContent = category;
        nameSpan.onclick = () => {
            currentCategory = category;

            // Switch to first sheet in this category
            const firstSheetInCategory = tableData.sheets.findIndex((sheet, index) => {
                return tableData.sheetCategories[index] === category;
            });

            if (firstSheetInCategory !== -1) {
                currentSheet = firstSheetInCategory;
            }

            renderCategoryTabs();
            renderSheetTabs();
            renderTable();
            toggleCategoryList();
        };

        const countSpan = document.createElement('span');
        countSpan.className = 'category-item-count';
        countSpan.textContent = count;

        const deleteBtn = document.createElement('span');
        deleteBtn.className = 'category-delete-btn';
        deleteBtn.textContent = '×';
        deleteBtn.title = 'Delete category';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteCategory(category);
        };

        item.appendChild(nameSpan);
        item.appendChild(countSpan);
        item.appendChild(deleteBtn);
        categoryList.appendChild(item);
    });
}

async function deleteCategory(categoryName) {
    const count = Object.values(tableData.sheetCategories).filter(c => c === categoryName).length;

    if (!confirm(`Delete category "${categoryName}"?\n\n${count} sheet(s) will be moved to Uncategorized.`)) {
        return;
    }

    // Remove category from list
    const categoryIndex = tableData.categories.indexOf(categoryName);
    if (categoryIndex > -1) {
        tableData.categories.splice(categoryIndex, 1);
    }

    // Move all sheets in this category to uncategorized
    Object.keys(tableData.sheetCategories).forEach(key => {
        if (tableData.sheetCategories[key] === categoryName) {
            delete tableData.sheetCategories[key];
        }
    });

    // If we're currently viewing this category, switch to Uncategorized
    if (currentCategory === categoryName) {
        currentCategory = null;

        // Switch to first uncategorized sheet
        const firstUncategorized = tableData.sheets.findIndex((sheet, index) => {
            return !tableData.sheetCategories[index] && !tableData.sheetCategories[String(index)];
        });

        if (firstUncategorized !== -1) {
            currentSheet = firstUncategorized;
        }
    }

    await saveData();
    renderCategoryTabs();
    renderSheetTabs();
    renderTable();
    showToast(`Category "${categoryName}" deleted`, 'success');
}

async function moveCategoryUp() {
    if (!currentCategory) {
        showToast('Select a category to move (not Uncategorized)', 'error');
        return;
    }

    const index = tableData.categories.indexOf(currentCategory);
    if (index <= 0) {
        showToast('Category is already at the top', 'warning');
        return;
    }

    // Swap with previous category
    [tableData.categories[index - 1], tableData.categories[index]] =
        [tableData.categories[index], tableData.categories[index - 1]];

    await saveData();
    renderCategoryTabs();

    // Refresh F1 popup if it's open
    const f1Popup = document.getElementById('f1Popup');
    if (f1Popup && f1Popup.classList.contains('show')) {
        populateF1Categories();
    }

    showToast(`Category "${currentCategory}" moved up`, 'success');
}

async function moveCategoryDown() {
    if (!currentCategory) {
        showToast('Select a category to move (not Uncategorized)', 'error');
        return;
    }

    const index = tableData.categories.indexOf(currentCategory);
    if (index === -1 || index >= tableData.categories.length - 1) {
        showToast('Category is already at the bottom', 'warning');
        return;
    }

    // Swap with next category
    [tableData.categories[index], tableData.categories[index + 1]] =
        [tableData.categories[index + 1], tableData.categories[index]];

    await saveData();
    renderCategoryTabs();

    // Refresh F1 popup if it's open
    const f1Popup = document.getElementById('f1Popup');
    if (f1Popup && f1Popup.classList.contains('show')) {
        populateF1Categories();
    }

    showToast(`Category "${currentCategory}" moved down`, 'success');
}

let searchMatches = [];
let currentMatchIndex = -1;
let lastSearchTerm = '';

function nextSearchMatch() {
    if (searchMatches.length === 0) return;

    // Remove active class from previous
    if (currentMatchIndex >= 0 && currentMatchIndex < searchMatches.length) {
        searchMatches[currentMatchIndex].classList.remove('active-search-match');
    }

    // Increment index
    currentMatchIndex++;
    if (currentMatchIndex >= searchMatches.length) {
        currentMatchIndex = 0; // Wrap around
    }

    // Highlight new match
    const match = searchMatches[currentMatchIndex];
    match.classList.add('active-search-match');

    // Scroll into view
    match.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });

    // Update toast to show position
    showToast(`Match ${currentMatchIndex + 1} of ${searchMatches.length}`, 'info');
}

function searchTable() {
    const searchInput = document.getElementById('searchInput');
    const searchTerm = searchInput.value.trim();

    // Prevent reset if search term hasn't changed (e.g. Enter key release)
    if (searchTerm === lastSearchTerm) {
        return;
    }
    lastSearchTerm = searchTerm;

    const table = document.getElementById('dataTable');
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');

    // Reset matches
    searchMatches = [];
    currentMatchIndex = -1;

    // Remove previous highlights
    document.querySelectorAll('.search-highlight').forEach(el => {
        el.classList.remove('search-highlight');
    });

    // Remove previous text match highlights from markdown previews
    document.querySelectorAll('.markdown-preview').forEach(preview => {
        const originalHtml = preview.dataset.originalHtml;
        if (originalHtml) {
            preview.innerHTML = originalHtml;
            delete preview.dataset.originalHtml;
        }
    });

    // Remove previous text highlight overlays
    document.querySelectorAll('.text-highlight-overlay').forEach(overlay => {
        overlay.remove();
    });

    if (!searchTerm) {
        // Show all rows if search is empty
        rows.forEach(row => {
            row.style.display = '';
        });
        return;
    }

    // Split search terms by comma, strip markdown, and trim each term
    const searchTerms = searchTerm.split(',')
        .map(term => stripMarkdown(term.trim()).toLowerCase())
        .filter(term => term.length > 0);

    if (searchTerms.length === 0) {
        rows.forEach(row => {
            row.style.display = '';
        });
        return;
    }

    let foundCount = 0;
    const foundTerms = new Set();

    rows.forEach(row => {
        const cells = row.querySelectorAll('td:not(.row-number)');
        let rowMatches = false;

        cells.forEach(cell => {
            const input = cell.querySelector('input, textarea');
            if (input) {
                const cellValue = input.value;
                const cellValueLower = cellValue.toLowerCase();
                // Strip markdown for searching
                const strippedValue = stripMarkdown(cellValueLower);

                // Check if any search term matches
                const matchingTerms = searchTerms.filter(term => strippedValue.includes(term));

                if (matchingTerms.length > 0) {
                    rowMatches = true;
                    matchingTerms.forEach(term => foundTerms.add(term));
                    cell.classList.add('search-highlight');

                    // Highlight markdown preview if it exists
                    const preview = cell.querySelector('.markdown-preview');
                    if (preview) {
                        preview.classList.add('search-highlight');

                        // Highlight exact matching text in preview for all matching terms
                        if (!preview.dataset.originalHtml) {
                            preview.dataset.originalHtml = preview.innerHTML;
                        }
                        // Highlight all terms at once using the original HTML
                        const highlightedHtml = highlightMultipleTermsInHtml(preview.dataset.originalHtml, matchingTerms);
                        preview.innerHTML = highlightedHtml;

                        // Collect matches
                        preview.querySelectorAll('.text-match-highlight').forEach(el => searchMatches.push(el));
                    } else {
                        // For cells without markdown preview, create a temporary overlay with highlighted text
                        createTextHighlightOverlayMulti(cell, input, matchingTerms);

                        // Collect matches from overlay
                        const overlay = cell.querySelector('.text-highlight-overlay');
                        if (overlay) {
                            overlay.querySelectorAll('.text-match-highlight').forEach(el => searchMatches.push(el));
                        }
                    }
                }
            }
        });

        if (rowMatches) {
            row.style.display = '';
            foundCount++;
        } else {
            row.style.display = 'none';
        }
    });

    // Show toast with results
    if (searchTerms.length > 0 && foundCount === 0) {
        showToast('No results found', 'info');
    } else if (searchTerms.length > 1 && foundCount > 0) {
        const foundList = Array.from(foundTerms).join(', ');
        showToast(`Found ${foundCount} row(s) matching: ${foundList}`, 'success');
    } else if (searchTerms.length === 1 && foundCount > 0) {
        showToast(`Found ${foundCount} row(s)`, 'success');
    }
}

// Create a text highlight overlay for cells without markdown preview
function createTextHighlightOverlay(cell, input, searchTerm) {
    // Remove existing overlay if any
    const existingOverlay = cell.querySelector('.text-highlight-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }

    const text = input.value;
    const lowerText = text.toLowerCase();
    const lowerSearch = searchTerm.toLowerCase();

    if (!lowerText.includes(lowerSearch)) return;

    // Get computed styles from input
    const computedStyle = window.getComputedStyle(input);

    // Get input position within cell
    const cellRect = cell.getBoundingClientRect();
    const inputRect = input.getBoundingClientRect();
    const topOffset = inputRect.top - cellRect.top;
    const leftOffset = inputRect.left - cellRect.left;

    // Create overlay div
    const overlay = document.createElement('div');
    overlay.className = 'text-highlight-overlay';

    // Copy exact styles from input/textarea
    overlay.style.position = 'absolute';
    overlay.style.top = topOffset + 'px';
    overlay.style.left = leftOffset + 'px';
    overlay.style.width = computedStyle.width;
    overlay.style.height = computedStyle.height;
    overlay.style.pointerEvents = 'none';
    overlay.style.overflow = 'hidden';
    overlay.style.color = 'transparent';
    overlay.style.background = 'transparent';

    // Copy text-related styles exactly
    overlay.style.fontFamily = computedStyle.fontFamily;
    overlay.style.fontSize = computedStyle.fontSize;
    overlay.style.fontWeight = computedStyle.fontWeight;
    overlay.style.fontStyle = computedStyle.fontStyle;
    overlay.style.lineHeight = computedStyle.lineHeight;
    overlay.style.letterSpacing = computedStyle.letterSpacing;
    overlay.style.wordSpacing = computedStyle.wordSpacing;
    overlay.style.textAlign = computedStyle.textAlign;
    overlay.style.textIndent = computedStyle.textIndent;
    overlay.style.whiteSpace = computedStyle.whiteSpace;
    overlay.style.wordWrap = computedStyle.wordWrap;
    overlay.style.padding = computedStyle.padding;
    overlay.style.paddingTop = computedStyle.paddingTop;
    overlay.style.paddingRight = computedStyle.paddingRight;
    overlay.style.paddingBottom = computedStyle.paddingBottom;
    overlay.style.paddingLeft = computedStyle.paddingLeft;
    overlay.style.border = computedStyle.border;
    overlay.style.borderWidth = computedStyle.borderWidth;
    overlay.style.borderColor = 'transparent';
    overlay.style.margin = '0';
    overlay.style.boxSizing = computedStyle.boxSizing;

    // Build highlighted HTML
    let html = '';
    let lastIndex = 0;
    let index = lowerText.indexOf(lowerSearch);

    while (index !== -1) {
        // Add text before match (invisible)
        if (index > lastIndex) {
            html += escapeHtml(text.substring(lastIndex, index));
        }

        // Add highlighted match
        const matchLength = findActualMatchLength(text, index, lowerSearch);
        html += '<span class="text-match-highlight" style="color: transparent;">' +
            escapeHtml(text.substring(index, index + matchLength)) + '</span>';

        lastIndex = index + matchLength;
        index = lowerText.indexOf(lowerSearch, lastIndex);
    }

    // Add remaining text
    if (lastIndex < text.length) {
        html += escapeHtml(text.substring(lastIndex));
    }

    overlay.innerHTML = html;

    // Make cell position relative
    cell.style.position = 'relative';
    cell.appendChild(overlay);
}

// Helper to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Helper to find actual match length (handles Unicode properly)
function findActualMatchLength(text, startIndex, lowerSearch) {
    // For Unicode safety, extract the substring and check if it matches
    for (let len = lowerSearch.length; len <= text.length - startIndex && len <= lowerSearch.length + 10; len++) {
        const substr = text.substring(startIndex, startIndex + len);
        if (substr.toLowerCase() === lowerSearch) {
            return len;
        }
    }
    // Fallback to search term length
    return lowerSearch.length;
}

// Helper function to highlight matching text within HTML content
function highlightTextInHtml(html, searchTerm) {
    if (!searchTerm) return html;

    // Create a temporary div to parse HTML
    const temp = document.createElement('div');
    temp.innerHTML = html;

    // Function to highlight text in text nodes
    function highlightInNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent;
            const lowerText = text.toLowerCase();
            const lowerSearch = searchTerm.toLowerCase();

            if (lowerText.includes(lowerSearch)) {
                const parts = [];
                let lastIndex = 0;
                let index = lowerText.indexOf(lowerSearch);

                while (index !== -1) {
                    // Add text before match
                    if (index > lastIndex) {
                        parts.push(document.createTextNode(text.substring(lastIndex, index)));
                    }

                    // Add highlighted match - use actual length from original text
                    const matchLength = findActualMatchLength(text, index, lowerSearch);
                    const span = document.createElement('span');
                    span.className = 'text-match-highlight';
                    span.textContent = text.substring(index, index + matchLength);
                    parts.push(span);

                    lastIndex = index + matchLength;
                    index = lowerText.indexOf(lowerSearch, lastIndex);
                }

                // Add remaining text
                if (lastIndex < text.length) {
                    parts.push(document.createTextNode(text.substring(lastIndex)));
                }

                // Replace the text node with highlighted parts
                const parent = node.parentNode;
                parts.forEach(part => parent.insertBefore(part, node));
                parent.removeChild(node);
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // Recursively process child nodes
            Array.from(node.childNodes).forEach(child => highlightInNode(child));
        }
    }

    highlightInNode(temp);
    return temp.innerHTML;
}

// Helper function to highlight multiple search terms at once
function highlightMultipleTermsInHtml(html, searchTerms) {
    if (!searchTerms || searchTerms.length === 0) return html;

    // Create a temporary div to parse HTML
    const temp = document.createElement('div');
    temp.innerHTML = html;

    // Function to highlight text in text nodes
    function highlightInNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent;
            const lowerText = text.toLowerCase();

            // Find all matches for all terms
            const matches = [];
            searchTerms.forEach(term => {
                const lowerTerm = term.toLowerCase();
                let index = lowerText.indexOf(lowerTerm);
                while (index !== -1) {
                    matches.push({ start: index, length: lowerTerm.length });
                    index = lowerText.indexOf(lowerTerm, index + 1);
                }
            });

            if (matches.length > 0) {
                // Sort matches by start position
                matches.sort((a, b) => a.start - b.start);

                // Merge overlapping matches
                const merged = [];
                let current = matches[0];
                for (let i = 1; i < matches.length; i++) {
                    const next = matches[i];
                    if (next.start <= current.start + current.length) {
                        // Overlapping or adjacent, merge them
                        current.length = Math.max(current.start + current.length, next.start + next.length) - current.start;
                    } else {
                        merged.push(current);
                        current = next;
                    }
                }
                merged.push(current);

                // Build highlighted content
                const parts = [];
                let lastIndex = 0;
                merged.forEach(match => {
                    // Add text before match
                    if (match.start > lastIndex) {
                        parts.push(document.createTextNode(text.substring(lastIndex, match.start)));
                    }
                    // Add highlighted match
                    const span = document.createElement('span');
                    span.className = 'text-match-highlight';
                    span.textContent = text.substring(match.start, match.start + match.length);
                    parts.push(span);
                    lastIndex = match.start + match.length;
                });
                // Add remaining text
                if (lastIndex < text.length) {
                    parts.push(document.createTextNode(text.substring(lastIndex)));
                }

                // Replace the text node with highlighted parts
                const parent = node.parentNode;
                parts.forEach(part => parent.insertBefore(part, node));
                parent.removeChild(node);
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // Recursively process child nodes
            Array.from(node.childNodes).forEach(child => highlightInNode(child));
        }
    }

    highlightInNode(temp);
    return temp.innerHTML;
}

// Helper function to create overlay with multiple highlighted terms
function createTextHighlightOverlayMulti(cell, input, searchTerms) {
    // Remove existing overlay if any
    const existingOverlay = cell.querySelector('.text-highlight-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }

    // Get computed styles from input
    const computedStyle = window.getComputedStyle(input);

    // Get input position within cell
    const cellRect = cell.getBoundingClientRect();
    const inputRect = input.getBoundingClientRect();
    const topOffset = inputRect.top - cellRect.top;
    const leftOffset = inputRect.left - cellRect.left;

    // Create overlay div
    const overlay = document.createElement('div');
    overlay.className = 'text-highlight-overlay';

    // Copy exact styles from input/textarea
    overlay.style.position = 'absolute';
    overlay.style.top = topOffset + 'px';
    overlay.style.left = leftOffset + 'px';
    overlay.style.width = computedStyle.width;
    overlay.style.height = computedStyle.height;
    overlay.style.pointerEvents = 'none';
    overlay.style.overflow = 'hidden';
    overlay.style.color = 'transparent';
    overlay.style.background = 'transparent';

    // Copy text-related styles exactly
    overlay.style.fontFamily = computedStyle.fontFamily;
    overlay.style.fontSize = computedStyle.fontSize;
    overlay.style.fontWeight = computedStyle.fontWeight;
    overlay.style.fontStyle = computedStyle.fontStyle;
    overlay.style.lineHeight = computedStyle.lineHeight;
    overlay.style.letterSpacing = computedStyle.letterSpacing;
    overlay.style.wordSpacing = computedStyle.wordSpacing;
    overlay.style.textAlign = computedStyle.textAlign;
    overlay.style.textIndent = computedStyle.textIndent;
    overlay.style.padding = computedStyle.padding;
    overlay.style.paddingTop = computedStyle.paddingTop;
    overlay.style.paddingRight = computedStyle.paddingRight;
    overlay.style.paddingBottom = computedStyle.paddingBottom;
    overlay.style.paddingLeft = computedStyle.paddingLeft;
    overlay.style.border = computedStyle.border;
    overlay.style.boxSizing = computedStyle.boxSizing;
    overlay.style.whiteSpace = computedStyle.whiteSpace;
    overlay.style.wordWrap = computedStyle.wordWrap;
    overlay.style.overflowWrap = computedStyle.overflowWrap;

    // Highlight all terms in the text
    const highlightedHtml = highlightMultipleTermsInHtml(input.value.replace(/\n/g, '<br>'), searchTerms);
    overlay.innerHTML = highlightedHtml;

    cell.appendChild(overlay);
}

function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    searchInput.value = '';

    // Remove text match highlights from markdown previews
    document.querySelectorAll('.markdown-preview').forEach(preview => {
        const originalHtml = preview.dataset.originalHtml;
        if (originalHtml) {
            preview.innerHTML = originalHtml;
            delete preview.dataset.originalHtml;
        }
    });

    // Remove text highlight overlays
    document.querySelectorAll('.text-highlight-overlay').forEach(overlay => {
        overlay.remove();
    });

    searchTable(); // This will show all rows and remove highlights
    showToast('Search cleared', 'info');
}

function toggleRowWrap() {
    const wrapToggle = document.getElementById('wrapToggle');
    const table = document.getElementById('dataTable');

    if (wrapToggle.checked) {
        table.classList.add('wrap-enabled');
        localStorage.setItem('rowWrapEnabled', 'true');

        // Convert all inputs to textareas for wrapping
        const inputs = table.querySelectorAll('td input:not([type="date"]):not([type="email"])');
        inputs.forEach(input => {
            const textarea = document.createElement('textarea');
            // Use stored original value if available (preserves newlines), otherwise use current value
            textarea.value = input.dataset.originalValue || input.value || '';
            textarea.style.cssText = input.style.cssText;
            textarea.className = input.className;
            textarea.rows = 1;

            // Get row and col from parent td
            const td = input.closest('td');
            const rowIndex = parseInt(td.dataset.row);
            const colIndex = parseInt(td.dataset.col);

            if (!isNaN(rowIndex) && !isNaN(colIndex)) {
                textarea.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);
                textarea.oninput = (e) => {
                    autoResizeTextarea(e.target);
                    updateCell(rowIndex, colIndex, e.target.value);
                };
                textarea.oncontextmenu = (e) => showCellContextMenu(e, rowIndex, colIndex, textarea, td);

                // Enter key creates new line (default textarea behavior)
                // No need to prevent default - textareas naturally support multi-line

                // Mouse events for cell selection
                textarea.onmousedown = (e) => {
                    if (e.shiftKey) {
                        e.preventDefault();
                        startCellSelection(rowIndex, colIndex, td);
                    }
                };
                textarea.onmouseenter = () => {
                    if (isSelecting) {
                        addToSelection(rowIndex, colIndex, td);
                    }
                };
            }

            input.replaceWith(textarea);
            td.classList.add('has-textarea');
            autoResizeTextarea(textarea);
        });

        showToast('Text wrapping enabled', 'success');
    } else {
        table.classList.remove('wrap-enabled');
        localStorage.setItem('rowWrapEnabled', 'false');

        // Convert textareas back to inputs
        const textareas = table.querySelectorAll('td textarea');
        textareas.forEach(textarea => {
            // Skip merged cell textareas
            if (textarea.closest('td.merged-cell')) {
                return;
            }

            const input = document.createElement('input');
            input.type = 'text';
            // Preserve the value - inputs will show newlines as spaces but data is preserved
            input.value = textarea.value || '';
            input.style.cssText = textarea.style.cssText;
            input.className = textarea.className;

            // Store original value with newlines in dataset for later restoration
            input.dataset.originalValue = textarea.value;

            // Get row and col from parent td
            const td = textarea.closest('td');
            const rowIndex = parseInt(td.dataset.row);
            const colIndex = parseInt(td.dataset.col);

            if (!isNaN(rowIndex) && !isNaN(colIndex)) {
                input.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);
                input.oncontextmenu = (e) => showCellContextMenu(e, rowIndex, colIndex, input, td);

                // Mouse events for cell selection
                input.onmousedown = (e) => {
                    if (e.shiftKey) {
                        e.preventDefault();
                        startCellSelection(rowIndex, colIndex, td);
                    }
                };
                input.onmouseenter = () => {
                    if (isSelecting) {
                        addToSelection(rowIndex, colIndex, td);
                    }
                };
            }

            textarea.replaceWith(input);
            td.classList.remove('has-textarea');
        });

        showToast('Text wrapping disabled', 'success');
    }
}

function toggleSingleRowMode() {
    singleRowMode = !singleRowMode;
    const btn = document.getElementById('btnSingleRowMode');
    const prevBtn = document.getElementById('btnPrevRow');
    const nextBtn = document.getElementById('btnNextRow');

    if (singleRowMode) {
        btn.classList.add('active');
        prevBtn.disabled = false;
        nextBtn.disabled = false;
        showToast('Single Row Mode Enabled', 'info');
    } else {
        btn.classList.remove('active');
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        showToast('Single Row Mode Disabled', 'info');
    }

    if (singleRowIndex < 0) singleRowIndex = 0;

    renderTable();
    updateSingleRowButtons();
}

function prevSingleRow() {
    if (!singleRowMode) return;
    if (singleRowIndex > 0) {
        singleRowIndex--;
        renderTable();
        updateSingleRowButtons();
    }
}

function nextSingleRow() {
    if (!singleRowMode) return;
    const sheet = tableData.sheets[currentSheet];
    if (singleRowIndex < sheet.rows.length - 1) {
        singleRowIndex++;
        renderTable();
        updateSingleRowButtons();
    }
}

function updateSingleRowButtons() {
    const sheet = tableData.sheets[currentSheet];
    const prevBtn = document.getElementById('btnPrevRow');
    const nextBtn = document.getElementById('btnNextRow');

    if (!singleRowMode) {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        return;
    }

    prevBtn.disabled = singleRowIndex <= 0;
    nextBtn.disabled = singleRowIndex >= sheet.rows.length - 1;
}

function toggleRowNumbers() {
    const rowToggle = document.getElementById('rowToggle');
    const table = document.getElementById('dataTable');

    if (rowToggle.checked) {
        table.classList.remove('hide-row-numbers');
        localStorage.setItem('rowNumbersVisible', 'true');
        showToast('Row numbers shown', 'success');
    } else {
        table.classList.add('hide-row-numbers');
        localStorage.setItem('rowNumbersVisible', 'false');
        showToast('Row numbers hidden', 'success');
    }
}

function toggleMarkdownPreview() {
    const markdownToggle = document.getElementById('markdownToggle');
    const table = document.getElementById('dataTable');

    if (markdownToggle.checked) {
        table.classList.remove('hide-markdown-preview');
        localStorage.setItem('markdownPreviewEnabled', 'true');
        showToast('Markdown preview enabled', 'success');
    } else {
        table.classList.add('hide-markdown-preview');
        localStorage.setItem('markdownPreviewEnabled', 'false');
        showToast('Markdown preview disabled', 'success');
    }
}

function toggleCollapsible(id) {
    const element = document.getElementById(id);
    if (element) {
        if (element.style.display === 'none') {
            element.style.display = 'inline';
        } else {
            element.style.display = 'none';
        }
    }
}

function toggleAllCollapsibles() {
    const collapsibles = document.querySelectorAll('.collapsible-content');
    const correctAnswers = document.querySelectorAll('.correct-answer');

    if (collapsibles.length === 0 && correctAnswers.length === 0) {
        showToast('No hidden content found', 'info');
        return;
    }

    // Determine state based on collapsibles first, then correctAnswers
    let anyVisible = false;
    if (collapsibles.length > 0) {
        anyVisible = Array.from(collapsibles).some(el => el.style.display !== 'none');
    } else if (correctAnswers.length > 0) {
        anyVisible = Array.from(correctAnswers).some(el => el.classList.contains('revealed'));
    }

    // Toggle collapsibles
    collapsibles.forEach(el => {
        el.style.display = anyVisible ? 'none' : 'inline';
    });

    // Toggle correct answers
    correctAnswers.forEach(el => {
        if (anyVisible) el.classList.remove('revealed');
        else el.classList.add('revealed');
    });

    showToast(anyVisible ? 'All hidden content hidden' : 'All hidden content shown', 'success');
}

function autoResizeTextarea(textarea) {
    // Skip if it's a merged cell textarea
    if (textarea.closest('td.merged-cell')) {
        return;
    }

    // Save current scroll position
    const savedScrollTop = textarea.scrollTop;

    // Reset height to measure actual content
    textarea.style.height = 'auto';

    // Get the actual content height
    const scrollHeight = textarea.scrollHeight;
    const minHeight = 22; // Match input height exactly

    // Set height based on content
    const newHeight = Math.max(minHeight, scrollHeight);
    textarea.style.height = newHeight + 'px';

    // Restore scroll position
    textarea.scrollTop = savedScrollTop;

    // Mark the row if it has expanded content
    const tr = textarea.closest('tr');
    if (tr) {
        // Check if any textarea in this row actually needs more height
        const hasExpandedContent = Array.from(tr.querySelectorAll('textarea:not(.merged-cell textarea)')).some(ta => {
            const savedScroll = ta.scrollTop;
            ta.style.height = 'auto';
            const needsHeight = ta.scrollHeight > minHeight + 2; // Small threshold
            ta.style.height = Math.max(minHeight, ta.scrollHeight) + 'px';
            ta.scrollTop = savedScroll;
            return needsHeight;
        });

        if (hasExpandedContent) {
            tr.classList.add('has-wrapped-content');
        } else {
            tr.classList.remove('has-wrapped-content');
        }
    }
}

// Keep the line that contains the cursor vertically centered
function keepCursorCentered(textarea) {
    requestAnimationFrame(() => {
        const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 20;
        const lines = textarea.value.substr(0, textarea.selectionStart).split('\n');
        const wantedTop = (lines.length - 1) * lineHeight;
        textarea.scrollTop = wantedTop - textarea.clientHeight / 2 + lineHeight / 2;
    });
}



function renderTable() {
    const headerRow = document.getElementById('headerRow');
    const tableBody = document.getElementById('tableBody');
    const tableContainer = document.querySelector('.table-container');

    // Save current scroll position
    const scrollTop = tableContainer ? tableContainer.scrollTop : 0;
    const scrollLeft = tableContainer ? tableContainer.scrollLeft : 0;

    headerRow.innerHTML = '';
    tableBody.innerHTML = '';

    const sheet = tableData.sheets[currentSheet];
    if (!sheet) return;

    // Use DocumentFragment for better performance
    const fragment = document.createDocumentFragment();

    // Add row number column
    const rowNumHeader = document.createElement('th');
    rowNumHeader.className = 'row-number';
    rowNumHeader.textContent = '#';
    headerRow.appendChild(rowNumHeader);

    // Render headers
    sheet.columns.forEach((col, index) => {
        const th = document.createElement('th');
        th.style.width = col.width + 'px';
        th.style.minWidth = col.width + 'px';
        th.style.maxWidth = col.width + 'px';

        // Apply header background color (separate from cell color)
        th.style.backgroundColor = col.headerBgColor || col.color || '#f8f9fa';

        const headerCell = document.createElement('div');
        headerCell.className = 'header-cell';

        const columnName = document.createElement('span');
        columnName.className = 'column-name';
        columnName.textContent = col.name;

        // Apply header text styling
        columnName.style.color = col.headerTextColor || col.textColor || '#333333';
        columnName.style.fontWeight = (col.headerBold !== false) ? 'bold' : 'normal'; // Default bold
        columnName.style.fontStyle = col.headerItalic ? 'italic' : 'normal';

        // Apply header text alignment
        if (col.headerCenter) {
            columnName.style.textAlign = 'center';
            columnName.style.flex = '1';
        }

        const menuWrapper = document.createElement('div');
        menuWrapper.className = 'column-menu-wrapper';

        const menuBtn = document.createElement('button');
        menuBtn.className = 'column-menu-btn';
        menuBtn.textContent = '⋮';
        menuBtn.onclick = (e) => toggleColumnMenu(e, index);

        const menu = document.createElement('div');
        menu.className = 'column-menu';
        menu.id = `column-menu-${index}`;

        const sortItem = document.createElement('div');
        sortItem.className = 'column-menu-item has-submenu';
        sortItem.innerHTML = '<span>⇅</span> Sort <span class="submenu-arrow">›</span>';

        const sortSubmenu = document.createElement('div');
        sortSubmenu.className = 'column-submenu';

        const sortAscItem = document.createElement('div');
        sortAscItem.className = 'column-menu-item';
        sortAscItem.innerHTML = '<span>↑</span> A-Z';
        sortAscItem.onclick = (e) => {
            e.stopPropagation();
            sortColumn(index, 'asc');
            closeAllColumnMenus();
        };

        const sortDescItem = document.createElement('div');
        sortDescItem.className = 'column-menu-item';
        sortDescItem.innerHTML = '<span>↓</span> Z-A';
        sortDescItem.onclick = (e) => {
            e.stopPropagation();
            sortColumn(index, 'desc');
            closeAllColumnMenus();
        };

        sortSubmenu.appendChild(sortAscItem);
        sortSubmenu.appendChild(sortDescItem);
        sortItem.appendChild(sortSubmenu);

        const moveItem = document.createElement('div');
        moveItem.className = 'column-menu-item has-submenu';
        moveItem.innerHTML = '<span>↔</span> Move <span class="submenu-arrow">›</span>';

        const moveSubmenu = document.createElement('div');
        moveSubmenu.className = 'column-submenu';

        const moveLeftItem = document.createElement('div');
        moveLeftItem.className = 'column-menu-item';
        moveLeftItem.innerHTML = '<span>←</span> Left';
        if (index === 0) {
            moveLeftItem.classList.add('disabled');
        } else {
            moveLeftItem.onclick = (e) => {
                e.stopPropagation();
                moveColumn(index, 'left');
                closeAllColumnMenus();
            };
        }

        const moveRightItem = document.createElement('div');
        moveRightItem.className = 'column-menu-item';
        moveRightItem.innerHTML = '<span>→</span> Right';
        if (index === sheet.columns.length - 1) {
            moveRightItem.classList.add('disabled');
        } else {
            moveRightItem.onclick = (e) => {
                e.stopPropagation();
                moveColumn(index, 'right');
                closeAllColumnMenus();
            };
        }

        moveSubmenu.appendChild(moveLeftItem);
        moveSubmenu.appendChild(moveRightItem);
        moveItem.appendChild(moveSubmenu);

        const editItem = document.createElement('div');
        editItem.className = 'column-menu-item';
        editItem.innerHTML = '<span>✏️</span> Edit';
        editItem.onclick = () => {
            editColumn(index);
            closeAllColumnMenus();
        };

        const deleteItem = document.createElement('div');
        deleteItem.className = 'column-menu-item delete';
        deleteItem.innerHTML = '<span>🗑️</span> Delete';
        deleteItem.onclick = () => {
            deleteColumn(index);
            closeAllColumnMenus();
        };

        menu.appendChild(editItem);
        menu.appendChild(sortItem);
        menu.appendChild(moveItem);
        menu.appendChild(deleteItem);
        menuWrapper.appendChild(menuBtn);
        menuWrapper.appendChild(menu);

        headerCell.appendChild(menuWrapper);
        headerCell.appendChild(columnName);
        th.appendChild(headerCell);
        headerRow.appendChild(th);
    });

    const wrapEnabled = localStorage.getItem('rowWrapEnabled') === 'true';

    // Determine which rows to render based on Single Row Mode
    let rowsToRender, rowIndexOffset;
    if (singleRowMode) {
        // Clamp singleRowIndex to valid range
        if (singleRowIndex >= sheet.rows.length) singleRowIndex = sheet.rows.length - 1;
        if (singleRowIndex < 0) singleRowIndex = 0;

        rowsToRender = [sheet.rows[singleRowIndex]];
        rowIndexOffset = singleRowIndex;
    } else {
        rowsToRender = sheet.rows;
        rowIndexOffset = 0;
    }

    // Render rows
    rowsToRender.forEach((row, loopIndex) => {
        const rowIndex = singleRowMode ? singleRowIndex : loopIndex;
        const tr = document.createElement('tr');

        // Row number with delete X and number together
        const rowNumCell = document.createElement('td');
        rowNumCell.className = 'row-number';

        const contentSpan = document.createElement('span');
        contentSpan.innerHTML = '<span class="delete-x" title="Delete row">×</span>&nbsp;' + (rowIndex + 1);
        contentSpan.style.cursor = 'pointer';
        contentSpan.onclick = () => deleteRow(rowIndex);

        // Add row context menu
        rowNumCell.oncontextmenu = (e) => {
            e.preventDefault();
            showRowContextMenu(e, rowIndex);
        };

        rowNumCell.appendChild(contentSpan);
        tr.appendChild(rowNumCell);

        // Data cells
        sheet.columns.forEach((col, colIndex) => {
            const cellValue = row[colIndex] || '';
            const td = document.createElement('td');

            // Handle merged cells
            const mergeInfo = getCellMerge(rowIndex, colIndex);
            if (mergeInfo) {
                if (mergeInfo.hidden) {
                    td.style.display = 'none';
                    tr.appendChild(td);
                    return; // Skip rendering this cell
                }
                if (mergeInfo.colspan) td.colSpan = mergeInfo.colspan;
                if (mergeInfo.rowspan) td.rowSpan = mergeInfo.rowspan;
                td.classList.add('merged-cell');

                // For merged cells, always use textarea to support multiline
                const textarea = document.createElement('textarea');
                textarea.value = row[colIndex] || '';
                textarea.style.color = col.textColor || '#000000';

                // Ensure textarea preserves whitespace and line breaks
                textarea.style.whiteSpace = 'pre-wrap';
                textarea.style.wordWrap = 'break-word';

                if (col.font && col.font !== '') {
                    textarea.style.fontFamily = `'${col.font}', Vrinda, monospace`;
                }

                if (col.fontSize && col.fontSize !== '') {
                    textarea.style.fontSize = col.fontSize + 'px';
                }

                textarea.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);

                // Also handle input event for real-time updates
                textarea.oninput = (e) => {
                    const textarea = e.target;
                    updateCell(rowIndex, colIndex, textarea.value);
                    keepCursorCentered(textarea);
                };

                // Scroll to cursor position when clicking in merged cell textarea
                textarea.onclick = (e) => {
                    keepCursorCentered(e.target);
                };

                // Apply styles to merged cell
                const cellStyle = getCellStyle(rowIndex, colIndex);
                if (col.color) {
                    td.style.backgroundColor = col.color;
                }
                if (cellStyle.bold) textarea.style.fontWeight = 'bold';
                if (cellStyle.italic) textarea.style.fontStyle = 'italic';
                if (cellStyle.center) textarea.style.textAlign = 'center';
                if (cellStyle.border) {
                    const borderWidth = cellStyle.borderWidth || '1px';
                    const borderStyle = cellStyle.borderStyle || 'solid';
                    const borderColor = cellStyle.borderColor || '#000000';
                    td.style.border = `${borderWidth} ${borderStyle} ${borderColor}`;
                } else {
                    td.style.border = `1px solid ${getGridLineColor()}`;
                }
                if (cellStyle.bgColor) {
                    td.style.backgroundColor = cellStyle.bgColor;
                }
                if (cellStyle.textColor) {
                    textarea.style.color = cellStyle.textColor;
                }
                if (cellStyle.fontSize) {
                    textarea.style.fontSize = cellStyle.fontSize;
                }

                textarea.oncontextmenu = (e) => showCellContextMenu(e, rowIndex, colIndex, textarea, td);

                const handleMouseDown = (e) => {
                    if (e.button === 0 && e.shiftKey) {
                        e.preventDefault();
                        startCellSelection(rowIndex, colIndex, td);
                    }
                };

                textarea.onmousedown = (e) => {
                    if (e.shiftKey) {
                        handleMouseDown(e);
                    }
                };
                textarea.onmouseenter = () => {
                    if (isSelecting) {
                        addToSelection(rowIndex, colIndex, td);
                    }
                };

                td.appendChild(textarea);

                // Apply markdown formatting
                applyMarkdownFormatting(rowIndex, colIndex, row[colIndex], textarea);
                tr.appendChild(td);
                return;
            }

            const isTextType = col.type === 'text' || !col.type;
            let input;

            if (wrapEnabled && isTextType) {
                input = document.createElement('textarea');
                input.rows = 1;
                // Preserve newlines in the value
                input.value = cellValue;
                input.style.color = col.textColor || '#000000';

                if (col.font && col.font !== '') {
                    input.style.fontFamily = `'${col.font}', Vrinda, monospace`;
                }

                if (col.fontSize && col.fontSize !== '') {
                    input.style.fontSize = col.fontSize + 'px';
                }

                input.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);
                input.oninput = (e) => {
                    const textarea = e.target;
                    autoResizeTextarea(textarea);
                    updateCell(rowIndex, colIndex, textarea.value);
                    keepCursorCentered(textarea);
                };

                // Scroll to cursor position when clicking in textarea
                input.onclick = (e) => {
                    keepCursorCentered(e.target);
                };

                // Mark td as having textarea for vertical alignment
                td.classList.add('has-textarea');
            } else {
                input = document.createElement('input');
                input.type = col.type;
                // Store the original value (with newlines) in dataset for later restoration
                input.value = cellValue;
                input.dataset.originalValue = cellValue;
                input.style.color = col.textColor || '#000000';

                if (col.font && col.font !== '') {
                    input.style.fontFamily = `'${col.font}', Vrinda, monospace`;
                }

                if (col.fontSize && col.fontSize !== '') {
                    input.style.fontSize = col.fontSize + 'px';
                }

                input.onchange = (e) => {
                    updateCell(rowIndex, colIndex, e.target.value);
                    // Update the stored original value
                    e.target.dataset.originalValue = e.target.value;
                };
            }

            // Apply cell-specific styles
            const cellStyle = getCellStyle(rowIndex, colIndex);
            if (col.color) {
                td.style.backgroundColor = col.color;
            }
            if (cellStyle.bold) input.style.fontWeight = 'bold';
            if (cellStyle.italic) input.style.fontStyle = 'italic';
            if (cellStyle.center) input.style.textAlign = 'center';
            if (cellStyle.border) {
                const borderWidth = cellStyle.borderWidth || '1px';
                const borderStyle = cellStyle.borderStyle || 'solid';
                const borderColor = cellStyle.borderColor || '#000000';
                td.style.border = `${borderWidth} ${borderStyle} ${borderColor}`;
            } else {
                td.style.border = `1px solid ${getGridLineColor()}`;
            }
            if (cellStyle.bgColor) {
                td.style.backgroundColor = cellStyle.bgColor;
            }
            if (cellStyle.textColor) {
                input.style.color = cellStyle.textColor;
            }
            if (cellStyle.fontSize) {
                input.style.fontSize = cellStyle.fontSize;
            }

            input.oncontextmenu = (e) => showCellContextMenu(e, rowIndex, colIndex, input, td);

            // Selection handling
            td.dataset.row = rowIndex;
            td.dataset.col = colIndex;

            const handleMouseDown = (e) => {
                if (e.button === 0) { // Left click
                    if (e.shiftKey) {
                        e.preventDefault(); // Prevent text selection
                        startCellSelection(rowIndex, colIndex, td);
                    }
                }
            };

            const handleMouseEnter = () => {
                if (isSelecting) {
                    addToSelection(rowIndex, colIndex, td);
                }
            };

            // Attach to TD for better hit area, but also input for direct clicks
            td.onmousedown = handleMouseDown;
            input.onmousedown = (e) => {
                if (e.shiftKey) {
                    handleMouseDown(e);
                }
            };

            // Mouse enter for drag selection
            td.onmouseenter = handleMouseEnter;
            input.onmouseenter = handleMouseEnter;

            td.appendChild(input);

            // Apply markdown formatting
            applyMarkdownFormatting(rowIndex, colIndex, cellValue, input);
            tr.appendChild(td);
        });

        fragment.appendChild(tr);
    });

    tableBody.appendChild(fragment);

    // Auto-resize textareas if wrap is enabled
    if (localStorage.getItem('rowWrapEnabled') === 'true') {
        const textareas = tableBody.querySelectorAll('textarea:not(.merged-cell textarea)');
        textareas.forEach(textarea => autoResizeTextarea(textarea));
    }

    // Restore scroll position after rendering
    if (tableContainer) {
        requestAnimationFrame(() => {
            // First try to restore from saved position during this render
            if (scrollTop > 0 || scrollLeft > 0) {
                tableContainer.scrollTop = scrollTop;
                tableContainer.scrollLeft = scrollLeft;
            } else {
                // Otherwise restore from localStorage (after page refresh)
                const savedScrollTop = parseInt(localStorage.getItem('scrollTop') || '0');
                const savedScrollLeft = parseInt(localStorage.getItem('scrollLeft') || '0');
                tableContainer.scrollTop = savedScrollTop;
                tableContainer.scrollLeft = savedScrollLeft;
            }
        });
    }
}

function toggleColumnMenu(event, index) {
    event.stopPropagation();

    // Close all other menus
    closeAllColumnMenus();

    // Toggle current menu
    const menu = document.getElementById(`column-menu-${index}`);
    menu.classList.toggle('show');
}



function closeAllColumnMenus() {
    document.querySelectorAll('.column-menu').forEach(menu => {
        menu.classList.remove('show');
    });
}

function stripMarkdown(text) {
    if (!text) return '';
    let stripped = String(text);

    // Remove correct answer markers: [[text]] -> text
    stripped = stripped.replace(/\[\[(.+?)\]\]/g, '$1');

    // Remove color/style markers: {fg:#fff;bg:#000}text{/} -> text
    stripped = stripped.replace(/\{[^}]*\}(.+?)\{\/\}/g, '$1');

    // Remove bold markers: **text** -> text
    stripped = stripped.replace(/\*\*(.+?)\*\*/g, '$1');

    // Remove underline markers: __text__ -> text
    stripped = stripped.replace(/__(.+?)__/g, '$1');

    // Remove highlight markers: @@text@@ -> text
    stripped = stripped.replace(/@@(.+?)@@/g, '$1');

    // Remove header markers: ##text## -> text
    stripped = stripped.replace(/##(.+?)##/g, '$1');

    // Remove small text markers: ..text.. -> text
    stripped = stripped.replace(/\.\.(.+?)\.\./g, '$1');

    // Remove horizontal separator: ----- -> (empty)
    stripped = stripped.replace(/^-{5,}$/gm, '');

    // Remove code block markers: ```text``` -> text
    stripped = stripped.replace(/```(.+?)```/gs, '$1');

    // Remove inline code markers: `text` -> text
    stripped = stripped.replace(/`(.+?)`/g, '$1');

    // Remove strikethrough markers: ~~text~~ -> text
    stripped = stripped.replace(/~~(.+?)~~/g, '$1');

    // Remove mark/highlight markers: ==text== -> text
    stripped = stripped.replace(/==(.+?)==/g, '$1');

    // Remove red highlight markers: !!text!! -> text
    stripped = stripped.replace(/!!(.+?)!!/g, '$1');

    // Remove blue highlight markers: ??text?? -> text
    stripped = stripped.replace(/\?\?(.+?)\?\?/g, '$1');

    // Remove superscript markers: ^text^ -> text
    stripped = stripped.replace(/\^(.+?)\^/g, '$1');

    // Remove subscript markers: ~text~ -> text
    stripped = stripped.replace(/~(.+?)~/g, '$1');

    // Remove link markers: {link:url}text{/} -> text
    stripped = stripped.replace(/\{link:[^}]*\}(.+?)\{\/\}/g, '$1');

    // Remove collapsible text markers: {{text}} -> text
    stripped = stripped.replace(/\{\{(.+?)\}\}/g, '$1');

    // Remove bullet markers: - item -> item
    stripped = stripped.replace(/^\s*-\s+/gm, '');

    // Remove sub-bullet markers: -- item -> item
    stripped = stripped.replace(/^\s*--\s+/gm, '');

    // Remove Table*N marker
    stripped = stripped.replace(/^Table\*\d+(?:_[^\s\n,]+)?(?:_[^\s\n,]+)?(?:[\n\s,]+)/i, '');

    // Remove Math markers: \( ... \) -> ...
    stripped = stripped.replace(/\\\((.*?)\\\)/g, '$1');

    return stripped;
}

function sortColumn(colIndex, direction) {
    const sheet = tableData.sheets[currentSheet];
    const col = sheet.columns[colIndex];

    // Create array of row indices with their values
    const rowsWithIndices = sheet.rows.map((row, index) => ({
        index: index,
        value: row[colIndex] || '',
        row: row,
        cellStyles: sheet.cellStyles ? Object.keys(sheet.cellStyles)
            .filter(key => key.startsWith(`${index}-`))
            .reduce((obj, key) => {
                obj[key] = sheet.cellStyles[key];
                return obj;
            }, {}) : {}
    }));

    // Sort based on column type
    rowsWithIndices.sort((a, b) => {
        let valA = a.value;
        let valB = b.value;

        // Strip markdown formatting for comparison
        valA = stripMarkdown(valA);
        valB = stripMarkdown(valB);

        // Handle different data types
        if (col.type === 'number') {
            valA = parseFloat(valA) || 0;
            valB = parseFloat(valB) || 0;
        } else if (col.type === 'date') {
            valA = new Date(valA).getTime() || 0;
            valB = new Date(valB).getTime() || 0;
        } else {
            // Text comparison (case-insensitive)
            valA = String(valA).toLowerCase();
            valB = String(valB).toLowerCase();
        }

        if (direction === 'asc') {
            return valA > valB ? 1 : valA < valB ? -1 : 0;
        } else {
            return valA < valB ? 1 : valA > valB ? -1 : 0;
        }
    });

    // Rebuild rows and cell styles with new order
    const newRows = rowsWithIndices.map(item => item.row);
    const newCellStyles = {};

    rowsWithIndices.forEach((item, newIndex) => {
        // Map old cell styles to new row indices
        Object.keys(item.cellStyles).forEach(oldKey => {
            const colIdx = oldKey.split('-')[1];
            const newKey = `${newIndex}-${colIdx}`;
            newCellStyles[newKey] = item.cellStyles[oldKey];
        });
    });

    sheet.rows = newRows;
    if (Object.keys(newCellStyles).length > 0) {
        sheet.cellStyles = newCellStyles;
    }

    renderTable();
    showToast(`Sorted by ${col.name} (${direction === 'asc' ? 'A-Z' : 'Z-A'})`, 'success');
}

function moveColumn(colIndex, direction) {
    const sheet = tableData.sheets[currentSheet];
    const newIndex = direction === 'left' ? colIndex - 1 : colIndex + 1;

    // Check bounds
    if (newIndex < 0 || newIndex >= sheet.columns.length) {
        return;
    }

    // Swap columns
    [sheet.columns[colIndex], sheet.columns[newIndex]] = [sheet.columns[newIndex], sheet.columns[colIndex]];

    // Swap column data in all rows
    sheet.rows.forEach(row => {
        [row[colIndex], row[newIndex]] = [row[newIndex], row[colIndex]];
    });

    // Swap cell styles
    if (sheet.cellStyles) {
        const newCellStyles = {};
        Object.keys(sheet.cellStyles).forEach(key => {
            const [rowIdx, colIdx] = key.split('-').map(Number);
            let newColIdx = colIdx;

            if (colIdx === colIndex) {
                newColIdx = newIndex;
            } else if (colIdx === newIndex) {
                newColIdx = colIndex;
            }

            newCellStyles[`${rowIdx}-${newColIdx}`] = sheet.cellStyles[key];
        });
        sheet.cellStyles = newCellStyles;
    }

    renderTable();
    showToast(`Column moved ${direction}`, 'success');
}

// Close modal and dropdowns when clicking outside
window.onclick = function (event) {
    const columnModal = document.getElementById('columnModal');
    const renameModal = document.getElementById('renameModal');
    const settingsModal = document.getElementById('settingsModal');
    const sheetList = document.getElementById('sheetList');

    if (event.target === columnModal) {
        closeColumnModal();
    }
    if (event.target === renameModal) {
        closeRenameModal();
    }
    if (event.target === settingsModal) {
        closeSettingsModal();
    }

    // Close sheet list when clicking outside
    if (!event.target.closest('.sheet-selector')) {
        sheetList.classList.remove('show');
    }

    // Close column menus when clicking outside
    if (!event.target.closest('.column-menu-wrapper')) {
        closeAllColumnMenus();
    }

    // Close cell context menu when clicking outside
    if (!event.target.closest('#cellContextMenu')) {
        closeCellContextMenu();
    }
};

// F1 Quick Navigation Popup Functions
let selectedF1Category = null;

function openF1Popup() {
    const popup = document.getElementById('f1Popup');
    popup.classList.add('show');

    // Set selected category to current category
    selectedF1Category = currentCategory;

    // Populate categories and sheets
    populateF1Categories();
    populateF1Sheets();

    // Focus search input
    setTimeout(() => {
        const searchInput = document.getElementById('f1SearchInput');
        if (searchInput) {
            searchInput.focus();
        }
    }, 100);
}

function closeF1Popup() {
    const popup = document.getElementById('f1Popup');
    popup.classList.remove('show');

    // Clear search
    const searchInput = document.getElementById('f1SearchInput');
    if (searchInput) {
        searchInput.value = '';
    }

    // Reset filter
    filterF1Sheets();
}

// F2 Popup - Recent Sheets
function openF2Popup() {
    const popup = document.getElementById('f2Popup');
    popup.classList.add('show');

    // Populate recent sheets
    populateF2RecentSheets();

    // Focus on first sheet
    setTimeout(() => {
        const firstSheet = popup.querySelector('.f2-sheet-item');
        if (firstSheet) {
            firstSheet.focus();
        }
    }, 100);

    // Add click-outside-to-close listener
    setTimeout(() => {
        document.addEventListener('click', closeF2PopupOnClickOutside);
    }, 100);
}

function closeF2Popup() {
    const popup = document.getElementById('f2Popup');
    popup.classList.remove('show');
    document.removeEventListener('click', closeF2PopupOnClickOutside);
}

function closeF2PopupOnClickOutside(event) {
    const overlay = document.getElementById('f2Popup');
    if (overlay && overlay.classList.contains('show')) {
        // Close if clicking on the overlay itself (not the inner popup)
        if (event.target === overlay) {
            closeF2Popup();
        }
    }
}

function populateF2RecentSheets() {
    const container = document.getElementById('f2SheetsList');
    container.innerHTML = '';

    // Get recent sheets from history (stored by Alt+M toggle)
    const savedHistory = localStorage.getItem('sheetHistory');
    let recentSheets = [];
    let allSheetIndices = [];

    // Get all sheet indices
    tableData.sheets.forEach((sheet, index) => {
        allSheetIndices.push(index);
    });

    if (savedHistory) {
        try {
            const history = JSON.parse(savedHistory);
            // Filter out invalid sheet indices and reverse to show most recent first
            recentSheets = history.filter(idx => idx >= 0 && idx < tableData.sheets.length).reverse();

            // Add current sheet at the beginning if not already there
            if (!recentSheets.includes(currentSheet)) {
                recentSheets.unshift(currentSheet);
            } else {
                // Move current sheet to the beginning
                recentSheets = recentSheets.filter(idx => idx !== currentSheet);
                recentSheets.unshift(currentSheet);
            }

            // Add any sheets not in history to the end
            allSheetIndices.forEach(idx => {
                if (!recentSheets.includes(idx)) {
                    recentSheets.push(idx);
                }
            });
        } catch (e) {
            recentSheets = allSheetIndices;
        }
    } else {
        // No history, show current sheet first, then all others
        recentSheets = [currentSheet, ...allSheetIndices.filter(idx => idx !== currentSheet)];
    }

    // Display all sheets ordered by recency
    recentSheets.forEach((sheetIndex, index) => {
        const sheet = tableData.sheets[sheetIndex];
        if (!sheet) return;

        const item = document.createElement('div');
        item.className = 'f2-sheet-item';
        item.tabIndex = 0;

        if (sheetIndex === currentSheet) {
            item.classList.add('active');
        }

        const number = document.createElement('div');
        number.className = 'f2-sheet-number';
        number.textContent = `#${index + 1}`;

        const name = document.createElement('div');
        name.className = 'f2-sheet-name';
        name.textContent = sheet.name; // Use real name, not nickname

        item.appendChild(number);
        item.appendChild(name);

        item.onclick = () => {
            switchSheet(sheetIndex);
            closeF2Popup();
        };

        item.onkeydown = (e) => {
            if (e.key === 'Enter') {
                switchSheet(sheetIndex);
                closeF2Popup();
            }
        };

        container.appendChild(item);
    });

    if (container.children.length === 0) {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;">No sheets available</div>';
    }
}

// Quick Markdown Formatter (F3)
let quickFormatterTarget = null;
let quickFormatterSelection = { start: 0, end: 0 };

let selectedFormats = []; // Track selected formats for multi-apply

function showQuickFormatter(inputElement) {
    quickFormatterTarget = inputElement;
    quickFormatterSelection = {
        start: inputElement.selectionStart,
        end: inputElement.selectionEnd
    };

    // Clear selected formats when opening
    selectedFormats = [];
    updateFormatCheckmarks();

    const formatter = document.getElementById('quickFormatter');
    const colorSection = document.getElementById('colorPickerSection');

    // Show color section by default
    colorSection.style.display = 'block';
    loadColorSwatches();

    // Update selection stats
    updateSelectionStats(inputElement);

    // Show formatter first to get its dimensions
    formatter.style.display = 'block';

    // Center it on the screen
    setTimeout(() => {
        const formatterRect = formatter.getBoundingClientRect();
        const centerX = (window.innerWidth - formatterRect.width) / 2;
        const centerY = (window.innerHeight - formatterRect.height) / 2;

        formatter.style.left = Math.max(20, centerX) + 'px';
        formatter.style.top = Math.max(20, centerY) + 'px';
    }, 0);

    // Add click-outside-to-close listener
    setTimeout(() => {
        document.addEventListener('click', closeQuickFormatterOnClickOutside);
    }, 100);
}

function closeQuickFormatterOnClickOutside(event) {
    const formatter = document.getElementById('quickFormatter');
    if (formatter && formatter.style.display === 'block') {
        if (!formatter.contains(event.target)) {
            closeQuickFormatter();
            document.removeEventListener('click', closeQuickFormatterOnClickOutside);
        }
    }
}

function updateSelectionStats(inputElement) {
    const selectedText = inputElement.value.substring(
        inputElement.selectionStart,
        inputElement.selectionEnd
    );

    // Count lines
    const lines = selectedText.split('\n');
    const lineCount = lines.length;

    // Count words (split by whitespace and filter empty strings)
    const words = selectedText.trim().split(/\s+/).filter(word => word.length > 0);
    const wordCount = words.length;

    // Count characters
    const charCount = selectedText.length;

    // Update the stats display
    const statsElement = document.getElementById('selectionStats');
    if (statsElement) {
        statsElement.textContent = `${lineCount} line${lineCount !== 1 ? 's' : ''} • ${wordCount} word${wordCount !== 1 ? 's' : ''} • ${charCount} char${charCount !== 1 ? 's' : ''}`;
    }
}

function closeQuickFormatter() {
    const formatter = document.getElementById('quickFormatter');
    formatter.style.display = 'none';
    quickFormatterTarget = null;
    selectedFormats = [];
    document.removeEventListener('click', closeQuickFormatterOnClickOutside);
}

function selectAllMatchingFromFormatter(event) {
    event.preventDefault();
    event.stopPropagation();

    if (!quickFormatterTarget) {
        console.log('No quickFormatterTarget');
        return;
    }

    // Store the target and selection
    const target = quickFormatterTarget;
    const selection = quickFormatterSelection;

    // Keep the input focused and restore selection
    target.focus();
    target.setSelectionRange(selection.start, selection.end);

    // Select all matching occurrences
    selectAllMatchingOccurrences(target);

    // Close the formatter after selection is done
    setTimeout(() => {
        closeQuickFormatter();
    }, 50);
}

function toggleFormatSelection(prefix, suffix, event) {
    event.preventDefault();

    const formatKey = `${prefix}|${suffix}`;
    const index = selectedFormats.findIndex(f => f.key === formatKey);

    if (index >= 0) {
        // Remove if already selected
        selectedFormats.splice(index, 1);
    } else {
        // Add to selection
        selectedFormats.push({ key: formatKey, prefix, suffix });
    }

    updateFormatCheckmarks();
    return false;
}

function updateFormatCheckmarks() {
    // Remove all existing checkmarks
    document.querySelectorAll('.format-checkmark').forEach(el => el.remove());

    // Add checkmarks to selected formats
    selectedFormats.forEach(format => {
        const buttons = document.querySelectorAll('.format-btn');
        buttons.forEach(btn => {
            const onclick = btn.getAttribute('onclick');
            if (onclick && onclick.includes(`'${format.prefix}'`) && onclick.includes(`'${format.suffix}'`)) {
                if (!btn.querySelector('.format-checkmark')) {
                    const checkmark = document.createElement('span');
                    checkmark.className = 'format-checkmark';
                    checkmark.textContent = '✓';
                    btn.appendChild(checkmark);
                }
            }
        });
    });
}

function applyQuickFormat(prefix, suffix, event) {
    if (event && event.preventDefault) {
        event.preventDefault();
        event.stopPropagation();
    }

    if (!quickFormatterTarget) return;

    // If there are selected formats, apply all of them plus this one
    if (selectedFormats.length > 0) {
        applyMultipleFormats(prefix, suffix);
        return;
    }

    // Otherwise, apply single format as before
    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    // Insert the markdown syntax
    const newText = input.value.substring(0, start) +
        prefix + selectedText + suffix +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position after the inserted text
    const newCursorPos = start + prefix.length + selectedText.length + suffix.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast('Format applied', 'success');
}

function applyLinkFormat(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedUrl = input.value.substring(start, end);

    // Use default placeholder text with italic formatting
    const linkText = '@@Link@@';

    // Insert the link syntax: {link:url}@@Link@@{/}
    const newText = input.value.substring(0, start) +
        `{link:${selectedUrl}}` + linkText + '{/}' +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position after the inserted text
    const linkPrefix = `{link:${selectedUrl}}`;
    const newCursorPos = start + linkPrefix.length + linkText.length + 3;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast('Link applied', 'success');
}

function searchGoogle(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Strip markdown formatting before searching
    const cleanText = stripMarkdown(selectedText);

    // Open Google search in new tab
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(cleanText)}`;
    window.open(searchUrl, '_blank');

    closeQuickFormatter();
    showToast('Searching in Google', 'success');
}



function linesToComma(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Split into lines, remove leading dashes and trim, filter empty lines
    const lines = selectedText.split('\n')
        .map(line => line.replace(/^[-–—•]\s*/, '').trim())
        .filter(line => line.length > 0);

    // Join with comma and space
    const commaText = lines.join(', ');

    // Replace the selected text
    const newText = input.value.substring(0, start) +
        commaText +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Select the result
    input.setSelectionRange(start, start + commaText.length);
    input.focus();

    closeQuickFormatter();
    showToast(`Converted ${lines.length} lines to comma-separated`, 'success');
}

function commaToLines(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Split by comma, trim each item, filter empty items
    const items = selectedText.split(',')
        .map(item => item.trim())
        .filter(item => item.length > 0);

    // Join with newlines
    const linesText = items.join('\n');

    // Replace the selected text
    const newText = input.value.substring(0, start) +
        linesText +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Select the result
    input.setSelectionRange(start, start + linesText.length);
    input.focus();

    closeQuickFormatter();
    showToast(`Converted to ${items.length} lines`, 'success');
}

function applyMultipleFormats(lastPrefix, lastSuffix) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    let selectedText = input.value.substring(start, end);

    // Build the complete format string with all selected formats plus the last one
    let allPrefixes = '';
    let allSuffixes = '';

    // Add all selected formats
    selectedFormats.forEach(format => {
        allPrefixes += format.prefix;
        allSuffixes = format.suffix + allSuffixes; // Reverse order for closing tags
    });

    // Add the last clicked format
    allPrefixes += lastPrefix;
    allSuffixes = lastSuffix + allSuffixes;

    // Insert the markdown syntax
    const newText = input.value.substring(0, start) +
        allPrefixes + selectedText + allSuffixes +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position after the inserted text
    const newCursorPos = start + allPrefixes.length + selectedText.length + allSuffixes.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast(`Applied ${selectedFormats.length + 1} formats`, 'success');
}

function showColorPicker(event) {
    if (event) {
        event.preventDefault();
    }

    const colorSection = document.getElementById('colorPickerSection');
    const isShowing = colorSection.style.display === 'none';
    colorSection.style.display = isShowing ? 'block' : 'none';

    if (isShowing) {
        loadColorSwatches();
    }
}

function toggleColorSelection(event) {
    event.preventDefault();

    // Toggle color picker visibility for selection
    showColorPicker(event);

    return false;
}

// Load and display color swatches
function loadColorSwatches() {
    const swatchesContainer = document.getElementById('colorSwatches');
    swatchesContainer.innerHTML = '';

    // Default presets
    const defaultSwatches = [
        { fg: '#ffffff', bg: '#000000' }, // White on Black
        { fg: '#000000', bg: '#ffff00' }, // Black on Yellow
        { fg: '#ffffff', bg: '#ff0000' }, // White on Red
        { fg: '#000000', bg: '#00ff00' }, // Black on Green
        { fg: '#ffffff', bg: '#0000ff' }, // White on Blue
        { fg: '#000000', bg: '#ffa500' }, // Black on Orange
        { fg: '#ffffff', bg: '#800080' }, // White on Purple
    ];

    // Load saved swatches from localStorage
    const savedSwatches = JSON.parse(localStorage.getItem('colorSwatches') || '[]');
    const allSwatches = [...savedSwatches, ...defaultSwatches];

    allSwatches.forEach((swatch, index) => {
        const swatchBtn = document.createElement('button');
        swatchBtn.className = 'color-swatch';

        // Show visual indicator if noBg is set
        if (swatch.noBg) {
            swatchBtn.style.background = 'transparent';
            swatchBtn.style.border = '2px dashed #999';
        } else {
            swatchBtn.style.background = swatch.bg;
        }
        swatchBtn.style.color = swatch.fg;
        swatchBtn.textContent = 'Aa';

        const bgText = swatch.noBg ? 'No BG' : swatch.bg;
        swatchBtn.title = `Text: ${swatch.fg}, Background: ${bgText}`;

        swatchBtn.onclick = () => {
            document.getElementById('quickFgColor').value = swatch.fg;
            document.getElementById('quickBgColor').value = swatch.bg;
            document.getElementById('noBgCheckbox').checked = swatch.noBg || false;
        };

        // Add delete button for saved swatches
        if (index < savedSwatches.length) {
            const deleteBtn = document.createElement('span');
            deleteBtn.className = 'swatch-delete';
            deleteBtn.textContent = '×';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteSwatch(index);
            };
            swatchBtn.appendChild(deleteBtn);
        }

        swatchesContainer.appendChild(swatchBtn);
    });
}

function addCurrentColorToSwatches() {
    const fgColor = document.getElementById('quickFgColor').value;
    const bgColor = document.getElementById('quickBgColor').value;
    const noBgCheckbox = document.getElementById('noBgCheckbox');
    const noBg = noBgCheckbox.checked;

    const savedSwatches = JSON.parse(localStorage.getItem('colorSwatches') || '[]');

    // Check if already exists
    const exists = savedSwatches.some(s => s.fg === fgColor && s.bg === bgColor && s.noBg === noBg);
    if (exists) {
        showToast('Color combination already saved', 'info');
        return;
    }

    savedSwatches.unshift({ fg: fgColor, bg: bgColor, noBg: noBg });

    // Keep only last 6 custom swatches
    if (savedSwatches.length > 6) {
        savedSwatches.pop();
    }

    localStorage.setItem('colorSwatches', JSON.stringify(savedSwatches));
    loadColorSwatches();
    showToast('Color saved to presets', 'success');
}

function deleteSwatch(index) {
    const savedSwatches = JSON.parse(localStorage.getItem('colorSwatches') || '[]');
    savedSwatches.splice(index, 1);
    localStorage.setItem('colorSwatches', JSON.stringify(savedSwatches));
    loadColorSwatches();
    showToast('Color preset deleted', 'success');
}

function applyColorFormat() {
    if (!quickFormatterTarget) return;

    const fgColor = document.getElementById('quickFgColor').value;
    const bgColor = document.getElementById('quickBgColor').value;
    const noBgCheckbox = document.getElementById('noBgCheckbox');
    const useBg = !noBgCheckbox.checked;

    // Build color syntax
    let colorSyntax = '{';
    if (fgColor !== '#000000') {
        colorSyntax += `fg:${fgColor}`;
    }
    if (useBg && bgColor !== '#ffff00') {
        if (colorSyntax.length > 1) colorSyntax += ';';
        colorSyntax += `bg:${bgColor}`;
    }
    colorSyntax += '}';

    // If there are selected formats, apply all of them plus color
    if (selectedFormats.length > 0) {
        applyMultipleFormatsWithColor(colorSyntax);
        return;
    }

    // Otherwise, apply color format alone
    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    // Insert the color syntax
    const newText = input.value.substring(0, start) +
        colorSyntax + selectedText + '{/}' +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position
    const newCursorPos = start + colorSyntax.length + selectedText.length + 3;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast('Color format applied', 'success');
}

function applyMultipleFormatsWithColor(colorSyntax) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    let selectedText = input.value.substring(start, end);

    // Build the complete format string with all selected formats plus color
    let allPrefixes = colorSyntax; // Color goes first
    let allSuffixes = '{/}'; // Color closing

    // Add all selected markdown formats
    selectedFormats.forEach(format => {
        allPrefixes += format.prefix;
        allSuffixes = format.suffix + allSuffixes; // Reverse order for closing tags
    });

    // Insert the markdown syntax
    const newText = input.value.substring(0, start) +
        allPrefixes + selectedText + allSuffixes +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position after the inserted text
    const newCursorPos = start + allPrefixes.length + selectedText.length + allSuffixes.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast(`Applied color + ${selectedFormats.length} formats`, 'success');
}

// Multi-Selection (Ctrl+D) - Select Next Occurrence
let multiSelectionData = null;

function selectAllMatchingOccurrences(input) {
    const text = input.value;
    const selStart = input.selectionStart;
    const selEnd = input.selectionEnd;
    let selectedText;

    // If no selection, select the word under cursor
    if (selStart === selEnd) {
        const wordBoundary = /\W/;
        let start = selStart;
        let end = selStart;

        // Find word start
        while (start > 0 && !wordBoundary.test(text[start - 1])) {
            start--;
        }

        // Find word end
        while (end < text.length && !wordBoundary.test(text[end])) {
            end++;
        }

        if (start < end) {
            selectedText = text.substring(start, end);
            input.setSelectionRange(start, end);
        } else {
            return;
        }
    } else {
        selectedText = text.substring(selStart, selEnd);
    }

    if (!selectedText) return;

    // Find all occurrences
    const matches = [];
    let index = 0;
    while ((index = text.indexOf(selectedText, index)) !== -1) {
        matches.push({ start: index, end: index + selectedText.length });
        index += selectedText.length;
    }

    if (matches.length === 0) return;

    // Initialize multi-selection with all matches selected
    multiSelectionData = {
        input: input,
        searchText: selectedText,
        matches: matches,
        currentIndex: matches.length - 1,
        selectedMatches: matches,
        allSelected: true,
        listenerSetup: false
    };

    // Select the last match visually
    const lastMatch = matches[matches.length - 1];
    input.setSelectionRange(lastMatch.start, lastMatch.end);

    // Show indicator
    showMultiSelectionIndicator(input, matches.length, matches.length);
    showToast(`All ${matches.length} occurrences selected. Type to replace all.`, 'info');

    // Show visual markers for all selections
    showSelectionMarkers(input, matches);

    // Set up the listener for replacement
    setupMultiReplaceListener(input);
    multiSelectionData.listenerSetup = true;
}

function selectNextOccurrence(input) {
    const text = input.value;
    const selStart = input.selectionStart;
    const selEnd = input.selectionEnd;

    // If no selection, select the word under cursor
    if (selStart === selEnd) {
        const wordBoundary = /\W/;
        let start = selStart;
        let end = selStart;

        // Find word start
        while (start > 0 && !wordBoundary.test(text[start - 1])) {
            start--;
        }

        // Find word end
        while (end < text.length && !wordBoundary.test(text[end])) {
            end++;
        }

        if (start < end) {
            input.setSelectionRange(start, end);
            initMultiSelection(input, text.substring(start, end));
            return;
        }
    }

    const selectedText = text.substring(selStart, selEnd);
    if (!selectedText) return;

    // Initialize or continue multi-selection
    if (!multiSelectionData || multiSelectionData.input !== input || multiSelectionData.searchText !== selectedText) {
        initMultiSelection(input, selectedText);
    } else {
        selectNextMatch(input);
    }
}

function initMultiSelection(input, searchText) {
    const text = input.value;
    const matches = [];
    let index = 0;

    // Find all occurrences
    while ((index = text.indexOf(searchText, index)) !== -1) {
        matches.push({ start: index, end: index + searchText.length });
        index += searchText.length;
    }

    multiSelectionData = {
        input: input,
        searchText: searchText,
        matches: matches,
        currentIndex: 0,
        selectedMatches: [matches[0]],
        listenerSetup: false
    };

    // Highlight first match
    if (matches.length > 0) {
        input.setSelectionRange(matches[0].start, matches[0].end);
        showMultiSelectionIndicator(input, 1, matches.length);
    }

    // Don't set up listener yet - wait until user starts typing or selects all
}

function selectNextMatch(input) {
    if (!multiSelectionData || multiSelectionData.matches.length === 0) return;

    multiSelectionData.currentIndex++;
    if (multiSelectionData.currentIndex >= multiSelectionData.matches.length) {
        // All selected, show message
        showToast(`All ${multiSelectionData.matches.length} occurrences selected. Type to replace all.`, 'info');
        multiSelectionData.allSelected = true;

        // Now set up the listener for replacement
        if (!multiSelectionData.listenerSetup) {
            setupMultiReplaceListener(input);
            multiSelectionData.listenerSetup = true;
        }
        return;
    }

    const nextMatch = multiSelectionData.matches[multiSelectionData.currentIndex];
    multiSelectionData.selectedMatches.push(nextMatch);

    // Select the next match
    input.setSelectionRange(nextMatch.start, nextMatch.end);
    showMultiSelectionIndicator(input, multiSelectionData.currentIndex + 1, multiSelectionData.matches.length);

    // Show visual markers for all selections
    showSelectionMarkers(input, multiSelectionData.selectedMatches);
}

function showMultiSelectionIndicator(input, current, total) {
    // Create or update indicator
    let indicator = document.getElementById('multiSelectionIndicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'multiSelectionIndicator';
        indicator.className = 'multi-selection-indicator';
        document.body.appendChild(indicator);
    }

    indicator.textContent = `${current} of ${total} selected`;
    indicator.style.display = 'block';

    // Position near the input
    const rect = input.getBoundingClientRect();
    indicator.style.left = rect.right + 10 + 'px';
    indicator.style.top = rect.top + 'px';

    // Auto-hide after 2 seconds
    clearTimeout(indicator.hideTimeout);
    indicator.hideTimeout = setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

function setupMultiReplaceListener(input) {
    // Store the original ranges (these stay constant as reference points)
    multiSelectionData.originalRanges = multiSelectionData.matches.map(m => ({
        start: m.start,
        end: m.end,
        originalText: input.value.substring(m.start, m.end)
    }));
    multiSelectionData.currentText = input.value;

    // Remove old listeners if exist
    if (input.multiReplaceKeyListener) {
        input.removeEventListener('keydown', input.multiReplaceKeyListener);
    }

    // Keydown listener to handle all keys
    input.multiReplaceKeyListener = function (e) {
        if (!multiSelectionData || multiSelectionData.input !== input) return;

        // Handle selection extension keys (Shift+End, Shift+Home, etc.)
        if (e.shiftKey && (e.key === 'End' || e.key === 'Home' || e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
            e.preventDefault();
            handleMultiSelectionExtension(input, e.key);
            return;
        }

        // Allow other navigation keys to clear multi-selection
        const navigationKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End', 'PageUp', 'PageDown'];
        if (navigationKeys.includes(e.key)) {
            // Clear multi-selection mode when navigating without shift
            clearMultiSelection();
            return;
        }

        // Handle Backspace and Delete
        if (e.key === 'Backspace' || e.key === 'Delete') {
            e.preventDefault();
            handleMultiCursorEdit(input, e.key === 'Backspace' ? 'backspace' : 'delete', '');
            return;
        }

        // Handle Enter
        if (e.key === 'Enter') {
            e.preventDefault();
            handleMultiCursorEdit(input, 'insert', '\n');
            return;
        }

        // Handle Escape to finish
        if (e.key === 'Escape') {
            const count = multiSelectionData.matches.length;
            clearMultiSelection();
            showToast(`Edited ${count} locations`, 'success');
            return;
        }

        // Handle regular character input
        if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            handleMultiCursorEdit(input, 'insert', e.key);
            return;
        }
    };

    input.addEventListener('keydown', input.multiReplaceKeyListener);

    // Clear on blur
    input.addEventListener('blur', function clearOnBlur() {
        setTimeout(() => {
            if (multiSelectionData) {
                const count = multiSelectionData.matches.length;
                clearMultiSelection();
                if (input.multiReplaceKeyListener) {
                    input.removeEventListener('keydown', input.multiReplaceKeyListener);
                }
                showToast(`Edited ${count} locations`, 'success');
            }
        }, 100);
    }, { once: true });
}

function handleMultiCursorEdit(input, action, char) {
    if (!multiSelectionData) return;

    const text = input.value;
    let result = text;

    // Sort matches from right to left to maintain positions during replacement
    const sortedMatches = [...multiSelectionData.matches].sort((a, b) => b.start - a.start);

    // Apply the edit to each match (processing right to left)
    for (const match of sortedMatches) {
        if (action === 'insert') {
            // Insert character and replace selection
            result = result.substring(0, match.start) + char + result.substring(match.end);
        } else if (action === 'backspace') {
            // Delete selection or character before cursor
            if (match.start === match.end) {
                // No selection, delete character before
                if (match.start > 0) {
                    result = result.substring(0, match.start - 1) + result.substring(match.start);
                }
            } else {
                // Delete selection
                result = result.substring(0, match.start) + result.substring(match.end);
            }
        } else if (action === 'delete') {
            // Delete selection or character after cursor
            if (match.start === match.end) {
                // No selection, delete character after
                if (match.end < result.length) {
                    result = result.substring(0, match.start) + result.substring(match.start + 1);
                }
            } else {
                // Delete selection
                result = result.substring(0, match.start) + result.substring(match.end);
            }
        }
    }

    input.value = result;
    multiSelectionData.currentText = result;

    // Recalculate match positions (process in original order, left to right)
    let offset = 0;
    const newMatches = [];

    for (let i = 0; i < multiSelectionData.matches.length; i++) {
        const oldMatch = multiSelectionData.matches[i];
        const oldLength = oldMatch.end - oldMatch.start;
        let newLength = 0;
        let offsetChange = 0;

        if (action === 'insert') {
            // Cursor moves to after inserted text  
            const newPos = oldMatch.start + offset + char.length;
            newMatches.push({ start: newPos, end: newPos });
            offsetChange = char.length - oldLength;
            offset += offsetChange;
            continue;
        } else if (action === 'backspace') {
            if (oldLength === 0) {
                // Deleted one char before cursor
                offsetChange = -1;
            } else {
                // Deleted selection
                offsetChange = -oldLength;
            }
            newLength = 0;
        } else if (action === 'delete') {
            if (oldLength === 0) {
                // Deleted one char after cursor (position stays same)
                offsetChange = -1;
            } else {
                // Deleted selection
                offsetChange = -oldLength;
            }
            newLength = 0;
        }

        const newStart = oldMatch.start + offset;
        const newEnd = newStart + newLength;

        newMatches.push({ start: newStart, end: newEnd });

        // Update offset for next match
        offset += offsetChange;
    }

    multiSelectionData.matches = newMatches;

    // Position cursor at the last match
    const lastMatch = newMatches[newMatches.length - 1];
    input.setSelectionRange(lastMatch.end, lastMatch.end);

    // Show visual markers
    showSelectionMarkers(input, newMatches);

    // Trigger change event
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);
}

function handleMultiSelectionExtension(input, key) {
    if (!multiSelectionData || !multiSelectionData.allSelected) return;

    const text = input.value;
    const lines = text.split('\n');
    let currentPos = 0;
    const lineStarts = [0];

    // Build line start positions
    for (let i = 0; i < lines.length - 1; i++) {
        currentPos += lines[i].length + 1; // +1 for newline
        lineStarts.push(currentPos);
    }

    // Extend each match based on the key
    const newMatches = multiSelectionData.matches.map(match => {
        let newEnd = match.end;
        let newStart = match.start;

        if (key === 'End') {
            // Find which line this match is on
            const lineIndex = lineStarts.findIndex((start, idx) => {
                const nextStart = lineStarts[idx + 1] || text.length;
                return match.start >= start && match.start < nextStart;
            });

            if (lineIndex !== -1) {
                const nextLineStart = lineStarts[lineIndex + 1];
                newEnd = nextLineStart ? nextLineStart - 1 : text.length;
            }
        } else if (key === 'Home') {
            // Find which line this match is on
            const lineIndex = lineStarts.findIndex((start, idx) => {
                const nextStart = lineStarts[idx + 1] || text.length;
                return match.start >= start && match.start < nextStart;
            });

            if (lineIndex !== -1) {
                newStart = lineStarts[lineIndex];
            }
        } else if (key === 'ArrowRight') {
            newEnd = Math.min(text.length, match.end + 1);
        } else if (key === 'ArrowLeft') {
            newStart = Math.max(0, match.start - 1);
        }

        return { start: newStart, end: newEnd };
    });

    // Update the matches
    multiSelectionData.matches = newMatches;
    multiSelectionData.selectedMatches = newMatches;

    // Update search text to the new extended selection (use first match as reference)
    const firstMatch = newMatches[0];
    multiSelectionData.searchText = text.substring(firstMatch.start, firstMatch.end);
    multiSelectionData.originalText = text;
    multiSelectionData.replacementText = '';

    // Visually select the last match
    const lastMatch = newMatches[newMatches.length - 1];
    input.setSelectionRange(lastMatch.start, lastMatch.end);

    // Show visual markers for all selections
    showSelectionMarkers(input, newMatches);
    showMultiSelectionIndicator(input, newMatches.length, newMatches.length);
}

function clearMultiSelection() {
    multiSelectionData = null;
    const indicator = document.getElementById('multiSelectionIndicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
    clearVisualMarkers();
}

// Visual markers for multi-selection and multi-cursor
function measureText(text, font) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    context.font = font;
    return context.measureText(text).width;
}

function showSelectionMarkers(input, selections) {
    clearVisualMarkers();

    const cell = input.closest('td');
    if (!cell) return;

    // Create overlay container
    let overlay = document.createElement('div');
    overlay.className = 'multi-cursor-overlay';
    overlay.id = 'multiCursorOverlay';

    // Copy input styles
    const computedStyle = window.getComputedStyle(input);
    const inputRect = input.getBoundingClientRect();
    const cellRect = cell.getBoundingClientRect();

    overlay.style.position = 'absolute';
    overlay.style.top = (inputRect.top - cellRect.top) + 'px';
    overlay.style.left = (inputRect.left - cellRect.left) + 'px';
    overlay.style.width = input.offsetWidth + 'px';
    overlay.style.height = input.offsetHeight + 'px';

    const text = input.value;
    const lineHeight = parseFloat(computedStyle.lineHeight) || 20;
    const paddingLeft = parseFloat(computedStyle.paddingLeft) || 4;
    const paddingTop = parseFloat(computedStyle.paddingTop) || 4;
    const font = `${computedStyle.fontSize} ${computedStyle.fontFamily}`;

    // Create markers for each selection
    selections.forEach((sel, index) => {
        if (index === selections.length - 1) return; // Skip last one (native selection shows it)

        const beforeText = text.substring(0, sel.start);
        const selectedText = text.substring(sel.start, sel.end);

        // Calculate position
        const lines = beforeText.split('\n');
        const lineNum = lines.length - 1;
        const lineText = lines[lines.length - 1];

        // Measure actual text width
        const x = paddingLeft + measureText(lineText, font);
        const y = paddingTop + lineNum * lineHeight;
        const width = measureText(selectedText, font);

        // Create selection marker
        const marker = document.createElement('div');
        marker.className = 'selection-marker';
        marker.style.left = x + 'px';
        marker.style.top = y + 'px';
        marker.style.width = width + 'px';
        marker.style.height = lineHeight + 'px';

        overlay.appendChild(marker);
    });

    cell.style.position = 'relative';
    cell.appendChild(overlay);
}

function showCursorMarkers(textarea, cursors) {
    clearVisualMarkers();

    const cell = textarea.closest('td');
    if (!cell) return;

    // Create overlay container
    let overlay = document.createElement('div');
    overlay.className = 'multi-cursor-overlay';
    overlay.id = 'multiCursorOverlay';

    // Copy textarea styles
    const computedStyle = window.getComputedStyle(textarea);
    const textareaRect = textarea.getBoundingClientRect();
    const cellRect = cell.getBoundingClientRect();

    overlay.style.position = 'absolute';
    overlay.style.top = (textareaRect.top - cellRect.top) + 'px';
    overlay.style.left = (textareaRect.left - cellRect.left) + 'px';
    overlay.style.width = textarea.offsetWidth + 'px';
    overlay.style.height = textarea.offsetHeight + 'px';

    const text = textarea.value;
    const lines = text.split('\n');
    const lineHeight = parseFloat(computedStyle.lineHeight) || 20;
    const paddingLeft = parseFloat(computedStyle.paddingLeft) || 4;
    const paddingTop = parseFloat(computedStyle.paddingTop) || 4;
    const font = `${computedStyle.fontSize} ${computedStyle.fontFamily}`;

    // Create markers for each cursor
    cursors.forEach((cursor, index) => {
        if (index === cursors.length - 1) return; // Skip last one (native cursor shows it)

        const lineNum = cursor.line - 1;
        if (lineNum < lines.length) {
            const lineText = lines[lineNum].substring(0, cursor.column);
            const x = paddingLeft + measureText(lineText, font);
            const y = paddingTop + lineNum * lineHeight;

            // Create cursor marker
            const marker = document.createElement('div');
            marker.className = 'cursor-marker';
            marker.style.left = x + 'px';
            marker.style.top = y + 'px';
            marker.style.height = lineHeight + 'px';

            overlay.appendChild(marker);
        }
    });

    cell.style.position = 'relative';
    cell.appendChild(overlay);
}

function clearVisualMarkers() {
    const overlay = document.getElementById('multiCursorOverlay');
    if (overlay) {
        overlay.remove();
    }
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Multi-Line Cursor (Ctrl+Alt+Down/Up)
let multiLineCursorData = null;

function addCursorBelow(textarea) {
    const text = textarea.value;
    const cursorPos = textarea.selectionStart;

    // Find current line
    const beforeCursor = text.substring(0, cursorPos);
    const currentLineStart = beforeCursor.lastIndexOf('\n') + 1;
    const afterCursor = text.substring(cursorPos);
    const currentLineEnd = afterCursor.indexOf('\n');
    const nextLineStart = currentLineEnd === -1 ? text.length : cursorPos + currentLineEnd + 1;

    // Calculate column position
    const columnPos = cursorPos - currentLineStart;

    // Initialize or add to multi-cursor
    if (!multiLineCursorData || multiLineCursorData.textarea !== textarea) {
        multiLineCursorData = {
            textarea: textarea,
            cursors: [{ line: getCurrentLineNumber(text, cursorPos), column: columnPos, pos: cursorPos }]
        };
    }

    // Find next line
    if (nextLineStart < text.length) {
        const nextLineEnd = text.indexOf('\n', nextLineStart);
        const nextLineLength = nextLineEnd === -1 ? text.length - nextLineStart : nextLineEnd - nextLineStart;
        const nextCursorPos = nextLineStart + Math.min(columnPos, nextLineLength);

        multiLineCursorData.cursors.push({
            line: getCurrentLineNumber(text, nextCursorPos),
            column: columnPos,
            pos: nextCursorPos
        });

        // Move cursor to new position
        textarea.setSelectionRange(nextCursorPos, nextCursorPos);

        showMultiCursorIndicator(textarea, multiLineCursorData.cursors.length);
        // showCursorMarkers(textarea, multiLineCursorData.cursors); // Disabled - only show main cursor
        setupMultiLineCursorListener(textarea);
    }
}

function addCursorAbove(textarea) {
    const text = textarea.value;
    const cursorPos = textarea.selectionStart;

    // Find current line
    const beforeCursor = text.substring(0, cursorPos);
    const currentLineStart = beforeCursor.lastIndexOf('\n') + 1;

    // Calculate column position
    const columnPos = cursorPos - currentLineStart;

    // Initialize or add to multi-cursor
    if (!multiLineCursorData || multiLineCursorData.textarea !== textarea) {
        multiLineCursorData = {
            textarea: textarea,
            cursors: [{ line: getCurrentLineNumber(text, cursorPos), column: columnPos, pos: cursorPos }]
        };
    }

    // Find previous line
    if (currentLineStart > 0) {
        const prevLineEnd = currentLineStart - 1;
        const prevLineText = text.substring(0, prevLineEnd);
        const prevLineStart = prevLineText.lastIndexOf('\n') + 1;
        const prevLineLength = prevLineEnd - prevLineStart;
        const prevCursorPos = prevLineStart + Math.min(columnPos, prevLineLength);

        multiLineCursorData.cursors.unshift({
            line: getCurrentLineNumber(text, prevCursorPos),
            column: columnPos,
            pos: prevCursorPos
        });

        // Move cursor to new position
        textarea.setSelectionRange(prevCursorPos, prevCursorPos);

        showMultiCursorIndicator(textarea, multiLineCursorData.cursors.length);
        // showCursorMarkers(textarea, multiLineCursorData.cursors); // Disabled - only show main cursor
        setupMultiLineCursorListener(textarea);
    }
}

function getCurrentLineNumber(text, pos) {
    return text.substring(0, pos).split('\n').length;
}

function showMultiCursorIndicator(textarea, count) {
    let indicator = document.getElementById('multiCursorIndicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'multiCursorIndicator';
        indicator.className = 'multi-cursor-indicator';
        document.body.appendChild(indicator);
    }

    indicator.textContent = `${count} cursors`;
    indicator.style.display = 'block';

    // Position near the textarea
    const rect = textarea.getBoundingClientRect();
    indicator.style.left = rect.right + 10 + 'px';
    indicator.style.top = rect.top + 'px';
}

function setupMultiLineCursorListener(textarea) {
    // Store original text for comparison
    if (!multiLineCursorData.originalText) {
        multiLineCursorData.originalText = textarea.value;
    }

    // Remove old listener if exists
    if (textarea.multiLineCursorListener) {
        textarea.removeEventListener('input', textarea.multiLineCursorListener);
    }

    // Remove old keydown listener if exists
    if (textarea.multiLineCursorKeyListener) {
        textarea.removeEventListener('keydown', textarea.multiLineCursorKeyListener);
    }

    // Keydown listener to capture what will be typed/deleted
    textarea.multiLineCursorKeyListener = function (e) {
        if (!multiLineCursorData || multiLineCursorData.textarea !== textarea) return;

        // Prevent default to handle manually
        if (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Delete') {
            e.preventDefault();

            const cursors = multiLineCursorData.cursors;
            let newText = textarea.value;

            // Sort cursors by position (descending) to avoid position shifts
            const sortedCursors = [...cursors].sort((a, b) => b.pos - a.pos);

            // Process each cursor from end to start
            sortedCursors.forEach((cursor) => {
                const lines = newText.split('\n');

                if (cursor.line - 1 < lines.length) {
                    // Calculate actual position in current text
                    const lineStart = lines.slice(0, cursor.line - 1).join('\n').length + (cursor.line > 1 ? 1 : 0);
                    const currentLine = lines[cursor.line - 1];
                    const insertPos = lineStart + Math.min(cursor.column, currentLine.length);

                    if (e.key === 'Backspace' && cursor.column > 0) {
                        // Delete character before cursor
                        newText = newText.substring(0, insertPos - 1) + newText.substring(insertPos);
                    } else if (e.key === 'Delete' && cursor.column < currentLine.length) {
                        // Delete character after cursor
                        newText = newText.substring(0, insertPos) + newText.substring(insertPos + 1);
                    } else if (e.key.length === 1) {
                        // Insert character
                        newText = newText.substring(0, insertPos) + e.key + newText.substring(insertPos);
                    }
                }
            });

            // Update textarea
            textarea.value = newText;

            // Update cursor positions for all cursors
            multiLineCursorData.cursors.forEach(cursor => {
                if (e.key.length === 1) {
                    cursor.column++;
                } else if (e.key === 'Backspace' && cursor.column > 0) {
                    cursor.column--;
                }
            });

            // Trigger change event
            const changeEvent = new Event('input', { bubbles: true });
            textarea.dispatchEvent(changeEvent);

            // Move cursor to last position (in original order)
            const lastCursor = cursors[cursors.length - 1];
            const lines = newText.split('\n');
            if (lastCursor.line - 1 < lines.length) {
                const lineStart = lines.slice(0, lastCursor.line - 1).join('\n').length + (lastCursor.line > 1 ? 1 : 0);
                const newCursorPos = lineStart + lastCursor.column;
                textarea.setSelectionRange(newCursorPos, newCursorPos);
            }

            // Update visual markers
            // showCursorMarkers(textarea, cursors); // Disabled - only show main cursor
        }
    };

    textarea.addEventListener('keydown', textarea.multiLineCursorKeyListener);

    // Clear on blur or escape
    const clearOnBlur = function () {
        setTimeout(() => {
            clearMultiLineCursor();
            textarea.removeEventListener('keydown', textarea.multiLineCursorKeyListener);
        }, 100);
    };

    textarea.addEventListener('blur', clearOnBlur, { once: true });
}

function clearMultiLineCursor() {
    multiLineCursorData = null;
    const indicator = document.getElementById('multiCursorIndicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
    clearVisualMarkers();
}

function populateF1Categories() {
    const categoryList = document.getElementById('f1CategoryList');
    if (!categoryList) return;

    categoryList.innerHTML = '';

    // Add "Uncategorized" option
    const uncategorizedSheets = tableData.sheets.filter((sheet, index) => {
        const category = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)];
        return !category;
    });

    const uncategorizedItem = document.createElement('div');
    uncategorizedItem.className = 'f1-category-item' + (selectedF1Category === null ? ' active' : '');
    uncategorizedItem.innerHTML = `
        <input type="radio" name="f1Category" class="f1-category-radio" ${selectedF1Category === null ? 'checked' : ''}>
        <span class="f1-category-name">Uncategorized</span>
        <span class="f1-category-count">${uncategorizedSheets.length}</span>
    `;
    uncategorizedItem.onclick = () => selectF1Category(null);
    categoryList.appendChild(uncategorizedItem);

    // Add other categories
    tableData.categories.forEach(category => {
        const categorySheets = tableData.sheets.filter((sheet, index) => {
            const sheetCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)];
            return sheetCategory === category;
        });

        const item = document.createElement('div');
        item.className = 'f1-category-item' + (selectedF1Category === category ? ' active' : '');
        item.innerHTML = `
            <input type="radio" name="f1Category" class="f1-category-radio" ${selectedF1Category === category ? 'checked' : ''}>
            <span class="f1-category-name">${category}</span>
            <span class="f1-category-count">${categorySheets.length}</span>
        `;
        item.onclick = () => selectF1Category(category);
        categoryList.appendChild(item);
    });
}

function selectF1Category(category) {
    selectedF1Category = category;
    currentCategory = category; // Update currentCategory so Alt+Up/Down works

    // Update active state
    const items = document.querySelectorAll('.f1-category-item');
    items.forEach(item => {
        item.classList.remove('active');
        const radio = item.querySelector('.f1-category-radio');
        if (radio) radio.checked = false;
    });

    // Find and activate the selected category item
    items.forEach(item => {
        const categoryName = item.querySelector('.f1-category-name');
        if (categoryName) {
            const itemCategory = categoryName.textContent === 'Uncategorized' ? null : categoryName.textContent;
            if (itemCategory === category) {
                item.classList.add('active');
                const radio = item.querySelector('.f1-category-radio');
                if (radio) radio.checked = true;
            }
        }
    });

    // Repopulate sheets
    populateF1Sheets();
}

async function moveCategoryUpInF1() {
    // Get the currently selected category in F1
    const categoryToMove = selectedF1Category;

    if (!categoryToMove) {
        showToast('Cannot move Uncategorized', 'error');
        return;
    }

    const index = tableData.categories.indexOf(categoryToMove);
    if (index <= 0) {
        showToast('Category is already at the top', 'warning');
        return;
    }

    // Swap with previous category
    [tableData.categories[index - 1], tableData.categories[index]] =
        [tableData.categories[index], tableData.categories[index - 1]];

    await saveData();
    renderCategoryTabs();

    // Refresh F1 popup
    populateF1Categories();

    showToast(`Category "${categoryToMove}" moved up`, 'success');
}

async function moveCategoryDownInF1() {
    // Get the currently selected category in F1
    const categoryToMove = selectedF1Category;

    if (!categoryToMove) {
        showToast('Cannot move Uncategorized', 'error');
        return;
    }

    const index = tableData.categories.indexOf(categoryToMove);
    if (index === -1 || index >= tableData.categories.length - 1) {
        showToast('Category is already at the bottom', 'warning');
        return;
    }

    // Swap with next category
    [tableData.categories[index], tableData.categories[index + 1]] =
        [tableData.categories[index + 1], tableData.categories[index]];

    await saveData();
    renderCategoryTabs();

    // Refresh F1 popup
    populateF1Categories();

    showToast(`Category "${categoryToMove}" moved down`, 'success');
}

function populateF1Sheets(searchAllCategories = false) {
    const sheetList = document.getElementById('f1SheetList');
    if (!sheetList) return;

    sheetList.innerHTML = '';

    // Initialize separators if not exists
    if (!tableData.sheetSeparators) {
        tableData.sheetSeparators = {};
    }

    // Filter sheets by selected category (unless searching all categories)
    tableData.sheets.forEach((sheet, index) => {
        const sheetCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)];

        // If not searching all categories, check if sheet belongs to selected category
        if (!searchAllCategories) {
            if (selectedF1Category === null && sheetCategory) return;
            if (selectedF1Category !== null && sheetCategory !== selectedF1Category) return;
        }

        // Check if there's a separator before this sheet
        const separatorKey = `${selectedF1Category || 'uncategorized'}_${index}`;
        if (tableData.sheetSeparators[separatorKey]) {
            const separator = document.createElement('div');
            separator.className = 'f1-sheet-separator has-actions';
            separator.dataset.separatorKey = separatorKey;

            const actions = document.createElement('div');
            actions.className = 'f1-separator-actions';

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'f1-separator-btn';
            deleteBtn.innerHTML = '×';
            deleteBtn.title = 'Remove separator';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                delete tableData.sheetSeparators[separatorKey];
                saveData();
                populateF1Sheets(searchAllCategories);
            };

            actions.appendChild(deleteBtn);
            separator.appendChild(actions);
            sheetList.appendChild(separator);
        }

        const item = document.createElement('div');
        item.className = 'f1-sheet-item' + (index === currentSheet ? ' active' : '');
        item.dataset.sheetIndex = index;
        item.draggable = true;

        // Show category name if searching all categories
        const categoryLabel = searchAllCategories && sheetCategory ? ` <span style="color: #999; font-size: 12px;">(${sheetCategory})</span>` : '';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'f1-sheet-name-wrapper';
        nameSpan.innerHTML = `
            <span class="f1-sheet-icon">📄</span>
            <span class="f1-sheet-name">${sheet.name}${categoryLabel}</span>
        `;

        item.appendChild(nameSpan);

        // Track if user is dragging or clicking
        let isDragging = false;
        let dragStartTime = 0;

        item.addEventListener('mousedown', (e) => {
            isDragging = false;
            dragStartTime = Date.now();
        });

        item.addEventListener('dragstart', (e) => {
            isDragging = true;
            handleF1DragStart.call(item, e);
        });

        item.addEventListener('click', (e) => {
            // Only handle click if not dragging
            if (!isDragging) {
                if (window.f1SeparatorMode) {
                    e.stopPropagation();
                    addSeparatorAboveSheet(index);
                    window.f1SeparatorMode = false;
                    document.body.style.cursor = '';
                    document.querySelectorAll('.f1-sheet-item').forEach(el => {
                        el.style.cursor = '';
                        el.classList.remove('separator-mode');
                    });
                    populateF1Sheets(searchAllCategories);
                } else {
                    switchToSheetFromF1(index);
                }
            }
            isDragging = false;
        });

        // Drag and drop event handlers
        item.addEventListener('dragover', handleF1DragOver);
        item.addEventListener('drop', handleF1Drop);
        item.addEventListener('dragend', handleF1DragEnd);

        sheetList.appendChild(item);
    });

    // Show message if no sheets
    if (sheetList.children.length === 0) {
        const emptyMsg = document.createElement('div');
        emptyMsg.style.padding = '20px';
        emptyMsg.style.textAlign = 'center';
        emptyMsg.style.color = '#999';
        emptyMsg.textContent = 'No sheets found';
        sheetList.appendChild(emptyMsg);
    }
}

// Drag and drop variables
let draggedF1Item = null;
let draggedSheetIndex = null;

function handleF1DragStart(e) {
    draggedF1Item = this;
    draggedSheetIndex = parseInt(this.dataset.sheetIndex);
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleF1DragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';

    // Add visual indicator
    if (this !== draggedF1Item && this.classList.contains('f1-sheet-item')) {
        this.style.borderColor = '#007bff';
        this.style.borderWidth = '3px';
    }

    return false;
}

function handleF1Drop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }

    if (draggedF1Item !== this && this.classList.contains('f1-sheet-item')) {
        const targetIndex = parseInt(this.dataset.sheetIndex);

        // Remove the dragged sheet from its current position
        const movedSheet = tableData.sheets.splice(draggedSheetIndex, 1)[0];
        const movedCategory = tableData.sheetCategories[draggedSheetIndex];

        // Remove the category entry for the old position
        delete tableData.sheetCategories[draggedSheetIndex];

        // Rebuild sheetCategories with updated indices
        const newCategories = {};
        Object.keys(tableData.sheetCategories).forEach(key => {
            const idx = parseInt(key);
            if (idx > draggedSheetIndex) {
                // Shift down indices that were after the dragged item
                newCategories[idx - 1] = tableData.sheetCategories[key];
            } else {
                newCategories[idx] = tableData.sheetCategories[key];
            }
        });
        tableData.sheetCategories = newCategories;

        // Insert the sheet at the target position
        tableData.sheets.splice(targetIndex, 0, movedSheet);

        // Rebuild sheetCategories again to account for the insertion
        const finalCategories = {};
        Object.keys(tableData.sheetCategories).forEach(key => {
            const idx = parseInt(key);
            if (idx >= targetIndex) {
                // Shift up indices at or after the target position
                finalCategories[idx + 1] = tableData.sheetCategories[key];
            } else {
                finalCategories[idx] = tableData.sheetCategories[key];
            }
        });

        // Set the category for the moved sheet
        if (movedCategory) {
            finalCategories[targetIndex] = movedCategory;
        }
        tableData.sheetCategories = finalCategories;

        // Update current sheet index
        if (currentSheet === draggedSheetIndex) {
            currentSheet = targetIndex;
        } else if (draggedSheetIndex < targetIndex && currentSheet > draggedSheetIndex && currentSheet <= targetIndex) {
            currentSheet--;
        } else if (draggedSheetIndex > targetIndex && currentSheet >= targetIndex && currentSheet < draggedSheetIndex) {
            currentSheet++;
        }

        // Save and refresh
        saveData();
        renderSheetTabs();
        populateF1Sheets();
        showToast('Sheet moved', 'success');
    }

    return false;
}

function handleF1DragEnd(e) {
    this.classList.remove('dragging');

    // Remove all drag indicators
    document.querySelectorAll('.f1-sheet-item').forEach(item => {
        item.style.borderColor = '';
        item.style.borderWidth = '';
    });
}

function addSeparatorAboveSheet(sheetIndex) {
    if (!tableData.sheetSeparators) {
        tableData.sheetSeparators = {};
    }

    const separatorKey = `${selectedF1Category || 'uncategorized'}_${sheetIndex}`;
    tableData.sheetSeparators[separatorKey] = true;

    saveData();
    showToast('Separator added', 'success');
}

function addSeparatorAtCursor() {
    window.f1SeparatorMode = true;
    document.body.style.cursor = 'crosshair';

    // Add visual indicator to all sheets
    document.querySelectorAll('.f1-sheet-item').forEach(item => {
        item.style.cursor = 'crosshair';
        item.classList.add('separator-mode');
    });

    showToast('Click before any sheet to add separator', 'info');
}

function filterF1Sheets() {
    const searchInput = document.getElementById('f1SearchInput');
    let searchTerm = searchInput ? searchInput.value : '';

    // Hide all separators when searching
    const separators = document.querySelectorAll('.f1-sheet-separator');
    if (searchTerm) {
        separators.forEach(sep => sep.style.display = 'none');
    } else {
        separators.forEach(sep => sep.style.display = '');
    }

    // Check for special search prefixes
    if (searchTerm.startsWith('*')) {
        // Search all categories by sheet name or nickname
        const actualSearch = searchTerm.substring(1).toLowerCase();
        populateF1Sheets(true); // Show all sheets from all categories

        // Hide separators when searching
        const separators = document.querySelectorAll('.f1-sheet-separator');
        separators.forEach(sep => sep.style.display = 'none');

        // Filter by name or nickname
        const sheetItems = document.querySelectorAll('.f1-sheet-item');
        sheetItems.forEach(item => {
            const sheetIndex = parseInt(item.dataset.sheetIndex);
            const sheet = tableData.sheets[sheetIndex];
            const sheetName = sheet.name.toLowerCase();
            const sheetNickname = (sheet.nickname || '').toLowerCase();

            if (sheetName.includes(actualSearch) || sheetNickname.includes(actualSearch)) {
                item.classList.remove('hidden');
            } else {
                item.classList.add('hidden');
            }
        });
    } else if (searchTerm.startsWith('#')) {
        // Search by content inside sheets
        const actualSearch = searchTerm.substring(1).toLowerCase();
        const sheetList = document.getElementById('f1SheetList');
        if (!sheetList) return;

        sheetList.innerHTML = '';

        // Search through all sheets' content
        let foundSheets = [];
        tableData.sheets.forEach((sheet, index) => {
            let hasMatch = false;

            // Search in all rows and columns
            if (sheet.rows && sheet.rows.length > 0) {
                for (let row of sheet.rows) {
                    for (let cell of row) {
                        if (cell && String(cell).toLowerCase().includes(actualSearch)) {
                            hasMatch = true;
                            break;
                        }
                    }
                    if (hasMatch) break;
                }
            }

            if (hasMatch) {
                foundSheets.push(index);
            }
        });

        // Display matching sheets
        if (foundSheets.length > 0) {
            foundSheets.forEach(index => {
                const sheet = tableData.sheets[index];
                const sheetCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)];
                const categoryLabel = sheetCategory ? ` <span style="color: #999; font-size: 12px;">(${sheetCategory})</span>` : '';

                const item = document.createElement('div');
                item.className = 'f1-sheet-item' + (index === currentSheet ? ' active' : '');
                item.dataset.sheetIndex = index;
                item.innerHTML = `
                    <span class="f1-sheet-icon">🔍</span>
                    <span class="f1-sheet-name">${sheet.name}${categoryLabel}</span>
                `;
                item.onclick = () => switchToSheetFromF1(index);
                sheetList.appendChild(item);
            });
        } else {
            const emptyMsg = document.createElement('div');
            emptyMsg.style.padding = '20px';
            emptyMsg.style.textAlign = 'center';
            emptyMsg.style.color = '#999';
            emptyMsg.textContent = actualSearch ? 'No sheets contain this text' : 'Type to search sheet content';
            sheetList.appendChild(emptyMsg);
        }
    } else {
        // Normal search - filter current category sheets by name or nickname
        populateF1Sheets(false); // Show sheets from selected category only

        const searchLower = searchTerm.toLowerCase();
        const sheetItems = document.querySelectorAll('.f1-sheet-item');

        // Hide separators when searching
        if (searchLower) {
            const separators = document.querySelectorAll('.f1-sheet-separator');
            separators.forEach(sep => sep.style.display = 'none');
        }

        sheetItems.forEach(item => {
            const sheetIndex = parseInt(item.dataset.sheetIndex);
            const sheet = tableData.sheets[sheetIndex];
            const sheetName = sheet.name.toLowerCase();
            const sheetNickname = (sheet.nickname || '').toLowerCase();

            if (sheetName.includes(searchLower) || sheetNickname.includes(searchLower)) {
                item.classList.remove('hidden');
            } else {
                item.classList.add('hidden');
            }
        });
    }
}

function handleF1SearchKeydown(e) {
    if (e.key === 'Enter') {
        e.preventDefault();

        // Find the first visible (non-hidden) sheet item
        const sheetItems = document.querySelectorAll('.f1-sheet-item');
        for (let item of sheetItems) {
            if (!item.classList.contains('hidden')) {
                // Try to click the name wrapper first (for normal sheets), otherwise click the item itself (for search results)
                const nameWrapper = item.querySelector('.f1-sheet-name-wrapper');
                if (nameWrapper) {
                    nameWrapper.click();
                } else {
                    item.click();
                }
                break;
            }
        }
    }
}

function switchToSheetFromF1(sheetIndex) {
    // Switch to the sheet
    switchSheet(sheetIndex);

    // Close the popup
    closeF1Popup();
}

// Close F1 popup when clicking outside
document.addEventListener('click', (event) => {
    const popup = document.getElementById('f1Popup');
    if (popup && event.target === popup) {
        closeF1Popup();
    }
});

// Toggle between the 2 most recent sheets (Alt+M)
function toggleRecentSheets() {
    // If we have at least one sheet in history, switch to it
    if (sheetHistory.length > 0) {
        const previousSheet = sheetHistory[sheetHistory.length - 1];

        // Make sure the sheet index is valid
        if (previousSheet >= 0 && previousSheet < tableData.sheets.length) {
            switchSheet(previousSheet);
        }
    }
}


// Toggle top ribbons (toolbar and sheet tabs) with F4 - 4 states
function toggleTopRibbons() {
    const toolbar = document.querySelector('.toolbar');
    const sheetTabs = document.querySelector('.sheet-tabs');

    // Get current state (0=all shown, 1=sheets hidden, 2=toolbar hidden, 3=both hidden)
    let currentState = parseInt(localStorage.getItem('ribbonsState') || '0');

    // Cycle to next state
    currentState = (currentState + 1) % 4;

    // Apply state
    switch (currentState) {
        case 0: // Show all
            toolbar.style.display = 'flex';
            sheetTabs.style.display = 'flex';
            showToast('All ribbons shown', 'info');
            break;
        case 1: // Hide sheet tabs only
            toolbar.style.display = 'flex';
            sheetTabs.style.display = 'none';
            showToast('Sheet tabs hidden', 'info');
            break;
        case 2: // Hide toolbar only
            toolbar.style.display = 'none';
            sheetTabs.style.display = 'flex';
            showToast('Toolbar hidden', 'info');
            break;
        case 3: // Hide both
            toolbar.style.display = 'none';
            sheetTabs.style.display = 'none';
            showToast('All ribbons hidden (F4 to cycle)', 'info');
            break;
    }

    localStorage.setItem('ribbonsState', currentState.toString());
}

// Restore ribbons state on page load
window.addEventListener('load', () => {
    const ribbonsState = parseInt(localStorage.getItem('ribbonsState') || '0');
    const toolbar = document.querySelector('.toolbar');
    const sheetTabs = document.querySelector('.sheet-tabs');

    switch (ribbonsState) {
        case 1: // Hide sheet tabs only
            sheetTabs.style.display = 'none';
            break;
        case 2: // Hide toolbar only
            toolbar.style.display = 'none';
            break;
        case 3: // Hide both
            toolbar.style.display = 'none';
            sheetTabs.style.display = 'none';
            break;
    }
});


// Adjust cell height to fit both markdown preview and raw text
function adjustCellHeightForMarkdown(cell) {
    const input = cell.querySelector('input, textarea');
    const preview = cell.querySelector('.markdown-preview');

    if (!input || !preview || !input.classList.contains('has-markdown')) {
        return;
    }

    // Temporarily show both to measure
    const originalInputDisplay = input.style.display;
    const originalPreviewDisplay = preview.style.display;

    input.style.display = 'block';
    preview.style.display = 'block';

    // Measure heights
    const inputHeight = input.scrollHeight;
    const previewHeight = preview.scrollHeight;

    // Use the larger height
    const maxHeight = Math.max(inputHeight, previewHeight);

    // Apply to both
    if (input.tagName === 'TEXTAREA') {
        input.style.minHeight = maxHeight + 'px';
    }
    preview.style.minHeight = maxHeight + 'px';

    // Restore display
    input.style.display = originalInputDisplay;
    preview.style.display = originalPreviewDisplay;
}

// Apply to all cells with markdown after rendering
function adjustAllMarkdownCells() {
    const cells = document.querySelectorAll('td .has-markdown');
    cells.forEach(input => {
        const cell = input.closest('td');
        if (cell) {
            adjustCellHeightForMarkdown(cell);
        }
    });
}

// Call after table renders
const originalRenderTable = renderTable;
renderTable = function () {
    originalRenderTable.apply(this, arguments);
    setTimeout(() => {
        adjustAllMarkdownCells();
    }, 100);
};

// Quick Formatter Functions (F3)

function applyQuickFormat(prefix, suffix, event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    // Check if there are multiple formats selected (from right-clicks)
    if (selectedFormats.length > 0) {
        // Add the current format to the list
        selectedFormats.push({ prefix, suffix });

        // Apply all selected formats
        let allPrefixes = '';
        let allSuffixes = '';

        // Apply all selected formats (nesting them)
        selectedFormats.forEach(format => {
            allPrefixes += format.prefix;
            allSuffixes = format.suffix + allSuffixes;
        });

        // Insert the formatting
        const newText = input.value.substring(0, start) +
            allPrefixes + selectedText + allSuffixes +
            input.value.substring(end);

        input.value = newText;

        // Trigger change event to update cell
        const changeEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(changeEvent);

        // Set cursor position after the inserted text
        const newCursorPos = start + allPrefixes.length + selectedText.length + allSuffixes.length;
        input.setSelectionRange(newCursorPos, newCursorPos);
        input.focus();

        // Store count before clearing
        const formatCount = selectedFormats.length;

        // Clear selected formats
        selectedFormats = [];
        updateFormatCheckmarks();

        closeQuickFormatter();
        showToast(`Applied ${formatCount} formats`, 'success');
    } else {
        // Single format application
        const newText = input.value.substring(0, start) +
            prefix + selectedText + suffix +
            input.value.substring(end);

        input.value = newText;

        // Trigger change event to update cell
        const changeEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(changeEvent);

        // Set cursor position after the inserted text
        const newCursorPos = start + prefix.length + selectedText.length + suffix.length;
        input.setSelectionRange(newCursorPos, newCursorPos);
        input.focus();

        closeQuickFormatter();
        showToast('Format applied', 'success');
    }
}

function applyLinkFormat(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedUrl = input.value.substring(start, end);

    // Use default placeholder text with italic formatting
    const linkText = '@@Link@@';

    // Insert the link syntax: {link:url}@@Link@@{/}
    const newText = input.value.substring(0, start) +
        `{link:${selectedUrl}}` + linkText + '{/}' +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position after the inserted text
    const linkPrefix = `{link:${selectedUrl}}`;
    const newCursorPos = start + linkPrefix.length + linkText.length + 3;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast('Link applied', 'success');
}

function searchGoogle(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Strip markdown formatting before searching
    const cleanText = stripMarkdown(selectedText);

    // Open Google search in new tab
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(cleanText)}`;
    window.open(searchUrl, '_blank');

    closeQuickFormatter();
    showToast('Searching in Google', 'success');
}

function sortLines(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Parse lines into blocks (parent + children)
    const lines = selectedText.split('\n');
    const blocks = [];
    let currentBlock = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        // Check dash patterns
        const isDoubleDash = trimmed.startsWith('-- ');
        const isSingleDash = trimmed.startsWith('- ') && !trimmed.startsWith('-- ');
        const hasNoDash = !trimmed.startsWith('- ');

        // Determine if this is a child line by looking at context
        let isChildLine = false;

        if (isDoubleDash) {
            // -- is always a child
            isChildLine = true;
        } else if (isSingleDash) {
            // - could be parent or child depending on what came before
            if (currentBlock && currentBlock.children.length === 0) {
                // Previous line was a parent with no children yet
                // Check if previous parent has no dash (then this - is a child)
                // or if previous parent has - (then this - is also a parent)
                const prevParentTrimmed = currentBlock.parent.trim();
                if (prevParentTrimmed.startsWith('- ')) {
                    // Previous parent also starts with -, so this is a new parent
                    isChildLine = false;
                } else {
                    // Previous parent has no dash, so this - is a child
                    isChildLine = true;
                }
            } else if (currentBlock && currentBlock.children.length > 0) {
                // Previous line(s) were children, check the last child's format
                const lastChild = currentBlock.children[currentBlock.children.length - 1];
                if (lastChild.trim().startsWith('-- ')) {
                    // Last child was --, so this - is a new parent
                    isChildLine = false;
                } else {
                    // Last child was -, so this - is also a child
                    isChildLine = true;
                }
            } else {
                // No current block, this - starts a new parent
                isChildLine = false;
            }
        } else {
            // No dash = parent line
            isChildLine = false;
        }

        if (isChildLine) {
            // This is a child line, add to current block
            if (currentBlock) {
                currentBlock.children.push(line);
            } else {
                // Orphan child line, treat as its own block
                blocks.push({
                    parent: line,
                    children: [],
                    isOrphan: true
                });
            }
        } else {
            // This is a parent line, start a new block
            if (currentBlock) {
                blocks.push(currentBlock);
            }
            currentBlock = {
                parent: line,
                children: []
            };
        }
    }

    // Don't forget the last block
    if (currentBlock) {
        blocks.push(currentBlock);
    }

    // Sort blocks by their parent line with dash priority and smart numerical sorting
    const sortedBlocks = blocks.sort((a, b) => {
        const lineA = a.parent.trim();
        const lineB = b.parent.trim();

        // Check dash prefixes for priority (no dash > single dash > double dash)
        const dashPriorityA = lineA.startsWith('-- ') ? 2 : (lineA.startsWith('- ') ? 1 : 0);
        const dashPriorityB = lineB.startsWith('-- ') ? 2 : (lineB.startsWith('- ') ? 1 : 0);

        // If different dash priorities, sort by priority (lower number = higher priority)
        if (dashPriorityA !== dashPriorityB) {
            return dashPriorityA - dashPriorityB;
        }

        // Same dash priority, now compare content
        // Remove dash prefix for comparison
        const contentA = lineA.replace(/^-+\s*/, '');
        const contentB = lineB.replace(/^-+\s*/, '');

        // Extract leading numbers from both strings
        const numA = contentA.match(/^\d+/);
        const numB = contentB.match(/^\d+/);

        // If both start with numbers, compare numerically
        if (numA && numB) {
            const diff = parseInt(numA[0], 10) - parseInt(numB[0], 10);
            if (diff !== 0) return diff;
            // If numbers are equal, compare the rest of the string
            return contentA.toLowerCase().localeCompare(contentB.toLowerCase());
        }

        // If only one starts with a number, numbers come first
        if (numA) return -1;
        if (numB) return 1;

        // Otherwise, alphabetical comparison (case-insensitive)
        return contentA.toLowerCase().localeCompare(contentB.toLowerCase());
    });

    // Reconstruct the sorted text
    const sortedLines = [];
    for (const block of sortedBlocks) {
        sortedLines.push(block.parent);
        sortedLines.push(...block.children);
    }

    const sortedText = sortedLines.join('\n');

    // Replace the selected text with sorted text
    const newText = input.value.substring(0, start) +
        sortedText +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position at the end of the sorted text
    const newCursorPos = start + sortedText.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast('Lines sorted (keeping lists with parents)', 'success');
}

function removeFormatting(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Use the stripMarkdown function to remove all formatting
    const cleanText = stripMarkdown(selectedText);

    // Replace the selected text with clean text
    const newText = input.value.substring(0, start) +
        cleanText +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position at the end of the clean text
    const newCursorPos = start + cleanText.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast('Formatting removed', 'success');
}

function selectAllMatchingFromFormatter(event) {
    event.preventDefault();
    event.stopPropagation();

    if (!quickFormatterTarget) {
        console.log('No quickFormatterTarget');
        return;
    }

    // Store the target and selection
    const target = quickFormatterTarget;
    const selection = quickFormatterSelection;

    // Keep the input focused and restore selection
    target.focus();
    target.setSelectionRange(selection.start, selection.end);

    // Select all matching occurrences
    selectAllMatchingOccurrences(target);

    // Close the formatter after selection is done
    closeQuickFormatter();
}

function showColorPicker(event) {
    if (event) {
        event.preventDefault();
    }

    const colorSection = document.getElementById('colorPickerSection');
    const isShowing = colorSection.style.display === 'none';
    colorSection.style.display = isShowing ? 'block' : 'none';

    if (isShowing) {
        loadColorSwatches();
    }
}

function toggleColorSelection(event) {
    event.preventDefault();

    // Toggle color picker visibility for selection
    showColorPicker(event);

    return false;
}

function applyColorFormat() {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    const fgColor = document.getElementById('quickFgColor').value;
    const bgColor = document.getElementById('quickBgColor').value;
    const noBg = document.getElementById('noBgCheckbox').checked;

    // Build color syntax
    let colorSyntax = '';
    if (noBg) {
        colorSyntax = `{fg:${fgColor}}`;
    } else {
        colorSyntax = `{fg:${fgColor};bg:${bgColor}}`;
    }

    // Check if there are other formats selected (from right-clicks)
    if (selectedFormats.length > 0) {
        // Apply all selected formats along with color
        let allPrefixes = colorSyntax; // Color goes first
        let allSuffixes = '{/}'; // Color closing tag

        // Add other formats (nesting them)
        selectedFormats.forEach(format => {
            allPrefixes += format.prefix;
            allSuffixes = format.suffix + allSuffixes;
        });

        // Insert the formatting
        const newText = input.value.substring(0, start) +
            allPrefixes + selectedText + allSuffixes +
            input.value.substring(end);

        input.value = newText;

        // Trigger change event to update cell
        const changeEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(changeEvent);

        // Set cursor position after the inserted text
        const newCursorPos = start + allPrefixes.length + selectedText.length + allSuffixes.length;
        input.setSelectionRange(newCursorPos, newCursorPos);
        input.focus();

        // Store count before clearing
        const formatCount = selectedFormats.length + 1; // +1 for color

        // Clear selected formats
        selectedFormats = [];
        updateFormatCheckmarks();

        closeQuickFormatter();
        showToast(`Applied ${formatCount} formats (including color)`, 'success');
    } else {
        // Just color formatting
        const newText = input.value.substring(0, start) +
            colorSyntax + selectedText + '{/}' +
            input.value.substring(end);

        input.value = newText;

        // Trigger change event to update cell
        const changeEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(changeEvent);

        // Set cursor position after the inserted text
        const newCursorPos = start + colorSyntax.length + selectedText.length + 3;
        input.setSelectionRange(newCursorPos, newCursorPos);
        input.focus();

        closeQuickFormatter();
        showToast('Color applied', 'success');
    }
}

// Multi-format selection support (variable declared earlier in file)

function toggleFormatSelection(prefix, suffix, event) {
    event.preventDefault();

    // Find the format in selectedFormats
    const formatIndex = selectedFormats.findIndex(f => f.prefix === prefix && f.suffix === suffix);

    if (formatIndex >= 0) {
        // Remove from selection
        selectedFormats.splice(formatIndex, 1);
    } else {
        // Add to selection
        selectedFormats.push({ prefix, suffix });
    }

    // Update visual checkmarks
    updateFormatCheckmarks();

    return false;
}

function updateFormatCheckmarks() {
    // Remove all existing checkmarks
    document.querySelectorAll('.format-btn .format-checkmark').forEach(el => el.remove());

    // Add checkmarks to selected formats
    selectedFormats.forEach(format => {
        const buttons = document.querySelectorAll('.format-btn');
        buttons.forEach(btn => {
            const onclick = btn.getAttribute('onclick');
            if (onclick && onclick.includes(`'${format.prefix}'`) && onclick.includes(`'${format.suffix}'`)) {
                // Add checkmark if not already present
                if (!btn.querySelector('.format-checkmark')) {
                    const checkmark = document.createElement('span');
                    checkmark.className = 'format-checkmark';
                    checkmark.textContent = '✓';
                    checkmark.style.position = 'absolute';
                    checkmark.style.top = '2px';
                    checkmark.style.right = '2px';
                    checkmark.style.fontSize = '10px';
                    checkmark.style.color = '#4CAF50';
                    checkmark.style.fontWeight = 'bold';
                    btn.style.position = 'relative';
                    btn.appendChild(checkmark);
                }
            }
        });
    });
}

function applyMultipleFormats(event) {
    if (!quickFormatterTarget || selectedFormats.length === 0) {
        showToast('No formats selected', 'warning');
        return;
    }

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    // Build nested formatting
    let formattedText = selectedText;
    let allPrefixes = '';
    let allSuffixes = '';

    // Apply all selected formats (nesting them)
    selectedFormats.forEach(format => {
        allPrefixes += format.prefix;
        allSuffixes = format.suffix + allSuffixes;
    });

    // Insert the formatting
    const newText = input.value.substring(0, start) +
        allPrefixes + selectedText + allSuffixes +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position after the inserted text
    const newCursorPos = start + allPrefixes.length + selectedText.length + allSuffixes.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    // Clear selected formats
    selectedFormats = [];
    updateFormatCheckmarks();

    closeQuickFormatter();
    showToast('Multiple formats applied', 'success');
}

// Load and display color swatches
function loadColorSwatches() {
    const swatchesContainer = document.getElementById('colorSwatches');
    if (!swatchesContainer) return;

    swatchesContainer.innerHTML = '';

    // Default presets
    const defaultSwatches = [
        { fg: '#ffffff', bg: '#000000' }, // White on Black
        { fg: '#000000', bg: '#ffff00' }, // Black on Yellow
        { fg: '#ffffff', bg: '#ff0000' }, // White on Red
        { fg: '#000000', bg: '#00ff00' }, // Black on Green
        { fg: '#ffffff', bg: '#0000ff' }, // White on Blue
        { fg: '#000000', bg: '#ffa500' }, // Black on Orange
        { fg: '#ffffff', bg: '#800080' }, // White on Purple
    ];

    // Load saved swatches from localStorage
    const savedSwatches = JSON.parse(localStorage.getItem('colorSwatches') || '[]');
    const allSwatches = [...savedSwatches, ...defaultSwatches];

    allSwatches.forEach((swatch, index) => {
        const swatchBtn = document.createElement('button');
        swatchBtn.className = 'color-swatch';

        // Show visual indicator if noBg is set
        if (swatch.noBg) {
            swatchBtn.style.background = 'transparent';
            swatchBtn.style.border = '2px dashed #999';
        } else {
            swatchBtn.style.background = swatch.bg;
        }
        swatchBtn.style.color = swatch.fg;
        swatchBtn.textContent = 'Aa';

        const bgText = swatch.noBg ? 'No BG' : swatch.bg;
        swatchBtn.title = `Text: ${swatch.fg}, Background: ${bgText}`;

        // Build color syntax for this swatch
        let colorSyntax = '';
        if (swatch.noBg) {
            colorSyntax = `{fg:${swatch.fg}}`;
        } else {
            colorSyntax = `{fg:${swatch.fg};bg:${swatch.bg}}`;
        }

        // Left-click: Apply color (with any selected formats)
        swatchBtn.onclick = (e) => {
            e.preventDefault();
            applySwatchColor(colorSyntax);
        };

        // Right-click: Add to multi-selection
        swatchBtn.oncontextmenu = (e) => {
            e.preventDefault();
            toggleSwatchSelection(colorSyntax, swatch);
            return false;
        };

        // Add delete button for saved swatches
        if (index < savedSwatches.length) {
            const deleteBtn = document.createElement('span');
            deleteBtn.className = 'swatch-delete';
            deleteBtn.textContent = '×';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteSwatch(index);
            };
            swatchBtn.appendChild(deleteBtn);
        }

        // Check if this swatch is in selectedFormats and add checkmark
        const isSelected = selectedFormats.some(f => f.prefix === colorSyntax && f.suffix === '{/}');
        if (isSelected) {
            const checkmark = document.createElement('span');
            checkmark.className = 'format-checkmark swatch-checkmark';
            checkmark.textContent = '✓';
            checkmark.style.position = 'absolute';
            checkmark.style.top = '2px';
            checkmark.style.right = '2px';
            checkmark.style.fontSize = '10px';
            checkmark.style.color = '#4CAF50';
            checkmark.style.fontWeight = 'bold';
            checkmark.style.zIndex = '10';
            swatchBtn.appendChild(checkmark);
        }

        swatchesContainer.appendChild(swatchBtn);
    });
}

function applySwatchColor(colorSyntax) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    // Check if there are other formats selected (from right-clicks)
    if (selectedFormats.length > 0) {
        // Apply all selected formats along with color
        let allPrefixes = colorSyntax; // Color goes first
        let allSuffixes = '{/}'; // Color closing tag

        // Add other formats (nesting them)
        selectedFormats.forEach(format => {
            allPrefixes += format.prefix;
            allSuffixes = format.suffix + allSuffixes;
        });

        // Insert the formatting
        const newText = input.value.substring(0, start) +
            allPrefixes + selectedText + allSuffixes +
            input.value.substring(end);

        input.value = newText;

        // Trigger change event to update cell
        const changeEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(changeEvent);

        // Set cursor position after the inserted text
        const newCursorPos = start + allPrefixes.length + selectedText.length + allSuffixes.length;
        input.setSelectionRange(newCursorPos, newCursorPos);
        input.focus();

        // Store count before clearing
        const formatCount = selectedFormats.length + 1; // +1 for color

        // Clear selected formats
        selectedFormats = [];
        updateFormatCheckmarks();

        closeQuickFormatter();
        showToast(`Applied ${formatCount} formats (including color)`, 'success');
    } else {
        // Just color formatting
        const newText = input.value.substring(0, start) +
            colorSyntax + selectedText + '{/}' +
            input.value.substring(end);

        input.value = newText;

        // Trigger change event to update cell
        const changeEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(changeEvent);

        // Set cursor position after the inserted text
        const newCursorPos = start + colorSyntax.length + selectedText.length + 3;
        input.setSelectionRange(newCursorPos, newCursorPos);
        input.focus();

        closeQuickFormatter();
        showToast('Color applied', 'success');
    }
    const fgColor = document.getElementById('quickFgColor').value;
    const bgColor = document.getElementById('quickBgColor').value;
    const noBg = document.getElementById('noBgCheckbox').checked;

    const newSwatch = {
        fg: fgColor,
        bg: bgColor,
        noBg: noBg
    };

    // Load existing swatches
    const savedSwatches = JSON.parse(localStorage.getItem('colorSwatches') || '[]');

    // Check if this combination already exists
    const exists = savedSwatches.some(s =>
        s.fg === fgColor && s.bg === bgColor && s.noBg === noBg
    );

    if (!exists) {
        savedSwatches.unshift(newSwatch); // Add to beginning
        // Keep only last 10 custom swatches
        if (savedSwatches.length > 10) {
            savedSwatches.pop();
        }
        localStorage.setItem('colorSwatches', JSON.stringify(savedSwatches));
        loadColorSwatches();
        showToast('Color saved to swatches', 'success');
    } else {
        showToast('This color combination already exists', 'info');
    }
}

function deleteSwatch(index) {
    const savedSwatches = JSON.parse(localStorage.getItem('colorSwatches') || '[]');
    savedSwatches.splice(index, 1);
    localStorage.setItem('colorSwatches', JSON.stringify(savedSwatches));
    loadColorSwatches();
    showToast('Swatch deleted', 'success');
}

function toggleSwatchSelection(colorSyntax, swatch) {
    // Find the format in selectedFormats
    const formatIndex = selectedFormats.findIndex(f => f.prefix === colorSyntax && f.suffix === '{/}');

    if (formatIndex >= 0) {
        // Remove from selection (deselecting this color)
        selectedFormats.splice(formatIndex, 1);
    } else {
        // Remove any other color selections first (only one color allowed)
        selectedFormats = selectedFormats.filter(f => !f.isColor);

        // Add this color to selection
        selectedFormats.push({ prefix: colorSyntax, suffix: '{/}', isColor: true, swatch: swatch });
    }

    // Update visual checkmarks on both format buttons and swatches
    updateFormatCheckmarks();
    loadColorSwatches(); // Reload to show/hide checkmarks on swatches
}

function toggleHiddenText() {
    const toggle = document.getElementById('hiddenTextToggle');
    if (toggle && toggle.checked) {
        document.body.classList.add('show-hidden-text');
        localStorage.setItem('hiddenTextVisible', 'true');
        showToast('Hidden text shown', 'success');
    } else {
        document.body.classList.remove('show-hidden-text');
        localStorage.setItem('hiddenTextVisible', 'false');
        showToast('Hidden text hidden', 'success');
    }
}
