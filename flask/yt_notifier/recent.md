# recent.md — AI Handoff

## 1. Project DNA
YouTube channel RSS/API notifier. **Convex** (DB + backend functions + crons) + **Cloudflare Pages** (static frontend, no framework). Frontend talks to Convex via raw HTTP API (`/api/query|mutation|action`). No SDK, no bundler.

## 2. Latest Implementation (2026-08-18)

| File | What changed |
|---|---|
| `convex/schema.ts` | Added `sourcePlaylistTitle` to videos table. Added `playlistMeta` (array of `{id, title}`) to channels table for caching playlist names. |
| `convex/youtube.ts` | `parseRulesText` — headers only on lines starting with `:`. `fetchPlaylistFeedWithApiKey` now fetches real playlist title via `playlists?part=snippet` API (was wrongly using channel name). hardCap raised to 5000. |
| `convex/videos.ts` | OR logic for playlist+allow rules. `addFromFeed` patches `sourcePlaylistId` + `sourcePlaylistTitle` on existing videos. `listPlaylists` query (channel→playlist tree with counts/unseen). `playlistId` arg on `list` and `counts`. **Blocked/watchlater now use `take(10000)` and skip feedLimit slice** so all matching videos are shown. **`hideShorts` filter scoped to main feeds only** — blocked and watchlater pass shorts through regardless of setting. `isPrivateVideo()` helper added; `hidePrivate` setting applied in both `list` and `counts`. |
| `convex/channels.ts` | `updateRules` only extracts allow-section lines into `titleFilters`. `upsertPlaylistMeta` (internal) and `savePlaylistMeta` (public mutation) store playlist id→title map on channel. |
| `convex/refresh.ts` | `refreshChannel` saves playlist videos with `sourcePlaylistId` + `sourcePlaylistTitle`, calls `upsertPlaylistMeta`. `loadPlaylistVideos` same. |
| `convex/settings.ts` | Added `hide_private` key. Exposed `hidePrivate` in `config` query and `updateConfig` mutation. |
| `public/js/app.js` | **`headerCardCount`** badge — white bg, black text, more visible. **`channelAvatarsBar`** — square corners, fully opaque bg, border-b only (fixes scroll bleed-through). **Playlist banner** redesigned — gradient bg, icon badge, proper Clear button. **Nav counts no longer pass `playlistId`** to `videos:counts` — badges always show global unread. `hidePrivate` toggle wired in `renderSettingsConfig`, form submit, and `changeFeedLimitFromHeader`. |
| `public/settings.html` | Added "Hide Private & Deleted Videos" toggle (between Hide Shorts and Unseen First). |

## 3. Critical Context — How Rules Work

**`:Allow-Rules:`** — title whitelist. Empty = all pass.
**`:Block-Rules:`** — title blacklist. Matches → always Blocked Items.
**`:Playlists:`** — two sub-modes:
- **URL** → strict playlist mode: only videos with matching `sourcePlaylistId` in main feed
- **Text name** → extra allow-rule by title substring, amber highlight

**OR logic:** Playlist URL rules and Allow-Rules are OR conditions. Video passes if either matches. Fails both → Blocked Items.

**`sourcePlaylistId`** — stamped at insert. Re-load "All" to retroactively stamp existing videos.
**`playlistMeta`** on channel — stores `{id, title}` pairs. Populated on Load/refresh/panel auto-sync. Used by Playlists panel so titles show without scanning videos.
**Section headers** must start with `:`. URLs containing "playlist" are NOT headers.
**Playlist titles** come from `playlists?part=snippet` API (not from `playlistItems` channelTitle which returns channel name).

## 4. Key Behavioral Notes

- **`hideShorts`** — hides shorts from main/unseen/seen/favorites feeds only. Shorts still appear in the Shorts feed, Blocked Items, and Watch Later.
- **`hidePrivate`** — filters out videos titled `"Private video"` or `"Deleted video"` from all feeds and counts.
- **Blocked Items** — no feedLimit cap. Uses `take(10000)` so count in nav badge matches videos shown.
- **Watch Later** — same, no feedLimit cap.
- **Nav badges** — always show global counts (never scoped to active `playlistId`).
- **Playlist banner** — shown when `?playlistId=` is in URL. Shows playlist title, channel name, video count, and a Clear link.

## 5. Pending Task
Deploy + open Playlists panel to trigger auto-sync of titles. Re-load "All" on each playlist to stamp `sourcePlaylistId`/`sourcePlaylistTitle` on existing videos. Verify playlist view shows all videos (not capped by feedLimit).
