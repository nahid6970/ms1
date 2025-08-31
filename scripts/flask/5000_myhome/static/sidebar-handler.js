// Sidebar buttons management
let sidebarButtons = [];
let sidebarEditMode = false;

// Load sidebar buttons on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSidebarButtons();
    setupSidebarEventListeners();
});

// Load sidebar buttons from API
function loadSidebarButtons() {
    fetch('/api/sidebar-buttons')
        .then(response => response.json())
        .then(buttons => {
            sidebarButtons = buttons;
            renderSidebarButtons();
            setupNotificationUpdates();
        })
        .catch(error => {
            console.error('Error loading sidebar buttons:', error);
        });
}

// Render sidebar buttons in the container
function renderSidebarButtons() {
    const container = document.getElementById('sidebar-buttons-container');
    container.innerHTML = '';

    sidebarButtons.forEach((button, index) => {
        const buttonElement = createSidebarButtonElement(button, index);
        container.appendChild(buttonElement);
    });

    // Add the "+" button for adding new buttons
    const addButton = document.createElement('div');
    addButton.className = 'notification-button-container';
    addButton.innerHTML = `
        <a href="#" id="add-sidebar-button" class="add-button sidebar-add-button" title="Add New Button">
            <i class="nf nf-fa-plus"></i>
        </a>
    `;
    container.appendChild(addButton);

    // Show/hide edit buttons based on edit mode
    updateSidebarEditMode();
}

// Create a sidebar button element
function createSidebarButtonElement(button, index) {
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'notification-button-container';
    
    let buttonHtml = '';
    
    if (button.has_notification) {
        buttonHtml = `
            <a href="#" id="${button.id}" class="add-button" title="${button.name}">
                <i class="${button.icon_class}"></i>
            </a>
            <span id="${button.id}-notification-badge" class="notification-badge" style="display: none;">0</span>
        `;
    } else {
        buttonHtml = `
            <a href="${button.url}" class="add-button" target="_blank" title="${button.name}">
                <i class="${button.icon_class}"></i>
            </a>
        `;
    }
    
    // Add edit and delete buttons (hidden by default)
    buttonHtml += `
        <div class="sidebar-edit-buttons" style="display: none;">
            <button class="edit-sidebar-btn" onclick="editSidebarButton(${index})" title="Edit">✏️</button>
            <button class="delete-sidebar-btn" onclick="deleteSidebarButton(${index})" title="Delete">🗑️</button>
        </div>
    `;
    
    buttonContainer.innerHTML = buttonHtml;
    return buttonContainer;
}

// Setup event listeners for sidebar functionality
function setupSidebarEventListeners() {
    // Add button click handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('#add-sidebar-button')) {
            e.preventDefault();
            showAddSidebarButtonPopup();
        }
    });

    // Add sidebar button form submission
    const addForm = document.getElementById('add-sidebar-button-form');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addSidebarButton();
        });
    }

    // Edit sidebar button form submission
    const editForm = document.getElementById('edit-sidebar-button-form');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveSidebarButtonEdit();
        });
    }

    // Notification checkbox handlers
    const notificationCheckbox = document.getElementById('sidebar-button-notification');
    if (notificationCheckbox) {
        notificationCheckbox.addEventListener('change', function() {
            const settings = document.getElementById('notification-settings');
            settings.style.display = this.checked ? 'block' : 'none';
        });
    }

    const editNotificationCheckbox = document.getElementById('edit-sidebar-button-notification');
    if (editNotificationCheckbox) {
        editNotificationCheckbox.addEventListener('change', function() {
            const settings = document.getElementById('edit-notification-settings');
            settings.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Close popup handlers
    setupSidebarPopupCloseHandlers();
}

// Setup popup close handlers
function setupSidebarPopupCloseHandlers() {
    const addPopup = document.getElementById('add-sidebar-button-popup');
    const editPopup = document.getElementById('edit-sidebar-button-popup');

    // Close buttons
    const addCloseBtn = addPopup?.querySelector('.close-button');
    const editCloseBtn = editPopup?.querySelector('.close-button');

    if (addCloseBtn) {
        addCloseBtn.addEventListener('click', () => {
            addPopup.classList.add('hidden');
        });
    }

    if (editCloseBtn) {
        editCloseBtn.addEventListener('click', () => {
            editPopup.classList.add('hidden');
        });
    }

    // Click outside to close
    window.addEventListener('click', (e) => {
        if (e.target === addPopup) {
            addPopup.classList.add('hidden');
        }
        if (e.target === editPopup) {
            editPopup.classList.add('hidden');
        }
    });
}

// Show add sidebar button popup
function showAddSidebarButtonPopup() {
    const popup = document.getElementById('add-sidebar-button-popup');
    popup.classList.remove('hidden');
    
    // Reset form
    document.getElementById('add-sidebar-button-form').reset();
    document.getElementById('notification-settings').style.display = 'none';
}

// Add new sidebar button
function addSidebarButton() {
    const name = document.getElementById('sidebar-button-name').value;
    const iconClass = document.getElementById('sidebar-button-icon').value;
    const url = document.getElementById('sidebar-button-url').value;
    const hasNotification = document.getElementById('sidebar-button-notification').checked;
    
    const newButton = {
        id: `custom-button-${Date.now()}`,
        name: name,
        icon_class: iconClass,
        url: url,
        has_notification: hasNotification
    };

    if (hasNotification) {
        newButton.notification_api = document.getElementById('sidebar-button-notification-api').value;
        newButton.mark_seen_api = document.getElementById('sidebar-button-mark-seen-api').value;
    }

    fetch('/api/sidebar-buttons', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(newButton)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Button added successfully');
        loadSidebarButtons(); // Reload buttons
        document.getElementById('add-sidebar-button-popup').classList.add('hidden');
    })
    .catch(error => {
        console.error('Error adding button:', error);
        alert('Error adding button');
    });
}

// Edit sidebar button
function editSidebarButton(index) {
    const button = sidebarButtons[index];
    const popup = document.getElementById('edit-sidebar-button-popup');
    
    // Fill form with current values
    document.getElementById('edit-sidebar-button-index').value = index;
    document.getElementById('edit-sidebar-button-name').value = button.name;
    document.getElementById('edit-sidebar-button-icon').value = button.icon_class;
    document.getElementById('edit-sidebar-button-url').value = button.url;
    document.getElementById('edit-sidebar-button-notification').checked = button.has_notification || false;
    
    if (button.has_notification) {
        document.getElementById('edit-notification-settings').style.display = 'block';
        document.getElementById('edit-sidebar-button-notification-api').value = button.notification_api || '';
        document.getElementById('edit-sidebar-button-mark-seen-api').value = button.mark_seen_api || '';
    } else {
        document.getElementById('edit-notification-settings').style.display = 'none';
    }
    
    popup.classList.remove('hidden');
}

// Save sidebar button edit
function saveSidebarButtonEdit() {
    const index = parseInt(document.getElementById('edit-sidebar-button-index').value);
    const name = document.getElementById('edit-sidebar-button-name').value;
    const iconClass = document.getElementById('edit-sidebar-button-icon').value;
    const url = document.getElementById('edit-sidebar-button-url').value;
    const hasNotification = document.getElementById('edit-sidebar-button-notification').checked;
    
    const updatedButton = {
        ...sidebarButtons[index],
        name: name,
        icon_class: iconClass,
        url: url,
        has_notification: hasNotification
    };

    if (hasNotification) {
        updatedButton.notification_api = document.getElementById('edit-sidebar-button-notification-api').value;
        updatedButton.mark_seen_api = document.getElementById('edit-sidebar-button-mark-seen-api').value;
    } else {
        delete updatedButton.notification_api;
        delete updatedButton.mark_seen_api;
    }

    fetch(`/api/sidebar-buttons/${index}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedButton)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Button updated successfully');
        loadSidebarButtons(); // Reload buttons
        document.getElementById('edit-sidebar-button-popup').classList.add('hidden');
    })
    .catch(error => {
        console.error('Error updating button:', error);
        alert('Error updating button');
    });
}

// Delete sidebar button
function deleteSidebarButton(index) {
    const button = sidebarButtons[index];
    if (confirm(`Delete "${button.name}" button?`)) {
        fetch(`/api/sidebar-buttons/${index}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            console.log('Button deleted successfully');
            loadSidebarButtons(); // Reload buttons
        })
        .catch(error => {
            console.error('Error deleting button:', error);
            alert('Error deleting button');
        });
    }
}

