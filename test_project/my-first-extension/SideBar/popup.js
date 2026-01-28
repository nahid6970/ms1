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
    linksList.innerHTML = '';

    if (links.length === 0) {
        showEmptyState(true);
        return;
    }

    showEmptyState(false);

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
                <img src="${link.icon || ''}" onerror="this.src='https://www.google.com/s2/favicons?domain=google.com&sz=64'">
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

        linksList.appendChild(item);
    });
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
        saveToPythonBtn.innerHTML = '...';
        
        chrome.storage.sync.get(null, function (items) {
            chrome.runtime.sendMessage({
                action: 'saveToPython',
                data: items
            }, function (response) {
                if (response && response.success !== false) {
                    saveToPythonBtn.style.color = '#4CAF50';
                    setTimeout(() => {
                        saveToPythonBtn.innerHTML = originalContent;
                        saveToPythonBtn.style.color = '';
                    }, 2000);
                } else {
                    saveToPythonBtn.style.color = '#f44336';
                    setTimeout(() => {
                        saveToPythonBtn.innerHTML = originalContent;
                        saveToPythonBtn.style.color = '';
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
        loadFromPythonBtn.innerHTML = '...';

        chrome.runtime.sendMessage({
            action: 'loadFromPython'
        }, function (response) {
            if (response && response.success !== false && response.data) {
                chrome.storage.sync.set(response.data, () => {
                    loadFromPythonBtn.style.color = '#4CAF50';
                    // Update local links and re-render
                    if (response.data.sidebar_links) {
                        links = response.data.sidebar_links;
                        renderLinks();
                    }
                    setTimeout(() => {
                        loadFromPythonBtn.innerHTML = originalContent;
                        loadFromPythonBtn.style.color = '';
                    }, 2000);
                });
            } else {
                loadFromPythonBtn.style.color = '#f44336';
                setTimeout(() => {
                    loadFromPythonBtn.innerHTML = originalContent;
                    loadFromPythonBtn.style.color = '';
                }, 2000);
            }
        });
    });
}

init();
