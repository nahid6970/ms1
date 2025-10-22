// Sidebar buttons management

let sidebarButtons = [];
let sidebarEditMode = false;

// Load sidebar buttons on page load
document.addEventListener('DOMContentLoaded', function() {
    setupSidebarToggle(); // Setup toggle first
    loadSidebarButtons(); // Then load buttons
    setupSidebarEventListeners(); // Finally setup other listeners
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

// Setup sidebar - always expanded, no toggle functionality
function setupSidebarToggle() {
    const sidebarContainer = document.getElementById('sidebar-container');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    
    // Always keep sidebar expanded
    sidebarContainer.classList.add('expanded');
    
    // Hide the toggle button since we don't need it
    if (sidebarToggle) {
        sidebarToggle.style.display = 'none';
    }
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
    
    // Create the button element
    const buttonElement = document.createElement('a');
    buttonElement.className = 'add-button custom-sidebar-button';
    buttonElement.title = button.name;
    buttonElement.id = button.id;
    
    // Apply custom styling using both CSS custom properties and direct styles
    const textColor = button.text_color || '#000000';
    const bgColor = button.bg_color || '#ffffff';
    const hoverColor = button.hover_color || '#e0e0e0';
    const borderColor = button.border_color || '#cccccc';
    const borderRadius = button.border_radius || '4px';
    const fontSize = button.font_size || '16px';
    
    console.log(`Applying styles to ${button.name}: text=${textColor}, bg=${bgColor}, hover=${hoverColor}, border=${borderColor}, radius=${borderRadius}, fontSize=${fontSize}`);
    
    // Set CSS custom properties
    buttonElement.style.setProperty('--custom-text-color', textColor);
    buttonElement.style.setProperty('--custom-bg-color', bgColor);
    buttonElement.style.setProperty('--custom-hover-color', hoverColor);
    buttonElement.style.setProperty('--custom-border-color', borderColor);
    buttonElement.style.setProperty('--custom-border-radius', borderRadius);
    buttonElement.style.setProperty('--custom-font-size', fontSize);
    
    // Also set direct styles as fallback
    buttonElement.style.setProperty('color', textColor, 'important');
    buttonElement.style.setProperty('background-color', bgColor, 'important');
    buttonElement.style.setProperty('border', `2px solid ${borderColor}`, 'important');
    buttonElement.style.setProperty('border-radius', borderRadius, 'important');
    buttonElement.style.setProperty('font-size', fontSize, 'important');
    
    // Add hover event listeners for guaranteed hover effect
    buttonElement.addEventListener('mouseenter', function() {
        this.style.setProperty('background-color', hoverColor, 'important');
    });
    
    buttonElement.addEventListener('mouseleave', function() {
        this.style.setProperty('background-color', bgColor, 'important');
    });
    
    // Set content based on display type
    if (button.display_type === 'image' && button.img_src) {
        const img = document.createElement('img');
        img.src = button.img_src;
        img.style.width = '25px';
        img.style.height = '25px';
        img.alt = button.name;
        buttonElement.appendChild(img);
    } else {
        const icon = document.createElement('i');
        icon.className = button.icon_class || 'nf nf-fa-question';
        buttonElement.appendChild(icon);
    }
    
    // Set up click behavior
    if (button.has_notification) {
        buttonElement.href = '#';
    } else {
        buttonElement.href = button.url;
        buttonElement.target = '_blank';
    }
    
    buttonContainer.appendChild(buttonElement);
    
    // Add notification badge if needed
    if (button.has_notification) {
        const badge = document.createElement('span');
        badge.id = `${button.id}-notification-badge`;
        badge.className = 'notification-badge';
        badge.style.display = 'none';
        badge.textContent = '0';
        buttonContainer.appendChild(badge);
    }
    
    // Add edit and delete buttons (hidden by default)
    const editButtons = document.createElement('div');
    editButtons.className = 'sidebar-edit-buttons';
    editButtons.style.display = 'none';
    editButtons.innerHTML = `
        <button class="edit-sidebar-btn" onclick="editSidebarButton(${index})" title="Edit">✏️</button>
        <button class="delete-sidebar-btn" onclick="deleteSidebarButton(${index})" title="Delete">🗑️</button>
    `;
    buttonContainer.appendChild(editButtons);
    
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

    // Display type handlers
    const displayTypeSelect = document.getElementById('sidebar-button-display-type');
    if (displayTypeSelect) {
        displayTypeSelect.addEventListener('change', function() {
            const iconSettings = document.getElementById('icon-settings');
            const imageSettings = document.getElementById('image-settings');
            if (this.value === 'image') {
                iconSettings.style.display = 'none';
                imageSettings.style.display = 'block';
            } else {
                iconSettings.style.display = 'block';
                imageSettings.style.display = 'none';
            }
        });
    }

    const editDisplayTypeSelect = document.getElementById('edit-sidebar-button-display-type');
    if (editDisplayTypeSelect) {
        editDisplayTypeSelect.addEventListener('change', function() {
            const iconSettings = document.getElementById('edit-icon-settings');
            const imageSettings = document.getElementById('edit-image-settings');
            if (this.value === 'image') {
                iconSettings.style.display = 'none';
                imageSettings.style.display = 'block';
            } else {
                iconSettings.style.display = 'block';
                imageSettings.style.display = 'none';
            }
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
    
    // Reset display type settings
    document.getElementById('icon-settings').style.display = 'block';
    document.getElementById('image-settings').style.display = 'none';
    document.getElementById('sidebar-button-display-type').value = 'icon';
}

// Add new sidebar button
function addSidebarButton() {
    const name = document.getElementById('sidebar-button-name').value;
    const url = document.getElementById('sidebar-button-url').value;
    const displayType = document.getElementById('sidebar-button-display-type').value;
    const iconClass = document.getElementById('sidebar-button-icon').value;
    const imgSrc = document.getElementById('sidebar-button-img-src').value;
    const textColor = document.getElementById('sidebar-button-text-color').value;
    const bgColor = document.getElementById('sidebar-button-bg-color').value;
    const hoverColor = document.getElementById('sidebar-button-hover-color').value;
    const borderColor = document.getElementById('sidebar-button-border-color').value;
    const borderRadius = document.getElementById('sidebar-button-border-radius').value;
    const fontSize = document.getElementById('sidebar-button-font-size').value;
    const hasNotification = document.getElementById('sidebar-button-notification').checked;
    
    const newButton = {
        id: `custom-button-${Date.now()}`,
        name: name,
        display_type: displayType,
        icon_class: iconClass,
        img_src: imgSrc,
        url: url,
        has_notification: hasNotification,
        text_color: textColor || '#000000',
        bg_color: bgColor || '#ffffff',
        hover_color: hoverColor || '#e0e0e0',
        border_color: borderColor || '#cccccc',
        border_radius: borderRadius || '4px',
        font_size: fontSize || '16px'
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
    document.getElementById('edit-sidebar-button-url').value = button.url;
    document.getElementById('edit-sidebar-button-display-type').value = button.display_type || 'icon';
    document.getElementById('edit-sidebar-button-icon').value = button.icon_class || '';
    document.getElementById('edit-sidebar-button-img-src').value = button.img_src || '';
    document.getElementById('edit-sidebar-button-text-color').value = button.text_color || '';
    document.getElementById('edit-sidebar-button-bg-color').value = button.bg_color || '';
    document.getElementById('edit-sidebar-button-hover-color').value = button.hover_color || '';
    document.getElementById('edit-sidebar-button-border-color').value = button.border_color || '';
    document.getElementById('edit-sidebar-button-border-radius').value = button.border_radius || '';
    document.getElementById('edit-sidebar-button-font-size').value = button.font_size || '';
    document.getElementById('edit-sidebar-button-notification').checked = button.has_notification || false;
    
    // Show/hide settings based on display type
    const displayType = button.display_type || 'icon';
    const iconSettings = document.getElementById('edit-icon-settings');
    const imageSettings = document.getElementById('edit-image-settings');
    if (displayType === 'image') {
        iconSettings.style.display = 'none';
        imageSettings.style.display = 'block';
    } else {
        iconSettings.style.display = 'block';
        imageSettings.style.display = 'none';
    }
    
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
    const url = document.getElementById('edit-sidebar-button-url').value;
    const displayType = document.getElementById('edit-sidebar-button-display-type').value;
    const iconClass = document.getElementById('edit-sidebar-button-icon').value;
    const imgSrc = document.getElementById('edit-sidebar-button-img-src').value;
    const textColor = document.getElementById('edit-sidebar-button-text-color').value;
    const bgColor = document.getElementById('edit-sidebar-button-bg-color').value;
    const hoverColor = document.getElementById('edit-sidebar-button-hover-color').value;
    const borderColor = document.getElementById('edit-sidebar-button-border-color').value;
    const borderRadius = document.getElementById('edit-sidebar-button-border-radius').value;
    const fontSize = document.getElementById('edit-sidebar-button-font-size').value;
    const hasNotification = document.getElementById('edit-sidebar-button-notification').checked;
    
    const updatedButton = {
        ...sidebarButtons[index],
        name: name,
        display_type: displayType,
        icon_class: iconClass,
        img_src: imgSrc,
        url: url,
        has_notification: hasNotification,
        text_color: textColor || '#000000',
        bg_color: bgColor || '#ffffff',
        hover_color: hoverColor || '#e0e0e0',
        border_color: borderColor || '#cccccc',
        border_radius: borderRadius || '4px',
        font_size: fontSize || '16px'
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