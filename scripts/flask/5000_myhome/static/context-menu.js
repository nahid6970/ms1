
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

    // Add class to prevent touch actions globally
    document.body.classList.add('context-menu-active');

    // Additional mobile touch event prevention
    if (event.type === 'contextmenu') {
        // Prevent any touch events from bubbling up
        document.addEventListener('touchstart', preventTouchBubbling, { passive: false, capture: true });
        document.addEventListener('touchmove', preventTouchBubbling, { passive: false, capture: true });
        document.addEventListener('touchend', preventTouchBubbling, { passive: false, capture: true });
        document.addEventListener('click', preventTouchBubbling, { passive: false, capture: true });

        // Remove these listeners after a short delay
        setTimeout(() => {
            document.removeEventListener('touchstart', preventTouchBubbling, { capture: true });
            document.removeEventListener('touchmove', preventTouchBubbling, { capture: true });
            document.removeEventListener('touchend', preventTouchBubbling, { capture: true });
            document.removeEventListener('click', preventTouchBubbling, { capture: true });
        }, 300);
    }

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
        // Remove the context menu active class
        document.body.classList.remove('context-menu-active');
    }
}

// Helper function to prevent touch event bubbling during context menu display
function preventTouchBubbling(event) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
}

// Enhanced context menu handler for mobile compatibility
function addMobileContextMenu(element, items) {
    let touchTimer;
    let touchStarted = false;
    let touchMoved = false;

    // Handle touch start
    element.addEventListener('touchstart', function (e) {
        touchStarted = true;
        touchMoved = false;

        // Add visual feedback after a short delay
        const feedbackTimer = setTimeout(() => {
            if (touchStarted && !touchMoved) {
                element.classList.add('long-press-active');
            }
        }, 200);

        // Start long press timer
        touchTimer = setTimeout(() => {
            if (touchStarted && !touchMoved) {
                // Add class to prevent touch actions
                document.body.classList.add('context-menu-active');

                // Remove visual feedback
                element.classList.remove('long-press-active');

                // Prevent any other touch events
                e.preventDefault();
                e.stopPropagation();

                // Create a synthetic contextmenu event
                const syntheticEvent = {
                    preventDefault: () => { },
                    stopPropagation: () => { },
                    clientX: e.touches[0].clientX,
                    clientY: e.touches[0].clientY,
                    type: 'contextmenu'
                };

                // Show context menu
                showContextMenu(syntheticEvent, items);

                // Prevent default touch behavior and remove class after delay
                document.addEventListener('touchend', function preventTouch(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    document.removeEventListener('touchend', preventTouch);

                    // Remove the class after a short delay
                    setTimeout(() => {
                        document.body.classList.remove('context-menu-active');
                    }, 200);
                }, { once: true, passive: false });
            }
        }, 500); // 500ms long press

        // Store timers for cleanup
        element._feedbackTimer = feedbackTimer;
        element._touchTimer = touchTimer;
    }, { passive: false });

    // Handle touch move
    element.addEventListener('touchmove', function () {
        touchMoved = true;
        clearTimeout(touchTimer);
        clearTimeout(element._feedbackTimer);
        element.classList.remove('long-press-active');
    }, { passive: true });

    // Handle touch end
    element.addEventListener('touchend', function () {
        touchStarted = false;
        clearTimeout(touchTimer);
        clearTimeout(element._feedbackTimer);
        element.classList.remove('long-press-active');
    }, { passive: true });

    // Handle touch cancel
    element.addEventListener('touchcancel', function () {
        touchStarted = false;
        clearTimeout(touchTimer);
        clearTimeout(element._feedbackTimer);
        element.classList.remove('long-press-active');
    }, { passive: true });

    // Still keep the regular contextmenu for desktop
    element.addEventListener('contextmenu', function (e) {
        showContextMenu(e, items);
    });
}
