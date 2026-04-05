# Image Checker Chrome Extension

A Chrome extension that allows you to mark images with green checkmarks on any website.

## Features

- Click the extension icon to toggle "checking mode"
- When active, click on any image to add/remove a green checkmark
- Works on all images, videos, and elements with background images
- Clear all checkmarks with one button
- Visual feedback and notifications

## How to Use

1. Install the extension in Chrome
2. Navigate to any website (like YouTube)
3. Click the Image Checker extension icon
4. Click "Start Checking Mode"
5. Click on any image/video to mark it with a green checkmark
6. Click again to remove the checkmark
7. Use "Clear All Checkmarks" to remove all marks
8. Click "Stop Checking Mode" when done

## Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `image_checker` folder
4. The extension will appear in your toolbar

## Files Structure

- `manifest.json` - Extension configuration
- `popup.html` - Extension popup interface
- `popup.js` - Popup functionality
- `content.js` - Main functionality that runs on web pages
- `styles.css` - Styling for checkmarks and notifications

Note: You'll need to add icon files (16x16, 48x48, 128x128 PNG) in the `assets` folder for the extension to display properly.