// YouTube Comments-Sidebar Swapper
// Swaps the comments section with the recommended videos sidebar
// Comments go to the right sidebar, Video list goes below the video

(function () {
    'use strict';

    let isSwapped = false;
    let swapApplied = false;

    // Swap comments with sidebar video list
    function swapSections() {
        const secondary = document.querySelector('#secondary-inner, #secondary');
        const comments = document.querySelector('ytd-comments#comments');
        const below = document.querySelector('#below');

        if (!secondary || !comments || !below || swapApplied) return false;

        const relatedContainer = secondary.querySelector('ytd-watch-next-secondary-results-renderer');
        if (!relatedContainer) return false;

        let videoListWrapper = document.getElementById('swapped-video-list');
        if (!videoListWrapper) {
            videoListWrapper = document.createElement('div');
            videoListWrapper.id = 'swapped-video-list';
        }

        videoListWrapper.appendChild(relatedContainer);
        below.appendChild(videoListWrapper);
        secondary.appendChild(comments);

        injectSwapCSS();
        swapApplied = true;
        isSwapped = true;
        return true;
    }

    // Restore original layout
    function restoreSections() {
        const secondary = document.querySelector('#secondary-inner, #secondary');
        const comments = document.querySelector('ytd-comments#comments');
        const below = document.querySelector('#below');
        const relatedContainer = document.querySelector('ytd-watch-next-secondary-results-renderer');
        const videoListWrapper = document.getElementById('swapped-video-list');

        if (!secondary || !below) return;

        if (comments) below.appendChild(comments);
        if (relatedContainer) secondary.appendChild(relatedContainer);
        if (videoListWrapper) videoListWrapper.remove();

        removeSwapCSS();
        swapApplied = false;
        isSwapped = false;
    }

    // CSS styling for swapped layout
    function injectSwapCSS() {
        if (document.getElementById('youtube-section-swap-css')) return;

        const style = document.createElement('style');
        style.id = 'youtube-section-swap-css';
        style.textContent = `
            /* ===== COMMENTS IN SIDEBAR ===== */
            #secondary > ytd-comments#comments,
            #secondary-inner > ytd-comments#comments {
                width: 100% !important;
                max-height: calc(100vh - 100px) !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                padding: 8px !important;
                background: var(--yt-spec-brand-background-secondary, #0f0f0f) !important;
                border-radius: 12px !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            
            /* Scrollbar for sidebar comments */
            #secondary > ytd-comments::-webkit-scrollbar,
            #secondary-inner > ytd-comments::-webkit-scrollbar {
                width: 6px;
            }
            
            #secondary > ytd-comments::-webkit-scrollbar-track,
            #secondary-inner > ytd-comments::-webkit-scrollbar-track {
                background: transparent;
            }
            
            #secondary > ytd-comments::-webkit-scrollbar-thumb,
            #secondary-inner > ytd-comments::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, #ff0050 0%, #7b2ff7 100%);
                border-radius: 3px;
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
            
            /* Force the main container to be block */
            #swapped-video-list ytd-watch-next-secondary-results-renderer {
                display: block !important;
                width: 100% !important;
            }
            
            /* Hide the chips filter bar */
            #swapped-video-list #chips {
                display: none !important;
            }
            
            /* ===== FORCE GRID ON ALL CONTENT CONTAINERS ===== */
            #swapped-video-list #contents {
                display: grid !important;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)) !important;
                gap: 20px !important;
                width: 100% !important;
                flex-wrap: wrap !important;
            }
            
            #swapped-video-list ytd-item-section-renderer {
                display: contents !important;
            }
            
            #swapped-video-list ytd-item-section-renderer #contents {
                display: grid !important;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)) !important;
                gap: 20px !important;
                width: 100% !important;
            }
            
            /* Hide continuation items */
            #swapped-video-list ytd-continuation-item-renderer {
                display: none !important;
            }
            
            /* ===== VIDEO CARDS (yt-lockup-view-model) ===== */
            #swapped-video-list yt-lockup-view-model {
                display: flex !important;
                flex-direction: column !important;
                width: 100% !important;
                max-width: 100% !important;
                height: auto !important;
                margin: 0 !important;
                background: rgba(255, 255, 255, 0.03) !important;
                border-radius: 12px !important;
                overflow: hidden !important;
                transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease !important;
            }
            
            #swapped-video-list yt-lockup-view-model:hover {
                transform: translateY(-6px) scale(1.02) !important;
                background: rgba(255, 255, 255, 0.06) !important;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
            }
            
            /* Inner div of yt-lockup-view-model */
            #swapped-video-list yt-lockup-view-model > div {
                display: flex !important;
                flex-direction: column !important;
                width: 100% !important;
            }
            
            /* Thumbnail in new format */
            #swapped-video-list yt-lockup-view-model yt-thumbnail,
            #swapped-video-list yt-lockup-view-model .yt-thumbnail-view-model {
                width: 100% !important;
                aspect-ratio: 16/9 !important;
            }
            
            #swapped-video-list yt-lockup-view-model img {
                width: 100% !important;
                height: 100% !important;
                object-fit: cover !important;
                border-radius: 12px 12px 0 0 !important;
            }
            
            /* Metadata in new format */
            #swapped-video-list yt-lockup-view-model .yt-lockup-metadata-view-model,
            #swapped-video-list yt-lockup-view-model .lockup-metadata {
                padding: 12px !important;
            }
            
            /* ===== OLD YouTube elements (ytd-compact-video-renderer) ===== */
            #swapped-video-list ytd-compact-video-renderer,
            #swapped-video-list ytd-compact-radio-renderer,
            #swapped-video-list ytd-compact-playlist-renderer {
                display: flex !important;
                flex-direction: column !important;
                width: 100% !important;
                background: rgba(255, 255, 255, 0.03) !important;
                border-radius: 12px !important;
                overflow: hidden !important;
                transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease !important;
            }
            
            #swapped-video-list ytd-compact-video-renderer:hover,
            #swapped-video-list ytd-compact-radio-renderer:hover,
            #swapped-video-list ytd-compact-playlist-renderer:hover {
                transform: translateY(-6px) scale(1.02) !important;
                background: rgba(255, 255, 255, 0.06) !important;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
            }
            
            /* Thumbnail styling (old format) */
            #swapped-video-list ytd-thumbnail {
                width: 100% !important;
                margin: 0 !important;
            }
            
            #swapped-video-list ytd-thumbnail #thumbnail {
                width: 100% !important;
                border-radius: 12px 12px 0 0 !important;
            }
            
            #swapped-video-list ytd-compact-video-renderer img,
            #swapped-video-list ytd-thumbnail img {
                width: 100% !important;
                height: auto !important;
                aspect-ratio: 16/9 !important;
                object-fit: cover !important;
            }
            
            /* Video details styling */
            #swapped-video-list .details,
            #swapped-video-list #details {
                padding: 12px !important;
                flex: 1 !important;
            }
            
            #swapped-video-list #video-title,
            #swapped-video-list .video-title {
                font-size: 14px !important;
                font-weight: 500 !important;
                line-height: 1.4 !important;
                margin-bottom: 8px !important;
                display: -webkit-box !important;
                -webkit-line-clamp: 2 !important;
                -webkit-box-orient: vertical !important;
                overflow: hidden !important;
            }
            
            #swapped-video-list #metadata,
            #swapped-video-list .metadata {
                font-size: 12px !important;
                color: var(--yt-spec-text-secondary) !important;
            }
            
            /* Hide dismissible container properly */
            #swapped-video-list #dismissible {
                display: flex !important;
                flex-direction: column !important;
                width: 100% !important;
            }
            
            /* ===== INDICATOR BANNER ===== */
            #youtube-swap-indicator {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 8px 12px;
                margin-bottom: 12px;
                background: linear-gradient(135deg, #ff0050 0%, #7b2ff7 50%, #00d4ff 100%);
                color: white;
                font-weight: 600;
                font-size: 11px;
                border-radius: 8px;
                text-align: center;
                letter-spacing: 0.3px;
                box-shadow: 0 4px 15px rgba(123, 47, 247, 0.3);
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
        addIndicator();
    }

    // Add visual indicator
    function addIndicator() {
        const comments = document.querySelector('#secondary ytd-comments#comments, #secondary-inner ytd-comments#comments');
        if (!comments || document.getElementById('youtube-swap-indicator')) return;

        const indicator = document.createElement('div');
        indicator.id = 'youtube-swap-indicator';
        indicator.innerHTML = `
            <span>🔄 Comments ↔ Videos Swapped</span>
            <span class="swap-hotkey">Alt+Q to toggle</span>
        `;
        comments.insertBefore(indicator, comments.firstChild);
    }

    // Remove swap CSS
    function removeSwapCSS() {
        document.getElementById('youtube-section-swap-css')?.remove();
        document.getElementById('youtube-swap-indicator')?.remove();
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
    document.addEventListener('keydown', (e) => {
        if (e.altKey && e.key.toLowerCase() === 'q') {
            e.preventDefault();
            toggleSwap();
        }
    });

    // Wait for all elements to load and then swap
    function waitForElementsAndSwap() {
        if (window._ytSwapInterval) clearInterval(window._ytSwapInterval);

        let attempts = 0;
        window._ytSwapInterval = setInterval(() => {
            const comments = document.querySelector('ytd-comments#comments');
            const secondary = document.querySelector('#secondary-inner, #secondary');
            const relatedVideos = document.querySelector('ytd-watch-next-secondary-results-renderer');
            const below = document.querySelector('#below');

            if (++attempts > 60) {
                clearInterval(window._ytSwapInterval);
                return;
            }

            if (comments && secondary && relatedVideos && below && comments.offsetHeight > 0) {
                clearInterval(window._ytSwapInterval);
                setTimeout(() => swapSections(), 200);
            }
        }, 200);
    }

    // Reset state and prepare for new page
    function resetState() {
        swapApplied = false;
        isSwapped = false;
        document.getElementById('youtube-swap-indicator')?.remove();
        document.getElementById('youtube-section-swap-css')?.remove();
        document.getElementById('swapped-video-list')?.remove();
    }

    // Handle page navigation (YouTube SPA)
    function handleNavigation() {
        resetState();
        if (window.location.pathname.includes('/watch')) {
            setTimeout(waitForElementsAndSwap, 800);
        }
    }

    // Initialize
    if (!window.location.hostname.includes('youtube.com')) return;

    window.addEventListener('yt-navigate-finish', handleNavigation);
    window.addEventListener('yt-navigate-start', () => {
        if (window._ytSwapInterval) clearInterval(window._ytSwapInterval);
    });

    let lastUrl = location.href;
    new MutationObserver(() => {
        if (location.href !== lastUrl) {
            lastUrl = location.href;
            handleNavigation();
        }
    }).observe(document.body, { childList: true, subtree: true });

    if (window.location.pathname.includes('/watch')) {
        setTimeout(waitForElementsAndSwap, 1000);
    }

})();
