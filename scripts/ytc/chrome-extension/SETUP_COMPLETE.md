# ✓ Setup Complete!

The native host has been successfully installed and configured.

## What's Been Done

✓ Native messaging host installed  
✓ Windows Registry configured  
✓ Batch wrapper created  
✓ Extension icons created  
✓ yt-dlp verified (version 2026.02.04)

## Next Steps (Do These Now)

### 1. Load Extension in Chrome

1. Open Chrome
2. Go to: `chrome://extensions/`
3. Enable "Developer mode" (toggle in top-right)
4. Click "Load unpacked"
5. Select this folder: `C:\@delta\ms1\scripts\ytc\chrome-extension`

### 2. Get Your Extension ID

After loading, you'll see an ID like: `abcdefghijklmnopqrstuvwxyz123456`

**Copy this ID!**

### 3. Update the Manifest

1. Open: `C:\@delta\ms1\scripts\ytc\chrome-extension\com.ytc.subtitle_extractor.json`
2. Find: `"chrome-extension://YOUR_EXTENSION_ID_HERE/"`
3. Replace `YOUR_EXTENSION_ID_HERE` with your actual Extension ID
4. Save the file

### 4. Reload Extension

1. Go back to `chrome://extensions/`
2. Click the reload icon on your extension

### 5. Configure Settings

1. Click the extension icon in Chrome toolbar
2. Click "⚙️ Settings"
3. Set **Save Directory** (example: `C:\Users\nahid\Downloads\Subtitles`)
4. Click "SAVE SETTINGS"

### 6. Test It!

1. Go to any YouTube video
2. Click the extension icon
3. Click "EXTRACT SUBTITLES"
4. Check your save directory!

---

## Features

- **Extract subtitles** from any video site (YouTube, Vimeo, etc.)
- **Multiple languages**: English, Bengali, Hindi, All
- **Multiple formats**: SRT, VTT, TXT (clean text)
- **Timeline range**: Extract specific time ranges
- **Auto-detection**: Detects `?t=` timestamps in URLs
- **Settings**: Configurable defaults and authentication

---

## Quick Reference

### Files Created

- `native_host.bat` - Windows wrapper script
- `native_host.py` - Python host script
- `com.ytc.subtitle_extractor.json` - Native messaging manifest
- `icons/` - Extension icons

### Registry Entry

`HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.ytc.subtitle_extractor`

### Test Installation

Run anytime to verify setup:
```bash
python test_host.py
```

---

## Troubleshooting

If you get "native host not found" error:

1. Make sure you updated the Extension ID in the manifest
2. Reload the extension after updating
3. Run `python test_host.py` to diagnose

---

## Support

- See `INSTALL.md` for detailed installation guide
- See `README.md` for full documentation
- See `QUICKSTART.md` for quick reference

Enjoy extracting subtitles! 🎬
