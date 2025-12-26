let links = [];

const linksList = document.getElementById('links-list');
const emptyState = document.getElementById('empty-state');
const linksContainer = document.getElementById('links-container');
const addBtn = document.getElementById('add-btn');
const addFirstBtn = document.getElementById('add-first-btn');

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

        item.innerHTML = `
            <div class="favicon-box">
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

function saveLinks() {
    chrome.storage.sync.set({ sidebar_links: links }, () => {
        renderLinks();
    });
}

addBtn.addEventListener('click', () => triggerBrowserModal());
addFirstBtn.addEventListener('click', () => triggerBrowserModal());

init();
