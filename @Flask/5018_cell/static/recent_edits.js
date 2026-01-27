
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
            <span class="recent-edits-close" onclick="document.getElementById('lastEditedPopup').style.display='none'">✕</span>
        </div>
        <div class="recent-edit-list">
    `;

    if (edits.length === 0) {
        html += `<div class="recent-edit-empty">No recent edits in other sheets.</div>`;
    } else {
        edits.forEach(edit => {
            // Validate sheet existence
            const sheet = tableData.sheets[edit.sheetIdx];
            if (!sheet) return;

            const sheetName = sheet.name;
            const cellRef = `${getExcelColumnName(edit.col)}${edit.row + 1}`;

            // FETCH FRESH VALUE FROM SOURCE OF TRUTH
            // This ensures we show what is actually in the table, not just what was cached
            let freshValue = "";
            try {
                if (sheet.rows[edit.row] && sheet.rows[edit.row][edit.col] !== undefined) {
                    freshValue = sheet.rows[edit.row][edit.col];
                }
            } catch (e) {
                console.error("Error fetching fresh value for popup:", e);
                freshValue = edit.value || "";
            }

            // Sync cache if needed
            if (freshValue !== edit.value) {
                console.log(`[POPUP] Syncing stale cache for ${cellRef}. Old: "${edit.value}", New: "${freshValue}"`);
                edit.value = freshValue;
                if (lastEditedCells[edit.sheetIdx]) {
                    lastEditedCells[edit.sheetIdx].value = freshValue;
                    localStorage.setItem('lastEditedCells', JSON.stringify(lastEditedCells));
                }
            }

            // Escape value for attribute safely
            const safeValue = String(freshValue).replace(/"/g, '&quot;');

            html += `
                <div class="recent-edit-item">
                    <div class="recent-edit-info">
                        <span class="recent-edit-sheet">📄 ${sheetName}</span>
                        <span class="recent-edit-cell-ref">${cellRef}</span>
                    </div>
                    <div class="recent-edit-view-container editing" style="border-color: #007bff; box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);">
                        <textarea class="recent-edit-textarea" 
                                  style="display: block; height: auto;"
                                  onblur="savePopupEdit(this, ${edit.sheetIdx}, ${edit.row}, ${edit.col})"
                                  onkeydown="handlePopupTextareaKey(event)"
                                  oninput="autoResizePopupTextarea(this)">${safeValue}</textarea>
                    </div>
                </div>
            `;
        });
    }

    html += `</div>`;
    popup.innerHTML = html;

    // Auto-resize all textareas after rendering
    popup.querySelectorAll('.recent-edit-textarea').forEach(ta => autoResizePopupTextarea(ta));
}

/**
 * Set textarea height based on content without showing scrollbars
 */
function autoResizePopupTextarea(textarea) {
    // Reset height to recalculate
    textarea.style.height = 'auto';
    
    // Set height based on content, capped at ~15 lines (approx 330px)
    // standard line-height ~21px * 15 = 315 + padding
    const maxHeight = 330;
    
    if (textarea.scrollHeight > maxHeight) {
        textarea.style.height = maxHeight + 'px';
        textarea.style.overflowY = 'auto'; // Enable scrollbar
    } else {
        textarea.style.height = textarea.scrollHeight + 'px';
        textarea.style.overflowY = 'hidden'; // Hide scrollbar when fitting
    }
}

/**
 * Save the popup edit when textarea loses focus.
 */
function savePopupEdit(textarea, sheetIdx, row, col) {
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
}

/**
 * Handle keyboard events in popup textarea.
 */
function handlePopupTextareaKey(event) {
    // Check for Ctrl+S
    if (event.ctrlKey && (event.key === 's' || event.key === 'S')) {
        event.preventDefault(); // Prevent browser "Save Page As"
        event.stopPropagation();
        event.target.blur(); // Trigger save via the onblur handler
        return;
    }

    // Stop all propagation to prevent global hotkeys and page behavior for other keys
    event.stopPropagation();
    // Allow default Enter behavior (newline)
}

// Click-outside listener removed to keep popup open while working
// Close via the button or the 'X' icon only

/**
 * Synchronize the popup content when a cell is updated in the main table.
 * Called from script.js updateCell().
 */
function syncPopupWithMainUpdate(sheetIdx, row, col, newValue) {
    // Ensure types match for comparison
    sheetIdx = parseInt(sheetIdx);
    row = parseInt(row);
    col = parseInt(col);

    console.log(`[SYNC] Checking sync for Sheet:${sheetIdx} R:${row} C:${col}`);

    // Check if we have this sheet in our records
    // lastEditedCells keys are strings in JSON, but we can access with numbers
    const cellData = lastEditedCells[sheetIdx];

    if (cellData &&
        parseInt(cellData.row) === row &&
        parseInt(cellData.col) === col) {

        console.log(`[SYNC] Match found! Updating value to: "${newValue.substring(0, 20)}..."`);

        lastEditedCells[sheetIdx].value = newValue;
        lastEditedCells[sheetIdx].timestamp = Date.now();
        localStorage.setItem('lastEditedCells', JSON.stringify(lastEditedCells));

        // 2. If popup is open, update the UI dynamically
        const popup = document.getElementById('lastEditedPopup');
        if (popup && popup.style.display === 'block') {
            console.log(`[SYNC] Popup is open, re-rendering...`);
            renderLastEditedPopup();
        }
    } else {
        console.log(`[SYNC] No match found in bookmarks.`);
    }
}
