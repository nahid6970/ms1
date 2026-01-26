// Image Checker - Global Tracking Version
console.log('Image Checker: Global tracking loaded');

// Check blacklist first
chrome.storage.local.get(['excludedDomains'], (result) => {
    const excludedDomains = result.excludedDomains || [];
    const currentHostname = window.location.hostname.toLowerCase();

    const isExcluded = excludedDomains.some(input => {
        let domain = input.trim().toLowerCase();
        if (!domain) return false;

        // 1. Strip protocol (http://, https://)
        domain = domain.replace(/^https?:\/\//, '');

        // 2. Strip anything after the first slash (paths, queries)
        const slashIndex = domain.indexOf('/');
        if (slashIndex !== -1) {
            domain = domain.substring(0, slashIndex);
        }

        // 3. Strip port (e.g., :8080)
        const colonIndex = domain.indexOf(':');
        if (colonIndex !== -1) {
            domain = domain.substring(0, colonIndex);
        }

        // 4. Compare
        // Exact match OR subdomain match (e.g. "google.com" matches "mail.google.com")
        return currentHostname === domain || currentHostname.endsWith('.' + domain);
    });

    if (isExcluded) {
        console.log('Image Checker: Domain excluded. Stopping extension.');
        return;
    }

    runExtension();
});

function runExtension() {
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
        // We strictly prefer 'yt_' ID for global video tracking on YouTube
        // Valid for both Links (Titles) and Thumbnails if we can extract ID.
        // However, user wants separation.
        // Let's keep strict YouTube ID ONLY for what looks like a video/thumbnail interaction.
        if (location.hostname.includes('youtube.com')) {
            const link = element.closest('a');
            const urlPromise = link ? link.href : (element.src || element.href);
            if (urlPromise && (urlPromise.includes('youtube.com') || urlPromise.includes('youtu.be'))) {
                const videoId = extractYouTubeId(urlPromise);
                // Return yt_ID only for visual elements to avoid checking Titles
                if (videoId) {
                    const isVisual = element.tagName === 'IMG' ||
                        element.tagName === 'VIDEO' ||
                        element.tagName === 'YTD-THUMBNAIL' ||
                        element.classList.contains('ytd-thumbnail') ||
                        element.style.backgroundImage;

                    // If it is visual, return ID. If it's a Text Link (Title), fall through to generic link logic?
                    // Or we can return separate ID for YouTube Title? 
                    // Let's just return yt_ID for visuals.
                    if (isVisual) return `yt_${videoId}`;
                }
            }
        }

        // 2. Generic Sites: Strict Decoupling

        // Case A: Visual Media (Image/Video/Background)
        // ID = "media|" + source URL. Ignore parent Link!
        if (element.tagName === 'IMG') {
            return element.src ? `media|${element.src}` : null;
        }
        if (element.tagName === 'VIDEO') {
            return element.currentSrc || element.src ? `media|${element.currentSrc || element.src}` : null;
        }
        if (element.style && element.style.backgroundImage && element.style.backgroundImage !== 'none') {
            const bg = element.style.backgroundImage.slice(5, -2).replace(/['"]/g, "");
            return bg ? `media|${bg}` : null;
        }

        // Case B: Navigation Links
        // ID = "link|" + href.
        const link = element.closest('a');
        if (link && link.href) {
            // Option: Make ID even more specific to avoid "Read More" matching "Title"?
            // `link|${link.href}|${link.textContent.trim()}`
            // This makes it VERY specific (Individual).
            // Let's try adding text content hash to link ID to satisfy "Individual" request.
            // Simple hash to avoid huge IDs
            const textSnippet = link.textContent.trim().substring(0, 30).replace(/\s+/g, '');
            return `link|${link.href}|${textSnippet}`;
        }

        return null;
    }

    function extractYouTubeId(url) {
        const match = url.match(/(?:shorts\/|watch\?v=|youtu\.be\/|^)([a-zA-Z0-9_-]{11})/);
        return match ? match[1] : null;
    }

    // --- UI & Interaction ---

    function getTargetContainer(element) {
        // For YouTube, we strictly want the thumbnail container
        if (element.closest('ytd-thumbnail')) return element.closest('ytd-thumbnail');
        if (element.closest('ytd-playlist-thumbnail')) return element.closest('ytd-playlist-thumbnail');
        if (element.closest('.ytd-thumbnail')) return element.closest('.ytd-thumbnail');

        // For generic sites
        // If element is an IMG, return it (renderCheckmark handles sibling insertion)
        // If element is a DIV with background-image, return it.
        return element;
    }

    function scanPage() {
        // Expanded selectors for "Robustness"
        const selectors = [
            'ytd-thumbnail',
            'ytd-playlist-thumbnail',
            'a#thumbnail',
            'img',
            'video',
            '[style*="background-image"]', // Catch divs with backgrounds
            'article a', // Links inside articles suitable for checking
            '.card a',
            '.post a'
        ];

        const elements = document.querySelectorAll(selectors.join(','));
        elements.forEach(processElement);
    }

    function processElement(element) {
        if (element.dataset.icProcessed) return;

        // --- De-duplication Logic ---
        // If we are on YouTube, strictly ignore inner elements to prevent double-marking
        if (location.hostname.includes('youtube.com')) {
            const ytContainer = element.closest('ytd-thumbnail, ytd-playlist-thumbnail, .ytd-thumbnail');
            if (ytContainer && element !== ytContainer) {
                // If we found an inner element but we are tracking the container, stop.
                // But wait, the loop might process the inner element BEFORE the container.
                // We should only process the CONTAINER.
                // If 'element' is NOT one of the containers, and it IS inside one, skip.
                if (!['YTD-THUMBNAIL', 'YTD-PLAYLIST-THUMBNAIL'].includes(element.tagName) &&
                    !element.classList.contains('ytd-thumbnail')) return;
            }
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

        // Calculate dynamic size based on container dimensions
        const rect = container.getBoundingClientRect();
        // Use the smaller dimension to ensure it fits well
        const baseDimension = Math.min(rect.width, rect.height) || 100; // Fallback to 100 if rect is 0 (hidden)
        const calculatedSize = Math.max(20, baseDimension * (s.checkmarkSize / 100)); // Min 20px size
        
        // Checkmark base styles
        Object.assign(checkmark.style, {
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: '2147483640', // Very high z-index to stay on top
            width: `${calculatedSize}px`,
            height: `${calculatedSize}px`,
            backgroundColor: s.checkmarkColor,
            color: s.textColor,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: `${calculatedSize * 0.6}px`,
            fontWeight: 'bold',
            pointerEvents: 'none',
            boxShadow: '0 2px 4px rgba(0,0,0,0.5)',
            border: '2px solid white',
            margin: '0',
            padding: '0',
            lineHeight: '1',
            boxSizing: 'border-box' // Changed to border-box to include border in size
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

            // For centering over a void element (sibling), we position at center of that element
            checkmark.style.top = (container.offsetTop + (container.offsetHeight / 2)) + 'px';
            checkmark.style.left = (container.offsetLeft + (container.offsetWidth / 2)) + 'px';
            // transform is already set to -50%, -50%

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
            // top/left 50% is already set
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
            showNotification('Image Checker: OFF.', true); // true = isOff
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
    function getTabId() { return 'global'; }

    function loadSettings() {
        chrome.storage.local.get(['imageCheckerSettings'], function (result) {
            if (result.imageCheckerSettings) currentSettings = result.imageCheckerSettings;
        });
    }

    function showNotification(msg, isOff = false) {
        // Remove existing
        const existing = document.querySelector('.image-checker-notification');
        if (existing) existing.remove();

        const n = document.createElement('div');
        n.className = 'image-checker-notification';
        if (isOff) n.classList.add('off');

        // Minimal inline styles for strict positioning, rest in CSS
        n.style.position = 'fixed';
        n.style.top = '30px';
        n.style.left = '50%';
        n.style.transform = 'translateX(-50%)'; // Center it
        n.style.zIndex = '2147483647'; // Max Z-index

        n.textContent = msg;
        document.body.appendChild(n);

        setTimeout(() => {
            n.style.opacity = '0';
            n.style.transform = 'translate(-50%, -20px)';
            n.style.transition = 'all 0.5s ease-out';
            setTimeout(() => n.remove(), 500);
        }, 2500);
    }
}
