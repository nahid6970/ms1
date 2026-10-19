# How to Download Odoo Course Subtitles into a Text File

A step-by-step guide on how to scrape an Odoo eLearning course page, find each video on YouTube, download English subtitles (text only), and compile everything into a single `.txt` file.

---

## What You Need

| Tool | Purpose |
|------|---------|
| `yt-dlp` | Download YouTube subtitles |
| `Node.js` | JavaScript runtime required by yt-dlp for YouTube extraction |
| `Python 3` | Run the script |
| Internet connection | Fetch pages and subtitles |

### Install yt-dlp (if not already installed)

```bash
# Using pip
pip install yt-dlp

# Or using scoop (Windows)
scoop install yt-dlp

# Or using winget
winget install yt-dlp
```

### Install Node.js (required by yt-dlp)

yt-dlp **requires** a JavaScript runtime to extract YouTube content. Without it, subtitle downloads will fail silently.

```bash
# Using winget
winget install OpenJS.NodeJS

# Or download from https://nodejs.org/
```

### Install Python (if not already installed)

Download from https://www.python.org/downloads/ — version 3.8 or higher is fine.

---

## Step 1 — Get the Video List from the Odoo Course Page

Go to the course URL, e.g.:
```
https://www.odoo.com/slides/subscription-20
```

The page lists all lessons. There are two approaches for finding the YouTube videos:

### Approach A — Use the Odoo YouTube Playlist (Recommended)

Most Odoo courses link to a YouTube playlist in the video description. Fetch the playlist URL and use yt-dlp to list all video IDs:

```bash
yt-dlp --js-runtimes node --extractor-args "youtube:player_client=android" \
  --flat-playlist --print "%(id)s|||%(title)s" \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

This gives you exact video IDs and titles — no search guessing involved.

### Approach B — Search YouTube by Title

You can also search YouTube directly by title:

> **Tip:** Add `Odoo tutorial` to the end of each search query. This helps yt-dlp find the right video and prefer the official Odoo channel.

---

## Step 2 — Understand How yt-dlp Finds YouTube Videos

`yt-dlp` has a built-in YouTube search feature using the `ytsearch` prefix:

```bash
yt-dlp --js-runtimes node --extractor-args "youtube:player_client=android" \
  "ytsearch5:MRP Overview Odoo tutorial" --print "%(id)s|||%(title)s|||%(channel)s" --no-playlist
```

- `ytsearch5:` — returns up to 5 results
- `--print "..."` — prints metadata without downloading anything
- The `|||` separator makes it easy to split the output in Python

To prefer the **official Odoo channel**, loop through results and check if `'odoo'` appears in the channel name.

> **Warning:** YouTube search can return wrong videos (e.g. "Subscription Products" may match "Subscription Basics"). If accuracy matters, use the playlist approach (Step 1, Approach A).

---

## Step 3 — Download English Subtitles Only

### Critical Flags for yt-dlp

Recent YouTube changes require two flags that are **mandatory**:

```bash
# Manual subtitles first
yt-dlp --js-runtimes node --extractor-args "youtube:player_client=android" \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --write-sub --sub-lang en --skip-download --output "output_name"

# If no manual subs, fall back to auto-generated
yt-dlp --js-runtimes node --extractor-args "youtube:player_client=android" \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --write-auto-sub --sub-lang en --skip-download --output "output_name"
```

Key flags:
- `--js-runtimes node` — **required**: provides the JavaScript runtime yt-dlp needs to extract YouTube content
- `--extractor-args "youtube:player_client=android"` — **required**: bypasses YouTube's HTTP 429 rate limiting and PO token requirements
- `--write-sub` — download manually uploaded subtitles
- `--write-auto-sub` — download auto-generated captions
- `--sub-lang en` — English only
- `--skip-download` — don't download the video, just the subtitle file
- `--output` — where to save the file

This saves a `.vtt` file (WebVTT format).

> **Why `--extractor-args "youtube:player_client=android"`?**
> YouTube's web client now requires PO tokens and frequently returns HTTP 429 (Too Many Requests). Using the Android player client bypasses these restrictions entirely. Without this flag, subtitle downloads will fail with 429 errors.

---

## Step 4 — Parse the VTT File (Remove Timestamps)

YouTube's auto-generated VTT files look like this:

```
WEBVTT
Kind: captions
Language: en

00:00:05.839 --> 00:00:08.790 align:start position:0%
 
What's<00:00:06.160><c> up,</c><00:00:06.480><c> Odoers</c>

