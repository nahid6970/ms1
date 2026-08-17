# recent.md — AI Handoff

## 1. Project DNA
YouTube channel RSS/API notifier. **Convex** (DB + backend functions + crons) + **Cloudflare Pages** (static frontend, no framework). Frontend talks to Convex via raw HTTP API (`/api/query|mutation|action`). No SDK, no bundler.

## 2. Latest Implementation (2026-08-17)

| File | What changed |
|---|---|
| `convex/youtube.ts` | `parseRulesText` — section headers only recognized when line **starts with `:`**. Fixes playlist URLs containing "playlist" being misread as headers. `fetchPlaylistFeedWithApiKey` hardCap raised 500→5000 for "All" loads. |
| `convex/videos.ts` | Playlist URL rules and Allow-Rules are **OR conditions** (`list`, `unreadCount`, `counts`). `isTitleBlocked` returns false if video passes either filter. `counts` computes blocked from all channel videos. `addFromFeed` patches `sourcePlaylistId` on existing videos missing it. |
| `convex/refresh.ts` | `refreshChannel` saves playlist videos via separate `addFromFeed` with `sourcePlaylistId`. `loadPlaylistVideos` accepts `maxItems` only (date filter removed). |
| `convex/channels.ts` | `updateRules` only extracts `:Allow-Rules:` lines into `titleFilters`. |
| `public/js/app.js` | `parseRulesCount` counts all non-header lines. Playlist row: inline select removed, Load opens a **modal** with limit pills (10/25/50/100/250/All — All pre-selected). Duplicate Load button fragment fixed. |

## 3. Critical Context — How Rules Work

Each channel has a `rulesText` field parsed by `parseRulesText()` into three buckets.

**`:Allow-Rules:`** — title whitelist. If any terms exist, a video's title must match at least one to appear in the main feed. Empty = all titles pass.

**`:Block-Rules:`** — title blacklist. If a video title matches any term it is always excluded → Blocked Items.

**`:Playlists:`** — two sub-modes:
- **Playlist URL** (`https://youtube.com/playlist?list=PLxxx`) → **strict playlist mode**: only videos with matching `sourcePlaylistId` in DB appear in main feed.
- **Playlist name / text** (`Series Name`) → extra allow-rule matched by title substring; matching videos get amber highlight.

**OR logic (critical):** Playlist URL rules and Allow-Rules are **OR conditions**. Video reaches main feed if it **either** comes from an allowed playlist **or** its title matches an allow-rule. Fails both → Blocked Items.

**Example:**
```
:Allow-Rules:
key odoo concept        ← non-playlist videos with this title also show

:Block-Rules:

:Playlists:
https://youtube.com/playlist?list=PLxxx   ← all playlist videos show
```

**`sourcePlaylistId`** — DB field stamped at insert. If videos existed before a playlist rule was added, hit **Load → All** to retroactively stamp them. Re-loading (even 0 new videos) patches unstamped existing videos.

**Section header rule:** Lines must **start with `:`** to be treated as headers. Content lines including URLs are never headers.

**Load modal:** Default is "All" (fetches up to 5000 from API). Use lower limits only to save API quota on very large playlists.

## 4. Current Status
Everything working. Key reminder: after re-loading a playlist, existing videos that were already marked **seen** (`isNew=false`) will appear at the bottom or be hidden if on Unseen filter — switch to **All Videos** filter to see them. No pending tasks.
