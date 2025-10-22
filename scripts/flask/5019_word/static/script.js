let documentData = { documents: [], activeDocument: 0 };
let currentDocument = 0;
let isModified = false;

// Load data on page load
window.onload = function () {
    initializeApp();
};

function initializeApp() {
    // Set up form handlers
    document.getElementById('renameForm').onsubmit = handleRenameFormSubmit;

    // Set up keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // Set up editor event listeners
    const editor = document.getElementById('editor');
    editor.addEventListener('input', handleEditorChange);
    editor.addEventListener('keydown', handleEditorKeydown);

    // Initialize custom heading styles
    initializeCustomHeadingStyles();

    // Setup ribbon heading right-click (ensure it's called after DOM is ready)
    setupRibbonHeadingRightClick();

    // Load initial data
    loadData();
}

function handleKeyboardShortcuts(e) {
    // Ctrl+S or Cmd+S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveData();
    }

    // Formatting shortcuts
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
        switch (e.key) {
            case 'b':
                e.preventDefault();
                formatText('bold');
                break;
            case 'i':
                e.preventDefault();
                formatText('italic');
                break;
            case 'u':
                e.preventDefault();
                formatText('underline');
                break;
        }
    }
}

function handleEditorChange() {
    const editor = document.getElementById('editor');
    const content = editor.innerHTML;

    // Update document content
    documentData.documents[currentDocument].content = content;

    // Mark as modified
    isModified = true;
    updateDocumentInfo();
}

function handleEditorKeydown(e) {
    // Handle Enter key for better paragraph formatting
    if (e.key === 'Enter' && !e.shiftKey) {
        // Let the browser handle it naturally
        setTimeout(() => {
            // Ensure we have proper paragraph tags
            const editor = document.getElementById('editor');
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                const container = range.commonAncestorContainer;

                // If we're not in a paragraph, wrap in one
                if (container.nodeType === Node.TEXT_NODE &&
                    container.parentNode === editor) {
                    document.execCommand('formatBlock', false, 'p');
                }
            }
        }, 0);
    }
}

async function loadData() {
    try {
        const response = await fetch('/api/data');
        documentData = await response.json();
        currentDocument = documentData.activeDocument || 0;
        renderDocumentTabs();
        renderEditor();
        updateDocumentInfo();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

async function saveData() {
    try {
        documentData.activeDocument = currentDocument;
        const response = await fetch('/api/data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(documentData)
        });
        const result = await response.json();
        if (result.success) {
            isModified = false;
            updateDocumentInfo();
            showToast('Document saved successfully!', 'success');
        }
    } catch (error) {
        console.error('Error saving data:', error);
        showToast('Error saving document!', 'error');
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

async function addDocument() {
    const docName = prompt('Enter document name:', `Document${documentData.documents.length + 1}`);
    if (!docName) return;

    try {
        const response = await fetch('/api/documents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: docName })
        });

        if (response.ok) {
            const result = await response.json();
            const now = new Date().toLocaleString();
            documentData.documents.push({
                name: docName,
                content: '',
                created: now,
                modified: now
            });
            currentDocument = result.documentIndex;
            renderDocumentTabs();
            renderEditor();
            updateDocumentInfo();
        }
    } catch (error) {
        console.error('Error adding document:', error);
    }
}

async function deleteDocument(index) {
    if (documentData.documents.length <= 1) {
        alert('Cannot delete the last document!');
        return;
    }

    const docName = documentData.documents[index].name;
    if (!confirm(`Delete document "${docName}"?`)) return;

    try {
        const response = await fetch(`/api/documents/${index}`, { method: 'DELETE' });
        if (response.ok) {
            documentData.documents.splice(index, 1);
            if (currentDocument >= documentData.documents.length) {
                currentDocument = documentData.documents.length - 1;
            }
            renderDocumentTabs();
            renderEditor();
            updateDocumentInfo();
        }
    } catch (error) {
        console.error('Error deleting document:', error);
    }
}

function switchDocument(index) {
    currentDocument = index;
    renderDocumentTabs();
    renderEditor();
    updateDocumentInfo();
}

function showRenameModal(index) {
    currentDocument = index;
    document.getElementById('documentName').value = documentData.documents[index].name;
    document.getElementById('renameModal').style.display = 'block';
}

function closeRenameModal() {
    document.getElementById('renameModal').style.display = 'none';
    document.getElementById('renameForm').reset();
}

async function handleRenameFormSubmit(e) {
    e.preventDefault();

    const newName = document.getElementById('documentName').value;

    try {
        const response = await fetch(`/api/documents/${currentDocument}/rename`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName })
        });

        if (response.ok) {
            documentData.documents[currentDocument].name = newName;
            renderDocumentTabs();
            closeRenameModal();
        }
    } catch (error) {
        console.error('Error renaming document:', error);
    }
}

