// Setup context menu for heading buttons
function setupHeadingContextMenu() {
    const h1Button = document.querySelector("[onclick=\"formatHeading('h1')\"]");
    const h2Button = document.querySelector("[onclick=\"formatHeading('h2')\"]");
    const h3Button = document.querySelector("[onclick=\"formatHeading('h3')\"]");
    
    if (h1Button) h1Button.addEventListener('contextmenu', (e) => showHeadingContextMenu(e, 'h1'));
    if (h2Button) h2Button.addEventListener('contextmenu', (e) => showHeadingContextMenu(e, 'h2'));
    if (h3Button) h3Button.addEventListener('contextmenu', (e) => showHeadingContextMenu(e, 'h3'));
}

function showHeadingContextMenu(event, headingType) {
    event.preventDefault();
    
    // Create context menu if it doesn't exist
    let contextMenu = document.getElementById('headingContextMenu');
    if (!contextMenu) {
        contextMenu = document.createElement('div');
        contextMenu.id = 'headingContextMenu';
        contextMenu.className = 'context-menu';
        document.body.appendChild(contextMenu);
        
        // Close context menu when clicking on it
        contextMenu.addEventListener('click', () => {
            contextMenu.style.display = 'none';
        });
    }
    
    // Position the context menu
    contextMenu.style.left = event.pageX + 'px';
    contextMenu.style.top = event.pageY + 'px';
    
    // Populate context menu with styling options
    contextMenu.innerHTML = `
        <div class="context-menu-item" onclick="openHeadingStyleModal('${headingType}')">
            Modify Style
        </div>
    `;
    
    contextMenu.style.display = 'block';
}

