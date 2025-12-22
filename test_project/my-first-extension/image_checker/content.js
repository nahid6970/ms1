// Image Checker - Global Tracking Version
console.log('Image Checker: Global tracking loaded');

let checkingMode = false;
let seenItems = new Set(); // Local cache of seen IDs
let currentSettings = {
    checkmarkSize: 15,
    checkmarkColor: '#4CAF50',
    textColor: '#ffffff',
    enableBorder: false,
    borderColor: '#4CAF50',
    borderWidth: 3
};

// --- Initialization ---

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    init();
}

function init() {
    loadSettings();
    loadSeenItems().then(() => {
        // Initial scan
        scanPage();

        // Watch for changes (YouTube/SPA navigation + Infinite Scroll)
        setupObservers();

        // Check if mode should be active
        const tabId = getTabId();
        chrome.storage.local.get([`checkingMode_${tabId}`], function (result) {
            if (result[`checkingMode_${tabId}`]) {
                toggleMode(true);
            }
        });
    });
}

// --- Data & Storage ---

function loadSeenItems() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['seenItems'], function (result) {
            if (result.seenItems) {
                // seenItems is expected to be an object: { "ID": timestamp, "ID2": timestamp }
                // We just cache the keys for fast lookup
                seenItems = new Set(Object.keys(result.seenItems));
            }
            resolve();
        });
    });
}

function markAsSeen(id) {
    if (!id) return;

    seenItems.add(id);

    chrome.storage.local.get(['seenItems'], function (result) {
        const store = result.seenItems || {};
        store[id] = Date.now();
        chrome.storage.local.set({ seenItems: store });
    });

    // Visually update immediately
    applyCheckmarksToMatching(id);
}

function markAsUnseen(id) {
    if (!id) return;

    seenItems.delete(id);

    chrome.storage.local.get(['seenItems'], function (result) {
        const store = result.seenItems || {};
        delete store[id];
        chrome.storage.local.set({ seenItems: store });
    });

    // Visually remove immediately
    removeCheckmarksMatching(id);
}

// --- Identification Logic ---

function getContentId(element) {
    // 1. YouTube Specific Logic
    // Try to find the closest valid endpoint for ID
    const link = element.closest('a');
    let url = link ? link.href : (element.currentSrc || element.src || element.href);

    if (!url || url.startsWith('data:') || url.startsWith('blob:')) return null;

    // YouTube Video / Short ID extraction
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
        const videoId = extractYouTubeId(url);
        // Only mark if we actually found an ID, otherwise ignore (generic page, navigation links)
        if (videoId) return `yt_${videoId}`;
    }

    // 2. Fallback: Use the full URL as ID
    return url;
}