function renderDocumentTabs() {
    // Update current document name
    const currentDocumentNameEl = document.getElementById('currentDocumentName');
    if (documentData.documents[currentDocument]) {
        currentDocumentNameEl.textContent = documentData.documents[currentDocument].name;
    }

    // Render document list
    const documentList = document.getElementById('documentList');
    documentList.innerHTML = '';

    documentData.documents.forEach((doc, index) => {
        const item = document.createElement('div');
        item.className = `document-item ${index === currentDocument ? 'active' : ''}`;

        const nameSpan = document.createElement('span');
        nameSpan.className = 'document-item-name';
        nameSpan.textContent = doc.name;
        nameSpan.onclick = () => {
            switchDocument(index);
            toggleDocumentList();
        };

        const infoSpan = document.createElement('div');
        infoSpan.className = 'document-item-info';
        infoSpan.textContent = `Modified: ${doc.modified || 'Never'}`;

        item.appendChild(nameSpan);
        item.appendChild(infoSpan);
        documentList.appendChild(item);
    });
}

function toggleDocumentList() {
    const documentList = document.getElementById('documentList');
    documentList.classList.toggle('show');
}

function renderEditor() {
    const editor = document.getElementById('editor');
    const doc = documentData.documents[currentDocument];

    if (doc) {
        editor.innerHTML = doc.content || '';
    } else {
        editor.innerHTML = '';
    }

    // Focus the editor
    editor.focus();
}

function updateDocumentInfo() {
    const infoEl = document.getElementById('documentInfo');
    const doc = documentData.documents[currentDocument];

    if (doc) {
        const status = isModified ? 'Modified' : 'Saved';
        const wordCount = getWordCount(doc.content);
        infoEl.textContent = `${status} • ${wordCount} words`;
    } else {
        infoEl.textContent = 'Ready';
    }
}

function getWordCount(html) {
    // Remove HTML tags and count words
    const text = html.replace(/<[^>]*>/g, '').trim();
    if (!text) return 0;
    return text.split(/\s+/).length;
}

function formatText(command, value = null) {
    document.execCommand(command, false, value);

    // Update button states
    updateFormatButtons();

    // Mark as modified
    handleEditorChange();
}

function formatHeading(headingTag) {
    // Use formatBlock to apply heading
    document.execCommand('formatBlock', false, headingTag);

    // Update button states
    updateFormatButtons();

    // Mark as modified
    handleEditorChange();
}

function updateFormatButtons() {
    const commands = ['bold', 'italic', 'underline'];
    commands.forEach(cmd => {
        const button = document.querySelector(`[onclick="formatText('${cmd}')"]`);
        if (button) {
            if (document.queryCommandState(cmd)) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        }
    });

    // Check heading states (including normal paragraph)
    const headings = ['p', 'h1', 'h2', 'h3'];
    headings.forEach(heading => {
        const button = document.querySelector(`[onclick="formatHeading('${heading}')"]`);
        if (button) {
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                const container = range.commonAncestorContainer;
                const element = container.nodeType === Node.TEXT_NODE ? container.parentNode : container;

                // Check if current element or its parent is the heading we're checking
                let currentElement = element;
                let isCurrentFormat = false;
                while (currentElement && currentElement !== document.getElementById('editor')) {
                    if (currentElement.tagName && currentElement.tagName.toLowerCase() === heading) {
                        isCurrentFormat = true;
                        break;
                    }
                    currentElement = currentElement.parentNode;
                }

                // Special case for normal text - check if we're not in any heading
                if (heading === 'p') {
                    let inHeading = false;
                    let checkElement = element;
                    while (checkElement && checkElement !== document.getElementById('editor')) {
                        if (checkElement.tagName && ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(checkElement.tagName)) {
                            inHeading = true;
                            break;
                        }
                        checkElement = checkElement.parentNode;
                    }
                    isCurrentFormat = !inHeading;
                }

                if (isCurrentFormat) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            } else {
                // Default to normal text when no selection
                if (heading === 'p') {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            }
        }
    });
}

