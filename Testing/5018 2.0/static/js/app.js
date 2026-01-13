/**
 * Markdown-First Single-Column Sheet System
 * Main Application JavaScript
 */

// State
let appData = null;
let currentSheet = null;
let currentCategory = null;
let customSyntaxes = {};
let history = [];
let activeEditor = null;

// DOM Elements
const sidebar = document.getElementById('sidebar');
const categoryTree = document.getElementById('category-tree');
const sheetContainer = document.getElementById('sheet-container');
const sheetTitle = document.getElementById('sheet-title');

// Modals
const vaultModal = document.getElementById('vault-modal');
const historyModal = document.getElementById('history-modal');
const formatModal = document.getElementById('format-modal');
const mathModal = document.getElementById('math-modal');
const contextMenu = document.getElementById('context-menu');

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
    if (typeof IS_STATIC !== 'undefined' && IS_STATIC) {
        appData = STATIC_DATA;
    } else {
        await loadData();
        await loadCustomSyntaxes();
    }
    
    renderSidebar();
    
    // Load last sheet or first available
    const lastSheetId = appData.lastSheet;
    const sheet = findSheetById(lastSheetId);
    if (sheet) {
        selectSheet(sheet.sheet, sheet.category);
    } else if (appData.categories.length > 0 && appData.categories[0].sheets.length > 0) {
        selectSheet(appData.categories[0].sheets[0], appData.categories[0]);
    }
    
    setupEventListeners();
    setupKeyboardShortcuts();
    renderCustomSyntaxButtons();
}

async function loadData() {
    const res = await fetch('/api/data');
    appData = await res.json();
}

async function loadCustomSyntaxes() {
    try {
        const res = await fetch('/api/custom-syntaxes');
        customSyntaxes = await res.json();
    } catch (e) {
        customSyntaxes = {};
    }
}

async function saveData() {
    if (typeof IS_STATIC !== 'undefined' && IS_STATIC) return;
    await fetch('/api/data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appData)
    });
}

async function saveState() {
    if (typeof IS_STATIC !== 'undefined' && IS_STATIC) return;
    await fetch('/api/state', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            lastSheet: currentSheet?.id,
            lastCursor: appData.lastCursor
        })
    });
}

// Sidebar Rendering
function renderSidebar() {
    categoryTree.innerHTML = '';
    
    appData.categories.forEach(cat => {
        const catEl = document.createElement('div');
        catEl.className = 'category';
        catEl.dataset.id = cat.id;
        
        const header = document.createElement('div');
        header.className = 'category-header';
        header.innerHTML = `
            <span class="arrow">▼</span>
            <span class="category-name">${escapeHtml(cat.name)}</span>
            <span class="category-count">${cat.sheets.length}</span>
        `;
        
        header.addEventListener('click', () => {
            header.classList.toggle('collapsed');
            sheetList.style.display = header.classList.contains('collapsed') ? 'none' : 'flex';
        });
        
        header.addEventListener('contextmenu', (e) => showContextMenu(e, 'category', cat));
        
        const sheetList = document.createElement('div');
        sheetList.className = 'sheet-list';
        
        // Render parent sheets first, then sub-sheets
        const parentSheets = cat.sheets.filter(s => !s.parentId);
        parentSheets.forEach(sheet => {
            sheetList.appendChild(createSheetItem(sheet, cat));
            
            // Render sub-sheets
            const subSheets = cat.sheets.filter(s => s.parentId === sheet.id);
            subSheets.forEach(sub => {
                const subItem = createSheetItem(sub, cat);
                subItem.classList.add('sub-sheet');
                sheetList.appendChild(subItem);
            });
        });
        
        catEl.appendChild(header);
        catEl.appendChild(sheetList);
        categoryTree.appendChild(catEl);
    });
}

function createSheetItem(sheet, category) {
    const item = document.createElement('div');
    item.className = 'sheet-item';
    item.dataset.id = sheet.id;
    item.textContent = sheet.name;
    
    if (currentSheet && currentSheet.id === sheet.id) {
        item.classList.add('active');
    }
    
    item.addEventListener('click', () => selectSheet(sheet, category));
    item.addEventListener('contextmenu', (e) => showContextMenu(e, 'sheet', sheet, category));
    
    return item;
}

