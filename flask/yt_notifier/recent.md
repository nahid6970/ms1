# recent.md — AI Handoff

## 1. Project DNA
YouTube channel RSS/API notifier. **Convex** (DB + backend functions + crons) + **Cloudflare Pages** (static frontend, no framework). Frontend talks to Convex via raw HTTP API (`/api/query|mutation|action`). No SDK, no bundler.

## 2. Latest Implementation (2026-08-18)

| File | What changed |
|---|---|
| `convex/schema.ts` | Added `sourcePlaylistTitle` to videos table. Added `playlistMeta` (array of `{id, title}`) to channels table for caching playlist names. |
| `convex/youtube.ts` | `parseRulesText` — headers only on lines starting with `:`. `fetchPlaylistFeedWithApiKey` now fetches real playlist title via `playlists?part=snippet` API (was wrongly using channel name). hardCap raised to 5000. |
| `convex/videos.ts` | OR logic for playlist+allow rules. `addFromFeed` patches `sourcePlaylistId` + `sourcePlaylistTitle` on existing videos. `takeAmount=10000` when `playlistId` filter active. Added `listPlaylists` query (channel→playlist tree with counts/unseen). Added `playlistId` arg to `list` and `counts`. |
| `convex/channels.ts` | `updateRules` only extracts allow-section lines into `titleFilters`. Added `upsertPlaylistMeta` (internal) and `savePlaylistMeta` (public mutation) to store playlist id→title map on channel. |
| `convex/refresh.ts` | `refreshChannel` saves playlist videos with `sourcePlaylistId` + `sourcePlaylistTitle`, calls `upsertPlaylistMeta`. `loadPlaylistVideos` same. |
| `public/js/app.js` | Playlist row: Load button opens modal (limit pills 10/25/50/100/250/All, All default). Added Playlists nav icon (list icon) → popup showing channel→playlist tree with unseen badges. Clicking a playlist navigates to `?playlistId=PLxxx`. Feed shows playlist banner when active. Auto-syncs missing titles via `listChannelPlaylists` on panel open. |

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

## 4. Pending Task
Deploy + open Playlists panel to trigger auto-sync of titles. Re-load "All" on each playlist to stamp `sourcePlaylistId`/`sourcePlaylistTitle` on existing videos. Verify playlist view shows all videos (not capped by feedLimit).
