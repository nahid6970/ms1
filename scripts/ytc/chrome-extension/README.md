# YTC Subtitle Extractor - Chrome Extension

A Chrome extension that extracts subtitles from any video site using yt-dlp and automates AI-driven summaries via Google AI Studio.

## New Features (v1.1.0)

- **Google AI Studio Integration:** Automatically open [Google AI Studio](https://aistudio.google.com/prompts/new_chat) and inject extracted subtitles along with a custom prompt.
- **Automated Text Injection:** No more manual copy-pasting; the extension handles the input for you.
- **Enhanced Cookie Management:** Support for Edge, Brave, and manual `cookies.txt` files to bypass Chrome's database locking issues.
- **Flexible UI:** Toggle the subtitle viewer window on or off based on your preference.
- **JS Runtime Support:** Verification for Node.js/Deno runtimes required by modern YouTube player logic.

## Core Features

- Extract subtitles from any video URL (YouTube, Vimeo, etc.)
- Support for multiple languages (English, Bengali, Hindi, All)
- Multiple output formats (SRT, VTT, TXT)
- Auto-generated subtitle support
- Timeline range selection (extract specific time ranges)
- Configurable custom prompts for AI analysis

## Installation

### Prerequisites

1. **Install yt-dlp**:
   ```bash
   pip install yt-dlp
   ```

2. **Install a JavaScript Runtime (Recommended)**:
   Install [Node.js](https://nodejs.org/) and ensure it's in your system PATH. Modern YouTube extraction often requires a JS runtime.

3. **Ensure yt-dlp is in PATH**:
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
   - Copy the Extension ID from `chrome://extensions/` (e.g., `abcdefghijklmnopqrstuvwxyz123456`)

4. **Update the Manifest**:
   - Open `com.ytc.subtitle_extractor.json`
   - Replace `YOUR_EXTENSION_ID_HERE` with your actual Extension ID
   - Save the file

5. **Reload the Extension**:
   - Go back to `chrome://extensions/` and click the reload icon on your extension.

## Usage

1. **Configure Settings**:
   - Click the extension icon -> "⚙️ Settings"
   - Set your **Save Directory**.
   - Enter your **Default Custom Prompt** (e.g., "Summarize this video in bullet points:").
   - Click "SAVE SETTINGS".

2. **Extraction**:
   - Navigate to a video page.
   - Select your format (SRT, VTT, or TXT).
   - Check **"SEND TO GOOGLE AI STUDIO"** if you want automatic AI analysis.
   - Click **"EXTRACT SUBTITLES"**.

## Google AI Studio Integration

When enabled, the extension will:
1. Extract the subtitles using `yt-dlp`.
2. Combine the subtitles with your saved **Custom Prompt**.
3. Open a new chat tab at Google AI Studio.
4. **Automatically inject** the text into the chat box so you can start processing immediately.

## Authentication & Errors

### "Could not copy Chrome cookie database"
Chrome locks its database while running. If you see this error:
1. Go to **Settings**.
2. Change **Authentication** to **Browser Cookies** and select **Edge** (or Brave/Firefox).
3. Ensure you have logged into YouTube at least once in that other browser.
4. Alternatively, use a **Cookie File** exported via a browser extension (like "Get cookies.txt LOCALLY").

## Troubleshooting

- **Native host has exited:** Verify the Extension ID in `com.ytc.subtitle_extractor.json`.
- **429 Too Many Requests:** Ensure you are using a Cookie source (Edge, File, etc.) to authenticate as a logged-in user.
- **JS Runtime Warning:** Install Node.js or Deno and restart your terminal/browser.

## Credits

Based on the subtitle extraction functionality from `ytc_qt.py`. Updated with modern AI integration and improved authentication handling.

## License

Free to use and modify.