function changeFontFamily() {
    const fontFamily = document.getElementById('fontFamily').value;
    formatText('fontName', fontFamily);
}

function changeFontSize() {
    const fontSize = document.getElementById('fontSize').value;
    // Convert px to pt for execCommand
    const sizeInPt = parseInt(fontSize) * 0.75;
    formatText('fontSize', Math.round(sizeInPt / 2)); // execCommand uses 1-7 scale

    // Also apply direct CSS for better control
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const span = document.createElement('span');
            span.style.fontSize = fontSize;
            try {
                range.surroundContents(span);
            } catch (e) {
                // If can't surround, apply to selection differently
                formatText('fontSize', fontSize);
            }
        }
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function (event) {
    const documentSelector = document.querySelector('.document-selector');
    const documentList = document.getElementById('documentList');
    if (!documentSelector.contains(event.target)) {
        documentList.classList.remove('show');
    }
});

// Update format buttons on selection change
document.addEventListener('selectionchange', updateFormatButtons);

// Heading context menu functionality
let currentHeadingElement = null;
let currentHeadingType = null;

// Add right-click event listener to editor and ribbon heading buttons
document.addEventListener('DOMContentLoaded', function () {
    const editor = document.getElementById('editor');
    if (editor) {
        editor.addEventListener('contextmenu', handleEditorRightClick);
    }

    // Setup ribbon heading right-click immediately
    setupRibbonHeadingRightClick();
});

function handleEditorRightClick(e) {
    const target = e.target;

    // Check if we're right-clicking on a heading
    let headingElement = target;
    while (headingElement && headingElement !== document.getElementById('editor')) {
        if (headingElement.tagName && ['H1', 'H2', 'H3'].includes(headingElement.tagName)) {
            e.preventDefault();
            showHeadingContextMenu(e, headingElement);
            return;
        }
        headingElement = headingElement.parentNode;
    }
}

function showHeadingContextMenu(e, headingElement) {
    currentHeadingElement = headingElement;
    currentHeadingType = headingElement.tagName.toLowerCase();

    const menu = document.getElementById('headingContextMenu');
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    menu.classList.add('show');
}

function closeHeadingContextMenu() {
    document.getElementById('headingContextMenu').classList.remove('show');
    currentHeadingElement = null;
    currentHeadingType = null;
}

function showHeadingStyleModal() {
    if (!currentHeadingElement) return;

    closeHeadingContextMenu();

    // Set modal title
    const title = document.getElementById('headingStyleTitle');
    title.textContent = `Customize ${currentHeadingType.toUpperCase()} Style`;

    // Load current styles
    loadCurrentHeadingStyles();

    // Show modal
    document.getElementById('headingStyleModal').style.display = 'block';

    // Set up form handler
    document.getElementById('headingStyleForm').onsubmit = handleHeadingStyleSubmit;
}

function closeHeadingStyleModal() {
    document.getElementById('headingStyleModal').style.display = 'none';
    document.getElementById('headingStyleForm').reset();
}

