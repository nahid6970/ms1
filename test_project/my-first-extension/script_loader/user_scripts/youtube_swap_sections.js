// YouTube Comments-Sidebar Swapper
// Swaps the comments section with the recommended videos sidebar
// Comments go to the right sidebar, Video list goes below the video

(function () {
    'use strict';

    // Prevent multiple injections
    if (window._ytSwapSectionsLoaded) {
        console.log('YouTube Section Swapper: Script already loaded, skipping injection');
        // If navigation happened, we might still need to re-initiate the wait
        if (typeof window._ytSwapInit === 'function') {
            window._ytSwapInit();
        }
        return;
    }
    window._ytSwapSectionsLoaded = true;

    console.log('YouTube Section Swapper: Script loaded and initializing...');

    let isSwapped = false;
    let observer = null;

    // Swap comments with sidebar video list
    function swapSections() {
        const secondary = document.querySelector('#secondary-inner') || document.querySelector('#secondary');
        const comments = document.querySelector('ytd-comments#comments');
        const below = document.querySelector('#below');

        if (!secondary || !comments || !below) {
            return false;
        }

        // Check if already swapped by looking at DOM structure
        if (secondary.contains(comments) && document.getElementById('swapped-video-list')) {
            isSwapped = true;
            addIndicator(); // Ensure indicator is present
            return true;
        }

        // Clone the related videos before clearing
        const relatedContainer = secondary.querySelector('ytd-watch-next-secondary-results-renderer');

        if (!relatedContainer) {
            return false;
        }

        // Create wrapper for related videos in main section
        let videoListWrapper = document.getElementById('swapped-video-list');
        if (!videoListWrapper) {
            videoListWrapper = document.createElement('div');
            videoListWrapper.id = 'swapped-video-list';
        }

        // Move related videos to wrapper
        videoListWrapper.appendChild(relatedContainer);

        // Add wrapper to below section
        below.appendChild(videoListWrapper);

        // Move comments to secondary sidebar
        secondary.appendChild(comments);

        // Add indicator and styling
        injectSwapCSS();

        isSwapped = true;
        console.log('YouTube Section Swapper: ✅ Sections swapped!');
        return true;
    }

    // Restore original layout
    function restoreSections() {
        const secondary = document.querySelector('#secondary-inner') || document.querySelector('#secondary');
        const comments = document.querySelector('ytd-comments#comments');
        const below = document.querySelector('#below');
        const relatedContainer = document.querySelector('ytd-watch-next-secondary-results-renderer');
        const videoListWrapper = document.getElementById('swapped-video-list');

        if (!secondary || !below) return;

        // Move comments back to #below
        if (comments) {
            below.appendChild(comments);
        }

        // Move related videos back to secondary
        if (relatedContainer) {
            secondary.appendChild(relatedContainer);
        }

        // Remove wrapper
        if (videoListWrapper) {
            videoListWrapper.remove();
        }

        // Remove styling
        removeSwapCSS();

        isSwapped = false;
        console.log('YouTube Section Swapper: ✅ Sections restored!');
    }

    // CSS styling for swapped layout
    function injectSwapCSS() {
        if (!document.getElementById('youtube-section-swap-css')) {
            const style = document.createElement('style');
            style.id = 'youtube-section-swap-css';
            style.textContent = `
                /* ===== COMMENTS IN SIDEBAR ===== */
                #secondary > ytd-comments#comments,
                #secondary-inner > ytd-comments#comments {
                    width: 100% !important;
                    max-height: calc(100vh - 120px) !important;
                    overflow-y: auto !important;
                    overflow-x: hidden !important;
                    padding: 12px !important;
                    margin-top: 0 !important;
                    background: var(--yt-spec-brand-background-secondary, #0f0f0f) !important;
                    border-radius: 12px !important;
                    border: 1px solid rgba(255, 255, 255, 0.08) !important;
                    box-sizing: border-box !important;
                    display: block !important;
                }

                /* Ensure internal renderer doesn't have its own scroll conflicting */
                #secondary ytd-comments#comments #sections {
                    overflow: visible !important;
                    height: auto !important;
                }
                
                /* Scrollbar for sidebar comments */
                #secondary > ytd-comments::-webkit-scrollbar,
                #secondary-inner > ytd-comments::-webkit-scrollbar {
                    width: 8px;
                }
                
                #secondary > ytd-comments::-webkit-scrollbar-track,
                #secondary-inner > ytd-comments::-webkit-scrollbar-track {
                    background: transparent;
                }
                
                #secondary > ytd-comments::-webkit-scrollbar-thumb,
                #secondary-inner > ytd-comments::-webkit-scrollbar-thumb {
                    background: linear-gradient(180deg, #ff0050 0%, #7b2ff7 100%);
                    border-radius: 4px;
                }
                
                /* ===== VIDEO LIST GRID BELOW VIDEO ===== */
                #swapped-video-list {
                    margin-top: 24px;
                    padding: 20px;
                    background: var(--yt-spec-brand-background-secondary, #0f0f0f);
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    width: 100% !important;
                }
                
                #swapped-video-list ytd-watch-next-secondary-results-renderer {
                    display: block !important;
                    width: 100% !important;
                }
                
                #swapped-video-list #chips {
                    display: none !important;
                }
                
                #swapped-video-list #contents {
                    display: grid !important;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)) !important;
                    gap: 20px !important;
                    width: 100% !important;
                }
                
                /* ===== INDICATOR BANNER ===== */
                #youtube-swap-indicator {
                    display: flex !important;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    padding: 10px 12px;
                    margin-bottom: 16px;
                    background: linear-gradient(135deg, #ff0050 0%, #7b2ff7 50%, #00d4ff 100%);
                    color: white !important;
                    font-weight: 600;
                    font-size: 12px;
                    border-radius: 8px;
                    text-align: center;
                    letter-spacing: 0.3px;
                    box-shadow: 0 4px 15px rgba(123, 47, 247, 0.3);
                    z-index: 10;
                }
                
                #youtube-swap-indicator .swap-hotkey {
                    background: rgba(0, 0, 0, 0.3);
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: monospace;
                    font-size: 10px;
                }
                
                /* Grid header styling */
                #swapped-video-list::before {
                    content: "📺 Recommended Videos";
                    display: block;
                    padding: 8px 0 16px 0;
                    font-weight: 600;
                    font-size: 16px;
                    color: var(--yt-spec-text-primary, #fff);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    margin-bottom: 16px;
                }
            `;
            document.head.appendChild(style);
        }
        addIndicator();
    }

    // Add visual indicator
    function addIndicator() {
        if (document.getElementById('youtube-swap-indicator')) return;

        const comments = document.querySelector('#secondary ytd-comments#comments, #secondary-inner ytd-comments#comments');
        if (!comments) return;

        const indicator = document.createElement('div');
        indicator.id = 'youtube-swap-indicator';
        indicator.innerHTML = `
            <span>🔄 Comments ↔ Videos Swapped</span>
            <span class="swap-hotkey">Alt+Q to toggle</span>
        `;
        
        // Insert at the top of comments section
        const header = comments.querySelector('#sections');
        if (header) {
            comments.insertBefore(indicator, header);
        } else {
            comments.insertBefore(indicator, comments.firstChild);
        }
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
        // Remove existing listener if any (though IIFE prevents some of this)
        document.removeEventListener('keydown', window._ytSwapKeyHandler);
        
        window._ytSwapKeyHandler = (e) => {
            if (e.altKey && e.key.toLowerCase() === 'q') {
                if (window.location.pathname.includes('/watch')) {
                    e.preventDefault();
                    toggleSwap();
                }
            }
        };
        
        document.addEventListener('keydown', window._ytSwapKeyHandler);
        console.log('YouTube Section Swapper: 🎹 Alt+Q toggle active');
    }

    // Polling function for robustness
    function waitForElementsAndSwap() {
        let attempts = 0;
        const maxAttempts = 60; // 12 seconds with 200ms interval

        if (window._ytSwapInterval) clearInterval(window._ytSwapInterval);

        window._ytSwapInterval = setInterval(() => {
            attempts++;
            
            // Check if we are even on a watch page
            if (!window.location.pathname.includes('/watch')) {
                clearInterval(window._ytSwapInterval);
                return;
            }

            const success = swapSections();
            
            if (success) {
                // Keep polling for a bit even after success to ensure stability
                if (attempts > 15) {
                    clearInterval(window._ytSwapInterval);
                }
            } else if (attempts >= maxAttempts) {
                clearInterval(window._ytSwapInterval);
                console.log('YouTube Section Swapper: Timeout waiting for elements');
            }
        }, 200);
    }

    // Handle navigation
    function handleNavigation() {
        if (!window.location.pathname.includes('/watch')) {
            isSwapped = false;
            return;
        }

        console.log('YouTube Section Swapper: Navigation to watch page detected');
        waitForElementsAndSwap();
    }

    // Watch for DOM changes to detect when YouTube re-renders the layout
    function setupMutationObserver() {
        if (window._ytSwapObserver) window._ytSwapObserver.disconnect();

        window._ytSwapObserver = new MutationObserver((mutations) => {
            if (!window.location.pathname.includes('/watch')) return;

            // Check if comments or related videos were moved back by YouTube
            const comments = document.querySelector('ytd-comments#comments');
            const secondary = document.querySelector('#secondary-inner') || document.querySelector('#secondary');
            const below = document.querySelector('#below');

            if (comments && below && below.contains(comments)) {
                // YouTube put comments back in the main section, swap them again!
                swapSections();
            }
            
            // Ensure indicator is always there if swapped
            if (isSwapped && comments && secondary && secondary.contains(comments)) {
                if (!document.getElementById('youtube-swap-indicator')) {
                    addIndicator();
                }
            }
        });

        window._ytSwapObserver.observe(document.body, { childList: true, subtree: true });
    }

    // Global initializer function that can be called on navigation
    window._ytSwapInit = function() {
        handleNavigation();
    };

    // Initialize
    function init() {
        if (!window.location.hostname.includes('youtube.com')) return;

        setupKeyboardShortcut();
        setupMutationObserver();

        // Standard YouTube navigation events
        window.addEventListener('yt-navigate-finish', handleNavigation);
        window.addEventListener('yt-page-data-updated', handleNavigation);

        // Initial run
        handleNavigation();

        console.log('YouTube Section Swapper: 🚀 Active and ready');
    }

    // Start
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
