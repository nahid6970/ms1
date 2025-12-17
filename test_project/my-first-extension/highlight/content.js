const COLORS = ['#ffff00', '#aaffaa', '#aaddff', '#ffaaaa'];
// Use hostname to share highlights across the entire domain
let currentURL = window.location.hostname;

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
    }
});

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

// Add Color Picker Button (+) via Label
let pickerLabel = document.createElement('label');
pickerLabel.className = 'web-highlighter-color-btn web-highlighter-plus-btn';
pickerLabel.textContent = '+';
pickerLabel.style.backgroundColor = '#fff';
pickerLabel.style.color = '#333';
pickerLabel.style.display = 'flex';
pickerLabel.style.alignItems = 'center';
pickerLabel.style.justifyContent = 'center';
pickerLabel.style.fontSize = '14px';
pickerLabel.style.cursor = 'pointer';

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
            menu.style.top = (window.scrollY + rect.top - 40) + 'px'; // -40 to be above
            menu.style.left = (window.scrollX + rect.left + (rect.width / 2)) + 'px';
            menu.style.display = 'flex';
            return;
        }
    }
    menu.style.display = 'none';
});

// Handle clicking on existing highlight
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('web-highlighter-span')) {
        if (confirm("Remove this highlight?")) {
            removeHighlight(e.target);
        }
    }
});

function highlightSelection(color) {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;

    const range = selection.getRangeAt(0);
    const text = selection.toString();

    // MVP Limit: Single block check
    // We will attempt to wrap. If it fails (cross-block), we warn.
    const span = document.createElement('span');
    span.className = 'web-highlighter-span';
    span.style.backgroundColor = color;
    span.dataset.highlightId = generateId();
    span.textContent = text;

    // Determine context BEFORE mutation
    const parent = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;
    const parentPath = getDomPath(parent);

    // Calculate start offset in the text content of the parent
    // This allows differentiation between multiple same words in one paragraph.
    // Note: 'textContent' of parent includes the text we are selecting.
    const fullText = parent.textContent;
    // We need the start index relative to parent text.
    // range.startContainer might be a text node, range.startOffset is relative to that node.
    // We need to walk up from startContainer to parent to count previous characters.

    let offset = 0;
    let node = parent;
    // Simple recursive offset finder
    // (A bit complex to implement perfectly in one go, relying on simple string index for now as fallback)
    // Fallback: First occurrence of 'text' in parent? No, that's weak.

    try {
        range.surroundContents(span);

        // Save to storage
        saveToStorage({
            id: span.dataset.highlightId,
            text: text,
            color: color,
            path: parentPath
        });

    } catch (e) {
        alert("Cannot highlight across multiple main elements. Try selecting within a single paragraph.");
        return;
    }
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
    let node;
    while (node = walker.nextNode()) {
        const index = node.nodeValue.indexOf(h.text);
        if (index >= 0) {
            // Check if already covered by OUR highlight
            // We need to be careful. If the text is inside a highlight already?
            if (node.parentElement.classList.contains('web-highlighter-span')) {
                // It's already highlighted.
                // If it has the same ID, we are good.
                if (node.parentElement.dataset.highlightId === h.id) return true;
                // If different ID, maybe overlapping or duplicate?
                continue;
            }

            const range = document.createRange();
            range.setStart(node, index);
            range.setEnd(node, index + h.text.length);

            const span = document.createElement('span');
            span.className = 'web-highlighter-span';
            span.style.backgroundColor = h.color;
            span.dataset.highlightId = h.id;
            span.textContent = h.text;

            try {
                range.deleteContents();
                range.insertNode(span);
                parent.normalize();
                success = true;
                // For MVP, we highlight the first match we find in fallback mode too.
                return true;
            } catch (err) {
                console.error(err);
            }
        }
    }
    return success;
}
