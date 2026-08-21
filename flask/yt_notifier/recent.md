# recent.md — AI Handoff

## 1. Project DNA
YouTube channel RSS/API notifier. **Convex** (DB + backend functions + crons) + **Cloudflare Pages** (static frontend, no framework). Frontend talks to Convex via raw HTTP API (`/api/query|mutation|action`). No SDK, no bundler.

## 2. Latest Implementation (2026-08-18)

| File | What changed |
|---|---|
| `convex/schema.ts` | Added `sourcePlaylistTitle` to videos table. Added `playlistMeta` (array of `{id, title}`) to channels table for caching playlist names. |
| `convex/youtube.ts` | `parseRulesText` — headers only on lines starting with `:`. `fetchPlaylistFeedWithApiKey` fetches real playlist title via `playlists?part=snippet`. hardCap raised to 5000. |
| `convex/videos.ts` | OR logic for playlist+allow rules. `addFromFeed` patches `sourcePlaylistId`+`sourcePlaylistTitle`. `listPlaylists` query. `playlistId` arg on `list`+`counts`. Blocked/watchlater use `take(10000)` and skip feedLimit slice. `hideShorts` scoped to main feeds only. `isPrivateVideo()` helper; `hidePrivate` applied in `list` and `counts`. |
| `convex/channels.ts` | `updateRules` extracts allow-section lines into `titleFilters`. `upsertPlaylistMeta` (internal) + `savePlaylistMeta` (public mutation). |
| `convex/refresh.ts` | `refreshChannel` saves `sourcePlaylistId`+`sourcePlaylistTitle`, calls `upsertPlaylistMeta`. `loadPlaylistVideos` same. |
| `convex/settings.ts` | Added `hide_private` key. Exposed `hidePrivate` in `config` + `updateConfig`. |
| `public/js/app.js` | See detailed breakdown below. |
| `public/settings.html` | Added "Hide Private & Deleted Videos" toggle (between Hide Shorts and Unseen First). |

### app.js Changes (detailed)

| Area | What changed |
|---|---|
| `headerCardCount` | White bg, black text, more visible pill badge. |
| `channelAvatarsBar` | Square corners, fully opaque bg, `border-b` only — fixes scroll bleed-through. Sticky `× Playlist` pill when `playlistId` active (sky color). `playlistTitle` preserved in avatar links. |
| Playlist banner | Compact single-line: `[icon] Channel / Playlist Name · N videos ↗`. Title resolved via: URL param → `sourcePlaylistTitle` → `playlistMeta` cache → `"Playlist"`. No Clear button (redundant with sticky bar). Count number sky-400 bold. YouTube external link icon red-400 at end. |
| Playlist panel URLs | Include `&playlistTitle=...` so banner title is immediately available on page load without DB lookup. |
| Nav counts | `videos:counts` follows the active folder/channel, while playlist views keep global nav counts. |
| `renderNav` | Accepts `playlistId` + `sortBy`. `isMainActive` false when on a playlist. Playlist button highlights sky + dot when active. Shorts removed from main feed filter dropdown. **Playlist button moved before Blocked Items button.** |
| Filter dropdown | Added **Sort By section**: Newest First (default), Oldest First, Title A→Z, Title Z→A. Active sort highlighted in indigo. Filter links preserve `sortBy`. Sort links preserve `category`+`playlistId`. |
| Sort | Client-side sort before grid render. `sortBy` URL param (`date-desc` default). |
| `hidePrivate` | Toggle wired in `renderSettingsConfig`, form submit, `changeFeedLimitFromHeader`. |
| `addPlaylistToChannelRules` | Now accepts `plCount`. After saving rule + re-rendering channels: re-opens playlists box + reloads its list, re-opens rules box, **auto-opens Load modal** — one click does add rule + load. |
| `removePlaylistRule` | New `channels:removePlaylistRule` mutation strips playlist URL line from `rulesText` (videos untouched). Playlists panel rows have a hover `×` button — removes rule, re-renders panel, navigates away if currently on that playlist. |

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

- **`hideShorts`** — hides shorts from main/unseen/seen/favorites only. Shorts still appear in Shorts feed, Blocked Items, Watch Later.
- **`hidePrivate`** — filters out `"Private video"` / `"Deleted video"` from all feeds and counts.
- **Blocked Items** — no feedLimit cap. `take(10000)`, no slice. Count in nav badge always matches.
- **Watch Later** — same, no feedLimit cap.
- **Nav badges** — the active feed badge/header shows the total matching videos before the page limit, scoped to the active folder, channel, and category; inactive badges retain unseen/saved indicators.
- **Playlist banner** — compact pill. Title from `?playlistTitle=` URL param (set by panel nav) first, then fallbacks.
- **Sort** — `?sortBy=date-desc|date-asc|title-asc|title-desc`. Client-side. Default `date-desc`.
- **Nav button order** — YouTube → Shorts → Watch Later → Long Videos → Playlists → Blocked → Filter → Channels → Stats → Settings → Refresh.
- **"+ Rule" button** — adds playlist URL to channel rules AND immediately opens the Load modal. No scrolling needed.

## 5. Long Videos Feed (2026-08-21)

| File | What changed |
|---|---|
| `convex/schema.ts` | Added optional `isLong` flag to videos. |
| `convex/videos.ts` | Added `long` category, `toggleLong` mutation, uncapped Long Videos listing/count, and excludes selected long videos from ordinary feeds. |
| `public/js/app.js` | Added Long Videos nav item immediately after Watch Later, filter/settings entries, long-video count badge, hover hourglass toggle on cards, and a two-row responsive navbar on narrow screens. |

Long Videos behaves like Watch Later: selecting a video moves it out of ordinary feeds and into the uncapped dedicated feed. Videos may be in both collections.

## 6. Key Behavioral Notes Addendum

- **Long Videos** — manually selected with the hourglass hover button; uncapped, hidden from ordinary feeds, and independent from Watch Later.
- **Mobile navbar** — feed controls and navigation/action icons use separate centered rows on narrow screens; desktop alignment is unchanged.
- **Folder Only channels** — channel cards have a toggle that requires an assigned folder; enabled channels are hidden from ordinary main feeds and unread counts until their assigned folder is selected, but remain visible in Shorts, Watch Later, Long Videos, and Blocked feeds.
- **Feed counts** — the active feed’s navbar/header count uses the total matching videos before the page limit, so it remains stable when switching between a numeric limit and All Limit; inactive badges retain their unseen/saved indicators.
- **Channel feed loading** — channel-scoped list queries fetch the full channel set before applying the feed limit, so channel card counts are not based on the global page slice.
- **Folder feed loading** — folder-scoped list queries also fetch the full folder set before applying the feed limit, so a 50-limit folder feed can fill all 50 cards.
- **Folder navigation** — switching between Main, Shorts, Watch Later, Long Videos, and Blocked preserves the active folder filter.

## 7. Pending Task
Deploy to production. Verify playlist views load correctly end-to-end.
