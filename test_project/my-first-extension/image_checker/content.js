// Image Checker Content Script
console.log('Image Checker: Content script loaded');
let checkingMode = false;
let checkedImages = new Set();
let pageUrl = window.location.href;
let currentSettings = {
    checkmarkSize: 15,
    checkmarkColor: '#4CAF50',
    textColor: '#ffffff',
    enableBorder: false,
    borderColor: '#4CAF50',
    borderWidth: 3
};

// URL change detection for single-page apps like YouTube
let lastUrl = pageUrl;

function handleUrlChange() {
    const currentUrl = window.location.href;
    if (currentUrl !== lastUrl) {
        console.log('URL changed from', lastUrl, 'to', currentUrl);
        lastUrl = currentUrl;
        pageUrl = currentUrl;
        
        // Clear current checkmarks from display
        clearCurrentCheckmarks();
        checkedImages.clear();
        
        // Load checkmarks for new page after a short delay
        setTimeout(() => {
            loadSavedCheckmarks();
        }, 1000); // Increased delay for YouTube to load content
    }
}

// Listen for browser navigation events
window.addEventListener('popstate', handleUrlChange);

// Override pushState and replaceState to catch programmatic navigation
const originalPushState = history.pushState;
const originalReplaceState = history.replaceState;

history.pushState = function() {
    originalPushState.apply(history, arguments);
    setTimeout(handleUrlChange, 100);
};

history.replaceState = function() {
    originalReplaceState.apply(history, arguments);
    setTimeout(handleUrlChange, 100);
};

// Also check periodically as backup (every 2 seconds)
setInterval(handleUrlChange, 2000);

// F2 key to toggle checking mode
document.addEventListener('keydown', function(event) {
    if (event.key === 'F2') {
        // Toggle the mode
        checkingMode = !checkingMode;
        
        if (checkingMode) {
            enableImageChecking();
            showNotification('Image checking mode started (F2 pressed)');
        } else {
            disableImageChecking();
            showNotification('Image checking mode stopped (F2 pressed)');
        }
        
        // Update storage to reflect the mode change
        const tabId = getTabId();
        chrome.storage.local.set({[`checkingMode_${tabId}`]: checkingMode});
    }
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message) => {
    if (message.action === 'toggleCheckingMode') {
        checkingMode = message.enabled;
        if (checkingMode) {
            enableImageChecking();
        } else {
            disableImageChecking();
        }
    } else if (message.action === 'clearAllCheckmarks') {
        clearAllCheckmarks();
    } else if (message.action === 'updateSettings') {
        currentSettings = message.settings;
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
    loadSavedCheckmarks();
    
    // Check if checking mode was previously enabled for this tab
    const tabId = getTabId();
    chrome.storage.local.get([`checkingMode_${tabId}`], function(result) {
        if (result[`checkingMode_${tabId}`]) {
            checkingMode = true;
            enableImageChecking();
        }
    });
});

// Also initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        loadSettings();
        loadSavedCheckmarks();
    });
} else {
    loadSettings();
    loadSavedCheckmarks();
}

function enableImageChecking() {
    document.body.style.cursor = 'crosshair';
    addImageClickListeners();
    showNotification('Image checking mode enabled! Click on images to mark them.');
}

function disableImageChecking() {
    document.body.style.cursor = 'default';
    removeImageClickListeners();
    showNotification('Image checking mode disabled.');
}

