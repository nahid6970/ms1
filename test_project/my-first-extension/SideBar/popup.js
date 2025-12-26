let links = [];

const linksList = document.getElementById('links-list');
const emptyState = document.getElementById('empty-state');
const linksContainer = document.getElementById('links-container');
const addBtn = document.getElementById('add-btn');
const addFirstBtn = document.getElementById('add-first-btn');
const modalOverlay = document.getElementById('modal-overlay');
const modalTitle = document.getElementById('modal-title');
const cancelBtn = document.getElementById('cancel-btn');
const saveBtn = document.getElementById('save-btn');
const titleInput = document.getElementById('title-input');
const urlInput = document.getElementById('url-input');
const colorInput = document.getElementById('color-input');
const solidInput = document.getElementById('solid-input');
const editIdInput = document.getElementById('edit-id');

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
}

function showEmptyState(show) {
    if (show) {
        emptyState.classList.remove('hidden');
        linksContainer.classList.add('hidden');
    } else {
        emptyState.classList.add('hidden');
        linksContainer.classList.remove('hidden');
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
            <div class="item-actions">
                <button class="action-btn edit-btn" title="Edit">
                    <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z" /></svg>
                </button>
                <button class="action-btn delete-btn delete" title="Delete">
                    <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19V4M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" /></svg>
                </button>
            </div>
        `;

        // Click to Open
        item.addEventListener('click', (e) => {
            if (e.target.closest('.action-btn')) return;
            window.open(link.url, '_blank');
        });

        // Edit button
        item.querySelector('.edit-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            openModal(link);
        });

        // Delete button
        item.querySelector('.delete-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            links = links.filter(l => l.id !== link.id);
            saveLinks();
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

function openModal(editLink = null) {
    if (editLink) {
        modalTitle.textContent = 'Edit Link';
        editIdInput.value = editLink.id;
        titleInput.value = editLink.title;
        urlInput.value = editLink.url;
        colorInput.value = editLink.color || '#38bdf8';
        solidInput.checked = editLink.isSolid || false;
    } else {
        modalTitle.textContent = 'New Link';
        editIdInput.value = '';
        titleInput.value = '';
        urlInput.value = '';
        colorInput.value = '#38bdf8';
        solidInput.checked = false;
    }
    modalOverlay.classList.add('visible');
    titleInput.focus();
}

function saveLinks() {
    chrome.storage.sync.set({ sidebar_links: links }, () => {
        renderLinks();
    });
}

addBtn.addEventListener('click', () => openModal());
addFirstBtn.addEventListener('click', () => openModal());
cancelBtn.addEventListener('click', () => modalOverlay.classList.remove('visible'));

modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) modalOverlay.classList.remove('visible');
});

saveBtn.addEventListener('click', () => {
    const title = titleInput.value.trim();
    let url = urlInput.value.trim();
    const color = colorInput.value;
    const isSolid = solidInput.checked;
    const editId = editIdInput.value;

    if (!url) return;
    if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

    let domain;
    try {
        domain = new URL(url).hostname;
    } catch (e) {
        alert('Please enter a valid URL');
        return;
    }

    const linkData = {
        title: title || domain,
        url: url,
        color: color,
        isSolid: isSolid,
        icon: `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
    };

    if (editId) {
        links = links.map(l => l.id === editId ? { ...l, ...linkData } : l);
    } else {
        links.push({
            id: Date.now().toString(),
            ...linkData
        });
    }

    saveLinks();
    modalOverlay.classList.remove('visible');
});

init();
