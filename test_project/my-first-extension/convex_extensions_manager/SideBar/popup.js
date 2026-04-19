let links = [];
let globalSettings = {
    itemsPerRow: 4,
    extraPadding: 20,
    iconSize: 28,
    borderRadius: 8,
    borderOpacity: 100
};

const linksList = document.getElementById('links-list');
const emptyState = document.getElementById('empty-state');
const linksContainer = document.getElementById('links-container');
const addBtn = document.getElementById('add-btn');
const settingsBtn = document.getElementById('settings-btn');
const addFirstBtn = document.getElementById('add-first-btn');
const saveToConvexBtn = document.getElementById('saveToConvex');
const loadFromConvexBtn = document.getElementById('loadFromConvex');
const reloadBtn = document.getElementById('reload-extension');

// Context Menu Elements
const contextMenu = document.getElementById('context-menu');
const ctxEdit = document.getElementById('ctx-edit');
const ctxDelete = document.getElementById('ctx-delete');
let currentRightClickedLinkId = null;

// Initial Load
const CACHE_KEYS = ['sidebar_links', 'itemsPerRow', 'extraPadding', 'iconSize', 'borderRadius', 'borderOpacity'];

function applyResult(result) {
    globalSettings = {
        itemsPerRow: result.itemsPerRow || 4,
        extraPadding: result.extraPadding || 20,
        iconSize: result.iconSize || 28,
        borderRadius: result.borderRadius !== undefined ? result.borderRadius : 8,
        borderOpacity: result.borderOpacity !== undefined ? result.borderOpacity : 100
    };
    if (result.sidebar_links && result.sidebar_links.length > 0) {
        links = result.sidebar_links;
        applyGridLayout(globalSettings.itemsPerRow, globalSettings.extraPadding);
        renderLinks();
    } else {
        showEmptyState(true);
    }
}

function init() {
    chrome.storage.session.get(CACHE_KEYS, (cached) => {
        if (cached.sidebar_links) applyResult(cached);
        chrome.storage.local.get(CACHE_KEYS, (result) => {
            chrome.storage.session.set(result);
            if (!cached.sidebar_links) applyResult(result);
        });
    });

    // Close context menu on any click
    document.addEventListener('click', () => {
        contextMenu.classList.remove('visible');
    });

    // Handle Context Menu Actions
    ctxEdit.addEventListener('click', () => {
        const link = links.find(l => l.id === currentRightClickedLinkId);
        if (link) triggerBrowserModal(link);
    });

    ctxDelete.addEventListener('click', () => {
        links = links.filter(l => l.id !== currentRightClickedLinkId);
        saveLinks();
    });
}

// Apply grid layout based on items per row
function applyGridLayout(itemsPerRow, extraPadding = 20) {
    const itemSize = 56; // favicon box size
    const gap = 12;
    const containerPaddingLeft = 20; // from CSS .container padding
    const containerPaddingRight = 20; // from CSS .container padding
    const minWidth = 320; // minimum width to show all header buttons
    
    let popupWidth = (itemSize * itemsPerRow) + (gap * (itemsPerRow - 1)) + containerPaddingLeft + containerPaddingRight + extraPadding;
    popupWidth = Math.max(popupWidth, minWidth);
    document.body.style.width = `${popupWidth}px`;
    linksList.style.gridTemplateColumns = `repeat(${itemsPerRow}, 1fr)`;
}

// Listen for updates from other contexts
chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === 'local') {
        // Keep session cache in sync
        const update = {};
        Object.keys(changes).forEach(k => { update[k] = changes[k].newValue; });
        chrome.storage.session.set(update);
        let needsReRender = false;
        
        if (changes.sidebar_links) {
            links = changes.sidebar_links.newValue || [];
            needsReRender = true;
        }
        
        // Update global settings
        ['itemsPerRow', 'extraPadding', 'iconSize', 'borderRadius', 'borderOpacity'].forEach(key => {
            if (changes[key]) {
                globalSettings[key] = changes[key].newValue;
                if (key === 'itemsPerRow' || key === 'extraPadding') {
                    applyGridLayout(globalSettings.itemsPerRow, globalSettings.extraPadding);
                }
                needsReRender = true;
            }
        });

        if (needsReRender) renderLinks();
    }
});