function loadCurrentHeadingStyles() {
    if (!currentHeadingElement) return;

    const computedStyle = window.getComputedStyle(currentHeadingElement);

    // Load current values
    document.getElementById('headingFontSize').value = computedStyle.fontSize || '1.5em';
    document.getElementById('headingFontWeight').value = computedStyle.fontWeight || '600';
    document.getElementById('headingTextColor').value = rgbToHex(computedStyle.color) || '#1a1a1a';
    document.getElementById('headingTextColorText').value = (rgbToHex(computedStyle.color) || '#1a1a1a').toUpperCase();
    document.getElementById('headingAlignment').value = computedStyle.textAlign || 'left';
    document.getElementById('headingLineHeight').value = computedStyle.lineHeight || '1.2';

    // Parse margin values (convert px to em approximately)
    const marginTop = parseFloat(computedStyle.marginTop) / 16 || 0.5;
    const marginBottom = parseFloat(computedStyle.marginBottom) / 16 || 0.5;
    document.getElementById('headingMarginTop').value = marginTop.toFixed(1);
    document.getElementById('headingMarginBottom').value = marginBottom.toFixed(1);

    // Check border settings
    const borderBottom = computedStyle.borderBottomWidth !== '0px';
    const borderTop = computedStyle.borderTopWidth !== '0px';
    document.getElementById('headingBorderBottom').checked = borderBottom;
    document.getElementById('headingBorderTop').checked = borderTop;

    if (borderBottom || borderTop) {
        document.getElementById('borderColorRow').style.display = 'grid';
        document.getElementById('headingBorderColor').value = rgbToHex(computedStyle.borderBottomColor) || '#e0e0e0';
        document.getElementById('headingBorderColorText').value = (rgbToHex(computedStyle.borderBottomColor) || '#e0e0e0').toUpperCase();
        document.getElementById('headingBorderWidth').value = computedStyle.borderBottomWidth || '2px';
    }

    // Set up color picker sync
    setupColorPickerSync();
    setupBorderToggle();
}

function setupColorPickerSync() {
    const textColorInput = document.getElementById('headingTextColor');
    const textColorText = document.getElementById('headingTextColorText');
    const borderColorInput = document.getElementById('headingBorderColor');
    const borderColorText = document.getElementById('headingBorderColorText');

    textColorInput.addEventListener('input', (e) => {
        textColorText.value = e.target.value.toUpperCase();
    });

    borderColorInput.addEventListener('input', (e) => {
        borderColorText.value = e.target.value.toUpperCase();
    });
}

function setupBorderToggle() {
    const borderBottom = document.getElementById('headingBorderBottom');
    const borderTop = document.getElementById('headingBorderTop');
    const borderColorRow = document.getElementById('borderColorRow');

    function toggleBorderOptions() {
        if (borderBottom.checked || borderTop.checked) {
            borderColorRow.style.display = 'grid';
        } else {
            borderColorRow.style.display = 'none';
        }
    }

    borderBottom.addEventListener('change', toggleBorderOptions);
    borderTop.addEventListener('change', toggleBorderOptions);
}

function handleHeadingStyleSubmit(e) {
    e.preventDefault();

    if (!currentHeadingElement) return;

    // Get form values
    const fontSize = document.getElementById('headingFontSize').value;
    const fontWeight = document.getElementById('headingFontWeight').value;
    const textColor = document.getElementById('headingTextColor').value;
    const alignment = document.getElementById('headingAlignment').value;
    const lineHeight = document.getElementById('headingLineHeight').value;
    const marginTop = document.getElementById('headingMarginTop').value + 'em';
    const marginBottom = document.getElementById('headingMarginBottom').value + 'em';
    const borderBottom = document.getElementById('headingBorderBottom').checked;
    const borderTop = document.getElementById('headingBorderTop').checked;
    const borderColor = document.getElementById('headingBorderColor').value;
    const borderWidth = document.getElementById('headingBorderWidth').value;

    // Apply styles to the heading element
    currentHeadingElement.style.fontSize = fontSize;
    currentHeadingElement.style.fontWeight = fontWeight;
    currentHeadingElement.style.color = textColor;
    currentHeadingElement.style.textAlign = alignment;
    currentHeadingElement.style.lineHeight = lineHeight;
    currentHeadingElement.style.marginTop = marginTop;
    currentHeadingElement.style.marginBottom = marginBottom;

    // Apply borders
    if (borderBottom) {
        currentHeadingElement.style.borderBottom = `${borderWidth} solid ${borderColor}`;
        currentHeadingElement.style.paddingBottom = '0.3em';
    } else {
        currentHeadingElement.style.borderBottom = 'none';
        currentHeadingElement.style.paddingBottom = '';
    }

    if (borderTop) {
        currentHeadingElement.style.borderTop = `${borderWidth} solid ${borderColor}`;
        currentHeadingElement.style.paddingTop = '0.3em';
    } else {
        currentHeadingElement.style.borderTop = 'none';
        currentHeadingElement.style.paddingTop = '';
    }

    // Mark as modified
    handleEditorChange();

    // Close modal
    closeHeadingStyleModal();

    showToast('Heading style updated!', 'success');
}

