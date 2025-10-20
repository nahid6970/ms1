let tableData = { sheets: [], activeSheet: 0 };
let currentSheet = 0;

// Load data on page load
window.onload = function() {
    initializeApp();
};

function initializeApp() {
    // Set up form handlers
    document.getElementById('columnForm').onsubmit = handleColumnFormSubmit;
    document.getElementById('renameForm').onsubmit = handleRenameFormSubmit;
    
    // Load initial data
    loadData();
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
            alert('Data saved successfully!');
        }
    } catch (error) {
        console.error('Error saving data:', error);
        alert('Error saving data!');
    }
}

function addColumn() {
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

async function handleColumnFormSubmit(e) {
    e.preventDefault();
    
    const column = {
        name: document.getElementById('columnName').value,
        type: document.getElementById('columnType').value,
        width: document.getElementById('columnWidth').value,
        color: document.getElementById('columnColor').value
    };

    try {
        const response = await fetch('/api/columns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ column, sheetIndex: currentSheet })
        });
        
        if (response.ok) {
            const sheet = tableData.sheets[currentSheet];
            sheet.columns.push(column);
            sheet.rows.forEach(row => row.push(''));
            renderTable();
            closeColumnModal();
        }
    } catch (error) {
        console.error('Error adding column:', error);
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
    tableData.sheets[currentSheet].rows[rowIndex][colIndex] = value;
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
    
    if (!confirm(`Delete sheet "${tableData.sheets[index].name}"?`)) return;
    
    try {
        const response = await fetch(`/api/sheets/${index}`, { method: 'DELETE' });
        if (response.ok) {
            tableData.sheets.splice(index, 1);
            if (currentSheet >= tableData.sheets.length) {
                currentSheet = tableData.sheets.length - 1;
            }
            renderSheetTabs();
            renderTable();
        }
    } catch (error) {
        console.error('Error deleting sheet:', error);
    }
}

function switchSheet(index) {
    currentSheet = index;
    renderSheetTabs();
    renderTable();
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
    
    // Render sheet list
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
        
        const actions = document.createElement('div');
        actions.className = 'sheet-item-actions';
        
        const renameBtn = document.createElement('button');
        renameBtn.className = 'sheet-action-btn rename';
        renameBtn.textContent = '✏️';
        renameBtn.title = 'Rename';
        renameBtn.onclick = (e) => {
            e.stopPropagation();
            showRenameModal(index);
            toggleSheetList();
        };
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'sheet-action-btn delete';
        deleteBtn.textContent = '🗑️';
        deleteBtn.title = 'Delete';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteSheet(index);
            toggleSheetList();
        };
        
        actions.appendChild(renameBtn);
        if (tableData.sheets.length > 1) {
            actions.appendChild(deleteBtn);
        }
        
        item.appendChild(nameSpan);
        item.appendChild(actions);
        sheetList.appendChild(item);
    });
}

function toggleSheetList() {
    const sheetList = document.getElementById('sheetList');
    sheetList.classList.toggle('show');
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
        th.innerHTML = `
            <div class="header-cell">
                <span class="column-name">${col.name}</span>
                <button class="btn btn-danger" onclick="deleteColumn(${index})">×</button>
            </div>
        `;
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
        
        // Data cells
        row.forEach((cellValue, colIndex) => {
            const td = document.createElement('td');
            const col = sheet.columns[colIndex];
            td.style.backgroundColor = col.color;
            
            const input = document.createElement('input');
            input.type = col.type;
            input.value = cellValue;
            input.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);
            
            td.appendChild(input);
            tr.appendChild(td);
        });
        
        // Actions cell
        const actionsCell = document.createElement('td');
        actionsCell.className = 'row-actions';
        actionsCell.innerHTML = `
            <button class="btn btn-danger" onclick="deleteRow(${rowIndex})">Delete</button>
        `;
        tr.appendChild(actionsCell);
        
        tableBody.appendChild(tr);
    });
}

// Close modal and dropdowns when clicking outside
window.onclick = function(event) {
    const columnModal = document.getElementById('columnModal');
    const renameModal = document.getElementById('renameModal');
    const sheetList = document.getElementById('sheetList');
    
    if (event.target === columnModal) {
        closeColumnModal();
    }
    if (event.target === renameModal) {
        closeRenameModal();
    }
    
    // Close sheet list when clicking outside
    if (!event.target.closest('.sheet-selector')) {
        sheetList.classList.remove('show');
    }
};