// Listen for settings updates via message
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'settings_updated') {
        chrome.storage.local.get(['itemsPerRow', 'extraPadding', 'iconSize', 'borderRadius', 'borderOpacity'], (result) => {
            globalSettings = {
                itemsPerRow: result.itemsPerRow || 4,
                extraPadding: result.extraPadding || 20,
                iconSize: result.iconSize || 28,
                borderRadius: result.borderRadius !== undefined ? result.borderRadius : 8,
                borderOpacity: result.borderOpacity !== undefined ? result.borderOpacity : 100
            };
            applyGridLayout(globalSettings.itemsPerRow, globalSettings.extraPadding);
            renderLinks();
        });
    }
});

function showEmptyState(show) {
    if (show) {
        emptyState.classList.remove('hidden');
        linksList.classList.add('hidden');
    } else {
        emptyState.classList.add('hidden');
        linksList.classList.remove('hidden');
    }
}

function renderLinks() {
    if (links.length === 0) {
        showEmptyState(true);
        return;
    }

    showEmptyState(false);
    const fragment = document.createDocumentFragment();

    links.forEach((link) => {
        const item = document.createElement('div');
        item.className = 'link-item';
        if (link.newLine) {
            item.classList.add('new-line');
        }
        item.draggable = true;

        // Calculate Border Color based on Opacity
        const opacityHex = Math.round((globalSettings.borderOpacity / 100) * 255).toString(16).padStart(2, '0');
        const borderColor = link.color ? `${link.color}${opacityHex}` : `rgba(51, 51, 51, ${globalSettings.borderOpacity / 100})`;
        const shadowColor = link.color ? `${link.color}${Math.round((globalSettings.borderOpacity / 100) * 0.4 * 255).toString(16).padStart(2, '0')}` : `rgba(0, 0, 0, ${globalSettings.borderOpacity / 100 * 0.3})`;

        // Define Icon Styles
        let iconBoxStyle = `border-radius: ${globalSettings.borderRadius}px; border-color: ${borderColor};`;
        
        if (link.color) {
            if (link.isSolid) {
                iconBoxStyle += `background: ${link.color}; box-shadow: 0 4px 10px ${shadowColor};`;
            } else {
                iconBoxStyle += `background: ${link.color}15; box-shadow: 0 0 15px ${shadowColor};`;
            }
        }
        
        // If opacity is 0, make border truly invisible
        if (globalSettings.borderOpacity === 0) {
            iconBoxStyle += "border-width: 0;";
        }

        const imgStyle = `width: ${globalSettings.iconSize}px; height: ${globalSettings.iconSize}px;`;

        item.innerHTML = `
            <div class="favicon-box" style="${iconBoxStyle}">
                <img src="${link.icon || ''}" style="${imgStyle}" onerror="this.src='https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=${link.url}&size=64'">
            </div>
        `;

        // Left Click to Open
        item.addEventListener('click', (e) => {
            window.open(link.url, '_blank');
        });

        // Right Click for Context Menu
        item.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            currentRightClickedLinkId = link.id;

            contextMenu.style.left = `${e.clientX}px`;
            contextMenu.style.top = `${e.clientY}px`;
            contextMenu.classList.add('visible');

            const menuBounds = contextMenu.getBoundingClientRect();
            if (menuBounds.right > window.innerWidth) {
                contextMenu.style.left = `${e.clientX - menuBounds.width}px`;
            }
            if (menuBounds.bottom > window.innerHeight) {
                contextMenu.style.top = `${e.clientY - menuBounds.height}px`;
            }
        });

        // Drag and Drop
        item.addEventListener('dragstart', (e) => {
            item.classList.add('dragging');
            e.dataTransfer.setData('text/plain', link.id);
        });

        item.addEventListener('dragend', () => item.classList.remove('dragging'));
        item.addEventListener('dragover', (e) => e.preventDefault());

        item.addEventListener('drop', (e) => {
            e.preventDefault();
            const draggedId = e.dataTransfer.getData('text/plain');
            if (draggedId === link.id) return;

            const draggedIndex = links.findIndex(l => l.id === draggedId);
            const targetIndex = links.findIndex(l => l.id === link.id);

            if (draggedIndex !== -1 && targetIndex !== -1) {
                const [draggedItem] = links.splice(draggedIndex, 1);
                links.splice(targetIndex, 0, draggedItem);
                saveLinks();
            }
        });

        fragment.appendChild(item);
    });

    linksList.innerHTML = '';
    linksList.appendChild(fragment);
}

