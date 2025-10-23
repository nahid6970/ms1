#!/usr/bin/env python3
"""
Static HTML Export Script
Generates a standalone HTML file from the current table data
"""

import json
import os
from datetime import datetime

# Paths
DATA_FILE = r'C:\Users\nahid\ms\ms1\scripts\flask\5018_cell\data.json'
OUTPUT_FILE = r'C:\Users\nahid\ms\db\5000_myhome\mycell.html'

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'sheets': [], 'activeSheet': 0}

def generate_static_html(data):
    """Generate static HTML from table data - matches main application exactly"""
    
    # Get current time for export info
    export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get active sheet
    active_sheet = data.get('activeSheet', 0)
    sheets = data.get('sheets', [])
    
    # Start building HTML with exact same structure as main app
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Cell Data - Static Export</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            height: calc(100vh - 40px);
        }

        .sheet-tabs {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }

        .sheet-controls {
            display: flex;
            align-items: center;
            gap: 5px;
            flex: 1;
            min-width: 0;
        }

        .sheet-selector {
            position: relative;
            flex: 1;
            min-width: 150px;
            max-width: 300px;
        }

        .sheet-current {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding: 8px 15px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
            transition: all 0.2s;
        }

        .sheet-current:hover {
            background: #f8f9fa;
            border-color: #007bff;
        }

        #currentSheetName {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            text-align: left;
        }

        .dropdown-arrow {
            color: #666;
            font-size: 12px;
            flex-shrink: 0;
        }

        .sheet-list {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            margin-top: 5px;
            max-height: 300px;
            overflow-y: auto;
        }

        .sheet-list.show {
            display: block;
        }

        .sheet-item {
            padding: 12px 15px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s;
        }

        .sheet-item:last-child {
            border-bottom: none;
        }

        .sheet-item:hover {
            background: #f8f9fa;
        }

        .sheet-item.active {
            background: #e7f3ff;
            color: #007bff;
            font-weight: 600;
        }

        .sheet-item-name {
            font-size: 14px;
            display: block;
            width: 100%;
        }

        .export-info {
            margin-left: auto;
            color: #666;
            font-size: 12px;
            padding: 8px 15px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .table-container {
            flex: 1;
            overflow: auto;
            padding: 0 20px;
        }

        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: white;
            table-layout: fixed;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            position: relative;
            box-sizing: border-box;
        }

        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .header-cell {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 5px;
            overflow: visible;
            position: relative;
            padding-right: 25px;
            min-width: 0;
        }

        .column-name {
            flex: 1;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .row-number {
            background: #f8f9fa;
            font-weight: 600;
            text-align: left;
            white-space: nowrap;
            width: 60px;
            min-width: 60px;
            padding: 0 5px;
            font-family: monospace;
            font-size: 12px;
            vertical-align: middle;
            display: table-cell;
            line-height: 1.2;
        }

        .cell-content {
            width: 100%;
            border: none;
            padding: 4px;
            font-size: 14px;
            background: transparent;
            box-sizing: border-box;
            pointer-events: none;
        }

        td.merged-cell {
            text-align: center;
            vertical-align: middle;
            padding: 0 !important;
            position: relative;
        }

        td.merged-cell .cell-content {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 8px;
            font-size: 14px;
            background: transparent;
            resize: none;
            font-family: inherit;
            overflow: auto;
            box-sizing: border-box;
        }

        tr {
            height: 40px;
        }

        .no-data {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }

        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
                height: auto;
            }
            
            .sheet-tabs {
                display: none;
            }
        }
    </style>
    <script>
        let currentSheet = ''' + str(active_sheet) + ''';
        let tableData = ''' + json.dumps(data) + ''';

        function switchSheet(index) {
            currentSheet = index;
            renderSheetTabs();
            renderTable();
        }

        function toggleSheetList() {
            const sheetList = document.getElementById('sheetList');
            sheetList.classList.toggle('show');
        }

        function renderSheetTabs() {
            const currentSheetNameEl = document.getElementById('currentSheetName');
            if (tableData.sheets[currentSheet]) {
                currentSheetNameEl.textContent = tableData.sheets[currentSheet].name;
            }

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
                th.style.backgroundColor = col.headerBgColor || col.color || '#f8f9fa';

                const headerCell = document.createElement('div');
                headerCell.className = 'header-cell';

                const columnName = document.createElement('span');
                columnName.className = 'column-name';
                columnName.textContent = col.name;
                columnName.style.color = col.headerTextColor || col.textColor || '#333333';
                columnName.style.fontWeight = (col.headerBold !== false) ? 'bold' : 'normal';
                columnName.style.fontStyle = col.headerItalic ? 'italic' : 'normal';

                if (col.headerCenter) {
                    columnName.style.textAlign = 'center';
                    columnName.style.flex = '1';
                }

                headerCell.appendChild(columnName);
                th.appendChild(headerCell);
                headerRow.appendChild(th);
            });

            // Render rows
            sheet.rows.forEach((row, rowIndex) => {
                const tr = document.createElement('tr');

                // Row number
                const rowNumCell = document.createElement('td');
                rowNumCell.className = 'row-number';
                rowNumCell.textContent = rowIndex + 1;
                tr.appendChild(rowNumCell);

                // Data cells
                sheet.columns.forEach((col, colIndex) => {
                    const td = document.createElement('td');
                    td.style.width = col.width + 'px';
                    td.style.minWidth = col.width + 'px';
                    td.style.maxWidth = col.width + 'px';
                    td.style.backgroundColor = col.color;

                    const cellContent = document.createElement('div');
                    cellContent.className = 'cell-content';
                    cellContent.textContent = row[colIndex] || '';
                    cellContent.style.color = col.textColor || '#000000';

                    if (col.font && col.font !== '') {
                        cellContent.style.fontFamily = `'${col.font}', monospace`;
                    }

                    // Apply cell-specific styles
                    const cellStyle = (sheet.cellStyles || {})[`${rowIndex}-${colIndex}`] || {};
                    if (cellStyle.bold) cellContent.style.fontWeight = 'bold';
                    if (cellStyle.italic) cellContent.style.fontStyle = 'italic';
                    if (cellStyle.center) cellContent.style.textAlign = 'center';
                    if (cellStyle.border !== false && (cellStyle.borderWidth || cellStyle.borderStyle || cellStyle.borderColor)) {
                        const borderWidth = cellStyle.borderWidth || '1px';
                        const borderStyle = cellStyle.borderStyle || 'solid';
                        const borderColor = cellStyle.borderColor || '#000000';
                        td.style.border = `${borderWidth} ${borderStyle} ${borderColor}`;
                    }
                    if (cellStyle.bgColor) {
                        td.style.backgroundColor = cellStyle.bgColor;
                    }
                    if (cellStyle.textColor) {
                        cellContent.style.color = cellStyle.textColor;
                    }
                    if (cellStyle.fontSize) {
                        cellContent.style.fontSize = cellStyle.fontSize;
                    }

                    // Handle merged cells
                    const mergeInfo = (sheet.mergedCells || {})[`${rowIndex}-${colIndex}`];
                    if (mergeInfo) {
                        if (mergeInfo.hidden) {
                            td.style.display = 'none';
                            tr.appendChild(td);
                            return;
                        } else if (mergeInfo.colspan || mergeInfo.rowspan) {
                            td.colSpan = mergeInfo.colspan || 1;
                            td.rowSpan = mergeInfo.rowspan || 1;
                            td.classList.add('merged-cell');
                        }
                    }

                    td.appendChild(cellContent);
                    tr.appendChild(td);
                });

                tableBody.appendChild(tr);
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const sheetSelector = document.querySelector('.sheet-selector');
            const sheetList = document.getElementById('sheetList');
            if (!sheetSelector.contains(event.target)) {
                sheetList.classList.remove('show');
            }
        });

        // Initialize on load
        window.onload = function() {
            renderSheetTabs();
            renderTable();
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="sheet-tabs">
            <div class="sheet-controls">
                <div class="sheet-selector">
                    <button class="sheet-current" id="currentSheetBtn" onclick="toggleSheetList()">
                        <span id="currentSheetName">''' + (sheets[active_sheet]['name'] if sheets and active_sheet < len(sheets) else 'Sheet1') + '''</span>
                        <span class="dropdown-arrow">▼</span>
                    </button>
                    <div class="sheet-list" id="sheetList"></div>
                </div>
            </div>

            <div class="export-info">
                Static export - ''' + export_time + '''
            </div>
        </div>

        <div class="table-container">
            <table id="dataTable">
                <thead id="tableHead">
                    <tr id="headerRow"></tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>
</body>
</html>'''

    return html_content

def export_to_static():
    """Main export function"""
    try:
        # Check if data file exists
        if not os.path.exists(DATA_FILE):
            print(f"ERROR: Data file not found: {DATA_FILE}")
            return False
        
        # Load data
        data = load_data()
        print(f"Loaded data with {len(data.get('sheets', []))} sheets")
        
        # Generate HTML
        html_content = generate_static_html(data)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(OUTPUT_FILE)
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Write HTML file
        print(f"Writing HTML file to: {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Verify file was created
        if os.path.exists(OUTPUT_FILE):
            file_size = os.path.getsize(OUTPUT_FILE)
            print(f"Static HTML exported successfully!")
            print(f"   File: {OUTPUT_FILE}")
            print(f"   Size: {file_size:,} bytes")
            return True
        else:
            print(f"ERROR: File was not created: {OUTPUT_FILE}")
            return False
        
    except Exception as e:
        import traceback
        print(f"ERROR: Error exporting static HTML: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    export_to_static()