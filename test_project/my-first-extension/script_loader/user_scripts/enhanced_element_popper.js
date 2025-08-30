// Enhanced Element Popper Script
// Improved version with better highlighting and more reliable popping
// Works with dynamic content like YouTube comments, live chats, etc.

(function() {
    'use strict';
    
    console.log('Enhanced Element Popper: Script loaded');
    
    // Configuration
    const config = {
        highlightColor: 'rgba(74, 144, 226, 0.3)',
        borderColor: '#4A90E2',
        borderWidth: '2px',
        excludeSelectors: [
            'html', 'body', 'head', 'script', 'style', 'meta', 'link',
            '.highlight-overlay', '[data-element-popper-overlay]'
        ]
    };
    
    let isCtrlPressed = false;
    let currentHighlightedElement = null;
    let overlay = null;
    let isActive = false;
    
    // Create enhanced overlay with better styling
    function createOverlay() {
        if (overlay) return overlay;
        
        overlay = document.createElement('div');
        overlay.setAttribute('data-element-popper-overlay', 'true');
        overlay.style.cssText = `
            position: absolute;
            background-color: ${config.highlightColor};
            border: ${config.borderWidth} solid ${config.borderColor};
            border-radius: 4px;
            z-index: 2147483647;
            pointer-events: none;
            transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(1px);
        `;
        
        document.body.appendChild(overlay);
        return overlay;
    }
    
    // Check if element should be excluded from selection
    function shouldExcludeElement(element) {
        if (!element || element === document.documentElement) return true;
        
        // Check against exclude selectors
        return config.excludeSelectors.some(selector => {
            try {
                return element.matches && element.matches(selector);
            } catch (e) {
                return false;
            }
        });
    }
    
    // Get the best target element (avoid selecting parent when child is more appropriate)
    function getBestTargetElement(element) {
        if (!element) return null;
        
        // If it's a very small element, try to get a more meaningful parent
        const rect = element.getBoundingClientRect();
        if (rect.width < 20 || rect.height < 20) {
            let parent = element.parentElement;
            while (parent && parent !== document.body) {
                const parentRect = parent.getBoundingClientRect();
                if (parentRect.width >= 100 && parentRect.height >= 50) {
                    return parent;
                }
                parent = parent.parentElement;
            }
        }
        
        return element;
    }
    
    // Update overlay position and size with smooth animation
    function updateOverlay(element) {
        if (!overlay) createOverlay();
        
        if (element && !shouldExcludeElement(element)) {
            const rect = element.getBoundingClientRect();
            const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
            const scrollY = window.pageYOffset || document.documentElement.scrollTop;
            
            overlay.style.display = 'block';
            overlay.style.width = `${rect.width}px`;
            overlay.style.height = `${rect.height}px`;
            overlay.style.left = `${rect.left + scrollX}px`;
            overlay.style.top = `${rect.top + scrollY}px`;
            
            // Add a subtle pulse effect for better visibility
            overlay.style.animation = 'none';
            requestAnimationFrame(() => {
                overlay.style.animation = 'elementPopperPulse 2s infinite';
            });
        } else {
            hideOverlay();
        }
    }
    
    // Hide overlay
    function hideOverlay() {
        if (overlay) {
            overlay.style.display = 'none';
            overlay.style.animation = 'none';
        }
    }
    
    // Inject CSS for animations and improvements
    function injectCSS() {
        if (document.getElementById('element-popper-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'element-popper-styles';
        style.textContent = `
            @keyframes elementPopperPulse {
                0%, 100% { opacity: 0.6; }
                50% { opacity: 0.9; }
            }
            
            /* Ensure popped windows have proper styling */
            .element-popper-window {
                font-family: inherit !important;
                line-height: inherit !important;
            }
            
            /* Improve text selection visibility */
            *::selection {
                background-color: rgba(74, 144, 226, 0.5) !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Enhanced element detection for mouse events
    function getElementFromPoint(x, y) {
        // Temporarily hide overlay to get accurate element
        const originalDisplay = overlay ? overlay.style.display : 'none';
        if (overlay) overlay.style.display = 'none';
        
        const element = document.elementFromPoint(x, y);
        
        // Restore overlay
        if (overlay) overlay.style.display = originalDisplay;
        
        return element;
    }
    
    // Mouse move handler with improved element detection
    function handleMouseMove(event) {
        if (!isCtrlPressed || !isActive) return;
        
        const element = getElementFromPoint(event.clientX, event.clientY);
        const targetElement = getBestTargetElement(element);
        
        if (targetElement !== currentHighlightedElement) {
            currentHighlightedElement = targetElement;
            updateOverlay(targetElement);
        }
    }
    
    // Enhanced pop-out functionality
    function popElement(element) {
        if (!element) return;
        
        const rect = element.getBoundingClientRect();
        const computedStyle = window.getComputedStyle(element);
        
        // Calculate optimal window size
        const minWidth = 400;
        const minHeight = 300;
        const maxWidth = 1200;
        const maxHeight = 800;
        
        const windowWidth = Math.min(maxWidth, Math.max(minWidth, rect.width + 40));
        const windowHeight = Math.min(maxHeight, Math.max(minHeight, rect.height + 40));
        
        // Position new window near cursor but ensure it's visible
        const screenWidth = window.screen.availWidth;
        const screenHeight = window.screen.availHeight;
        const left = Math.min(screenWidth - windowWidth, window.screenX + rect.left);
        const top = Math.min(screenHeight - windowHeight, window.screenY + rect.top);
        
        const windowFeatures = `
            width=${windowWidth},
            height=${windowHeight},
            left=${left},
            top=${top},
            scrollbars=yes,
            resizable=yes,
            menubar=no,
            toolbar=no,
            location=no,
            status=no
        `.replace(/\s+/g, '');
        
        try {
            const newWindow = window.open('', `element_popper_${Date.now()}`, windowFeatures);
            
            if (!newWindow) {
                console.error('Enhanced Element Popper: Popup blocked');
                return;
            }
            
            // Clone the element deeply
            const clonedElement = element.cloneNode(true);
            
            // Collect all relevant styles
            const allStyles = collectStyles();
            
            // Build the popup document
            const htmlContent = `
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Popped Element - ${document.title}</title>
                    <style>
                        ${allStyles}
                        
                        body {
                            margin: 20px;
                            font-family: ${computedStyle.fontFamily};
                            background-color: ${computedStyle.backgroundColor || '#ffffff'};
                            color: ${computedStyle.color || '#000000'};
                        }
                        
                        .popped-element {
                            max-width: 100%;
                            max-height: 100%;
                            overflow: auto;
                        }
                        
                        /* Fix for YouTube comments and dynamic content */
                        .popped-element * {
                            max-width: 100% !important;
                        }
                        
                        /* Ensure videos and iframes work */
                        video, iframe {
                            max-width: 100% !important;
                            height: auto !important;
                        }
                        
                        /* Fix text wrapping */
                        .popped-element {
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                        }
                    </style>
                </head>
                <body class="element-popper-window">
                    <div class="popped-element"></div>
                </body>
                </html>
            `;
            
            newWindow.document.write(htmlContent);
            newWindow.document.close();
            
            // Insert the cloned element
            const container = newWindow.document.querySelector('.popped-element');
            container.appendChild(clonedElement);
            
            // Fix any broken functionality in the popped element
            fixPoppedElement(clonedElement, newWindow);
            
            console.log('Enhanced Element Popper: Element successfully popped out');
            
        } catch (error) {
            console.error('Enhanced Element Popper: Error creating popup:', error);
        }
    }
    
    // Collect styles from the current page
    function collectStyles() {
        let styles = '';
        
        // Get inline styles
        const styleElements = document.querySelectorAll('style');
        styleElements.forEach(styleEl => {
            styles += styleEl.textContent + '\n';
        });
        
        // Get external stylesheets (if accessible)
        Array.from(document.styleSheets).forEach(sheet => {
            try {
                if (sheet.cssRules) {
                    Array.from(sheet.cssRules).forEach(rule => {
                        styles += rule.cssText + '\n';
                    });
                }
            } catch (e) {
                // External stylesheet, create link tag
                if (sheet.href) {
                    styles += `@import url("${sheet.href}");\n`;
                }
            }
        });
        
        return styles;
    }
    
    // Fix functionality in popped elements
    function fixPoppedElement(element, popupWindow) {
        // Re-enable any disabled scripts or functionality
        const scripts = element.querySelectorAll('script');
        scripts.forEach(script => {
            if (script.src) {
                const newScript = popupWindow.document.createElement('script');
                newScript.src = script.src;
                popupWindow.document.head.appendChild(newScript);
            } else if (script.textContent) {
                const newScript = popupWindow.document.createElement('script');
                newScript.textContent = script.textContent;
                popupWindow.document.head.appendChild(newScript);
            }
        });
        
        // Fix relative URLs
        const links = element.querySelectorAll('a[href]');
        links.forEach(link => {
            if (link.href && !link.href.startsWith('http')) {
                link.href = new URL(link.href, window.location.href).href;
            }
        });
        
        // Fix image sources
        const images = element.querySelectorAll('img[src]');
        images.forEach(img => {
            if (img.src && !img.src.startsWith('http')) {
                img.src = new URL(img.src, window.location.href).href;
            }
        });
    }
    
    // Keyboard event handlers
    function handleKeyDown(event) {
        if (event.key === 'Control' || event.ctrlKey) {
            if (!isCtrlPressed) {
                isCtrlPressed = true;
                isActive = true;
                createOverlay();
                document.addEventListener('mousemove', handleMouseMove, { passive: true });
                console.log('Enhanced Element Popper: Ctrl mode activated');
            }
        }
        
        // ESC to cancel
        if (event.key === 'Escape') {
            deactivate();
        }
    }
    
    function handleKeyUp(event) {
        if (event.key === 'Control' || !event.ctrlKey) {
            deactivate();
        }
    }
    
    // Click handler for popping elements
    function handleClick(event) {
        if (!isCtrlPressed || !currentHighlightedElement) return;
        
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        
        popElement(currentHighlightedElement);
        deactivate();
    }
    
    // Deactivate the popper
    function deactivate() {
        isCtrlPressed = false;
        isActive = false;
        currentHighlightedElement = null;
        hideOverlay();
        document.removeEventListener('mousemove', handleMouseMove);
        console.log('Enhanced Element Popper: Deactivated');
    }
    
    // Handle page visibility changes
    function handleVisibilityChange() {
        if (document.hidden) {
            deactivate();
        }
    }
    
    // Initialize the script
    function init() {
        injectCSS();
        
        // Event listeners
        document.addEventListener('keydown', handleKeyDown, { passive: true });
        document.addEventListener('keyup', handleKeyUp, { passive: true });
        document.addEventListener('mousedown', handleClick, true);
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // Handle focus loss
        window.addEventListener('blur', deactivate);
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', deactivate);
        
        console.log('Enhanced Element Popper: Initialized');
    }
    
    // Handle dynamic content changes (like YouTube comments loading)
    function observeChanges() {
        const observer = new MutationObserver((mutations) => {
            // If ctrl is pressed and we're highlighting, update the overlay
            if (isCtrlPressed && currentHighlightedElement) {
                // Check if the highlighted element still exists
                if (!document.contains(currentHighlightedElement)) {
                    currentHighlightedElement = null;
                    hideOverlay();
                }
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class']
        });
    }
    
    // Start the script
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            init();
            observeChanges();
        });
    } else {
        init();
        observeChanges();
    }
    
    // Expose cleanup function for debugging
    window.elementPopperCleanup = deactivate;
    
})();