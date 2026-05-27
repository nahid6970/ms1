# Image Checker Developer Guide

Main guide for the Chrome extension at:

```text
C:\@delta\ms1\test_project\my-first-extension\convex_extensions_manager\image_checker
```

Related docs:

- `#[[file:md/IMAGE_CHECKER_RECENT.md]]`
- `#[[file:md/IMAGE_CHECKER_PROBLEMS_AND_FIXES.md]]`
- `#[[file:md/IMAGE_CHECKER_FEATURES.md]]`

## Project Summary

Image Checker is a Manifest V3 Chrome extension for marking already-reviewed images, videos, and media thumbnails with persistent green checkmarks.

The extension is especially tuned for Facebook group media/video grids, where video items often appear as image thumbnails inside complex React wrappers.

## Runtime Files

- `manifest.json`: extension config, permissions, content script registration.
- `content.js`: page scanning, media ID generation, marking, syncing, rendering.
- `styles.css`: checkmarks, notifications, temporary hide behavior, edit button styling.
- `popup.html`: popup layout.
- `popup.js`: popup state, settings, clear/save/load actions.
- `popup.css`: popup styling.
- `background.js`: background worker and Convex sync behavior.

## Setup

1. Open Chrome.
2. Go to `chrome://extensions/`.
3. Enable Developer Mode.
4. Click `Load unpacked`.
5. Select:

```text
C:\@delta\ms1\test_project\my-first-extension\convex_extensions_manager\image_checker
```

After code changes, reload the unpacked extension and refresh the target webpage.

## Development Checks

Run this after editing `content.js`:

```powershell
node --check content.js
```

## Storage Keys

- `seenItems`: map of content IDs to timestamps.
- `imageCheckerSettings`: user settings for checkmark size, color, border, and hide behavior.
- `checkingMode_global`: global checking mode state.
- `excludedDomains`: domains where the extension should not run.

## Content ID Strategy

Media items are stored using stable IDs:

```text
media|<normalized-media-url>
yt_<youtube-video-id>
link|<href>|<text-snippet>
```

For Facebook CDN media, strip query parameters and keep:

```text
origin + pathname
```

This prevents saved marks from disappearing when Facebook rotates CDN query parameters.

## Checking Mode Contract

Checking mode controls editing only.

When ON:

- User can mark/unmark media.
- Hover/edit affordances may appear.
- Facebook edit controls can appear over thumbnails.

When OFF:

- Edit affordances disappear.
- Saved center checkmarks remain visible.

## Manual Test Checklist

1. Reload the extension.
2. Open a normal image-heavy page.
3. Enable checking mode with popup or `F2`.
4. Mark an item.
5. Disable checking mode.
6. Confirm center checkmark remains visible.
7. Refresh the page.
8. Confirm the checkmark returns.
9. Open Facebook group Media > Videos.
10. Mark a video thumbnail.
11. Disable checking mode.
12. Confirm center checkmark remains visible.
13. Refresh Facebook.
14. Confirm the mark persists.
15. Clear all checkmarks from popup.
16. Confirm all marks disappear.

