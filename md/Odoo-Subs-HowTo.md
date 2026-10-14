# How to Download Odoo Course Subtitles into a Text File

A step-by-step guide on how to scrape an Odoo eLearning course page, find each video on YouTube, download English subtitles (text only), and compile everything into a single `.txt` file.

---

## What You Need

| Tool | Purpose |
|------|---------|
| `yt-dlp` | Download YouTube subtitles |
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

### Install Python (if not already installed)

Download from https://www.python.org/downloads/ — version 3.8 or higher is fine.

---

## Step 1 — Get the Video List from the Odoo Course Page

Go to the course URL, e.g.:
```
https://www.odoo.com/slides/mrp-manufacturing-shop-floor-29
```

The page lists all lessons. For each lesson, note down:
- The **topic title** (e.g. `MRP Overview`)
- A **search query** you'll use to find it on YouTube (e.g. `MRP Overview Odoo tutorial`)

You don't need the Odoo slide URLs — you'll search YouTube directly by title.

> **Tip:** Add `Odoo tutorial` to the end of each search query. This helps yt-dlp find the right video and prefer the official Odoo channel.

---

## Step 2 — Understand How yt-dlp Finds YouTube Videos

`yt-dlp` has a built-in YouTube search feature using the `ytsearch` prefix:

```bash
yt-dlp "ytsearch5:MRP Overview Odoo tutorial" --print "%(id)s|||%(title)s|||%(channel)s" --no-playlist
```

- `ytsearch5:` — returns up to 5 results
- `--print "..."` — prints metadata without downloading anything
- The `|||` separator makes it easy to split the output in Python

To prefer the **official Odoo channel**, loop through results and check if `'odoo'` appears in the channel name.

---

## Step 3 — Download English Subtitles Only

Once you have a video ID (e.g. `XvAe_B29mB8`), download subtitles with:

```bash
# Manual subtitles first
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" \
  --write-sub --sub-lang en --skip-download --output "output_name"

# If no manual subs, fall back to auto-generated
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" \
  --write-auto-sub --sub-lang en --skip-download --output "output_name"
```

Key flags:
- `--write-sub` — download manually uploaded subtitles
- `--write-auto-sub` — download auto-generated captions
- `--sub-lang en` — English only
- `--skip-download` — don't download the video, just the subtitle file
- `--output` — where to save the file

This saves a `.vtt` file (WebVTT format).

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
import subprocess, os, re, glob, shutil, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DESKTOP = r"C:\Users\YOUR_USERNAME\Desktop"
OUTPUT_FILE = os.path.join(DESKTOP, "Output.txt")
TEMP_DIR = os.path.join(DESKTOP, "subtitle_temp")

# List of (search_query, display_title) pairs
VIDEOS = [
    ("MRP Overview Odoo tutorial", "MRP Overview"),
    ("Manufacturing Order Work Order Basics Odoo tutorial", "Manufacturing Order & Work Order Basics"),
    # ... add more entries here
]

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip(), result.stderr.strip()

def get_video_id(query):
    cmd = f'yt-dlp "ytsearch5:{query}" --print "%(id)s|||%(title)s|||%(channel)s" --no-playlist 2>NUL'
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
        cmd = (f'yt-dlp "https://www.youtube.com/watch?v={video_id}" '
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
    for i, (query, title) in enumerate(VIDEOS):
        print(f"[{i+1}/{len(VIDEOS)}] {title}")
        video_id, yt_title = get_video_id(query)
        if not video_id:
            print(f"  [SKIP] Not found")
            results.append((title, None, None))
            continue
        print(f"  [OK] https://youtu.be/{video_id} | {yt_title}")
        subtitle_text = download_subtitles(video_id, TEMP_DIR)
        print(f"  [OK] {len(subtitle_text)} chars" if subtitle_text else "  [--] No subtitles")
        results.append((title, video_id, subtitle_text))

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

---

## How to Use It for Any Other Odoo Course

1. Go to the course page on `odoo.com/slides/...`
2. Copy all the lesson titles from the page
3. Build a `VIDEOS` list — each entry is `("Title Odoo tutorial", "Title")`
4. Change `OUTPUT_FILE` to your desired output path
5. Run: `python fetch_odoo_subtitles.py`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Wrong video found | Make the search query more specific, e.g. add `"Odoo MRP"` |
| No subtitles | The video may not have auto-captions enabled; the script writes `[No subtitles available]` |
| Unicode error on Windows | Make sure `sys.stdout.reconfigure(encoding='utf-8')` is at the top of the script |
| yt-dlp JS runtime warning | Install Deno or Node.js — it still works without it but some formats may be missing |

---

## Notes

- Auto-generated captions are available on almost all YouTube videos
- Manual (human-written) subtitles are preferred when available — the script tries those first
- The `ytsearch` feature requires no API key — it works out of the box with yt-dlp
- The output file is saved as UTF-8 so it handles special characters correctly
