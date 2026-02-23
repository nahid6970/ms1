let groups = [];
let extensions = [];

document.addEventListener('DOMContentLoaded', () => {
    chrome.management.getAll((exts) => {
        extensions = exts.filter(e => e.type === 'extension' && e.id !== chrome.runtime.id);
        loadGroups();
    });
});

function loadGroups() {
    chrome.storage.local.get(['groups'], (result) => {
        groups = result.groups || [];
        if (groups.length === 0) {
            groups = [{ id: Date.now(), name: 'All Extensions', extIds: [] }];
            saveGroups();
        }
        renderGroups();
    });
}

function saveGroups() {
    chrome.storage.local.set({ groups });
}

function renderGroups() {
    const container = document.getElementById('groups');
    if (groups.length === 0) {
        container.innerHTML = '<div class="empty-state">No groups. Click + GROUP to create one.</div>';
        return;
    }
    
    container.innerHTML = groups.map(group => {
        const groupExts = group.extIds.length > 0 
            ? extensions.filter(e => group.extIds.includes(e.id))
            : extensions.filter(e => !groups.some(g => g.extIds.length > 0 && g.extIds.includes(e.id)));
        
        return `
            <div class="group" data-group-id="${group.id}">
                <div class="group-header">
                    <span class="group-title">${group.name}</span>
                    <div class="group-actions">
                        <button class="group-btn" onclick="deleteGroup(${group.id})">×</button>
                    </div>
                </div>
                <div class="extensions">
                    ${groupExts.length === 0 ? '<div class="empty-state">Drag extensions here</div>' : groupExts.map(ext => `
                        <div class="extension" draggable="true" data-ext-id="${ext.id}">
                            <div class="ext-status ${ext.enabled ? 'enabled' : ''}"></div>
                            <img class="ext-icon" src="${ext.icons?.[0]?.url || 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2232%22 height=%2232%22><rect width=%2232%22 height=%2232%22 fill=%22%23333%22/></svg>'}" alt="">
                            <div class="ext-name">${ext.name}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
    
    attachDragListeners();
}

function attachDragListeners() {
    document.querySelectorAll('.extension').forEach(ext => {
        ext.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('extId', ext.dataset.extId);
            ext.classList.add('dragging');
        });
        ext.addEventListener('dragend', () => {
            ext.classList.remove('dragging');
        });
        ext.addEventListener('click', () => {
            const id = ext.dataset.extId;
            const extension = extensions.find(e => e.id === id);
            chrome.management.setEnabled(id, !extension.enabled, () => {
                extension.enabled = !extension.enabled;
                renderGroups();
            });
        });
    });
    
    document.querySelectorAll('.group').forEach(group => {
        group.addEventListener('dragover', (e) => {
            e.preventDefault();
            group.classList.add('drag-over');
        });
        group.addEventListener('dragleave', () => {
            group.classList.remove('drag-over');
        });
        group.addEventListener('drop', (e) => {
            e.preventDefault();
            group.classList.remove('drag-over');
            const extId = e.dataTransfer.getData('extId');
            const groupId = parseInt(group.dataset.groupId);
            moveExtension(extId, groupId);
        });
    });
}

function moveExtension(extId, toGroupId) {
    groups.forEach(g => {
        g.extIds = g.extIds.filter(id => id !== extId);
    });
    
    const targetGroup = groups.find(g => g.id === toGroupId);
    if (targetGroup && targetGroup.extIds.length === 0 && targetGroup.name === 'All Extensions') {
        // Don't add to All Extensions
    } else if (targetGroup) {
        targetGroup.extIds.push(extId);
    }
    
    saveGroups();
    renderGroups();
}

function deleteGroup(id) {
    groups = groups.filter(g => g.id !== id);
    saveGroups();
    renderGroups();
}

document.getElementById('addGroup').addEventListener('click', () => {
    document.getElementById('modal').classList.add('show');
    document.getElementById('groupName').value = '';
    document.getElementById('groupName').focus();
});

document.getElementById('cancelBtn').addEventListener('click', () => {
    document.getElementById('modal').classList.remove('show');
});

document.getElementById('saveBtn').addEventListener('click', () => {
    const name = document.getElementById('groupName').value.trim();
    if (name) {
        groups.push({ id: Date.now(), name, extIds: [] });
        saveGroups();
        renderGroups();
        document.getElementById('modal').classList.remove('show');
    }
});

document.getElementById('groupName').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') document.getElementById('saveBtn').click();
});
