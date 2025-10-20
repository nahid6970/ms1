let tableData = { columns: [], rows: [] };

// Load data on page load
window.onload = function() {
    loadData();
};

async function loadData() {
    try {
        const response = await fetch('/api/data');
        tableData = await response.json();
        renderTable();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

async function saveData() {
    try {
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

function closeModal() {
    document.getElementById('columnModal').style.display = 'none';
    document.getElementById('columnForm').reset();
}

document.getElementById('columnForm').onsubmit = async function(e) {
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
            body: JSON.stringify(column)
        });
        
        if (response.ok) {
            tableData.columns.push(column);
            tableData.rows.forEach(row => row.push(''));
            renderTable();
            closeModal();
        }
    } catch (error) {
        console.error('Error adding column:', error);
    }
};

async function deleteColumn(index) {
    if (!confirm('Delete this column?')) return;
    
    try {
        const response = await fetch(`/api/columns/${index}`, { method: 'DELETE' });
        if (response.ok) {
            tableData.columns.splice(index, 1);
            tableData.rows.forEach(row => row.splice(index, 1));
            renderTable();
        }
    } catch (error) {
        console.error('Error deleting column:', error);
    }
}

async function addRow() {
    try {
        const response = await fetch('/api/rows', { method: 'POST' });
        if (response.ok) {
            tableData.rows.push(new Array(tableData.columns.length).fill(''));
            renderTable();
        }
    } catch (error) {
        console.error('Error adding row:', error);
    }
}

async function deleteRow(index) {
    if (!confirm('Delete this row?')) return;
    
    try {
        const response = await fetch(`/api/rows/${index}`, { method: 'DELETE' });
        if (response.ok) {
            tableData.rows.splice(index, 1);
            renderTable();
        }
    } catch (error) {
        console.error('Error deleting row:', error);
    }
}

function updateCell(rowIndex, colIndex, value) {
    tableData.rows[rowIndex][colIndex] = value;
}

function renderTable() {
    const headerRow = document.getElementById('headerRow');
    const tableBody = document.getElementById('tableBody');
    
    headerRow.innerHTML = '<th class="row-number">#</th>';
    tableBody.innerHTML = '';

    // Render headers
    tableData.columns.forEach((col, index) => {
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
    tableData.rows.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        
        // Row number
        const rowNumCell = document.createElement('td');
        rowNumCell.className = 'row-number';
        rowNumCell.textContent = rowIndex + 1;
        tr.appendChild(rowNumCell);
        
        // Data cells
        row.forEach((cellValue, colIndex) => {
            const td = document.createElement('td');
            const col = tableData.columns[colIndex];
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

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('columnModal');
    if (event.target === modal) {
        closeModal();
    }
};
