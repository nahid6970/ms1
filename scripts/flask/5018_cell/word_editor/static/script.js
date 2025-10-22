let documentData = { documents: [], activeDocument: 0 };
let currentDocument = 0;
let isModified = false;
let headingStyles = {
    h1: {},
    h2: {},
    h3: {}
};

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
    
    // Set up context menu for heading buttons
    setupHeadingContextMenu();

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
        
        // Load heading styles if they exist
        if (documentData.headingStyles) {
            headingStyles = documentData.headingStyles;
        }
        
        renderDocumentTabs();
        renderEditor();
        updateDocumentInfo();
        applyHeadingStyles();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

async function saveData() {
    try {
        documentData.activeDocument = currentDocument;
        // Save heading styles with document data
        documentData.headingStyles = headingStyles;
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
    
    // Apply direct CSS for better control
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            // Always use the extract and wrap approach for consistency
            // Extract the selected content
            const contents = range.extractContents();
            
            // Create a new span with the font size
            const span = document.createElement('span');
            span.style.fontSize = fontSize;
            
            // Wrap all the content in our span
            span.appendChild(contents);
            
            // Insert the span at the start of the original range
            range.insertNode(span);
            
            // Reselect the content we just inserted
            const newRange = document.createRange();
            newRange.selectNodeContents(span);
            selection.removeAllRanges();
            selection.addRange(newRange);
        }
    }
    
    // Mark as modified
    handleEditorChange();
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const documentSelector = document.querySelector('.document-selector');
    const documentList = document.getElementById('documentList');
    if (!documentSelector.contains(event.target)) {
        documentList.classList.remove('show');
    }
    
    // Close context menu when clicking outside
    const contextMenu = document.getElementById('headingContextMenu');
    if (contextMenu && !contextMenu.contains(event.target)) {
        contextMenu.style.display = 'none';
    }
});

// Update format buttons on selection change
document.addEventListener('selectionchange', updateFormatButtons);