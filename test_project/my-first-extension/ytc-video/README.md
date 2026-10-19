# YTC Video Downloader - Chrome Extension

Chrome extension for downloading videos from YouTube, Facebook, and other sites using yt-dlp.

## Features

- Download videos in any quality/format
- Separate video and audio format selection
- Combined [A+V] format support (common on Facebook)
- Optional subtitle download
- Support for age-restricted videos (browser cookies or cookie file)
- Facebook page video support (with authentication)
- Works on any video site supported by yt-dlp

## Requirements

- Python 3.6+
- yt-dlp (`pip install yt-dlp`)
- Pillow (for icon generation): `pip install pillow`

## Installation

### 1. Generate Icons

```bash
cd chrome-extension-video
python create_icons.py
```

### 2. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `chrome-extension-video` folder
5. Copy the Extension ID

### 3. Install Native Messaging Host

```bash
python install_host.py
```

Enter the Extension ID when prompted.

### 4. Configure Settings

1. Click the extension icon
2. Click "⚙️ Settings"
3. Set your download directory
4. (Optional) Configure authentication for age-restricted or Facebook videos
5. Click "SAVE SETTINGS"

## Usage

1. Navigate to any video page (YouTube, Facebook, etc.)
2. Click the extension icon
3. Click "FETCH FORMATS" to load available formats
4. Select desired video and audio formats
5. (Optional) Enable subtitle download
6. Click "DOWNLOAD VIDEO"

## Authentication

Two methods:

1. **Browser Cookies**: Use cookies from your logged-in browser
2. **Cookie File**: Export cookies using "Get cookies.txt LOCALLY" extension

### Facebook Page Videos

Many Facebook page videos (e.g. `https://www.facebook.com/<page>/videos/<id>/`)
are not publicly accessible and **require authentication**:

- **Browser Cookies** — log in to Facebook in your browser, then select
  "Browser Cookies → Chrome" in Settings. This is the easiest option.
- **Cookie File** — export a `cookies.txt` from your logged-in Facebook
  session using the "Get cookies.txt LOCALLY" extension, then point to it
  in Settings.

The popup will show a "FACEBOOK VIDEO DETECTED" hint when you're on a
Facebook video page to remind you to configure authentication.

## Troubleshooting

- **"Native host has exited"**: Run `install_host.py` again
- **No formats available**: Check if yt-dlp is installed and updated
- **Download fails**: Try updating yt-dlp: `yt-dlp -U`
- **Facebook video returns no formats or fails**: Enable Browser Cookies or
  Cookie File authentication in Settings

## Based On

This extension is based on the `ytc_subs.py` script and follows the same architecture as the YTC Subtitle Extractor extension.
