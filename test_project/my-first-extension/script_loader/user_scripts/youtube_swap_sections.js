// Move YouTube comments to the sidebar and suggested videos below the player.
// Narrow windows use YouTube theater mode. Shift+F switches to a manual
// comments/recommendations swap, which requires theater mode to be off.
(function () {
    'use strict';

    if (window._ytSwapSectionsLoaded) {
        window._ytSwapInit?.();
        return;
    }
    window._ytSwapSectionsLoaded = true;

    let observer;
    let theaterTimer;
    let swapRetryTimer;
    let resizeTimer;
    let refreshTimer;
    let manualOverride = false;
    let theaterTarget = null;
    const THEATER_WIDTH_THRESHOLD = 1800;
    const RESIZE_DEBOUNCE_MS = 400;

    const commentsSelector = 'ytd-comments#comments';
    const relatedSelector = 'ytd-watch-next-secondary-results-renderer';

    function getSecondary() {
        return document.querySelector('#secondary-inner') || document.querySelector('#secondary');
    }

    function getRelated() {
        return document.querySelector(relatedSelector);
    }

    function isTheaterMode() {
        return !!document.querySelector('ytd-watch-flexy[theater]');
    }

    function ensureTheaterMode(enabled, attempts = 20) {
        if (theaterTarget !== enabled) {
            clearTimeout(theaterTimer);
            theaterTarget = enabled;
        }
        if (isTheaterMode() === enabled) return;
        if (attempts <= 0) {
            console.warn('YouTube Section Swapper: Could not change theater mode');
            return;
        }

        const button = document.querySelector('.ytp-size-button');
        if (!button) {
            theaterTimer = setTimeout(() => ensureTheaterMode(enabled, attempts - 1), 400);
            return;
        }
        button.click();
        theaterTimer = setTimeout(() => {
            if (isTheaterMode() !== enabled) ensureTheaterMode(enabled, attempts - 1);
        }, 500);
    }

    function addStyle() {
        if (document.getElementById('youtube-section-swap-css')) return;
        const style = document.createElement('style');
        style.id = 'youtube-section-swap-css';
        style.textContent = `
            #secondary > ytd-comments#comments,
            #secondary-inner > ytd-comments#comments {
                width: 100% !important;
                max-height: calc(100vh - 120px) !important;
                overflow: auto !important;
                padding: 12px !important;
                box-sizing: border-box !important;
                display: block !important;
            }
            #swapped-video-list {
                width: 100% !important;
                margin-top: 24px;
                padding: 20px;
                box-sizing: border-box;
            }
            #swapped-video-list ytd-watch-next-secondary-results-renderer {
                display: block !important;
                width: 100% !important;
            }
            #swapped-video-list #chips { display: none !important; }
            #swapped-video-list #contents {
                display: grid !important;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)) !important;
                gap: 20px !important;
                width: 100% !important;
            }
            #swapped-video-list::before {
                content: "📺 Recommended Videos";
                display: block;
                padding: 8px 0 16px;
                font-weight: 600;
                font-size: 16px;
                border-bottom: 1px solid rgba(255,255,255,.1);
                margin-bottom: 16px;
            }
        `;
        document.head.appendChild(style);
    }

    function isSwapped() {
        const secondary = getSecondary();
        const comments = document.querySelector(commentsSelector);
        const related = getRelated();
        const wrapper = document.getElementById('swapped-video-list');
        return !!(secondary && comments && related && wrapper
            && secondary.contains(comments) && wrapper.contains(related));
    }

    function swapSections() {
        const secondary = getSecondary();
        const comments = document.querySelector(commentsSelector);
        const below = document.querySelector('#below');
        const related = getRelated();
        if (!secondary || !comments || !below || !related) return false;
        if (isSwapped()) return true;

        let commentsAnchor = document.querySelector('[data-yt-swap-anchor="comments"]');
        if (!commentsAnchor) {
            commentsAnchor = document.createElement('span');
            commentsAnchor.dataset.ytSwapAnchor = 'comments';
            commentsAnchor.hidden = true;
            comments.parentNode.insertBefore(commentsAnchor, comments);
        }
        let relatedAnchor = document.querySelector('[data-yt-swap-anchor="related"]');
        if (!relatedAnchor) {
            relatedAnchor = document.createElement('span');
            relatedAnchor.dataset.ytSwapAnchor = 'related';
            relatedAnchor.hidden = true;
            related.parentNode.insertBefore(relatedAnchor, related);
        }

        let wrapper = document.getElementById('swapped-video-list');
        if (!wrapper) {
            wrapper = document.createElement('div');
            wrapper.id = 'swapped-video-list';
        }
        wrapper.appendChild(related);
        below.appendChild(wrapper);
        secondary.appendChild(comments);
        addStyle();
        return true;
    }

    function restoreSections() {
        const comments = document.querySelector(commentsSelector);
        const related = getRelated();
        const commentsAnchor = document.querySelector('[data-yt-swap-anchor="comments"]');
        const relatedAnchor = document.querySelector('[data-yt-swap-anchor="related"]');
        if (comments && commentsAnchor?.parentNode) {
            commentsAnchor.parentNode.insertBefore(comments, commentsAnchor.nextSibling);
        }
        if (related && relatedAnchor?.parentNode) {
            relatedAnchor.parentNode.insertBefore(related, relatedAnchor.nextSibling);
        }
        document.getElementById('swapped-video-list')?.remove();
        commentsAnchor?.remove();
        relatedAnchor?.remove();
        document.getElementById('youtube-section-swap-css')?.remove();
    }

    function applyAutomaticLayout() {
        if (!location.pathname.includes('/watch') || manualOverride) return;
        if (window.innerWidth >= THEATER_WIDTH_THRESHOLD) {
            ensureTheaterMode(false);
            startSwapRetry();
        } else {
            clearInterval(swapRetryTimer);
            restoreSections();
            ensureTheaterMode(true);
        }
    }

    function startSwapRetry() {
        clearInterval(swapRetryTimer);
        let attempts = 0;
        swapRetryTimer = setInterval(() => {
            if (!location.pathname.includes('/watch') || manualOverride
                || window.innerWidth < THEATER_WIDTH_THRESHOLD) {
                clearInterval(swapRetryTimer);
                return;
            }
            if (swapSections() || ++attempts >= 60) clearInterval(swapRetryTimer);
        }, 200);
    }

    function handleNavigation() {
        manualOverride = false;
        if (location.pathname.includes('/watch')) applyAutomaticLayout();
        else {
            restoreSections();
            ensureTheaterMode(false);
        }
    }

    function init() {
        if (!location.hostname.includes('youtube.com')) return;

        document.addEventListener('keydown', (event) => {
            if (event.shiftKey && event.key.toLowerCase() === 'f'
                && location.pathname.includes('/watch')) {
                event.preventDefault();
                event.stopImmediatePropagation();
                manualOverride = true;
                if (isSwapped()) {
                    restoreSections();
                    ensureTheaterMode(false);
                } else {
                    ensureTheaterMode(false);
                    swapSections();
                }
            }
        }, true);

        window.addEventListener('yt-navigate-finish', handleNavigation);
        window.addEventListener('yt-page-data-updated', handleNavigation);
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                manualOverride = false;
                applyAutomaticLayout();
            }, RESIZE_DEBOUNCE_MS);
        });
        observer = new MutationObserver(() => {
            clearTimeout(refreshTimer);
            refreshTimer = setTimeout(() => {
                if (location.pathname.includes('/watch') && !manualOverride) applyAutomaticLayout();
            }, 250);
        });
        observer.observe(document.documentElement, { childList: true, subtree: true });

        window._ytSwapInit = handleNavigation;
        handleNavigation();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