function resetHeadingStyle() {
    if (!currentHeadingElement) return;

    closeHeadingContextMenu();

    // Reset to default styles based on heading type
    const headingType = currentHeadingElement.tagName.toLowerCase();

    // Clear all inline styles
    currentHeadingElement.removeAttribute('style');

    // Mark as modified
    handleEditorChange();

    showToast(`${headingType.toUpperCase()} style reset to default`, 'success');
}

// Helper function to convert RGB to Hex
function rgbToHex(rgb) {
    if (!rgb) return '#000000';

    // If already hex, return it
    if (rgb.startsWith('#')) {
        return rgb.length === 7 ? rgb : '#000000';
    }

    // If rgb/rgba format
    const rgbMatch = rgb.match(/\d+/g);
    if (rgbMatch && rgbMatch.length >= 3) {
        const r = parseInt(rgbMatch[0]).toString(16).padStart(2, '0');
        const g = parseInt(rgbMatch[1]).toString(16).padStart(2, '0');
        const b = parseInt(rgbMatch[2]).toString(16).padStart(2, '0');
        return `#${r}${g}${b}`;
    }

    return '#000000';
}

// Setup right-click functionality for ribbon heading buttons
function setupRibbonHeadingRightClick() {
    // Get all heading buttons by their onclick attribute
    const h1Button = document.querySelector('[onclick="formatHeading(\'h1\')"]');
    const h2Button = document.querySelector('[onclick="formatHeading(\'h2\')"]');
    const h3Button = document.querySelector('[onclick="formatHeading(\'h3\')"]');

    if (h1Button) {
        h1Button.addEventListener('contextmenu', function (e) {
            e.preventDefault();
            showRibbonHeadingContextMenu(e, 'h1', h1Button);
        });
    }

    if (h2Button) {
        h2Button.addEventListener('contextmenu', function (e) {
            e.preventDefault();
            showRibbonHeadingContextMenu(e, 'h2', h2Button);
        });
    }

    if (h3Button) {
        h3Button.addEventListener('contextmenu', function (e) {
            e.preventDefault();
            showRibbonHeadingContextMenu(e, 'h3', h3Button);
        });
    }
}

function showRibbonHeadingContextMenu(e, headingType, buttonElement) {
    currentHeadingType = headingType;
    currentHeadingElement = null; // We're customizing the default style, not a specific element
    currentRibbonButton = buttonElement;

    const menu = document.getElementById('headingContextMenu');

    // Update context menu content for ribbon customization
    menu.innerHTML = `
        <div class="context-menu-item" onclick="openHeadingCustomizer('${headingType}')">
            <span>🎨</span>
            <span>Customize Default ${headingType.toUpperCase()} Style</span>
        </div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" onclick="resetRibbonHeadingStyle()">
            <span>🔄</span>
            <span>Reset ${headingType.toUpperCase()} to Default</span>
        </div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" onclick="applyHeadingToSelection()">
            <span>📝</span>
            <span>Apply ${headingType.toUpperCase()} to Selection</span>
        </div>
    `;

    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    menu.classList.add('show');
}

// New simplified function to open heading customizer
function openHeadingCustomizer(headingType) {
    currentHeadingType = headingType;
    currentHeadingElement = null;
    
    closeHeadingContextMenu();

    // Set modal title
    const title = document.getElementById('headingStyleTitle');
    title.textContent = `Customize Default ${headingType.toUpperCase()} Style`;

    // Load default styles for this heading type
    loadDefaultHeadingStyles();

    // Show modal
    const modal = document.getElementById('headingStyleModal');
    modal.style.display = 'block';

    // Set up form handler for ribbon customization
    const form = document.getElementById('headingStyleForm');
    form.onsubmit = handleRibbonHeadingStyleSubmit;
}

