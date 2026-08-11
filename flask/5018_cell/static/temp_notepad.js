
// -----------------------------------------------------------------------------
// TEMPORARY NOTEPAD FEATURE
// -----------------------------------------------------------------------------

/**
 * Toggles the visibility of the "Temporary Notepad" popup and renders its content.
 */
function toggleTempNotepad() {
    const popup = document.getElementById('tempNotepadPopup');

    if (popup.style.display === 'block') {
        popup.style.display = 'none';
        return;
    }

    // Close other menus if open
    if (typeof closeCellContextMenu === 'function') {
        closeCellContextMenu();
    }
    
    // Also close bookmark popup if open
    const bookmarkPopup = document.getElementById('lastEditedPopup');
    if (bookmarkPopup) bookmarkPopup.style.display = 'none';

    renderTempNotepad();

    // Position the popup: Right side, Vertically centered
    popup.style.position = 'fixed';
    popup.style.left = 'auto';
    popup.style.right = '20px';
    popup.style.top = '50%';
    popup.style.transform = 'translateY(-50%)';

    popup.style.display = 'block';
    
    // Focus the textarea after a short delay to allow rendering
    setTimeout(() => {
        const ta = document.getElementById('tempNotepadTextarea');
        if (ta) ta.focus();
    }, 50);
}

/**
 * Renders the content of the "Temporary Notepad" popup.
 */
function renderTempNotepad() {
    const popup = document.getElementById('tempNotepadPopup');
    
    // Load from localStorage or use empty string
    const savedContent = localStorage.getItem('temp_notepad_content') || "";

    let html = `
        <div class="recent-edits-header">
            <span>Temporary Notepad</span>
            <span class="recent-edits-close" onclick="document.getElementById('tempNotepadPopup').style.display='none'">✕</span>
        </div>
        <div class="temp-notepad-container">
            <textarea id="tempNotepadTextarea" 
                      class="temp-notepad-textarea" 
                      placeholder="Type temporary notes here... (Not saved to sheet)"
                      oninput="saveTempNotepadContent(this)">${savedContent}</textarea>
        </div>
    `;

    popup.innerHTML = html;
}

/**
 * Saves the notepad content to localStorage.
 */
function saveTempNotepadContent(textarea) {
    const content = textarea.value;
    localStorage.setItem('temp_notepad_content', content);
}

// Close popup when clicking outside
document.addEventListener('click', function(event) {
    const popup = document.getElementById('tempNotepadPopup');
    const btn = document.getElementById('btnTempNotepad');
    if (popup && popup.style.display === 'block') {
        if (!popup.contains(event.target) && !btn.contains(event.target)) {
            popup.style.display = 'none';
        }
    }
});