00:00:08.790 --> 00:00:08.800 align:start position:0%
What's up, Odoers and welcome. In this
```

YouTube duplicates every line — one with inline timing tags (karaoke style) and one clean. The parsing strategy:

1. Skip lines starting with `WEBVTT`, `Kind:`, `Language:`, `NOTE`
2. Skip blank lines and lines that are just a number (cue index)
3. Skip lines matching the timestamp pattern `00:00:00.000 --> 00:00:00.000`
4. **Skip lines containing inline timing tags** like `<00:00:06.160>` — these are the duplicates
5. Strip any remaining HTML tags with regex: `re.sub(r'<[^>]+>', '', line)`
6. Deduplicate with a `seen` set
7. Join everything into one paragraph

```python
import re

def parse_youtube_vtt(content):
    lines = content.splitlines()
    seen = set()
    output = []

    for line in lines:
        line = line.strip()

        if (not line
                or line.startswith('WEBVTT')
                or line.startswith('Kind:')
                or line.startswith('Language:')
                or line.startswith('NOTE')
                or re.match(r'^\d+$', line)
                or re.match(r'[\d:\.]+\s+-->\s+[\d:\.]+', line)
                or line == ' '):
            continue

        # Skip karaoke-style duplicate lines
        if re.search(r'<\d{2}:\d{2}:\d{2}\.\d+>', line):
            continue

        clean = re.sub(r'<[^>]+>', '', line).strip()

        if clean and clean not in seen:
            seen.add(clean)
            output.append(clean)

    return ' '.join(output)
```

---

## Step 5 — Compile into a Text File

Write each entry in this format:

```
Topic Title
-----------
https://www.youtube.com/watch?v=VIDEO_ID

[full subtitle text as a paragraph]



Next Topic Title
...
```

- Title on line 1
- Dashes under it (same length as title)
- YouTube URL
- Blank line
- Subtitle text
- **3 blank lines** before the next entry

---

## The Full Python Script

Save this as `fetch_odoo_subtitles.py` and edit the `VIDEOS` list for any course.

```python
import subprocess, os, re, glob, shutil, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DESKTOP = r"C:\Users\YOUR_USERNAME\Desktop"
OUTPUT_FILE = os.path.join(DESKTOP, "Output.txt")
TEMP_DIR = os.path.join(DESKTOP, "subtitle_temp")

# Common yt-dlp flags that fix YouTube 429 rate-limiting and PO token issues
YT_DLP_BASE = 'yt-dlp --js-runtimes node --extractor-args "youtube:player_client=android"'

# (video_id, display_title) — get video IDs from the Odoo YouTube playlist
# using: yt-dlp --flat-playlist --print "%(id)s|||%(title)s" "PLAYLIST_URL"
VIDEOS = [
    ("y7vlKyx2p1o", "Subscription Basics"),
    ("8HT9FhG9I5Q", "Subscription Products"),
    ("Ir8foeWnSYI", "Renewing and Closing Subscriptions"),
    ("y4kwPEnpsPU", "Upsell Subscriptions"),
    ("Dtow9yZnKh0", "Subscription Reports"),
    ("R23ygFQrhmw", "Automation Rules"),
    ("ZabnNmxnU8M", "Self-Service Subscriptions"),
    ("OXLuF4a0vFY", "Scheduled actions in Subscriptions"),
    ("7vBU1eDC94Y", "Subscriptions MRR Reports"),
    ("G_AD4FqQY6w", "Subscriptions Behavioral Reports"),
    ("mVqSrelaGSk", "Subscriptions with Deliveries"),
]

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip(), result.stderr.strip()

def parse_youtube_vtt(content):
    lines = content.splitlines()
    seen, output = set(), []
    for line in lines:
        line = line.strip()
        if (not line or line.startswith('WEBVTT') or line.startswith('Kind:')
                or line.startswith('Language:') or line.startswith('NOTE')
                or re.match(r'^\d+$', line)
                or re.match(r'[\d:\.]+\s+-->\s+[\d:\.]+', line)
                or line == ' '):
            continue
        if re.search(r'<\d{2}:\d{2}:\d{2}\.\d+>', line):
            continue
        clean = re.sub(r'<[^>]+>', '', line).strip()
        if clean and clean not in seen:
            seen.add(clean)
            output.append(clean)
    return ' '.join(output)

def download_subtitles(video_id, out_dir):
    base = os.path.join(out_dir, video_id)
    for f in glob.glob(base + '*'):
        try: os.remove(f)
        except: pass
    for flag in ['--write-sub', '--write-auto-sub']:
        cmd = (f'{YT_DLP_BASE} "https://www.youtube.com/watch?v={video_id}" '
               f'{flag} --sub-lang en --skip-download --output "{base}" 2>NUL')
        run(cmd)
        files = glob.glob(base + '*.vtt') + glob.glob(base + '*.srt')
        if files:
            with open(files[0], 'r', encoding='utf-8', errors='replace') as f:
                return parse_youtube_vtt(f.read())
    return None

