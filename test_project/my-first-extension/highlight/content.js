let COLORS = ['#ffff00', '#aaffaa', '#aaddff', '#ffaaaa'];
// Use hostname to share highlights across the entire domain
let currentURL = window.location.hostname;

// Load custom colors from storage
chrome.storage.local.get(['customColors'], (result) => {
    if (result.customColors && result.customColors.length === 4) {
        COLORS = result.customColors;
        // Rebuild the menu with new colors
        rebuildColorMenu();
    }
});

// --- UTILS ---

function generateId() {
    return Math.random().toString(36).substr(2, 9);
}

// Robust CSS Selector Generator
function getDomPath(el) {
    if (!(el instanceof Element)) return;
    const path = [];
    while (el.nodeType === Node.ELEMENT_NODE) {
        let selector = el.nodeName.toLowerCase();
        if (el.id) {
            selector += '#' + el.id;
            path.unshift(selector);
            break; // IDs are unique, we can stop here
        } else {
            let sib = el, nth = 1;
            while (sib = sib.previousElementSibling) {
                if (sib.nodeName.toLowerCase() === selector) nth++;
            }
            if (nth != 1) selector += ":nth-of-type(" + nth + ")";
        }
        path.unshift(selector);
        el = el.parentNode;
    }
    return path.join(" > ");
}

// --- CORE ---

// Load highlights
chrome.storage.local.get([currentURL], (result) => {
    const highlights = result[currentURL] || [];
    highlights.forEach(h => applyHighlight(h));
});

// Listen for messages
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "refresh_highlights") {
        location.reload();
    } else if (request.action === "reload_colors") {
        chrome.storage.local.get(['customColors'], (result) => {
            if (result.customColors && result.customColors.length === 4) {
                COLORS = result.customColors;
                rebuildColorMenu();
            }
        });
    }
});

function rebuildColorMenu() {
    // Clear existing color buttons (keep the plus button)
    const colorButtons = menu.querySelectorAll('.web-highlighter-color-btn:not(.web-highlighter-plus-btn)');
    colorButtons.forEach(btn => btn.remove());

    // Re-add color buttons with new colors
    const plusBtn = menu.querySelector('.web-highlighter-plus-btn');
    COLORS.forEach(color => {
        let btn = document.createElement('div');
        btn.className = 'web-highlighter-color-btn';
        btn.style.backgroundColor = color;
        btn.onmousedown = (e) => {
            e.preventDefault();
            highlightSelection(color);
            menu.style.display = 'none';
            window.getSelection().removeAllRanges();
        };
        menu.insertBefore(btn, plusBtn);
    });
}

// UI: Floating Menu
let menu = document.createElement('div');
menu.className = 'web-highlighter-menu';
menu.style.display = 'none';
document.body.appendChild(menu);

COLORS.forEach(color => {
    let btn = document.createElement('div');
    btn.className = 'web-highlighter-color-btn';
    btn.style.backgroundColor = color;
    btn.onmousedown = (e) => {
        e.preventDefault();
        highlightSelection(color);
        menu.style.display = 'none';
        window.getSelection().removeAllRanges();
    };
    menu.appendChild(btn);
});

// Add Color Picker Button (rainbow) via Label
let pickerLabel = document.createElement('label');
pickerLabel.className = 'web-highlighter-color-btn web-highlighter-plus-btn';
pickerLabel.textContent = '🎨';

// Native Color Input
let colorInput = document.createElement('input');
colorInput.type = 'color';
// We hide it but keep it functional
colorInput.style.opacity = '0';
colorInput.style.position = 'absolute';
colorInput.style.width = '0';
colorInput.style.height = '0';
colorInput.style.padding = '0';
colorInput.style.margin = '0';
colorInput.style.border = '0';

pickerLabel.appendChild(colorInput);

pickerLabel.onmousedown = (e) => {
    // Stop propagation so we don't trigger document clikcs
    e.stopPropagation();
    // We do NOT preventDefault here because we want the Label to trigger the Input
};