function extractYouTubeId(url) {
    const match = url.match(/(?:shorts\/|watch\?v=|youtu\.be\/|^)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
}

// --- UI & Interaction ---

function getTargetContainer(element) {
    // For YouTube, we strictly want the thumbnail container to avoid hitting titles/avatars
    if (element.closest('ytd-thumbnail')) return element.closest('ytd-thumbnail');
    if (element.closest('ytd-playlist-thumbnail')) return element.closest('ytd-playlist-thumbnail');
    if (element.closest('.ytd-thumbnail')) return element.closest('.ytd-thumbnail');

    // For generic sites
    // If it's an IMG, we want the IMG itself to be the target for sizing,
    // but we can't append to it. We'll handle that in renderCheckmark.
    return element;
}

function scanPage() {
    // YouTube: strictly target thumbnails to avoid title links
    // Generic: target images directly
    const selectors = [
        'ytd-thumbnail',
        'ytd-playlist-thumbnail',
        'a#thumbnail', // YouTube alternative
        'img',
        // 'video' // Video elements can be tricky with overlays, sticking to IMG/Thumbnail for now
    ];

    const elements = document.querySelectorAll(selectors.join(','));
    elements.forEach(processElement);
}

function processElement(element) {
    if (element.dataset.icProcessed) return;

    // --- De-duplication Logic ---
    // If we are on YouTube, and this element is inside a known container we already track, skip it.
    // e.g. IMG inside ytd-thumbnail.
    if (location.hostname.includes('youtube.com')) {
        if (element.tagName === 'IMG' && element.closest('ytd-thumbnail')) return;
        if (element.tagName === 'A' && element.closest('ytd-thumbnail')) return;
        // Exclude avatars
        if (element.closest('#avatar') || element.closest('yt-img-shadow.ytd-channel-name')) return;
    }

    const id = getContentId(element);
    if (!id) return;

    element.dataset.icContentId = id;
    element.dataset.icProcessed = 'true';

    // Listeners
    element.addEventListener('click', handleContentClick, true);
    element.addEventListener('mouseenter', handleMouseEnter);
    element.addEventListener('mouseleave', handleMouseLeave);

    if (seenItems.has(id)) {
        renderCheckmark(element);
    }
}

function handleContentClick(event) {
    if (!checkingMode) return;

    event.preventDefault();
    event.stopPropagation();

    const element = event.currentTarget;
    const id = element.dataset.icContentId;

    if (seenItems.has(id)) {
        markAsUnseen(id);
    } else {
        markAsSeen(id);
    }
}

function handleMouseEnter(event) {
    if (!checkingMode) return;
    const element = event.currentTarget;
    element.style.outline = `4px solid ${currentSettings.checkmarkColor}`;
    element.style.outlineOffset = '-4px'; // Draw inside to avoid layout shifts/clipping
    element.style.cursor = 'help'; // Distinct cursor
}

function handleMouseLeave(event) {
    const element = event.currentTarget;
    element.style.outline = '';
    element.style.cursor = '';
}

// --- Checkmark Rendering ---

function renderCheckmark(element) {
    // Check if already has checkmark (on element or as sibling)
    if (element.dataset.hasCheckmark === 'true') return;

    const container = getTargetContainer(element);

    const checkmark = document.createElement('div');
    checkmark.className = 'ic-checkmark';
    checkmark.innerHTML = '✓';
    checkmark.dataset.forId = element.dataset.icContentId;

    const s = currentSettings;
    // Checkmark base styles
    Object.assign(checkmark.style, {
        position: 'absolute',
        zIndex: '9999',
        width: `${s.checkmarkSize}px`,
        height: `${s.checkmarkSize}px`,
        backgroundColor: s.checkmarkColor,
        color: s.textColor,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: `${s.checkmarkSize * 0.6}px`,
        fontWeight: 'bold',
        pointerEvents: 'none',
        boxShadow: '0 2px 4px rgba(0,0,0,0.5)',
        border: '2px solid white'
    });

    // --- Insertion Logic ---
    // Case 1: Void elements (IMG, INPUT) - Cannot appendChild
    const isVoidElement = ['IMG', 'INPUT', 'BR', 'HR'].includes(container.tagName);

    if (isVoidElement) {
        // We must insert as sibling and position relative to the element
        const parent = container.offsetParent || container.parentNode;

        // Ensure parent can hold absolute children anchored to it?
        // Actually, we can just use offsetTop/Left relative to the parent.
        // But if the parent isn't positioned, absolute children bubble up.
        // Let's try to enforce position on parent if it's static.
        const parentStyle = window.getComputedStyle(parent);
        if (parentStyle.position === 'static') {
            parent.style.position = 'relative';
        }

        // Calculate position relative to the parent
        // container.offsetLeft/Top gives position relative to offsetParent.
        // Since we force parent to be relative (or find offsetParent), we can use these directly.

        checkmark.style.top = (container.offsetTop + 5) + 'px';
        checkmark.style.left = (container.offsetLeft + 5) + 'px';

        // Insert after container
        if (container.nextSibling) {
            parent.insertBefore(checkmark, container.nextSibling);
        } else {
            parent.appendChild(checkmark);
        }

    } else {
        // Case 2: Normal Container (Div, A, etc) - Just append inside
        const style = window.getComputedStyle(container);
        if (style.position === 'static') {
            container.style.position = 'relative';
        }
        checkmark.style.top = '5px';
        checkmark.style.left = '5px';
        container.appendChild(checkmark);
    }

    // Mark element as having checkmark
    element.dataset.hasCheckmark = 'true';
    checkmark.dataset.ownerElementRawId = element.dataset.icContentId; // For cleanup mapping

    // Border option
    if (s.enableBorder) {
        container.dataset.originalBorder = container.style.border;
        container.style.border = `${s.borderWidth}px solid ${s.borderColor}`;
    }
}

function removeCheckmarksMatching(id) {
    const checks = document.querySelectorAll(`.ic-checkmark`);
    checks.forEach(check => {
        if (check.dataset.forId === id) {
            // Restore border if needed
            const container = check.parentNode;
            if (container && container.dataset.originalBorder !== undefined) {
                container.style.border = container.dataset.originalBorder;
            } else if (container) {
                container.style.border = '';
            }

            // Clean up dataset on owner element
            if (check.dataset.ownerElementRawId) {
                const owners = document.querySelectorAll(`[data-ic-content-id="${check.dataset.ownerElementRawId}"]`);
                owners.forEach(owner => delete owner.dataset.hasCheckmark);
            }

            check.remove();
        }
    });
}

function applyCheckmarksToMatching(id) {
    // Find all elements on page with this ID and mark them
    const elements = document.querySelectorAll(`[data-ic-content-id="${id}"]`);
    elements.forEach(el => {
        renderCheckmark(el);
    });
}

// --- Observers ---

function setupObservers() {
    // Watch for new content (Infinite Scroll)
    const observer = new MutationObserver((mutations) => {
        let shouldScan = false;
        mutations.forEach(m => {
            if (m.addedNodes.length > 0) shouldScan = true;
        });

        if (shouldScan) {
            // Debounce scan slightly
            if (window.scanTimeout) clearTimeout(window.scanTimeout);
            window.scanTimeout = setTimeout(scanPage, 500);
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

// --- Toggles & Messages ---

function toggleMode(enabled) {
    checkingMode = enabled;
    const tabId = getTabId();
    chrome.storage.local.set({ [`checkingMode_${tabId}`]: checkingMode });

    if (enabled) {
        showNotification('Image Checker: ON. Click items to mark/unmark.');
    } else {
        showNotification('Image Checker: OFF.');
    }
}

// F2 listener
document.addEventListener('keydown', function (event) {
    if (event.key === 'F2') {
        toggleMode(!checkingMode);
    }
});

// Messages
chrome.runtime.onMessage.addListener((message) => {
    if (message.action === 'toggleCheckingMode') {
        toggleMode(message.enabled);
    } else if (message.action === 'updateSettings') {
        currentSettings = message.settings;
        document.querySelectorAll('.ic-checkmark').forEach(c => {
            // Cleanup owner
            if (c.dataset.ownerElementRawId) {
                const owners = document.querySelectorAll(`[data-ic-content-id="${c.dataset.ownerElementRawId}"]`);
                owners.forEach(owner => delete owner.dataset.hasCheckmark);
            }
            c.remove();
        });
        seenItems.forEach(id => applyCheckmarksToMatching(id));
    } else if (message.action === 'clearAllCheckmarks') {
        seenItems.clear();
        chrome.storage.local.remove('seenItems');
        document.querySelectorAll('.ic-checkmark').forEach(c => {
            if (c.dataset.ownerElementRawId) {
                const owners = document.querySelectorAll(`[data-ic-content-id="${c.dataset.ownerElementRawId}"]`);
                owners.forEach(owner => delete owner.dataset.hasCheckmark);
            }
            c.remove();
        });
        showNotification('All checkmarks cleared!');
    }
});

// Utils
function getTabId() { return 'global'; } // Keep mode persistent globally or per tab? User requested "work on other sites", global pref is usually better.
// But for now, let's keep it simple. If valid URL, use it, else generic.

function loadSettings() {
    chrome.storage.local.get(['imageCheckerSettings'], function (result) {
        if (result.imageCheckerSettings) currentSettings = result.imageCheckerSettings;
    });
}

function showNotification(msg) {
    const n = document.createElement('div');
    Object.assign(n.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: '#333',
        color: '#fff',
        padding: '10px 20px',
        borderRadius: '5px',
        zIndex: 100000,
        boxShadow: '0 2px 10px rgba(0,0,0,0.5)',
        transition: 'opacity 0.5s'
    });
    n.textContent = msg;
    document.body.appendChild(n);
    setTimeout(() => {
        n.style.opacity = '0';
        setTimeout(() => n.remove(), 500);
    }, 2500);
}
