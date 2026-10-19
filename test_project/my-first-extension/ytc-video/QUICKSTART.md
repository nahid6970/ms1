# YTC Video Downloader — Quick Start

## 1. Install Python dependencies

```bash
pip install -U "yt-dlp[default,curl-cffi]" pillow
```

> **Important:** The **stable** yt-dlp release has a broken Facebook extractor.
> You need the **nightly build**. To install it explicitly:
> ```bash
> pip install -U "yt-dlp[default,curl-cffi] @ https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt-dlp.tar.gz"
> ```
> If you previously ran `yt-dlp -U`, you're likely already on nightly.
> Check with `yt-dlp --version` — nightly versions look like `2026.10.10.233141`.

> `curl-cffi` is required for private Facebook group videos (browser impersonation).

Verify impersonation is available — Chrome entries should **not** say `(not available)`:

```bash
yt-dlp --list-impersonate-targets
```

## 2. Generate icons

```bash
python create_icons.py
```

## 3. Load the extension in your browser

**Chrome:**
1. Go to `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select this folder
4. Copy the **Extension ID**

**Firefox:**
1. Go to `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on...** → select `manifest.json`
3. Copy the **Extension ID** shown in the listing

## 4. Register the native messaging host

```bash
python install_host.py
```

Choose Chrome or Firefox when prompted, then paste the Extension ID.

## 5. Configure settings

1. Click the extension icon → **⚙️ Settings**
2. Set your **save directory** (e.g. `C:\Downloads\Videos`)
3. For Facebook page/group videos, set **Authentication**:
   - **Cookie File** *(recommended)*: log into Facebook in your browser, export
     `cookies.txt` with the "Get cookies.txt LOCALLY" extension, then paste the path
   - **Browser Cookies → Firefox**: log into Facebook in Firefox first
     *(Chrome cookies often fail due to app-bound encryption)*
4. Click **SAVE SETTINGS**

## Usage

1. Go to any video page (YouTube, Facebook, etc.)
2. Click the extension icon
3. Click **FETCH FORMATS**
4. Select video/audio formats (`best` = auto)
5. Click **DOWNLOAD VIDEO**

---

## Re-setup checklist (new PC)

```bash
# 1. Install nightly yt-dlp + curl_cffi (both required for Facebook private groups)
pip install -U "yt-dlp[default,curl-cffi] @ https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt-dlp.tar.gz"
pip install pillow

# 2. Verify — nightly version looks like 2026.10.10.233141, NOT 2026.08.19
yt-dlp --version
# Chrome targets must NOT say "(not available)"
yt-dlp --list-impersonate-targets

# 3. Generate icons
python create_icons.py

# 4. Load extension in browser, copy Extension ID, then:
python install_host.py

# 5. In extension Settings:
#    - set save directory
#    - set Cookie File or Firefox cookies for Facebook
```

## Keeping it working

- Re-export `cookies.txt` if Facebook downloads suddenly fail (cookies expire)
- Keep yt-dlp updated: `yt-dlp -U`
- If Chrome cookie reading fails, switch to Cookie File or Firefox
