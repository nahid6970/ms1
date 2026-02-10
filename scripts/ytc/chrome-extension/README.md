# YTC Subtitle Extractor - Chrome Extension

A Chrome extension that extracts subtitles from any video site using yt-dlp. Based on the subtitle functionality from ytc_qt.py.

## Features

- Extract subtitles from any video URL (YouTube, Vimeo, etc.)
- Support for multiple languages (English, Bengali, Hindi, All)
- Multiple output formats (SRT, VTT, TXT)
- Auto-generated subtitle support
- Timeline range selection (extract specific time ranges)
- Configurable default settings
- Cookie-based authentication (browser or file)

## Installation

### Prerequisites

1. **Install yt-dlp**:
   ```bash
   pip install yt-dlp
   ```

2. **Ensure yt-dlp is in PATH**:
   ```bash
   yt-dlp --version
   ```

### Setup Steps

1. **Install the Native Messaging Host**:
   ```bash
   python install_host.py
   ```

2. **Load the Extension in Chrome**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `chrome-extension` folder

3. **Get the Extension ID**:
   - Copy the Extension ID from `chrome://extensions/`
   - It looks like: `abcdefghijklmnopqrstuvwxyz123456`

4. **Update the Manifest**:
   - Open `com.ytc.subtitle_extractor.json`
   - Replace `YOUR_EXTENSION_ID_HERE` with your actual Extension ID
   - Save the file

5. **Reload the Extension**:
   - Go back to `chrome://extensions/`
   - Click the reload icon on your extension

6. **Configure Settings**:
   - Click the extension icon
   - Click "⚙️ Settings"
   - Set your save directory (e.g., `C:\Downloads\Subtitles`)
   - Configure authentication if needed
   - Set default values
   - Click "SAVE SETTINGS"

## Usage

1. Navigate to any video page (YouTube, Vimeo, etc.)
2. Click the extension icon
3. The current URL will be auto-populated
4. Select your preferences:
   - Language (English, Bengali, Hindi, All)
   - Format (SRT, VTT, TXT)
   - Include auto-generated subtitles (optional)
   - Timeline range (optional)
5. Click "EXTRACT SUBTITLES"
6. Subtitles will be saved to your configured directory

## Settings

### Save Directory
The folder where subtitles will be saved. Must be a full path.

Example: `C:\Downloads\Subtitles`

### Authentication
For private or age-restricted videos:

- **None**: No authentication
- **Browser Cookies**: Use cookies from your browser (Chrome, Firefox, Edge, Opera, Brave)
- **Cookie File**: Use a Netscape format cookie file

### Default Values
Set default preferences for:
- Language
- Format
- Auto-generated subtitles

## Timeline Range

Extract subtitles for a specific time range:

- **Format**: Accepts seconds (`3062`) or time format (`51:02` or `1:30:45`)
- **Auto-detection**: If the URL contains `?t=3040`, it will auto-populate the start time

## Supported Sites

Any site supported by yt-dlp, including:
- YouTube
- Vimeo
- Dailymotion
- Facebook
- Twitter
- And 1000+ more sites

## Troubleshooting

### "Native host has exited" error
- Make sure `install_host.py` was run successfully
- Verify the Extension ID in `com.ytc.subtitle_extractor.json` matches your actual ID
- Check that `native_host.py` has the correct path in the manifest

### "yt-dlp not found" error
- Ensure yt-dlp is installed: `pip install yt-dlp`
- Verify it's in PATH: `yt-dlp --version`

### No subtitles downloaded
- Check if the video has subtitles available
- Try enabling "Include auto-generated" option
- Try different language options
- Check authentication settings for private videos

### Permission errors
- Ensure the save directory exists and is writable
- Run Chrome as administrator if needed

## File Structure

```
chrome-extension/
├── manifest.json              # Extension manifest
├── popup.html                 # Main popup UI
├── popup.js                   # Popup logic
├── popup.css                  # Popup styles
├── options.html               # Settings page UI
├── options.js                 # Settings logic
├── options.css                # Settings styles
├── background.js              # Background service worker
├── native_host.py             # Native messaging host
├── install_host.py            # Installation script
├── com.ytc.subtitle_extractor.json  # Native host manifest
└── README.md                  # This file
```

## Technical Details

### Native Messaging
The extension uses Chrome's Native Messaging API to communicate with a Python script that executes yt-dlp commands. This is necessary because Chrome extensions cannot directly execute system commands.

### Subtitle Processing
- Downloads subtitles using yt-dlp
- Converts to requested format (SRT, VTT, or TXT)
- For TXT format: removes timestamps, duplicates, and formatting
- Supports timeline filtering for specific time ranges

## Credits

Based on the subtitle extraction functionality from `ytc_qt.py`.

## License

Free to use and modify.
