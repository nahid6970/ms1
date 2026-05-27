# Image Checker Feature Specifications

## Persistent Media Checkmarks

**Status:** Complete

**Description:** Lets users mark media items as reviewed. Saved media items show green center checkmarks.

**Implementation:** `content.js` scans supported media selectors, generates a content ID, stores IDs in `chrome.storage.local.seenItems`, and renders visual checkmarks for matching processed elements.

**Files Involved:** `content.js`, `styles.css`, `popup.js`

**Usage:** Enable checking mode, mark media, then disable checking mode. Saved checkmarks remain visible.

## Facebook Group Media Support

**Status:** Complete

**Description:** Supports Facebook group Media > Videos thumbnails, which are typically rendered as images rather than actual video tags.

**Implementation:** Facebook CDN URLs are normalized so unstable query parameters do not affect saved IDs. Checkmarks render independently of Facebook's nested DOM.

**Files Involved:** `content.js`, `styles.css`

**Usage:** Enable checking mode on Facebook group media pages, mark video thumbnails, then disable checking mode to view persistent center checkmarks.

## Temporary Hide Checkmarks

**Status:** Complete

**Description:** Allows temporarily hiding checkmarks from popup settings.

**Implementation:** Adds/removes `ic-hide-checkmarks` class on `body`. Saved IDs remain in storage.

**Files Involved:** `popup.html`, `popup.js`, `content.js`, `styles.css`

**Usage:** Toggle `Hide All Checkmarks (Temp)` in popup settings.

## Domain Exclusions

**Status:** Complete

**Description:** Allows disabling the extension on specific domains.

**Implementation:** `content.js` checks `excludedDomains` before running the extension.

**Files Involved:** `content.js`, `popup.js`

**Usage:** Add domains in popup settings.

## Convex Save/Load

**Status:** Present

**Description:** Popup includes save/load actions for syncing extension data through Convex.

**Implementation:** Popup sends messages to `background.js`, which handles Convex-related actions.

**Files Involved:** `popup.js`, `background.js`

**Usage:** Use popup `Save to Convex` and `Load from Convex` controls.

