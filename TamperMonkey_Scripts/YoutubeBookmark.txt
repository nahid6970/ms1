// ==UserScript==
// @name         YouTube Bookmark with Categories, CSV Export/Import, and Reset
// @namespace    http://tampermonkey.net/
// @version      1.9
// @description  Add a bookmark button to categorize YouTube videos and export/import bookmarks to/from CSV file and reset the data.
// @author       YourName
// @match        https://www.youtube.com/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // Function to create the "Bookmark" button
    function createBookmarkButton(videoId, thumbnail) {
        const button = document.createElement('button');
        button.innerText = '📌 Bookmark';
        button.style.position = 'absolute';
        button.style.top = '10px';
        button.style.left = '10px'; // Change to top-left
        button.style.backgroundColor = '#2196F3';
        button.style.color = 'white';
        button.style.border = 'none';
        button.style.borderRadius = '4px';
        button.style.padding = '5px 10px';
        button.style.cursor = 'pointer';
        button.style.zIndex = '10';
        button.setAttribute('data-video-id', videoId);

        button.addEventListener('click', () => {
            showBookmarkOptions(videoId, thumbnail, button);
        });

        return button;
    }

    // Function to show the 3 bookmark options ❤️, 🎯, ⭕)
    function showBookmarkOptions(videoId, thumbnail, bookmarkButton) {
        const optionsContainer = document.createElement('div');
        optionsContainer.style.position = 'absolute';
        optionsContainer.style.top = '40px';
        optionsContainer.style.left = '10px'; // Change to top-left
        optionsContainer.style.zIndex = '10';
        optionsContainer.style.backgroundColor = '#ffffff';
        optionsContainer.style.border = '1px solid #ccc';
        optionsContainer.style.padding = '5px';
        optionsContainer.style.borderRadius = '4px';
        optionsContainer.style.display = 'flex';
        optionsContainer.style.gap = '5px';

        // ❤️ - For loving videos
        const loveButton = document.createElement('button');
        loveButton.innerText = '❤️';
        loveButton.style.backgroundColor = '#FF4081';
        loveButton.style.border = 'none';
        loveButton.style.padding = '5px';
        loveButton.style.cursor = 'pointer';

        loveButton.addEventListener('click', () => {
            addBookmark(videoId, 'love');
            replaceBookmarkButton(bookmarkButton, '❤️');
            optionsContainer.remove();
        });

        // 🎯 - For important videos
        const importantButton = document.createElement('button');
        importantButton.innerText = '🎯';
        importantButton.style.backgroundColor = '#FF9800';
        importantButton.style.border = 'none';
        importantButton.style.padding = '5px';
        importantButton.style.cursor = 'pointer';

        importantButton.addEventListener('click', () => {
            addBookmark(videoId, 'important');
            replaceBookmarkButton(bookmarkButton, '🎯');
            optionsContainer.remove();
        });

        // ⭕ - For Linux-related videos
        const linuxButton = document.createElement('button');
        linuxButton.innerText = '⭕';
        linuxButton.style.backgroundColor = '#4CAF50';
        linuxButton.style.border = 'none';
        linuxButton.style.padding = '5px';
        linuxButton.style.cursor = 'pointer';

        linuxButton.addEventListener('click', () => {
            addBookmark(videoId, 'linux');
            replaceBookmarkButton(bookmarkButton, '⭕');
            optionsContainer.remove();
        });

        // Append buttons to the options container
        optionsContainer.appendChild(loveButton);
        optionsContainer.appendChild(importantButton);
        optionsContainer.appendChild(linuxButton);

        // Append the options container to the thumbnail
        thumbnail.appendChild(optionsContainer);
    }

    // Function to add the video to a category in localStorage along with its video ID
    function addBookmark(videoId, category) {
        const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;

        const bookmarks = JSON.parse(localStorage.getItem('videoBookmarks') || '{}');
        if (!bookmarks[category]) {
            bookmarks[category] = [];
        }
        const existingBookmark = bookmarks[category].find(item => item.videoId === videoId);
        if (!existingBookmark) {
            bookmarks[category].push({ videoId, videoUrl });
            localStorage.setItem('videoBookmarks', JSON.stringify(bookmarks));
        }
    }

    // Function to replace the bookmark icon with the selected category icon
    function replaceBookmarkButton(bookmarkButton, category) {
        bookmarkButton.innerText = category; // Replace text with the category emoji
        bookmarkButton.style.backgroundColor = 'transparent';
        bookmarkButton.style.color = '#333'; // Use a dark color for the emoji
        bookmarkButton.disabled = true; // Disable the button to prevent further clicks
    }

    // Function to create a "Bookmark" button and add it to the thumbnail
    function addBookmarkButton() {
        const thumbnails = document.querySelectorAll('ytd-thumbnail');
        thumbnails.forEach(thumbnail => {
            const videoLink = thumbnail.querySelector('a#thumbnail');
            if (!videoLink) return;

            const url = new URL(videoLink.href, window.location.origin);
            const videoId = url.searchParams.get('v');
            if (!videoId || thumbnail.querySelector('.bookmark-button')) return;

            const button = createBookmarkButton(videoId, thumbnail);
            button.classList.add('bookmark-button');
            thumbnail.style.position = 'relative';
            thumbnail.appendChild(button);

            // Load the saved category from localStorage and update the button
            loadCategoryFromLocalStorage(videoId, button);
        });
    }

    // Function to load the category from localStorage
    function loadCategoryFromLocalStorage(videoId, bookmarkButton) {
        const bookmarks = JSON.parse(localStorage.getItem('videoBookmarks') || '{}');
        for (const category in bookmarks) {
            const video = bookmarks[category].find(item => item.videoId === videoId);
            if (video) {
                // Replace the button text with the appropriate emoji
                replaceBookmarkButton(bookmarkButton, category === 'love' ? '❤️' : category === 'important' ? '🎯' : '⭕');
                break;
            }
        }
    }

    // Function to export the bookmarks to CSV
    function exportToCSV() {
        const bookmarks = JSON.parse(localStorage.getItem('videoBookmarks') || '{}');
        let csvContent = 'Video ID,Category,URL\n';

        // Iterate through each category and its videos
        for (const category in bookmarks) {
            bookmarks[category].forEach(item => {
                csvContent += `${item.videoId},${category},${item.videoUrl}\n`;
            });
        }

        // Create a temporary link to download the CSV file
        const encodedUri = encodeURI('data:text/csv;charset=utf-8,' + csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'bookmarked_videos.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // Function to import bookmarks from CSV
    function importFromCSV(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (e) {
            const content = e.target.result;
            const rows = content.split('\n').slice(1); // Skip header row
            const bookmarks = {};

            rows.forEach(row => {
                const [videoId, category, videoUrl] = row.split(',');
                if (videoId && category && videoUrl) {
                    if (!bookmarks[category]) bookmarks[category] = [];
                    bookmarks[category].push({ videoId, videoUrl });
                }
            });

            localStorage.setItem('videoBookmarks', JSON.stringify(bookmarks));
            alert('Bookmarks imported successfully!');
            location.reload();
        };
        reader.readAsText(file);
    }

    // Function to reset the bookmarks
    function resetBookmarks() {
        localStorage.removeItem('videoBookmarks');
        alert('Bookmarks have been reset.');
        location.reload();
    }

    // Add buttons for Export, Import, Reset, and Tool
    function addControlButtons() {
        const controlContainer = document.createElement('div');
        controlContainer.style.position = 'fixed';
        controlContainer.style.bottom = '10px';
        controlContainer.style.right = '10px';
        controlContainer.style.zIndex = '1000';
        controlContainer.style.display = 'flex';
        controlContainer.style.flexDirection = 'column';
        controlContainer.style.gap = '10px';

        // Tool Button to toggle visibility of other buttons
        const toolButton = document.createElement('button');
        toolButton.innerText = '🔧 Tools';
        toolButton.style.backgroundColor = '#3f51b5';
        toolButton.style.color = 'white';
        toolButton.style.border = 'none';
        toolButton.style.padding = '10px 20px';
        toolButton.style.borderRadius = '5px';
        toolButton.style.cursor = 'pointer';

        const buttonsContainer = document.createElement('div');
        buttonsContainer.style.display = 'none'; // Hidden by default
        buttonsContainer.style.flexDirection = 'column';
        buttonsContainer.style.gap = '10px';

        // Export Button
        const exportButton = document.createElement('button');
        exportButton.innerText = 'Export Bookmarks to CSV';
        exportButton.style.backgroundColor = '#4CAF50';
        exportButton.style.color = 'white';
        exportButton.style.border = 'none';
        exportButton.style.padding = '10px 20px';
        exportButton.style.borderRadius = '5px';
        exportButton.style.cursor = 'pointer';
        exportButton.addEventListener('click', exportToCSV);

        // Import Button
        const importButton = document.createElement('input');
        importButton.type = 'file';
        importButton.style.display = 'none';
        importButton.addEventListener('change', importFromCSV);

        const importButtonContainer = document.createElement('button');
        importButtonContainer.innerText = 'Import Bookmarks from CSV';
        importButtonContainer.style.backgroundColor = '#FF9800';
        importButtonContainer.style.color = 'white';
        importButtonContainer.style.border = 'none';
        importButtonContainer.style.padding = '10px 20px';
        importButtonContainer.style.borderRadius = '5px';
        importButtonContainer.style.cursor = 'pointer';
        importButtonContainer.addEventListener('click', () => importButton.click());

        // Reset Button
        const resetButton = document.createElement('button');
        resetButton.innerText = 'Reset Bookmarks';
        resetButton.style.backgroundColor = '#f44336';
        resetButton.style.color = 'white';
        resetButton.style.border = 'none';
        resetButton.style.padding = '10px 20px';
        resetButton.style.borderRadius = '5px';
        resetButton.style.cursor = 'pointer';
        resetButton.addEventListener('click', resetBookmarks);

        buttonsContainer.appendChild(exportButton);
        buttonsContainer.appendChild(importButtonContainer);
        buttonsContainer.appendChild(resetButton);

        toolButton.addEventListener('click', () => {
            buttonsContainer.style.display = buttonsContainer.style.display === 'none' ? 'flex' : 'none';
        });

        controlContainer.appendChild(toolButton);
        controlContainer.appendChild(buttonsContainer);
        document.body.appendChild(controlContainer);
    }

    // Initialize the script
    addControlButtons();
    setInterval(addBookmarkButton, 1000);
})();
