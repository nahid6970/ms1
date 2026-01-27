
// -----------------------------------------------------------------------------
// RECENT EDITS POPUP FEATURE
// -----------------------------------------------------------------------------

/**
 * Toggles the visibility of the "Last Edited" popup and renders its content.
 */
function toggleLastEditedPopup() {
    const popup = document.getElementById('lastEditedPopup');
    const button = document.getElementById('btnLastEdited');

    if (popup.style.display === 'block') {
        popup.style.display = 'none';
        return;
    }

    // specific logic: close other menus if open (optional but good practice)
    // Use the global function if available to ensure proper cleanup, or just remove class
    if (typeof closeCellContextMenu === 'function') {
        closeCellContextMenu();
    } else {
        const ctxMenu = document.getElementById('cellContextMenu');
        if (ctxMenu) {
            ctxMenu.classList.remove('show');
            // Ensure we don't leave an inline display:none that overrides the class later
            ctxMenu.style.display = '';
        }
    }

    renderLastEditedPopup();

    // Position the popup: Right side, Vertically centered
    popup.style.position = 'fixed';
    popup.style.left = 'auto'; // Reset left
    popup.style.right = '20px';
    popup.style.top = '50%';
    popup.style.transform = 'translateY(-50%)'; // Perfect vertical centering

    popup.style.display = 'block';
}

/**
 * Renders the content of the "Last Edited" popup.
 * Shows last edited cell from up to 3 OTHER sheets.
 */
function renderLastEditedPopup() {
    const popup = document.getElementById('lastEditedPopup');

    // Get edits from other sheets
    const edits = Object.entries(lastEditedCells)
        .map(([sheetIdx, data]) => ({ sheetIdx: parseInt(sheetIdx), ...data }))
        //.filter(edit => edit.sheetIdx !== currentSheet) // Removed filter to allow current sheet
        .sort((a, b) => b.timestamp - a.timestamp) // Most recent first
        .slice(0, 1); // Show only 1 item

    let html = `
        <div class="recent-edits-header">
            <span>Bookmark</span>
            <span style="font-size:10px; cursor:pointer;" onclick="document.getElementById('lastEditedPopup').style.display='none'">✕</span>
        </div>
        <div class="recent-edit-list">
    `;

    if (edits.length === 0) {
        html += `<div class="recent-edit-empty">No recent edits in other sheets.</div>`;
    } else {
        edits.forEach(edit => {
            const sheetName = tableData.sheets[edit.sheetIdx].name;
            const cellRef = `${getExcelColumnName(edit.col)}${edit.row + 1}`;

            // Escape value for attribute safely
            const safeValue = edit.value.replace(/"/g, '&quot;');

            // Generate Markdown Preview HTML (using main app's parser)
            // checkHasMarkdown and parseMarkdown are in script.js (global)
            let previewHtml = safeValue;
            if (typeof checkHasMarkdown === 'function' && typeof parseMarkdown === 'function') {
                // Use empty style object if getCellStyle unavailable or just default
                const style = {};
                previewHtml = checkHasMarkdown(edit.value)
                    ? parseMarkdown(edit.value, style)
                    : edit.value.replace(/\n/g, '<br>');
            }

            html += `
                <div class="recent-edit-item">
                    <div class="recent-edit-info">
                        <span class="recent-edit-sheet">📄 ${sheetName}</span>
                        <span class="recent-edit-cell-ref">${cellRef}</span>
                    </div>
                    <div class="recent-edit-view-container" onclick="enablePopupEdit(this, ${edit.sheetIdx}, ${edit.row}, ${edit.col})">
                        <div class="recent-edit-preview">${previewHtml}</div>
                        <textarea class="recent-edit-textarea" 
                                  onblur="disablePopupEdit(this, ${edit.sheetIdx}, ${edit.row}, ${edit.col})"
                                  onkeydown="handlePopupTextareaKey(event)"
                                  oninput="autoResizePopupTextarea(this)">${safeValue}</textarea>
                    </div>
                </div>
            `;
        });
    }

    html += `</div>`;
    popup.innerHTML = html;
}

/**
 * Auto-resize the textarea based on content
 */
function autoResizePopupTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight + 5) + 'px';
}

/**
 * Switch to edit mode for a popup item.
 */
function enablePopupEdit(container, sheetIdx, row, col) {
    if (container.classList.contains('editing')) return; // Already editing

    container.classList.add('editing');

    const preview = container.querySelector('.recent-edit-preview');
    const textarea = container.querySelector('.recent-edit-textarea');

    // Hide preview, show textarea
    preview.style.display = 'none';
    textarea.style.display = 'block';

    // Adjust height to fit content accurately
    autoResizePopupTextarea(textarea);

    textarea.focus();
}

/**
 * Save and switch back to preview mode.
 */
function disablePopupEdit(textarea, sheetIdx, row, col) {
    const container = textarea.parentElement;
    const preview = container.querySelector('.recent-edit-preview');

    // Saving logic
    const newValue = textarea.value;
    const sheet = tableData.sheets[sheetIdx];
    const currentValue = sheet.rows[row][col];

    if (newValue !== currentValue) {
        // Update data
        sheet.rows[row][col] = newValue;

        // Update history tracking
        if (lastEditedCells[sheetIdx]) {
            lastEditedCells[sheetIdx].value = newValue;
            lastEditedCells[sheetIdx].timestamp = Date.now();
            localStorage.setItem('lastEditedCells', JSON.stringify(lastEditedCells));
        }

        saveData();
        showToast(`Updated cell in ${sheet.name}`, 'success');
    }

    // Update preview HTML
    let previewHtml = newValue.replace(/\n/g, '<br>');
    if (typeof checkHasMarkdown === 'function' && typeof parseMarkdown === 'function') {
        const style = {};
        previewHtml = checkHasMarkdown(newValue)
            ? parseMarkdown(newValue, style)
            : newValue.replace(/\n/g, '<br>');
    }
    preview.innerHTML = previewHtml;

    // Switch view
    textarea.style.display = 'none';
    preview.style.display = 'block';
    container.classList.remove('editing');
}

/**
 * Allow Shift+Enter for new lines, Enter to save (standard spreadsheet behavior),
 * or standard text area behavior if preferred. 
 * User asked for "wrap", so multi-line is implied.
 * Let's stick to: Enter = New Line (since it's a textarea), Ctrl+Enter = Save?
 * Or just Blur to save (which is implemented).
 */
function handlePopupTextareaKey(event) {
    // Optional: Stop propagation to prevent global hotkeys
    event.stopPropagation();
}

// Click-outside listener removed to keep popup open while working
// Close via the button or the 'X' icon only

/**
 * Synchronize the popup content when a cell is updated in the main table.
 * Called from script.js updateCell().
 */
function syncPopupWithMainUpdate(sheetIdx, row, col, newValue) {
    // 1. Update the backing storage if this cell is pinned
    if (lastEditedCells[sheetIdx] &&
        lastEditedCells[sheetIdx].row === row &&
        lastEditedCells[sheetIdx].col === col) {

        lastEditedCells[sheetIdx].value = newValue;
        lastEditedCells[sheetIdx].timestamp = Date.now();
        localStorage.setItem('lastEditedCells', JSON.stringify(lastEditedCells));

        // 2. If popup is open, update the UI dynamically
        const popup = document.getElementById('lastEditedPopup');
        if (popup && popup.style.display === 'block') {
            // Find the specific item in the DOM
            // We don't have IDs on items, so we'll re-render if we can't find it easily.
            // But re-rendering is safe here because the user is typing in the MAIN table,
            // not the popup.
            renderLastEditedPopup();
        }
    }
}