// Handle color selection
colorInput.addEventListener('input', (e) => {
    const color = e.target.value;
    highlightSelection(color);
    menu.style.display = 'none';
    window.getSelection().removeAllRanges();
});

// Since input change/input events might happen, we rely on 'input' for real-time or 'change' for final.
// 'change' ensures the user closed the picker (usually). 'input' is live.
// Let's use 'change' to be safe about the final color decision? 
// Actually 'input' is cooler (live preview?) but we close the menu immediately.
// If we close menu immediately on 'input', dragging the color wheel might flicker?
// Better to use 'change' which fires when dismissal happens or complete.
colorInput.addEventListener('change', (e) => {
    const color = e.target.value;
    highlightSelection(color);
    menu.style.display = 'none';
    window.getSelection().removeAllRanges();
});

menu.appendChild(pickerLabel);

// Event Listeners
document.addEventListener('mouseup', (e) => {
    // If clicking inside menu, ignore
    if (menu.contains(e.target)) return;

    const selection = window.getSelection();
    // Only show if selection is not empty and not just whitespace
    if (selection.toString().trim().length > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // Show menu above selection
        if (rect.width > 0 && rect.height > 0) {
            menu.style.top = (window.scrollY + rect.top - 45) + 'px';
            menu.style.left = (window.scrollX + rect.left + (rect.width / 2) - 90) + 'px';
            menu.style.display = 'flex';
            return;
        }
    }
    menu.style.display = 'none';
});

// Context Menu for Highlighted Text
let contextMenu = document.createElement('div');
contextMenu.className = 'web-highlighter-context-menu';
document.body.appendChild(contextMenu);

let currentHighlightTarget = null;

// Handle clicking on existing highlight
document.addEventListener('click', (e) => {
    // Close context menu if clicking elsewhere
    if (!contextMenu.contains(e.target) && !e.target.classList.contains('web-highlighter-span')) {
        contextMenu.style.display = 'none';
        currentHighlightTarget = null;
        return;
    }

    if (e.target.classList.contains('web-highlighter-span')) {
        e.preventDefault();
        e.stopPropagation();

        currentHighlightTarget = e.target;
        const rect = e.target.getBoundingClientRect();

        // Clear previous buttons
        contextMenu.innerHTML = '';

        // Change Color Button
        let changeColorBtn = document.createElement('button');
        changeColorBtn.className = 'web-highlighter-context-btn';
        changeColorBtn.textContent = '🎨';
        changeColorBtn.onclick = (evt) => {
            evt.stopPropagation();
            showColorChangeMenu(currentHighlightTarget);
        };
        contextMenu.appendChild(changeColorBtn);

        // Note Button
        let noteBtn = document.createElement('button');
        noteBtn.className = 'web-highlighter-context-btn note-btn';
        noteBtn.textContent = '📝';
        noteBtn.onclick = (evt) => {
            evt.stopPropagation();
            showNoteDialog(currentHighlightTarget);
        };
        contextMenu.appendChild(noteBtn);

        // Delete Button
        let deleteBtn = document.createElement('button');
        deleteBtn.className = 'web-highlighter-context-btn delete-btn';
        deleteBtn.textContent = '×';
        deleteBtn.onclick = (evt) => {
            evt.stopPropagation();
            removeHighlight(currentHighlightTarget);
            contextMenu.style.display = 'none';
            currentHighlightTarget = null;
        };
        contextMenu.appendChild(deleteBtn);

        // Check if this highlight contains or is within a link
        let linkElement = findLinkElement(e.target);
        if (linkElement) {
            let openLinkBtn = document.createElement('button');
            openLinkBtn.className = 'web-highlighter-context-btn link-btn';
            openLinkBtn.textContent = '↗';
            openLinkBtn.onclick = (evt) => {
                evt.stopPropagation();
                window.open(linkElement.href, '_blank');
                contextMenu.style.display = 'none';
            };
            contextMenu.appendChild(openLinkBtn);
        }

        // Position the menu
        contextMenu.style.top = (window.scrollY + rect.bottom + 5) + 'px';
        contextMenu.style.left = (window.scrollX + rect.left) + 'px';
        contextMenu.style.display = 'flex';
    }
});

