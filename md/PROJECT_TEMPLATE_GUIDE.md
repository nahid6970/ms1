# Image Checker Extension Guide

This document describes the `image_checker` Chrome extension project, its main files, runtime behavior, and the current implementation notes for marking images and Facebook group media thumbnails.

## Project Location

```text
C:\@delta\ms1\test_project\my-first-extension\convex_extensions_manager\image_checker
```

## Purpose

Image Checker is a Manifest V3 Chrome extension that lets the user mark media items with green checkmarks while browsing. It is mainly used to track which images or video thumbnails have already been reviewed.

The extension supports:

- Images (`img`)
- Videos (`video`)
- Elements with inline `background-image`
- YouTube thumbnails and player items
- Facebook group media/video thumbnails

## Core User Flow

1. Load the extension from `chrome://extensions/` with Developer Mode enabled.
2. Open a supported page, such as a Facebook group Media tab.
3. Enable checking mode from the popup or with `F2`.
4. Mark or unmark media items.
5. Disable checking mode when finished.
6. Saved checkmarks remain visible on marked thumbnails.

## Main Files

```text
image_checker/
├── manifest.json      # Chrome extension manifest
├── content.js         # Main page scanning, marking, rendering, persistence sync
├── styles.css         # Checkmark, notification, and edit button styles
├── popup.html         # Extension popup UI
├── popup.js           # Popup toggle/settings behavior
├── popup.css          # Popup styles
├── background.js      # Background service worker and Convex sync hooks
├── README.md          # Basic project README
├── icons/             # Extension icons
└── assets/            # Optional assets
```

## Manifest

The extension uses Manifest V3.

Important permissions:

- `storage`: saves seen items and settings.
- `scripting`: available for extension scripting needs.
- `downloads`: used by existing extension features.
- `tabs`: lets popup messaging reach tabs.

Host permissions:

- `<all_urls>` so the content script can run on general sites.
- `https://*.convex.cloud/*` for Convex-related syncing.

The content script injects:

- `styles.css`
- `content.js`

## Storage Model

The main local storage keys are:

- `seenItems`: object keyed by content ID, value is timestamp.
- `imageCheckerSettings`: checkmark color, size, border, text color, hide toggle.
- `checkingMode_global`: global checking mode state used by popup/F2 flow.
- `excludedDomains`: domains where the extension should not run.

`seenItems` example:

```json
{
  "media|https://scontent.example.fbcdn.net/v/t15.5256-10/file.jpg": 1779880000000
}
```

## Content IDs

`content.js` generates stable IDs for media so saved marks can be restored after reloads.

Generic media IDs:

```text
media|<normalized-media-url>
```

YouTube IDs:

```text
yt_<video-id>
```

Link fallback IDs:

```text
link|<href>|<text-snippet>
```

Facebook CDN handling is important: `fbcdn.net` URLs often rotate query parameters after refresh. The extension normalizes those URLs by keeping only:

```text
origin + pathname
```

This avoids losing saved checkmarks when Facebook changes tracking/query parameters.

## Checking Mode

Checking mode controls editing, not whether saved checkmarks are visible.

When checking mode is ON:

- The page scans for media.
- Hover outlines appear.
- Media can be marked/unmarked.
- Edit controls may appear where needed, especially for Facebook media grids.

When checking mode is OFF:

- Editing controls are removed.
- Saved center checkmarks remain visible.
- Stored marks still sync when the page changes.

## Checkmark Rendering

Saved marks are rendered as fixed-position overlays centered on the target thumbnail. This is necessary for pages like Facebook, where thumbnails often live inside complex wrappers with clipping, stacking contexts, and React-managed click behavior.

Rendering rules:

- Use the media element or target container bounding box.
- Place the checkmark at the visual center.
- Use a high `z-index`.
- Keep `pointer-events: none` so the mark does not block page interactions.
- Re-render on scroll/resize because fixed overlays depend on viewport coordinates.

## Facebook Media Notes

Facebook group video grids do not behave like simple pages:

- The visible video tile is usually an image thumbnail.
- Click handlers may be attached to wrapper links, overlays, or React-managed elements.
- The actual `img` can be detected and processed even when normal click marking fails.
- `fbcdn.net` URLs include expiring or rotating query params.

The stable approach is:

- Detect and process the thumbnail image.
- Normalize `fbcdn.net` URL IDs.
- Render saved checkmarks independently of Facebook's DOM nesting.
- Keep edit behavior separate from saved mark visibility.

## Popup Behavior

The popup controls:

- Start/stop checking mode.
- Clear all checkmarks.
- Save/load data with Convex.
- Visual settings such as checkmark size/color and border.
- Temporary hide checkmarks setting.
- Domain exclusions.

The popup communicates with `content.js` through `chrome.tabs.sendMessage`.

## Development Workflow

After editing `content.js`, run:

```powershell
node --check content.js
```

Then reload the unpacked extension:

1. Open `chrome://extensions/`.
2. Find `Image Checker`.
3. Click reload.
4. Refresh the target webpage.

## Manual Test Checklist

Use this after behavior changes:

1. Enable checking mode with `F2`.
2. Mark a normal image.
3. Disable checking mode.
4. Confirm the center checkmark remains visible.
5. Refresh the page.
6. Confirm the checkmark returns.
7. Test Facebook group Media > Videos.
8. Mark a Facebook video thumbnail.
9. Disable checking mode.
10. Confirm the center checkmark remains visible.
11. Refresh Facebook.
12. Confirm the mark persists.
13. Clear all checkmarks from popup.
14. Confirm all marks disappear.

## Common Issues

### Checkmark Only Shows While F2 Is Enabled

Cause:

Saved mark display was tied too closely to checking mode.

Fix:

Checking mode should only control editing. Saved marks should render independently when `seenItems` contains the media ID.

### Facebook Marks Disappear After Refresh

Cause:

Full `fbcdn.net` URLs include rotating query parameters.

Fix:

Normalize Facebook media URLs to `origin + pathname` before generating the `media|...` ID.

### Checkmark Appears in Wrong Position

Cause:

Fixed-position overlays depend on viewport coordinates.

Fix:

Re-render overlays on scroll and resize.

### Checkmark Hidden Behind Facebook UI

Cause:

Facebook uses nested wrappers, clipping, and stacking contexts.

Fix:

Render checkmarks into `document.body` as fixed overlays with high `z-index`.

## Safe Editing Notes

- Keep edits focused in `content.js` and `styles.css` unless popup UI changes are required.
- Avoid tying saved mark visibility to checking mode.
- Do not use raw CSS attribute selectors with full media URLs for matching, because long query strings can break matching logic or become unstable.
- Prefer comparing `dataset.icContentId` values in JavaScript when matching processed elements.
- Always test on both a normal image page and Facebook group media/video grids.