function openHeadingStyleModal(headingType) {
    // Hide context menu
    const contextMenu = document.getElementById('headingContextMenu');
    if (contextMenu) contextMenu.style.display = 'none';
    
    // Create or show modal
    let modal = document.getElementById('headingStyleModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'headingStyleModal';
        modal.className = 'modal';
        document.body.appendChild(modal);
    }
    
    // Get current styles for this heading type
    const currentStyles = headingStyles[headingType] || {};
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Style ${headingType.toUpperCase()}</h2>
                <span class="close" onclick="closeHeadingStyleModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div class="form-row">
                    <div class="form-col">
                        <div class="form-group">
                            <label>Font Family</label>
                            <select id="headingFontFamily" class="form-input">
                                <option value="Inter" ${currentStyles.fontFamily === 'Inter' ? 'selected' : ''}>Inter</option>
                                <option value="Arial" ${currentStyles.fontFamily === 'Arial' ? 'selected' : ''}>Arial</option>
                                <option value="Times New Roman" ${currentStyles.fontFamily === 'Times New Roman' ? 'selected' : ''}>Times New Roman</option>
                                <option value="Courier New" ${currentStyles.fontFamily === 'Courier New' ? 'selected' : ''}>Courier New</option>
                                <option value="Georgia" ${currentStyles.fontFamily === 'Georgia' ? 'selected' : ''}>Georgia</option>
                                <option value="Verdana" ${currentStyles.fontFamily === 'Verdana' ? 'selected' : ''}>Verdana</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-col">
                        <div class="form-group">
                            <label>Font Size</label>
                            <input type="text" id="headingFontSize" class="form-input" value="${currentStyles.fontSize || getDefaultFontSize(headingType)}" placeholder="e.g., 24px">
                        </div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-col">
                        <div class="form-group">
                            <label>Font Weight</label>
                            <select id="headingFontWeight" class="form-input">
                                <option value="normal" ${currentStyles.fontWeight === 'normal' ? 'selected' : ''}>Normal</option>
                                <option value="bold" ${currentStyles.fontWeight === 'bold' ? 'selected' : ''}>Bold</option>
                                <option value="600" ${currentStyles.fontWeight === '600' ? 'selected' : ''}>Semi-Bold</option>
                                <option value="700" ${currentStyles.fontWeight === '700' ? 'selected' : ''}>Bold</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-col">
                        <div class="form-group">
                            <label>Text Alignment</label>
                            <select id="headingTextAlign" class="form-input">
                                <option value="left" ${currentStyles.textAlign === 'left' ? 'selected' : ''}>Left</option>
                                <option value="center" ${currentStyles.textAlign === 'center' ? 'selected' : ''}>Center</option>
                                <option value="right" ${currentStyles.textAlign === 'right' ? 'selected' : ''}>Right</option>
                                <option value="justify" ${currentStyles.textAlign === 'justify' ? 'selected' : ''}>Justify</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-col">
                        <div class="form-group">
                            <label>Text Color</label>
                            <input type="color" id="headingColor" class="form-input" value="${currentStyles.color || getDefaultColor(headingType)}">
                        </div>
                    </div>
                    <div class="form-col">
                        <div class="form-group">
                            <label>Background Color</label>
                            <input type="color" id="headingBgColor" class="form-input" value="${currentStyles.backgroundColor || '#ffffff'}">
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Border</label>
                    <input type="text" id="headingBorder" class="form-input" value="${currentStyles.border || ''}" placeholder="e.g., 1px solid #000">
                </div>
                
                <div class="form-row">
                    <div class="form-col">
                        <div class="form-group">
                            <label>Padding</label>
                            <input type="text" id="headingPadding" class="form-input" value="${currentStyles.padding || getDefaultPadding(headingType)}" placeholder="e.g., 10px 0">
                        </div>
                    </div>
                    <div class="form-col">
                        <div class="form-group">
                            <label>Margin</label>
                            <input type="text" id="headingMargin" class="form-input" value="${currentStyles.margin || getDefaultMargin(headingType)}" placeholder="e.g., 20px 0 10px 0">
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="closeHeadingStyleModal()">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="saveHeadingStyle('${headingType}')">Save</button>
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeHeadingStyleModal() {
    const modal = document.getElementById('headingStyleModal');
    if (modal) modal.style.display = 'none';
}

function getDefaultFontSize(headingType) {
    switch(headingType) {
        case 'h1': return '2em';
        case 'h2': return '1.5em';
        case 'h3': return '1.25em';
        default: return '1em';
    }
}

function getDefaultColor(headingType) {
    switch(headingType) {
        case 'h1': return '#1a1a1a';
        case 'h2': return '#2a2a2a';
        case 'h3': return '#3a3a3a';
        default: return '#333333';
    }
}

function getDefaultPadding(headingType) {
    switch(headingType) {
        case 'h1': return '0.3em 0 0.5em 0';
        case 'h2': return '0.4em 0 0.4em 0';
        case 'h3': return '0.5em 0 0.3em 0';
        default: return '0.5em 0';
    }
}

function getDefaultMargin(headingType) {
    switch(headingType) {
        case 'h1': return '0.5em 0';
        case 'h2': return '0.8em 0 0.4em 0';
        case 'h3': return '0.6em 0 0.3em 0';
        default: return '1em 0';
    }
}

function saveHeadingStyle(headingType) {
    // Get values from form
    const fontFamily = document.getElementById('headingFontFamily').value;
    const fontSize = document.getElementById('headingFontSize').value;
    const fontWeight = document.getElementById('headingFontWeight').value;
    const color = document.getElementById('headingColor').value;
    const backgroundColor = document.getElementById('headingBgColor').value;
    const border = document.getElementById('headingBorder').value;
    const padding = document.getElementById('headingPadding').value;
    const margin = document.getElementById('headingMargin').value;
    const textAlign = document.getElementById('headingTextAlign').value;
    
    // Save to headingStyles object
    headingStyles[headingType] = {
        fontFamily: fontFamily || undefined,
        fontSize: fontSize || undefined,
        fontWeight: fontWeight || undefined,
        color: color || undefined,
        backgroundColor: backgroundColor || undefined,
        border: border || undefined,
        padding: padding || undefined,
        margin: margin || undefined,
        textAlign: textAlign || undefined
    };
    
    // Remove undefined values
    Object.keys(headingStyles[headingType]).forEach(key => {
        if (headingStyles[headingType][key] === undefined) {
            delete headingStyles[headingType][key];
        }
    });
    
    // Close modal
    closeHeadingStyleModal();
    
    // Apply styles
    applyHeadingStyles();
    
    // Save data (this applies to all sheets)
    saveData();
    
    showToast(`Style saved for ${headingType.toUpperCase()}!`, 'success');
    
    // Mark as modified
    isModified = true;
    updateDocumentInfo();
}

function applyHeadingStyles() {
    // Remove existing style element if it exists
    let styleElement = document.getElementById('headingStyles');
    if (styleElement) {
        styleElement.remove();
    }
    
    // Create new style element
    styleElement = document.createElement('style');
    styleElement.id = 'headingStyles';
    
    // Build CSS rules
    let cssRules = '';
    
    for (const [headingType, styles] of Object.entries(headingStyles)) {
        if (Object.keys(styles).length > 0) {
            cssRules += `.editor ${headingType} {`;
            for (const [property, value] of Object.entries(styles)) {
                if (value) {
                    // Convert camelCase to kebab-case
                    const cssProperty = property.replace(/([A-Z])/g, '-$1').toLowerCase();
                    cssRules += `${cssProperty}: ${value};`;
                }
            }
            cssRules += '}\n';
        }
    }
    
    styleElement.textContent = cssRules;
    document.head.appendChild(styleElement);
}