// Update sidebar edit mode visibility
function updateSidebarEditMode() {
    const editButtons = document.querySelectorAll('.sidebar-edit-buttons');
    editButtons.forEach(btn => {
        btn.style.display = sidebarEditMode ? 'flex' : 'none';
    });
}

// Toggle sidebar edit mode (called from main edit mode toggle)
function toggleSidebarEditMode(enabled) {
    sidebarEditMode = enabled;
    updateSidebarEditMode();
}

// Setup notification updates for buttons with notifications
function setupNotificationUpdates() {
    sidebarButtons.forEach((button, index) => {
        if (button.has_notification && button.notification_api) {
            setupButtonNotifications(button);
        }
    });
}

// Setup notifications for a specific button
function setupButtonNotifications(button) {
    // Update notifications on page load
    updateButtonNotifications(button);
    
    // Update notifications every 30 seconds
    setInterval(() => {
        updateButtonNotifications(button);
    }, 30000);
    
    // Setup click handler for notification buttons
    const buttonElement = document.getElementById(button.id);
    if (buttonElement) {
        buttonElement.addEventListener('click', function(e) {
            e.preventDefault();
            handleNotificationButtonClick(button);
        });
    }
}

// Update notification badge for a button
function updateButtonNotifications(button) {
    if (!button.notification_api) return;
    
    fetch(button.notification_api)
        .then(response => response.json())
        .then(data => {
            const count = data.unseen_count || 0;
            const badge = document.getElementById(`${button.id}-notification-badge`);
            
            if (badge) {
                if (count > 0) {
                    badge.textContent = count;
                    badge.style.display = 'block';
                    badge.classList.remove('zero');
                } else {
                    badge.style.display = 'none';
                    badge.classList.add('zero');
                }
            }
        })
        .catch(error => {
            console.error(`Error fetching notifications for ${button.name}:`, error);
        });
}

// Handle click on notification button
function handleNotificationButtonClick(button) {
    const badge = document.getElementById(`${button.id}-notification-badge`);
    const count = badge ? parseInt(badge.textContent) || 0 : 0;
    
    if (count === 0) {
        // No notifications, just open the URL
        window.open(button.url, '_blank');
        return;
    }
    
    if (button.mark_seen_api && confirm(`Mark all ${count} items as seen?`)) {
        fetch(button.mark_seen_api, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`Marked items as seen for ${button.name}`);
                    updateButtonNotifications(button); // Refresh the count
                    window.open(button.url, '_blank');
                } else {
                    console.error(`Failed to mark items as seen for ${button.name}:`, data.error);
                    alert('Failed to mark items as seen');
                }
            })
            .catch(error => {
                console.error(`Error marking items as seen for ${button.name}:`, error);
                alert('Error marking items as seen');
            });
    } else {
        // Just open the URL without marking as seen
        window.open(button.url, '_blank');
    }
}