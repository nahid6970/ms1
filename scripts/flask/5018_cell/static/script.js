let tableData = { sheets: [], activeSheet: 0 };
let currentSheet = 0;
let contextMenuCell = null;
let selectedCells = []; // Array of {row, col, td} objects for multi-cell operations
let isSelecting = false;

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
    initializeApp();
};

function initializeApp() {
    // Set up form handlers
    document.getElementById('columnForm').onsubmit = handleColumnFormSubmit;
    document.getElementById('renameForm').onsubmit = handleRenameFormSubmit;

    // Set up keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

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

    // Clear old localStorage values and set new defaults
    localStorage.removeItem('actionsWidth');
    localStorage.removeItem('rownumWidth');

    // Load initial data
    loadData();
}

function loadColumnWidths() {
    const actionsWidth = localStorage.getItem('actionsWidth') || '75px';
    const rownumWidth = localStorage.getItem('rownumWidth') || '75px';

    document.documentElement.style.setProperty('--actions-width', actionsWidth);
    document.documentElement.style.setProperty('--rownum-width', rownumWidth);
}



function handleKeyboardShortcuts(e) {
    // Ctrl+S or Cmd+S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();

        // Blur the currently focused element to trigger onchange
        if (document.activeElement && document.activeElement.tagName === 'INPUT') {
            document.activeElement.blur();
        }

        // Small delay to ensure onchange fires before saving
        setTimeout(() => {
            saveData();
        }, 50);
    }
}

async function loadData() {
    try {
        const response = await fetch('/api/data');
        tableData = await response.json();
        currentSheet = tableData.activeSheet || 0;
        renderSheetTabs();
        renderTable();
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

async function handleColumnFormSubmit(e) {
    e.preventDefault();

    const editingIndex = parseInt(document.getElementById('editingColumnIndex').value);
    const column = {
        name: document.getElementById('columnName').value,
        type: document.getElementById('columnType').value,
        width: document.getElementById('columnWidth').value,
        color: document.getElementById('columnColor').value,
        textColor: document.getElementById('columnTextColor').value,
        font: document.getElementById('columnFont').value,
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

    try {
        const response = await fetch(`/api/sheets/${currentSheet}/rename`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName })
        });

        if (response.ok) {
            tableData.sheets[currentSheet].name = newName;
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

async function addRow() {
    try {
        const response = await fetch('/api/rows', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sheetIndex: currentSheet })
        });
        if (response.ok) {
            const sheet = tableData.sheets[currentSheet];
            sheet.rows.push(new Array(sheet.columns.length).fill(''));
            renderTable();
        }
    } catch (error) {
        console.error('Error adding row:', error);
    }
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

function updateCell(rowIndex, colIndex, value) {
    const sheet = tableData.sheets[currentSheet];
    if (!sheet.cellStyles) {
        sheet.cellStyles = {};
    }

    // Store value
    sheet.rows[rowIndex][colIndex] = value;
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
    return sheet.cellStyles[key] || {};
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
            }
        });
        showToast(`Bold ${newValue ? 'applied' : 'removed'} for ${selectedCells.length} cells`, 'success');
    } else {
        // Apply to single cell
        setCellStyle(rowIndex, colIndex, 'bold', newValue);
        inputElement.style.fontWeight = newValue ? 'bold' : 'normal';
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
            }
        });
        showToast(`Italic ${newValue ? 'applied' : 'removed'} for ${selectedCells.length} cells`, 'success');
    } else {
        // Apply to single cell
        setCellStyle(rowIndex, colIndex, 'italic', newValue);
        inputElement.style.fontStyle = newValue ? 'italic' : 'normal';
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

    // Position menu
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    menu.classList.add('show');
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
    toggleInput.checked = currentStyle.border !== false; // Default to true if not explicitly false
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
    okBtn.onclick = () => applyUnifiedBorderOptions(rowIndex, colIndex);

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

function applyUnifiedBorderOptions(rowIndex, colIndex) {
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
                    cellTd.style.border = '1px solid #ddd';
                }
            }
        });
        showToast(`Border options applied to ${selectedCells.length} cells`, 'success');
    } else {
        const { tdElement } = contextMenuCell;
        
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
                tdElement.style.border = '1px solid #ddd';
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
            renderSheetTabs();
            renderTable();
        }
    } catch (error) {
        console.error('Error adding sheet:', error);
    }
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
    currentSheet = index;
    renderSheetTabs();
    renderTable();
    autoSaveActiveSheet();
}

function showRenameModal(index) {
    currentSheet = index;
    document.getElementById('sheetName').value = tableData.sheets[index].name;
    document.getElementById('renameModal').style.display = 'block';
}



