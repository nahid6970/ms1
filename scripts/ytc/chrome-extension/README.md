# YTC Subtitle Extractor — Chrome Extension

A Chrome extension that extracts subtitles from any video site using `yt-dlp`, with optional AI-powered summaries via Google AI Studio.

---

## Features

- Extract subtitles from any video URL (YouTube, Vimeo, etc.)
- Multiple languages: English, Bengali, Hindi, All
- Multiple formats: SRT, VTT, TXT
- Auto-generated subtitle support
- Timeline range selection
- Google AI Studio integration — auto-injects subtitles + custom prompt
- Cookie authentication support (Edge, Brave, cookie file)

---

## What to Install

### 1. Python
Download: https://www.python.org/downloads/  
Verify: `python --version`

### 2. yt-dlp — pip ONLY
> ⚠️ Do NOT install via Scoop. The Scoop version is a standalone exe with no plugin support. The pip version is required for bgutil to work.

```bash
pip install yt-dlp
```

### 3. Node.js (v20+)
Download: https://nodejs.org/  
Verify: `node --version`

### 4. bgutil POT Provider (fixes YouTube bot detection)

**Why it's needed:** YouTube requires a cryptographic Proof of Origin Token (POT) to serve video formats to automated tools. bgutil generates this token by running YouTube's own BotGuard JavaScript challenge via Node.js and serves it to yt-dlp over HTTP on port 4416. Without it, yt-dlp gets blocked and only sees image formats.

**Clone and build the server:**
```bash
git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git
cd bgutil-ytdlp-pot-provider/server
npm ci
npx tsc
```

> The server is written in TypeScript. `npm ci` installs dependencies, `npx tsc` compiles TypeScript → JavaScript into `build/`. Node.js can't run TypeScript directly, so this step is required.

**Install the yt-dlp plugin:**
```bash
pip install bgutil-ytdlp-pot-provider
```

---

## File Placement

```
C:\Users\<you>\
└── bgutil-ytdlp-pot-provider\
    └── server\
        ├── build\main.js        ← generated after npx tsc
        ├── node_modules\
        └── package.json

Chrome Extension (load unpacked from here):
<project>\chrome-extension\
├── manifest.json
├── background.js
├── popup.html / popup.js / popup.css
├── options.html / options.js / options.css
├── viewer.html / viewer.js
├── native_host.py               ← native messaging host
├── native_host.bat
├── com.ytc.subtitle_extractor.json   ← update with your Extension ID
└── icons\

Registry (set automatically by install_host.py):
HKCU\Software\Google\Chrome\NativeMessagingHosts\com.ytc.subtitle_extractor
```

> `%APPDATA%\yt-dlp\plugins\` — ignore this folder, not needed when using pip install.

---

## Setup Steps

### 1. Install the Native Messaging Host
```bash
cd chrome-extension
python install_host.py
```

### 2. Load the Extension in Chrome
1. Go to `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `chrome-extension` folder
4. Copy the **Extension ID** (e.g. `abcdefghijklmnopqrstuvwxyz123456`)

### 3. Update the Native Messaging Manifest
Open `com.ytc.subtitle_extractor.json`, replace `YOUR_EXTENSION_ID_HERE`:
```json
{
  "allowed_origins": ["chrome-extension://YOUR_EXTENSION_ID_HERE/"]
}
```
Save, then reload the extension in `chrome://extensions/`.

### 4. Start the POT Server
```bash
cd C:\Users\<you>\bgutil-ytdlp-pot-provider\server
node build/main.js
```
Server runs on `http://127.0.0.1:4416`. Must be running when using yt-dlp.

> POT tokens are cached for 12 hours, so yt-dlp works briefly after stopping the server. Once cache expires it will fail again.

### 5. Auto-start Server on Login
1. Press `Win+R` → type `shell:startup` → Enter
2. Copy `start_bgutil_server.bat` into that folder (included in this project)

---

## Usage

1. Click the extension icon → **⚙️ Settings**
2. Set **Save Directory** and optional **Custom Prompt**
3. Click **SAVE SETTINGS**
4. Navigate to a video, select format, click **EXTRACT SUBTITLES**
5. Check **SEND TO GOOGLE AI STUDIO** for automatic AI analysis

---

## Verify bgutil is Working

```bash
yt-dlp -v "https://www.youtube.com/watch?v=VIDEOID" 2>&1 | findstr /i "bgutil pot"
```

Expected:
```
[pot] PO Token Providers: bgutil:http-1.3.1 (external), ...
```

---

## Keeping Things Updated

When downloads break, update in this order:

```bash
# 1. Update yt-dlp (fixes most issues)
pip install -U yt-dlp

# 2. Update bgutil plugin
pip install -U bgutil-ytdlp-pot-provider

# 3. Update bgutil server (only if needed)
cd C:\Users\<you>\bgutil-ytdlp-pot-provider
git pull
cd server && npm ci && npx tsc
# then restart: node build/main.js
```

---

## Common Errors & Fixes

### `n challenge solving failed` / `Only images available`
**Cause:** yt-dlp installed via Scoop (no plugin support).  
**Fix:** Uninstall Scoop's yt-dlp, use `pip install yt-dlp` only. Don't have both installed.

### `Error reaching GET http://127.0.0.1:4416/ping`
**Cause:** bgutil server not running.  
**Fix:** Run `node build/main.js` in the server folder, or set up the startup script.

### `Native host has exited`
**Cause:** Wrong Extension ID in `com.ytc.subtitle_extractor.json`.  
**Fix:** Update the ID and reload the extension.

### `Could not copy Chrome cookie database`
**Cause:** Chrome locks its cookie DB while running.  
**Fix:** In Settings, switch Authentication to **Edge** or **Brave**, or use a `cookies.txt` file (export via "Get cookies.txt LOCALLY" extension).

### `429 Too Many Requests`
**Cause:** Unauthenticated requests from a flagged IP.  
**Fix:** Set a cookie source in Settings (Edge/Brave/cookie file).

### `npm error ENOENT: package.json not found`
**Cause:** Running `npm install` from repo root instead of the `server` subfolder.  
**Fix:** `cd bgutil-ytdlp-pot-provider/server` first, then `npm ci`.

---

## What NOT to Do

- ❌ Don't install yt-dlp via Scoop — plugins won't work
- ❌ Don't have two yt-dlp installs (Scoop + pip) — they conflict
- ❌ Don't run `npm ci` from the repo root — `package.json` is in `/server`
- ❌ Don't close the POT server terminal without the startup script set up

---

## Quick Reference

| Component | Install | Notes |
|---|---|---|
| yt-dlp | `pip install yt-dlp` | pip only, not Scoop |
| bgutil plugin | `pip install bgutil-ytdlp-pot-provider` | auto-detected by yt-dlp |
| bgutil server | `git clone` → `npm ci` → `npx tsc` | must run before yt-dlp |
| Chrome extension | Load unpacked in `chrome://extensions/` | |
| Native host | `python install_host.py` | writes to registry |
