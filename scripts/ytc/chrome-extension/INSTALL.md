# Installation Guide - Step by Step

Follow these steps exactly to install the YTC Subtitle Extractor.

## Step 1: Install yt-dlp

Open Command Prompt and run:

```bash
pip install yt-dlp
```

Verify installation:

```bash
yt-dlp --version
```

You should see a version number. If not, yt-dlp is not in your PATH.

## Step 2: Create Icons

Navigate to the chrome-extension folder and run:

```bash
cd chrome-extension
pip install pillow
python create_icons.py
```

## Step 3: Install Native Host

Still in the chrome-extension folder, run:

```bash
python install_host.py
```

This will:
- Create `native_host.bat` (wrapper script)
- Create `com.ytc.subtitle_extractor.json` (manifest)
- Register with Windows Registry

## Step 4: Test Installation

Run the test script:

```bash
python test_host.py
```

This will verify everything is set up correctly. Fix any errors it reports.

## Step 5: Load Extension in Chrome

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (toggle switch in top-right corner)
4. Click "Load unpacked" button
5. Browse to and select the `chrome-extension` folder
6. The extension should now appear in your extensions list

## Step 6: Get Extension ID

1. Look at your extension in `chrome://extensions/`
2. Find the "ID" field under the extension name
3. Copy the entire ID (it's a long string like `abcdefghijklmnopqrstuvwxyz123456`)

## Step 7: Update Manifest with Extension ID

1. Open `com.ytc.subtitle_extractor.json` in a text editor
2. Find this line:
   ```json
   "chrome-extension://YOUR_EXTENSION_ID_HERE/"
   ```
3. Replace `YOUR_EXTENSION_ID_HERE` with your actual Extension ID
4. Save the file

Example:
```json
"allowed_origins": [
  "chrome-extension://abcdefghijklmnopqrstuvwxyz123456/"
]
```

## Step 8: Reload Extension

1. Go back to `chrome://extensions/`
2. Find your extension
3. Click the reload icon (circular arrow)

## Step 9: Configure Extension

1. Click the extension icon in Chrome toolbar (top-right)
2. Click "⚙️ Settings" at the bottom of the popup
3. Enter a **Save Directory** (full path):
   - Example: `C:\Users\YourName\Downloads\Subtitles`
   - The folder will be created if it doesn't exist
4. (Optional) Configure authentication for private videos
5. (Optional) Set default language and format
6. Click "SAVE SETTINGS"

## Step 10: Test It!

1. Go to a YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
2. Click the extension icon
3. The URL should be auto-filled
4. Click "EXTRACT SUBTITLES"
5. Check your save directory for the subtitle file!

---

## Troubleshooting

### "Specified native messaging host not found"

This means Chrome can't find the native host. Run through these checks:

1. **Run test script:**
   ```bash
   python test_host.py
   ```

2. **Check registry manually:**
   - Press Win+R
   - Type `regedit` and press Enter
   - Navigate to: `HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.ytc.subtitle_extractor`
   - Check if the path points to your `com.ytc.subtitle_extractor.json` file

3. **Verify Extension ID:**
   - Make sure you replaced `YOUR_EXTENSION_ID_HERE` in the manifest
   - Make sure the ID matches exactly (including the trailing `/`)

4. **Reinstall:**
   ```bash
   python install_host.py
   ```

### "yt-dlp not found"

```bash
pip install yt-dlp
```

Make sure Python's Scripts folder is in your PATH.

### "Set save directory in settings first"

1. Click extension icon
2. Click "⚙️ Settings"
3. Enter full path in "Save Directory"
4. Click "SAVE SETTINGS"

### Extension icon doesn't appear

1. Go to `chrome://extensions/`
2. Make sure the extension is enabled
3. Pin it to toolbar: Click the puzzle icon → Find your extension → Click the pin icon

### No subtitles downloaded

- Check if video has subtitles (try on YouTube with CC button)
- Enable "Include auto-generated" option
- Try "All" languages
- Check the save directory path is correct

---

## Uninstall

To remove the extension:

1. Go to `chrome://extensions/`
2. Click "Remove" on the extension

To remove the native host:

1. Delete the registry key:
   - Open Registry Editor (Win+R → `regedit`)
   - Navigate to: `HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts`
   - Delete the `com.ytc.subtitle_extractor` key

2. Delete the files:
   - Delete the `chrome-extension` folder

---

## Need Help?

Run the test script to diagnose issues:

```bash
python test_host.py
```

It will tell you exactly what's wrong and how to fix it.
