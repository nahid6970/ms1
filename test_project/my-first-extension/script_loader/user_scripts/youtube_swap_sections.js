// YouTube Comments-Sidebar Swapper + Auto Theater Mode
// - Windowed browser (<FULL_WIDTH_THRESHOLD):  enable theater mode + swap DOM
//   (comments in sidebar, recommended grid below)
// - Maximized browser (>=FULL_WIDTH_THRESHOLD): disable theater mode + restore DOM
//
// Shift+F → manual toggle at any window size

(function () {
    'use strict';

    // ─── CONFIG ──────────────────────────────────────────────────────────────
    // Width (px) below which we consider the window "windowed / resized".
    // On a 1920-wide screen the maximized inner width is ~1920 (minus scrollbar).
    // 1800 gives a safe ~120 px buffer.
    const FULL_WIDTH_THRESHOLD = 1800;

    // Debounce delay for the resize handler (ms)
    const RESIZE_DEBOUNCE_MS = 400;
    // ─────────────────────────────────────────────────────────────────────────

    // Prevent multiple injections
    if (window._ytSwapSectionsLoaded) {
        console.log('YouTube Section Swapper: already loaded, skipping re-injection');
        if (typeof window._ytSwapInit === 'function') window._ytSwapInit();
        return;
    }
    window._ytSwapSectionsLoaded = true;

    console.log('YouTube Section Swapper: initializing…');

    let isSwapped = false;

    // ── helpers ──────────────────────────────────────────────────────────────

    function isFullWidth() {
        return window.innerWidth >= FULL_WIDTH_THRESHOLD;
    }

    // ── Theater mode ─────────────────────────────────────────────────────────

    /** Returns true if YouTube is currently in theater mode. */
    function isTheaterMode() {
        const player = document.querySelector('ytd-watch-flexy');
        return player ? player.hasAttribute('theater') : false;
    }

    /**
     * Click YouTube's theater-mode button to toggle it.
     * The button lives inside the player controls.
     */
    function clickTheaterButton() {
        // Primary selector (current YouTube DOM)
        const btn =
            document.querySelector('.ytp-size-button') ||
            document.querySelector('button.ytp-size-button');
        if (btn) {
            btn.click();
            return true;
        }
        return false;
    }

    /**
     * Ensure theater mode is ON.
     * Retries up to `retries` times with `interval` ms gaps.
     */
    function enableTheaterMode(retries = 15, interval = 300) {
        if (isTheaterMode()) return; // already on

        if (!clickTheaterButton()) {
            // Button not found yet — retry
            if (retries > 0) {
                setTimeout(() => enableTheaterMode(retries - 1, interval), interval);
            }
            return;
        }

        // Give YouTube a moment to apply the attribute, then verify
        setTimeout(() => {
            if (!isTheaterMode() && retries > 0) {
                enableTheaterMode(retries - 1, interval);
            } else {
                console.log('YouTube Section Swapper: 🎭 Theater mode ON');
            }
        }, interval);
    }

    /**
     * Ensure theater mode is OFF.
     */
    function disableTheaterMode(retries = 10, interval = 300) {
        if (!isTheaterMode()) return; // already off

        if (!clickTheaterButton()) {
            if (retries > 0) {
                setTimeout(() => disableTheaterMode(retries - 1, interval), interval);
            }
            return;
        }

        setTimeout(() => {
            if (isTheaterMode() && retries > 0) {
                disableTheaterMode(retries - 1, interval);
            } else {
                console.log('YouTube Section Swapper: 🎭 Theater mode OFF');
            }
        }, interval);
    }

    // ── DOM swap ─────────────────────────────────────────────────────────────

    function swapSections() {
        const secondary = document.querySelector('#secondary-inner') || document.querySelector('#secondary');
        const comments  = document.querySelector('ytd-comments#comments');
        const below     = document.querySelector('#below');

        if (!secondary || !comments || !below) return false;

        // Already swapped
        if (secondary.contains(comments) && document.getElementById('swapped-video-list')) {
            isSwapped = true;
            return true;
        }

        const relatedContainer = document.querySelector('ytd-watch-next-secondary-results-renderer');
        if (!relatedContainer) return false;

        // Wrapper for related videos
        let videoListWrapper = document.getElementById('swapped-video-list');
        if (!videoListWrapper) {
            videoListWrapper = document.createElement('div');
            videoListWrapper.id = 'swapped-video-list';
        }

        videoListWrapper.appendChild(relatedContainer);
        below.appendChild(videoListWrapper);
        secondary.appendChild(comments);

        injectSwapCSS();

        isSwapped = true;
        console.log('YouTube Section Swapper: ✅ DOM swapped (windowed mode)');
        return true;
    }

    function restoreSections() {
        const secondary       = document.querySelector('#secondary-inner') || document.querySelector('#secondary');
        const comments        = document.querySelector('ytd-comments#comments');
        const below           = document.querySelector('#below');
        const relatedContainer = document.querySelector('ytd-watch-next-secondary-results-renderer');
        const videoListWrapper = document.getElementById('swapped-video-list');

        if (!secondary || !below) return;

        if (comments)        below.appendChild(comments);
        if (relatedContainer) secondary.appendChild(relatedContainer);
        if (videoListWrapper) videoListWrapper.remove();

        removeSwapCSS();

        isSwapped = false;
        console.log('YouTube Section Swapper: ✅ DOM restored (maximized mode)');
    }

    // ── CSS ──────────────────────────────────────────────────────────────────

    function injectSwapCSS() {
        if (document.getElementById('youtube-section-swap-css')) return;

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
                border: 1px solid rgba(255,255,255,0.08) !important;
                box-sizing: border-box !important;
                display: block !important;
            }

            #secondary ytd-comments#comments #sections {
                overflow: visible !important;
                height: auto !important;
            }

            #secondary > ytd-comments::-webkit-scrollbar,
            #secondary-inner > ytd-comments::-webkit-scrollbar { width: 8px; }
            #secondary > ytd-comments::-webkit-scrollbar-track,
            #secondary-inner > ytd-comments::-webkit-scrollbar-track { background: transparent; }
            #secondary > ytd-comments::-webkit-scrollbar-thumb,
            #secondary-inner > ytd-comments::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg,#ff0050 0%,#7b2ff7 100%);
                border-radius: 4px;
            }

            /* ===== VIDEO GRID BELOW ===== */
            #swapped-video-list {
                margin-top: 24px;
                padding: 20px;
                background: var(--yt-spec-brand-background-secondary, #0f0f0f);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.08);
                width: 100% !important;
            }
            #swapped-video-list ytd-watch-next-secondary-results-renderer {
                display: block !important;
                width: 100% !important;
            }
            #swapped-video-list #chips    { display: none !important; }
            #swapped-video-list #contents {
                display: grid !important;
                grid-template-columns: repeat(auto-fill, minmax(280px,1fr)) !important;
                gap: 20px !important;
                width: 100% !important;
            }
            #swapped-video-list::before {
                content: "📺 Recommended Videos";
                display: block;
                padding: 8px 0 16px 0;
                font-weight: 600;
                font-size: 16px;
                color: var(--yt-spec-text-primary, #fff);
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 16px;
            }
        `;
        document.head.appendChild(style);
    }

    function removeSwapCSS() {
        const style = document.getElementById('youtube-section-swap-css');
        if (style) style.remove();
    }

    // ── Combined swap + theater ───────────────────────────────────────────────

    /** Activate windowed mode: DOM swap + theater mode ON */
    function activateWindowedMode() {
        enableTheaterMode();          // YouTube theater mode ON
        waitForElementsAndSwap();     // DOM swap (polls until elements ready)
    }

    /** Activate maximized mode: restore DOM + theater mode OFF */
    function activateMaximizedMode() {
        disableTheaterMode();         // YouTube theater mode OFF
        if (isSwapped) restoreSections(); // restore DOM if needed
    }

    // ── Window-size decision ──────────────────────────────────────────────────

    function applyLayoutForWindowSize() {
        if (!window.location.pathname.includes('/watch')) return;

        if (isFullWidth()) {
            console.log(`YouTube Section Swapper: innerWidth=${window.innerWidth} → MAXIMIZED mode`);
            activateMaximizedMode();
        } else {
            console.log(`YouTube Section Swapper: innerWidth=${window.innerWidth} → WINDOWED mode`);
            activateWindowedMode();
        }
    }

    // Debounced resize
    let _resizeTimer = null;
    function onWindowResize() {
        clearTimeout(_resizeTimer);
        _resizeTimer = setTimeout(applyLayoutForWindowSize, RESIZE_DEBOUNCE_MS);
    }

    // ── Manual toggle (Shift+F) ───────────────────────────────────────────────

    function toggleSwap() {
        if (isSwapped) {
            activateMaximizedMode();
        } else {
            activateWindowedMode();
        }
    }

    function setupKeyboardShortcut() {
        document.removeEventListener('keydown', window._ytSwapKeyHandler, true);
        window._ytSwapKeyHandler = (e) => {
            if (e.shiftKey && e.key.toLowerCase() === 'f') {
                if (window.location.pathname.includes('/watch')) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    toggleSwap();
                }
            }
        };
        document.addEventListener('keydown', window._ytSwapKeyHandler, true);
        console.log('YouTube Section Swapper: 🎹 Shift+F toggle active');
    }

    // ── Polling swap ─────────────────────────────────────────────────────────

    function waitForElementsAndSwap() {
        let attempts = 0;
        const maxAttempts = 60;

        if (window._ytSwapInterval) clearInterval(window._ytSwapInterval);

        window._ytSwapInterval = setInterval(() => {
            attempts++;

            if (!window.location.pathname.includes('/watch')) {
                clearInterval(window._ytSwapInterval);
                return;
            }
            if (isFullWidth()) {
                clearInterval(window._ytSwapInterval);
                return;
            }

            const success = swapSections();

            if (success && attempts > 15) {
                clearInterval(window._ytSwapInterval);
            } else if (attempts >= maxAttempts) {
                clearInterval(window._ytSwapInterval);
                console.log('YouTube Section Swapper: timeout waiting for elements');
            }
        }, 200);
    }

    // ── Navigation ────────────────────────────────────────────────────────────

    function handleNavigation() {
        if (!window.location.pathname.includes('/watch')) {
            isSwapped = false;
            return;
        }
        console.log('YouTube Section Swapper: watch page navigation detected');
        applyLayoutForWindowSize();
    }

    function setupMutationObserver() {
        if (window._ytSwapObserver) window._ytSwapObserver.disconnect();
    }

    window._ytSwapInit = function () { handleNavigation(); };

    // ── Init ─────────────────────────────────────────────────────────────────

    function init() {
        if (!window.location.hostname.includes('youtube.com')) return;

        setupKeyboardShortcut();
        setupMutationObserver();

        window.addEventListener('yt-navigate-finish', handleNavigation);
        window.addEventListener('yt-page-data-updated', handleNavigation);
        window.addEventListener('resize', onWindowResize);

        handleNavigation();

        console.log(
            `YouTube Section Swapper: 🚀 Active | innerWidth=${window.innerWidth} | ` +
            `initial mode=${isFullWidth() ? 'MAXIMIZED' : 'WINDOWED'}`
        );
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