function triggerBrowserModal(editLink = null) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'open_modal',
                link: editLink
            }).catch(err => {
                alert('Please visit a webpage (not a Chrome settings page) to use the Add/Edit form.');
            });
            window.close();
        }
    });
}

function triggerSettingsModal() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'open_settings'
            }).catch(err => {
                alert('Please visit a webpage to use Settings.');
            });
            window.close();
        }
    });
}

function saveLinks() {
    chrome.storage.local.set({ sidebar_links: links }, () => {
        renderLinks();
    });
}

addBtn.addEventListener('click', () => triggerBrowserModal());
settingsBtn.addEventListener('click', () => triggerSettingsModal());
addFirstBtn.addEventListener('click', () => triggerBrowserModal());

if (reloadBtn) {
    reloadBtn.addEventListener('click', () => {
        chrome.runtime.reload();
    });
}

// Save to Convex button handler
if (saveToConvexBtn) {
    saveToConvexBtn.addEventListener('click', function () {
        const originalContent = saveToConvexBtn.innerHTML;
        saveToConvexBtn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18Z" /></svg>`;
        saveToConvexBtn.classList.add('loading');
        
        chrome.storage.local.get(null, function (items) {
            chrome.runtime.sendMessage({
                action: 'saveToConvex',
                data: items
            }, function (response) {
                saveToConvexBtn.classList.remove('loading');
                if (response && response.success !== false) {
                    saveToConvexBtn.classList.add('success');
                    saveToConvexBtn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" /></svg>`;
                    setTimeout(() => {
                        saveToConvexBtn.innerHTML = originalContent;
                        saveToConvexBtn.classList.remove('success');
                    }, 2000);
                } else {
                    saveToConvexBtn.classList.add('error');
                    setTimeout(() => {
                        saveToConvexBtn.innerHTML = originalContent;
                        saveToConvexBtn.classList.remove('error');
                    }, 2000);
                }
            });
        });
    });
}

// Load from Convex button handler
if (loadFromConvexBtn) {
    loadFromConvexBtn.addEventListener('click', function () {
        const originalContent = loadFromConvexBtn.innerHTML;
        loadFromConvexBtn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18Z" /></svg>`;
        loadFromConvexBtn.classList.add('loading');

        chrome.runtime.sendMessage({
            action: 'loadFromConvex'
        }, function (response) {
            loadFromConvexBtn.classList.remove('loading');
            
            // Be more lenient with what we consider "valid" data (must be a truthy object)
            if (response && response.success !== false && response.data && typeof response.data === 'object') {
                chrome.storage.local.clear(() => {
                chrome.storage.local.set(response.data, () => {
                    loadFromConvexBtn.classList.add('success');
                    loadFromConvexBtn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" /></svg>`;
                    
                    if (response.data.sidebar_links) {
                        links = response.data.sidebar_links;
                    }

                    // Update global settings from restored data
                    ['itemsPerRow', 'extraPadding', 'iconSize', 'borderRadius', 'borderOpacity'].forEach(key => {
                        if (response.data[key] !== undefined) {
                            globalSettings[key] = response.data[key];
                        }
                    });

                    applyGridLayout(globalSettings.itemsPerRow, globalSettings.extraPadding);
                    renderLinks();

                    setTimeout(() => {
                        loadFromConvexBtn.innerHTML = originalContent;
                        loadFromConvexBtn.classList.remove('success');
                    }, 2000);
                });
                });
            } else {
                console.error('Restore failed or no data found:', response);
                loadFromConvexBtn.classList.add('error');
                setTimeout(() => {
                    loadFromConvexBtn.innerHTML = originalContent;
                    loadFromConvexBtn.classList.remove('error');
                }, 2000);
            }
        });
    });
}

init();