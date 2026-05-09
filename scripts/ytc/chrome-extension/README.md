# YTC Subtitle Interceptor

A lightweight Chrome extension that intercepts YouTube subtitles directly from the network traffic and sends them to Google AI Studio with custom prompts.

## Features

- **High Reliability:** Intercepts subtitle data (VTT, XML, JSON3) directly from YouTube's player requests.
- **Auto-Cleaning:** Automatically strips timestamps and formatting to provide clean text.
- **AI Studio Integration:** Seamlessly injects captured subtitles as a file and applies your selected prompt in Google AI Studio.
- **Prompt Management:** Maintain a list of custom prompts for different AI tasks.

## How It Works

This extension uses a **Network Interceptor** approach:
1. When you open a YouTube video, a script is injected into the page context.
2. This script overrides the global `fetch` and `XMLHttpRequest` objects.
3. When YouTube requests subtitle data (via the `timedtext` API), the extension captures a copy of the response.
4. The captured data is cleaned and stored in the extension's local storage.
5. The popup allows you to review, copy, or send this data to AI Studio.

## Usage Instructions

### 1. Capturing Subtitles
1. Open any YouTube video.
2. **Turn on Captions (CC)** in the YouTube player settings.
3. The extension will automatically "catch" the subtitles as they load.
4. Open the extension popup to see the captured text.

### 2. Sending to AI Studio
1. In the popup, select your desired **AI Studio Prompt** from the dropdown.
2. Click **"Send to AI Studio"**.
3. A new Google AI Studio tab will open, and the extension will automatically:
   - Insert your prompt text into the chat box.
   - Upload the cleaned subtitles as a `subtitles.txt` file.

### 3. Managing Prompts
1. Click **"Settings & Prompts"** at the bottom of the popup.
2. Add, edit, or remove prompts that you want to use for subtitle analysis.

## Development Note

This extension is built with **Manifest V3** and uses `chrome.scripting` for secure injection into page contexts. It requires host permissions for YouTube (to intercept) and Google AI Studio (to inject).
