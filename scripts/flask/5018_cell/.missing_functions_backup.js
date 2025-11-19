// Missing F1, F2, F3 functions that need to be added back to script.js

// Global variable for F1 category selection
let selectedF1Category = null;

// F1 Popup Functions
function openF1Popup() {
    const popup = document.getElementById('f1Popup');
    if (popup) {
        popup.classList.add('show');
        populateF1Categories();
        populateF1Sheets();

        // Focus search input
        const searchInput = document.getElementById('f1SearchInput');
        if (searchInput) {
            setTimeout(() => {
                searchInput.focus();
            }, 100);
        }
    }
}

function closeF1Popup() {
    const popup = document.getElementById('f1Popup');
    if (popup) {
        popup.classList.remove('show');

        // Clear search
        const searchInput = document.getElementById('f1SearchInput');
        if (searchInput) {
            searchInput.value = '';
            filterF1Sheets();
        }

        // Exit separator mode if active
        if (window.f1SeparatorMode) {
            window.f1SeparatorMode = false;
            document.body.style.cursor = '';
            document.querySelectorAll('.f1-sheet-item').forEach(el => {
                el.style.cursor = '';
                el.classList.remove('separator-mode');
            });
        }
    }
}

// F2 Popup Functions
function openF2Popup() {
    const popup = document.getElementById('f2Popup');
    if (popup) {
        popup.classList.add('show');
        populateF2Sheets();
    }
}

function closeF2Popup() {
    const popup = document.getElementById('f2Popup');
    if (popup) {
        popup.classList.remove('show');
    }
}

function populateF2Sheets() {
    const sheetsList = document.getElementById('f2SheetsList');
    if (!sheetsList) return;

    sheetsList.innerHTML = '';

    if (sheetHistory.length === 0) {
        const emptyMsg = document.createElement('div');
        emptyMsg.style.padding = '20px';
        emptyMsg.style.textAlign = 'center';
        emptyMsg.style.color = '#999';
        emptyMsg.textContent = 'No recent sheets';
        sheetsList.appendChild(emptyMsg);
        return;
    }

    // Show recent sheets in reverse order (most recent first)
    const recentSheets = [...sheetHistory].reverse();

    recentSheets.forEach(sheetIndex => {
        if (sheetIndex >= 0 && sheetIndex < tableData.sheets.length) {
            const sheet = tableData.sheets[sheetIndex];
            const sheetCategory = tableData.sheetCategories[sheetIndex] || tableData.sheetCategories[String(sheetIndex)];
            const categoryLabel = sheetCategory ? ` <span style="color: #999; font-size: 12px;">(${sheetCategory})</span>` : '';

            const item = document.createElement('div');
            item.className = 'f2-sheet-item' + (sheetIndex === currentSheet ? ' active' : '');
            item.innerHTML = `
                <span class="f2-sheet-icon">📄</span>
                <span class="f2-sheet-name">${sheet.name}${categoryLabel}</span>
            `;
            item.onclick = () => {
                switchSheet(sheetIndex);
                closeF2Popup();
            };
            sheetsList.appendChild(item);
        }
    });
}

// F3 Quick Formatter Functions
function showQuickFormatter(inputElement) {
    const formatter = document.getElementById('quickFormatter');
    if (!formatter) return;

    // Store reference to the active input
    window.quickFormatterTarget = inputElement;

    // Position near the input
    const rect = inputElement.getBoundingClientRect();
    formatter.style.display = 'block';
    formatter.style.left = rect.left + 'px';
    formatter.style.top = (rect.bottom + 5) + 'px';

    // Update selection stats
    updateSelectionStats(inputElement);

    // Hide color picker section by default
    const colorSection = document.getElementById('colorPickerSection');
    if (colorSection) {
        colorSection.style.display = 'none';
    }
}

function closeQuickFormatter() {
    const formatter = document.getElementById('quickFormatter');
    if (formatter) {
        formatter.style.display = 'none';
    }
    window.quickFormatterTarget = null;

    // Hide color picker section
    const colorSection = document.getElementById('colorPickerSection');
    if (colorSection) {
        colorSection.style.display = 'none';
    }
}

function updateSelectionStats(inputElement) {
    const statsDiv = document.getElementById('selectionStats');
    if (!statsDiv || !inputElement) return;

    const selectedText = inputElement.value.substring(
        inputElement.selectionStart,
        inputElement.selectionEnd
    );

    const lines = selectedText.split('\n').length;
    const words = selectedText.trim() ? selectedText.trim().split(/\s+/).length : 0;
    const chars = selectedText.length;

    statsDiv.textContent = `${lines} lines • ${words} words • ${chars} chars`;
}
