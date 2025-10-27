let tableData = { sheets: [], activeSheet: 0, categories: [], sheetCategories: {} };
let currentSheet = 0;
let currentCategory = null; // null means "Uncategorized"
let contextMenuCell = null;
let selectedCells = []; // Array of {row, col, td} objects for multi-cell operations
let isSelecting = false;
let sheetHistory = []; // Track recently visited sheets for Alt+M toggle

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

    // Initialize font size scale
    setTimeout(() => {
        applyFontSizeScale();
    }, 100);
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

    // F1 to open quick navigation popup
    if (e.key === 'F1') {
        e.preventDefault();
        openF1Popup();
    }

    // Escape to close F1 popup
    if (e.key === 'Escape' && document.getElementById('f1Popup').classList.contains('show')) {
        closeF1Popup();
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
    document.getElementById('columnFontSize').value = '14';
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
    document.getElementById('columnFontSize').value = col.fontSize || '14';

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
            const newRowIndex = sheet.rows.length - 1;
            renderTable();

            // Scroll to and focus on the new row
            setTimeout(() => {
                const table = document.getElementById('dataTable');
                const tbody = table.querySelector('tbody');
                const rows = tbody.querySelectorAll('tr');
                const newRow = rows[newRowIndex];

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
 * 1. Add the detection pattern here in hasMarkdown check
 * 2. Add the parsing logic in parseMarkdown() function
 * 3. Update the detection in renderTable() function (search for "Apply markdown formatting to all cells")
 * 4. Update the Markdown Guide modal in templates/index.html
 * 5. Add CSS styling if needed in static/style.css
 */
function applyMarkdownFormatting(rowIndex, colIndex, value) {
    // Find the cell element
    const table = document.getElementById('dataTable');
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    if (!rows[rowIndex]) return;

    const cells = rows[rowIndex].querySelectorAll('td:not(.row-number)');
    if (!cells[colIndex]) return;

    const cell = cells[colIndex];
    const inputElement = cell.querySelector('input, textarea');
    if (!inputElement) return;

    // Parse markdown-style formatting
    const hasMarkdown = value && (
        value.includes('**') ||
        value.includes('__') ||
        value.includes('@@') ||
        value.includes('##') ||
        value.includes('```') ||
        value.includes('`') ||
        value.includes('~~') ||
        value.includes('==') ||
        value.includes('^') ||
        value.includes('~') ||
        value.includes('{fg:') ||
        value.includes('{bg:') ||
        value.includes('\n- ') ||
        value.includes('\n-- ') ||
        value.trim().startsWith('- ') ||
        value.trim().startsWith('-- ')
    );

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

        // Copy ALL styles from input/textarea and cell
        const computedInput = window.getComputedStyle(inputElement);
        const computedCell = window.getComputedStyle(cell);

        preview.style.color = inputElement.style.color || computedInput.color;
        preview.style.fontFamily = inputElement.style.fontFamily || computedInput.fontFamily;
        preview.style.fontSize = inputElement.style.fontSize || computedInput.fontSize;
        preview.style.fontWeight = inputElement.style.fontWeight || computedInput.fontWeight;
        preview.style.fontStyle = inputElement.style.fontStyle || computedInput.fontStyle;
        preview.style.textAlign = inputElement.style.textAlign || computedInput.textAlign;

        // Copy background from cell (not input, as input is transparent)
        preview.style.backgroundColor = computedCell.backgroundColor;

        cell.style.position = 'relative';
        cell.appendChild(preview);
    } else {
        delete inputElement.dataset.formattedHtml;
        inputElement.classList.remove('has-markdown');
    }
}

/**
 * Parse markdown syntax and convert to HTML
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
 * - {fg:color}text{/} or {bg:color}text{/} or {fg:color;bg:color}text{/} -> colored text
 * - - item -> bullet list
 * - -- subitem -> sub-bullet list
 * - 1. item -> numbered list
 * - ``` code block ```
 */
function parseMarkdown(text) {
    if (!text) return '';

    // Handle code blocks first (multiline)
    let inCodeBlock = false;
    const lines = text.split('\n');
    const formattedLines = lines.map(line => {
        let formatted = line;

        // Code block: ```text``` -> <code>text</code>
        if (formatted.trim() === '```') {
            inCodeBlock = !inCodeBlock;
            return ''; // Remove the ``` markers
        }

        if (inCodeBlock) {
            return `<code>${formatted}</code>`;
        }

        // Custom colors: {fg:color;bg:color}text{/} or {fg:color}text{/} or {bg:color}text{/}
        formatted = formatted.replace(/\{((?:fg:[^;}\s]+)?(?:;)?(?:bg:[^;}\s]+)?)\}(.+?)\{\/\}/g, (match, styles, text) => {
            const styleObj = {};
            const parts = styles.split(';').filter(p => p.trim());
            parts.forEach(part => {
                const [key, value] = part.split(':').map(s => s.trim());
                if (key === 'fg') styleObj.color = value;
                if (key === 'bg') styleObj.backgroundColor = value;
            });
            // Add padding and border-radius for better appearance
            styleObj.padding = '2px 6px';
            styleObj.borderRadius = '4px';
            styleObj.display = 'inline-block';
            const styleStr = Object.entries(styleObj).map(([k, v]) => {
                const cssKey = k.replace(/([A-Z])/g, '-$1').toLowerCase();
                return `${cssKey}: ${v}`;
            }).join('; ');
            return `<span style="${styleStr}">${text}</span>`;
        });

        // Heading: ##text## -> larger text
        formatted = formatted.replace(/##(.+?)##/g, '<span style="font-size: 1.3em; font-weight: 600;">$1</span>');

        // Bold: **text** -> <strong>text</strong>
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic: @@text@@ -> <em>text</em>
        formatted = formatted.replace(/@@(.+?)@@/g, '<em>$1</em>');

        // Underline: __text__ -> <u>text</u>
        formatted = formatted.replace(/__(.+?)__/g, '<u>$1</u>');

        // Strikethrough: ~~text~~ -> <del>text</del> (process first to avoid conflict with subscript)
        formatted = formatted.replace(/~~(.+?)~~/g, '<del>$1</del>');

        // Superscript: ^text^ -> <sup>text</sup>
        formatted = formatted.replace(/\^(.+?)\^/g, '<sup>$1</sup>');

        // Subscript: ~text~ -> <sub>text</sub> (single tilde only, after strikethrough is processed)
        formatted = formatted.replace(/~([^~\s]+?)~/g, '<sub>$1</sub>');

        // Sublist: -- item -> ◦ item with more indent (white circle)
        if (formatted.trim().startsWith('-- ')) {
            const content = formatted.replace(/^(\s*)-- (.+)$/, '$2');
            formatted = formatted.replace(/^(\s*)-- .+$/, '$1<span style="display: inline-flex; align-items: flex-start; width: 100%; margin-left: 1em;"><span style="margin-right: 0.5em; flex-shrink: 0;">◦</span><span style="flex: 1;">◦CONTENT◦</span></span>');
            formatted = formatted.replace('◦CONTENT◦', content);
        }
        // Bullet list: - item -> • item with hanging indent (black circle)
        else if (formatted.trim().startsWith('- ')) {
            const content = formatted.replace(/^(\s*)- (.+)$/, '$2');
            formatted = formatted.replace(/^(\s*)- .+$/, '$1<span style="display: inline-flex; align-items: flex-start; width: 100%;"><span style="margin-right: 0.5em; flex-shrink: 0;">•</span><span style="flex: 1;">•CONTENT•</span></span>');
            formatted = formatted.replace('•CONTENT•', content);
        }

        // Numbered list: 1. item -> 1. item with hanging indent
        if (/^\d+\.\s/.test(formatted.trim())) {
            const match = formatted.match(/^(\s*)(\d+\.\s)(.+)$/);
            if (match) {
                const spaces = match[1];
                const number = match[2];
                const content = match[3];
                formatted = `${spaces}<span style="display: inline-flex; align-items: flex-start; width: 100%;"><span style="margin-right: 0.5em; flex-shrink: 0;">${number}</span><span style="flex: 1;">NUMCONTENT</span></span>`;
                formatted = formatted.replace('NUMCONTENT', content);
            }
        }

        // Inline code: `text` -> <code>text</code>
        formatted = formatted.replace(/`(.+?)`/g, '<code>$1</code>');

        // Highlight: ==text== -> <mark>text</mark>
        formatted = formatted.replace(/==(.+?)==/g, '<mark>$1</mark>');

        return formatted;
    });

    return formattedLines.join('\n');
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

                    cellTd.style.border = '1px solid #ddd';

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
    // Track sheet history for Alt+M toggle
    if (currentSheet !== index) {
        // Remove the index if it already exists in history
        sheetHistory = sheetHistory.filter(i => i !== index);
        // Add current sheet to history before switching
        if (sheetHistory[sheetHistory.length - 1] !== currentSheet) {
            sheetHistory.push(currentSheet);
        }
        // Keep only last 2 sheets in history
        if (sheetHistory.length > 2) {
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
    document.getElementById('sheetName').value = tableData.sheets[index].name;
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
    document.getElementById('settingsModal').style.display = 'block';
}

// Category Management Functions
function toggleCategoryList() {
    const categoryList = document.getElementById('categoryList');
    categoryList.classList.toggle('show');
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
            const input = cell.querySelector('input, textarea');
            if (input) {
                const cellValue = input.value.toLowerCase();
                // Strip markdown for searching
                const strippedValue = stripMarkdown(cellValue);

                if (strippedValue.includes(searchTerm)) {
                    rowMatches = true;
                    cell.classList.add('search-highlight');

                    // Also highlight markdown preview if it exists
                    const preview = cell.querySelector('.markdown-preview');
                    if (preview) {
                        preview.classList.add('search-highlight');
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
    if (searchTerm && foundCount === 0) {
        showToast('No results found', 'info');
    } else if (searchTerm) {
        showToast(`Found ${foundCount} row(s)`, 'success');
    }
}

function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    searchInput.value = '';
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

function autoResizeTextarea(textarea) {
    // Skip if it's a merged cell textarea
    if (textarea.closest('td.merged-cell')) {
        return;
    }

    // Reset height to measure actual content
    textarea.style.height = 'auto';

    // Get the actual content height
    const scrollHeight = textarea.scrollHeight;
    const minHeight = 22; // Match input height exactly

    // Set height based on content
    const newHeight = Math.max(minHeight, scrollHeight);
    textarea.style.height = newHeight + 'px';

    // Mark the row if it has expanded content
    const tr = textarea.closest('tr');
    if (tr) {
        // Check if any textarea in this row actually needs more height
        const hasExpandedContent = Array.from(tr.querySelectorAll('textarea:not(.merged-cell textarea)')).some(ta => {
            ta.style.height = 'auto';
            const needsHeight = ta.scrollHeight > minHeight + 2; // Small threshold
            ta.style.height = Math.max(minHeight, ta.scrollHeight) + 'px';
            return needsHeight;
        });

        if (hasExpandedContent) {
            tr.classList.add('has-wrapped-content');
        } else {
            tr.classList.remove('has-wrapped-content');
        }
    }
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

            // Check if wrap is enabled
            const wrapEnabled = localStorage.getItem('rowWrapEnabled') === 'true';
            const isTextType = col.type === 'text' || !col.type;

            let inputElement;
            const cellValue = row[colIndex] || '';

            if (wrapEnabled && isTextType) {
                // Create textarea for wrapping
                inputElement = document.createElement('textarea');
                inputElement.rows = 1;
                // Preserve newlines in the value
                inputElement.value = cellValue;
                inputElement.style.color = col.textColor || '#000000';

                if (col.font && col.font !== '') {
                    inputElement.style.fontFamily = `'${col.font}', monospace`;
                }

                if (col.fontSize && col.fontSize !== '') {
                    inputElement.style.fontSize = col.fontSize + 'px';
                }

                inputElement.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);
                inputElement.oninput = (e) => {
                    autoResizeTextarea(e.target);
                    updateCell(rowIndex, colIndex, e.target.value);
                };

                // Mark td as having textarea for vertical alignment
                td.classList.add('has-textarea');
            } else {
                // Create regular input
                inputElement = document.createElement('input');
                inputElement.type = col.type;
                // Store the original value (with newlines) in dataset for later restoration
                inputElement.value = cellValue;
                inputElement.dataset.originalValue = cellValue;
                inputElement.style.color = col.textColor || '#000000';

                if (col.font && col.font !== '') {
                    inputElement.style.fontFamily = `'${col.font}', monospace`;
                }

                if (col.fontSize && col.fontSize !== '') {
                    inputElement.style.fontSize = col.fontSize + 'px';
                }

                inputElement.onchange = (e) => {
                    updateCell(rowIndex, colIndex, e.target.value);
                    // Update the stored original value
                    e.target.dataset.originalValue = e.target.value;
                };
            }

            const input = inputElement;

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

                    // Mark row as having wrapped content if it has merged cells
                    tr.classList.add('has-wrapped-content');

                    // Use textarea for merged cells
                    const textarea = document.createElement('textarea');
                    textarea.value = row[colIndex] || '';
                    textarea.style.color = col.textColor || '#000000';

                    // Ensure textarea preserves whitespace and line breaks
                    textarea.style.whiteSpace = 'pre-wrap';
                    textarea.style.wordWrap = 'break-word';

                    if (col.font && col.font !== '') {
                        textarea.style.fontFamily = `'${col.font}', monospace`;
                    }

                    if (col.fontSize && col.fontSize !== '') {
                        textarea.style.fontSize = col.fontSize + 'px';
                    }

                    textarea.onchange = (e) => updateCell(rowIndex, colIndex, e.target.value);

                    // Also handle input event for real-time updates
                    textarea.oninput = (e) => updateCell(rowIndex, colIndex, e.target.value);

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

    // Auto-resize textareas if wrap is enabled
    if (localStorage.getItem('rowWrapEnabled') === 'true') {
        const textareas = tableBody.querySelectorAll('textarea:not(.merged-cell textarea)');
        textareas.forEach(textarea => autoResizeTextarea(textarea));
    }

    // Apply markdown formatting to all cells
    // IMPORTANT: When adding new markdown syntax, update this detection check
    // to match the one in applyMarkdownFormatting() function
    sheet.rows.forEach((row, rowIndex) => {
        row.forEach((cellValue, colIndex) => {
            if (cellValue && (
                cellValue.includes('**') ||
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
                cellValue.includes('\n- ') ||
                cellValue.trim().startsWith('- ')
            )) {
                applyMarkdownFormatting(rowIndex, colIndex, cellValue);
            }
        });
    });

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
    // Remove bold markers: **text** -> text
    stripped = stripped.replace(/\*\*(.+?)\*\*/g, '$1');
    // Remove bullet markers: - item -> item
    stripped = stripped.replace(/^\s*-\s+/gm, '');
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

    // Filter sheets by selected category (unless searching all categories)
    tableData.sheets.forEach((sheet, index) => {
        const sheetCategory = tableData.sheetCategories[index] || tableData.sheetCategories[String(index)];

        // If not searching all categories, check if sheet belongs to selected category
        if (!searchAllCategories) {
            if (selectedF1Category === null && sheetCategory) return;
            if (selectedF1Category !== null && sheetCategory !== selectedF1Category) return;
        }

        const item = document.createElement('div');
        item.className = 'f1-sheet-item' + (index === currentSheet ? ' active' : '');
        item.dataset.sheetIndex = index;

        // Show category name if searching all categories
        const categoryLabel = searchAllCategories && sheetCategory ? ` <span style="color: #999; font-size: 12px;">(${sheetCategory})</span>` : '';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'f1-sheet-name-wrapper';
        nameSpan.innerHTML = `
            <span class="f1-sheet-icon">📄</span>
            <span class="f1-sheet-name">${sheet.name}${categoryLabel}</span>
        `;
        nameSpan.onclick = () => switchToSheetFromF1(index);

        const actions = document.createElement('div');
        actions.className = 'f1-sheet-actions';
        
        const upBtn = document.createElement('button');
        upBtn.className = 'f1-sheet-action-btn';
        upBtn.innerHTML = '⬆️';
        upBtn.title = 'Move sheet up';
        upBtn.onclick = (e) => {
            e.stopPropagation();
            moveSheetUp(index);
            setTimeout(() => populateF1Sheets(searchAllCategories), 100);
        };
        
        const downBtn = document.createElement('button');
        downBtn.className = 'f1-sheet-action-btn';
        downBtn.innerHTML = '⬇️';
        downBtn.title = 'Move sheet down';
        downBtn.onclick = (e) => {
            e.stopPropagation();
            moveSheetDown(index);
            setTimeout(() => populateF1Sheets(searchAllCategories), 100);
        };

        actions.appendChild(upBtn);
        actions.appendChild(downBtn);
        
        item.appendChild(nameSpan);
        item.appendChild(actions);
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

function filterF1Sheets() {
    const searchInput = document.getElementById('f1SearchInput');
    let searchTerm = searchInput ? searchInput.value : '';

    // Check for special search prefixes
    if (searchTerm.startsWith('*')) {
        // Search all categories by sheet name
        const actualSearch = searchTerm.substring(1).toLowerCase();
        populateF1Sheets(true); // Show all sheets from all categories

        // Filter by name
        const sheetItems = document.querySelectorAll('.f1-sheet-item');
        sheetItems.forEach(item => {
            const sheetName = item.querySelector('.f1-sheet-name').textContent.toLowerCase();
            if (sheetName.includes(actualSearch)) {
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
        // Normal search - filter current category sheets by name
        populateF1Sheets(false); // Show sheets from selected category only

        const searchLower = searchTerm.toLowerCase();
        const sheetItems = document.querySelectorAll('.f1-sheet-item');
        sheetItems.forEach(item => {
            const sheetName = item.querySelector('.f1-sheet-name').textContent.toLowerCase();
            if (sheetName.includes(searchLower)) {
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
                // Click the first visible item
                item.click();
                break;
            }
        }
    }
    
    // Alt+Up to move category up (only when F1 is open)
    if (e.altKey && e.key === 'ArrowUp') {
        e.preventDefault();
        moveCategoryUpInF1();
    }
    
    // Alt+Down to move category down (only when F1 is open)
    if (e.altKey && e.key === 'ArrowDown') {
        e.preventDefault();
        moveCategoryDownInF1();
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
