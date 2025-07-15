// ==UserScript==
// @name         YouTube Ad Skipper
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Automatically clicks the "Skip Ad" button on YouTube.
// @author       You
// @match        *://www.youtube.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    setInterval(() => {
        const skipButton = document.querySelector('.ytp-skip-ad-button');
        if (skipButton) {
            skipButton.click();
        }
    }, 1000);
})();
