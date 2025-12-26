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
        renderSidebar();
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

            // Display row count if >= 100
            updateRowCountDisplay();
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

// Helper function to update row count display
function updateRowCountDisplay() {
    const sheet = tableData.sheets[currentSheet];
    const rowCount = sheet ? sheet.rows.length : 0;
    const rowCountElement = document.getElementById('rowCountValue');
    const rowCountContainer = document.getElementById('rowCount');
    if (rowCountElement && rowCountContainer) {
        if (rowCount >= 100) {
            rowCountElement.textContent = rowCount;
            rowCountContainer.style.display = 'flex';
        } else {
            rowCountContainer.style.display = 'none';
        }
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
            renderSidebar();
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
        updateRowCountDisplay();

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
            updateRowCountDisplay();
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
        (str.includes('http') && str.includes('[')) ||
        str.includes('{{') ||
        str.includes('\n- ') ||
        str.includes('\n-- ') ||
        str.includes('\n--- ') ||
        str.trim().startsWith('- ') ||
        str.trim().startsWith('-- ') ||
        str.trim().startsWith('--- ') ||
        str.match(/(?:^|\n)Table\*\d+/i) ||
        str.trim().startsWith('|') ||
        str.includes('\\(') ||
        str.match(/^-{5,}$/m) ||
        str.match(/^[A-Z]+-{5,}$/m) || // Colored separator (prefix)
        str.match(/^-{5,}[A-Z]+$/m) || // Colored separator (suffix for bg)
        str.match(/^[A-Z]+-{5,}[A-Z]+$/m) || // Colored separator (both)
        str.match(/^-{5,}#[0-9a-fA-F]{6}/m) || // Hex color bg
        str.match(/^[A-Z]+-{5,}#[0-9a-fA-F]{6}/m) || // Colored sep + hex bg
        (str.includes('|') && str.split('|').length >= 2) ||
        str.includes('\n') || // Treat multi-line text as markdown for proper height handling
        str.match(/#[\d.]+#.+?#\/#/) || // Variable font size heading
        str.match(/#[A-Z]+#.+?#\/#/) || // Border box syntax
        str.includes('_.') || // Wavy underline
        str.match(/^Timeline(?:C)?(?:-[A-Z]+)?\*/m) || // Timeline syntax
        str.match(/\[\d+(?:-[A-Z]+)?\]\S+/) || // Word connector syntax
        customColorSyntaxes.some(syntax => str.includes(syntax.marker)) // Check custom syntaxes
    );
}


function handlePreviewMouseDown(e) {
    // Only handle left clicks
    if (e.button !== 0) return;

    // Don't interfere with links or check boxes inside the preview
    if (e.target.closest('a') || e.target.tagName === 'INPUT') return;

    // Stop propagation
    e.stopPropagation();

    // Prevent default to stop immediate browser focus handling
    // We will handle focus manually
    e.preventDefault();

    const preview = e.currentTarget;
    const cell = preview.closest('td');
    if (!cell) return;

    const input = cell.querySelector('input, textarea');
    if (!input) return;

    // 1. Get Click Position in the Preview
    let range;
    if (document.caretRangeFromPoint) {
        range = document.caretRangeFromPoint(e.clientX, e.clientY);
    } else if (document.caretPositionFromPoint) {
        // Firefox fallback
        const pos = document.caretPositionFromPoint(e.clientX, e.clientY);
        if (pos) {
            range = document.createRange();
            range.setStart(pos.offsetNode, pos.offset);
        }
    }

    // Default to end if detection fails
    let finalPos = input.value.length;

    if (range) {
        const clickedNode = range.startContainer;
        const clickOffset = range.startOffset;

        if (clickedNode.nodeType === Node.TEXT_NODE) {
            const searchPhrase = clickedNode.textContent;
            const rawText = input.value;

            // 2. Count occurrences of this phrase before the click in Preview
            let found = false;
            let count = 0;

            function countOccurrencesBefore(node) {
                if (node === clickedNode) {
                    found = true;
                    return;
                }

                if (node.nodeType === Node.TEXT_NODE) {
                    const text = node.textContent;
                    let pos = text.indexOf(searchPhrase);
                    while (pos !== -1) {
                        count++;
                        pos = text.indexOf(searchPhrase, pos + 1);
                    }
                }

                if (node.childNodes) {
                    for (let i = 0; i < node.childNodes.length; i++) {
                        if (found) return;
                        countOccurrencesBefore(node.childNodes[i]);
                    }
                }
            }

            countOccurrencesBefore(preview);

            // 3. Find the (count + 1)th instance in Raw Text
            let rawSearchPos = -1;
            for (let i = 0; i <= count; i++) {
                rawSearchPos = rawText.indexOf(searchPhrase, rawSearchPos + 1);
                if (rawSearchPos === -1) break;
            }

            // 4. Calculate final position
            if (rawSearchPos !== -1) {
                finalPos = rawSearchPos + clickOffset;
            }
        }
    }

    // 5. Apply focus and selection synchronously
    // Use preventScroll to stop browser from jumping around
    input.focus({ preventScroll: true });

    try {
        input.setSelectionRange(finalPos, finalPos);
    } catch (e) {
        console.error('Selection set failed', e);
    }

    // 6. Manual scroll to ensure visibility
    // 6. Manual scroll to ensure correct positioning (Solution 1: Position at Click)
    if (input.tagName === 'TEXTAREA') {
        positionCursorAtMouseClick(input, e);
    }
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
        preview.onmousedown = handlePreviewMouseDown; // Handle clicks to position cursor
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

        // Draw word connectors after preview is added
        requestAnimationFrame(() => {
            drawWordConnectors(preview);
        });
    } else {
        delete inputElement.dataset.formattedHtml;
        inputElement.classList.remove('has-markdown');
    }
}

/**
 * Draw connector lines between words with matching connection IDs
 * Called after markdown preview is rendered
 */
function drawWordConnectors(previewElement) {
    if (!previewElement) return;

    // Remove existing connector lines
    previewElement.querySelectorAll('.word-connector-line').forEach(el => el.remove());

    // Group connectors by ID
    const connectorGroups = {};
    previewElement.querySelectorAll('.word-connector').forEach(connector => {
        const connId = connector.dataset.connId;
        if (!connectorGroups[connId]) {
            connectorGroups[connId] = [];
        }
        connectorGroups[connId].push(connector);
    });

    // Draw lines for each group
    Object.entries(connectorGroups).forEach(([connId, connectors]) => {
        if (connectors.length < 2) return; // Need at least 2 words to connect

        // Sort by position in document
        connectors.sort((a, b) => {
            const rectA = a.getBoundingClientRect();
            const rectB = b.getBoundingClientRect();
            return rectA.left - rectB.left;
        });

        const color = connectors[0].dataset.connColor;

        // Connect consecutive pairs
        for (let i = 0; i < connectors.length - 1; i++) {
            const start = connectors[i];
            const end = connectors[i + 1];

            const startRect = start.getBoundingClientRect();
            const endRect = end.getBoundingClientRect();
            const containerRect = previewElement.getBoundingClientRect();

            // Calculate positions relative to container
            const startX = startRect.left - containerRect.left + startRect.width / 2;
            const endX = endRect.left - containerRect.left + endRect.width / 2;
            const y = startRect.bottom - containerRect.top + 2;

            // Create SVG line with extra space for arrows
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.classList.add('word-connector-line');
            svg.style.left = (Math.min(startX, endX) - 3) + 'px';
            svg.style.top = y + 'px';
            svg.style.width = (Math.abs(endX - startX) + 6) + 'px';
            svg.style.height = '12px';
            svg.style.position = 'absolute';
            svg.style.overflow = 'visible';

            // Draw U-shaped bracket line with arrows: ↑─────↑
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            const width = Math.abs(endX - startX);
            // Draw U-shape with arrow tips at top of both verticals (offset by 3 for padding)
            const d = `M 3,9 L 3,2 M 3,9 L ${width + 3},9 M ${width + 3},9 L ${width + 3},2 M 1.5,4 L 3,2 L 4.5,4 M ${width + 1.5},4 L ${width + 3},2 L ${width + 4.5},4`;
            path.setAttribute('d', d);
            path.setAttribute('stroke', color);
            path.setAttribute('stroke-width', '2');
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke-linecap', 'round');
            path.setAttribute('stroke-linejoin', 'round');

            svg.appendChild(path);
            previewElement.appendChild(svg);
        }
    });
}

/* ----------  COMMA-TABLE → CSS-GRID  ---------- */
function parseCommaTable(cols, text, borderColor, borderWidth) {
    const items = text.split(',').map(c => c.trim());

    let gridStyle = `--cols:${cols};`;

    // Explicitly calculate border style to ensure it applies
    const bColor = borderColor || '#ced4da';
    const bWidth = borderWidth || '1px';
    const cellStyle = `border: ${bWidth} solid ${bColor} !important;`;

    // First pass: identify ^^ cells and calculate rowspans
    const rowspans = {}; // key: "row-col", value: span count
    items.forEach((item, i) => {
        if (item.trim() === '^^') {
            const col = i % cols;
            const row = Math.floor(i / cols);
            // Find the first non-^^ cell above this one
            let targetRow = row - 1;
            while (targetRow >= 0) {
                const targetIndex = targetRow * cols + col;
                if (targetIndex < items.length && items[targetIndex].trim() !== '^^') {
                    break;
                }
                targetRow--;
            }
            if (targetRow >= 0) {
                const targetKey = `${targetRow}-${col}`;
                rowspans[targetKey] = (rowspans[targetKey] || 1) + 1;
            }
        }
    });

    // Second pass: identify which rows contain rowspan cells (for border styling)
    const rowsWithRowspan = new Set();
    Object.entries(rowspans).forEach(([key, span]) => {
        if (span > 1) {
            const [row, col] = key.split('-').map(Number);
            // Mark the starting row and all rows it spans
            for (let r = row; r < row + span; r++) {
                rowsWithRowspan.add(r);
            }
        }
    });

    // Third pass: render with rowspan attributes
    let html = `<div class="md-grid" style="${gridStyle}">`;
    items.forEach((item, i) => {
        // Skip empty last item if it's just a trailing comma
        if (i === items.length - 1 && item === '') return;

        const col = i % cols;
        const row = Math.floor(i / cols);
        const key = `${row}-${col}`;

        // Skip cells with ^^ (they're merged)
        if (item.trim() === '^^') {
            return;
        }

        const rowspan = rowspans[key] || 1;
        const isInRowspanRow = rowsWithRowspan.has(row);
        const rowspanRowClass = isInRowspanRow ? ' md-rowspan-row' : '';
        const rowspanAttr = rowspan > 1 ? ` rowspan="${rowspan}" style="grid-row: span ${rowspan}; ${cellStyle}"` : ` style="${cellStyle}"`;

        html += `<div class="md-cell${rowspanRowClass}"${rowspanAttr}>${parseMarkdownInline(item)}</div>`;
    });
    html += '</div>';
    return html;
}

/* ----------  PIPE-TABLE → CSS-GRID  ---------- */
function parseGridTable(lines) {
    const rows = lines.map(l => {
        // Remove leading/trailing whitespace and pipes
        const trimmed = l.trim().replace(/^\||\|$/g, '');
        // Split by pipe and trim each cell
        const cells = trimmed.split('|').map(c => c.trim());
        // Filter out completely empty cells only if they're at the edges (from double pipes)
        // Keep intentionally empty cells (marked with -)
        return cells;
    });
    const cols = rows[0].length;

    // Check if first row is a header separator (e.g., |---|---|)
    const hasHeaderSeparator = rows.length > 1 &&
        rows[1].every(cell => /^-+$/.test(cell.trim()));

    // If header separator exists, skip it from rendering
    const dataRows = hasHeaderSeparator ? [rows[0], ...rows.slice(2)] : rows;
    const hasHeader = hasHeaderSeparator;

    // Color map for separator colors
    const colorMap = {
        'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
        'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
        'K': '#000000', 'GR': '#808080'
    };

    // Track column-wide colors (from :R-A: syntax in first row)
    const columnColors = [];

    // Process each cell and check for alignment markers and color codes
    const grid = dataRows.map((r, rowIndex) =>
        r.map((c, colIndex) => {
            let align = 'left';
            let content = c;
            let borderColor = null;

            // Check for column-wide color code: :R-A:text or :G-A:text (only in first row)
            if (rowIndex === 0) {
                const columnColorMatch = content.match(/^:([A-Z]+)-A:(.+)$/);
                if (columnColorMatch) {
                    const [, colorCode, rest] = columnColorMatch;
                    if (colorMap[colorCode]) {
                        columnColors[colIndex] = colorMap[colorCode];
                        borderColor = colorMap[colorCode];
                        content = rest;

                        // Check if content also has alignment markers
                        if (content.startsWith(':') && content.endsWith(':') && content.length > 2) {
                            align = 'center';
                            content = content.slice(1, -1).trim();
                        } else if (content.endsWith(':')) {
                            align = 'right';
                            content = content.slice(0, -1).trim();
                        }
                    }
                }
            }

            // If no column-wide color was set, check for single-cell color: :R:text
            if (!borderColor) {
                const colorAlignMatch = content.match(/^:([A-Z]+):(.+)$/);
                if (colorAlignMatch) {
                    const [, colorCode, rest] = colorAlignMatch;
                    if (colorMap[colorCode]) {
                        borderColor = colorMap[colorCode];
                        content = rest;

                        // Check if content also has alignment markers
                        if (content.startsWith(':') && content.endsWith(':') && content.length > 2) {
                            align = 'center';
                            content = content.slice(1, -1).trim();
                        } else if (content.endsWith(':')) {
                            align = 'right';
                            content = content.slice(0, -1).trim();
                        }
                    }
                }
            }

            // Apply column-wide color if set and no cell-specific color
            if (!borderColor && columnColors[colIndex]) {
                borderColor = columnColors[colIndex];
            }

            // Check for alignment without color codes
            if (!borderColor && !content.match(/^:[A-Z]+:/)) {
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
            }

            return {
                content: parseMarkdownInline(content),
                align: align,
                borderColor: borderColor
            };
        })
    );

    // First pass: identify ^^ cells and calculate rowspans
    const rowspans = {}; // key: "row-col", value: span count
    grid.forEach((row, rowIndex) => {
        row.forEach((cell, colIndex) => {
            if (cell.content.trim() === '^^') {
                // Find the first non-^^ cell above this one
                let targetRow = rowIndex - 1;
                while (targetRow >= 0 && grid[targetRow][colIndex].content.trim() === '^^') {
                    targetRow--;
                }
                if (targetRow >= 0) {
                    const targetKey = `${targetRow}-${colIndex}`;
                    rowspans[targetKey] = (rowspans[targetKey] || 1) + 1;
                }
            }
        });
    });

    // Second pass: identify which rows contain rowspan cells (for border styling)
    const rowsWithRowspan = new Set();
    Object.entries(rowspans).forEach(([key, span]) => {
        if (span > 1) {
            const [row, col] = key.split('-').map(Number);
            // Mark the starting row and all rows it spans
            for (let r = row; r < row + span; r++) {
                rowsWithRowspan.add(r);
            }
        }
    });

    /*  build a single <div> that looks like a table  */
    let html = `<div class="md-grid" style="--cols:${cols}">`;
    grid.forEach((row, i) => {
        row.forEach((cell, colIndex) => {
            // Skip cells with ^^ (they're merged)
            if (cell.content.trim() === '^^') {
                return;
            }

            const key = `${i}-${colIndex}`;
            const rowspan = rowspans[key] || 1;
            const isInRowspanRow = rowsWithRowspan.has(i);

            let styles = [];
            if (cell.align !== 'left') {
                styles.push(`text-align: ${cell.align}`);
            }
            if (cell.borderColor) {
                styles.push(`border-right-color: ${cell.borderColor} !important`);
            }
            if (rowspan > 1) {
                styles.push(`grid-row: span ${rowspan}`);
            }
            const styleAttr = styles.length > 0 ? ` style="${styles.join('; ')}"` : '';

            // Check if cell content is only "-" (empty cell marker)
            const isEmpty = cell.content.trim() === '-';
            const emptyClass = isEmpty ? ' md-empty' : '';
            // Only apply header class if we have a header separator and it's the first row
            const isHeader = hasHeader && i === 0;
            const rowspanAttr = rowspan > 1 ? ` rowspan="${rowspan}"` : '';
            const rowspanRowClass = isInRowspanRow ? ' md-rowspan-row' : '';
            html += `<div class="md-cell ${isHeader ? 'md-header' : ''}${emptyClass}${rowspanRowClass}"${rowspanAttr}${styleAttr}>${cell.content}</div>`;
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

    // New Links: url[text] -> <a href="url">text</a> (supports nested markdown)
    formatted = formatted.replace(/(https?:\/\/[^\s\[]+)\[(.+?)\]/g, (match, url, text) => {
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
        }
        styleObj.display = 'inline';
        styleObj.verticalAlign = 'baseline';
        styleObj.lineHeight = '1.3';
        styleObj.boxDecorationBreak = 'clone';
        styleObj.WebkitBoxDecorationBreak = 'clone';
        const styleStr = Object.entries(styleObj).map(([k, v]) => {
            const cssKey = k.replace(/([A-Z])/g, '-$1').toLowerCase();
            return `${cssKey}: ${v}`;
        }).join('; ');
        return `<span style="${styleStr}">${text}</span>`;
    });

    // Border box: #R#text#/# -> colored border (letters only)
    formatted = formatted.replace(/#([A-Z]+)#(.+?)#\/#/g, (match, colorCode, text) => {
        const colorMap = {
            'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
            'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
            'K': '#000000', 'GR': '#808080'
        };
        if (colorMap[colorCode]) {
            return `<span style="border: 2px solid ${colorMap[colorCode]}; padding: 2px 6px; border-radius: 4px; display: inline; box-decoration-break: clone; -webkit-box-decoration-break: clone;">${text}</span>`;
        }
        return match; // Not a valid color, leave unchanged
    });

    // Variable font size heading: #2#text#/# -> custom size (2em, 1.5em, etc.)
    formatted = formatted.replace(/#([\d.]+)#(.+?)#\/#/g, (match, size, text) => {
        return `<span style="font-size: ${size}em; font-weight: 600;">${text}</span>`;
    });

    // Heading: ##text## -> larger text
    formatted = formatted.replace(/##(.+?)##/g, '<span style="font-size: 1.3em; font-weight: 600;">$1</span>');

    // Small text: ..text.. -> smaller text
    formatted = formatted.replace(/\.\.(.+?)\.\./g, '<span style="font-size: 0.75em;">$1</span>');

    // Wavy underline: _.text._ -> wavy underline
    formatted = formatted.replace(/_\.(.+?)\._/g, '<span style="text-decoration: underline wavy;">$1</span>');

    // Colored horizontal separator with optional background/text color for content below
    // Pattern: [COLOR1]-----[COLOR2] or [COLOR1]-----[COLOR2-COLOR3] or -----#HEX-#HEX
    // Examples: R----- (red line), -----G (green bg), R-----G (red line + green bg)
    //           R-----K (red line + black bg), -----R-W (red bg + white text)
    //           -----#ff0000-#000000 (6-digit hex), -----#f00-#000 (3-digit hex)
    formatted = formatted.replace(/^([A-Z]+)?-{5,}((?:[A-Z]+(?:-[A-Z]+)?)|(?:#[0-9a-fA-F]{3,6}(?:-#[0-9a-fA-F]{3,6})?))?$/gm, (match, prefixColor, suffixColor) => {
        const colorMap = {
            'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
            'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
            'K': '#000000', 'GR': '#808080'
        };

        // Helper to expand 3-digit hex to 6-digit
        const expandHex = (hex) => {
            if (!hex || !hex.startsWith('#')) return hex;
            const color = hex.substring(1);
            if (color.length === 3) {
                return '#' + color[0] + color[0] + color[1] + color[1] + color[2] + color[2];
            }
            return hex;
        };

        let separatorStyle = '';
        if (prefixColor && colorMap[prefixColor]) {
            separatorStyle = ` style="background: ${colorMap[prefixColor]} !important;"`;
        }

        let result = `<div class="md-separator"${separatorStyle}></div>`;

        // Parse suffix color (can be color code or hex with optional text color)
        if (suffixColor) {
            let bgColor = '';
            let textColor = '';

            if (suffixColor.startsWith('#')) {
                // Hex color format: #RRGGBB or #RGB or #RRGGBB-#RRGGBB or #RGB-#RGB
                const hexParts = suffixColor.split('-');
                bgColor = expandHex(hexParts[0]);
                textColor = hexParts[1] ? expandHex(hexParts[1]) : '';
            } else if (suffixColor.includes('-')) {
                // Color code with text color: R-W, G-K, etc.
                const [bgCode, textCode] = suffixColor.split('-');
                bgColor = colorMap[bgCode] || '';
                textColor = colorMap[textCode] || '';
            } else if (colorMap[suffixColor]) {
                // Single color code format: R, G, B, etc.
                bgColor = colorMap[suffixColor];
            }

            if (bgColor) {
                result += `<div class="md-bg-section" data-bg-color="${bgColor}" data-text-color="${textColor}">`;
            }
        }

        return result;
    });

    // Bold: **text** -> <strong>text</strong>
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic: @@text@@ -> <em>text</em>
    formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

    // Colored underline: _R_text__ -> colored underline (must come before regular underline)
    formatted = formatted.replace(/_([A-Z]+)_(.+?)__/g, (match, colorCode, text) => {
        const colorMap = {
            'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
            'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
            'K': '#000000', 'GR': '#808080'
        };
        if (colorMap[colorCode]) {
            return `<u style="text-decoration-color: ${colorMap[colorCode]}; text-decoration-thickness: 2px;">${text}</u>`;
        }
        return match; // Not a valid color, leave unchanged
    });

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

    // Red highlight: !!text!! -> red background with white text
    formatted = formatted.replace(/!!(.+?)!!/g, '<span style="background: #ff0000; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">$1</span>');

    // Blue highlight: ??text?? -> blue background with white text
    formatted = formatted.replace(/\?\?(.+?)\?\?/g, '<span style="background: #0000ff; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">$1</span>');

    // Correct Answer: [[text]] -> text with hidden green highlight
    formatted = formatted.replace(/\[\[(.+?)\]\]/g, '<span class="correct-answer">$1</span>');

    // Word Connectors: [1]Word or [1-R]Word -> creates visual connection between words with same number
    // Process connectors and create wrapper with data attributes
    const connectorColors = ['#007bff', '#dc3545', '#28a745', '#fd7e14', '#6f42c1', '#20c997', '#e83e8c', '#17a2b8'];
    const colorMap = {
        'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
        'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
        'K': '#000000', 'GR': '#808080'
    };
    formatted = formatted.replace(/\[(\d+)(?:-([A-Z]+))?\](\S+)/g, (match, connId, colorCode, word) => {
        let color;
        if (colorCode && colorMap[colorCode]) {
            color = colorMap[colorCode];
        } else {
            const colorIndex = (parseInt(connId) - 1) % connectorColors.length;
            color = connectorColors[colorIndex];
        }
        return `<span class="word-connector" data-conn-id="${connId}" data-conn-color="${color}">${word}</span>`;
    });

    // Timeline: Timeline*Name or Timeline-R*Name or TimelineC-B*Name followed by list items
    // Timeline* = top-aligned, TimelineC* = center-aligned, -COLOR = custom separator color
    formatted = formatted.replace(/^(Timeline(?:C)?)(?:-([A-Z]+))?\*(.+?)$/gm, (match, type, colorCode, name) => {
        const isCenter = type === 'TimelineC';
        const alignStyle = isCenter ? 'align-items: center;' : 'align-items: flex-start;';
        const colorMap = {
            'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
            'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
            'K': '#000000', 'GR': '#808080'
        };
        const separatorColor = (colorCode && colorMap[colorCode]) ? colorMap[colorCode] : '#ffffff';
        return `<div class="md-timeline" style="display: flex; gap: 12px; margin: 8px 0; ${alignStyle}">
            <div class="md-timeline-left" style="flex: 0 0 150px; text-align: left; font-weight: 600; line-height: 1.4;">${name}</div>
            <div class="md-timeline-separator" style="width: 3px; background: ${separatorColor}; align-self: stretch; margin-top: 2px;"></div>
            <div class="md-timeline-right" style="flex: 1; line-height: 1.4;">`;
    });

    // Apply custom color syntaxes
    formatted = applyCustomColorSyntaxes(formatted);

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

        // New Links: url[text] -> <a href="url">text</a> (supports nested markdown)
        formatted = formatted.replace(/(https?:\/\/[^\s\[]+)\[(.+?)\]/g, (match, url, text) => {
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
            }
            styleObj.display = 'inline';
            styleObj.verticalAlign = 'baseline';
            styleObj.lineHeight = '1.3';
            styleObj.boxDecorationBreak = 'clone';
            styleObj.WebkitBoxDecorationBreak = 'clone';
            const styleStr = Object.entries(styleObj).map(([k, v]) => {
                const cssKey = k.replace(/([A-Z])/g, '-$1').toLowerCase();
                return `${cssKey}: ${v}`;
            }).join('; ');
            return `<span style="${styleStr}">${text}</span>`;
        });

        // Border box: #R#text#/# -> colored border (letters only)
        formatted = formatted.replace(/#([A-Z]+)#(.+?)#\/#/g, (match, colorCode, text) => {
            const colorMap = {
                'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                'K': '#000000', 'GR': '#808080'
            };
            if (colorMap[colorCode]) {
                return `<span style="border: 2px solid ${colorMap[colorCode]}; padding: 2px 6px; border-radius: 4px; display: inline; box-decoration-break: clone; -webkit-box-decoration-break: clone;">${text}</span>`;
            }
            return match; // Not a valid color, leave unchanged
        });

        // Variable font size heading: #2#text#/# -> custom size (2em, 1.5em, etc.)
        formatted = formatted.replace(/#([\d.]+)#(.+?)#\/#/g, (match, size, text) => {
            return `<span style="font-size: ${size}em; font-weight: 600;">${text}</span>`;
        });

        // Heading: ##text## -> larger text
        formatted = formatted.replace(/##(.+?)##/g, '<span style="font-size: 1.3em; font-weight: 600;">$1</span>');

        // Small text: ..text.. -> smaller text
        formatted = formatted.replace(/\.\.(.+?)\.\./g, '<span style="font-size: 0.75em;">$1</span>');

        // Wavy underline: _.text._ -> wavy underline
        formatted = formatted.replace(/_\.(.+?)\._/g, '<span style="text-decoration: underline wavy;">$1</span>');

        // Colored horizontal separator with optional background/text color for content below
        // Pattern: [COLOR1]-----[COLOR2] or [COLOR1]-----[COLOR2-COLOR3] or -----#HEX-#HEX
        formatted = formatted.replace(/^([A-Z]+)?-{5,}((?:[A-Z]+(?:-[A-Z]+)?)|(?:#[0-9a-fA-F]{3,6}(?:-#[0-9a-fA-F]{3,6})?))?$/gm, (match, prefixColor, suffixColor) => {
            const colorMap = {
                'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                'K': '#000000', 'GR': '#808080'
            };

            // Helper to expand 3-digit hex to 6-digit
            const expandHex = (hex) => {
                if (!hex || !hex.startsWith('#')) return hex;
                const color = hex.substring(1);
                if (color.length === 3) {
                    return '#' + color[0] + color[0] + color[1] + color[1] + color[2] + color[2];
                }
                return hex;
            };

            let separatorStyle = '';
            if (prefixColor && colorMap[prefixColor]) {
                separatorStyle = ` style="background: ${colorMap[prefixColor]} !important;"`;
            }

            let result = `<div class="md-separator"${separatorStyle}></div>`;

            // Parse suffix color (can be color code or hex with optional text color)
            if (suffixColor) {
                let bgColor = '';
                let textColor = '';

                if (suffixColor.startsWith('#')) {
                    // Hex color format: #RRGGBB or #RGB or #RRGGBB-#RRGGBB or #RGB-#RGB
                    const hexParts = suffixColor.split('-');
                    bgColor = expandHex(hexParts[0]);
                    textColor = hexParts[1] ? expandHex(hexParts[1]) : '';
                } else if (suffixColor.includes('-')) {
                    // Color code with text color: R-W, G-K, etc.
                    const [bgCode, textCode] = suffixColor.split('-');
                    bgColor = colorMap[bgCode] || '';
                    textColor = colorMap[textCode] || '';
                } else if (colorMap[suffixColor]) {
                    // Single color code format: R, G, B, etc.
                    bgColor = colorMap[suffixColor];
                }

                if (bgColor) {
                    result += `<div class="md-bg-section" data-bg-color="${bgColor}" data-text-color="${textColor}">`;
                }
            }

            return result;
        });

        // Bold: **text** -> <strong>text</strong>
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic: @@text@@ -> <em>text</em>
        formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

        // Colored underline: _R_text__ -> colored underline (must come before regular underline)
        formatted = formatted.replace(/_([A-Z]+)_(.+?)__/g, (match, colorCode, text) => {
            const colorMap = {
                'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                'K': '#000000', 'GR': '#808080'
            };
            if (colorMap[colorCode]) {
                return `<u style="text-decoration-color: ${colorMap[colorCode]}; text-decoration-thickness: 2px;">${text}</u>`;
            }
            return match; // Not a valid color, leave unchanged
        });

        // Underline: __text__ -> <u>text</u>
        formatted = formatted.replace(/__(.+?)__/g, '<u>$1</u>');

        // Strikethrough: ~~text~~ -> <del>text</del>
        formatted = formatted.replace(/~~(.+?)~~/g, '<del>$1</del>');

        // Superscript: ^text^ -> <sup>text</sup>
        formatted = formatted.replace(/\^(.+?)\^/g, '<sup>$1</sup>');

        // Subscript: ~text~ -> <sub>text</sub>
        formatted = formatted.replace(/~(.+?)~/g, '<sub>$1</sub>');

        // Sub-sublist: --- item -> ▪ item with more indent (small square)
        if (formatted.trim().startsWith('--- ')) {
            const content = formatted.replace(/^(\s*)--- (.+)$/, '$2');
            formatted = formatted.replace(/^(\s*)--- .+$/, '$1<span style="display: inline-flex; align-items: baseline; width: 100%; margin-left: 2em;"><span style="margin-right: 0.5em; flex-shrink: 0; position: relative; top: -0.05em; font-size: 0.85em;">▪</span><span style="flex: 1;">▪CONTENT▪</span></span>');
            formatted = formatted.replace('▪CONTENT▪', content);
        }
        // Sublist: -- item -> ◦ item with more indent (white circle)
        else if (formatted.trim().startsWith('-- ')) {
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
        formatted = formatted.replace(/!!(.+?)!!/g, '<span style="background: #ff0000; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">$1</span>');

        // Blue highlight: ??text?? -> blue background with white text
        formatted = formatted.replace(/\?\?(.+?)\?\?/g, '<span style="background: #0000ff; color: #ffffff; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">$1</span>');

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

        // Word Connectors: [1]Word or [1-R]Word -> creates visual connection between words with same number
        const connectorColors = ['#007bff', '#dc3545', '#28a745', '#fd7e14', '#6f42c1', '#20c997', '#e83e8c', '#17a2b8'];
        const colorMap = {
            'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
            'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
            'K': '#000000', 'GR': '#808080'
        };
        formatted = formatted.replace(/\[(\d+)(?:-([A-Z]+))?\](\S+)/g, (match, connId, colorCode, word) => {
            let color;
            if (colorCode && colorMap[colorCode]) {
                color = colorMap[colorCode];
            } else {
                const colorIndex = (parseInt(connId) - 1) % connectorColors.length;
                color = connectorColors[colorIndex];
            }
            return `<span class="word-connector" data-conn-id="${connId}" data-conn-color="${color}">${word}</span>`;
        });

        // Timeline: Timeline*Name or Timeline-R*Name or TimelineC-B*Name followed by list items
        // Timeline* = top-aligned, TimelineC* = center-aligned, -COLOR = custom separator color
        formatted = formatted.replace(/^(Timeline(?:C)?)(?:-([A-Z]+))?\*(.+?)$/gm, (match, type, colorCode, name) => {
            const isCenter = type === 'TimelineC';
            const alignStyle = isCenter ? 'align-items: center;' : 'align-items: flex-start;';
            const colorMap = {
                'R': '#ff0000', 'G': '#00ff00', 'B': '#0000ff', 'Y': '#ffff00',
                'O': '#ff8800', 'P': '#ff00ff', 'C': '#00ffff', 'W': '#ffffff',
                'K': '#000000', 'GR': '#808080'
            };
            const separatorColor = (colorCode && colorMap[colorCode]) ? colorMap[colorCode] : '#ffffff';
            return `<div class="md-timeline" style="display: flex; gap: 12px; margin: 8px 0; ${alignStyle}">
            <div class="md-timeline-left" style="flex: 0 0 150px; text-align: left; font-weight: 600; line-height: 1.4;">${name}</div>
            <div class="md-timeline-separator" style="width: 3px; background: ${separatorColor}; align-self: stretch; margin-top: 2px;"></div>
            <div class="md-timeline-right" style="flex: 1; line-height: 1.4;">`;
        });

        // Apply custom color syntaxes
        formatted = applyCustomColorSyntaxes(formatted);

        return formatted;
    });

    // Post-process to close timeline divs and handle background sections
    const processedLines = [];
    let inTimeline = false;
    let inBgSection = false;
    let bgColor = '';
    let textColor = '';

    for (let i = 0; i < formattedLines.length; i++) {
        const line = formattedLines[i];
        const isTimelineStart = line.includes('class="md-timeline"');
        const isListItem = line.trim().startsWith('<span style="display: inline-flex') &&
            (line.includes('•') || line.includes('◦') || line.includes('▪'));
        const isEmpty = line.trim() === '';

        // Check for background section markers (now with optional text color)
        const bgSectionMatch = line.match(/<div class="md-bg-section" data-bg-color="([^"]+)" data-text-color="([^"]*)">/);
        const isSeparator = line.includes('class="md-separator"');

        // If line has both separator and bg-section marker, handle both
        if (isSeparator && bgSectionMatch) {
            if (inBgSection) {
                processedLines.push('</div>');
            }
            processedLines.push(line);
            // Open the background wrapper div with optional text color
            bgColor = bgSectionMatch[1];
            textColor = bgSectionMatch[2];
            let styleStr = `background-color: ${bgColor}; padding: 2px 6px; margin: 0;`;
            if (textColor) {
                styleStr += ` color: ${textColor};`;
            }
            processedLines.push(`<div style="${styleStr}">`);
            inBgSection = true;
            continue;
        }

        // If we hit a separator without bg marker and we're in a background section, close it
        if (isSeparator && inBgSection) {
            processedLines.push('</div>');
            inBgSection = false;
            bgColor = '';
            processedLines.push(line);
            continue;
        }

        // If we hit a separator and not in bg section, just push it
        if (isSeparator) {
            processedLines.push(line);
            continue;
        }

        if (isTimelineStart) {
            processedLines.push(line);
            inTimeline = true;
        } else if (inTimeline && isEmpty) {
            processedLines.push('</div></div>');
            processedLines.push(line);
            inTimeline = false;
        } else if (inTimeline && !isListItem && line.trim() !== '') {
            processedLines.push('</div></div>');
            processedLines.push(line);
            inTimeline = false;
        } else {
            // Just push the line as-is (it's already inside the bg wrapper if inBgSection is true)
            processedLines.push(line);
        }
    }

    // Close timeline at end if still open
    if (inTimeline) {
        processedLines.push('</div></div>');
    }

    // Close background section at end if still open
    if (inBgSection) {
        processedLines.push('</div>');
    }

    return processedLines.reduce((acc, line, i) => {
        if (i === 0) return line;
        const prev = processedLines[i - 1];
        // Check for separator to avoid double line breaks (newline + block element break)
        const isSeparator = line.includes('class="md-separator"');
        const prevIsSeparator = prev.includes('class="md-separator"');

        // Check for background section wrapper
        const isBgWrapper = line.includes('background-color:') && line.trim().startsWith('<div style=');
        const prevIsBgWrapper = prev.includes('background-color:') && prev.trim().startsWith('<div style=');

        // Don't add newline after timeline opening or before timeline closing
        const isTimelineStart = prev.includes('class="md-timeline"');
        const isTimelineEnd = line === '</div></div>';
        const isListItem = line.trim().startsWith('<span style="display: inline-flex');

        if (isSeparator || prevIsSeparator || isBgWrapper || prevIsBgWrapper || (isTimelineStart && isListItem) || isTimelineEnd) {
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

function toggleCellComplete() {
    if (!contextMenuCell) return;

    const { rowIndex, colIndex, tdElement } = contextMenuCell;
    const style = getCellStyle(rowIndex, colIndex);
    const newValue = !style.complete;

    // Apply to multiple cells if selected
    if (selectedCells.length > 0) {
        selectedCells.forEach(cell => {
            setCellStyle(cell.row, cell.col, 'complete', newValue);
            if (newValue) {
                cell.td.classList.add('cell-complete');
            } else {
                cell.td.classList.remove('cell-complete');
            }
        });
        showToast(`${newValue ? 'Marked' : 'Unmarked'} ${selectedCells.length} cells as complete`, 'success');
    } else {
        // Apply to single cell
        setCellStyle(rowIndex, colIndex, 'complete', newValue);
        if (newValue) {
            tdElement.classList.add('cell-complete');
        } else {
            tdElement.classList.remove('cell-complete');
        }
    }

    document.getElementById('ctxComplete').classList.toggle('checked', newValue);
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
    document.getElementById('ctxComplete').classList.toggle('checked', style.complete === true);

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

    // Add click-outside-to-close listener
    setTimeout(() => {
        document.addEventListener('click', closeCellContextMenuOnClickOutside);
    }, 10);
}

function closeCellContextMenu() {
    document.getElementById('cellContextMenu').classList.remove('show');
    document.removeEventListener('click', closeCellContextMenuOnClickOutside);
    contextMenuCell = null;
}

function closeCellContextMenuOnClickOutside(event) {
    const menu = document.getElementById('cellContextMenu');
    if (menu && menu.classList.contains('show')) {
        // Close if clicking outside the menu
        if (!menu.contains(event.target)) {
            closeCellContextMenu();
        }
    }
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

    // OK button
    const okBtn = document.createElement('button');
    okBtn.className = 'btn btn-success';
    okBtn.textContent = 'OK';
    okBtn.style.marginLeft = 'auto';
    okBtn.onclick = () => applyUnifiedColors(rowIndex, colIndex);

    customSection.appendChild(customLabel);
    customSection.appendChild(customInput);
    customSection.appendChild(customBtn);
    customSection.appendChild(okBtn);

    popup.appendChild(customSection);

    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'color-picker-close';
    closeBtn.textContent = '×';
    closeBtn.onclick = () => document.body.removeChild(overlay);

    popup.appendChild(closeBtn);

    // Create color history sidebar (right panel)
    const historySidebar = document.createElement('div');
    historySidebar.className = 'color-history-sidebar';
    historySidebar.id = 'colorHistorySidebar';

    const historyTitle = document.createElement('div');
    historyTitle.className = 'color-history-sidebar-title';
    historyTitle.textContent = 'Most Used';
    historySidebar.appendChild(historyTitle);

    const historyList = document.createElement('div');
    historyList.className = 'color-history-list';
    historyList.id = 'cellColorHistoryGrid';
    historySidebar.appendChild(historyList);

    popup.appendChild(historySidebar);

    overlay.appendChild(popup);
    document.body.appendChild(overlay);

    // Load cell color history AFTER adding to DOM
    loadCellColorHistory();

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
    // Track cell color usage
    trackCellColorUsage(selectedBgColor, selectedTextColor);

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

// Load and display cell color history
function loadCellColorHistory() {
    const historyGrid = document.getElementById('cellColorHistoryGrid');
    if (!historyGrid) {
        console.log('History grid not found!');
        return;
    }

    historyGrid.innerHTML = '';

    // Load cell color usage history from localStorage
    const cellColorHistory = JSON.parse(localStorage.getItem('cellColorHistory') || '[]');
    console.log('Loading cell color history, found', cellColorHistory.length, 'colors');

    // Sort by usage count (most used first)
    cellColorHistory.sort((a, b) => b.count - a.count);

    // Display top 10 most used colors
    const topColors = cellColorHistory.slice(0, 10);

    if (topColors.length === 0) {
        historyGrid.innerHTML = '<div style="padding: 8px; text-align: center; color: #999; font-size: 12px;">No history yet</div>';
        console.log('No color history to display');
        return;
    }

    console.log('Displaying', topColors.length, 'colors in history');

    topColors.forEach((item, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'cell-color-history-item';
        historyItem.style.backgroundColor = item.bg;
        historyItem.style.color = item.fg;
        historyItem.style.position = 'relative';
        historyItem.textContent = 'Aa';
        historyItem.title = `BG: ${item.bg}, Text: ${item.fg}\nUsed ${item.count} time${item.count > 1 ? 's' : ''}`;

        historyItem.onclick = () => {
            selectedBgColor = item.bg;
            selectedTextColor = item.fg;
            updateColorPickerState();
        };

        // Add delete button that appears on hover
        const deleteBtn = document.createElement('span');
        deleteBtn.className = 'cell-history-delete';
        deleteBtn.textContent = '×';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteCellColorHistory(index);
        };
        historyItem.appendChild(deleteBtn);

        historyGrid.appendChild(historyItem);
    });
}

function deleteCellColorHistory(index) {
    const cellColorHistory = JSON.parse(localStorage.getItem('cellColorHistory') || '[]');
    cellColorHistory.sort((a, b) => b.count - a.count);
    cellColorHistory.splice(index, 1);
    localStorage.setItem('cellColorHistory', JSON.stringify(cellColorHistory));
    loadCellColorHistory();
    showToast('Color removed from history', 'success');
}

function trackCellColorUsage(bg, fg) {
    const cellColorHistory = JSON.parse(localStorage.getItem('cellColorHistory') || '[]');

    // Normalize colors to hex format
    const bgHex = rgbToHex(bg);
    const fgHex = rgbToHex(fg);

    console.log('Tracking color usage:', { bg, fg, bgHex, fgHex });

    // Find if this color combination already exists
    const existingIndex = cellColorHistory.findIndex(item =>
        item.bg.toLowerCase() === bgHex.toLowerCase() &&
        item.fg.toLowerCase() === fgHex.toLowerCase()
    );

    if (existingIndex >= 0) {
        // Increment count
        cellColorHistory[existingIndex].count++;
        console.log('Incremented existing color, new count:', cellColorHistory[existingIndex].count);
    } else {
        // Add new entry
        cellColorHistory.push({ bg: bgHex, fg: fgHex, count: 1 });
        console.log('Added new color to history');
    }

    localStorage.setItem('cellColorHistory', JSON.stringify(cellColorHistory));
    console.log('Saved to localStorage, total colors:', cellColorHistory.length);
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

function setCellRank() {
    if (!contextMenuCell) return;

    const { rowIndex, colIndex } = contextMenuCell;
    const sheet = tableData.sheets[currentSheet];
    const cellKey = `${rowIndex}-${colIndex}`;

    // Get current rank if exists
    const currentRank = sheet.cellStyles?.[cellKey]?.rank || '';

    // Prompt for rank (number or empty to remove)
    const rankInput = prompt('Set sort rank (number, or leave empty to remove):', currentRank);

    if (rankInput === null) {
        closeCellContextMenu();
        return; // User cancelled
    }

    // Initialize cellStyles if needed
    if (!sheet.cellStyles) {
        sheet.cellStyles = {};
    }
    if (!sheet.cellStyles[cellKey]) {
        sheet.cellStyles[cellKey] = {};
    }

    if (rankInput.trim() === '') {
        // Remove rank
        delete sheet.cellStyles[cellKey].rank;
        closeCellContextMenu();
        renderTable();
        showToast('Rank removed', 'success');
    } else {
        const rank = parseInt(rankInput);
        if (isNaN(rank)) {
            showToast('Please enter a valid number', 'error');
            return;
        }

        // Set rank
        sheet.cellStyles[cellKey].rank = rank;
        closeCellContextMenu();
        renderTable();
        showToast(`Rank set to ${rank}`, 'success');
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

            renderSidebar();
            renderTable();
        }
    } catch (error) {
        console.error('Error adding sheet:', error);
    }
}

async function addSubSheet(parentIndex) {
    const parentSheet = tableData.sheets[parentIndex];
    const subSheetName = prompt('Enter sub-sheet name:', `${parentSheet.name} - Sub`);
    if (!subSheetName) return;

    try {
        const response = await fetch('/api/sheets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: subSheetName, parentSheet: parentIndex })
        });

        if (response.ok) {
            const result = await response.json();
            tableData.sheets.push({
                name: subSheetName,
                columns: [],
                rows: [],
                parentSheet: parentIndex
            });
            currentSheet = result.sheetIndex;

            // Inherit parent's category
            const parentCategory = tableData.sheetCategories[parentIndex] || tableData.sheetCategories[String(parentIndex)] || null;
            if (parentCategory !== null) {
                initializeCategories();
                tableData.sheetCategories[currentSheet] = parentCategory;
            }

            await saveData();
            renderSidebar();
            renderTable();
            showToast(`Sub-sheet added under "${parentSheet.name}"`, 'success');
        }
    } catch (error) {
        console.error('Error adding sub-sheet:', error);
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
    renderSidebar();
    renderSidebar();
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
    renderSidebar();
    renderSidebar();
    renderTable();
    showToast('Sheet moved down', 'success');
}

async function deleteSheet(index) {
    if (tableData.sheets.length <= 1) {
        alert('Cannot delete the last sheet!');
        return;
    }

    const sheetName = tableData.sheets[index].name;

    // Check if this sheet has sub-sheets
    const hasSubSheets = tableData.sheets.some(sheet => sheet.parentSheet === index);
    if (hasSubSheets) {
        if (!confirm(`"${sheetName}" has sub-sheets. Deleting it will also delete all its sub-sheets. Continue?`)) {
            return;
        }
    } else {
        if (!confirm(`Delete sheet "${sheetName}"?`)) return;
    }

    try {
        const response = await fetch(`/api/sheets/${index}`, { method: 'DELETE' });
        if (response.ok) {
            // Delete the sheet and all its sub-sheets
            const sheetsToDelete = [index];
            tableData.sheets.forEach((sheet, idx) => {
                if (sheet.parentSheet === index) {
                    sheetsToDelete.push(idx);
                }
            });

            // Sort in descending order to delete from end to start (prevents index shifting issues)
            sheetsToDelete.sort((a, b) => b - a);
            sheetsToDelete.forEach(idx => {
                tableData.sheets.splice(idx, 1);
            });

            // Reindex sheetCategories after deletion
            const newSheetCategories = {};
            const deletedCount = sheetsToDelete.length;
            Object.keys(tableData.sheetCategories).forEach(key => {
                const sheetIndex = parseInt(key);
                // Count how many deleted sheets are before this index
                const deletedBefore = sheetsToDelete.filter(delIdx => delIdx < sheetIndex).length;

                if (!sheetsToDelete.includes(sheetIndex)) {
                    // This sheet wasn't deleted, reindex it
                    newSheetCategories[sheetIndex - deletedBefore] = tableData.sheetCategories[key];
                }
            });
            tableData.sheetCategories = newSheetCategories;

            // Reindex parentSheet references
            tableData.sheets.forEach((sheet, idx) => {
                if (sheet.parentSheet !== undefined && sheet.parentSheet !== null) {
                    // Count how many deleted sheets are before the parent
                    const deletedBeforeParent = sheetsToDelete.filter(delIdx => delIdx < sheet.parentSheet).length;
                    sheet.parentSheet = sheet.parentSheet - deletedBeforeParent;
                }
            });

            if (currentSheet >= tableData.sheets.length) {
                currentSheet = tableData.sheets.length - 1;
            }

            await saveData();
            renderSidebar();
            renderTable();
            autoSaveActiveSheet();
            showToast('Sheet deleted', 'success');
        }
    } catch (error) {
        console.error('Error deleting sheet:', error);
    }
}

function switchSheet(index) {
    // Save current scroll position before switching
    if (currentSheet !== index) {
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            const scrollPositions = JSON.parse(localStorage.getItem('sheetScrollPositions') || '{}');
            scrollPositions[currentSheet] = {
                scrollTop: tableContainer.scrollTop,
                scrollLeft: tableContainer.scrollLeft
            };
            localStorage.setItem('sheetScrollPositions', JSON.stringify(scrollPositions));
        }
    }

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

    renderSidebar();
    renderTable();
    autoSaveActiveSheet();

    // Apply font size scale after rendering
    setTimeout(() => {
        applyFontSizeScale();
    }, 0);

    // Restore scroll position after rendering
    setTimeout(() => {
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            const scrollPositions = JSON.parse(localStorage.getItem('sheetScrollPositions') || '{}');
            const savedPosition = scrollPositions[index];
            if (savedPosition) {
                tableContainer.scrollTop = savedPosition.scrollTop || 0;
                tableContainer.scrollLeft = savedPosition.scrollLeft || 0;
            }
        }
    }, 0);
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

    // Helper function to render a sheet and its sub-sheets recursively
    function renderSheetItem(sheet, index, level = 0) {
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
        item.style.paddingLeft = (level * 20 + 15) + 'px';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'sheet-item-name';
        nameSpan.textContent = sheet.name;

        nameSpan.onclick = () => {
            switchSheet(index);
            toggleSheetList();
        };

        item.appendChild(nameSpan);
        sheetList.appendChild(item);

        // Render sub-sheets
        tableData.sheets.forEach((subSheet, subIndex) => {
            if (subSheet.parentSheet === index) {
                renderSheetItem(subSheet, subIndex, level + 1);
            }
        });
    }

    // Render only top-level sheets (those without a parent)
    tableData.sheets.forEach((sheet, index) => {
        if (!sheet.parentSheet && sheet.parentSheet !== 0) {
            renderSheetItem(sheet, index, 0);
        }
    });

    // Render sub-sheet bar
    renderSubSheetBar();
}

function renderSubSheetBar() {
    const subsheetTabs = document.getElementById('subsheetTabs');
    if (!subsheetTabs) return;

    subsheetTabs.innerHTML = '';

    // Get current sheet's parent (if it's a sub-sheet) or use current sheet as parent
    const currentSheetData = tableData.sheets[currentSheet];
    const parentIndex = currentSheetData?.parentSheet !== undefined ? currentSheetData.parentSheet : currentSheet;
    const parentSheet = tableData.sheets[parentIndex];

    if (!parentSheet) return;

    // Add parent sheet tab
    const parentTab = document.createElement('div');
    parentTab.className = `subsheet-tab ${currentSheet === parentIndex ? 'active' : ''}`;
    parentTab.dataset.sheetIndex = parentIndex;

    const parentName = document.createElement('span');
    parentName.className = 'subsheet-tab-name';
    parentName.textContent = parentSheet.name;

    parentTab.appendChild(parentName);
    parentTab.onclick = () => switchSheet(parentIndex);

    // Add right-click context menu for parent sheet
    parentTab.oncontextmenu = (e) => {
        e.preventDefault();
        showSubSheetContextMenu(e, parentIndex);
    };

    subsheetTabs.appendChild(parentTab);

    // Add sub-sheets
    tableData.sheets.forEach((sheet, index) => {
        if (sheet.parentSheet === parentIndex) {
            const tab = document.createElement('div');
            tab.className = `subsheet-tab ${currentSheet === index ? 'active' : ''}`;
            tab.dataset.sheetIndex = index;

            const name = document.createElement('span');
            name.className = 'subsheet-tab-name';
            name.textContent = sheet.name;

            tab.appendChild(name);
            tab.onclick = () => switchSheet(index);

            // Add right-click context menu for sub-sheet
            tab.oncontextmenu = (e) => {
                e.preventDefault();
                showSubSheetContextMenu(e, index);
            };

            subsheetTabs.appendChild(tab);
        }
    });

    // Add + button to create new sub-sheet
    const addBtn = document.createElement('button');
    addBtn.className = 'subsheet-add-btn';
    addBtn.innerHTML = '+';
    addBtn.title = 'Add sub-sheet';
    addBtn.onclick = () => addSubSheet(parentIndex);
    subsheetTabs.appendChild(addBtn);
}

function showSubSheetContextMenu(event, sheetIndex) {
    // Remove any existing context menu
    const existingMenu = document.getElementById('subsheetContextMenu');
    if (existingMenu) {
        existingMenu.remove();
    }

    // Create context menu
    const menu = document.createElement('div');
    menu.id = 'subsheetContextMenu';
    menu.className = 'subsheet-context-menu';
    menu.style.position = 'fixed';
    menu.style.left = event.clientX + 'px';
    menu.style.top = event.clientY + 'px';

    // Rename option
    const renameItem = document.createElement('div');
    renameItem.className = 'context-menu-item';
    renameItem.innerHTML = '<span>✏️</span><span>Rename</span>';
    renameItem.onclick = () => {
        showRenameModal(sheetIndex);
        menu.remove();
    };

    // Delete option
    const deleteItem = document.createElement('div');
    deleteItem.className = 'context-menu-item';
    deleteItem.innerHTML = '<span>🗑️</span><span>Delete</span>';
    deleteItem.onclick = () => {
        deleteSheet(sheetIndex);
        menu.remove();
    };

    menu.appendChild(renameItem);
    menu.appendChild(deleteItem);
    document.body.appendChild(menu);

    // Close menu when clicking outside
    const closeMenu = (e) => {
        if (!menu.contains(e.target)) {
            menu.remove();
            document.removeEventListener('click', closeMenu);
        }
    };
    setTimeout(() => document.addEventListener('click', closeMenu), 0);
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

let moveToCategorySheetIndex = null;

function showMoveToCategoryModal(sheetIndex) {
    moveToCategorySheetIndex = sheetIndex; // Store the sheet index

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
    renderSidebar();
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
    renderSidebar();
    closeRenameCategoryModal();
    showToast(`Category renamed to "${newName}"`, 'success');
};

// Move to category form handler
document.getElementById('moveToCategoryForm').onsubmit = async function (e) {
    e.preventDefault();
    const targetCategory = document.getElementById('targetCategory').value;
    const sheetToMove = moveToCategorySheetIndex !== null ? moveToCategorySheetIndex : currentSheet;

    initializeCategories();

    // Move the selected sheet
    if (targetCategory) {
        tableData.sheetCategories[sheetToMove] = targetCategory;
    } else {
        delete tableData.sheetCategories[sheetToMove];
    }

    // Also move all sub-sheets to the same category
    tableData.sheets.forEach((sheet, index) => {
        if (sheet.parentSheet === sheetToMove) {
            if (targetCategory) {
                tableData.sheetCategories[index] = targetCategory;
            } else {
                delete tableData.sheetCategories[index];
            }
        }
    });

    await saveData();
    renderSidebar();
    closeMoveToCategoryModal();
    showToast('Sheet and sub-sheets moved to category', 'success');
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

        renderSidebar();
        renderSidebar();
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

            renderSidebar();
            renderSidebar();
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
    renderSidebar();
    renderSidebar();
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
    renderSidebar();

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
    renderSidebar();

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
                    // Don't add search-highlight to cell - preserve cell background color
                    // cell.classList.add('search-highlight');

                    // Highlight markdown preview if it exists
                    const preview = cell.querySelector('.markdown-preview');
                    if (preview) {
                        // Don't add search-highlight to preview - preserve cell background
                        // preview.classList.add('search-highlight');

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

function positionCursorAtMouseClick(textarea, mouseEvent) {
    requestAnimationFrame(() => {
        const style = window.getComputedStyle(textarea);

        // Robust line-height calculation
        let lineHeight = parseFloat(style.lineHeight);
        if (isNaN(lineHeight)) {
            // If 'normal' or invalid, measure it dynamically
            const temp = document.createElement('div');
            temp.style.position = 'absolute';
            temp.style.visibility = 'hidden';
            temp.style.whiteSpace = 'pre';
            temp.style.font = style.font;
            temp.style.fontFamily = style.fontFamily;
            temp.style.fontSize = style.fontSize;
            temp.style.fontWeight = style.fontWeight;
            temp.style.padding = '0';
            temp.style.border = '0';
            temp.textContent = 'Mg';
            document.body.appendChild(temp);
            lineHeight = temp.clientHeight;
            document.body.removeChild(temp);
        }

        // Get padding and border
        const paddingTop = parseFloat(style.paddingTop) || 0;
        const borderTop = parseFloat(style.borderTopWidth) || 0;

        // Calculate cursor line position
        const lines = textarea.value.substr(0, textarea.selectionStart).split('\n');
        const cursorLineIndex = lines.length - 1;
        const cursorLineTop = paddingTop + (cursorLineIndex * lineHeight);

        // Get the mouse Y position relative to the textarea border box
        const textareaRect = textarea.getBoundingClientRect();
        const mouseY = mouseEvent.clientY - textareaRect.top;

        // Calculate scroll position so the center of the cursor line aligns with mouse Y
        // We want: borderTop + cursorLineTop - scrollTop + (lineHeight/2) = mouseY
        // So: scrollTop = borderTop + cursorLineTop + lineHeight/2 - mouseY

        const targetScrollTop = borderTop + cursorLineTop + (lineHeight / 2) - mouseY;

        // Ensure we don't scroll beyond the content bounds
        const maxScrollTop = Math.max(0, textarea.scrollHeight - textarea.clientHeight);
        textarea.scrollTop = Math.max(0, Math.min(targetScrollTop, maxScrollTop));
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
                if (cellStyle.complete) td.classList.add('cell-complete');
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

                // Add rank badge if cell has a rank
                if (cellStyle.rank !== undefined) {
                    td.style.position = 'relative';
                    const rankBadge = document.createElement('div');
                    rankBadge.className = 'cell-rank-badge';
                    rankBadge.textContent = cellStyle.rank;
                    rankBadge.title = `Sort rank: ${cellStyle.rank}`;
                    td.appendChild(rankBadge);
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

                    // If this cell has markdown, also adjust for preview height
                    const cell = textarea.closest('td');
                    if (cell && textarea.classList.contains('has-markdown')) {
                        adjustCellHeightForMarkdown(cell);
                    }
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
            if (cellStyle.complete) td.classList.add('cell-complete');
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

            // Add rank badge if cell has a rank
            if (cellStyle.rank !== undefined) {
                td.style.position = 'relative';
                const rankBadge = document.createElement('div');
                rankBadge.className = 'cell-rank-badge';
                rankBadge.textContent = cellStyle.rank;
                rankBadge.title = `Sort rank: ${cellStyle.rank}`;
                td.appendChild(rankBadge);
            }

            input.oncontextmenu = (e) => showCellContextMenu(e, rowIndex, colIndex, input, td);
            td.oncontextmenu = (e) => showCellContextMenu(e, rowIndex, colIndex, input, td);

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

    // Update row count display
    updateRowCountDisplay();
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

function stripMarkdown(text, preserveLinks = false) {
    if (!text) return '';
    let stripped = String(text);

    // Remove correct answer markers: [[text]] -> text
    stripped = stripped.replace(/\[\[(.+?)\]\]/g, '$1');

    // Remove color/style markers: {fg:#fff;bg:#000}text{/} -> text
    stripped = stripped.replace(/\{[^}]*\}(.+?)\{\/\}/g, '$1');

    // Remove bold markers: **text** -> text
    stripped = stripped.replace(/\*\*(.+?)\*\*/g, '$1');

    // Remove colored underline markers: _R_text__ -> text
    stripped = stripped.replace(/_[A-Z]+_(.+?)__/g, '$1');

    // Remove underline markers: __text__ -> text
    stripped = stripped.replace(/__(.+?)__/g, '$1');

    // Remove highlight markers: @@text@@ -> text
    stripped = stripped.replace(/@@(.+?)@@/g, '$1');

    // Remove variable font size heading markers: #2#text#/# -> text
    stripped = stripped.replace(/#[\d.]+#(.+?)#\/#/g, '$1');

    // Remove border box markers: #R#text#/# -> text
    stripped = stripped.replace(/#[A-Z]+#(.+?)#\/#/g, '$1');

    // Remove header markers: ##text## -> text
    stripped = stripped.replace(/##(.+?)##/g, '$1');

    // Remove small text markers: ..text.. -> text
    stripped = stripped.replace(/\.\.(.+?)\.\./g, '$1');

    // Remove wavy underline markers: _.text._ -> text
    stripped = stripped.replace(/_\.(.+?)\._/g, '$1');

    // Remove colored horizontal separator: R-----, -----G, R-----G, R-----K, -----R-W, -----#ff0000, -----#f00, etc. -> (empty)
    stripped = stripped.replace(/^[A-Z]*-{5,}(?:[A-Z]+(?:-[A-Z]+)?|#[0-9a-fA-F]{3,6}(?:-#[0-9a-fA-F]{3,6})?)?$/gm, '');

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

    // Remove Math markers: \( ... \) -> ...
    stripped = stripped.replace(/\\\((.*?)\\\)/g, '$1');

    // Remove superscript markers: ^text^ -> text
    stripped = stripped.replace(/\^(.+?)\^/g, '$1');

    // Remove subscript markers: ~text~ -> text
    stripped = stripped.replace(/~(.+?)~/g, '$1');

    if (!preserveLinks) {
        // Remove link markers: {link:url}text{/} -> text
        stripped = stripped.replace(/\{link:[^}]*\}(.+?)\{\/\}/g, '$1');

        // Remove new link markers: url[text] -> text
        stripped = stripped.replace(/(https?:\/\/[^\s\[]+)\[(.+?)\]/g, '$2');
    }

    // Remove collapsible text markers: {{text}} -> text
    stripped = stripped.replace(/\{\{(.+?)\}\}/g, '$1');

    // Remove bullet markers: - item -> item
    stripped = stripped.replace(/^\s*-\s+/gm, '');

    // Remove sub-bullet markers: -- item -> item
    stripped = stripped.replace(/^\s*--\s+/gm, '');

    // Remove sub-sub-bullet markers: --- item -> item
    stripped = stripped.replace(/^\s*---\s+/gm, '');

    // Remove Table*N marker
    stripped = stripped.replace(/^Table\*\d+(?:_[^\s\n,]+)?(?:_[^\s\n,]+)?(?:[\n\s,]+)/i, '');

    // Remove Math markers: \( ... \) -> ...
    stripped = stripped.replace(/\\\((.*?)\\\)/g, '$1');

    // Remove Timeline markers: Timeline*Name or Timeline-R*Name -> Name
    stripped = stripped.replace(/^Timeline(?:C)?(?:-[A-Z]+)?\*(.+?)$/gm, '$1');


    // Remove word connector markers: [1]Word or [1-R]Word -> Word
    stripped = stripped.replace(/\[(\d+)(?:-[A-Z]+)?\](\S+)/g, '$2');

    return stripped;
}

function sortColumn(colIndex, direction) {
    const sheet = tableData.sheets[currentSheet];
    const col = sheet.columns[colIndex];

    // Create array of row indices with their values
    const rowsWithIndices = sheet.rows.map((row, index) => {
        const cellKey = `${index}-${colIndex}`;
        const cellStyle = sheet.cellStyles?.[cellKey];
        return {
            index: index,
            value: row[colIndex] || '',
            row: row,
            rank: cellStyle?.rank, // Get rank if exists
            cellStyles: sheet.cellStyles ? Object.keys(sheet.cellStyles)
                .filter(key => key.startsWith(`${index}-`))
                .reduce((obj, key) => {
                    obj[key] = sheet.cellStyles[key];
                    return obj;
                }, {}) : {}
        };
    });

    // Sort based on rank first, then column type
    rowsWithIndices.sort((a, b) => {
        // If both have ranks, sort by rank
        if (a.rank !== undefined && b.rank !== undefined) {
            return direction === 'asc' ? a.rank - b.rank : b.rank - a.rank;
        }
        // If only one has rank, it comes first
        if (a.rank !== undefined) return -1;
        if (b.rank !== undefined) return 1;

        // Neither has rank, sort normally
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
let showSubSheetsInF1 = localStorage.getItem('showSubSheetsInF1') !== 'false'; // Default true

function openF1Popup() {
    const popup = document.getElementById('f1Popup');
    popup.classList.add('show');

    // Clear search input but keep the mode
    const searchInput = document.getElementById('f1SearchInput');
    if (searchInput) searchInput.value = '';

    // Restore the mode icon and color based on current mode
    const modeIcon = document.getElementById('f1SearchModeIcon');
    const toggle = document.getElementById('f1SearchModeToggle');
    if (modeIcon && toggle) {
        if (f1SearchMode === '*') {
            modeIcon.textContent = '*';
            toggle.style.color = '#00ff9d';
            toggle.title = 'Search all sheets';
        } else if (f1SearchMode === '#') {
            modeIcon.textContent = '#';
            toggle.style.color = '#00f3ff';
            toggle.title = 'Search sheet content';
        } else {
            modeIcon.textContent = '🔍';
            toggle.style.color = '';
            toggle.title = 'Normal search';
        }
    }

    // Set selected category to current category
    selectedF1Category = currentCategory;

    // Populate categories and sheets
    populateF1Categories();
    populateF1Sheets();

    // Set initial state of toggle button
    const btn = document.getElementById('toggleSubSheetsBtn');
    if (btn) {
        btn.style.opacity = showSubSheetsInF1 ? '1' : '0.5';
        btn.title = showSubSheetsInF1 ? 'Hide Sub-sheets' : 'Show Sub-sheets';
    }

    // Focus search input
    setTimeout(() => {
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

function toggleF1SubSheets() {
    showSubSheetsInF1 = !showSubSheetsInF1;
    localStorage.setItem('showSubSheetsInF1', showSubSheetsInF1);

    // Update button appearance
    const btn = document.getElementById('toggleSubSheetsBtn');
    if (btn) {
        btn.style.opacity = showSubSheetsInF1 ? '1' : '0.5';
        btn.title = showSubSheetsInF1 ? 'Hide Sub-sheets' : 'Show Sub-sheets';
    }

    populateF1Sheets(document.getElementById('f1SearchInput')?.value ? true : false);
}

// F2 Popup - Recent Sheets
function openF2Popup() {
    const popup = document.getElementById('f2Popup');
    popup.classList.add('show');

    // Clear search input
    const searchInput = document.getElementById('f2SearchInput');
    if (searchInput) searchInput.value = '';

    // Populate recent sheets
    populateF2RecentSheets();

    // Focus on search input
    setTimeout(() => {
        if (searchInput) {
            searchInput.focus();
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

function filterF2Sheets() {
    const searchInput = document.getElementById('f2SearchInput');
    const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const items = document.querySelectorAll('.f2-sheet-item');

    items.forEach(item => {
        const sheetName = item.querySelector('.f2-sheet-name');
        const name = sheetName ? sheetName.textContent.toLowerCase() : '';

        if (name.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
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

        // Show sub-sheets with parent name: "Subsheet [Parent]"
        if (sheet.parentSheet !== undefined && sheet.parentSheet !== null) {
            const parentSheet = tableData.sheets[sheet.parentSheet];
            if (parentSheet) {
                name.innerHTML = `${sheet.name} <span class="f2-parent-name">[${parentSheet.name}]</span>`;
            } else {
                name.textContent = sheet.name;
            }
        } else {
            name.textContent = sheet.name;
        }

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

    // Hide color section by default (collapsed)
    colorSection.style.display = 'none';
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

function searchGoogleWithExtra(event) {
    event.preventDefault();
    event.stopPropagation();

    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Get the extra text from localStorage (default: "make this text bengali as its in bengali phonetic")
    const extraText = localStorage.getItem('searchExtraText') || 'make this text bengali as its in bengali phonetic';

    // Strip markdown formatting before searching
    const cleanText = stripMarkdown(selectedText);

    // Combine selected text with extra text
    const fullSearchQuery = `${cleanText} ${extraText}`;

    // Open Google search in new tab
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(fullSearchQuery)}`;
    window.open(searchUrl, '_blank');

    closeQuickFormatter();
    showToast('Searching with extra text', 'success');
}

function editSearchExtraText(event) {
    event.preventDefault();
    event.stopPropagation();

    // Get current extra text
    const currentText = localStorage.getItem('searchExtraText') || 'make this text bengali as its in bengali phonetic';

    // Prompt user to edit
    const newText = prompt('Edit the extra text to add to searches:', currentText);

    if (newText !== null && newText.trim() !== '') {
        localStorage.setItem('searchExtraText', newText.trim());
        showToast('Search extra text updated', 'success');
    }

    return false; // Prevent context menu
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

// Helper function to calculate visual width of text (handles Unicode/Bangla properly)
function getVisualTextWidth(text) {
    // Create a temporary element to measure actual text width
    const tempSpan = document.createElement('span');
    tempSpan.style.visibility = 'hidden';
    tempSpan.style.position = 'absolute';
    tempSpan.style.whiteSpace = 'pre';
    tempSpan.style.fontFamily = 'Vrinda, "Segoe UI", Tahoma, Geneva, Verdana, sans-serif';
    tempSpan.style.fontSize = '14px'; // Match table font size
    tempSpan.textContent = text;
    
    document.body.appendChild(tempSpan);
    const width = tempSpan.offsetWidth;
    document.body.removeChild(tempSpan);
    
    // Convert pixel width to approximate character width (assuming ~8px per char for monospace-like alignment)
    return Math.ceil(width / 8);
}

// Helper function to pad text properly for Unicode characters
function padTextToWidth(text, targetWidth) {
    const currentWidth = getVisualTextWidth(text);
    const spacesNeeded = Math.max(0, targetWidth - currentWidth);
    return text + ' '.repeat(spacesNeeded);
}

function formatPipeTable(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Check if text contains pipes (basic table detection)
    if (!selectedText.includes('|')) {
        showToast('Not a pipe table', 'warning');
        return;
    }

    try {
        // Split into lines
        const lines = selectedText.trim().split('\n');

        // Parse each line into columns (split by |, remove leading/trailing pipes)
        const rows = lines.map(line => {
            // Remove leading/trailing whitespace and pipes
            const trimmed = line.trim().replace(/^\||\|$/g, '');
            // Split by pipe and trim each cell
            return trimmed.split('|').map(cell => cell.trim());
        });

        // Calculate max width for each column (excluding separator rows)
        const colCount = Math.max(...rows.map(r => r.length));
        const colWidths = [];

        for (let col = 0; col < colCount; col++) {
            let maxWidth = 0;
            for (let row of rows) {
                if (row[col]) {
                    // Skip separator rows (all dashes) when calculating width
                    if (!/^-+$/.test(row[col])) {
                        maxWidth = Math.max(maxWidth, getVisualTextWidth(row[col]));
                    }
                }
            }
            colWidths[col] = maxWidth;
        }

        // Rebuild table with proper alignment
        const formatted = rows.map((row, rowIndex) => {
            const cells = row.map((cell, colIndex) => {
                const width = colWidths[colIndex] || 0;

                // Check if it's a separator row (all dashes)
                if (/^-+$/.test(cell)) {
                    return '-'.repeat(width);
                }

                // Pad cell to column width using Unicode-aware padding
                return padTextToWidth(cell, width);
            });

            // Join with pipes and add leading/trailing pipes
            return '| ' + cells.join(' | ') + ' |';
        });

        const formattedText = formatted.join('\n');

        // Replace the selected text
        const newText = input.value.substring(0, start) +
            formattedText +
            input.value.substring(end);

        input.value = newText;

        // Trigger change event to update cell
        const changeEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(changeEvent);

        // Select the result
        input.setSelectionRange(start, start + formattedText.length);
        input.focus();

        closeQuickFormatter();
        showToast('Table formatted', 'success');
    } catch (error) {
        console.error('Error formatting table:', error);
        showToast('Error formatting table', 'error');
    }
}

function changeTextCase(caseType, event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    let convertedText;
    switch (caseType) {
        case 'upper':
            convertedText = selectedText.toUpperCase();
            break;
        case 'lower':
            convertedText = selectedText.toLowerCase();
            break;
        case 'proper':
            // Proper case: capitalize first letter of each word
            convertedText = selectedText.toLowerCase().replace(/\b\w/g, char => char.toUpperCase());
            break;
        default:
            return;
    }

    // Replace the selected text
    const newText = input.value.substring(0, start) +
        convertedText +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Select the converted text
    input.setSelectionRange(start, start + convertedText.length);
    input.focus();

    closeQuickFormatter();
    const caseNames = { upper: 'UPPERCASE', lower: 'lowercase', proper: 'Proper Case' };
    showToast(`Converted to ${caseNames[caseType]}`, 'success');
}

function applySqrtFormat(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Insert the square root syntax: \(\sqrt{value}\)
    const newText = input.value.substring(0, start) +
        `\\(\\sqrt{${selectedText}}\\)` +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position after the inserted text
    const sqrtSyntax = `\\(\\sqrt{${selectedText}}\\)`;
    const newCursorPos = start + sqrtSyntax.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast('Square root applied', 'success');
}

function applyHatFormat(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('No text selected', 'warning');
        return;
    }

    // Smart parsing: detect if text contains fraction patterns
    // Pattern 1: Simple fraction a/b
    // Pattern 2: Complex fraction with parentheses: (a+b)/(c+d)
    // Pattern 3: Multiple operations: a*b/c or a/b*c
    // Pattern 4: Nested: 5555/(1550+10)/150

    let fracSyntax;

    // Check if it's a simple fraction pattern (no * outside parentheses)
    if (selectedText.includes('/')) {
        // Try to intelligently parse the fraction
        // Replace * with \cdot for multiplication in LaTeX
        let processed = selectedText;

        // Find the main division (last / that's not inside parentheses)
        let depth = 0;
        let mainDivIndex = -1;

        for (let i = selectedText.length - 1; i >= 0; i--) {
            if (selectedText[i] === ')') depth++;
            else if (selectedText[i] === '(') depth--;
            else if (selectedText[i] === '/' && depth === 0) {
                mainDivIndex = i;
                break;
            }
        }

        if (mainDivIndex !== -1) {
            // Split at the main division
            let numerator = selectedText.substring(0, mainDivIndex).trim();
            let denominator = selectedText.substring(mainDivIndex + 1).trim();

            // Replace * with \times (cross sign) in both parts
            numerator = numerator.replace(/\*/g, '\\times ');
            denominator = denominator.replace(/\*/g, '\\times ');

            fracSyntax = `\\(\\frac{${numerator}}{${denominator}}\\)`;
        } else {
            // No division found, just wrap it
            processed = processed.replace(/\*/g, '\\cdot ');
            fracSyntax = `\\(${processed}\\)`;
        }
    } else if (selectedText.includes('*')) {
        // Just multiplication, no division
        const processed = selectedText.replace(/\*/g, '\\times ');
        fracSyntax = `\\(${processed}\\)`;
    } else {
        // No special operators, just wrap it
        fracSyntax = `\\(${selectedText}\\)`;
    }

    const newText = input.value.substring(0, start) +
        fracSyntax +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event to update cell
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor position after the inserted text
    const newCursorPos = start + fracSyntax.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast('Math notation applied', 'success');
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
    const formatter = document.getElementById('quickFormatter');
    const isShowing = colorSection.style.display === 'none';

    colorSection.style.display = isShowing ? 'block' : 'none';

    // Add/remove class to shift formatter left
    if (isShowing) {
        formatter.classList.add('with-color-picker');
        loadColorSwatches();
    } else {
        formatter.classList.remove('with-color-picker');
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

    // Load color history
    loadColorHistory();
}

// Load and display color history (most used colors)
function loadColorHistory() {
    const historyContainer = document.getElementById('colorHistory');
    if (!historyContainer) return;

    historyContainer.innerHTML = '';

    // Load color usage history from localStorage
    const colorHistory = JSON.parse(localStorage.getItem('colorHistory') || '[]');

    // Sort by usage count (most used first)
    colorHistory.sort((a, b) => b.count - a.count);

    // Display top 10 most used colors
    const topColors = colorHistory.slice(0, 10);

    if (topColors.length === 0) {
        historyContainer.innerHTML = '<div style="padding: 8px; text-align: center; color: #999; font-size: 11px;">No history yet</div>';
        return;
    }

    topColors.forEach((item, index) => {
        const historyBtn = document.createElement('button');
        historyBtn.className = 'color-history-item';

        // Show visual indicator if noBg is set
        if (item.noBg) {
            historyBtn.style.background = 'transparent';
            historyBtn.style.border = '2px dashed #999';
        } else {
            historyBtn.style.background = item.bg;
        }
        historyBtn.style.color = item.fg;
        historyBtn.textContent = 'Aa';

        const bgText = item.noBg ? 'No BG' : item.bg;
        historyBtn.title = `Text: ${item.fg}, Background: ${bgText}\nUsed ${item.count} time${item.count > 1 ? 's' : ''}`;

        historyBtn.onclick = () => {
            document.getElementById('quickFgColor').value = item.fg;
            document.getElementById('quickBgColor').value = item.bg;
            document.getElementById('noBgCheckbox').checked = item.noBg || false;
        };

        // Add delete button that appears on hover
        const deleteBtn = document.createElement('span');
        deleteBtn.className = 'history-delete';
        deleteBtn.textContent = '×';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteColorHistory(index);
        };
        historyBtn.appendChild(deleteBtn);

        historyContainer.appendChild(historyBtn);
    });
}

function deleteColorHistory(index) {
    const colorHistory = JSON.parse(localStorage.getItem('colorHistory') || '[]');
    colorHistory.sort((a, b) => b.count - a.count);
    colorHistory.splice(index, 1);
    localStorage.setItem('colorHistory', JSON.stringify(colorHistory));
    loadColorHistory();
    showToast('Color removed from history', 'success');
}

function trackColorUsage(fg, bg, noBg) {
    const colorHistory = JSON.parse(localStorage.getItem('colorHistory') || '[]');

    // Find if this color combination already exists
    const existingIndex = colorHistory.findIndex(item =>
        item.fg === fg && item.bg === bg && item.noBg === noBg
    );

    if (existingIndex >= 0) {
        // Increment count
        colorHistory[existingIndex].count++;
    } else {
        // Add new entry
        colorHistory.push({ fg, bg, noBg, count: 1 });
    }

    localStorage.setItem('colorHistory', JSON.stringify(colorHistory));
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

    // Track color usage
    trackColorUsage(fgColor, bgColor, noBgCheckbox.checked);

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

    // Find match corresponding to current selection
    const currentStart = input.selectionStart;
    // Helper to see if a match is "close enough" or exactly matches current selection
    let initialMatchIndex = matches.findIndex(m => m.start === currentStart);
    if (initialMatchIndex === -1) {
        // If not exact match, find closest one or default to 0
        // For now, let's just pick the first one if exact match fails, 
        // to avoid logic breakage, though exact match should exist if selectNextOccurrence called it.
        initialMatchIndex = 0;
    }

    multiSelectionData = {
        input: input,
        searchText: searchText,
        matches: matches,
        currentIndex: initialMatchIndex,
        selectedMatches: [matches[initialMatchIndex]],
        listenerSetup: false
    };

    // Highlight initial match (redundant if already same)
    if (matches.length > 0) {
        showMultiSelectionIndicator(input, 1, matches.length);
    }

    // Don't set up listener yet - wait until user starts typing or selects next
}

function selectNextMatch(input) {
    if (!multiSelectionData || multiSelectionData.matches.length === 0) return;

    // Find next unselected match
    let nextIndex = -1;
    for (let i = 1; i < multiSelectionData.matches.length; i++) {
        const checkIdx = (multiSelectionData.currentIndex + i) % multiSelectionData.matches.length;
        const match = multiSelectionData.matches[checkIdx];
        if (!multiSelectionData.selectedMatches.includes(match)) {
            nextIndex = checkIdx;
            break;
        }
    }

    if (nextIndex !== -1) {
        multiSelectionData.currentIndex = nextIndex;
        const nextMatch = multiSelectionData.matches[nextIndex];
        multiSelectionData.selectedMatches.push(nextMatch);

        // Select the next match
        input.setSelectionRange(nextMatch.start, nextMatch.end);

        // Setup listener immediately if > 1 selected
        if (!multiSelectionData.listenerSetup) {
            setupMultiReplaceListener(input);
            multiSelectionData.listenerSetup = true;
        }
    } else {
        // All selected
        showToast(`All ${multiSelectionData.matches.length} occurrences selected.`, 'info');
        multiSelectionData.allSelected = true;
        if (!multiSelectionData.listenerSetup) {
            setupMultiReplaceListener(input);
            multiSelectionData.listenerSetup = true;
        }
    }

    showMultiSelectionIndicator(input, multiSelectionData.selectedMatches.length, multiSelectionData.matches.length);
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
    // Store the selected ranges for reference
    multiSelectionData.originalRanges = multiSelectionData.selectedMatches.map(m => ({
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

    // Sort SELECTED matches from right to left to apply edits without breaking indices
    const sortedSelected = [...multiSelectionData.selectedMatches].sort((a, b) => b.start - a.start);

    // Apply the edit to each SELECTED match
    for (const match of sortedSelected) {
        if (action === 'insert') {
            result = result.substring(0, match.start) + char + result.substring(match.end);
        } else if (action === 'backspace') {
            if (match.start === match.end) {
                if (match.start > 0) {
                    result = result.substring(0, match.start - 1) + result.substring(match.start);
                }
            } else {
                result = result.substring(0, match.start) + result.substring(match.end);
            }
        } else if (action === 'delete') {
            if (match.start === match.end) {
                if (match.end < result.length) {
                    result = result.substring(0, match.start) + result.substring(match.start + 1);
                }
            } else {
                result = result.substring(0, match.start) + result.substring(match.end);
            }
        }
    }

    input.value = result;
    multiSelectionData.currentText = result;

    // Recalculate match positions for ALL matches
    let offset = 0;
    const newMatches = [];
    const newSelectedMatches = [];

    for (let i = 0; i < multiSelectionData.matches.length; i++) {
        const oldMatch = multiSelectionData.matches[i];
        // Check if this match was one of the selected/edited ones
        // We use reference comparison or finding based on start/end if refs changed (they shouldn't have yet)
        const wasSelected = multiSelectionData.selectedMatches.includes(oldMatch);

        let newStart = oldMatch.start + offset;
        let newEnd = oldMatch.end + offset; // default if not edited
        let offsetChange = 0;

        if (wasSelected) {
            const oldLength = oldMatch.end - oldMatch.start;

            if (action === 'insert') {
                newEnd = newStart + char.length; // Replaced with char
                offsetChange = char.length - oldLength;
            } else if (action === 'backspace') {
                if (oldLength > 0) {
                    newEnd = newStart; // Deleted selection
                    offsetChange = -oldLength;
                } else {
                    newStart--; // Deleted char before
                    newEnd--;
                    offsetChange = -1;
                }
            } else if (action === 'delete') {
                if (oldLength > 0) {
                    newEnd = newStart; // Deleted selection
                    offsetChange = -oldLength;
                } else {
                    // Deleted char after, start/end stay same but text shifts left
                    offsetChange = -1;
                }
            }

            const newMatch = { start: newStart, end: newEnd };
            newMatches.push(newMatch);
            newSelectedMatches.push(newMatch);

            offset += offsetChange;
        } else {
            // Not selected, just shift
            newMatches.push({ start: newStart, end: newEnd });
        }
    }

    multiSelectionData.matches = newMatches;
    multiSelectionData.selectedMatches = newSelectedMatches;

    // Move cursor to the last selected match's new end
    if (newSelectedMatches.length > 0) {
        const lastSelected = newSelectedMatches[newSelectedMatches.length - 1];
        input.setSelectionRange(lastSelected.end, lastSelected.end);
    }

    showSelectionMarkers(input, newSelectedMatches);

    // Trigger change event
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);
}

function handleMultiSelectionExtension(input, key) {
    if (!multiSelectionData) return;

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
    const newMatches = [];
    const newSelectedMatches = [];

    for (let i = 0; i < multiSelectionData.matches.length; i++) {
        const match = multiSelectionData.matches[i];
        const isSelected = multiSelectionData.selectedMatches.includes(match);

        if (!isSelected) {
            newMatches.push(match);
            continue;
        }

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
            if (newEnd < text.length) newEnd++;
        } else if (key === 'ArrowLeft') {
            if (newStart > 0) newStart--;
        }

        const newMatch = { start: newStart, end: newEnd };
        newMatches.push(newMatch);
        newSelectedMatches.push(newMatch);
    }

    // Update the matches
    multiSelectionData.matches = newMatches;
    multiSelectionData.selectedMatches = newSelectedMatches;

    // Update search text to the new extended selection (use first match as reference)
    const firstMatch = newSelectedMatches[0];
    if (firstMatch) {
        multiSelectionData.searchText = text.substring(firstMatch.start, firstMatch.end);
    }
    multiSelectionData.originalText = text;
    multiSelectionData.replacementText = '';

    // Visually select the last match
    const lastMatch = newSelectedMatches[newSelectedMatches.length - 1];
    if (lastMatch) {
        input.setSelectionRange(lastMatch.start, lastMatch.end);
    }

    // Show visual markers for all selections
    showSelectionMarkers(input, newSelectedMatches);
    showMultiSelectionIndicator(input, newSelectedMatches.length, multiSelectionData.matches.length);
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

    uncategorizedItem.addEventListener('click', (e) => {
        selectF1Category(null);
    });

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

        // Add click handler
        item.addEventListener('click', (e) => {
            selectF1Category(category);
        });

        // Add right-click context menu for categories
        item.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showF1CategoryContextMenu(e, category);
        });

        categoryList.appendChild(item);
    });
}

// F1 Category Context Menu
function showF1CategoryContextMenu(event, categoryName) {
    const menu = document.getElementById('f1CategoryContextMenu');

    menu.innerHTML = `
        <div class="context-menu-item" onclick="showAddCategoryModal(); hideF1CategoryContextMenu();">
            <span>➕</span>
            <span>Add Category</span>
        </div>
        <div class="context-menu-item" onclick="renameF1Category('${categoryName}'); hideF1CategoryContextMenu();">
            <span>✏️</span>
            <span>Rename</span>
        </div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" onclick="deleteF1Category('${categoryName}'); hideF1CategoryContextMenu();">
            <span>🗑️</span>
            <span>Delete</span>
        </div>
    `;

    menu.classList.add('show');
    menu.style.position = 'fixed';
    menu.style.left = event.clientX + 'px';
    menu.style.top = event.clientY + 'px';
    menu.style.zIndex = '10000';

    // Close menu when clicking outside
    setTimeout(() => {
        document.addEventListener('click', hideF1CategoryContextMenu);
    }, 10);
}

function hideF1CategoryContextMenu() {
    const menu = document.getElementById('f1CategoryContextMenu');
    menu.classList.remove('show');
    document.removeEventListener('click', hideF1CategoryContextMenu);
}

function renameF1Category(categoryName) {
    // Set the current category and show rename modal
    currentCategory = categoryName;
    showRenameCategoryModal();
}

async function deleteF1Category(categoryName) {
    await deleteCategory(categoryName);
    populateF1Categories();
    populateF1Sheets();
}

// F1 Sheet Context Menu
function showF1SheetContextMenu(event, sheetIndex, isSubSheet) {
    const menu = document.getElementById('f1SheetContextMenu');
    const sheet = tableData.sheets[sheetIndex];

    if (isSubSheet) {
        // Sub-sheet menu: Rename, Delete
        menu.innerHTML = `
            <div class="context-menu-item" onclick="renameF1Sheet(${sheetIndex}); hideF1SheetContextMenu();">
                <span>✏️</span>
                <span>Rename</span>
            </div>
            <div class="context-menu-separator"></div>
            <div class="context-menu-item" onclick="deleteF1Sheet(${sheetIndex}); hideF1SheetContextMenu();">
                <span>🗑️</span>
                <span>Delete</span>
            </div>
        `;
    } else {
        // Parent sheet menu: Rename, Move to Category, Delete
        menu.innerHTML = `
            <div class="context-menu-item" onclick="renameF1Sheet(${sheetIndex}); hideF1SheetContextMenu();">
                <span>✏️</span>
                <span>Rename</span>
            </div>
            <div class="context-menu-item" onclick="moveF1SheetToCategory(${sheetIndex}); hideF1SheetContextMenu();">
                <span>📁</span>
                <span>Move to Category</span>
            </div>
            <div class="context-menu-separator"></div>
            <div class="context-menu-item" onclick="deleteF1Sheet(${sheetIndex}); hideF1SheetContextMenu();">
                <span>🗑️</span>
                <span>Delete</span>
            </div>
        `;
    }

    menu.classList.add('show');
    menu.style.position = 'fixed';
    menu.style.left = event.clientX + 'px';
    menu.style.top = event.clientY + 'px';
    menu.style.zIndex = '10000';

    // Close menu when clicking outside
    setTimeout(() => {
        document.addEventListener('click', hideF1SheetContextMenu);
    }, 10);
}

function hideF1SheetContextMenu() {
    const menu = document.getElementById('f1SheetContextMenu');
    menu.classList.remove('show');
    document.removeEventListener('click', hideF1SheetContextMenu);
}

function renameF1Sheet(sheetIndex) {
    // Switch to the sheet and show rename modal
    currentSheet = sheetIndex;
    renderTable();
    document.getElementById('sheetName').value = tableData.sheets[sheetIndex].name;
    document.getElementById('sheetNickname').value = tableData.sheets[sheetIndex].nickname || '';
    document.getElementById('renameModal').style.display = 'block';
}

function moveF1SheetToCategory(sheetIndex) {
    showMoveToCategoryModal(sheetIndex);
}

async function deleteF1Sheet(sheetIndex) {
    await deleteSheet(sheetIndex);
    populateF1Categories();
    populateF1Sheets();
}

async function addF1Sheet() {
    const sheetName = prompt('Enter sheet name:');
    if (!sheetName) return;

    const newSheet = {
        name: sheetName,
        columns: [],
        rows: [],
        cellStyles: {},
        mergedCells: {}
    };

    tableData.sheets.push(newSheet);
    const newIndex = tableData.sheets.length - 1;

    // Assign to current category if one is selected
    if (selectedF1Category) {
        initializeCategories();
        tableData.sheetCategories[newIndex] = selectedF1Category;
    }

    await saveData();
    renderSidebar();
    populateF1Categories();
    populateF1Sheets();
    showToast(`Sheet "${sheetName}" added`, 'success');
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
    renderSidebar();

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
    renderSidebar();

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
        // Skip sub-sheets in the main loop - they'll be rendered with their parents
        if (sheet.parentSheet !== undefined && sheet.parentSheet !== null) {
            return;
        }

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

        // Create container for parent and its sub-sheets
        const sheetGroup = document.createElement('div');
        sheetGroup.className = 'f1-sheet-group';

        // Create parent sheet item
        const item = document.createElement('div');
        item.className = 'f1-sheet-item f1-parent-sheet' + (index === currentSheet ? ' active' : '');
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

        // Add right-click context menu for parent sheets
        item.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showF1SheetContextMenu(e, index, false);
            return false;
        });

        sheetGroup.appendChild(item);

        // Find and add sub-sheets directly to the group
        // Only if showSubSheetsInF1 is true
        if (showSubSheetsInF1) {
            const subSheets = tableData.sheets
                .map((s, idx) => ({ sheet: s, index: idx }))
                .filter(({ sheet }) => sheet.parentSheet === index);

            subSheets.forEach(({ sheet: subSheet, index: subIndex }) => {
                const subItem = document.createElement('div');
                subItem.className = 'f1-sheet-item f1-sub-sheet' + (subIndex === currentSheet ? ' active' : '');
                subItem.dataset.sheetIndex = subIndex;

                const subNameSpan = document.createElement('span');
                subNameSpan.className = 'f1-sheet-name-wrapper';
                subNameSpan.innerHTML = `
                <span class="f1-sheet-icon">📃</span>
                <span class="f1-sheet-name">${subSheet.name}</span>
            `;

                subItem.appendChild(subNameSpan);

                // Enable dragging for sub-sheets
                subItem.draggable = true;

                subItem.addEventListener('dragstart', (e) => {
                    handleF1DragStart.call(subItem, e);
                });

                subItem.addEventListener('dragover', handleF1DragOver);
                subItem.addEventListener('drop', handleF1Drop);
                subItem.addEventListener('dragend', handleF1DragEnd);

                subItem.addEventListener('click', (e) => {
                    switchToSheetFromF1(subIndex);
                });

                // Add right-click context menu for sub-sheets
                subItem.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    showF1SheetContextMenu(e, subIndex, true);
                    return false;
                });

                sheetGroup.appendChild(subItem);
            });
        }

        sheetList.appendChild(sheetGroup);
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
    e.dataTransfer.setData('text/plain', this.dataset.sheetIndex);
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleF1DragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }

    const targetSheetIndex = parseInt(this.dataset.sheetIndex);

    // Safety check
    if (draggedSheetIndex === null || isNaN(targetSheetIndex)) return false;

    const draggedSheet = tableData.sheets[draggedSheetIndex];
    const targetSheet = tableData.sheets[targetSheetIndex];

    if (!draggedSheet || !targetSheet) return false;

    // Check constraints
    let canDrop = false;

    const isDraggedSubSheet = draggedSheet.parentSheet !== undefined && draggedSheet.parentSheet !== null;
    const isTargetSubSheet = targetSheet.parentSheet !== undefined && targetSheet.parentSheet !== null;

    if (!isDraggedSubSheet && !isTargetSubSheet) {
        // Parent -> Parent: Allow
        canDrop = true;
    } else if (isDraggedSubSheet && isTargetSubSheet) {
        // Sub-sheet -> Sub-sheet: Allow ONLY if same parent
        // Handle logic where parent index shifts are irrelevant because we just check values
        // Note: draggedSheet.parentSheet is an index.
        if (draggedSheet.parentSheet === targetSheet.parentSheet) {
            canDrop = true;
        }
    } else if (isDraggedSubSheet && !isTargetSubSheet) {
        // Sub-sheet -> Parent: Allow only if dropping on its own parent (reorder to top of sub-sheets?)
        // Actually, dropping on parent usually inserts BEFORE parent, which would make it a parent?
        // No, Drop logic is "Insert At".
        // If we want to strictly rearrange sub-sheets, only allow Sibling drops.
        if (draggedSheet.parentSheet === targetSheetIndex) {
            canDrop = true;
        }
    } else if (!isDraggedSubSheet && isTargetSubSheet) {
        // Parent -> Sub-sheet: Allow only if sub-sheet belongs to this parent
        if (targetSheet.parentSheet === draggedSheetIndex) {
            canDrop = true;
        }
    }

    if (canDrop) {
        e.dataTransfer.dropEffect = 'move';
        // Add visual indicator
        if (this !== draggedF1Item && this.classList.contains('f1-sheet-item')) {
            this.style.borderColor = '#007bff';
            this.style.borderWidth = '3px';
        }
    } else {
        e.dataTransfer.dropEffect = 'none';
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

        // Update parentSheet references after removal
        tableData.sheets.forEach((sheet, idx) => {
            if (sheet.parentSheet !== undefined && sheet.parentSheet !== null) {
                if (sheet.parentSheet === draggedSheetIndex) {
                    // This sub-sheet's parent was moved, update later
                    sheet.parentSheet = -1; // Temporary marker
                } else if (sheet.parentSheet > draggedSheetIndex) {
                    // Parent was after the moved sheet, shift down
                    sheet.parentSheet--;
                }
            }
        });

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

        // Update parentSheet references after insertion
        tableData.sheets.forEach((sheet, idx) => {
            if (sheet.parentSheet !== undefined && sheet.parentSheet !== null) {
                if (sheet.parentSheet === -1) {
                    // This sub-sheet's parent was moved, update to new position
                    sheet.parentSheet = targetIndex;
                } else if (sheet.parentSheet >= targetIndex && idx !== targetIndex) {
                    // Parent was at or after target, shift up
                    sheet.parentSheet++;
                }
            }
        });

        // Update separators to maintain their relative positions
        if (!tableData.sheetSeparators) tableData.sheetSeparators = {};
        const newSeparators = {};
        Object.keys(tableData.sheetSeparators).forEach(key => {
            const parts = key.split('_');
            const cat = parts.slice(0, -1).join('_');
            const idx = parseInt(parts[parts.length - 1]);

            let newIdx = idx;
            // Shifting logic identical to how sheet indices themselves shift
            if (idx > draggedSheetIndex) {
                newIdx--;
            }
            if (newIdx > targetIndex) {
                newIdx++;
            }

            newSeparators[`${cat}_${newIdx}`] = true;
        });
        tableData.sheetSeparators = newSeparators;

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
        renderSidebar();
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

// F1 search mode: '' (normal), '*' (all sheets), '#' (content search)
let f1SearchMode = localStorage.getItem('f1SearchMode') || '';

function toggleF1SearchMode() {
    const modeIcon = document.getElementById('f1SearchModeIcon');
    const toggle = document.getElementById('f1SearchModeToggle');

    // Cycle through modes: '' -> '*' -> '#' -> ''
    if (f1SearchMode === '') {
        f1SearchMode = '*';
        modeIcon.textContent = '*';
        toggle.style.color = '#00ff9d';
        toggle.title = 'Search all sheets';
    } else if (f1SearchMode === '*') {
        f1SearchMode = '#';
        modeIcon.textContent = '#';
        toggle.style.color = '#00f3ff';
        toggle.title = 'Search sheet content';
    } else {
        f1SearchMode = '';
        modeIcon.textContent = '🔍';
        toggle.style.color = '';
        toggle.title = 'Normal search';
    }

    // Save to localStorage
    localStorage.setItem('f1SearchMode', f1SearchMode);

    // Re-filter with new mode
    filterF1Sheets();
}

function filterF1Sheets() {
    const searchInput = document.getElementById('f1SearchInput');
    let searchTerm = searchInput ? searchInput.value.trim() : '';

    // Prepend the search mode prefix if mode is active
    if (f1SearchMode && searchTerm) {
        searchTerm = f1SearchMode + searchTerm;
    } else if (f1SearchMode && !searchTerm) {
        // If mode is active but no search term, show normal sheets
        searchTerm = '';
    }

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
                const categoryLabel = sheetCategory ? ` <span style="color: #00ff9d; font-size: 11px; opacity: 0.7;">[${sheetCategory}]</span>` : '';

                const item = document.createElement('div');
                item.className = 'f1-sheet-item f1-parent-sheet' + (index === currentSheet ? ' active' : '');
                item.dataset.sheetIndex = index;
                item.innerHTML = `
                    <div class="f1-sheet-name-wrapper">
                        <span class="f1-sheet-icon">🔍</span>
                        <span class="f1-sheet-name">${sheet.name}${categoryLabel}</span>
                    </div>
                `;
                item.onclick = () => switchToSheetFromF1(index);
                sheetList.appendChild(item);
            });
        } else {
            const emptyMsg = document.createElement('div');
            emptyMsg.style.padding = '20px';
            emptyMsg.style.textAlign = 'center';
            emptyMsg.style.color = '#666';
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

    // Clear existing heights to measure natural scrollHeight
    input.style.minHeight = '';
    preview.style.minHeight = '';
    if (input.tagName === 'TEXTAREA') input.style.height = 'auto';
    preview.style.height = 'auto';

    input.style.display = 'block';
    preview.style.display = 'block';

    // Force a reflow to ensure accurate scrollHeight measurement
    void input.offsetHeight;
    void preview.offsetHeight;

    // Measure heights
    const inputHeight = input.scrollHeight;
    const previewHeight = preview.scrollHeight;

    // Use the larger height with a healthy buffer (20px) to prevent cutoff
    // especially for KaTeX and complex formatting
    const maxHeight = Math.ceil(Math.max(inputHeight, previewHeight)) + 20;

    // Apply to both height and minHeight to ensure stability
    if (input.tagName === 'TEXTAREA') {
        input.style.height = maxHeight + 'px';
    }
    input.style.minHeight = maxHeight + 'px';
    preview.style.height = maxHeight + 'px';
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
    }, 300);
};

// Add resize listener to handle window scaling
window.addEventListener('resize', () => {
    adjustAllMarkdownCells();
});

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

    // Use the stripMarkdown function to remove all formatting, but preserve links
    const cleanText = stripMarkdown(selectedText, true);

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
    const formatter = document.getElementById('quickFormatter');
    const isShowing = colorSection.style.display === 'none';

    colorSection.style.display = isShowing ? 'block' : 'none';

    // Add/remove class to shift formatter left
    if (isShowing) {
        formatter.classList.add('with-color-picker');
        loadColorSwatches();
    } else {
        formatter.classList.remove('with-color-picker');
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

// Sub-Sheet Bar Logic
function renderSubSheetBar() {
    const subsheetTabs = document.getElementById('subsheetTabs');
    if (!subsheetTabs) return;

    subsheetTabs.innerHTML = '';

    // Get current sheet's parent (if it's a sub-sheet) or use current sheet as parent
    const currentSheetData = tableData.sheets[currentSheet];
    const parentIndex = currentSheetData?.parentSheet !== undefined ?
        currentSheetData.parentSheet : currentSheet;
    const parentSheet = tableData.sheets[parentIndex];

    if (!parentSheet) return;

    // Create parent tab
    const parentTab = document.createElement('div');
    parentTab.className = `subsheet-tab ${currentSheet === parentIndex ? 'active' : ''}`;
    parentTab.dataset.sheetIndex = parentIndex;

    const parentName = document.createElement('span');
    parentName.className = 'subsheet-tab-name';
    parentName.textContent = parentSheet.name;
    parentTab.appendChild(parentName);
    parentTab.onclick = () => switchSheet(parentIndex);

    subsheetTabs.appendChild(parentTab);

    // Find and render all sub-sheets
    tableData.sheets.forEach((sheet, index) => {
        if (sheet.parentSheet === parentIndex) {
            const tab = document.createElement('div');
            tab.className = `subsheet-tab ${currentSheet === index ? 'active' : ''}`;
            tab.dataset.sheetIndex = index;

            const name = document.createElement('span');
            name.className = 'subsheet-tab-name';
            name.textContent = sheet.name;

            tab.appendChild(name);
            tab.onclick = () => switchSheet(index);

            // Add right-click context menu for sub-sheet
            tab.oncontextmenu = (e) => {
                e.preventDefault();
                showSubSheetContextMenu(e, index);
            };

            subsheetTabs.appendChild(tab);
        }
    });

    // Add "+" button to add new sub-sheet
    const addBtn = document.createElement('button');
    addBtn.className = 'subsheet-add-btn';
    addBtn.innerHTML = '+';
    addBtn.title = 'Add sub-sheet';
    addBtn.onclick = () => addSubSheet(parentIndex);

    subsheetTabs.appendChild(addBtn);
}

function showSubSheetContextMenu(event, sheetIndex) {
    // Remove any existing context menu
    const existingMenu = document.getElementById('subsheetContextMenu');
    if (existingMenu) {
        existingMenu.remove();
    }

    const menu = document.createElement('div');
    menu.id = 'subsheetContextMenu';
    menu.className = 'subsheet-context-menu';
    menu.style.position = 'fixed';
    menu.style.left = event.pageX + 'px';
    menu.style.top = event.pageY + 'px';

    const renameItem = document.createElement('div');
    renameItem.className = 'context-menu-item';
    renameItem.innerHTML = '<span>✏️</span><span>Rename</span>';
    renameItem.onclick = () => {
        menu.remove();
        showRenameModal(sheetIndex);
    };

    const deleteItem = document.createElement('div');
    deleteItem.className = 'context-menu-item';
    deleteItem.innerHTML = '<span>🗑️</span><span>Delete</span>';
    deleteItem.onclick = () => {
        menu.remove();
        deleteSheet(sheetIndex);
    };

    menu.appendChild(renameItem);
    menu.appendChild(deleteItem);
    document.body.appendChild(menu);

    // Close menu on click outside
    const closeMenu = (e) => {
        if (!menu.contains(e.target)) {
            menu.remove();
            document.removeEventListener('click', closeMenu);
        }
    };
    setTimeout(() => document.addEventListener('click', closeMenu), 0);
}

// Sidebar Logic
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
}

function renderSidebar() {
    const treeContainer = document.getElementById('sidebarTree');
    if (!treeContainer) return;

    treeContainer.innerHTML = '';

    // Group sheets by category
    const categoryMap = {};

    // Initialize categories
    if (tableData.categories) {
        tableData.categories.forEach(cat => {
            categoryMap[cat] = [];
        });
    }
    // Ensure Uncategorized exists
    if (!categoryMap['Uncategorized']) {
        categoryMap['Uncategorized'] = [];
    }

    // Distribute sheets
    tableData.sheets.forEach((sheet, index) => {
        // Skip sub-sheets (they are shown under parents in the main view, 
        // but for the tree, maybe we should show them? 
        // The user said "more like tree", so maybe nested?
        // But the current app has a specific sub-sheet bar. 
        // For now, let's list all top-level sheets in the tree.
        // If a sheet is a sub-sheet (has parentSheet), maybe we hide it from the top level?
        // The developer guide says: "Sub-sheets are hidden from the F1 reorder window - only parent sheets are shown"
        // So I should probably only show parent sheets in the tree, or show them nested.
        // Let's show them nested if possible, or just list parents for now to match existing logic.

        if (sheet.parentSheet !== undefined && sheet.parentSheet !== null) {
            return; // Skip sub-sheets for now, or handle them later
        }

        const catName = tableData.sheetCategories[index] || 'Uncategorized';
        if (!categoryMap[catName]) categoryMap[catName] = [];
        categoryMap[catName].push({ ...sheet, originalIndex: index });
    });

    // Render Categories
    Object.keys(categoryMap).forEach(catName => {
        const sheets = categoryMap[catName];

        const catDiv = document.createElement('div');
        catDiv.className = 'tree-category collapsed'; // Start collapsed

        const header = document.createElement('div');
        header.className = 'tree-category-header tree-item';
        header.onclick = (e) => {
            // Toggle collapse and icon
            catDiv.classList.toggle('collapsed');
            const icon = header.querySelector('.tree-icon');
            icon.textContent = catDiv.classList.contains('collapsed') ? '📁' : '📂';
        };
        header.oncontextmenu = (e) => showTreeContextMenu(e, 'category', catName);

        header.innerHTML = `
            <span class="tree-icon">📁</span>
            <span class="tree-label">${catName}</span>
        `;

        const content = document.createElement('div');
        content.className = 'tree-category-content';

        sheets.forEach((sheet, idx) => {
            const isLast = idx === sheets.length - 1;
            const sheetDiv = document.createElement('div');
            sheetDiv.className = `tree-sheet tree-item ${sheet.originalIndex === currentSheet ? 'active' : ''} ${isLast ? 'last' : ''}`;
            sheetDiv.onclick = () => {
                switchSheet(sheet.originalIndex);
                toggleSidebar();
            };
            sheetDiv.oncontextmenu = (e) => showTreeContextMenu(e, 'sheet', sheet.originalIndex);

            sheetDiv.innerHTML = `
                <span class="tree-icon">📄</span>
                <span class="tree-label">${sheet.name}</span>
            `;
            content.appendChild(sheetDiv);
        });

        catDiv.appendChild(header);
        catDiv.appendChild(content);
        treeContainer.appendChild(catDiv);
    });

    // Update Header Info
    const currentSheetObj = tableData.sheets[currentSheet];
    if (currentSheetObj) {
        document.getElementById('currentSheetTitle').textContent = currentSheetObj.name;
        const currentCat = tableData.sheetCategories[currentSheet] || 'Uncategorized';
        document.getElementById('currentCategoryTitle').textContent = currentCat;
    }

    // Update sub-sheet bar
    renderSubSheetBar();
}

// Context Menu
function showTreeContextMenu(e, type, id) {
    e.preventDefault();
    const menu = document.getElementById('treeContextMenu');
    menu.innerHTML = '';

    if (type === 'category') {
        menu.innerHTML = `
            <div class="context-menu-item" onclick="showAddSheetToCategory('${id}')">
                <span>📄</span> Add Sheet Here
            </div>
            <div class="context-menu-item" onclick="showRenameCategoryModal('${id}')">
                <span>✏️</span> Rename
            </div>
            <div class="context-menu-item danger" onclick="deleteCategory('${id}')">
                <span>🗑️</span> Delete
            </div>
        `;
    } else if (type === 'sheet') {
        menu.innerHTML = `
            <div class="context-menu-item" onclick="showRenameModal(${id})">
                <span>✏️</span> Rename
            </div>
            <div class="context-menu-item" onclick="showMoveToCategoryModal(${id})">
                <span>📁</span> Move to Category
            </div>
            <div class="context-menu-item danger" onclick="deleteSheet(${id})">
                <span>🗑️</span> Delete
            </div>
        `;
    }

    // Position and show
    menu.style.display = 'block';
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';

    // Close on click outside
    const closeMenu = () => {
        menu.style.display = 'none';
        document.removeEventListener('click', closeMenu);
    };
    setTimeout(() => document.addEventListener('click', closeMenu), 0);
}

// Helper to add sheet to specific category
async function showAddSheetToCategory(category) {
    // Call existing addSheet but then move it? 
    // Or create a new API endpoint?
    // For now, add sheet then move it.

    // We can't use addSheet() directly because it prompts and uses currentCategory.
    // We need a custom logic here.

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
            const newIndex = result.sheetIndex;
            currentSheet = newIndex;

            // Assign to category
            if (category !== 'Uncategorized') {
                initializeCategories();
                tableData.sheetCategories[newIndex] = category;
                await saveData();
                showToast(`Sheet added to "${category}" category`, 'success');
            } else {
                // Explicitly set to Uncategorized (remove from map if exists, though it shouldn't)
                delete tableData.sheetCategories[newIndex];
                await saveData();
            }

            renderSidebar();
            renderTable();
        }
    } catch (error) {
        console.error('Error adding sheet:', error);
    }
}

async function deleteCategory(categoryName) {
    if (categoryName === 'Uncategorized') {
        alert('Cannot delete the Uncategorized category.');
        return;
    }

    if (!confirm(`Delete category "${categoryName}"? Sheets in this category will be moved to Uncategorized.`)) {
        return;
    }

    // Remove category from list
    const index = tableData.categories.indexOf(categoryName);
    if (index > -1) {
        tableData.categories.splice(index, 1);
    }

    // Move sheets to Uncategorized
    Object.keys(tableData.sheetCategories).forEach(key => {
        if (tableData.sheetCategories[key] === categoryName) {
            delete tableData.sheetCategories[key];
        }
    });

    await saveData();
    renderSidebar();
    showToast('Category deleted', 'success');
}


// ==================== CUSTOM COLOR SYNTAX ====================

// Load custom color syntaxes from JSON file
let customColorSyntaxes = [];

async function loadCustomColorSyntaxes() {
    try {
        const response = await fetch('/api/custom-syntaxes');
        if (response.ok) {
            customColorSyntaxes = await response.json();
            renderCustomSyntaxButtons(); // Render buttons after loading
        }
    } catch (e) {
        console.log('Could not load custom syntaxes:', e);
        customColorSyntaxes = [];
    }
}

function renderCustomSyntaxButtons() {
    const colorPickerBtn = document.getElementById('customColorPickerBtn');
    if (!colorPickerBtn) return;

    // Remove any existing custom syntax buttons
    const existingButtons = document.querySelectorAll('.format-btn.custom-syntax-btn');
    existingButtons.forEach(btn => btn.remove());

    // Insert custom syntax buttons before the color picker button
    customColorSyntaxes.forEach((syntax) => {
        if (!syntax.marker) return;

        const button = document.createElement('button');
        button.className = 'format-btn custom-syntax-btn';
        button.onclick = (event) => applyQuickFormat(syntax.marker, syntax.marker, event);
        button.oncontextmenu = (event) => toggleFormatSelection(syntax.marker, syntax.marker, event);
        button.title = `${syntax.marker}text${syntax.marker} (Right-click to select)`;
        button.style.background = syntax.bgColor;
        button.style.color = syntax.fgColor;
        button.style.fontSize = '12px';
        button.style.fontWeight = '600';
        button.textContent = syntax.marker;

        // Insert before the color picker button
        colorPickerBtn.parentNode.insertBefore(button, colorPickerBtn);
    });
}

async function saveCustomColorSyntaxes() {
    try {
        await fetch('/api/custom-syntaxes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(customColorSyntaxes)
        });
    } catch (e) {
        console.log('Could not save custom syntaxes:', e);
    }
}

function renderCustomColorSyntaxList() {
    const list = document.getElementById('customColorSyntaxList');
    if (!list) return;

    list.innerHTML = '';

    if (customColorSyntaxes.length === 0) {
        list.innerHTML = '<p style="color: #6c757d; font-size: 13px; text-align: center; padding: 20px;">No custom syntaxes added yet. Click "Add Custom Syntax" to create one.</p>';
        return;
    }

    customColorSyntaxes.forEach((syntax, index) => {
        const item = document.createElement('div');
        item.className = 'custom-syntax-item';

        item.innerHTML = `
            <div class="custom-syntax-input-group">
                <input type="text" value="${syntax.marker}" 
                    onchange="updateCustomSyntax(${index}, 'marker', this.value)" 
                    placeholder="++, $$"
                    maxlength="4">
            </div>
            <div class="custom-syntax-input-group">
                <label>BG:</label>
                <button onclick="showCustomSyntaxColorPicker(${index}, 'bgColor', event)" 
                    style="width: 32px; height: 28px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: ${syntax.bgColor};"
                    title="Background Color"></button>
            </div>
            <div class="custom-syntax-input-group">
                <label>FG:</label>
                <button onclick="showCustomSyntaxColorPicker(${index}, 'fgColor', event)" 
                    style="width: 32px; height: 28px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: ${syntax.fgColor};"
                    title="Text Color"></button>
            </div>
            <div class="custom-syntax-preview" style="background: ${syntax.bgColor}; color: ${syntax.fgColor};">
                ${syntax.marker}text${syntax.marker}
            </div>
            <button class="btn-remove-syntax" onclick="removeCustomSyntax(${index})">
                🗑️
            </button>
        `;

        list.appendChild(item);
    });

    // Also update the Quick Highlights section in F3 formatter
    renderCustomSyntaxButtons();
}



function addCustomColorSyntax() {
    customColorSyntaxes.push({
        marker: '++',
        bgColor: '#ff00ff',
        fgColor: '#ffffff'
    });
    saveCustomColorSyntaxes();
    renderCustomColorSyntaxList();
    renderTable(); // Re-render to apply new syntax
}

function updateCustomSyntax(index, field, value) {
    if (customColorSyntaxes[index]) {
        customColorSyntaxes[index][field] = value;
        saveCustomColorSyntaxes();
        renderCustomColorSyntaxList();
        renderTable(); // Re-render to apply changes
    }
}

function removeCustomSyntax(index) {
    if (confirm('Remove this custom syntax?')) {
        customColorSyntaxes.splice(index, 1);
        saveCustomColorSyntaxes();
        renderCustomColorSyntaxList();
        renderTable(); // Re-render to remove syntax
    }
}

function showCustomSyntaxColorPicker(index, field, event) {
    event.stopPropagation();

    let selectedBgColor = customColorSyntaxes[index].bgColor || '#ffffff';
    let selectedFgColor = customColorSyntaxes[index].fgColor || '#000000';
    let currentColorType = field === 'bgColor' ? 'background' : 'text';

    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'color-picker-overlay';
    overlay.id = 'customSyntaxColorPickerOverlay';

    // Create popup
    const popup = document.createElement('div');
    popup.className = 'color-picker-popup';
    popup.id = 'customSyntaxColorPickerPopup';

    const title = document.createElement('h3');
    title.textContent = `Custom Syntax Colors`;
    popup.appendChild(title);

    // Radio buttons for BG/FG selection
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
    bgRadioLabel.innerHTML = `<input type="radio" name="syntaxColorType" value="background" ${currentColorType === 'background' ? 'checked' : ''}> Background`;

    const fgRadioLabel = document.createElement('label');
    fgRadioLabel.style.display = 'flex';
    fgRadioLabel.style.alignItems = 'center';
    fgRadioLabel.style.gap = '5px';
    fgRadioLabel.style.cursor = 'pointer';
    fgRadioLabel.innerHTML = `<input type="radio" name="syntaxColorType" value="text" ${currentColorType === 'text' ? 'checked' : ''}> Text`;

    radioContainer.appendChild(bgRadioLabel);
    radioContainer.appendChild(fgRadioLabel);
    popup.appendChild(radioContainer);

    // Preview area
    const previewContainer = document.createElement('div');
    previewContainer.className = 'color-preview';
    previewContainer.style.margin = '15px 0';
    previewContainer.style.padding = '15px';
    previewContainer.style.borderRadius = '6px';
    previewContainer.style.border = '1px solid #ddd';
    previewContainer.style.backgroundColor = selectedBgColor;
    previewContainer.style.color = selectedFgColor;
    previewContainer.style.fontWeight = 'bold';
    previewContainer.style.textAlign = 'center';
    previewContainer.style.fontFamily = 'monospace';
    previewContainer.textContent = `${customColorSyntaxes[index].marker}text${customColorSyntaxes[index].marker}`;
    previewContainer.id = 'syntaxColorPreviewArea';
    popup.appendChild(previewContainer);

    // Transparent checkbox
    const transparentContainer = document.createElement('div');
    transparentContainer.style.marginBottom = '15px';
    transparentContainer.style.textAlign = 'center';

    const transparentLabel = document.createElement('label');
    transparentLabel.style.display = 'inline-flex';
    transparentLabel.style.alignItems = 'center';
    transparentLabel.style.gap = '8px';
    transparentLabel.style.cursor = 'pointer';
    transparentLabel.innerHTML = '<input type="checkbox" id="syntaxTransparentCheck"> Transparent';

    transparentContainer.appendChild(transparentLabel);
    popup.appendChild(transparentContainer);

    // Preset colors (exact same as cell color picker)
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

    const colorGrid = document.createElement('div');
    colorGrid.className = 'color-picker-grid';

    presetColors.forEach(color => {
        const colorSwatch = document.createElement('div');
        colorSwatch.className = 'color-swatch';
        colorSwatch.style.backgroundColor = color;
        colorSwatch.title = color;
        colorSwatch.onclick = () => {
            const bgRadio = popup.querySelector('input[name="syntaxColorType"][value="background"]');
            const transparentCheck = popup.querySelector('#syntaxTransparentCheck');

            if (bgRadio && bgRadio.checked) {
                selectedBgColor = color;
                transparentCheck.checked = false;
            } else {
                selectedFgColor = color;
            }

            updatePreview();
        };
        colorGrid.appendChild(colorSwatch);
    });

    popup.appendChild(colorGrid);

    // Update preview function
    function updatePreview() {
        const preview = popup.querySelector('#syntaxColorPreviewArea');
        const transparentCheck = popup.querySelector('#syntaxTransparentCheck');
        const bgRadio = popup.querySelector('input[name="syntaxColorType"][value="background"]');

        if (bgRadio && bgRadio.checked && transparentCheck && transparentCheck.checked) {
            preview.style.backgroundColor = 'transparent';
            preview.style.backgroundImage = 'linear-gradient(45deg, #ccc 25%, transparent 25%, transparent 75%, #ccc 75%, #ccc), linear-gradient(45deg, #ccc 25%, white 25%, white 75%, #ccc 75%, #ccc)';
            preview.style.backgroundSize = '10px 10px';
            preview.style.backgroundPosition = '0 0, 5px 5px';
        } else {
            preview.style.backgroundColor = selectedBgColor;
            preview.style.backgroundImage = 'none';
        }
        preview.style.color = selectedFgColor;
    }

    // Radio change listeners
    bgRadioLabel.querySelector('input').addEventListener('change', updatePreview);
    fgRadioLabel.querySelector('input').addEventListener('change', updatePreview);

    // Transparent checkbox listener
    transparentLabel.querySelector('input').addEventListener('change', (e) => {
        if (e.target.checked) {
            selectedBgColor = 'transparent';
        } else {
            selectedBgColor = '#ffffff';
        }
        updatePreview();
    });

    // Set initial transparent state
    if (selectedBgColor === 'transparent') {
        transparentLabel.querySelector('input').checked = true;
        updatePreview();
    }

    // OK button
    const okBtn = document.createElement('button');
    okBtn.className = 'btn btn-primary';
    okBtn.textContent = 'OK';
    okBtn.style.marginTop = '15px';
    okBtn.style.width = '100%';
    okBtn.onclick = () => {
        updateCustomSyntax(index, 'bgColor', selectedBgColor);
        updateCustomSyntax(index, 'fgColor', selectedFgColor);
        document.body.removeChild(overlay);
    };
    popup.appendChild(okBtn);

    // Close on overlay click
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    };

    // Append popup inside overlay, then overlay to body
    overlay.appendChild(popup);
    document.body.appendChild(overlay);
}

// Apply custom color syntaxes in parsing
function applyCustomColorSyntaxes(text) {
    let formatted = text;

    customColorSyntaxes.forEach(syntax => {
        if (!syntax.marker) return;

        // Escape special regex characters
        const escapedMarker = syntax.marker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`${escapedMarker}(.+?)${escapedMarker}`, 'g');

        formatted = formatted.replace(regex, (match, content) => {
            return `<span style="background: ${syntax.bgColor}; color: ${syntax.fgColor}; padding: 1px 4px; border-radius: 3px; display: inline; vertical-align: baseline; line-height: 1.3; box-decoration-break: clone; -webkit-box-decoration-break: clone;">${content}</span>`;
        });
    });

    return formatted;
}

// Initialize on page load
(async function () {
    await loadCustomColorSyntaxes();
    // Render custom syntax buttons in F3 formatter
    renderCustomSyntaxButtons();
    // Re-render table after syntaxes are loaded
    if (typeof renderTable === 'function') {
        renderTable();
    }
})();


// ==================== SETTINGS MODAL ====================

function openSettings() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.style.display = 'block';

        // Load current grid line color
        const currentColor = getGridLineColor();
        document.getElementById('gridLineColor').value = currentColor;
        document.getElementById('gridLineColorText').value = currentColor.substring(1).toUpperCase();

        renderCustomColorSyntaxList();
    }
}

function closeSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function toggleVrindaFont(enabled) {
    const table = document.getElementById('dataTable');
    if (enabled) {
        table.classList.remove('disable-vrinda');
    } else {
        table.classList.add('disable-vrinda');
    }
    localStorage.setItem('vrindaFontEnabled', enabled);
}



function showMarkdownGuide() {
    const modal = document.getElementById('markdownGuideModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeMarkdownGuide() {
    const modal = document.getElementById('markdownGuideModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modals when clicking outside
window.onclick = function (event) {
    const settingsModal = document.getElementById('settingsModal');
    const markdownModal = document.getElementById('markdownGuideModal');

    if (event.target === settingsModal) {
        closeSettingsModal();
    }
    if (event.target === markdownModal) {
        closeMarkdownGuide();
    }
};


// Variable Font Size Quick Format Function
function applyVariableFontSize(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('Please select text first', 'error');
        return;
    }

    // Prompt for font size
    const size = prompt('Enter font size multiplier (e.g., 2 for 2x, 1.5 for 1.5x, 0.8 for smaller):', '2');

    if (size === null) return; // User cancelled

    const sizeNum = parseFloat(size);
    if (isNaN(sizeNum) || sizeNum <= 0) {
        showToast('Invalid size. Please enter a positive number.', 'error');
        return;
    }

    // Apply the variable font size syntax
    const newText = input.value.substring(0, start) +
        `#${sizeNum}#${selectedText}#/#` +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor after the formatted text
    const newCursorPos = start + `#${sizeNum}#${selectedText}#/#`.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast(`Font size ${sizeNum}x applied`, 'success');
}


// Border Box Quick Format Function
function applyBorderBox(event) {
    if (!quickFormatterTarget) return;

    const input = quickFormatterTarget;
    const start = quickFormatterSelection.start;
    const end = quickFormatterSelection.end;
    const selectedText = input.value.substring(start, end);

    if (!selectedText) {
        showToast('Please select text first', 'error');
        return;
    }

    // Prompt for color
    const colorOptions = 'R (Red), G (Green), B (Blue), Y (Yellow), O (Orange), P (Purple), C (Cyan), W (White), K (Black), GR (Gray)';
    const color = prompt(`Enter border color:\n${colorOptions}`, 'R');

    if (color === null) return; // User cancelled

    const colorUpper = color.trim().toUpperCase();
    const validColors = ['R', 'G', 'B', 'Y', 'O', 'P', 'C', 'W', 'K', 'GR'];

    if (!validColors.includes(colorUpper)) {
        showToast('Invalid color. Use: R, G, B, Y, O, P, C, W, K, or GR', 'error');
        return;
    }

    // Apply the border box syntax
    const newText = input.value.substring(0, start) +
        `#${colorUpper}#${selectedText}#/#` +
        input.value.substring(end);

    input.value = newText;

    // Trigger change event
    const changeEvent = new Event('input', { bubbles: true });
    input.dispatchEvent(changeEvent);

    // Set cursor after the formatted text
    const newCursorPos = start + `#${colorUpper}#${selectedText}#/#`.length;
    input.setSelectionRange(newCursorPos, newCursorPos);
    input.focus();

    closeQuickFormatter();
    showToast(`${colorUpper} border applied`, 'success');
}

// ==========================================
// PDF EXPORT FEATURE
// ==========================================

function exportCellToPDF() {
    if (!contextMenuCell) return;

    // Close context menu
    const menu = document.getElementById('cellContextMenu');
    if (menu) menu.classList.remove('show');

    const { rowIndex, colIndex, inputElement, tdElement } = contextMenuCell;
    const sheet = tableData.sheets[currentSheet];
    const columnName = sheet.columns[colIndex]?.name || getExcelColumnName(colIndex);
    const sheetName = sheet.name || 'Sheet';

    // Prompt for filename
    const defaultFilename = `${sheetName}_${columnName}_Row${rowIndex + 1}.pdf`;
    const filename = prompt('Enter filename for PDF:', defaultFilename);
    if (!filename) return;

    showToast('Generating PDF...', 'info');

    // Create temporary container for rendering
    const tempContainer = createTempContainer();

    // Add header
    addPDFHeader(tempContainer, sheetName, columnName, rowIndex, colIndex);

    // Extract and style content
    const contentContainer = extractCellContent(tdElement, rowIndex, colIndex);
    tempContainer.appendChild(contentContainer);

    // Add footer
    addPDFFooter(tempContainer);

    // Capture and generate PDF
    captureAndGeneratePDF(tempContainer, filename);
}

function createTempContainer() {
    const container = document.createElement('div');
    container.id = 'pdf-export-container';
    container.style.position = 'fixed'; // Fixed to ensure it renders even if scrolled
    container.style.left = '-9999px'; // Move off-screen
    container.style.top = '0';
    container.style.width = '800px'; // A4 width approx
    container.style.minHeight = '100px';
    container.style.backgroundColor = 'white';
    container.style.padding = '20px';
    container.style.fontFamily = getComputedStyle(document.body).fontFamily;
    container.style.boxSizing = 'border-box';
    container.style.zIndex = '-1'; // Behind everything
    document.body.appendChild(container); // Must be in DOM to be rendered
    return container;
}

function addPDFHeader(container, sheetName, columnName, rowIndex, colIndex) {
    const header = document.createElement('div');
    header.style.marginBottom = '20px';
    header.style.borderBottom = '2px solid #333';
    header.style.paddingBottom = '10px';
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'flex-end';

    const titleDiv = document.createElement('div');
    titleDiv.innerHTML = `<h2 style="margin:0; font-size: 24px; color: #333;">${sheetName}</h2>`;

    const metaDiv = document.createElement('div');
    metaDiv.style.textAlign = 'right';
    metaDiv.style.fontSize = '12px';
    metaDiv.style.color = '#666';
    metaDiv.innerHTML = `
        <div>Column: <strong>${columnName}</strong></div>
        <div>Row: <strong>${rowIndex + 1}</strong></div>
        <div>Date: ${new Date().toLocaleDateString()}</div>
    `;

    header.appendChild(titleDiv);
    header.appendChild(metaDiv);
    container.appendChild(header);
}

function extractCellContent(tdElement, rowIndex, colIndex) {
    const contentContainer = document.createElement('div');

    // Style container
    contentContainer.style.padding = '10px';
    contentContainer.style.border = '1px solid #ddd';
    contentContainer.style.borderRadius = '4px';
    contentContainer.style.backgroundColor = 'white';
    contentContainer.style.marginBottom = '20px';

    // Get content sources
    const inputElement = tdElement.querySelector('input, textarea');
    const previewElement = tdElement.querySelector('.markdown-preview');
    const cellStyle = getCellStyle(rowIndex, colIndex) || {};

    // Create content div
    const contentDiv = document.createElement('div');
    contentDiv.style.wordWrap = 'break-word';
    contentDiv.style.whiteSpace = 'pre-wrap';
    contentDiv.style.fontSize = '14px';
    contentDiv.style.lineHeight = '1.5';
    contentDiv.style.color = '#000'; // Default black text
    contentDiv.style.fontFamily = 'inherit';

    // Extract content
    // Check if markdown preview is active and has content
    if (previewElement && !tdElement.classList.contains('hide-markdown-preview') && previewElement.style.display !== 'none' && previewElement.innerHTML.trim() !== '') {
        // Use markdown preview (clone and clean)
        const previewClone = previewElement.cloneNode(true);

        // Reset positioning constraints for PDF
        previewClone.style.display = 'block';
        previewClone.style.position = 'static';
        previewClone.style.width = '100%';
        previewClone.style.height = 'auto';
        previewClone.style.maxHeight = 'none';
        previewClone.style.overflow = 'visible';
        previewClone.style.border = 'none';
        previewClone.style.padding = '0';
        previewClone.style.margin = '0';

        // Remove edit buttons or other UI elements if they complicate 
        // (Assuming standard math/markdown elements are clean enough)

        contentDiv.appendChild(previewClone);
    } else if (inputElement && inputElement.value) {
        // Use raw text with styling
        let textContent = inputElement.value;
        // Escape HTML
        textContent = textContent
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Convert newlines to breaks
        textContent = textContent.replace(/\n/g, '<br>');

        contentDiv.innerHTML = textContent;

        // Copy basic input styles
        if (inputElement.style.color) contentDiv.style.color = inputElement.style.color;
        if (inputElement.style.fontWeight) contentDiv.style.fontWeight = inputElement.style.fontWeight;
        if (inputElement.style.fontStyle) contentDiv.style.fontStyle = inputElement.style.fontStyle;
        if (inputElement.style.textAlign) contentDiv.style.textAlign = inputElement.style.textAlign;
        if (inputElement.style.textDecoration) contentDiv.style.textDecoration = inputElement.style.textDecoration;
    } else {
        // Empty cell
        contentDiv.innerHTML = '<em style="color: #999;">Empty cell</em>';
    }

    // Apply container styling from cell style
    if (cellStyle) {
        if (cellStyle.bold && !contentDiv.style.fontWeight) contentDiv.style.fontWeight = 'bold';
        if (cellStyle.italic && !contentDiv.style.fontStyle) contentDiv.style.fontStyle = 'italic';
        if (cellStyle.center && !contentDiv.style.textAlign) contentDiv.style.textAlign = 'center';

        if (cellStyle.bgColor) { // Assuming structure { bgColor: '#...', ... } from memory of user's custom impl or std
            contentContainer.style.backgroundColor = cellStyle.bgColor;
        } else if (cellStyle.backgroundColor) {
            contentContainer.style.backgroundColor = cellStyle.backgroundColor;
        }

        if (cellStyle.textColor) {
            contentDiv.style.color = cellStyle.textColor;
        }
    }

    // Inherit from TD if not overridden
    if (!contentContainer.style.backgroundColor && tdElement.style.backgroundColor) {
        contentContainer.style.backgroundColor = tdElement.style.backgroundColor;
    }

    contentContainer.appendChild(contentDiv);
    return contentContainer;
}

function addPDFFooter(container) {
    const footer = document.createElement('div');
    footer.style.marginTop = '40px';
    footer.style.paddingTop = '10px';
    footer.style.borderTop = '1px solid #eee';
    footer.style.fontSize = '10px';
    footer.style.color = '#999';
    footer.style.textAlign = 'center';
    footer.innerHTML = `Generated by Excel-like Data Table • ${new Date().toLocaleString()}`;
    container.appendChild(footer);
}

function captureAndGeneratePDF(container, filename) {
    // Wait for content to render/load (especially math/images)
    setTimeout(() => {
        // Use html2canvas
        // Ensure html2canvas is loaded
        if (typeof html2canvas === 'undefined') {
            showToast('Library html2canvas not loaded!', 'error');
            document.body.removeChild(container);
            return;
        }

        html2canvas(container, {
            scale: 2, // 2x scale for sharper text
            useCORS: true,
            allowTaint: true,
            logging: false,
            backgroundColor: '#ffffff',
            windowWidth: container.scrollWidth,
            windowHeight: container.scrollHeight
        }).then(canvas => {
            try {
                // Ensure jsPDF is loaded
                if (typeof window.jspdf === 'undefined') {
                    showToast('Library jsPDF not loaded!', 'error');
                    document.body.removeChild(container);
                    return;
                }

                const { jsPDF } = window.jspdf;

                // Calculate dimensions
                const imgWidthPx = canvas.width;
                const imgHeightPx = canvas.height;

                // Standard A4 width in mm is 210. Margins 5mm each side => 200mm usable width.
                const pageMargin = 5;
                const usableWidthMm = 200;

                // Calculate equivalent height in mm maintaining aspect ratio
                const imgHeightMm = (imgHeightPx * usableWidthMm) / imgWidthPx;

                // Add margins to total height needed
                const totalHeightMm = imgHeightMm + (pageMargin * 2);

                // Standard A4 height is 297mm
                const a4HeightMm = 297;

                // Initialize PDF
                let doc;
                if (totalHeightMm > a4HeightMm) {
                    // Use custom page size (A4 width, sufficient height) to fit content
                    doc = new jsPDF({
                        orientation: 'p',
                        unit: 'mm',
                        format: [210, totalHeightMm] // A4 width, custom height
                    });
                } else {
                    // Use standard A4
                    doc = new jsPDF();
                }

                // Add image to PDF
                const imgData = canvas.toDataURL('image/jpeg', 0.95);

                // Add image exactly to fit width
                doc.addImage(imgData, 'JPEG', pageMargin, pageMargin, usableWidthMm, imgHeightMm);

                // --- ADD LINKS OVERLAY ---
                // Find all links in the original container to map them to PDF coordinates
                const links = container.querySelectorAll('a');
                if (links.length > 0) {
                    // Calculate scale factor: PDF width (mm) / Canvas width (px)
                    const scaleFactor = usableWidthMm / imgWidthPx;

                    // We need to account for the image position (margins)
                    const xOffset = pageMargin;
                    const yOffset = pageMargin;

                    links.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href) {
                            // Get visual position relative to container
                            // Since container is off-screen, we rely on its internal layout
                            // We use the canvas dimensions to map back, but checking specific element positions
                            // inside the container works if we haven't destroyed it yet.

                            // Note: container is absolute positioned off-screen, but layout is computed.
                            const rect = link.getBoundingClientRect();
                            const containerRect = container.getBoundingClientRect();

                            // Calculate relative position in pixels
                            const linkX = rect.left - containerRect.left;
                            const linkY = rect.top - containerRect.top;
                            const linkW = rect.width;
                            const linkH = rect.height;

                            // Convert to PDF coordinates (mm)
                            // We map the CSS pixel position (0 to scrollWidth) to the PDF mm position
                            const cssWidth = container.scrollWidth;
                            const cssHeight = container.scrollHeight;

                            const pdfX = pageMargin + (linkX / cssWidth) * usableWidthMm;
                            const pdfY = pageMargin + (linkY / cssHeight) * imgHeightMm;
                            const pdfW = (linkW / cssWidth) * usableWidthMm;
                            const pdfH = (linkH / cssHeight) * imgHeightMm;

                            // Ensure URL is absolute for PDF
                            let fullUrl = href;
                            if (!href.startsWith('http://') && !href.startsWith('https://') && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
                                if (href.includes('.') && !href.includes(' ')) {
                                    fullUrl = 'http://' + href;
                                } else {
                                    fullUrl = window.location.origin + (href.startsWith('/') ? '' : '/') + href;
                                }
                            }

                            // Add clickable link to PDF
                            doc.link(pdfX, pdfY, pdfW, pdfH, { url: fullUrl });

                            // Optional: Debugging - draw rect around link (comment out for production)
                            // doc.setDrawColor(255, 0, 0);
                            // doc.rect(pdfX, pdfY, pdfW, pdfH);
                        }
                    });
                }
                // -------------------------

                // Save PDF
                const finalFilename = filename.endsWith('.pdf') ? filename : filename + '.pdf';
                doc.save(finalFilename);

                showToast(`PDF exported: ${finalFilename}`, 'success');
            } catch (err) {
                console.error("PDF Generation Error: ", err);
                showToast("Failed to generate PDF", "error");
            } finally {
                // Cleanup
                if (container && container.parentNode) {
                    container.parentNode.removeChild(container);
                }
            }
        }).catch(err => {
            console.error("html2canvas Error: ", err);
            showToast("Failed to capture cell content", "error");
            if (container && container.parentNode) {
                container.parentNode.removeChild(container);
            }
        });
    }, 200); // 200ms delay to ensure rendering
}

function copySheetContent() {
    try {
        const sheet = tableData.sheets[currentSheet];
        if (!sheet || !sheet.rows || sheet.rows.length === 0) {
            showToast("Sheet is empty", "info");
            return;
        }

        let allText = [];

        sheet.rows.forEach(row => {
            let rowText = [];
            row.forEach((cellValue) => {
                if (cellValue !== null && cellValue !== undefined && cellValue !== '') {
                    // Start of Selection
                    const strValue = String(cellValue);
                    rowText.push(strValue.trim());
                    // End of Selection
                }
            });
            // Only add row if it has content
            if (rowText.length > 0) {
                allText.push(rowText.join(' '));
            }
        });

        const finalText = allText.join('\n\n');

        if (!finalText) {
            showToast("No content to copy", "info");
            return;
        }

        // Try Clipboard API first
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(finalText).then(() => {
                showToast("Sheet content copied!", "success");
            }).catch(err => {
                console.warn("Clipboard API failed, trying fallback...", err);
                copyToClipboardFallback(finalText);
            });
        } else {
            // Fallback for older browsers or insecure contexts
            copyToClipboardFallback(finalText);
        }
    } catch (e) {
        console.error("Error in copySheetContent:", e);
        showToast("Error copying content", "error");
    }
}

function copyToClipboardFallback(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed'; // Avoid scrolling to bottom
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();

    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showToast("Sheet content copied!", "success");
        } else {
            showToast("Failed to copy content", "error");
        }
    } catch (err) {
        console.error("Fallback copy failed", err);
        showToast("Failed to copy content", "error");
    }

    document.body.removeChild(textarea);
}
