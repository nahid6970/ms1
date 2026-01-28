// YouTube Comments-Sidebar Swapper
// Swaps the comments section with the recommended videos sidebar
// Comments go to the right sidebar, Video list goes below the video

(function () {
    'use strict';

    console.log('YouTube Section Swapper: Script loaded');

    let isSwapped = false;
    let swapApplied = false;

    // Swap comments with sidebar video list
    function swapSections() {
        const secondary = document.querySelector('#secondary, #secondary-inner');
        const comments = document.querySelector('ytd-comments#comments, #comments');
        const below = document.querySelector('#below');
        const columns = document.querySelector('#columns');

        if (!secondary || !comments || !below || !columns) {
            console.log('YouTube Section Swapper: Elements not found yet, waiting...');
            return false;
        }

        if (swapApplied) {
            console.log('YouTube Section Swapper: Already swapped');
            return true;
        }

        // Store original parents for restoration
        comments.dataset.originalParent = 'below';

        // Get the related videos container from secondary
        const relatedVideos = secondary.querySelector('#related, ytd-watch-next-secondary-results-renderer');
        if (relatedVideos) {
            relatedVideos.dataset.originalParent = 'secondary';
        }

        // Move comments to the secondary (right sidebar)
        secondary.innerHTML = '';
        secondary.appendChild(comments);

        // Move related videos to below section (where comments were)
        if (relatedVideos) {
            below.appendChild(relatedVideos);
        }

        // Add indicator and styling
        injectSwapCSS();

        swapApplied = true;
        isSwapped = true;
        console.log('YouTube Section Swapper: ✅ Sections swapped! Comments now in sidebar, videos below.');
        return true;
    }

    // Restore original layout
    function restoreSections() {
        const secondary = document.querySelector('#secondary, #secondary-inner');
        const comments = document.querySelector('ytd-comments#comments, #comments');
        const below = document.querySelector('#below');
        const relatedVideos = document.querySelector('#related, ytd-watch-next-secondary-results-renderer');

        if (!secondary || !below) {
            console.log('YouTube Section Swapper: Cannot restore - elements not found');
            return;
        }

        // Move comments back to #below
        if (comments) {
            below.appendChild(comments);
        }

        // Move related videos back to secondary
        if (relatedVideos) {
            secondary.innerHTML = '';
            secondary.appendChild(relatedVideos);
        }

        // Remove styling
        removeSwapCSS();

        swapApplied = false;
        isSwapped = false;
        console.log('YouTube Section Swapper: ✅ Sections restored to original layout.');
    }

    // CSS styling for swapped layout
    function injectSwapCSS() {
        if (document.getElementById('youtube-section-swap-css')) return;

        const style = document.createElement('style');
        style.id = 'youtube-section-swap-css';
        style.textContent = `
            /* Comments in sidebar styling */
            #secondary > ytd-comments#comments,
            #secondary > #comments,
            #secondary-inner > ytd-comments#comments {
                width: 100% !important;
                max-height: calc(100vh - 120px) !important;
                overflow-y: auto !important;
                padding: 12px !important;
                background: var(--yt-spec-brand-background-secondary, #0f0f0f) !important;
                border-radius: 12px !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            
            /* Related videos in main section styling */
            #below > #related,
            #below > ytd-watch-next-secondary-results-renderer {
                display: grid !important;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)) !important;
                gap: 16px !important;
                padding: 16px 0 !important;
            }
            
            #below > #related ytd-compact-video-renderer,
            #below > ytd-watch-next-secondary-results-renderer ytd-compact-video-renderer {
                flex-direction: row !important;
                width: 100% !important;
            }
            
            /* Scrollbar styling for comments in sidebar */
            #secondary > ytd-comments::-webkit-scrollbar,
            #secondary > #comments::-webkit-scrollbar {
                width: 6px;
            }
            
            #secondary > ytd-comments::-webkit-scrollbar-track,
            #secondary > #comments::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 3px;
            }
            
            #secondary > ytd-comments::-webkit-scrollbar-thumb,
            #secondary > #comments::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, #ff0050 0%, #7b2ff7 100%);
                border-radius: 3px;
            }
            
            /* Visual indicator banner */
            #youtube-swap-indicator {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 10px 12px;
                margin-bottom: 12px;
                background: linear-gradient(135deg, #ff0050 0%, #7b2ff7 50%, #00d4ff 100%);
                color: white;
                font-weight: 600;
                font-size: 11px;
                border-radius: 8px;
                text-align: center;
                letter-spacing: 0.3px;
                box-shadow: 0 4px 15px rgba(123, 47, 247, 0.3);
                animation: pulse-glow 2s ease-in-out infinite;
            }
            
            @keyframes pulse-glow {
                0%, 100% { box-shadow: 0 4px 15px rgba(123, 47, 247, 0.3); }
                50% { box-shadow: 0 4px 25px rgba(255, 0, 80, 0.4); }
            }
            
            #youtube-swap-indicator .swap-icon {
                font-size: 14px;
            }
            
            #youtube-swap-indicator .swap-hotkey {
                background: rgba(0, 0, 0, 0.3);
                padding: 2px 6px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 10px;
            }
        `;
        document.head.appendChild(style);

        // Add indicator banner
        addIndicator();
    }

    // Add visual indicator
    function addIndicator() {
        if (document.getElementById('youtube-swap-indicator')) return;

        const comments = document.querySelector('#secondary > ytd-comments#comments, #secondary > #comments');
        if (!comments) return;

        const indicator = document.createElement('div');
        indicator.id = 'youtube-swap-indicator';
        indicator.innerHTML = `
            <span class="swap-icon">🔄</span>
            <span>Comments ↔ Videos Swapped</span>
            <span class="swap-hotkey">Alt+Q</span>
        `;
        comments.insertBefore(indicator, comments.firstChild);
    }

    // Remove swap CSS
    function removeSwapCSS() {
        const style = document.getElementById('youtube-section-swap-css');
        if (style) style.remove();

        const indicator = document.getElementById('youtube-swap-indicator');
        if (indicator) indicator.remove();
    }

    // Toggle function
    function toggleSwap() {
        if (isSwapped) {
            restoreSections();
        } else {
            swapSections();
        }
    }

    // Add keyboard shortcut (Alt + Q)
    function setupKeyboardShortcut() {
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key.toLowerCase() === 'q') {
                e.preventDefault();
                toggleSwap();
            }
        });
        console.log('YouTube Section Swapper: 🎹 Press Alt+Q to toggle swap');
    }

    // Wait for elements to load and then swap
    function waitForElementsAndSwap() {
        const maxAttempts = 30;
        let attempts = 0;

        const checkInterval = setInterval(() => {
            attempts++;

            const comments = document.querySelector('ytd-comments#comments, #comments');
            const secondary = document.querySelector('#secondary');
            const commentsLoaded = comments && comments.querySelector('#header, #title');

            if (comments && secondary && commentsLoaded) {
                clearInterval(checkInterval);
                console.log('YouTube Section Swapper: Elements loaded, swapping...');
                setTimeout(() => swapSections(), 500);
            } else if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                console.log('YouTube Section Swapper: Timeout waiting for elements');
            }
        }, 500);
    }

    // Handle page navigation
    function handleNavigation() {
        // Reset state
        swapApplied = false;
        isSwapped = false;
        removeSwapCSS();

        if (window.location.pathname.includes('/watch')) {
            console.log('YouTube Section Swapper: Watch page detected, waiting for elements...');
            waitForElementsAndSwap();
        }
    }

    // Initialize
    function init() {
        if (!window.location.hostname.includes('youtube.com')) return;

        setupKeyboardShortcut();

        // Initial swap if on watch page
        if (window.location.pathname.includes('/watch')) {
            waitForElementsAndSwap();
        }

        // Handle YouTube SPA navigation
        window.addEventListener('yt-navigate-finish', handleNavigation);

        // Backup: URL change detection
        let lastUrl = location.href;
        const observer = new MutationObserver(() => {
            if (location.href !== lastUrl) {
                lastUrl = location.href;
                handleNavigation();
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });

        console.log('YouTube Section Swapper: 🚀 Initialized!');
    }

    // Start
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
