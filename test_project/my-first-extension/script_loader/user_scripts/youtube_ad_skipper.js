// Alternative YouTube Ad Handling Script
// This script uses multiple approaches that are harder for YouTube to detect

(function() {
    'use strict';
    
    console.log('YouTube Ad Handler: Script loaded');
    
    // Method 1: Speed up ads significantly (most effective)
    function speedUpAds() {
        const video = document.querySelector('video');
        if (!video) return;
        
        // Check if we're in an ad
        const adIndicators = [
            '.ytp-ad-player-overlay',
            '.ytp-ad-image-overlay',
            '.ad-showing',
            '[class*="ad-showing"]'
        ];
        
        const isAdPlaying = adIndicators.some(selector => document.querySelector(selector));
        
        if (isAdPlaying) {
            // Speed up the ad to 16x (makes it finish much faster)
            video.playbackRate = 16;
            video.muted = true; // Mute ads
            console.log('YouTube Ad Handler: Speeding up ad to 16x');
        } else {
            // Restore normal speed for actual content
            if (video.playbackRate > 2) {
                video.playbackRate = 1;
                video.muted = false;
            }
        }
    }
    
    // Method 2: Auto-click skip when available (backup method)
    function trySkipAd() {
        const skipSelectors = [
            '.ytp-skip-ad-button',
            '.ytp-ad-skip-button',
            'button[class*="skip"]',
            'button[aria-label*="Skip"]',
            'button[aria-label*="skip"]'
        ];
        
        for (const selector of skipSelectors) {
            const button = document.querySelector(selector);
            if (button && button.offsetParent !== null) {
                // Use a more human-like click
                setTimeout(() => {
                    button.click();
                    console.log('YouTube Ad Handler: Skip button clicked');
                }, Math.random() * 500 + 100); // Random delay 100-600ms
                return true;
            }
        }
        return false;
    }
    
    // Method 3: Remove ad overlays
    function removeAdOverlays() {
        const overlaySelectors = [
            '.ytp-ad-overlay-container',
            '.ytp-ad-image-overlay',
            '.ytp-ad-text-overlay',
            '.ytp-ad-player-overlay-skip-or-preview'
        ];
        
        overlaySelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el.style.display !== 'none') {
                    el.style.display = 'none';
                    console.log('YouTube Ad Handler: Removed ad overlay');
                }
            });
        });
    }
    
    // Method 4: Fast-forward through ads by manipulating time
    function fastForwardAd() {
        const video = document.querySelector('video');
        if (!video) return;
        
        const adIndicators = document.querySelector('.ytp-ad-player-overlay');
        if (adIndicators && video.duration) {
            // Jump to near the end of the ad
            const newTime = Math.max(0, video.duration - 1);
            if (video.currentTime < newTime) {
                video.currentTime = newTime;
                console.log('YouTube Ad Handler: Fast-forwarded ad');
            }
        }
    }
    
    // Method 5: Block ad requests (CSS-based)
    function injectAdBlockCSS() {
        if (document.getElementById('youtube-ad-block-css')) return;
        
        const style = document.createElement('style');
        style.id = 'youtube-ad-block-css';
        style.textContent = `
            /* Hide various ad elements */
            .ytp-ad-overlay-container,
            .ytp-ad-image-overlay,
            .ytp-ad-text-overlay,
            .ytp-ad-player-overlay-skip-or-preview,
            .ytp-ad-player-overlay-instream-info,
            ytd-display-ad-renderer,
            ytd-video-masthead-ad-advertiser-info-renderer,
            ytd-video-masthead-ad-primary-video-renderer,
            ytd-in-feed-ad-layout-renderer,
            ytd-ad-slot-renderer,
            yt-mealbar-promo-renderer,
            ytd-statement-banner-renderer,
            ytd-ad-slot-renderer,
            ytd-promoted-sparkles-text-search-renderer,
            #masthead-ad {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                height: 0 !important;
                width: 0 !important;
            }
            
            /* Speed up ads when they do appear */
            .ad-showing video {
                filter: brightness(0.1) !important;
            }
        `;
        document.head.appendChild(style);
        console.log('YouTube Ad Handler: CSS ad blocking applied');
    }
    
    // Main execution function
    function handleAds() {
        speedUpAds();
        trySkipAd();
        removeAdOverlays();
        fastForwardAd();
    }
    
    // Initialize
    function init() {
        // Only run on YouTube
        if (!window.location.hostname.includes('youtube.com')) return;
        
        injectAdBlockCSS();
        
        // Run immediately
        handleAds();
        
        // Set up observers for dynamic content
        const observer = new MutationObserver(() => {
            handleAds();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Also run on interval as backup
        setInterval(handleAds, 1000);
        
        console.log('YouTube Ad Handler: Initialized with multiple methods');
    }
    
    // Start when page is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();