function loadDefaultHeadingStyles() {
    if (!currentHeadingType) return;

    // Get existing custom styles or use defaults
    const customStyles = getCustomHeadingStyles(currentHeadingType);

    // Set default values based on heading type
    let defaults = {};
    switch (currentHeadingType) {
        case 'h1':
            defaults = {
                fontSize: '2em',
                fontWeight: '700',
                color: '#1a1a1a',
                marginTop: '0.5',
                marginBottom: '0.5',
                borderBottom: true,
                borderColor: '#e0e0e0',
                borderWidth: '2px'
            };
            break;
        case 'h2':
            defaults = {
                fontSize: '1.5em',
                fontWeight: '600',
                color: '#2a2a2a',
                marginTop: '0.8',
                marginBottom: '0.4',
                borderBottom: false,
                borderColor: '#e0e0e0',
                borderWidth: '1px'
            };
            break;
        case 'h3':
            defaults = {
                fontSize: '1.25em',
                fontWeight: '600',
                color: '#3a3a3a',
                marginTop: '0.6',
                marginBottom: '0.3',
                borderBottom: false,
                borderColor: '#e0e0e0',
                borderWidth: '1px'
            };
            break;
    }

    // Merge with custom styles
    const styles = { ...defaults, ...customStyles };

    // Load values into form
    document.getElementById('headingFontSize').value = styles.fontSize;
    document.getElementById('headingFontWeight').value = styles.fontWeight;
    document.getElementById('headingTextColor').value = styles.color;
    document.getElementById('headingTextColorText').value = styles.color.toUpperCase();
    document.getElementById('headingAlignment').value = styles.alignment || 'left';
    document.getElementById('headingLineHeight').value = styles.lineHeight || '1.2';
    document.getElementById('headingMarginTop').value = styles.marginTop;
    document.getElementById('headingMarginBottom').value = styles.marginBottom;
    document.getElementById('headingBorderBottom').checked = styles.borderBottom || false;
    document.getElementById('headingBorderTop').checked = styles.borderTop || false;
    document.getElementById('headingBorderColor').value = styles.borderColor;
    document.getElementById('headingBorderColorText').value = styles.borderColor.toUpperCase();
    document.getElementById('headingBorderWidth').value = styles.borderWidth;

    // Show/hide border options
    const borderColorRow = document.getElementById('borderColorRow');
    if (styles.borderBottom || styles.borderTop) {
        borderColorRow.style.display = 'grid';
    } else {
        borderColorRow.style.display = 'none';
    }

    // Set up color picker sync and border toggle
    setupColorPickerSync();
    setupBorderToggle();
}

function handleRibbonHeadingStyleSubmit(e) {
    e.preventDefault();

    if (!currentHeadingType) return;

    // Get form values
    const styles = {
        fontSize: document.getElementById('headingFontSize').value,
        fontWeight: document.getElementById('headingFontWeight').value,
        color: document.getElementById('headingTextColor').value,
        alignment: document.getElementById('headingAlignment').value,
        lineHeight: document.getElementById('headingLineHeight').value,
        marginTop: document.getElementById('headingMarginTop').value,
        marginBottom: document.getElementById('headingMarginBottom').value,
        borderBottom: document.getElementById('headingBorderBottom').checked,
        borderTop: document.getElementById('headingBorderTop').checked,
        borderColor: document.getElementById('headingBorderColor').value,
        borderWidth: document.getElementById('headingBorderWidth').value
    };

    // Save custom styles
    saveCustomHeadingStyles(currentHeadingType, styles);

    // Apply styles to CSS
    updateHeadingCSS(currentHeadingType, styles);

    // Update ribbon button appearance
    updateRibbonButtonStyle(currentHeadingType);

    // Close modal
    closeHeadingStyleModal();

    showToast(`Default ${currentHeadingType.toUpperCase()} style updated!`, 'success');
}

function resetRibbonHeadingStyle() {
    if (!currentHeadingType) return;

    closeHeadingContextMenu();

    // Remove custom styles
    removeCustomHeadingStyles(currentHeadingType);

    // Reset CSS to default
    resetHeadingCSS(currentHeadingType);

    // Update ribbon button appearance
    updateRibbonButtonStyle(currentHeadingType);

    showToast(`${currentHeadingType.toUpperCase()} style reset to default`, 'success');
}

