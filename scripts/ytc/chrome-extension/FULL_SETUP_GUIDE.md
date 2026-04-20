# YTC Subtitle Extractor — Full Setup Guide

## What This Project Does

A Chrome extension that extracts subtitles from YouTube (and other video sites) using `yt-dlp`, then optionally sends them to Google AI Studio for AI-powered summaries.

---

## Prerequisites — What to Install

### 1. Python (via Scoop or official installer)
- Download: https://www.python.org/downloads/
- Verify: `python --version`

### 2. yt-dlp — Install via pip ONLY
> ⚠️ Do NOT install yt-dlp via Scoop. The pip version supports plugins; the Scoop version does not.

```bash
pip install yt-dlp
```
Verify: `yt-dlp --version`

### 3. Node.js (via Scoop or official installer)
- Download: https://nodejs.org/ (v20+ recommended)
- Verify: `node --version`

### 4. bgutil POT Provider (fixes YouTube bot detection)

**Clone the server:**
```bash
git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git
cd bgutil-ytdlp-pot-provider/server
npm ci
npx tsc
```

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
        ├── build\main.js        ← compiled server (after npx tsc)
        ├── node_modules\
        └── package.json

%APPDATA%\yt-dlp\plugins\          ← NOT needed, ignore this folder
                                   (only used for manual/Scoop installs)

Chrome Extension folder (load unpacked from here):
<project>\chrome-extension\
├── manifest.json
├── background.js
├── popup.html / popup.js / popup.css
├── options.html / options.js / options.css
├── viewer.html / viewer.js
├── native_host.py               ← the native messaging host
├── native_host.bat
├── com.ytc.subtitle_extractor.json   ← update with your Extension ID
└── icons\

Native Messaging Host registry entry (set by install_host.py):
HKCU\Software\Google\Chrome\NativeMessagingHosts\com.ytc.subtitle_extractor
→ points to: com.ytc.subtitle_extractor.json
```

---

## Setup Steps

### Step 1 — Install the Native Messaging Host
```bash
cd chrome-extension
python install_host.py
```

### Step 2 — Load the Extension in Chrome
1. Go to `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `chrome-extension` folder
4. Copy the **Extension ID** shown (e.g. `abcdefghijklmnopqrstuvwxyz123456`)

### Step 3 — Update the Native Messaging Manifest
Open `com.ytc.subtitle_extractor.json` and replace `YOUR_EXTENSION_ID_HERE`:
```json
{
  "allowed_origins": ["chrome-extension://YOUR_EXTENSION_ID_HERE/"]
}
```
Save, then reload the extension in `chrome://extensions/`.

### Step 4 — Start the POT Server
```bash
cd C:\Users\<you>\bgutil-ytdlp-pot-provider\server
node build/main.js
```
Server starts on `http://127.0.0.1:4416`. Keep this running while using yt-dlp.

### Step 5 — Auto-start the Server on Login
1. Press `Win+R` → type `shell:startup` → Enter
2. Create `bgutil-server.bat`:
```bat
@echo off
cd /d C:\Users\<you>\bgutil-ytdlp-pot-provider\server
start /min node build/main.js
```

---

## Verify Everything Works

```bash
# Check yt-dlp sees the bgutil plugin
yt-dlp -v "https://www.youtube.com/watch?v=VIDEOID" 2>&1 | findstr /i "bgutil pot"
```

Expected output should include:
```
[pot] PO Token Providers: bgutil:http-1.3.1 (external), ...
```

---

## Common Errors & Fixes

### `n challenge solving failed` + `Only images available`
**Cause:** yt-dlp installed via Scoop (no plugin support) or Node.js not in PATH.  
**Fix:** Uninstall Scoop's yt-dlp, use `pip install yt-dlp` only.

### `Error reaching GET http://127.0.0.1:4416/ping`
**Cause:** bgutil POT server is not running.  
**Fix:** Start it with `node build/main.js` in the server folder, or set up the startup script above.

### `Native host has exited`
**Cause:** Wrong Extension ID in `com.ytc.subtitle_extractor.json`.  
**Fix:** Update the ID and reload the extension.

### `Could not copy Chrome cookie database`
**Cause:** Chrome locks its cookie DB while running.  
**Fix:** In extension Settings, switch Authentication to **Edge** or **Brave** browser cookies, or use a `cookies.txt` file exported via "Get cookies.txt LOCALLY" browser extension.

### `429 Too Many Requests`
**Cause:** yt-dlp making unauthenticated requests from a flagged IP.  
**Fix:** Set a cookie source in extension Settings (Edge/Brave/cookie file).

### `npm error ENOENT: package.json not found`
**Cause:** Running `npm install` from the repo root instead of the `server` subfolder.  
**Fix:** `cd bgutil-ytdlp-pot-provider/server` first, then `npm ci`.

---

## Keeping Things Updated

If downloads suddenly break, update in this order:

### 1. Update yt-dlp (do this first, most common fix)
```bash
pip install -U yt-dlp
```

### 2. Update bgutil plugin (if yt-dlp update alone didn't fix it)
```bash
pip install -U bgutil-ytdlp-pot-provider
```

### 3. Update bgutil server (only if plugin update requires it)
```bash
cd C:\Users\<you>\bgutil-ytdlp-pot-provider
git pull
cd server
npm ci
npx tsc
```
Then restart the server: `node build/main.js`

> POT tokens refresh automatically every 12 hours — no manual action needed.

---

## Why `npm ci` + `npx tsc` Instead of Just `npm install`?

The bgutil server is written in **TypeScript**, not plain JavaScript. Node.js can't run TypeScript directly, so it must be compiled first:

- `npm ci` — installs dependencies (stricter than `npm install`, uses exact locked versions)
- `npx tsc` — compiles TypeScript → JavaScript into the `build/` folder
- `node build/main.js` — runs the compiled output

The `build/` folder is not in the repo — you generate it locally with `tsc`.

---

## What NOT to Do

- ❌ Don't install yt-dlp via Scoop — plugins won't work
- ❌ Don't run `npm install` from the repo root — `package.json` is in `/server`
- ❌ Don't close the POT server terminal while using yt-dlp (or use the startup script)
- ❌ Don't have two versions of yt-dlp installed simultaneously (Scoop + pip conflict)

---

## Quick Reference

| Component | Install Method | Location |
|---|---|---|
| yt-dlp | `pip install yt-dlp` | Python Scripts in PATH |
| bgutil plugin | `pip install bgutil-ytdlp-pot-provider` | yt-dlp plugins (auto) |
| bgutil server | `git clone` + `npm ci` + `npx tsc` | `~/bgutil-ytdlp-pot-provider/server` |
| Chrome extension | Load unpacked | `chrome-extension/` folder |
| Native host | `python install_host.py` | Registry (auto) |