function findLinkElement(element) {
    // Check if element is inside a link
    let current = element;
    while (current && current !== document.body) {
        if (current.tagName === 'A' && current.href) {
            return current;
        }
        current = current.parentElement;
    }

    // Check if element contains a link
    let link = element.querySelector('a[href]');
    return link;
}

function showColorChangeMenu(highlightElement) {
    // Clear and show color picker
    contextMenu.innerHTML = '';

    // Add preset colors
    COLORS.forEach(color => {
        let colorBtn = document.createElement('div');
        colorBtn.className = 'web-highlighter-color-btn';
        colorBtn.style.backgroundColor = color;
        colorBtn.onclick = (e) => {
            e.stopPropagation();
            changeHighlightColor(highlightElement, color);
            contextMenu.style.display = 'none';
        };
        contextMenu.appendChild(colorBtn);
    });

    // Add custom color picker
    let customPickerLabel = document.createElement('label');
    customPickerLabel.className = 'web-highlighter-color-btn web-highlighter-plus-btn';
    customPickerLabel.textContent = '🎨';

    let customInput = document.createElement('input');
    customInput.type = 'color';
    customInput.style.opacity = '0';
    customInput.style.position = 'absolute';
    customInput.style.width = '0';
    customInput.style.height = '0';

    customInput.addEventListener('change', (e) => {
        changeHighlightColor(highlightElement, e.target.value);
        contextMenu.style.display = 'none';
    });

    customPickerLabel.appendChild(customInput);
    contextMenu.appendChild(customPickerLabel);

    // Position stays the same as when context menu was opened
}

function changeHighlightColor(element, newColor) {
    const id = element.dataset.highlightId;
    element.style.backgroundColor = newColor;

    // Update storage
    chrome.storage.local.get([currentURL], (result) => {
        let items = result[currentURL] || [];
        items = items.map(h => {
            if (h.id === id) {
                h.color = newColor;
            }
            return h;
        });
        chrome.storage.local.set({ [currentURL]: items });
    });
}

