const COLORS = ['#ffff00', '#aaffaa', '#aaddff', '#ffaaaa'];
// Use origin + pathname to be more robust against query param changes
let currentURL = window.location.origin + window.location.pathname;

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

// Add Color Picker Button (+)
let plusBtn = document.createElement('div');
plusBtn.className = 'web-highlighter-color-btn web-highlighter-plus-btn';
plusBtn.textContent = '+';
plusBtn.style.backgroundColor = '#fff';
plusBtn.style.color = '#333';
plusBtn.style.display = 'flex';
plusBtn.style.alignItems = 'center';
plusBtn.style.justifyContent = 'center';
plusBtn.style.fontSize = '14px';

// Hidden color input
let colorInput = document.createElement('input');
colorInput.type = 'color';
colorInput.style.display = 'none';
menu.appendChild(colorInput);

plusBtn.onmousedown = (e) => {
    e.preventDefault();
    // Delay click to ensure menu doesn't close immediately (scoping issue with selection clearing)
    // We open the native picker.
    setTimeout(() => colorInput.click(), 10);
};

// Handle color selection
colorInput.oninput = (e) => {
    const color = e.target.value;
    highlightSelection(color);
    menu.style.display = 'none';
    window.getSelection().removeAllRanges();
};

// Handle Color Picker cancel/close? 
// The input doesn't always fire cancel. But clicking away cleans up menu via mousedown listener elsewhere.

menu.appendChild(plusBtn);

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
        const parent = document.querySelector(h.path);
        if (!parent) return;

        // Search for text in this parent
        // We use a helper to wrap ONLY the text node that matches.

        const walker = document.createTreeWalker(parent, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while (node = walker.nextNode()) {
            const index = node.nodeValue.indexOf(h.text);
            if (index >= 0) {
                // Check if already highlighted (avoid double wrapping same id? No, id is unique)
                // But check if already wrapped in a span of our class?
                if (node.parentElement.classList.contains('web-highlighter-span')) continue;

                const range = document.createRange();
                range.setStart(node, index);
                range.setEnd(node, index + h.text.length);

                const span = document.createElement('span');
                span.className = 'web-highlighter-span';
                span.style.backgroundColor = h.color;
                span.dataset.highlightId = h.id;
                span.textContent = h.text; // Ensure content match

                range.deleteContents();
                range.insertNode(span);

                // Normalize parent to keep clean DOM
                parent.normalize();
                break; // Assume one match per saved item record in this block? 
                // If we have multiple same words saved, we rely on the order of applying?
                // It's tricky. But for MVP this works: finding the first unwrapped instance.
            }
        }
    } catch (e) {
        // console.log("Restoration error", e);
    }
}
