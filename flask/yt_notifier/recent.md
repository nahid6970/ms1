# recent.md — AI Handoff

## 1. Project DNA
YouTube channel RSS/API notifier. **Convex** (DB + backend functions + crons) + **Cloudflare Pages** (static frontend, no framework). Frontend talks to Convex via raw HTTP API (`/api/query|mutation|action`). No SDK, no bundler.

## 2. Latest Implementation (2026-08-18)

| File | What changed |
|---|---|
| `convex/schema.ts` | Added `sourcePlaylistTitle` to videos table. Added `playlistMeta` (array of `{id, title}`) to channels table for caching playlist names. |
| `convex/youtube.ts` | `parseRulesText` — headers only on lines starting with `:`. `fetchPlaylistFeedWithApiKey` fetches real playlist title via `playlists?part=snippet`. hardCap raised to 5000. |
| `convex/videos.ts` | OR logic for playlist+allow rules. `addFromFeed` patches `sourcePlaylistId`+`sourcePlaylistTitle`. `listPlaylists` query. `playlistId` arg on `list`+`counts`. **Blocked/watchlater use `take(10000)` and skip feedLimit slice.** **`hideShorts` scoped to main feeds only** (not blocked/watchlater). `isPrivateVideo()` helper; `hidePrivate` applied in `list` and `counts`. |
| `convex/channels.ts` | `updateRules` extracts allow-section lines into `titleFilters`. `upsertPlaylistMeta` (internal) + `savePlaylistMeta` (public mutation). |
| `convex/refresh.ts` | `refreshChannel` saves `sourcePlaylistId`+`sourcePlaylistTitle`, calls `upsertPlaylistMeta`. `loadPlaylistVideos` same. |
| `convex/settings.ts` | Added `hide_private` key. Exposed `hidePrivate` in `config` + `updateConfig`. |
| `public/js/app.js` | See detailed breakdown below. |
| `public/settings.html` | Added "Hide Private & Deleted Videos" toggle (between Hide Shorts and Unseen First). |

### app.js Changes (detailed)

| Area | What changed |
|---|---|
| `headerCardCount` | White bg, black text, more visible pill badge. |
| `channelAvatarsBar` | Square corners, fully opaque bg, `border-b` only — fixes scroll bleed-through. **Sticky `× Playlist` pill** appears when `playlistId` active (sky color). `playlistTitle` preserved in avatar links. |
| Playlist banner | Compact single-line: `[icon] Channel / Playlist Name · N videos`. Title resolved via: URL param → `sourcePlaylistTitle` → `playlistMeta` cache → `"Playlist"`. No Clear button (redundant with sticky bar). |
| Nav counts | `playlistId` removed from `videos:counts` call — badges always show global unread. |
| `renderNav` | Accepts `playlistId` + `sortBy` params. `isMainActive` false when on a playlist. **Playlist button** highlights sky + dot when `?playlistId=` active. **Shorts removed** from main feed filter dropdown. |
| Playlist panel URLs | Now include `&playlistTitle=...` so banner title is immediately available on page load. |
| Filter dropdown | Added **Sort By section**: Newest First (default), Oldest First, Title A→Z, Title Z→A. Active sort highlighted in indigo. Filter links preserve `sortBy`. Sort links preserve `category`+`playlistId`. |
| Sort | Client-side sort applied before grid render. `date-desc` = free (backend order). Others sort JS array. `sortBy` URL param (`date-desc` default). |
| `hidePrivate` | Toggle wired in `renderSettingsConfig`, form submit, `changeFeedLimitFromHeader`. |

## 3. Critical Context — How Rules Work

**`:Allow-Rules:`** — title whitelist. Empty = all pass.
**`:Block-Rules:`** — title blacklist. Matches → always Blocked Items.
**`:Playlists:`** — two sub-modes:
- **URL** → strict playlist mode: only videos with matching `sourcePlaylistId` in main feed
- **Text name** → extra allow-rule by title substring, amber highlight

**OR logic:** Playlist URL rules and Allow-Rules are OR conditions. Video passes if either matches. Fails both → Blocked Items.

**`sourcePlaylistId`** — stamped at insert. Re-load "All" to retroactively stamp existing videos.
**`playlistMeta`** on channel — stores `{id, title}` pairs. Populated on Load/refresh/panel auto-sync.
**Section headers** must start with `:`. URLs containing "playlist" are NOT headers.
**Playlist titles** come from `playlists?part=snippet` API.

## 4. Key Behavioral Notes

- **`hideShorts`** — hides shorts from main/unseen/seen/favorites feeds only. Shorts still appear in Shorts feed, Blocked Items, and Watch Later.
- **`hidePrivate`** — filters out `"Private video"` / `"Deleted video"` from all feeds and counts.
- **Blocked Items** — no feedLimit cap. `take(10000)`, no slice. Count in nav badge always matches.
- **Watch Later** — same, no feedLimit cap.
- **Nav badges** — always global counts, never scoped to active `playlistId`.
- **Playlist banner** — compact pill, title from URL param first (most reliable), falls back through `sourcePlaylistTitle` → `playlistMeta` → `"Playlist"`.
- **Sort** — `?sortBy=date-desc|date-asc|title-asc|title-desc`. Client-side only. Default is `date-desc`.

## 5. Pending Task
Deploy + open Playlists panel to trigger auto-sync of titles. Re-load "All" on each playlist to stamp `sourcePlaylistId`/`sourcePlaylistTitle` on existing videos.
