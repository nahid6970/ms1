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

        // Listen for storage changes to sync seenItems across tabs
        chrome.storage.onChanged.addListener((changes, areaName) => {
            if (areaName === 'local' && changes.seenItems) {
                const newSeenItems = changes.seenItems.newValue || {};
                seenItems = new Set(Object.keys(newSeenItems));
                // Update all existing checkmarks to reflect new state
                syncAllCheckmarks();
            }
            if (areaName === 'local' && changes.imageCheckerSettings) {
                currentSettings = changes.imageCheckerSettings.newValue;
                refreshAllCheckmarks();
            }
        });
    }

    // --- Data & Storage ---

    function loadSeenItems() {
        return new Promise((resolve) => {
            chrome.storage.local.get(['seenItems'], function (result) {
                if (result.seenItems) {
                    seenItems = new Set(Object.keys(result.seenItems));
                }
                resolve();
            });
        });
    }

    function markAsSeen(id) {
        if (!id) return;
        if (seenItems.has(id)) return; // Already seen

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
        if (!seenItems.has(id)) return; // Already unseen

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
        if (location.hostname.includes('youtube.com')) {
            // If clicking the player itself while watching a video, use the current page video ID
            if (element.closest('#movie_player') || element.tagName === 'VIDEO') {
                const videoId = extractYouTubeId(location.href);
                if (videoId) return `yt_${videoId}`;
            }

            const link = element.closest('a');
            const urlPromise = link ? link.href : (element.src || element.href);
            if (urlPromise && (urlPromise.includes('youtube.com') || urlPromise.includes('youtu.be'))) {
                const videoId = extractYouTubeId(urlPromise);
                if (videoId) {
                    const isVisual = element.tagName === 'IMG' ||
                        element.tagName === 'VIDEO' ||
                        element.tagName === 'YTD-THUMBNAIL' ||
                        element.classList.contains('ytd-thumbnail') ||
                        element.style.backgroundImage;
                    if (isVisual) return `yt_${videoId}`;
                }
            }
        }
        // 2. Generic Sites: Strict Decoupling

        // Case A: Visual Media (Image/Video/Background)
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
        const link = element.closest('a');
        if (link && link.href) {
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
        // For YouTube player page, use the player container
        if (element.closest('#movie_player')) return element.closest('#movie_player');
        // For YouTube, we strictly want the thumbnail container
        if (element.closest('ytd-thumbnail')) return element.closest('ytd-thumbnail');
        if (element.closest('ytd-playlist-thumbnail')) return element.closest('ytd-playlist-thumbnail');
        if (element.closest('.ytd-thumbnail')) return element.closest('.ytd-thumbnail');

        return element;
    }

    function scanPage() {
        const selectors = [
            'ytd-thumbnail',
            'ytd-playlist-thumbnail',
            'a#thumbnail',
            'img',
            'video',
            '[style*="background-image"]',
            'article a',
            '.card a',
            '.post a'
        ];

        const elements = document.querySelectorAll(selectors.join(','));
        elements.forEach(processElement);
    }

    function processElement(element) {
        // --- YouTube De-duplication ---
        if (location.hostname.includes('youtube.com')) {
            const ytContainer = element.closest('ytd-thumbnail, ytd-playlist-thumbnail, .ytd-thumbnail');
            if (ytContainer && element !== ytContainer) {
                if (!['YTD-THUMBNAIL', 'YTD-PLAYLIST-THUMBNAIL'].includes(element.tagName) &&
                    !element.classList.contains('ytd-thumbnail')) return;
            }
        }

        const id = getContentId(element);
        if (!id) return;

        const oldId = element.dataset.icContentId;

        // If ID changed (Element Recycling in SPAs like YouTube)
        if (oldId && oldId !== id) {
            removeCheckmarksFromElement(element);
            element.dataset.icProcessed = 'false'; // Allow re-processing
        }

        if (element.dataset.icProcessed === 'true') {
            // Even if processed, ensure checkmark matches current seenItems state
            syncElementCheckmark(element, id);
            return;
        }

        element.dataset.icContentId = id;
        element.dataset.icProcessed = 'true';

        // Add listeners only once
        if (element.dataset.icListenersAdded !== 'true') {
            element.addEventListener('click', handleContentClick, true);
            element.addEventListener('mouseenter', handleMouseEnter);
            element.addEventListener('mouseleave', handleMouseLeave);
            element.dataset.icListenersAdded = 'true';
        }

        if (seenItems.has(id)) {
            renderCheckmark(element);
        }
    }

    function syncElementCheckmark(element, id) {
        const isSeen = seenItems.has(id);
        const hasCheck = element.dataset.hasCheckmark === 'true';

        if (isSeen && !hasCheck) {
            renderCheckmark(element);
        } else if (!isSeen && hasCheck) {
            removeCheckmarksFromElement(element);
        }
    }

    function syncAllCheckmarks() {
        const elements = document.querySelectorAll('[data-ic-processed="true"]');
        elements.forEach(el => {
            const id = getContentId(el); // Re-get ID in case it changed without us noticing
            if (id) {
                if (el.dataset.icContentId !== id) {
                    removeCheckmarksFromElement(el);
                    el.dataset.icContentId = id;
                }
                syncElementCheckmark(el, id);
            }
        });
    }

    function refreshAllCheckmarks() {
        document.querySelectorAll('.ic-checkmark').forEach(c => {
            const container = c.parentNode;
            if (container && container.dataset.originalBorder !== undefined) {
                container.style.border = container.dataset.originalBorder;
                delete container.dataset.originalBorder;
            }
            c.remove();
        });
        document.querySelectorAll('[data-ic-processed="true"]').forEach(el => {
            delete el.dataset.hasCheckmark;
            const id = el.dataset.icContentId;
            if (id && seenItems.has(id)) {
                renderCheckmark(el);
            }
        });
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
        element.style.outlineOffset = '-4px';
        element.style.cursor = 'help';
    }

    function handleMouseLeave(event) {
        const element = event.currentTarget;
        element.style.outline = '';
        element.style.cursor = '';
    }

    // --- Checkmark Rendering ---

    function renderCheckmark(element) {
        if (element.dataset.hasCheckmark === 'true') return;

        const container = getTargetContainer(element);
        const id = element.dataset.icContentId;

        const checkmark = document.createElement('div');
        checkmark.className = 'ic-checkmark';
        checkmark.innerHTML = '✓';
        checkmark.dataset.forId = id;
        checkmark.dataset.ownerId = id; // Reference to owner

        const s = currentSettings;

        // Calculate dynamic size
        const rect = container.getBoundingClientRect();
        const baseDimension = Math.min(rect.width, rect.height) || 100;
        const calculatedSize = Math.max(20, baseDimension * (s.checkmarkSize / 100));
        
        Object.assign(checkmark.style, {
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: '2147483640',
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
            boxSizing: 'border-box'
        });

        const isVoidElement = ['IMG', 'INPUT', 'BR', 'HR'].includes(container.tagName);

        if (isVoidElement) {
            const parent = container.offsetParent || container.parentNode;
            const parentStyle = window.getComputedStyle(parent);
            if (parentStyle.position === 'static') {
                parent.style.position = 'relative';
            }

            checkmark.style.top = (container.offsetTop + (container.offsetHeight / 2)) + 'px';
            checkmark.style.left = (container.offsetLeft + (container.offsetWidth / 2)) + 'px';

            if (container.nextSibling) {
                parent.insertBefore(checkmark, container.nextSibling);
            } else {
                parent.appendChild(checkmark);
            }
        } else {
            const style = window.getComputedStyle(container);
            if (style.position === 'static') {
                container.style.position = 'relative';
            }
            container.appendChild(checkmark);
        }

        element.dataset.hasCheckmark = 'true';

        if (s.enableBorder) {
            container.dataset.originalBorder = container.style.border || '';
            container.style.border = `${s.borderWidth}px solid ${s.borderColor}`;
        }
    }

    function removeCheckmarksFromElement(element) {
        const id = element.dataset.icContentId;
        const container = getTargetContainer(element);
        
        // Find checkmarks in container or siblings
        const checks = document.querySelectorAll(`.ic-checkmark[data-for-id="${id}"]`);
        checks.forEach(check => {
            // Check if this checkmark belongs to this element (near it)
            // For simple implementation, we check if it's inside the container or a sibling
            if (check.parentNode === container || check.parentNode === container.parentNode) {
                // Restore border
                if (container.dataset.originalBorder !== undefined) {
                    container.style.border = container.dataset.originalBorder;
                    delete container.dataset.originalBorder;
                } else {
                    container.style.border = '';
                }
                check.remove();
            }
        });

        delete element.dataset.hasCheckmark;
    }

    function removeCheckmarksMatching(id) {
        const checks = document.querySelectorAll(`.ic-checkmark[data-for-id="${id}"]`);
        checks.forEach(check => {
            const owners = document.querySelectorAll(`[data-ic-content-id="${id}"]`);
            owners.forEach(owner => {
                const container = getTargetContainer(owner);
                if (container.dataset.originalBorder !== undefined) {
                    container.style.border = container.dataset.originalBorder;
                    delete container.dataset.originalBorder;
                }
                delete owner.dataset.hasCheckmark;
            });
            check.remove();
        });
    }

    function applyCheckmarksToMatching(id) {
        const elements = document.querySelectorAll(`[data-ic-content-id="${id}"]`);
        elements.forEach(el => {
            renderCheckmark(el);
        });
    }

    // --- Observers ---

    function setupObservers() {
        const observer = new MutationObserver((mutations) => {
            let shouldScan = false;
            for (const m of mutations) {
                if (m.addedNodes.length > 0) {
                    shouldScan = true;
                    break;
                }
                if (m.type === 'attributes' && (m.attributeName === 'src' || m.attributeName === 'href')) {
                    shouldScan = true;
                    break;
                }
            }

            if (shouldScan) {
                if (window.scanTimeout) clearTimeout(window.scanTimeout);
                window.scanTimeout = setTimeout(scanPage, 500);
            }
        });

        observer.observe(document.body, { 
            childList: true, 
            subtree: true,
            attributes: true,
            attributeFilter: ['src', 'href'] 
        });

        // YouTube SPA navigation events
        window.addEventListener('yt-navigate-finish', () => {
            if (window.scanTimeout) clearTimeout(window.scanTimeout);
            window.scanTimeout = setTimeout(scanPage, 500);
        });
    }

    // --- Toggles & Messages ---

    function toggleMode(enabled) {
        checkingMode = enabled;
        document.body.dataset.checkingMode = enabled; // Sync with CSS
        const tabId = getTabId();
        chrome.storage.local.set({ [`checkingMode_${tabId}`]: checkingMode });

        if (enabled) {
            showNotification('Image Checker: ON. Click items to mark/unmark.');
        } else {
            showNotification('Image Checker: OFF.', true);
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
            refreshAllCheckmarks();
        } else if (message.action === 'clearAllCheckmarks') {
            seenItems.clear();
            chrome.storage.local.remove('seenItems');
            refreshAllCheckmarks();
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
        const existing = document.querySelector('.image-checker-notification');
        if (existing) existing.remove();

        const n = document.createElement('div');
        n.className = 'image-checker-notification';
        if (isOff) n.classList.add('off');

        n.style.position = 'fixed';
        n.style.top = '30px';
        n.style.left = '50%';
        n.style.transform = 'translateX(-50%)';
        n.style.zIndex = '2147483647';

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
