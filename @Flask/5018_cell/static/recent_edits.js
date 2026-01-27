
// -----------------------------------------------------------------------------
// RECENT EDITS POPUP FEATURE
// -----------------------------------------------------------------------------

/**
 * Toggles the visibility of the "Last Edited" popup and renders its content.
 */
function toggleLastEditedPopup() {
    const popup = document.getElementById('lastEditedPopup');

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
let currentBookmarkIndex = 0;

/**
 * Renders the content of the "Last Edited" popup.
 * Shows last edited cell from up to 3 sheets.
 */
function renderLastEditedPopup() {
    const popup = document.getElementById('lastEditedPopup');

    // Filter valid edits
    let edits = [];
    if (Array.isArray(lastEditedCells)) {
        edits = lastEditedCells;
    } else {
        // Fallback for old object format
        edits = Object.entries(lastEditedCells)
            .map(([sheetIdx, data]) => ({ sheetIdx: parseInt(sheetIdx), ...data }));
    }

    // Sort by timestamp if not already sorted
    edits = edits.sort((a, b) => b.timestamp - a.timestamp).slice(0, 3);

    // Ensure index is valid
    if (currentBookmarkIndex >= edits.length) {
        currentBookmarkIndex = 0;
    }

    let html = `
        <div class="recent-edits-header">
            <span>Bookmark</span>
            <span class="recent-edits-close" onclick="document.getElementById('lastEditedPopup').style.display='none'">✕</span>
        </div>
    `;

    if (edits.length === 0) {
        html += `<div class="recent-edit-empty">No recent edits recorded.</div>`;
    } else {
        // Render Tabs
        html += `<div class="bookmark-tabs">`;
        edits.forEach((edit, index) => {
            const sheet = tableData.sheets[edit.sheetIdx];
            const sheetName = sheet ? sheet.name : `Sheet ${edit.sheetIdx + 1}`;
            const cellRef = `${getExcelColumnName(edit.col)}${edit.row + 1}`;
            const activeClass = index === currentBookmarkIndex ? 'active' : '';

            // Format: CellRef only, SheetName on hover using native title
            html += `
                <div class="bookmark-tab ${activeClass}" onclick="switchBookmark(${index})" title="${sheetName}">
                    <span class="tab-cell-ref">${cellRef}</span>
                </div>
            `;
        });
        html += `</div>`;

        // Render Active Content
        html += `<div class="recent-edit-list">`;

        const edit = edits[currentBookmarkIndex];
        const sheet = tableData.sheets[edit.sheetIdx];

        if (sheet) {
            // FETCH FRESH VALUE
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
                edit.value = freshValue;
                // Update specific item in array
                const target = Array.isArray(lastEditedCells) ? lastEditedCells.find(item =>
                    item.sheetIdx === edit.sheetIdx &&
                    item.row === edit.row &&
                    item.col === edit.col
                ) : null;

                if (target) {
                    target.value = freshValue;
                    localStorage.setItem('lastEditedCells', JSON.stringify(lastEditedCells));
                }
            }

            const safeValue = String(freshValue).replace(/"/g, '&quot;');

            html += `
                <div class="recent-edit-item">
                    <div class="recent-edit-view-container editing" style="border-color: #007bff; box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);">
                        <textarea class="recent-edit-textarea" 
                                  style="display: block; height: auto;"
                                  onblur="savePopupEdit(this, ${edit.sheetIdx}, ${edit.row}, ${edit.col})"
                                  onkeydown="handlePopupTextareaKey(event)"
                                  oninput="autoResizePopupTextarea(this)">${safeValue}</textarea>
                    </div>
                </div>
            `;
        }

        html += `</div>`;
    }

    popup.innerHTML = html;

    // Auto-resize active textarea
    popup.querySelectorAll('.recent-edit-textarea').forEach(ta => autoResizePopupTextarea(ta));
}

function switchBookmark(index) {
    currentBookmarkIndex = index;
    renderLastEditedPopup();
}

/**
 * Set textarea height based on content without showing scrollbars
 */
function autoResizePopupTextarea(textarea) {
    if (!textarea) return;

    // Use setTimeout to ensure DOM is rendered before calculating
    setTimeout(() => {
        // Reset height to recalculate
        textarea.style.height = 'auto';

        // Set height based on content, capped at ~15 lines (approx 330px)
        const maxHeight = 330;
        const scrollHeight = textarea.scrollHeight;

        // Force a minimum height if empty
        const effectiveHeight = Math.max(scrollHeight, 100);

        if (effectiveHeight > maxHeight) {
            textarea.style.height = maxHeight + 'px';
            textarea.style.overflowY = 'auto'; // Enable scrollbar
        } else {
            textarea.style.height = effectiveHeight + 'px';
            textarea.style.overflowY = 'auto'; // Keep auto to avoid jumpiness, max-height handles it
        }
    }, 0);
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

        // Update history tracking in array
        let target = null;
        if (Array.isArray(lastEditedCells)) {
            target = lastEditedCells.find(item =>
                item.sheetIdx === sheetIdx && item.row === row && item.col === col
            );
        } else {
            if (lastEditedCells[sheetIdx]) target = lastEditedCells[sheetIdx];
        }

        if (target) {
            target.value = newValue;
            target.timestamp = Date.now();
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

/**
 * Synchronize the popup content when a cell is updated in the main table.
 * Called from script.js updateCell().
 */
function syncPopupWithMainUpdate(sheetIdx, row, col, newValue) {
    // Ensure types match for comparison
    sheetIdx = parseInt(sheetIdx);
    row = parseInt(row);
    col = parseInt(col);

    // Update history tracking in array
    let target = null;
    if (Array.isArray(lastEditedCells)) {
        target = lastEditedCells.find(item =>
            item.sheetIdx === sheetIdx && item.row === row && item.col === col
        );
    } else {
        const item = lastEditedCells[sheetIdx];
        if (item && item.row === row && item.col === col) target = item;
    }

    if (target) {
        target.value = newValue;
        target.timestamp = Date.now();
        localStorage.setItem('lastEditedCells', JSON.stringify(lastEditedCells));

        // 2. If popup is open, update the UI dynamically
        const popup = document.getElementById('lastEditedPopup');
        if (popup && popup.style.display === 'block') {
            renderLastEditedPopup();
        }
    }
}
