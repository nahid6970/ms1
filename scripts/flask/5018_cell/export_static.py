#!/usr/bin/env python3
"""
Static HTML Export Script
Generates a standalone HTML file from the current table data

IMPORTANT: When adding new markdown syntax, update these 3 locations:
1. hasMarkdown detection (around line 1020) - add cellValue.includes() check
2. parseMarkdown() function (around line 1100) - add regex replacement pattern
3. CSS styles (around line 750) - add styling for new HTML elements if needed

These must match the implementation in:
- static/script.js (applyMarkdownFormatting and parseMarkdown functions)
- static/style.css (markdown-preview styles)
- templates/index.html (Markdown Guide modal)
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

        /* Mobile-first responsive design */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
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
            overflow: hidden;
        }

        .sheet-tabs {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
            flex-wrap: nowrap;
            overflow-x: auto;
            overflow-y: visible;
        }

        .category-controls {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 4px 8px;
            background: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 4px;
        }

        .category-selector {
            position: relative;
            min-width: 150px;
            z-index: 100;
        }

        .category-current {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            padding: 6px 12px;
            background: white;
            border: 1px solid #90caf9;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            width: 100%;
            transition: all 0.2s;
            font-weight: 500;
            color: #1976d2;
        }

        .category-current:hover {
            background: #f5f5f5;
            border-color: #1976d2;
        }

        .category-list {
            display: none;
            position: fixed;
            background: white;
            border: 1px solid #90caf9;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 2000;
            max-height: 300px;
            overflow-y: auto;
        }

        .category-list.show {
            display: block;
        }

        .category-item {
            padding: 10px 15px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .category-item:last-child {
            border-bottom: none;
        }

        .category-item:hover {
            background: #e3f2fd;
        }

        .category-item.active {
            background: #bbdefb;
            color: #1976d2;
            font-weight: 600;
        }

        .category-item-name {
            font-size: 13px;
            flex: 1;
        }

        .category-item-count {
            font-size: 11px;
            color: #666;
            background: #e0e0e0;
            padding: 2px 6px;
            border-radius: 10px;
        }

        .sheet-controls {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 4px 8px;
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .sheet-selector {
            position: relative;
            flex: 1;
            min-width: 150px;
            max-width: 300px;
            z-index: 100;
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
            position: fixed;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 2000;
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

        .search-box {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 4px 8px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .search-box:focus-within {
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }

        .search-box input {
            border: none;
            outline: none;
            padding: 6px 8px;
            font-size: 14px;
            width: 200px;
            background: transparent;
        }

        .btn-clear-search {
            background: none;
            border: none;
            color: #999;
            font-size: 20px;
            cursor: pointer;
            padding: 0 4px;
            line-height: 1;
            transition: color 0.2s;
            display: none;
        }

        .btn-clear-search:hover {
            color: #dc3545;
        }

        .search-box input:not(:placeholder-shown) ~ .btn-clear-search {
            display: block;
        }

        /* Search highlight */
        .search-highlight {
            background: rgba(255, 235, 59, 0.5) !important;
        }

        .button-group {
            display: flex;
            gap: 4px;
            align-items: center;
            padding: 4px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .btn-icon-toggle {
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 32px;
            height: 32px;
            cursor: pointer;
            user-select: none;
            transition: all 0.2s;
            position: relative;
        }

        .btn-icon-toggle:hover {
            background: #e9ecef;
            border-color: #007bff;
        }

        .btn-icon-toggle input[type="checkbox"] {
            position: absolute;
            opacity: 0;
            cursor: pointer;
            width: 100%;
            height: 100%;
            margin: 0;
        }

        .btn-icon-toggle span {
            font-size: 16px;
            pointer-events: none;
        }

        .btn-icon-toggle input[type="checkbox"]:checked + span {
            opacity: 1;
        }

        .btn-icon-toggle input[type="checkbox"]:not(:checked) + span {
            opacity: 0.4;
        }

        .font-size-control {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 4px 8px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .font-size-label {
            font-size: 13px;
            font-weight: 500;
            color: #333;
        }

        .btn-font-size {
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 28px;
            height: 28px;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            flex-shrink: 0;
        }

        .btn-font-size:hover {
            background: #e9ecef;
            border-color: #007bff;
            transform: scale(1.05);
        }

        .font-size-display {
            min-width: 40px;
            text-align: center;
            font-size: 13px;
            font-weight: 500;
            color: #333;
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

        /* Responsive column width variables */
        :root {
            --base-column-width: 150px;
            --row-number-width: 60px;
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
            width: var(--row-number-width);
            min-width: var(--row-number-width);
            padding: 0 5px;
            font-family: monospace;
            font-size: 12px;
            vertical-align: middle;
            display: table-cell;
            line-height: 1.2;
        }

        /* Hide row numbers when toggle is off */
        .hide-row-numbers .row-number {
            display: none;
        }

        .cell-content {
            width: 100%;
            border: none;
            padding: 4px;
            background: transparent;
            box-sizing: border-box;
            pointer-events: none;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.4;
        }

        /* Markdown formatting in static export */
        .cell-content strong {
            font-weight: bold;
            color: inherit;
        }

        /* Text wrapping enabled */
        .wrap-enabled td:not(.row-number) {
            white-space: normal;
            overflow: visible;
            word-wrap: break-word;
            word-break: break-word;
            vertical-align: top;
        }

        .wrap-enabled .cell-content {
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow: visible;
            text-overflow: clip;
            line-height: 1.4;
        }

        /* Markdown formatting works with wrap mode */
        .wrap-enabled .cell-content strong {
            font-weight: bold;
        }

        /* Default row height when wrap is enabled - keep same as normal */
        .wrap-enabled tr {
            height: 40px;
        }

        /* Only expand rows that actually have wrapped content */
        .wrap-enabled tr.has-wrapped-content {
            height: auto !important;
        }

        /* Keep row numbers centered vertically */
        .wrap-enabled .row-number {
            vertical-align: middle;
        }

        /* For rows without wrapped content, keep normal height */
        .wrap-enabled tr:not(.has-wrapped-content) td:not(.row-number) {
            height: 40px;
        }

        td.merged-cell {
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
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.4;
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

        /* Mobile responsive adjustments */
        @media (max-width: 768px) {
            :root {
                --base-column-width: 120px;
                --row-number-width: 50px;
            }

            body {
                padding: 10px;
            }

            .container {
                height: calc(100vh - 20px);
            }

            .table-container {
                padding: 0 10px;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                min-width: 100%;
            }

            table {
                min-width: 600px;
            }

            /* Make columns more flexible on mobile */
            th, td {
                min-width: 80px !important;
                padding: 6px 4px;
            }

            .row-number {
                width: var(--row-number-width) !important;
                min-width: var(--row-number-width) !important;
                font-size: 11px;
                padding: 0 3px;
            }

            /* Adjust sheet tabs for mobile */
            .sheet-tabs {
                padding: 8px 10px;
                gap: 5px;
                flex-wrap: nowrap;
                overflow-x: auto;
            }

            .category-controls {
                flex-shrink: 0;
            }

            .sheet-controls {
                flex-shrink: 0;
            }

            .category-selector {
                min-width: 120px;
            }

            .sheet-selector {
                min-width: 120px;
            }

            .search-box {
                min-width: 150px;
            }

            .button-group {
                flex-shrink: 0;
            }

            .font-size-control {
                flex-shrink: 0;
            }

            .export-info {
                display: none;
            }

            /* Adjust column headers */
            .header-cell {
                padding-left: 20px;
            }
        }

        /* Tablet responsive adjustments */
        @media (min-width: 769px) and (max-width: 1024px) {
            :root {
                --base-column-width: 130px;
                --row-number-width: 55px;
            }
        }

        /* Large screen adjustments */
        @media (min-width: 1200px) {
            :root {
                --base-column-width: 180px;
                --row-number-width: 70px;
            }
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

        /* Markdown formatting styles */
        strong {
            font-weight: bold;
        }

        em {
            font-style: italic;
        }

        code {
            background: #f4f4f4;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 2px 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #c7254e;
            line-height: 1.8;
            box-decoration-break: clone;
            -webkit-box-decoration-break: clone;
        }

        mark {
            background: #ffeb3b;
            padding: 2px 4px;
            border-radius: 6px;
        }

        del {
            text-decoration: line-through;
            color: #999;
        }

        /* IMPORTANT: When adding new markdown syntax, add CSS styling here */
        /* These styles must match static/style.css .markdown-preview styles */
        sup {
            vertical-align: super;
            font-size: 0.75em;
            line-height: 0;
        }

        sub {
            vertical-align: sub;
            font-size: 0.75em;
            line-height: 0;
        }

        u {
            text-decoration: underline;
        }

        a {
            color: #007bff;
            text-decoration: underline;
            cursor: pointer;
            pointer-events: auto;
            position: relative;
            z-index: 2;
        }

        a:hover {
            color: #0056b3;
            text-decoration: none;
        }

        /* Markdown Grid Table Styles (CSS Grid - no <table> elements) */
        .md-grid {
            display: grid;
            grid-template-columns: repeat(var(--cols), auto);
            gap: 4px;
            margin: 4px 0;
            font-size: 0.85em;
            font-family: inherit;
            width: fit-content;
            max-width: 100%;
        }

        .md-cell {
            padding: 4px 6px;
            border: 1px solid #ced4da;
            background: #fff;
            overflow: visible;
            word-break: normal;
            white-space: nowrap;
            min-width: fit-content;
        }

        .md-header {
            background: #f8f9fa;
            font-weight: 600;
            white-space: nowrap;
            border: 2px solid #495057;
        }

        /* Let coloured text / background css shine through */
        .md-grid strong {
            font-weight: bold;
        }

        .md-grid em {
            font-style: italic;
        }

        .md-grid code {
            background: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .md-grid a {
            color: #007bff;
            text-decoration: underline;
        }
    </style>
    <script>
        let currentSheet = ''' + str(active_sheet) + ''';
        let tableData = ''' + json.dumps(data) + ''';
        
        // Set currentCategory to match the active sheet's category
        let currentCategory = tableData.sheetCategories[currentSheet] || tableData.sheetCategories[String(currentSheet)] || null;

        function initializeCategories() {
            if (!tableData.categories) {
                tableData.categories = [];
            }
            if (!tableData.sheetCategories) {
                tableData.sheetCategories = {};
            }
        }

        function toggleCategoryList() {
            const categoryList = document.getElementById('categoryList');
            const button = document.getElementById('currentCategoryBtn');
            
            if (categoryList.classList.contains('show')) {
                categoryList.classList.remove('show');
            } else {
                // Position the dropdown
                const rect = button.getBoundingClientRect();
                categoryList.style.position = 'fixed';
                categoryList.style.top = (rect.bottom + 5) + 'px';
                categoryList.style.left = rect.left + 'px';
                categoryList.style.width = rect.width + 'px';
                categoryList.classList.add('show');
            }
        }

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
            if (tableData.categories) {
                tableData.categories.forEach(category => {
                    const count = Object.values(tableData.sheetCategories || {}).filter(c => c === category).length;
                    
                    const item = document.createElement('div');
                    item.className = `category-item ${currentCategory === category ? 'active' : ''}`;
                    
                    const nameSpan = document.createElement('span');
                    nameSpan.className = 'category-item-name';
                    nameSpan.textContent = category;
                    nameSpan.onclick = () => {
                        currentCategory = category;
                        
                        // Switch to first sheet in this category - handle both string and numeric keys
                        const firstSheetInCategory = tableData.sheets.findIndex((sheet, index) => {
                            const sheetCat = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)];
                            return sheetCat === category;
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
                    
                    item.appendChild(nameSpan);
                    item.appendChild(countSpan);
                    categoryList.appendChild(item);
                });
            }
        }

        function switchSheet(index) {
            currentSheet = index;
            renderSheetTabs();
            renderTable();
        }

        function toggleSheetList() {
            const sheetList = document.getElementById('sheetList');
            const button = document.getElementById('currentSheetBtn');
            
            if (sheetList.classList.contains('show')) {
                sheetList.classList.remove('show');
            } else {
                // Position the dropdown
                const rect = button.getBoundingClientRect();
                sheetList.style.position = 'fixed';
                sheetList.style.top = (rect.bottom + 5) + 'px';
                sheetList.style.left = rect.left + 'px';
                sheetList.style.width = rect.width + 'px';
                sheetList.classList.add('show');
            }
        }

        function renderSheetTabs() {
            initializeCategories();
            
            const currentSheetNameEl = document.getElementById('currentSheetName');
            if (tableData.sheets[currentSheet]) {
                currentSheetNameEl.textContent = tableData.sheets[currentSheet].name;
            }

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
                    
                    // Handle markdown formatting and newlines
                    // IMPORTANT: When adding new markdown syntax, add detection here
                    // This must match the hasMarkdown check in static/script.js
                    const cellValue = row[colIndex] || '';
                    const hasMarkdown = cellValue.includes('**') || 
                        cellValue.includes('__') || 
                        cellValue.includes('@@') || 
                        cellValue.includes('##') || 
                        cellValue.includes('```') || 
                        cellValue.includes('`') || 
                        cellValue.includes('~~') || 
                        cellValue.includes('==') || 
                        cellValue.includes('^') || 
                        cellValue.includes('~') || 
                        cellValue.includes('{fg:') || 
                        cellValue.includes('{bg:') || 
                        cellValue.includes('{link:') || 
                        cellValue.includes('\\n- ') || 
                        cellValue.includes('\\n-- ') || 
                        cellValue.trim().startsWith('- ') || 
                        cellValue.trim().startsWith('-- ') ||
                        cellValue.trim().startsWith('|') ||
                        (cellValue.includes('|') && cellValue.split('|').length >= 2);
                    
                    if (hasMarkdown) {
                        // Apply markdown formatting
                        cellContent.innerHTML = parseMarkdown(cellValue);
                    } else if (cellValue.includes('\\n')) {
                        // Just handle newlines
                        cellContent.innerHTML = cellValue.replace(/\\n/g, '<br>');
                    } else {
                        cellContent.textContent = cellValue;
                    }
                    
                    cellContent.style.color = col.textColor || '#000000';

                    if (col.font && col.font !== '') {
                        cellContent.style.fontFamily = `'${col.font}', monospace`;
                    }
                    
                    if (col.fontSize && col.fontSize !== '') {
                        cellContent.style.fontSize = col.fontSize + 'px';
                    }

                    // Apply cell-specific styles
                    const cellStyle = (sheet.cellStyles || {})[`${rowIndex}-${colIndex}`] || {};
                    if (cellStyle.bold) cellContent.style.fontWeight = 'bold';
                    if (cellStyle.italic) cellContent.style.fontStyle = 'italic';
                    if (cellStyle.center) cellContent.style.textAlign = 'center';
                    
                    // Handle borders properly
                    if (cellStyle.border === true) {
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

        function stripMarkdown(text) {
            if (!text) return '';
            let stripped = String(text);
            // Remove bold markers: **text** -> text
            stripped = stripped.replace(/\\*\\*(.+?)\\*\\*/g, '$1');
            // Remove bullet markers: - item -> item
            stripped = stripped.replace(/^\\s*-\\s+/gm, '');
            return stripped;
        }

        /**
         * Parse markdown syntax and convert to HTML
         * 
         * IMPORTANT: When adding new markdown syntax, add regex replacement here
         * This must match the parseMarkdown() function in static/script.js
         * 
         * Supported syntax:
         * - **bold** -> <strong>
         * - @@italic@@ -> <em>
         * - __underline__ -> <u>
         * - ~~strikethrough~~ -> <del>
         * - ^superscript^ -> <sup>
         * - ~subscript~ -> <sub>
         * - ##heading## -> larger text
         * - `code` -> <code>
         * - ==highlight== -> <mark>
         * - {link:url}text{/} -> clickable link
         * - {fg:color}text{/} or {bg:color}text{/} or {fg:color;bg:color}text{/} -> colored text
         * - - item -> bullet list
         * - -- subitem -> sub-bullet list
         * - 1. item -> numbered list
         * - ``` code block ```
         */
        /* ----------  PIPE-TABLE → CSS-GRID  ---------- */
        function parseGridTable(lines) {
            const rows = lines.map(l =>
                l.trim().replace(/^\\|\\|$/g, '').split('|').map(c => c.trim()));
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
                    html += `<div class="md-cell ${i ? '' : 'md-header'}"${alignStyle}>${cell.content}</div>`;
                });
            });
            html += '</div>';
            return html;
        }

        /*  inline parser for table cells - supports all markdown except lists  */
        function parseMarkdownInline(text) {
            let formatted = text;

            // Links: {link:url}text{/} -> <a href="url">text</a>
            formatted = formatted.replace(/\\{link:([^}]+)\\}(.+?)\\{\\/\\}/g, (match, url, text) => {
                return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
            });

            // Custom colors: {fg:color;bg:color}text{/} or {fg:color}text{/} or {bg:color}text{/}
            formatted = formatted.replace(/\\{((?:fg:[^;\\}\\s]+)?(?:;)?(?:bg:[^;\\}\\s]+)?)\\}(.+?)\\{\\/\\}/g, (match, styles, text) => {
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
                    styleObj.padding = '2px 6px';
                    styleObj.borderRadius = '4px';
                }
                // Only use extra spacing if there's a background color
                styleObj.lineHeight = hasBg ? '1.8' : '1.3';
                styleObj.boxDecorationBreak = 'clone';
                styleObj.WebkitBoxDecorationBreak = 'clone';
                const styleStr = Object.entries(styleObj).map(([k, v]) => {
                    const cssKey = k.replace(/([A-Z])/g, '-$1').toLowerCase();
                    return cssKey + ': ' + v;
                }).join('; ');
                return '<span style="' + styleStr + '">' + text + '</span>';
            });

            // Heading: ##text## -> larger text
            formatted = formatted.replace(/##(.+?)##/g, '<span style="font-size: 1.3em; font-weight: 600;">$1</span>');

            // Bold: **text** -> <strong>text</strong>
            formatted = formatted.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');

            // Italic: @@text@@ -> <em>text</em>
            formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

            // Underline: __text__ -> <u>text</u>
            formatted = formatted.replace(/__(.+?)__/g, '<u>$1</u>');

            // Strikethrough: ~~text~~ -> <del>text</del>
            formatted = formatted.replace(/~~(.+?)~~/g, '<del>$1</del>');

            // Superscript: ^text^ -> <sup>text</sup>
            formatted = formatted.replace(/\\^(.+?)\\^/g, '<sup>$1</sup>');

            // Subscript: ~text~ -> <sub>text</sub>
            formatted = formatted.replace(/~(.+?)~/g, '<sub>$1</sub>');

            // Inline code: `text` -> <code>text</code>
            formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');

            // Highlight: ==text== -> <mark>text</mark>
            formatted = formatted.replace(/==(.+?)==/g, '<mark>$1</mark>');

            return formatted;
        }

        function oldParseMarkdownBody(lines) {
            /* copy the *body* of the existing parser (bold, italic, lists …)
               but skip the table-splitting logic we just added. */
            let txt = lines.join('\\n');

            // Handle code blocks first (multiline)
            let inCodeBlock = false;
            const codeLines = txt.split('\\n');
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

                // Links: {link:url}text{/} -> <a href="url">text</a>
                formatted = formatted.replace(/\\{link:([^}]+)\\}(.+?)\\{\\/\\}/g, (match, url, text) => {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
                });

                // Custom colors: {fg:color;bg:color}text{/} or {fg:color}text{/} or {bg:color}text{/}
                formatted = formatted.replace(/\\{((?:fg:[^;\\}\\s]+)?(?:;)?(?:bg:[^;\\}\\s]+)?)\\}(.+?)\\{\\/\\}/g, (match, styles, text) => {
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
                        styleObj.padding = '2px 6px';
                        styleObj.borderRadius = '4px';
                    }
                    // Only use extra spacing if there's a background color
                    styleObj.lineHeight = hasBg ? '1.8' : '1.3';
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

                // Bold: **text** -> <strong>text</strong>
                formatted = formatted.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');

                // Italic: @@text@@ -> <em>text</em>
                formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

                // Underline: __text__ -> <u>text</u>
                formatted = formatted.replace(/__(.+?)__/g, '<u>$1</u>');

                // Strikethrough: ~~text~~ -> <del>text</del>
                formatted = formatted.replace(/~~(.+?)~~/g, '<del>$1</del>');

                // Superscript: ^text^ -> <sup>text</sup>
                formatted = formatted.replace(/\\^(.+?)\\^/g, '<sup>$1</sup>');

                // Subscript: ~text~ -> <sub>text</sub> (single tilde only, after strikethrough is processed)
                formatted = formatted.replace(/~(.+?)~/g, '<sub>$1</sub>');

                // Sublist: -- item -> ◦ item with more indent (white circle)
                if (formatted.trim().startsWith('-- ')) {
                    const content = formatted.replace(/^(\\s*)-- (.+)$/, '$2');
                    formatted = formatted.replace(/^(\\s*)-- .+$/, '$1<span style="display: inline-flex; align-items: flex-start; width: 100%; margin-left: 1em;"><span style="margin-right: 0.5em; flex-shrink: 0; line-height: 1; font-size: 0.9em; position: relative; top: 0.35em;">◦</span><span style="flex: 1;">◦CONTENT◦</span></span>');
                    formatted = formatted.replace('◦CONTENT◦', content);
                }
                // Bullet list: - item -> • item with hanging indent (black circle)
                else if (formatted.trim().startsWith('- ')) {
                    const content = formatted.replace(/^(\\s*)- (.+)$/, '$2');
                    formatted = formatted.replace(/^(\\s*)- .+$/, '$1<span style="display: inline-flex; align-items: flex-start; width: 100%;"><span style="margin-right: 0.5em; flex-shrink: 0; line-height: 1; font-size: 0.9em; position: relative; top: 0.35em;">•</span><span style="flex: 1;">•CONTENT•</span></span>');
                    formatted = formatted.replace('•CONTENT•', content);
                }

                // Numbered list: 1. item -> 1. item with hanging indent
                if (/^\\d+\\.\\s/.test(formatted.trim())) {
                    const match = formatted.match(/^(\\s*)(\\d+\\.\\s)(.+)$/);
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

                return formatted;
            });

            return formattedLines.join('<br>');
        }

        function parseMarkdown(text) {
            if (!text) return '';

            /* -----  GRID-TABLE DETECTION  ----- */
            const lines = text.split('\\n');
            
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
                ).join('<br>');
            }

            // If no grid table, process as normal markdown
            return oldParseMarkdownBody(lines);
        }

        function searchTable() {
            const searchInput = document.getElementById('searchInput');
            const searchTerm = searchInput.value.toLowerCase().trim();
            const table = document.getElementById('dataTable');
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');

            // Remove previous highlights
            document.querySelectorAll('.search-highlight').forEach(el => {
                el.classList.remove('search-highlight');
            });

            if (!searchTerm) {
                // Show all rows if search is empty
                rows.forEach(row => {
                    row.style.display = '';
                });
                return;
            }

            let foundCount = 0;

            rows.forEach(row => {
                const cells = row.querySelectorAll('td:not(.row-number)');
                let rowMatches = false;

                cells.forEach(cell => {
                    const cellContent = cell.querySelector('.cell-content');
                    if (cellContent) {
                        const cellValue = cellContent.textContent.toLowerCase();
                        // Strip markdown for searching
                        const strippedValue = stripMarkdown(cellValue);

                        if (strippedValue.includes(searchTerm)) {
                            rowMatches = true;
                            cell.classList.add('search-highlight');
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
        }

        function clearSearch() {
            const searchInput = document.getElementById('searchInput');
            searchInput.value = '';
            searchTable(); // This will show all rows and remove highlights
        }

        function toggleRowWrap() {
            const wrapToggle = document.getElementById('wrapToggle');
            const table = document.getElementById('dataTable');
            
            if (wrapToggle.checked) {
                table.classList.add('wrap-enabled');
                localStorage.setItem('rowWrapEnabled', 'true');
                
                // Convert all text content to wrapped display
                const cells = table.querySelectorAll('td:not(.row-number) .cell-content');
                cells.forEach(cellContent => {
                    const text = cellContent.textContent || cellContent.innerHTML;
                    if (text && text.length > 0) {
                        // Check if content needs wrapping (longer than typical cell width)
                        const tempSpan = document.createElement('span');
                        tempSpan.style.visibility = 'hidden';
                        tempSpan.style.position = 'absolute';
                        tempSpan.style.whiteSpace = 'nowrap';
                        tempSpan.textContent = text;
                        document.body.appendChild(tempSpan);
                        
                        const textWidth = tempSpan.offsetWidth;
                        const cellWidth = cellContent.closest('td').offsetWidth;
                        
                        document.body.removeChild(tempSpan);
                        
                        if (textWidth > cellWidth - 20) { // 20px padding
                            cellContent.closest('tr').classList.add('has-wrapped-content');
                        }
                    }
                });
            } else {
                table.classList.remove('wrap-enabled');
                localStorage.setItem('rowWrapEnabled', 'false');
                
                // Remove wrapped content classes
                const rows = table.querySelectorAll('tr.has-wrapped-content');
                rows.forEach(row => row.classList.remove('has-wrapped-content'));
            }
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
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
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const sheetSelector = document.querySelector('.sheet-selector');
            const sheetList = document.getElementById('sheetList');
            if (!sheetSelector.contains(event.target)) {
                sheetList.classList.remove('show');
            }
        });

        function toggleRowNumbers() {
            const rowToggle = document.getElementById('rowToggle');
            const table = document.getElementById('dataTable');

            if (rowToggle.checked) {
                table.classList.remove('hide-row-numbers');
                localStorage.setItem('rowNumbersVisible', 'true');
            } else {
                table.classList.add('hide-row-numbers');
                localStorage.setItem('rowNumbersVisible', 'false');
            }
        }

        let fontSizeScale = parseFloat(localStorage.getItem('fontSizeScale')) || 1.0;

        function adjustFontSize(delta) {
            fontSizeScale += delta * 0.1;
            fontSizeScale = Math.max(0.5, Math.min(2.0, fontSizeScale)); // Limit between 50% and 200%
            
            localStorage.setItem('fontSizeScale', fontSizeScale);
            
            // Update display
            document.getElementById('fontSizeDisplay').textContent = Math.round(fontSizeScale * 100) + '%';
            
            // Apply to all cell content
            const cells = document.querySelectorAll('.cell-content');
            cells.forEach(cell => {
                const currentFontSize = parseFloat(window.getComputedStyle(cell).fontSize);
                const baseFontSize = currentFontSize / (parseFloat(cell.dataset.fontScale) || 1.0);
                cell.style.fontSize = (baseFontSize * fontSizeScale) + 'px';
                cell.dataset.fontScale = fontSizeScale;
            });
        }

        function applyFontSizeScale() {
            const cells = document.querySelectorAll('.cell-content');
            cells.forEach(cell => {
                const currentFontSize = parseFloat(window.getComputedStyle(cell).fontSize);
                if (currentFontSize && fontSizeScale !== 1.0) {
                    cell.style.fontSize = (currentFontSize * fontSizeScale) + 'px';
                    cell.dataset.fontScale = fontSizeScale;
                }
            });
            document.getElementById('fontSizeDisplay').textContent = Math.round(fontSizeScale * 100) + '%';
        }

        // Initialize on load
        window.onload = function() {
            initializeCategories();
            renderCategoryTabs();
            renderSheetTabs();
            renderTable();
            
            // Restore wrap toggle state
            const wrapEnabled = localStorage.getItem('rowWrapEnabled') === 'true';
            const wrapToggle = document.getElementById('wrapToggle');
            if (wrapToggle) {
                wrapToggle.checked = wrapEnabled;
                if (wrapEnabled) {
                    document.getElementById('dataTable').classList.add('wrap-enabled');
                }
            }
            
            // Restore row numbers toggle state
            const rowNumbersVisible = localStorage.getItem('rowNumbersVisible') !== 'false'; // Default true
            const rowToggle = document.getElementById('rowToggle');
            if (rowToggle) {
                rowToggle.checked = rowNumbersVisible;
                if (!rowNumbersVisible) {
                    document.getElementById('dataTable').classList.add('hide-row-numbers');
                }
            }
            
            // Apply saved font size scale
            setTimeout(() => {
                applyFontSizeScale();
            }, 100);
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="sheet-tabs">
            <div class="category-controls">
                <div class="category-selector">
                    <button class="category-current" id="currentCategoryBtn" onclick="toggleCategoryList()">
                        <span id="currentCategoryName">Uncategorized</span>
                        <span class="dropdown-arrow">▼</span>
                    </button>
                    <div class="category-list" id="categoryList"></div>
                </div>
            </div>

            <div class="sheet-controls">
                <div class="sheet-selector">
                    <button class="sheet-current" id="currentSheetBtn" onclick="toggleSheetList()">
                        <span id="currentSheetName">''' + (sheets[active_sheet]['name'] if sheets and active_sheet < len(sheets) else 'Sheet1') + '''</span>
                        <span class="dropdown-arrow">▼</span>
                    </button>
                    <div class="sheet-list" id="sheetList"></div>
                </div>
            </div>

            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search..." onkeyup="searchTable()" title="Search in all cells">
                <button onclick="clearSearch()" class="btn-clear-search" title="Clear search">×</button>
            </div>

            <div class="button-group">
                <label class="btn-icon-toggle" title="Enable text wrapping - Press Enter for new lines">
                    <input type="checkbox" id="wrapToggle" onchange="toggleRowWrap()">
                    <span>↩️</span>
                </label>
                
                <label class="btn-icon-toggle" title="Show or hide row numbers">
                    <input type="checkbox" id="rowToggle" onchange="toggleRowNumbers()" checked>
                    <span>#️⃣</span>
                </label>
            </div>

            <div class="font-size-control">
                <span class="font-size-label">Font:</span>
                <button onclick="adjustFontSize(-1)" class="btn-font-size" title="Decrease font size">−</button>
                <span id="fontSizeDisplay" class="font-size-display">100%</span>
                <button onclick="adjustFontSize(1)" class="btn-font-size" title="Increase font size">+</button>
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