def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    results = []
    for i, (video_id, title) in enumerate(VIDEOS):
        print(f"[{i+1}/{len(VIDEOS)}] {title}")
        print(f"  [OK] https://youtu.be/{video_id}")
        subtitle_text = download_subtitles(video_id, TEMP_DIR)
        print(f"  [OK] {len(subtitle_text)} chars" if subtitle_text else "  [--] No subtitles")
        results.append((title, video_id, subtitle_text))
        if i < len(VIDEOS) - 1:
            time.sleep(2)  # avoid triggering 429 rate limits

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for idx, (title, video_id, subtitle_text) in enumerate(results):
            f.write(f"{title}\n{'-' * len(title)}\n")
            if video_id:
                f.write(f"https://www.youtube.com/watch?v={video_id}\n\n")
            f.write(subtitle_text + "\n" if subtitle_text else "[No subtitles available]\n")
            if idx < len(results) - 1:
                f.write("\n\n\n")

    print(f"\nSaved to: {OUTPUT_FILE}")
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
```

### Search-Based Variant (Less Reliable)

If you prefer to search YouTube by title instead of hardcoding video IDs, use this `get_video_id` function and change `VIDEOS` to `(search_query, display_title)` pairs:

```python
def get_video_id(query):
    cmd = f'{YT_DLP_BASE} "ytsearch5:{query}" --print "%(id)s|||%(title)s|||%(channel)s" --no-playlist 2>NUL'
    stdout, _ = run(cmd)
    if not stdout:
        return None, None
    lines = [l.strip() for l in stdout.splitlines() if '|||' in l]
    for line in lines:
        parts = line.split('|||')
        if len(parts) >= 3 and 'odoo' in parts[2].lower():
            return parts[0], parts[1]
    if lines:
        parts = lines[0].split('|||')
        return (parts[0], parts[1]) if len(parts) >= 2 else (None, None)
    return None, None
```

Then in `main()`, call `get_video_id(query)` before `download_subtitles()`.

> **Warning:** Search-based matching can return wrong videos. For example, searching "Subscription Products Odoo tutorial" may return the "Subscription Basics" video instead. If accuracy is critical, use hardcoded video IDs from the playlist method.

---

## How to Use It for Any Other Odoo Course

1. Go to the course page on `odoo.com/slides/...`
2. Open any lesson — the video description usually links to a YouTube playlist
3. List the playlist with:
   ```bash
   yt-dlp --js-runtimes node --extractor-args "youtube:player_client=android" \
     --flat-playlist --print "%(id)s|||%(title)s" "PLAYLIST_URL"
   ```
4. Build a `VIDEOS` list using the exact video IDs and titles from the playlist
5. Change `OUTPUT_FILE` to your desired output path
6. Run: `python fetch_odoo_subtitles.py`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **HTTP 429: Too Many Requests** | Add `--extractor-args "youtube:player_client=android"` — this bypasses YouTube's rate limiting |
| **No supported JavaScript runtime** | Install Node.js and add `--js-runtimes node` — yt-dlp now requires a JS runtime for YouTube |
| **PO Token / Visitor Data warning** | Use `--extractor-args "youtube:player_client=android"` to bypass PO token requirements |
| **Wrong video found (search mode)** | Use hardcoded video IDs from the Odoo YouTube playlist instead of search |
| **No subtitles** | The video may not have auto-captions enabled; the script writes `[No subtitles available]` |
| **Unicode error on Windows** | Make sure `sys.stdout.reconfigure(encoding='utf-8')` is at the top of the script |
| **Rate limiting after several videos** | The script includes `time.sleep(2)` between videos; increase if needed |
| **Cookie / login required error** | The Android player client bypasses this; if it persists, try `--cookies-from-browser firefox` |

---

## Notes

- Auto-generated captions are available on almost all YouTube videos
- Manual (human-written) subtitles are preferred when available — the script tries those first
- The `ytsearch` feature requires no API key — it works out of the box with yt-dlp
- The output file is saved as UTF-8 so it handles special characters correctly
- The `--extractor-args "youtube:player_client=android"` flag is the single most important fix — without it, YouTube returns 429 errors and subtitle downloads fail silently
- Node.js is required as of 2026 — yt-dlp no longer works with YouTube without a JS runtime
