# Tab Saver Chrome Extension

Save tabs to a list and close them. Restore them anytime with Python server backup!

## Features

✅ **Right-click context menu** - Save & close tabs instantly
✅ **Beautiful popup UI** - View all saved tabs with titles and URLs
✅ **Badge counter** - Shows number of saved tabs on extension icon
✅ **One-click restore** - Click any tab to reopen it
✅ **Easy removal** - X button to remove tabs from list
✅ **Python server integration** - Auto-backup to local server
✅ **Manual save/load** - Buttons to sync with Python server

## Installation

### 1. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `tab_saver` folder
5. Extension is now installed!

### 2. Start Python Server (Optional)

For automatic backup:

```bash
python extension_manager.py
```

Server runs on `http://localhost:8765`

## Usage

### Save a Tab

1. Right-click anywhere on a webpage
2. Select **"Save & Close Tab"**
3. Tab is saved to list and closed immediately

### View Saved Tabs

1. Click the Tab Saver extension icon
2. See all your saved tabs
3. Click any tab title/URL to reopen it
4. Click ❌ to remove from list
5. Click "Clear All" to remove all tabs (shows visual feedback)

### Backup to Python Server

- **Auto-save**: Every change auto-saves to Python server
- **Manual save**: Click 💾 Save button (turns green ✓ on success)
- **Manual load**: Click 📥 Load button (turns green ✓ on success)
- **Clear all**: Click "Clear All" button (turns green ✓ when cleared)
- **Visual feedback**: All buttons show success/failure with color changes (no popups!)

## File Structure

```
tab_saver/
├── manifest.json       # Extension configuration
├── background.js       # Context menu & Python integration
├── popup.html          # Popup UI structure
├── popup.js            # Popup functionality
├── popup.css           # Popup styling
├── icons/              # Extension icons
└── README.md           # This file
```

## Data Storage

- **Chrome Storage**: `chrome.storage.local`
- **Python Backup**: `extension_data/tab_saver/saved_tabs.json`

## Troubleshooting

### Context menu not appearing
- Reload the extension in `chrome://extensions/`
- Right-click on the page content (not on images/links)

### Python server not saving
- Make sure `extension_manager.py` is running
- Check console for errors (F12 → Console)
- Verify server is on `http://localhost:8765`

### Tabs not loading
- Check if URLs are valid
- Some Chrome internal pages can't be opened

## Keyboard Shortcuts

You can add custom shortcuts in Chrome:
1. Go to `chrome://extensions/shortcuts`
2. Find "Tab Saver"
3. Set your preferred shortcut

## Privacy

- All data stored locally on your machine
- No external servers (except your local Python server)
- No tracking or analytics
- Open source code

## License

Free to use and modify!
