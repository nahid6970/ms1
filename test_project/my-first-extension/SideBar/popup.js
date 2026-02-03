let links = [];

const linksList = document.getElementById('links-list');
const emptyState = document.getElementById('empty-state');
const linksContainer = document.getElementById('links-container');
const addBtn = document.getElementById('add-btn');
const settingsBtn = document.getElementById('settings-btn');
const addFirstBtn = document.getElementById('add-first-btn');
const saveToPythonBtn = document.getElementById('saveToPython');
const loadFromPythonBtn = document.getElementById('loadFromPython');
const reloadBtn = document.getElementById('reload-extension');

// Context Menu Elements
const contextMenu = document.getElementById('context-menu');
const ctxEdit = document.getElementById('ctx-edit');
const ctxDelete = document.getElementById('ctx-delete');
let currentRightClickedLinkId = null;

// Initial Load
function init() {
    chrome.storage.sync.get(['sidebar_links'], (result) => {
        if (result.sidebar_links && result.sidebar_links.length > 0) {
            links = result.sidebar_links;
            renderLinks();
        } else {
            showEmptyState(true);
        }
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

// Listen for updates from other contexts (like background script context menu)
chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === 'sync' && changes.sidebar_links) {
        links = changes.sidebar_links.newValue || [];
        renderLinks();
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
        item.draggable = true;

        // Define Icon Styles
        const iconStyle = link.color ? (link.isSolid
            ? `background: ${link.color}; border-color: ${link.color}; box-shadow: 0 4px 10px ${link.color}66;`
            : `border-color: ${link.color}; box-shadow: 0 0 15px ${link.color}44; background: ${link.color}15;`)
            : '';

        item.innerHTML = `
            <div class="favicon-box" style="${iconStyle}">
                <img src="${link.icon || ''}" onerror="this.src='https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=${link.url}&size=64'">
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

            // Prevent menu from going off-screen
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
            window.close(); // Close popup when modal opens in browser
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
    chrome.storage.sync.set({ sidebar_links: links }, () => {
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

// Save to Python server button handler
if (saveToPythonBtn) {
    saveToPythonBtn.addEventListener('click', function () {
        const originalContent = saveToPythonBtn.innerHTML;
        // Show spinning sync icon
        saveToPythonBtn.innerHTML = `
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18Z" />
            </svg>`;
        saveToPythonBtn.classList.add('loading');
        
        chrome.storage.sync.get(null, function (items) {
            chrome.runtime.sendMessage({
                action: 'saveToPython',
                data: items
            }, function (response) {
                saveToPythonBtn.classList.remove('loading');
                if (response && response.success !== false) {
                    saveToPythonBtn.classList.add('success');
                    saveToPythonBtn.innerHTML = `
                        <svg viewBox="0 0 24 24" width="16" height="16">
                            <path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" />
                        </svg>`;
                    setTimeout(() => {
                        saveToPythonBtn.innerHTML = originalContent;
                        saveToPythonBtn.classList.remove('success');
                    }, 2000);
                } else {
                    saveToPythonBtn.classList.add('error');
                    setTimeout(() => {
                        saveToPythonBtn.innerHTML = originalContent;
                        saveToPythonBtn.classList.remove('error');
                    }, 2000);
                }
            });
        });
    });
}

// Load from Python server button handler
if (loadFromPythonBtn) {
    loadFromPythonBtn.addEventListener('click', function () {
        const originalContent = loadFromPythonBtn.innerHTML;
        // Show spinning sync icon
        loadFromPythonBtn.innerHTML = `
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18Z" />
            </svg>`;
        loadFromPythonBtn.classList.add('loading');

        chrome.runtime.sendMessage({
            action: 'loadFromPython'
        }, function (response) {
            loadFromPythonBtn.classList.remove('loading');
            if (response && response.success !== false && response.data) {
                chrome.storage.sync.set(response.data, () => {
                    loadFromPythonBtn.classList.add('success');
                    loadFromPythonBtn.innerHTML = `
                        <svg viewBox="0 0 24 24" width="16" height="16">
                            <path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" />
                        </svg>`;
                    // Update local links and re-render
                    if (response.data.sidebar_links) {
                        links = response.data.sidebar_links;
                        renderLinks();
                    }
                    setTimeout(() => {
                        loadFromPythonBtn.innerHTML = originalContent;
                        loadFromPythonBtn.classList.remove('success');
                    }, 2000);
                });
            } else {
                loadFromPythonBtn.classList.add('error');
                setTimeout(() => {
                    loadFromPythonBtn.innerHTML = originalContent;
                    loadFromPythonBtn.classList.remove('error');
                }, 2000);
            }
        });
    });
}

init();
