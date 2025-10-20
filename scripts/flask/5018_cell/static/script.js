let tableData = { sheets: [], activeSheet: 0 };
let currentSheet = 0;
let contextMenuCell = null;

// Load data on page load
window.onload = function() {
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
    
    // Load initial data
    loadData();
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
        font: document.getElementById('columnFont').value
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
    
    setCellStyle(rowIndex, colIndex, 'bold', newValue);
    inputElement.style.fontWeight = newValue ? 'bold' : 'normal';
    
    document.getElementById('ctxBold').classList.toggle('checked', newValue);
}

function toggleCellItalic() {
    if (!contextMenuCell) return;
    
    const { rowIndex, colIndex, inputElement } = contextMenuCell;
    const style = getCellStyle(rowIndex, colIndex);
    const newValue = !style.italic;
    
    setCellStyle(rowIndex, colIndex, 'italic', newValue);
    inputElement.style.fontStyle = newValue ? 'italic' : 'normal';
    
    document.getElementById('ctxItalic').classList.toggle('checked', newValue);
}

function toggleCellCenter() {
    if (!contextMenuCell) return;
    
    const { rowIndex, colIndex, inputElement } = contextMenuCell;
    const style = getCellStyle(rowIndex, colIndex);
    const newValue = !style.center;
    
    setCellStyle(rowIndex, colIndex, 'center', newValue);
    inputElement.style.textAlign = newValue ? 'center' : 'left';
    
    document.getElementById('ctxCenter').classList.toggle('checked', newValue);
}

function closeCellContextMenu() {
    document.getElementById('cellContextMenu').classList.remove('show');
    contextMenuCell = null;
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
    
    headerRow.innerHTML = '<th class="row-number">#</th>';
    tableBody.innerHTML = '';
    
    const sheet = tableData.sheets[currentSheet];
    if (!sheet) return;

    // Render headers
    sheet.columns.forEach((col, index) => {
        const th = document.createElement('th');
        th.style.width = col.width + 'px';
        th.style.backgroundColor = col.color;
        
        const headerCell = document.createElement('div');
        headerCell.className = 'header-cell';
        
        const columnName = document.createElement('span');
        columnName.className = 'column-name';
        columnName.textContent = col.name;
        columnName.style.color = col.textColor || '#000000';
        
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
        sortAscItem.innerHTML = '<span>↑</span> Ascending';
        sortAscItem.onclick = () => {
            sortColumn(index, 'asc');
            closeAllColumnMenus();
        };
        
        const sortDescItem = document.createElement('div');
        sortDescItem.className = 'column-menu-item';
        sortDescItem.innerHTML = '<span>↓</span> Descending';
        sortDescItem.onclick = () => {
            sortColumn(index, 'desc');
            closeAllColumnMenus();
        };
        
        sortSubmenu.appendChild(sortAscItem);
        sortSubmenu.appendChild(sortDescItem);
        sortItem.appendChild(sortSubmenu);
        
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
        
        menu.appendChild(sortItem);
        menu.appendChild(editItem);
        menu.appendChild(deleteItem);
        menuWrapper.appendChild(menuBtn);
        menuWrapper.appendChild(menu);
        
        headerCell.appendChild(columnName);
        headerCell.appendChild(menuWrapper);
        th.appendChild(headerCell);
        headerRow.appendChild(th);
    });
    
    // Add actions column
    const actionsHeader = document.createElement('th');
    actionsHeader.textContent = 'Actions';
    actionsHeader.style.width = '100px';
    headerRow.appendChild(actionsHeader);
    
    // Render rows
    sheet.rows.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        
        // Row number
        const rowNumCell = document.createElement('td');
        rowNumCell.className = 'row-number';
        rowNumCell.textContent = rowIndex + 1;
        tr.appendChild(rowNumCell);
        
        // Data cells - only render cells for existing columns
        sheet.columns.forEach((col, colIndex) => {
            const td = document.createElement('td');
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
                td.style.border = '2px solid #007bff';
            }
            
            // Add context menu
            input.oncontextmenu = (e) => showCellContextMenu(e, rowIndex, colIndex, input, td);
            
            td.appendChild(input);
            tr.appendChild(td);
        });
        
        // Actions cell
        const actionsCell = document.createElement('td');
        actionsCell.className = 'row-actions';
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-danger';
        deleteBtn.textContent = 'Delete';
        deleteBtn.onclick = () => deleteRow(rowIndex);
        
        actionsCell.appendChild(deleteBtn);
        tr.appendChild(actionsCell);
        
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

// Close modal and dropdowns when clicking outside
window.onclick = function(event) {
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
