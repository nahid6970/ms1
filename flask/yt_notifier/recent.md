# recent.md — AI Handoff

## 1. Project DNA
YouTube channel RSS/API notifier. **Convex** (DB + backend functions + crons) + **Cloudflare Pages** (static frontend, no framework). Frontend talks to Convex via raw HTTP API (`/api/query|mutation|action`). No SDK, no bundler.

## 2. Latest Implementation (2026-08-17)

| File | What changed |
|---|---|
| `convex/youtube.ts` | `parseRulesText` — section headers now only recognized when line **starts with `:`**. Fixes playlist URLs (which contain the word "playlist") being misread as section headers instead of content. |
| `convex/videos.ts` | Playlist URL rules and Allow-Rules are now **OR conditions** throughout (`list`, `unreadCount`, `counts` queries). `isTitleBlocked` returns false if video passes either filter. `counts` query computes `blocked` from all channel videos (not just `validVideos`). `addFromFeed` patches `sourcePlaylistId` on existing videos that were inserted without one. |
| `convex/refresh.ts` | `refreshChannel` saves playlist videos in a separate `addFromFeed` call with `sourcePlaylistId` set. Accumulates playlist new-video counts into final result. |
| `convex/channels.ts` | `updateRules` only extracts `:Allow-Rules:` lines into `titleFilters`; playlist URLs no longer bleed into title filters. |
| `public/js/app.js` | `parseRulesCount` counts all non-header lines (including playlist URLs) so the rules icon badge activates. |

## 3. Critical Context — How Rules Work

Each channel has a `rulesText` field parsed by `parseRulesText()` into three buckets:

**`:Allow-Rules:`** — title whitelist. If any terms exist, a video's title must match at least one to appear in the main feed. Empty = all titles pass.

**`:Block-Rules:`** — title blacklist. If a video title matches any term it is always excluded from the main feed and goes to Blocked Items (checked before allow/playlist logic).

**`:Playlists:`** — two sub-modes:
- **Playlist URL** (e.g. `https://www.youtube.com/playlist?list=PLxxx`) → **strict playlist mode**: only videos with a matching `sourcePlaylistId` in the DB appear in the main feed.
- **Playlist name / text** (e.g. `Series Name`) → extra allow-rule matched by title substring; matching videos get amber highlight.

**OR logic (critical):** Playlist URL strict mode and Allow-Rules are **OR conditions**. A video reaches the main feed if it **either** comes from an allowed playlist **or** its title matches an allow-rule. Only videos that fail **both** go to Blocked Items. This means you can combine a playlist URL with allow-rules to show playlist videos + title-matched non-playlist videos together.

**Example:**
```
:Allow-Rules:
key odoo concept        ← non-playlist videos with this in title also show

:Block-Rules:

:Playlists:
https://youtube.com/playlist?list=PLxxx   ← all 26 playlist videos show
```
Result: 26 playlist videos + any video titled "key odoo concept" in main feed. Everything else → Blocked Items.

**Key variable:** `video.sourcePlaylistId` (DB field) — stamped at insert time via `loadPlaylistVideos` or `refreshChannel`. If a video was inserted before the rule was added, hit **Load** on the playlist again to retroactively stamp it.

**Section header rule:** Lines must **start with `:`** to be treated as section headers. Content lines (including URLs) are never headers even if they contain the word "playlist".

## 4. Pending Task
Verify after deploy: channel with playlist URL + allow-rule → playlist videos AND title-matched videos both appear in main feed; everything else in Blocked Items.
