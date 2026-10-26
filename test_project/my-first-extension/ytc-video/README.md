# YTC Video Downloader — Chrome/Firefox Extension

Download videos from YouTube, Facebook (including private groups), and any other
site supported by yt-dlp — directly from your browser.

## Features

- Download videos in any quality/format
- Download YouTube playlists with selectable maximum resolution and optional playlist-order filename prefixes
- Separate video + audio format selection
- Combined [A+V] format support (common on Facebook)
- Optional subtitle download
- Age-restricted video support via browser cookies or cookie file
- Private Facebook group video support (cookies + browser impersonation)
- Works in Chrome and Firefox

## Requirements

- Python 3.8+
- yt-dlp with curl_cffi (required for private Facebook content):
  ```bash
  pip install -U "yt-dlp[default,curl-cffi]"
  ```
- Pillow (icon generation only):
  ```bash
  pip install pillow
  ```

> **Note:** The stable yt-dlp release has a broken Facebook extractor (known bug).
> Use the **nightly build** for reliable Facebook support.

Verify impersonation is ready — Chrome entries should **not** say `(not available)`:
```bash
yt-dlp --list-impersonate-targets
```

## Installation

### 1. Install dependencies

```bash
pip install -U "yt-dlp[default,curl-cffi]" pillow
```

> **Important:** Install the **nightly build** of yt-dlp — the stable release has a
> broken Facebook extractor. The nightly is installed automatically by the command above
> if you previously ran `yt-dlp -U` to switch to nightly. To explicitly install nightly:
> ```bash
> pip install -U "yt-dlp[default,curl-cffi] @ https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt-dlp.tar.gz"
> ```

### 2. Generate icons

```bash
python create_icons.py
```

### 3. Load the extension

**Chrome:**
1. Go to `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select this folder
4. Copy the **Extension ID**

**Firefox:**
1. Go to `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on...** → select `manifest.json`
3. Copy the **Extension ID** shown in the listing

> Firefox temporary add-ons are removed when Firefox closes. Reload via
> `about:debugging` each session, or use Firefox Developer Edition with
> `xpinstall.signatures.required = false` in `about:config` for persistence.

### 4. Register the native messaging host

```bash
python install_host.py
```

Select Chrome or Firefox when prompted, paste the Extension ID.

### 5. Configure settings

1. Click the extension icon → **⚙️ Settings**
2. Set your **save directory**
3. (Optional / required for Facebook) set **Authentication** — see below
4. Click **SAVE SETTINGS**

## Usage

1. Navigate to any video page (YouTube, Facebook group, etc.)
2. Click the extension icon
3. Click **FETCH FORMATS**
4. Select video and audio formats
5. (Optional) enable subtitle download
6. Click **DOWNLOAD VIDEO**

## Authentication

### Cookie File *(recommended for Facebook)*

1. Log into Facebook in your browser
2. Install the "Get cookies.txt LOCALLY" extension
3. Export `cookies.txt` from the Facebook tab
4. In Settings → Authentication → **Cookie File** → paste the path

### Browser Cookies

- **Prefer Firefox** — log into Facebook in Firefox first, then select
  Browser Cookies → Firefox in Settings
- Chrome often fails because Chrome encrypts its cookie store since ~2024

## Facebook private group videos

Private group videos need two things:

1. **curl_cffi installed** (for `--impersonate chrome-99`):
   ```bash
   pip install -U "yt-dlp[default,curl-cffi]"
   ```
2. **Valid cookies** (Cookie File or Firefox browser cookies)

The native host automatically adds `--impersonate chrome-99` when curl_cffi
is detected. Manual test command:

```bash
yt-dlp --cookies "C:\path\to\cookies.txt" --impersonate chrome-99 -F "FACEBOOK_VIDEO_URL"
```

If that lists formats, the extension will work the same way.

## Re-setup on a new PC

```bash
# 1. Dependencies (nightly + curl_cffi for Facebook private groups)
pip install -U "yt-dlp[default,curl-cffi] @ https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt-dlp.tar.gz"
pip install pillow

# 2. Verify — nightly version looks like 2026.10.10.233141, NOT 2026.08.19
yt-dlp --version
yt-dlp --list-impersonate-targets  # Chrome must NOT say "(not available)"

# 3. Icons + host
python create_icons.py
# Load unpacked in Chrome (or Load Temporary Add-on in Firefox), copy Extension ID
python install_host.py

# 4. In extension Settings:
#    - set save directory
#    - set Cookie File or Firefox cookies for Facebook
```

## Troubleshooting

| Problem | Fix |
|---|---|
| Native host has exited | Run `python install_host.py` again |
| Cannot parse data (Facebook) | 1) `pip install -U "yt-dlp[default,curl-cffi]"` 2) Fresh `cookies.txt` or Firefox cookies 3) `yt-dlp -U` |
| Impersonate target not available | `pip install -U "yt-dlp[default,curl-cffi]"` |
| Chrome browser cookies fail | Use Cookie File or switch to Firefox |
| Cookie file rejected | Must be Netscape format — first line: `# Netscape HTTP Cookie File` |
| Download fails in general | `yt-dlp -U` then retry |
| Firefox extension disappears | Reload via `about:debugging` (temporary add-on limitation) |

## Based On

Based on the `ytc_subs.py` script, following the same architecture as the
YTC Subtitle Extractor extension.
