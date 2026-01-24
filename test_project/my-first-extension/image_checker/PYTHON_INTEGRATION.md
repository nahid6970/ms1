# Python Server Integration - Quick Start

## What's Been Added

Your Image Checker extension now automatically saves data to your Python server!

### New Files
- `background.js` - Handles communication with Python server

### Modified Files
- `manifest.json` - Added localhost permission and background service worker
- `popup.html` - Added "Save to Python Server" button
- `popup.js` - Added manual save functionality

## How to Use

### 1. Start Python Server
```bash
python extension_manager.py
```
Server runs on `http://localhost:8765`

### 2. Reload Extension
1. Go to `chrome://extensions/`
2. Click the reload icon on your Image Checker extension

### 3. Data Saves Automatically!
- Every time you mark/unmark an image, data auto-saves to Python server
- Data saves to: `extension_data/image_checker/image_checker_data.json`

### 4. Manual Save (Optional)
Click the purple "💾 Save to Python Server" button in the popup

## Features

✅ **Auto-save** - Data saves automatically on every change
✅ **Manual save** - Button for on-demand saves
✅ **Works offline** - Extension works even if server is down
✅ **Health checks** - Verifies server connection on startup

## File Location

Your data saves to:
```
extension_data/
└── image_checker/
    └── image_checker_data.json
```

## Customization

Edit `background.js` to change:
- `EXTENSION_NAME` - Folder name (default: 'image_checker')
- `FILE_NAME` - File name (default: 'image_checker_data.json')
- `PYTHON_SERVER` - Server URL (default: 'http://localhost:8765')

## Troubleshooting

**Button says "Failed to save":**
- Make sure Python server is running
- Check console for errors (F12 → Console)

**No auto-save:**
- Reload the extension after starting Python server
- Check background service worker logs in `chrome://extensions/`
