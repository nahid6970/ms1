# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install yt-dlp pillow
```

### 2. Generate Icons
```bash
cd chrome-extension-video
python create_icons.py
```

### 3. Load in Chrome
1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" → select `chrome-extension-video` folder
4. Copy the Extension ID

### 4. Install Native Host
```bash
python install_host.py
```
Paste the Extension ID when asked.

### 5. Configure
1. Click extension icon → "⚙️ Settings"
2. Set download directory (e.g., `C:\Downloads\Videos`)
3. Click "SAVE SETTINGS"

## Usage

1. Go to any video page
2. Click extension icon
3. Click "FETCH FORMATS"
4. Select video/audio formats
5. Click "DOWNLOAD VIDEO"

Done! Video will be saved to your configured directory.

## Tips

- Use "best" for automatic quality selection
- Enable subtitles if needed
- For age-restricted videos, configure authentication in settings