function selectSheet(sheet, category) {
    currentSheet = sheet;
    currentCategory = category;
    
    // Update sidebar active state
    document.querySelectorAll('.sheet-item').forEach(el => el.classList.remove('active'));
    const activeItem = document.querySelector(`.sheet-item[data-id="${sheet.id}"]`);
    if (activeItem) activeItem.classList.add('active');
    
    // Update title
    sheetTitle.textContent = sheet.name;
    
    // Add to history
    addToHistory(sheet, category);
    
    // Render rows
    renderSheet();
    
    // Save state
    appData.lastSheet = sheet.id;
    saveState();
}


function renderSheet() {
    sheetContainer.innerHTML = '';
    
    if (!currentSheet) return;
    
    currentSheet.rows.forEach((row, index) => {
        const block = createRowBlock(row, index);
        sheetContainer.appendChild(block);
    });
}

function createRowBlock(row, index) {
    const block = document.createElement('div');
    block.className = 'row-block';
    block.dataset.id = row.id;
    block.dataset.index = index;
    
    const wrapper = document.createElement('div');
    wrapper.className = 'row-wrapper';
    
    // Single contenteditable div - shows rendered when blurred, raw when focused
    const editor = document.createElement('div');
    editor.className = 'row-editor';
    editor.contentEditable = true;
    editor.dataset.placeholder = 'Type markdown here...';
    editor.innerHTML = parseMarkdown(row.content);
    editor._rawContent = row.content;
    
    const actions = document.createElement('div');
    actions.className = 'row-actions';
    actions.innerHTML = `
        <button class="move-up" title="Move Up">↑</button>
        <button class="move-down" title="Move Down">↓</button>
        <button class="delete-row" title="Delete">×</button>
    `;
    
    // Focus: switch to raw markdown with syntax visible
    editor.addEventListener('focus', () => {
        activeEditor = editor;
        editor.classList.add('editing');
        // Show raw content with syntax highlighting
        editor.innerHTML = highlightSyntax(editor._rawContent);
        // Restore cursor to end
        placeCaretAtEnd(editor);
    });
    
    // Blur: save and render back to preview
    editor.addEventListener('blur', () => {
        editor.classList.remove('editing');
        // Extract plain text (raw markdown)
        editor._rawContent = extractRawText(editor);
        row.content = editor._rawContent;
        // Render as preview
        editor.innerHTML = parseMarkdown(editor._rawContent);
        saveData();
    });
    
    // Input: update raw content and re-highlight
    editor.addEventListener('input', () => {
        if (editor.classList.contains('editing')) {
            editor._rawContent = extractRawText(editor);
            row.content = editor._rawContent;
            
            // Save cursor position
            const sel = window.getSelection();
            const offset = getCaretCharacterOffset(editor);
            
            // Re-highlight
            editor.innerHTML = highlightSyntax(editor._rawContent);
            
            // Restore cursor
            setCaretPosition(editor, offset);
        }
    });
    
    editor.addEventListener('keydown', (e) => handleEditorKeydown(e, row, index, editor));
    
    // Action buttons
    actions.querySelector('.move-up').addEventListener('click', () => moveRow(index, -1));
    actions.querySelector('.move-down').addEventListener('click', () => moveRow(index, 1));
    actions.querySelector('.delete-row').addEventListener('click', () => deleteRow(index));
    
    wrapper.appendChild(editor);
    block.appendChild(wrapper);
    block.appendChild(actions);
    
    return block;
}