function addImageClickListeners() {
    // Add click listeners to all images, videos, thumbnails, and clickable containers
    const selectors = [
        'img',
        'video',
        '[style*="background-image"]',
        'a',
        // YouTube specific selectors
        'ytd-rich-grid-media',
        'ytd-video-preview',
        'ytd-thumbnail',
        '#thumbnail',
        '.ytd-thumbnail',
        'a[href*="/shorts/"]',
        'a[href*="/watch"]',
        // Generic video thumbnail selectors
        '[class*="thumbnail"]',
        '[class*="video"]',
        '[class*="short"]',
        '[data-testid*="video"]',
        '[data-testid*="thumbnail"]'
    ];
    
    const elements = document.querySelectorAll(selectors.join(', '));
    elements.forEach(element => {
        element.addEventListener('click', handleImageClick, true);
        element.style.cursor = 'pointer';
        // Add visual indicator when hovering
        element.addEventListener('mouseenter', () => {
            if (checkingMode) {
                element.style.outline = '2px solid #4CAF50';
                element.style.outlineOffset = '2px';
            }
        });
        element.addEventListener('mouseleave', () => {
            element.style.outline = '';
            element.style.outlineOffset = '';
        });
    });
    
    // Also handle dynamically loaded content (important for YouTube)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                    // Check if the node itself matches
                    if (node.matches && node.matches(selectors.join(', '))) {
                        addListenerToElement(node);
                        // Check if this element should have a checkmark
                        checkForSavedCheckmark(node);
                    }
                    // Check children too
                    const childElements = node.querySelectorAll(selectors.join(', '));
                    childElements.forEach(element => {
                        addListenerToElement(element);
                        // Check if this element should have a checkmark
                        checkForSavedCheckmark(element);
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

function addListenerToElement(element) {
    element.addEventListener('click', handleImageClick, true);
    element.style.cursor = 'pointer';
    element.addEventListener('mouseenter', () => {
        if (checkingMode) {
            element.style.outline = '2px solid #4CAF50';
            element.style.outlineOffset = '2px';
        }
    });
    element.addEventListener('mouseleave', () => {
        element.style.outline = '';
        element.style.outlineOffset = '';
    });
}

function removeImageClickListeners() {
    const selectors = [
        'img', 
        'video', 
        '[style*="background-image"]',
        'a',
        'ytd-rich-grid-media',
        'ytd-video-preview',
        'ytd-thumbnail',
        '#thumbnail',
        '.ytd-thumbnail',
        'a[href*="/shorts/"]',
        'a[href*="/watch"]',
        '[class*="thumbnail"]',
        '[class*="video"]',
        '[class*="short"]',
        '[data-testid*="video"]',
        '[data-testid*="thumbnail"]'
    ];
    
    const elements = document.querySelectorAll(selectors.join(', '));
    elements.forEach(element => {
        element.removeEventListener('click', handleImageClick, true);
        element.style.cursor = 'default';
        element.style.outline = '';
        element.style.outlineOffset = '';
    });
}

function handleImageClick(event) {
    if (!checkingMode) return;
    
    event.preventDefault();
    event.stopPropagation();
    
    const element = event.target;
    const elementData = getElementData(element);
    
    if (checkedImages.has(elementData.id)) {
        // Remove checkmark
        removeCheckmark(element);
        checkedImages.delete(elementData.id);
        removeFromStorage(elementData);
    } else {
        // Add checkmark
        addCheckmark(element, currentSettings);
        checkedImages.add(elementData.id);
        saveToStorage(elementData);
    }
}

function addCheckmark(element, settings) {
    // Remove existing checkmark if any
    removeCheckmark(element);
    
    const checkmark = document.createElement('div');
    checkmark.className = 'image-checker-checkmark';
    checkmark.innerHTML = '✓';
    
    // The element itself is the target
    let targetElement = element;
    
    const checkmarkSettings = settings || currentSettings;

    // Apply current settings to checkmark
    applyCheckmarkStyles(checkmark, targetElement, checkmarkSettings);
    
    // Apply border if enabled
    if (checkmarkSettings.enableBorder) {
        targetElement.style.border = `${checkmarkSettings.borderWidth}px solid ${checkmarkSettings.borderColor}`;
        targetElement.style.borderRadius = '4px';
    }
    
    document.body.appendChild(checkmark);
    
    // Store reference to checkmark on the element
    const checkmarkId = 'checkmark-' + Date.now() + '-' + Math.random().toString(36).substring(2, 11);
    element.setAttribute('data-checkmark-id', checkmarkId);
    checkmark.id = checkmarkId;
    
    // Update position on scroll
    const updatePosition = () => {
        const newRect = targetElement.getBoundingClientRect();
        const size = Math.min(newRect.width, newRect.height) * (checkmarkSettings.checkmarkSize / 100);
        checkmark.style.left = (newRect.left + window.scrollX + newRect.width / 2 - size / 2) + 'px';
        checkmark.style.top = (newRect.top + window.scrollY + newRect.height / 2 - size / 2) + 'px';
    };
    
    window.addEventListener('scroll', updatePosition);
    window.addEventListener('resize', updatePosition);
    
    // Store cleanup function and target element reference
    checkmark.cleanup = () => {
        window.removeEventListener('scroll', updatePosition);
        window.removeEventListener('resize', updatePosition);
    };
    checkmark.targetElement = targetElement;
    checkmark.settings = checkmarkSettings;
}

function removeCheckmark(element) {
    const checkmarkId = element.getAttribute('data-checkmark-id');
    if (checkmarkId) {
        const existingCheckmark = document.getElementById(checkmarkId);
        if (existingCheckmark) {
            // Remove border from target element
            if (existingCheckmark.targetElement) {
                existingCheckmark.targetElement.style.border = '';
                existingCheckmark.targetElement.style.borderRadius = '';
            }
            
            // Clean up event listeners
            if (existingCheckmark.cleanup) {
                existingCheckmark.cleanup();
            }
            existingCheckmark.remove();
        }
        element.removeAttribute('data-checkmark-id');
    }
}

function clearAllCheckmarks() {
    // Remove all checkmarks
    clearCurrentCheckmarks();
    checkedImages.clear();
    
    // Clear from storage for this page
    clearPageFromStorage();
    
    showNotification('All checkmarks cleared!');
}

function clearCurrentCheckmarks() {
    // Remove all checkmarks from display only (don't affect storage)
    const checkmarks = document.querySelectorAll('.image-checker-checkmark');
    checkmarks.forEach(checkmark => {
        if (checkmark.cleanup) {
            checkmark.cleanup();
        }
        checkmark.remove();
    });
    
    // Clear all data attributes
    const markedElements = document.querySelectorAll('[data-checkmark-id]');
    markedElements.forEach(element => {
        element.removeAttribute('data-checkmark-id');
        // Remove borders too
        element.style.border = '';
        element.style.borderRadius = '';
    });
}

function getElementData(element) {
    let linkUrl = '';
    let elementId = '';

    // Prioritize getting a link URL if the element is a link or inside one
    const linkElement = element.closest('a');
    if (linkElement) {
        linkUrl = linkElement.href;
    }

    // Create a unique identifier for the element
    if (linkUrl) {
        elementId = linkUrl;
    } else if (element.src) {
        elementId = element.src;
    } else if (element.id) {
        elementId = element.id;
    } else {
        // Fallback for elements without a clear unique identifier
        elementId = element.outerHTML.substring(0, 200); // Increased length for more uniqueness
    }

    return {
        id: elementId,
        linkUrl: linkUrl,
        pageUrl: pageUrl,
        timestamp: Date.now()
    };
}

function getTabId() {
    // Simple way to identify current tab (not perfect but works for basic use)
    return window.location.href;
}

function showNotification(message) {
    // Create a temporary notification
    const notification = document.createElement('div');
    notification.className = 'image-checker-notification';
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.background = '#4CAF50';
    notification.style.color = 'white';
    notification.style.padding = '10px 15px';
    notification.style.borderRadius = '5px';
    notification.style.zIndex = '10001';
    notification.style.fontSize = '14px';
    notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Storage functions
function saveToStorage(elementData) {
    elementData.settings = currentSettings; // Add settings immediately
    chrome.storage.local.get(['checkedElements'], function(result) {
        const checkedElements = result.checkedElements || {};
        
        // Use page URL as key
        if (!checkedElements[pageUrl]) {
            checkedElements[pageUrl] = [];
        }

        // Check if element already exists
        const existingIndex = checkedElements[pageUrl].findIndex(item => item.id === elementData.id);
        if (existingIndex === -1) {
            checkedElements[pageUrl].push(elementData);
        }
        
        chrome.storage.local.set({ checkedElements: checkedElements });
    });
}

function removeFromStorage(elementData) {
    chrome.storage.local.get(['checkedElements'], function(result) {
        const checkedElements = result.checkedElements || {};
        
        if (checkedElements[pageUrl]) {
            checkedElements[pageUrl] = checkedElements[pageUrl].filter(item => item.id !== elementData.id);
            
            // Remove page entry if no elements left
            if (checkedElements[pageUrl].length === 0) {
                delete checkedElements[pageUrl];
            }
            
            chrome.storage.local.set({ checkedElements: checkedElements });
        }
    });
}

function clearPageFromStorage() {
    chrome.storage.local.get(['checkedElements'], function(result) {
        const checkedElements = result.checkedElements || {};
        delete checkedElements[pageUrl];
        chrome.storage.local.set({ checkedElements: checkedElements });
    });
}

function loadSavedCheckmarks() {
    chrome.storage.local.get(['checkedElements'], function(result) {
        const checkedElements = result.checkedElements || {};
        const pageElements = checkedElements[pageUrl] || [];
        
        // Wait a bit for page to load, then restore checkmarks
        setTimeout(() => {
            pageElements.forEach(elementData => {
                const element = findElementByData(elementData);
                if (element) {
                    addCheckmark(element, elementData.settings);
                    checkedImages.add(elementData.id);
                }
            });
        }, 1000);
    });
}

function checkForSavedCheckmark(element) {
    // Check if this specific element should have a checkmark
    chrome.storage.local.get(['checkedElements'], function(result) {
        const checkedElements = result.checkedElements || {};
        const pageElements = checkedElements[pageUrl] || [];
        
        // Create element data for this element to compare
        const elementData = getElementData(element);
        
        // Check if this element is in our saved list
        const savedElementData = pageElements.find(saved => saved.id === elementData.id);
        
        if (savedElementData && !element.getAttribute('data-checkmark-id')) {
            // Element should be marked but isn't yet
            addCheckmark(element, savedElementData.settings);
            checkedImages.add(elementData.id);
        }
    });
}

function findElementByData(elementData) {
    // Try to find element by various methods
    if (elementData.linkUrl) {
        // Look for exact href match first
        let linkElement = document.querySelector(`a[href="${elementData.linkUrl}"]`);
        if (linkElement) return linkElement;
        
        // YouTube sometimes changes URLs slightly, so try partial match
        const videoId = extractVideoId(elementData.linkUrl);
        if (videoId) {
            linkElement = document.querySelector(`a[href*="${videoId}"]`);
            if (linkElement) return linkElement;
        }
    }
    
    if (elementData.id.startsWith('http')) {
        const imgElement = document.querySelector(`img[src="${elementData.id}"]`);
        if (imgElement) return imgElement;
    }
    
    // Try to find by ID
    const idElement = document.getElementById(elementData.id);
    if (idElement) return idElement;
    
    return null;
}

function extractVideoId(url) {
    // Extract video ID from YouTube URL for better matching
    const match = url.match(/(?:shorts\/|watch\?v=)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
}

function applyCheckmarkStyles(checkmark, targetElement, settings) {
    const rect = targetElement.getBoundingClientRect();
    const checkmarkSettings = settings || currentSettings;
    const size = Math.min(rect.width, rect.height) * (checkmarkSettings.checkmarkSize / 100);
    
    checkmark.style.position = 'absolute';
    checkmark.style.left = (rect.left + window.scrollX + rect.width / 2 - size / 2) + 'px';
    checkmark.style.top = (rect.top + window.scrollY + rect.height / 2 - size / 2) + 'px';
    checkmark.style.width = size + 'px';
    checkmark.style.height = size + 'px';
    checkmark.style.background = checkmarkSettings.checkmarkColor;
    checkmark.style.color = checkmarkSettings.textColor;
    checkmark.style.fontSize = (size * 0.6) + 'px';
    checkmark.style.zIndex = '10000';
    checkmark.style.borderRadius = '50%';
    checkmark.style.display = 'flex';
    checkmark.style.alignItems = 'center';
    checkmark.style.justifyContent = 'center';
    checkmark.style.fontWeight = 'bold';
    checkmark.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
    checkmark.style.border = '2px solid white';
}

function loadSettings() {
    chrome.storage.local.get(['imageCheckerSettings'], function(result) {
        if (result.imageCheckerSettings) {
            currentSettings = result.imageCheckerSettings;
        }
    });
}

