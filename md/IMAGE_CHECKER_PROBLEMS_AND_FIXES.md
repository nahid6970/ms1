# Image Checker Problems & Fixes Log

## 2026-05-27 - Facebook Video Thumbnails Would Not Mark

**Problem:** Clicking Facebook group Media > Videos thumbnails did not reliably add a mark.

**Root Cause:** Facebook thumbnails are React-managed image/link wrappers. The visible tile is often not a simple clickable `video` element, and Facebook can consume or redirect click behavior.

**Solution:** Treat the thumbnail image as the media identity and use extension-owned marking controls/overlays where needed.

**Files Modified:** `content.js`, `styles.css`

## 2026-05-27 - Checkmarks Disappeared After Refresh

**Problem:** Marked Facebook video thumbnails did not restore after refreshing the page.

**Root Cause:** Facebook CDN (`fbcdn.net`) image URLs rotate query parameters. Saving the full URL made the same thumbnail look like a new item after refresh.

**Solution:** Normalize Facebook CDN URLs to `origin + pathname` before building `media|...` IDs.

**Files Modified:** `content.js`

## 2026-05-27 - Checkmarks Only Visible While F2 Mode Was Enabled

**Problem:** Saved marks were visible during checking mode, but disappeared when edit mode was disabled.

**Root Cause:** Display behavior was too closely tied to checking mode and edit controls.

**Solution:** Separate saved checkmark display from checking mode. Checking mode controls editing; saved marks remain visible independently.

**Files Modified:** `content.js`

## 2026-05-27 - Facebook DOM Could Hide Center Checkmarks

**Problem:** Checkmarks could be clipped or hidden by Facebook tile containers.

**Root Cause:** Facebook uses nested wrappers, overflow clipping, and stacking contexts.

**Solution:** Render checkmarks as document-level fixed overlays with high `z-index`, and refresh overlay positions on scroll/resize.

**Files Modified:** `content.js`, `styles.css`

