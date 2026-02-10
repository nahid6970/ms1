# Quick Start Guide

## 1. Install Prerequisites

```bash
# Install yt-dlp
pip install yt-dlp

# Install Pillow (for creating icons)
pip install pillow
```

## 2. Create Icons

```bash
cd chrome-extension
python create_icons.py
```

## 3. Install Native Host

```bash
python install_host.py
```

This will:
- Create the native messaging manifest
- Register it with Chrome's registry
- Show you the next steps

## 4. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder
5. **Copy the Extension ID** (looks like: `abcdefghijklmnopqrstuvwxyz123456`)

## 5. Update Extension ID

1. Open `com.ytc.subtitle_extractor.json`
2. Find the line: `"chrome-extension://YOUR_EXTENSION_ID_HERE/"`
3. Replace `YOUR_EXTENSION_ID_HERE` with your actual Extension ID
4. Save the file

## 6. Reload Extension

1. Go back to `chrome://extensions/`
2. Click the reload icon (circular arrow) on your extension

## 7. Configure Settings

1. Click the extension icon in Chrome toolbar
2. Click "⚙️ Settings" at the bottom
3. Set **Save Directory** (e.g., `C:\Downloads\Subtitles`)
4. Configure authentication if needed (for private videos)
5. Set default language and format
6. Click "SAVE SETTINGS"

## 8. Use It!

1. Go to any video page (YouTube, Vimeo, etc.)
2. Click the extension icon
3. Adjust settings if needed
4. Click "EXTRACT SUBTITLES"
5. Find your subtitles in the save directory!

## Common Issues

### "Native host has exited"
- Make sure you ran `install_host.py`
- Verify the Extension ID in `com.ytc.subtitle_extractor.json` is correct
- Reload the extension after updating the ID

### "Set save directory in settings first"
- Click the extension icon → Settings
- Enter a full path like `C:\Downloads\Subtitles`
- Click "SAVE SETTINGS"

### No subtitles downloaded
- Enable "Include auto-generated" option
- Try "All" languages option
- Check if the video actually has subtitles

## Features

- **Multiple Languages**: English, Bengali, Hindi, or All
- **Multiple Formats**: SRT, VTT, or clean TXT
- **Timeline Range**: Extract only specific time ranges
- **Auto-detection**: Automatically detects `?t=` timestamp in URLs
- **Authentication**: Support for browser cookies or cookie files

## Example URLs to Test

- YouTube: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- With timestamp: `https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42`

Enjoy! 🎬
