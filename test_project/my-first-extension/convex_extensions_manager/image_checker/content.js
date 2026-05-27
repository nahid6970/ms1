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
    let lastPressToggle = {
        id: null,
        time: 0
    };
    let currentSettings = {
        checkmarkSize: 15,
        checkmarkColor: '#4CAF50',
        textColor: '#ffffff',
        hideCheckmarks: false,
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
        loadSettings().then(() => {
            loadSeenItems().then(() => {
                // Initial scan
                scanPage();

                // Watch for changes (YouTube/SPA navigation + Infinite Scroll)
                setupObservers();

                // Check if mode should be active
                const modeKey = getModeStorageKey();
                chrome.storage.local.get([modeKey], function (result) {
                    if (result[modeKey]) {
                        toggleMode(true);
                    }
                });
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

    function getVisualSource(element) {
        if (!element || element.nodeType !== 1) return null;

        if (element.tagName === 'IMG') {
            return element.currentSrc || element.src || null;
        }

        if (element.tagName === 'VIDEO') {
            return element.currentSrc || element.src || null;
        }

        if (element.style && element.style.backgroundImage && element.style.backgroundImage !== 'none') {
            const bg = element.style.backgroundImage.slice(5, -2).replace(/['"]/g, "");
            return bg || null;
        }

        return null;
    }

    function normalizeMediaUrl(rawUrl) {
        if (!rawUrl) return null;
        try {
            const parsed = new URL(rawUrl, location.href);
            const host = parsed.hostname.toLowerCase();

            // fbcdn links rotate query params frequently; keep stable identity by origin + path.
            if (host.includes('fbcdn.net')) {
                return `${parsed.origin}${parsed.pathname}`;
            }

            parsed.hash = '';
            return parsed.toString();
        } catch {
            return rawUrl.split('#')[0];
        }
    }

    function findVisualMediaElement(element) {
        if (!element || element.nodeType !== 1) return null;

        const directSource = getVisualSource(element);
        if (directSource) return element;

        if (!isLikelyInteractiveWrapper(element)) return null;

        const candidates = element.querySelectorAll('img, video, [style*="background-image"]');
        let bestCandidate = null;
        let bestArea = 0;

        candidates.forEach(candidate => {
            const source = getVisualSource(candidate);
            if (!source) return;

            const area = (candidate.offsetWidth || 0) * (candidate.offsetHeight || 0);
            if (area > bestArea) {
                bestArea = area;
                bestCandidate = candidate;
            }
        });

        return bestCandidate;
    }

    function isLikelyInteractiveWrapper(element) {
        if (!element || element.nodeType !== 1) return false;

        return element.matches(
            'a, button, [role="button"], [role="link"], [role="gridcell"], [tabindex], ytd-thumbnail, ytd-playlist-thumbnail, .ytd-thumbnail'
        );
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

    function markElementAsSeen(element, id) {
        markAsSeen(id);
        if (element && element.dataset.hasCheckmark !== 'true') {
            renderCheckmark(element);
        }
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
        const visualElement = findVisualMediaElement(element);
        if (visualElement) {
            const mediaSource = normalizeMediaUrl(getVisualSource(visualElement));
            if (mediaSource) return `media|${mediaSource}`;
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

    function resolveInteractiveElement(startNode) {
        let element = startNode && startNode.nodeType === 1 ? startNode : startNode?.parentElement;

        while (element && element !== document.body) {
            if (getVisualSource(element)) return element;

            if (isLikelyInteractiveWrapper(element) && findVisualMediaElement(element)) {
                return element;
            }

            if (element.tagName === 'A' && element.href) {
                return element;
            }

            element = element.parentElement;
        }

        return null;
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
        refreshToggleButtons();
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

        // Add direct listeners too; Facebook often targets the media node inside a wrapper.
        if (element.dataset.icListenersAdded !== 'true') {
            element.addEventListener('pointerdown', handleInteractivePointerDown, true);
            element.addEventListener('mousedown', handleInteractivePointerDown, true);
            element.addEventListener('click', handleInteractiveClick, true);
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

        refreshToggleButtons();
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
        if (currentSettings.hideCheckmarks) {
            document.body.classList.add('ic-hide-checkmarks');
        } else {
            document.body.classList.remove('ic-hide-checkmarks');
        }

        document.querySelectorAll('.ic-checkmark').forEach(c => {
            const container = getCheckmarkOwnerContainer(c);
            if (container && container.dataset.originalBorder !== undefined) {
                container.style.border = container.dataset.originalBorder;
                delete container.dataset.originalBorder;
            }
            if (container) delete container.dataset.icHasBorder;
            c.remove();
        });
        document.querySelectorAll('[data-ic-processed="true"]').forEach(el => {
            delete el.dataset.hasCheckmark;
            const id = el.dataset.icContentId;
            if (id && seenItems.has(id)) {
                renderCheckmark(el);
            }
        });
        refreshToggleButtons();
    }

    function handleInteractivePointerDown(event) {
        if (!checkingMode) return;
        if (event.button !== undefined && event.button !== 0) return;

        const element = event.currentTarget?.dataset?.icContentId
            ? event.currentTarget
            : resolveInteractiveElement(event.target);
        if (!element) return;

        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === 'function') {
            event.stopImmediatePropagation();
        }

        toggleElementCheckmark(element);
    }

    function handleInteractiveClick(event) {
        if (!checkingMode) return;
        if (event.button !== undefined && event.button !== 0) return;

        const element = event.currentTarget?.dataset?.icContentId
            ? event.currentTarget
            : resolveInteractiveElement(event.target);
        if (!element) return;

        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === 'function') {
            event.stopImmediatePropagation();
        }

        if (element.dataset.icContentId === lastPressToggle.id && Date.now() - lastPressToggle.time < 600) {
            return;
        }

        toggleElementCheckmark(element);
    }

    function toggleElementCheckmark(element) {
        if (element.dataset.icProcessed !== 'true') {
            processElement(element);
        }

        const id = element.dataset.icContentId;
        if (!id) return;

        lastPressToggle = {
            id,
            time: Date.now()
        };

        if (seenItems.has(id)) {
            markAsUnseen(id);
        } else {
            markElementAsSeen(element, id);
        }

        refreshToggleButtons();
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

    function getCheckmarkOwnerContainer(checkmark) {
        const ownerId = checkmark?.dataset?.ownerId;
        if (!ownerId) return null;

        const owners = getProcessedElementsById(ownerId);
        if (!owners.length) return null;

        return getTargetContainer(owners[0]);
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

        const rect = container.getBoundingClientRect();
        const baseDimension = Math.min(rect.width, rect.height) || 100;
        const calculatedSize = Math.max(20, baseDimension * (s.checkmarkSize / 100));

        Object.assign(checkmark.style, {
            position: 'fixed',
            top: `${Math.max(0, rect.top + (rect.height / 2) - (calculatedSize / 2))}px`,
            left: `${Math.max(0, rect.left + (rect.width / 2) - (calculatedSize / 2))}px`,
            transform: 'none',
            zIndex: '2147483647',
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

        document.body.appendChild(checkmark);

        element.dataset.hasCheckmark = 'true';

        if (s.enableBorder) {
            container.dataset.originalBorder = container.style.border || '';
            container.style.border = `${s.borderWidth}px solid ${s.borderColor}`;
            container.dataset.icHasBorder = 'true';
        }
    }

    function removeCheckmarksFromElement(element) {
        const id = element.dataset.icContentId;
        const container = getTargetContainer(element);
        
        const checks = getCheckmarksById(id);
        checks.forEach(check => {
            if (container.dataset.originalBorder !== undefined) {
                container.style.border = container.dataset.originalBorder;
                delete container.dataset.originalBorder;
            } else {
                container.style.border = '';
            }
            check.remove();
        });

        delete element.dataset.hasCheckmark;
    }

    function removeCheckmarksMatching(id) {
        const checks = getCheckmarksById(id);
        checks.forEach(check => {
            const owners = getProcessedElementsById(id);
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
        getProcessedElementsById(id).forEach(renderCheckmark);
    }

    function getProcessedElementsById(id) {
        return Array.from(document.querySelectorAll('[data-ic-content-id]'))
            .filter(el => el.dataset.icContentId === id);
    }

    function getCheckmarksById(id) {
        return Array.from(document.querySelectorAll('.ic-checkmark'))
            .filter(el => el.dataset.forId === id);
    }

    function refreshToggleButtons() {
        document.querySelectorAll('.ic-toggle-button').forEach(button => button.remove());

        if (!checkingMode) return;

        const renderedIds = new Set();
        getVisibleProcessedElements().forEach(element => {
            const id = element.dataset.icContentId;
            if (!id || renderedIds.has(id)) return;

            const rect = getTargetContainer(element).getBoundingClientRect();
            if (rect.width < 40 || rect.height < 40) return;

            renderedIds.add(id);
            renderToggleButton(element, id, rect);
        });
    }

    function getVisibleProcessedElements() {
        return Array.from(document.querySelectorAll('[data-ic-processed="true"]'))
            .filter(element => {
                const rect = getTargetContainer(element).getBoundingClientRect();
                return rect.bottom > 0 &&
                    rect.right > 0 &&
                    rect.top < window.innerHeight &&
                    rect.left < window.innerWidth;
            });
    }

    function renderToggleButton(element, id, rect) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'ic-toggle-button';
        button.textContent = seenItems.has(id) ? '✓' : '';
        button.title = seenItems.has(id) ? 'Unmark item' : 'Mark item';
        button.dataset.forId = id;

        Object.assign(button.style, {
            position: 'fixed',
            top: `${Math.max(8, rect.top + 8)}px`,
            left: `${Math.max(8, rect.left + 8)}px`,
            zIndex: '2147483647',
            width: '30px',
            height: '30px',
            border: `2px solid ${currentSettings.checkmarkColor}`,
            borderRadius: '6px',
            background: seenItems.has(id) ? currentSettings.checkmarkColor : 'rgba(0, 0, 0, 0.65)',
            color: currentSettings.textColor,
            fontSize: '20px',
            fontWeight: '700',
            lineHeight: '24px',
            padding: '0',
            margin: '0',
            cursor: 'pointer',
            pointerEvents: 'auto',
            boxShadow: '0 2px 8px rgba(0,0,0,0.55)'
        });

        ['pointerdown', 'mousedown', 'click'].forEach(type => {
            button.addEventListener(type, event => {
                event.preventDefault();
                event.stopPropagation();
                if (typeof event.stopImmediatePropagation === 'function') {
                    event.stopImmediatePropagation();
                }

                if (type === 'click') {
                    toggleElementCheckmark(element);
                }
            }, true);
        });

        document.body.appendChild(button);
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

        document.addEventListener('pointerdown', handleInteractivePointerDown, true);
        document.addEventListener('mousedown', handleInteractivePointerDown, true);
        document.addEventListener('click', handleInteractiveClick, true);
        window.addEventListener('scroll', () => requestAnimationFrame(refreshToggleButtons), true);
        window.addEventListener('resize', () => requestAnimationFrame(refreshToggleButtons), true);

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
        const modeKey = getModeStorageKey();
        chrome.storage.local.set({ [modeKey]: checkingMode });

        if (enabled) {
            showNotification('Image Checker: ON. Click items to mark/unmark.');
            scanPage();
            refreshToggleButtons();
        } else {
            showNotification('Image Checker: OFF.', true);
            refreshToggleButtons();
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
    function getModeStorageKey() { return 'checkingMode_global'; }

    function loadSettings() {
        return new Promise((resolve) => {
            chrome.storage.local.get(['imageCheckerSettings'], function (result) {
                if (result.imageCheckerSettings) {
                    currentSettings = result.imageCheckerSettings;
                    if (currentSettings.hideCheckmarks) {
                        document.body.classList.add('ic-hide-checkmarks');
                    }
                }
                resolve();
            });
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
