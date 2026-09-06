# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, discovery, and episode updates.

# 2. Latest Implementation

- `static/style.css`: Increased `#editShowModal > div` max-width from 450px to 620px for a wider edit modal.
- `app.py`, `static/script.js`: Edit show save now live-updates the card in-place (title, cover image, status badge, rating stars, and `data-*` filter attributes) without a page reload; `edit_show` POST JSON response now returns updated show fields. Card patch extracted into reusable `patchShowCard(s)` helper.
- `static/style.css`: Show card hover buttons now have permanent per-button colors (sync/edit → blue `#3b82f6`, episodes-update → emerald, folder → amber, list → green, sonarr → cyan, delete → red); hover darkens each; overlay fades in on card hover, hidden by default. First two buttons (sync + episodes-update) are on the same row via `.hover-btn-row`.
- `app.py`, `static/script.js`, `templates/index.html`, `templates/_settings_modal.html`, `static/style.css`: Episode file-existence icons in episodes modal — `GET /api/episode_file_check/<show_id>` scans directory for video files; returns keys by scan mode (sxxexx/date/title); yellow folder icon (`#ffc83d`) shown after episode title for matched files; global "Episode File Icons" toggle in Settings; per-show "File Pattern" and "File Scan Mode" fields in Edit Show modal (`sxxexx` / `date` YYYY-MM-DD / `title`); `currentEpisodeFileSet` + `currentEpisodeFileScanMode` preserved across re-renders.
- `app.py`, `templates/index.html`, `static/script.js`: Fixed file sync duplicates — `scan_and_update_episodes` extracts `SxxExx` or `YYYY-MM-DD` (per `scan_mode`) from filenames, matches existing TVmaze episodes by `(season, episode)` or `air_date`, sets `has_file=True`/`file_name` instead of creating duplicates. Title-match fallback for non-standard shows.
- `app.py`, `static/script.js`: TVmaze episode refresh (`refreshEpisodesInModal`, `updateShowEpisodes`) now calls `patchShowCard` to live-update cover, status, and TMDb rating badge without reload. New `resolve_tmdb_for_show` helper auto-discovers `tmdb_id` via TVmaze `externals.thetvdb` → TMDb `/find` (then `imdb` fallback) for manually added shows; also refreshes `tmdb_rating` from TMDb `vote_average`; falls back to TVmaze `image.original` for cover when no TMDb available.
- `app.py`: `last_episode` sort now skips future-dated episodes — only episodes with `air_date` ≤ today are considered, preventing upcoming episodes from inflating a show's sort position.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date`. TVmaze updates merge by season/episode, preserve watched/file fields, and refresh show poster/status. Per-show `episode_update_time` is local `HH:MM`; cadence supports daily, weekly weekday, or monthly day; blank disables it. APScheduler checks once per minute. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. Stars are whole-number 1–5; original scores remain `tmdb_rating`.

# 4. Pending Task

Run an end-to-end browser test at desktop/mobile widths for discovery, imports, refresh, sorting, TVmaze updates, and responsive layout.
