
function createContextMenu(items) {
    const contextMenu = document.createElement('div');
    contextMenu.className = 'context-menu';

    items.forEach(item => {
        const menuItem = document.createElement('div');
        menuItem.className = 'context-menu-item';
        menuItem.textContent = item.label;
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
    hideContextMenu(); // Hide any existing context menu

    const contextMenu = createContextMenu(items);
    contextMenu.style.top = `${event.clientY}px`;
    contextMenu.style.left = `${event.clientX}px`;

    document.body.appendChild(contextMenu);

    document.addEventListener('click', hideContextMenu);
}

function hideContextMenu() {
    const contextMenu = document.querySelector('.context-menu');
    if (contextMenu) {
        contextMenu.remove();
        document.removeEventListener('click', hideContextMenu);
    }
}