// Syntax highlighting for edit mode - shows markers but keeps same visual styling as preview
function highlightSyntax(text) {
    if (!text) return '';
    
    let html = escapeHtml(text);
    
    // Headings - same size as preview, markers visible
    html = html.replace(/^(###)\s(.+)$/gm, '<span class="md-h3"><span class="syn-marker">$1 </span>$2</span>');
    html = html.replace(/^(##)\s(.+)$/gm, '<span class="md-h2"><span class="syn-marker">$1 </span>$2</span>');
    html = html.replace(/^(#)\s(.+)$/gm, '<span class="md-h1"><span class="syn-marker">$1 </span>$2</span>');
    
    // Big text #2#text#/# - keep the size
    html = html.replace(/(#(\d)#)(.+?)(#\/#)/g, (m, open, size, content, close) => {
        return `<span class="md-big" style="font-size: ${size}em;"><span class="syn-marker">${open}</span>${content}<span class="syn-marker">${close}</span></span>`;
    });
    
    // Box #B#content#/#
    html = html.replace(/(#B#)(.+?)(#\/#)/gs, '<span class="md-box"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Bold **text**
    html = html.replace(/(\*\*)(.+?)(\*\*)/g, '<span class="md-bold"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Italic @@text@@
    html = html.replace(/(@@)(.+?)(@@)/g, '<span class="md-italic"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Underline __text__
    html = html.replace(/(__)(.+?)(__)/g, '<span class="md-underline"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Strikethrough ~~text~~
    html = html.replace(/(~~)(.+?)(~~)/g, '<span class="md-strike"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Small text ..text..
    html = html.replace(/(\.\.)(.+?)(\.\.)/g, '<span class="md-small"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Superscript ^text^
    html = html.replace(/(\^)([^\^]+)(\^)/g, '<span class="md-sup"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Subscript ~text~
    html = html.replace(/(?<!~)(~)([^~]+)(~)(?!~)/g, '<span class="md-sub"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Highlights - same colors as preview
    html = html.replace(/(==)(.+?)(==)/g, '<span class="md-hl-yellow"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    html = html.replace(/(!!)(.+?)(!!)/g, '<span class="md-hl-red"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    html = html.replace(/(\?\?)(.+?)(\?\?)/g, '<span class="md-hl-blue"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Custom syntaxes - same styling as preview
    for (const [marker, config] of Object.entries(customSyntaxes)) {
        const escaped = escapeRegex(marker);
        const regex = new RegExp(`(${escaped})(.+?)(${escaped})`, 'g');
        const style = buildCustomStyle(config);
        html = html.replace(regex, `<span class="md-custom" style="${style}"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>`);
    }
    
    // Math \( ... \) - show raw latex but styled
    html = html.replace(/(\\\()(.+?)(\\\))/g, '<span class="syn-math-wrap"><span class="syn-marker">$1</span><span class="syn-math">$2</span><span class="syn-marker">$3</span></span>');
    
    // Collapsible {{ }}
    html = html.replace(/(\{\{)(.+?)(\}\})/gs, '<span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span>');
    
    // Answer [[ ]]
    html = html.replace(/(\[\[)(.+?)(\]\])/g, '<span class="md-answer"><span class="syn-marker">$1</span>$2<span class="syn-marker">$3</span></span>');
    
    // Lists - keep indentation
    html = html.replace(/^(---)\s+(.+)$/gm, '<span class="md-list" style="padding-left:3em;"><span class="syn-marker">$1 </span><span class="md-list-item">$2</span></span>');
    html = html.replace(/^(--)(?!-)\s+(.+)$/gm, '<span class="md-list" style="padding-left:2em;"><span class="syn-marker">$1 </span><span class="md-list-item">$2</span></span>');
    html = html.replace(/^(-)(?!-)\s+(.+)$/gm, '<span class="md-list"><span class="syn-marker">$1 </span><span class="md-list-item">$2</span></span>');
    
    // Separators
    html = html.replace(/^([RGBYPO])?(-{3,})([RGBYPO])?$/gm, (match, c1, dashes, c2) => {
        const colors = { R: '#ef4444', G: '#22c55e', B: '#3b82f6', Y: '#eab308', P: '#a855f7', O: '#f97316' };
        const color = colors[c1] || colors[c2] || 'var(--border)';
        return `<span class="syn-marker">${c1 || ''}${dashes}${c2 || ''}</span><hr class="md-separator" style="background: ${color};">`;
    });
    
    // Preserve line breaks
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

// Extract raw text from contenteditable
function extractRawText(element) {
    let text = '';
    const walk = (node) => {
        if (node.nodeType === Node.TEXT_NODE) {
            text += node.textContent;
        } else if (node.nodeName === 'BR') {
            text += '\n';
        } else if (node.nodeName === 'DIV' && text.length > 0 && !text.endsWith('\n')) {
            text += '\n';
            node.childNodes.forEach(walk);
        } else {
            node.childNodes.forEach(walk);
        }
    };
    walk(element);
    return text;
}

// Caret position helpers for contenteditable
function getCaretCharacterOffset(element) {
    let caretOffset = 0;
    const sel = window.getSelection();
    if (sel.rangeCount > 0) {
        const range = sel.getRangeAt(0);
        const preCaretRange = range.cloneRange();
        preCaretRange.selectNodeContents(element);
        preCaretRange.setEnd(range.endContainer, range.endOffset);
        caretOffset = preCaretRange.toString().length;
    }
    return caretOffset;
}

function setCaretPosition(element, offset) {
    const range = document.createRange();
    const sel = window.getSelection();
    let currentOffset = 0;
    let found = false;
    
    const walk = (node) => {
        if (found) return;
        if (node.nodeType === Node.TEXT_NODE) {
            if (currentOffset + node.length >= offset) {
                range.setStart(node, offset - currentOffset);
                range.collapse(true);
                found = true;
            } else {
                currentOffset += node.length;
            }
        } else {
            for (const child of node.childNodes) {
                walk(child);
                if (found) break;
            }
        }
    };
    
    walk(element);
    
    if (!found) {
        // Place at end if offset exceeds content
        range.selectNodeContents(element);
        range.collapse(false);
    }
    
    sel.removeAllRanges();
    sel.addRange(range);
}

function placeCaretAtEnd(element) {
    const range = document.createRange();
    const sel = window.getSelection();
    range.selectNodeContents(element);
    range.collapse(false);
    sel.removeAllRanges();
    sel.addRange(range);
}

function handleEditorKeydown(e, row, index, editor) {
    // Tab handling
    if (e.key === 'Tab') {
        e.preventDefault();
        document.execCommand('insertText', false, '\t');
    }
    
    // Ctrl+S to save
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveData();
    }
    
    // Alt+Up/Down to move row
    if (e.altKey && e.key === 'ArrowUp') {
        e.preventDefault();
        moveRow(index, -1);
    }
    if (e.altKey && e.key === 'ArrowDown') {
        e.preventDefault();
        moveRow(index, 1);
    }
    
    // Ctrl+D for duplicate
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        const sel = window.getSelection();
        const text = sel.toString() || getCurrentLine(editor);
        document.execCommand('insertText', false, text);
    }
}

function getCurrentLine(element) {
    const text = extractRawText(element);
    const offset = getCaretCharacterOffset(element);
    const before = text.substring(0, offset);
    const lineStart = before.lastIndexOf('\n') + 1;
    const lineEnd = text.indexOf('\n', offset);
    return text.substring(lineStart, lineEnd === -1 ? text.length : lineEnd);
}

function moveRow(index, direction) {
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= currentSheet.rows.length) return;
    
    const rows = currentSheet.rows;
    [rows[index], rows[newIndex]] = [rows[newIndex], rows[index]];
    
    renderSheet();
    saveData();
}

function deleteRow(index) {
    if (currentSheet.rows.length <= 1) return;
    currentSheet.rows.splice(index, 1);
    renderSheet();
    saveData();
}

function addRow() {
    const newRow = {
        id: `row_${Date.now()}`,
        content: ''
    };
    currentSheet.rows.push(newRow);
    renderSheet();
    saveData();
    
    // Focus the new row
    const editors = sheetContainer.querySelectorAll('.row-editor');
    if (editors.length > 0) {
        editors[editors.length - 1].focus();
    }
}

// Markdown Parser
function parseMarkdown(text) {
    if (!text) return '';
    
    let html = escapeHtml(text);
    
    // Headings (must be at start of line)
    html = html.replace(/^### (.+)$/gm, '<span class="md-h3">$1</span>');
    html = html.replace(/^## (.+)$/gm, '<span class="md-h2">$1</span>');
    html = html.replace(/^# (.+)$/gm, '<span class="md-h1">$1</span>');
    
    // Big text #2#text#/#
    html = html.replace(/#(\d)#(.+?)#\/#/g, '<span class="md-big" style="font-size: $1em;">$2</span>');
    
    // Box containers #B#content#/#
    html = html.replace(/#B#(.+?)#\/#/gs, '<span class="md-box">$1</span>');
    
    // Bold **text**
    html = html.replace(/\*\*(.+?)\*\*/g, '<span class="md-bold">$1</span>');
    
    // Italic @@text@@
    html = html.replace(/@@(.+?)@@/g, '<span class="md-italic">$1</span>');
    
    // Underline __text__
    html = html.replace(/__(.+?)__/g, '<span class="md-underline">$1</span>');
    
    // Strikethrough ~~text~~
    html = html.replace(/~~(.+?)~~/g, '<span class="md-strike">$1</span>');
    
    // Small text ..text..
    html = html.replace(/\.\.(.+?)\.\./g, '<span class="md-small">$1</span>');
    
    // Superscript ^text^
    html = html.replace(/\^([^\^]+)\^/g, '<span class="md-sup">$1</span>');
    
    // Subscript ~text~ (single tilde, not double)
    html = html.replace(/(?<!~)~([^~]+)~(?!~)/g, '<span class="md-sub">$1</span>');
    
    // Highlights
    html = html.replace(/==(.+?)==/g, '<span class="md-hl-yellow">$1</span>');
    html = html.replace(/!!(.+?)!!/g, '<span class="md-hl-red">$1</span>');
    html = html.replace(/\?\?(.+?)\?\?/g, '<span class="md-hl-blue">$1</span>');
    
    // Custom syntaxes
    for (const [marker, config] of Object.entries(customSyntaxes)) {
        const escaped = escapeRegex(marker);
        const regex = new RegExp(`${escaped}(.+?)${escaped}`, 'g');
        const style = buildCustomStyle(config);
        html = html.replace(regex, `<span class="md-custom" style="${style}">$1</span>`);
    }
    
    // Collapsible {{ content }}
    html = html.replace(/\{\{(.+?)\}\}/gs, '<span class="md-collapsible" onclick="this.classList.toggle(\'open\')">📁 <span class="md-collapsible-content">$1</span></span>');
    
    // Answer blocks [[ answer ]]
    html = html.replace(/\[\[(.+?)\]\]/g, '<span class="md-answer hidden-answer" onclick="this.classList.toggle(\'hidden-answer\')">$1</span>');
    
    // Horizontal separators (R-----G for colored)
    html = html.replace(/^([RGBYPO])?-{3,}([RGBYPO])?$/gm, (match, c1, c2) => {
        const colors = { R: '#ef4444', G: '#22c55e', B: '#3b82f6', Y: '#eab308', P: '#a855f7', O: '#f97316' };
        const color = colors[c1] || colors[c2] || 'var(--border)';
        return `<hr class="md-separator" style="background: ${color};">`;
    });
    
    // Lists
    html = html.replace(/^---\s+(.+)$/gm, '<span class="md-list" style="padding-left:3em;"><span class="md-list-item">$1</span></span>');
    html = html.replace(/^--\s+(.+)$/gm, '<span class="md-list" style="padding-left:2em;"><span class="md-list-item">$1</span></span>');
    html = html.replace(/^-\s+(.+)$/gm, '<span class="md-list"><span class="md-list-item">$1</span></span>');
    
    // KaTeX math \( ... \)
    html = html.replace(/\\\((.+?)\\\)/g, (match, math) => {
        try {
            return katex.renderToString(unescapeHtml(math), { throwOnError: false });
        } catch (e) {
            return match;
        }
    });
    
    // Preserve line breaks
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

function buildCustomStyle(config) {
    const styles = [];
    if (config.bgColor) styles.push(`background-color: ${config.bgColor}`);
    if (config.fgColor) styles.push(`color: ${config.fgColor}`);
    if (config.isBold) styles.push('font-weight: bold');
    if (config.isItalic) styles.push('font-style: italic');
    return styles.join('; ');
}

function stripMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/\*\*(.+?)\*\*/g, '$1')
        .replace(/@@(.+?)@@/g, '$1')
        .replace(/__(.+?)__/g, '$1')
        .replace(/~~(.+?)~~/g, '$1')
        .replace(/==(.+?)==/g, '$1')
        .replace(/!!(.+?)!!/g, '$1')
        .replace(/\?\?(.+?)\?\?/g, '$1')
        .replace(/#\d#(.+?)#\/#/g, '$1')
        .replace(/#B#(.+?)#\/#/g, '$1')
        .replace(/^#{1,3}\s+/gm, '')
        .replace(/\.\.(.+?)\.\./g, '$1')
        .replace(/\^([^\^]+)\^/g, '$1')
        .replace(/~([^~]+)~/g, '$1')
        .replace(/\{\{(.+?)\}\}/g, '$1')
        .replace(/\[\[(.+?)\]\]/g, '$1')
        .replace(/\\\((.+?)\\\)/g, '$1');
}


// History
function addToHistory(sheet, category) {
    // Remove if already exists
    history = history.filter(h => h.sheet.id !== sheet.id);
    // Add to front
    history.unshift({ sheet, category });
    // Keep only last 20
    history = history.slice(0, 20);
}

function renderHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = '';
    
    history.forEach((item, index) => {
        const el = document.createElement('div');
        el.className = 'history-item';
        
        const parent = item.sheet.parentId ? 
            currentCategory?.sheets.find(s => s.id === item.sheet.parentId)?.name : null;
        
        el.innerHTML = `
            <span class="history-number">#${index + 1}</span>
            <span class="history-name">${escapeHtml(item.sheet.name)}</span>
            ${parent ? `<span class="history-parent">[${escapeHtml(parent)}]</span>` : ''}
        `;
        
        el.addEventListener('click', () => {
            selectSheet(item.sheet, item.category);
            historyModal.classList.add('hidden');
        });
        
        list.appendChild(el);
    });
}

// Vault (F1)
function renderVault(searchMode = 'normal', query = '') {
    const categoriesEl = document.getElementById('vault-categories');
    const sheetsEl = document.getElementById('vault-sheets');
    
    categoriesEl.innerHTML = '';
    sheetsEl.innerHTML = '';
    
    let filteredCategories = appData.categories;
    let selectedCatId = currentCategory?.id || appData.categories[0]?.id;
    
    // Render categories
    filteredCategories.forEach(cat => {
        const el = document.createElement('div');
        el.className = 'vault-category-item' + (cat.id === selectedCatId ? ' active' : '');
        el.innerHTML = `
            <span>${escapeHtml(cat.name)}</span>
            <span class="category-count">${cat.sheets.length}</span>
        `;
        el.addEventListener('click', () => {
            document.querySelectorAll('.vault-category-item').forEach(e => e.classList.remove('active'));
            el.classList.add('active');
            renderVaultSheets(cat, query, searchMode);
        });
        categoriesEl.appendChild(el);
    });
    
    // Render sheets for selected category
    const selectedCat = filteredCategories.find(c => c.id === selectedCatId);
    if (selectedCat) {
        renderVaultSheets(selectedCat, query, searchMode);
    }
}

function renderVaultSheets(category, query, searchMode) {
    const sheetsEl = document.getElementById('vault-sheets');
    sheetsEl.innerHTML = '';
    
    let sheets = category.sheets;
    
    // Filter by query
    if (query) {
        const lowerQuery = query.toLowerCase();
        if (searchMode === 'content') {
            // Search in content
            sheets = sheets.filter(s => 
                s.name.toLowerCase().includes(lowerQuery) ||
                s.rows.some(r => stripMarkdown(r.content).toLowerCase().includes(lowerQuery))
            );
        } else {
            // Search by name
            sheets = sheets.filter(s => s.name.toLowerCase().includes(lowerQuery));
        }
    }
    
    sheets.forEach(sheet => {
        const el = document.createElement('div');
        el.className = 'vault-sheet-item' + (sheet.id === currentSheet?.id ? ' active' : '');
        el.textContent = sheet.name;
        el.addEventListener('click', () => {
            selectSheet(sheet, category);
            vaultModal.classList.add('hidden');
        });
        sheetsEl.appendChild(el);
    });
}

// Format Modal (F3)
function renderCustomSyntaxButtons() {
    const container = document.getElementById('custom-syntax-buttons');
    container.innerHTML = '';
    
    for (const [marker, config] of Object.entries(customSyntaxes)) {
        const btn = document.createElement('button');
        btn.dataset.format = marker;
        btn.textContent = marker;
        btn.style.cssText = buildCustomStyle(config);
        container.appendChild(btn);
    }
}

function applyFormat(format, endFormat = null) {
    if (!activeEditor) return;
    
    const sel = window.getSelection();
    const selected = sel.toString();
    const endMarker = endFormat || format;
    const newText = format + selected + endMarker;
    
    activeEditor.focus();
    document.execCommand('insertText', false, newText);
}

function updateSelectionStats() {
    const sel = window.getSelection();
    const selected = sel.toString();
    
    const chars = selected.length;
    const words = selected.trim() ? selected.trim().split(/\s+/).length : 0;
    const lines = selected ? selected.split('\n').length : 0;
    
    document.getElementById('selection-stats').innerHTML = `
        <span>Chars: ${chars}</span>
        <span>Words: ${words}</span>
        <span>Lines: ${lines}</span>
    `;
}

// Math Assistant
function updateMathPreview() {
    const num = document.getElementById('math-numerator').value;
    const den = document.getElementById('math-denominator').value;
    const sqrt = document.getElementById('math-sqrt').value;
    const exp = document.getElementById('math-exponent').value;
    
    let latex = '';
    
    if (num && den) {
        latex = `\\frac{${num}}{${den}}`;
    } else if (num) {
        latex = num;
    }
    
    if (sqrt) {
        latex = latex ? `${latex} \\cdot \\sqrt{${sqrt}}` : `\\sqrt{${sqrt}}`;
    }
    
    if (exp) {
        latex = latex ? `(${latex})^{${exp}}` : `x^{${exp}}`;
    }
    
    if (!latex) latex = 'x';
    
    document.getElementById('math-latex-output').textContent = `\\(${latex}\\)`;
    
    try {
        document.getElementById('math-preview-output').innerHTML = katex.renderToString(latex, { throwOnError: false });
    } catch (e) {
        document.getElementById('math-preview-output').textContent = 'Invalid expression';
    }
}

function insertMath() {
    const latex = document.getElementById('math-latex-output').textContent;
    if (activeEditor && latex) {
        activeEditor.focus();
        document.execCommand('insertText', false, latex);
    }
    mathModal.classList.add('hidden');
}

// Context Menu
let contextTarget = null;
let contextType = null;
let contextCategory = null;

function showContextMenu(e, type, target, category = null) {
    e.preventDefault();
    contextTarget = target;
    contextType = type;
    contextCategory = category;
    
    contextMenu.style.left = e.pageX + 'px';
    contextMenu.style.top = e.pageY + 'px';
    contextMenu.classList.remove('hidden');
}

function hideContextMenu() {
    contextMenu.classList.add('hidden');
}

function handleContextAction(action) {
    hideContextMenu();
    
    if (action === 'rename') {
        const newName = prompt('Enter new name:', contextTarget.name);
        if (newName && newName !== contextTarget.name) {
            contextTarget.name = newName;
            renderSidebar();
            if (contextType === 'sheet' && currentSheet?.id === contextTarget.id) {
                sheetTitle.textContent = newName;
            }
            saveData();
        }
    } else if (action === 'delete') {
        if (confirm(`Delete "${contextTarget.name}"?`)) {
            if (contextType === 'category') {
                appData.categories = appData.categories.filter(c => c.id !== contextTarget.id);
            } else {
                contextCategory.sheets = contextCategory.sheets.filter(s => s.id !== contextTarget.id);
                if (currentSheet?.id === contextTarget.id) {
                    currentSheet = null;
                    sheetContainer.innerHTML = '';
                }
            }
            renderSidebar();
            saveData();
        }
    } else if (action === 'move' && contextType === 'sheet') {
        const catNames = appData.categories.map((c, i) => `${i + 1}. ${c.name}`).join('\n');
        const choice = prompt(`Move to category:\n${catNames}\nEnter number:`);
        const idx = parseInt(choice) - 1;
        if (idx >= 0 && idx < appData.categories.length) {
            contextCategory.sheets = contextCategory.sheets.filter(s => s.id !== contextTarget.id);
            appData.categories[idx].sheets.push(contextTarget);
            renderSidebar();
            saveData();
        }
    }
}


// Event Listeners
function setupEventListeners() {
    // Add category
    document.getElementById('add-category-btn').addEventListener('click', async () => {
        const name = prompt('Category name:');
        if (name) {
            const res = await fetch('/api/category', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const newCat = await res.json();
            appData.categories.push(newCat);
            renderSidebar();
        }
    });
    
    // Add row
    document.getElementById('add-row-btn').addEventListener('click', addRow);
    
    // Export
    document.getElementById('export-btn').addEventListener('click', () => {
        window.location.href = '/api/export/static';
    });
    
    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', () => {
        const current = document.body.dataset.theme;
        document.body.dataset.theme = current === 'light' ? 'dark' : 'light';
        document.getElementById('theme-toggle').textContent = current === 'light' ? '🌙' : '☀️';
    });
    
    // Toggle sidebar
    document.getElementById('toggle-sidebar').addEventListener('click', () => {
        sidebar.classList.toggle('hidden');
    });
    
    // Sheet title editing
    sheetTitle.addEventListener('blur', () => {
        if (currentSheet && sheetTitle.textContent !== currentSheet.name) {
            currentSheet.name = sheetTitle.textContent;
            renderSidebar();
            saveData();
        }
    });
    
    sheetTitle.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sheetTitle.blur();
        }
    });
    
    // Modal close buttons
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').classList.add('hidden');
        });
    });
    
    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    });
    
    // Vault search
    document.getElementById('vault-search').addEventListener('input', (e) => {
        const query = e.target.value;
        let mode = 'normal';
        let searchQuery = query;
        
        if (query.startsWith('*')) {
            mode = 'global';
            searchQuery = query.substring(1);
        } else if (query.startsWith('#')) {
            mode = 'content';
            searchQuery = query.substring(1);
        }
        
        renderVault(mode, searchQuery);
    });
    
    document.getElementById('vault-search').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const firstSheet = document.querySelector('.vault-sheet-item');
            if (firstSheet) firstSheet.click();
        }
    });
    
    // Format buttons
    document.querySelector('.format-sections').addEventListener('click', (e) => {
        const btn = e.target.closest('button[data-format]');
        if (btn) {
            const format = btn.dataset.format;
            const endFormat = btn.dataset.end || null;
            const wrap = btn.dataset.wrap !== 'false';
            
            if (wrap) {
                applyFormat(format, endFormat);
            } else {
                // Insert at start of line
                if (activeEditor) {
                    activeEditor.focus();
                    document.execCommand('insertText', false, format);
                }
            }
            formatModal.classList.add('hidden');
        }
    });
    
    // Math assistant button
    document.getElementById('math-assistant-btn').addEventListener('click', () => {
        formatModal.classList.add('hidden');
        mathModal.classList.remove('hidden');
        updateMathPreview();
    });
    
    // Math inputs
    ['math-numerator', 'math-denominator', 'math-sqrt', 'math-exponent'].forEach(id => {
        document.getElementById(id).addEventListener('input', updateMathPreview);
    });
    
    // Math insert
    document.getElementById('math-insert-btn').addEventListener('click', insertMath);
    
    // Context menu
    document.addEventListener('click', hideContextMenu);
    document.querySelectorAll('.context-item').forEach(item => {
        item.addEventListener('click', () => handleContextAction(item.dataset.action));
    });
    
    // Selection stats update
    document.addEventListener('selectionchange', updateSelectionStats);
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // F1 - Vault
        if (e.key === 'F1') {
            e.preventDefault();
            vaultModal.classList.toggle('hidden');
            if (!vaultModal.classList.contains('hidden')) {
                renderVault();
                document.getElementById('vault-search').focus();
                document.getElementById('vault-search').value = '';
            }
        }
        
        // F2 - History
        if (e.key === 'F2') {
            e.preventDefault();
            historyModal.classList.toggle('hidden');
            if (!historyModal.classList.contains('hidden')) {
                renderHistory();
            }
        }
        
        // F3 - Quick Format
        if (e.key === 'F3') {
            e.preventDefault();
            formatModal.classList.toggle('hidden');
            if (!formatModal.classList.contains('hidden')) {
                updateSelectionStats();
            }
        }
        
        // F4 - Zen Mode (toggle sidebar + header)
        if (e.key === 'F4') {
            e.preventDefault();
            sidebar.classList.toggle('hidden');
            document.getElementById('header').classList.toggle('hidden');
        }
        
        // Escape - close modals
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
            hideContextMenu();
        }
        
        // Ctrl+S - Save
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            saveData();
        }
        
        // Number shortcuts in history modal
        if (!historyModal.classList.contains('hidden') && e.key >= '1' && e.key <= '9') {
            const idx = parseInt(e.key) - 1;
            if (history[idx]) {
                selectSheet(history[idx].sheet, history[idx].category);
                historyModal.classList.add('hidden');
            }
        }
    });
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function unescapeHtml(text) {
    const div = document.createElement('div');
    div.innerHTML = text;
    return div.textContent;
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function findSheetById(id) {
    for (const cat of appData.categories) {
        for (const sheet of cat.sheets) {
            if (sheet.id === id) {
                return { sheet, category: cat };
            }
        }
    }
    return null;
}
