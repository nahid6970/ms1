
function createContextMenu(items) {
    const contextMenu = document.createElement('div');
    contextMenu.className = 'context-menu';

    items.forEach(item => {
        const menuItem = document.createElement('div');
        menuItem.className = 'context-menu-item';
        menuItem.textContent = item.label;
        if (item.label === 'New-Tab') {
            menuItem.classList.add('context-menu-new-tab');
        } else if (item.label === 'Edit') {
            menuItem.classList.add('context-menu-edit');
        } else if (item.label === 'Copy') {
            menuItem.classList.add('context-menu-copy');
        } else if (item.label === 'Copy Note') {
            menuItem.classList.add('context-menu-copy-note');
        } else if (item.label === 'Delete') {
            menuItem.classList.add('context-menu-delete');
        }
        menuItem.addEventListener('click', () => {
            item.action();
            hideContextMenu();
        });
        contextMenu.appendChild(menuItem);
    });

    return contextMenu;
}

function showContextMenu(event, items) {
    event.preventDefault();
    event.stopPropagation();
    hideContextMenu(); // Hide any existing context menu

    const contextMenu = createContextMenu(items);
    
    // Add to DOM invisibly to measure dimensions
    contextMenu.style.visibility = 'hidden';
    contextMenu.style.position = 'fixed';
    document.body.appendChild(contextMenu);

    // Get menu dimensions
    const menuRect = contextMenu.getBoundingClientRect();
    const menuWidth = menuRect.width;
    const menuHeight = menuRect.height;
    
    // Get viewport dimensions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Calculate initial position
    let left = event.clientX;
    let top = event.clientY;
    
    // Adjust if menu would go off right edge
    if (left + menuWidth > viewportWidth - 5) {
        left = Math.max(5, event.clientX - menuWidth);
    }
    
    // Adjust if menu would go off bottom edge
    if (top + menuHeight > viewportHeight - 5) {
        top = Math.max(5, event.clientY - menuHeight);
    }
    
    // Ensure menu doesn't go off left edge
    if (left < 5) {
        left = 5;
    }
    
    // Ensure menu doesn't go off top edge
    if (top < 5) {
        top = 5;
    }
    
    // Apply final position and make visible
    contextMenu.style.top = `${top}px`;
    contextMenu.style.left = `${left}px`;
    contextMenu.style.visibility = 'visible';

    // Delay adding click listener to prevent immediate closing
    setTimeout(() => {
        document.addEventListener('click', hideContextMenu);
    }, 10);
}

function hideContextMenu() {
    const contextMenu = document.querySelector('.context-menu');
    if (contextMenu) {
        contextMenu.remove();
        document.removeEventListener('click', hideContextMenu);
    }
}
