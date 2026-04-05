# Tab Saver Chrome Extension

Save tabs to a list and close them. Restore them anytime with Convex cloud backup!

## Features

✅ **Right-click context menu** - Save & close tabs instantly
✅ **Beautiful popup UI** - View all saved tabs with titles and URLs
✅ **Badge counter** - Shows number of saved tabs on extension icon
✅ **One-click restore** - Click any tab to reopen it
✅ **Easy removal** - X button to remove tabs from list
✅ **Convex integration** - Auto-backup to Convex cloud
✅ **Manual save/load** - Buttons to sync with Convex
✅ **YouTube channel icons** - Shows both YouTube favicon and channel avatar for videos
✅ **Customizable icon sizes** - Adjust YouTube and channel icon sizes via settings

## Installation

### 1. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `tab_saver` folder
5. Extension is now installed!

### 2. Configure Convex

See the [Convex Integration Guide](../CONVEX_INTEGRATION_GUIDE.md) for setup instructions.

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

### Customize Icon Sizes

1. Click the ⚙️ settings button (top right of popup)
2. Adjust YouTube icon size (16-32px)
3. Adjust channel icon size (12-24px)
4. Changes apply instantly
5. Click "Reset to Default" to restore original sizes

### YouTube Videos

When saving YouTube videos:
- YouTube favicon appears as the main icon
- Channel avatar appears as a smaller overlay icon
- Both icons are customizable in settings

### Backup to Convex

- **Auto-save**: Every change auto-saves to Convex
- **Manual save**: Click 💾 Save button (turns green ✓ on success)
- **Manual load**: Click 📥 Load button (turns green ✓ on success)
- **Clear all**: Click "Clear All" button (turns green ✓ when cleared)
- **Visual feedback**: All buttons show success/failure with color changes (no popups!)

## File Structure

```
tab_saver/
├── manifest.json       # Extension configuration
├── background.js       # Context menu & Convex integration
├── popup.html          # Popup UI structure
├── popup.js            # Popup functionality
├── popup.css           # Popup styling
├── icons/              # Extension icons
└── README.md           # This file
```

## Data Storage

- **Chrome Storage**: `chrome.storage.local`
- **Convex Backup**: Stored in Convex `backups` table under `tab_saver`

## Troubleshooting

### Context menu not appearing
- Reload the extension in `chrome://extensions/`
- Right-click on the page content (not on images/links)

### Convex not saving
- Make sure `npx convex dev` is running
- Check console for errors (F12 → Console)
- Verify your Convex URL is set correctly in `background.js`

### Tabs not loading
- Check if URLs are valid
- Some Chrome internal pages can't be opened

## Keyboard Shortcuts

You can add custom shortcuts in Chrome:
1. Go to `chrome://extensions/shortcuts`
2. Find "Tab Saver"
3. Set your preferred shortcut

## Privacy

- All data stored in your Convex project
- No third-party tracking or analytics
- Open source code

## License

Free to use and modify!
