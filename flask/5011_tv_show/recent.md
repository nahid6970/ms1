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
- `templates/index.html`, `static/style.css`: Title and Year fields shown side by side in Edit Show modal via `.modal-form-row` / `.modal-form-col` flex layout.
- `app.py`: Scheduler overhauled — replaced same-day window check with `get_last_due_date()` helper that computes the most recent due date per frequency (daily/weekly/monthly); missed runs (PC was off) are caught up on next startup regardless of how much time has passed. Due shows are processed one-by-one with a 3-second stagger between API calls to avoid rate-limit bursts; each show is saved immediately after update so progress survives a mid-batch restart.
- `app.py`: TVmaze is now authoritative for TV-show lifecycle status during discovery adds and episode refreshes; TMDb remains available for show posters and ratings.
- `app.py`: Episode airtimes from TVmaze are converted from the timezone-aware `airstamp` to Bangladesh Standard Time (`Asia/Dhaka`) before storage/display; the UI continues formatting them as 12-hour AM/PM times.
- `app.py`: `last_episode` sort now uses `air_datetime` (UTC airstamp) converted to Bangladesh time as the primary sort key, with `air_date`+`airtime` and date-only as fallbacks. This fixes incorrect ordering caused by `air_date` being the US-local TVmaze date (which can be a day behind the Bangladesh date for late-night US shows like WWE SmackDown).
- `static/style.css`: Hidden Shows modal uses a fixed viewport-height, scrollable max-content grid that preserves 2:3 poster thumbnails; cards use square corners and omit the redundant `Ended` status label.
- `app.py`: The hourly whole-Sonarr-storage scan now hydrates newly discovered shows from TVmaze before attaching files, preventing raw filename episodes from duplicating TVmaze episodes.
- `app.py`: The hourly combined scan now runs the full storage scan after auto-adding folders on every interval run, matching the Scan Storage button consistently.
- `app.py`, `templates/_settings_modal.html`, `static/script.js`: Whole-storage scan interval is configurable in Settings from 1 to 10,080 minutes; it defaults to 60 minutes and applies immediately when saved.
- `app.py`: Saving the storage interval now explicitly schedules the next scan from the save time and prevents overlapping scan runs.
- `app.py`: Fixed Settings save failure by applying the scheduler interval and next-run time through their supported APScheduler APIs.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date`. TVmaze updates merge by season/episode, preserve watched/file fields, and refresh show poster/status. Per-show `episode_update_time` is local `HH:MM`; cadence supports daily, weekly weekday, or monthly day; blank disables it. APScheduler checks once per minute. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. Stars are whole-number 1–5; original scores remain `tmdb_rating`.

- `app.py`, `templates/index.html`: Added "Next Episode" sort option — sorts shows by their next upcoming episode after the last released one (soonest first by default); shows with no upcoming episodes sort to the end. Uses the same UTC airstamp → Bangladesh datetime logic as the `last_episode` sort.
- `static/script.js`: `isReleasedAndUnwatched` now includes today's episodes in the red-highlight logic — episodes with `air_date < today` are always red; episodes with `air_date === today` are red only if their `airtime` has already passed (time-aware check).

# 4. Pending Task

Run an end-to-end browser test at desktop/mobile widths for discovery, imports, refresh, sorting, TVmaze updates, and responsive layout.