function applyHeadingToSelection() {
    if (!currentHeadingType) return;

    closeHeadingContextMenu();

    // Apply the heading format to current selection
    formatHeading(currentHeadingType);

    showToast(`${currentHeadingType.toUpperCase()} applied to selection`, 'success');
}

// Custom styles storage and management
function getCustomHeadingStyles(headingType) {
    const stored = localStorage.getItem(`customHeadingStyles_${headingType}`);
    return stored ? JSON.parse(stored) : {};
}

function saveCustomHeadingStyles(headingType, styles) {
    localStorage.setItem(`customHeadingStyles_${headingType}`, JSON.stringify(styles));
}

function removeCustomHeadingStyles(headingType) {
    localStorage.removeItem(`customHeadingStyles_${headingType}`);
}

// CSS manipulation functions
function updateHeadingCSS(headingType, styles) {
    // Remove existing custom style if any
    const existingStyle = document.getElementById(`custom-${headingType}-style`);
    if (existingStyle) {
        existingStyle.remove();
    }

    // Create new style element
    const styleElement = document.createElement('style');
    styleElement.id = `custom-${headingType}-style`;

    let css = `.editor ${headingType} {
        font-size: ${styles.fontSize} !important;
        font-weight: ${styles.fontWeight} !important;
        color: ${styles.color} !important;
        text-align: ${styles.alignment} !important;
        line-height: ${styles.lineHeight} !important;
        margin-top: ${styles.marginTop}em !important;
        margin-bottom: ${styles.marginBottom}em !important;`;

    if (styles.borderBottom) {
        css += `
        border-bottom: ${styles.borderWidth} solid ${styles.borderColor} !important;
        padding-bottom: 0.3em !important;`;
    } else {
        css += `
        border-bottom: none !important;
        padding-bottom: 0 !important;`;
    }

    if (styles.borderTop) {
        css += `
        border-top: ${styles.borderWidth} solid ${styles.borderColor} !important;
        padding-top: 0.3em !important;`;
    } else {
        css += `
        border-top: none !important;
        padding-top: 0 !important;`;
    }

    css += `
    }`;

    styleElement.textContent = css;
    document.head.appendChild(styleElement);
}

function resetHeadingCSS(headingType) {
    const existingStyle = document.getElementById(`custom-${headingType}-style`);
    if (existingStyle) {
        existingStyle.remove();
    }
}

function updateRibbonButtonStyle(headingType) {
    const button = document.querySelector(`[onclick*="formatHeading('${headingType}')"]`);
    if (button) {
        const customStyles = getCustomHeadingStyles(headingType);
        if (Object.keys(customStyles).length > 0) {
            // Add visual indicator that this heading has custom styling
            button.style.background = 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)';
            button.style.color = 'white';
            button.style.borderColor = '#0056b3';
            button.title = `${headingType.toUpperCase()} (Custom Style) - Right-click to customize`;
        } else {
            // Reset to default appearance
            button.style.background = '';
            button.style.color = '';
            button.style.borderColor = '';
            button.title = `${headingType.toUpperCase()} - Right-click to customize`;
        }
    }
}

// Initialize custom styles on page load
function initializeCustomHeadingStyles() {
    ['h1', 'h2', 'h3'].forEach(headingType => {
        const customStyles = getCustomHeadingStyles(headingType);
        if (Object.keys(customStyles).length > 0) {
            updateHeadingCSS(headingType, customStyles);
            updateRibbonButtonStyle(headingType);
        } else {
            // Set default tooltip
            const button = document.querySelector(`[onclick*="formatHeading('${headingType}')"]`);
            if (button) {
                button.title = `${headingType.toUpperCase()} - Right-click to customize`;
            }
        }
    });
}

let currentRibbonButton = null;

// Close context menu when clicking elsewhere
document.addEventListener('click', function (event) {
    const contextMenu = document.getElementById('headingContextMenu');
    if (!contextMenu.contains(event.target)) {
        closeHeadingContextMenu();
    }
});