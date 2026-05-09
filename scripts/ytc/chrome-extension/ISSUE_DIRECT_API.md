# Direct YouTube API — Subtitle Fetch Issue

## Status
Fixed ✅ (Implemented via tab context injection)

## What Works
- Fetching the YouTube video page HTML ✅
- Parsing `captionTracks` from `ytInitialPlayerResponse` ✅
- Selecting the correct track by language ✅
- Getting a 200 response from the timedtext endpoint ✅
- Fetching VTT content via `chrome.scripting.executeScript` in the active YouTube tab ✅

## The Problem (Resolved)
The signed `baseUrl` from `captionTracks` contains `ip=0.0.0.0` — a server-side placeholder.
When fetched from the service worker, it returned empty content.

## The Fix
The fetch is now injected into an active YouTube tab for that video using `chrome.scripting.executeScript`. Since content scripts share the page's session and cookies, YouTube returns the full VTT data.

## Next Steps
- [x] Test signed baseUrl with `Referer: https://www.youtube.com/` header (still empty in SW)
- [x] Try fetching via a content script injected into the YouTube tab instead of the service worker
- [x] Use `chrome.scripting.executeScript` to run the fetch inside the YouTube tab context

## Implementation Details
In `background.js`, `fetchDirectAPI` now:
1. Finds a tab matching the video URL.
2. Executes a fetch script within that tab.
3. Falls back to background fetch if no tab is found or injection fails.