function renderSheetTabs() {
    // Update current sheet name
    const currentSheetNameEl = document.getElementById('currentSheetName');
    if (tableData.sheets[currentSheet]) {
        currentSheetNameEl.textContent = tableData.sheets[currentSheet].name;
    }

    // Render sheet list (simplified - just for switching)
    const sheetList = document.getElementById('sheetList');
    sheetList.innerHTML = '';

    tableData.sheets.forEach((sheet, index) => {
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
    document.getElementById('settingsModal').style.display = 'block';
}

function renderTable() {
    const headerRow = document.getElementById('headerRow');
    const tableBody = document.getElementById('tableBody');

    headerRow.innerHTML = '';
    tableBody.innerHTML = '';

    const sheet = tableData.sheets[currentSheet];
    if (!sheet) return;

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

        headerCell.appendChild(columnName);
        headerCell.appendChild(menuWrapper);
        th.appendChild(headerCell);
        headerRow.appendChild(th);
    });

    // Render rows
    sheet.rows.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');

        // Row number with delete X and number together
        const rowNumCell = document.createElement('td');
        rowNumCell.className = 'row-number';

        const contentSpan = document.createElement('span');
        contentSpan.innerHTML = '<span class="delete-x" title="Delete row">×</span>&nbsp;' + (rowIndex + 1);
        contentSpan.style.cursor = 'pointer';
        contentSpan.onclick = () => deleteRow(rowIndex);

        rowNumCell.appendChild(contentSpan);
        tr.appendChild(rowNumCell);

        // Data cells - only render cells for existing columns
        sheet.columns.forEach((col, colIndex) => {
            const td = document.createElement('td');
            td.style.width = col.width + 'px';
            td.style.minWidth = col.width + 'px';
            td.style.maxWidth = col.width + 'px';
            td.style.backgroundColor = col.color;

            const input = document.createElement('input');
            input.type = col.type;
            input.value = row[colIndex] || '';
            input.style.color = col.textColor || '#000000';

            // Apply column font
            if (col.font && col.font !== '') {
                input.style.fontFamily = `'${col.font}', monospace`;
            }

            input.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);

            // Apply cell-specific styles
            const cellStyle = getCellStyle(rowIndex, colIndex);
            if (cellStyle.bold) input.style.fontWeight = 'bold';
            if (cellStyle.italic) input.style.fontStyle = 'italic';
            if (cellStyle.center) input.style.textAlign = 'center';
            if (cellStyle.border) {
                const borderWidth = cellStyle.borderWidth || '1px';
                const borderStyle = cellStyle.borderStyle || 'solid';
                const borderColor = cellStyle.borderColor || '#000000';
                td.style.border = `${borderWidth} ${borderStyle} ${borderColor}`;
            } else {
                td.style.border = '1px solid #ddd';
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

            // Add context menu
            input.oncontextmenu = (e) => showCellContextMenu(e, rowIndex, colIndex, input, td);

            // Cell selection for merging - add to both td and input
            td.dataset.row = rowIndex;
            td.dataset.col = colIndex;

            const handleMouseDown = (e) => {
                if (e.button === 0 && e.shiftKey) {
                    e.preventDefault();
                    startCellSelection(rowIndex, colIndex, td);
                }
            };

            const handleMouseEnter = () => {
                if (isSelecting) {
                    addToSelection(rowIndex, colIndex, td);
                }
            };

            td.onmousedown = handleMouseDown;
            input.onmousedown = (e) => {
                if (e.shiftKey) {
                    handleMouseDown(e);
                }
            };
            td.onmouseenter = handleMouseEnter;
            input.onmouseenter = handleMouseEnter;

            // Check if merged
            const mergeInfo = getCellMerge(rowIndex, colIndex);
            if (mergeInfo) {
                if (mergeInfo.hidden) {
                    td.style.display = 'none';
                    tr.appendChild(td);
                    return; // Skip adding input for hidden cells
                } else if (mergeInfo.colspan || mergeInfo.rowspan) {
                    td.colSpan = mergeInfo.colspan || 1;
                    td.rowSpan = mergeInfo.rowspan || 1;
                    td.classList.add('merged-cell');

                    // Use textarea for merged cells
                    const textarea = document.createElement('textarea');
                    textarea.value = row[colIndex] || '';
                    textarea.style.color = col.textColor || '#000000';

                    if (col.font && col.font !== '') {
                        textarea.style.fontFamily = `'${col.font}', monospace`;
                    }

                    textarea.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);

                    const cellStyle = getCellStyle(rowIndex, colIndex);
                    if (cellStyle.bold) textarea.style.fontWeight = 'bold';
                    if (cellStyle.italic) textarea.style.fontStyle = 'italic';
                    if (cellStyle.center) textarea.style.textAlign = 'center';
                    if (cellStyle.border) {
                        const borderWidth = cellStyle.borderWidth || '1px';
                        const borderStyle = cellStyle.borderStyle || 'solid';
                        const borderColor = cellStyle.borderColor || '#000000';
                        td.style.border = `${borderWidth} ${borderStyle} ${borderColor}`;
                    } else {
                        td.style.border = '1px solid #ddd';
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
                    tr.appendChild(td);
                    return;
                }
            }

            td.appendChild(input);
            tr.appendChild(td);
        });

        tableBody.appendChild(tr);
    });
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