function showNoteDialog(highlightElement) {
    const id = highlightElement.dataset.highlightId;
    
    // Get current note from storage
    chrome.storage.local.get([currentURL], (result) => {
        let items = result[currentURL] || [];
        let highlight = items.find(h => h.id === id);
        let currentNote = highlight ? (highlight.note || '') : '';
        
        // Create note dialog
        let noteDialog = document.createElement('div');
        noteDialog.className = 'web-highlighter-note-dialog';
        noteDialog.innerHTML = `
            <div class="web-highlighter-note-content">
                <h3>Add Note</h3>
                <textarea placeholder="Add your note here..." rows="4">${currentNote}</textarea>
                <div class="web-highlighter-note-buttons">
                    <button class="save-note-btn">Save</button>
                    <button class="cancel-note-btn">Cancel</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(noteDialog);
        
        let textarea = noteDialog.querySelector('textarea');
        let saveBtn = noteDialog.querySelector('.save-note-btn');
        let cancelBtn = noteDialog.querySelector('.cancel-note-btn');
        
        // Focus textarea and select existing text
        textarea.focus();
        if (currentNote) textarea.select();
        
        saveBtn.onclick = () => {
            let noteText = textarea.value.trim();
            
            // Update storage
            chrome.storage.local.get([currentURL], (result) => {
                let items = result[currentURL] || [];
                items = items.map(h => {
                    if (h.id === id) {
                        h.note = noteText;
                    }
                    return h;
                });
                chrome.storage.local.set({ [currentURL]: items });
            });
            
            // Update visual indicator
            if (noteText) {
                highlightElement.setAttribute('title', noteText);
                highlightElement.style.borderBottom = '2px dotted rgba(0,0,0,0.3)';
            } else {
                highlightElement.removeAttribute('title');
                highlightElement.style.borderBottom = 'none';
            }
            
            document.body.removeChild(noteDialog);
            contextMenu.style.display = 'none';
        };
        
        cancelBtn.onclick = () => {
            document.body.removeChild(noteDialog);
        };
        
        // Close on outside click
        noteDialog.onclick = (e) => {
            if (e.target === noteDialog) {
                document.body.removeChild(noteDialog);
            }
        };
    });
}

function highlightSelection(color) {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;

    const range = selection.getRangeAt(0);
    const text = selection.toString();

    if (!text.trim()) {
        menu.style.display = 'none';
        return;
    }

    // Determine context for robust re-highlighting on page load
    const parent = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;
    const parentPath = getDomPath(parent);

    const highlightData = {
        id: generateId(),
        text: text,
        color: color,
        path: parentPath,
        note: ''
    };

    saveToStorage(highlightData);

    const parentElement = document.querySelector(parentPath);
    let found = false;
    if (parentElement) {
        found = wrapTextInParent(parentElement, highlightData);
    }
    if (!found) {
        wrapTextInParent(document.body, highlightData);
    }
    
    menu.style.display = 'none';
    window.getSelection().removeAllRanges();
}

function saveToStorage(data) {
    chrome.storage.local.get([currentURL], (result) => {
        let items = result[currentURL] || [];
        items.push(data);
        chrome.storage.local.set({ [currentURL]: items });
    });
}

function removeHighlight(element) {
    const id = element.dataset.highlightId;
    const parent = element.parentNode;

    const text = document.createTextNode(element.textContent);
    parent.replaceChild(text, element);

    // Normalize to merge adjacent text nodes
    parent.normalize();

    // Update storage
    chrome.storage.local.get([currentURL], (result) => {
        let items = result[currentURL] || [];
        items = items.filter(h => h.id !== id);
        chrome.storage.local.set({ [currentURL]: items });
    });
}

function applyHighlight(h) {
    try {
        let parent = null;
        try {
            parent = document.querySelector(h.path);
        } catch (e) {
            // Invalid selector or not found
        }

        let found = false;

        // Strategy 1: Try exact path
        if (parent) {
            found = wrapTextInParent(parent, h);
        }

        // Strategy 2: Fallback to Body (if path search failed to find text)
        if (!found) {
            // Only if text is long enough to avoid massive noise, or just do it?
            // Let's rely on the text being somewhat unique or user intent.
            wrapTextInParent(document.body, h);
        }

    } catch (e) {
        // console.log("Restoration error", e);
    }
}

function wrapTextInParent(parent, h) {
    let success = false;
    const walker = document.createTreeWalker(parent, NodeFilter.SHOW_TEXT, null, false);
    
    const nodes = [];
    while(walker.nextNode()) {
        if (walker.currentNode.parentElement.closest('.web-highlighter-span')) continue;
        if (walker.currentNode.nodeValue.includes(h.text)) {
            nodes.push(walker.currentNode);
        }
    }

    nodes.forEach(node => {
        let currentNode = node;
        while (currentNode) {
            const index = currentNode.nodeValue.indexOf(h.text);
            if (index === -1) break;

            // Infinite loop prevention for empty strings
            if (h.text.length === 0) break;

            const range = document.createRange();
            range.setStart(currentNode, index);
            range.setEnd(currentNode, index + h.text.length);

            const span = document.createElement('span');
            span.className = 'web-highlighter-span';
            span.style.backgroundColor = h.color;
            span.dataset.highlightId = h.id;
            span.textContent = range.toString();

            if (h.note && h.note.trim()) {
                span.setAttribute('title', h.note);
                span.style.borderBottom = '2px dotted rgba(0,0,0,0.3)';
            }

            try {
                range.deleteContents();
                range.insertNode(span);
                success = true;
                
                // Safely advance to the next text node to prevent infinite loops
                if (span.nextSibling && span.nextSibling.nodeType === Node.TEXT_NODE) {
                    currentNode = span.nextSibling;
                } else {
                    currentNode = null;
                }
            } catch (e) {
                console.error("Failed to wrap text:", e);
                currentNode = null; 
            }
        }
    });

    parent.normalize();
    return success;
}
