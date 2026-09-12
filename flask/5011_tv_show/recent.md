# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, discovery, and episode updates.

# 2. Latest Implementation

- `templates/_settings_modal.html`, `static/script.js`, `app.py`: Added configurable Auto Schedule Start/End times. The Scheduled Episode Updates header action is now `RESCHEDULE`, which redistributes every active show across that time window, assigns Weekly weekdays and Monthly dates, and preserves `None` shows.
- `templates/discover.html`, `static/discover.js`, `static/style.css`: Discover search controls are sticky and use the neon UI. Non-search modes hide the query box; browse-mode controls shrink and center. The preset button now uses mode-specific icons plus a compact region label, with the mode text hidden.
- `templates/discover.html`, `static/discover.js`, `app.py`: Discovery region filters now include Korean, Chinese, Japanese Live Action, Cartoons / Animation, and Documentary / Reality. General animation excludes Japanese-original animation so Anime remains a separate filter.
- `templates/index.html`, `static/script.js`, `static/style.css`: Scheduled Episode Updates received the neon reference UI, compact header `SAVE` / `CLEAR` / `SORT` controls, default `Cadence` sorting (Daily → Weekly → Monthly → unscheduled), and aligned per-show action controls even when a row has no clear-stats button.
- `templates/index.html`, `static/script.js`, `static/style.css`, `app.py`: Scheduled Episode Updates modal now manages per-show `None` / `Daily` / `Weekly` / `Monthly` frequency choices in-row; bulk save preserves existing schedule values and auto-fills missing time/day/date values. Scheduling controls were removed from Edit Show, and editing show metadata no longer overwrites schedules. Edit Show now uses the neon reference styling with a vertical `SAVE` button.
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

# 4. Latest Changes

- `app.py`, `static/movies.js`, `static/style.css`: Scheduled Movie Metadata rows now display the next calculated run date/time for active Daily/Weekly/Monthly schedules.

- `app.py`, `templates/movies.html`, `static/movies.js`, `static/style.css`: Added Scheduled Movie Metadata. The Movies page now has a searchable modal with Daily/Weekly/Monthly/None cadence controls, reschedule and Run Now actions, timestamped results, and completed green digital-release dates. Scheduled checks stop automatically once TMDb supplies a digital release date.

- `templates/index.html`, `static/style.css`: Improved the Edit Show episode settings layout with wider equal columns, single-line labels, and shorter scan-mode help text.

- `templates/index.html`: Simplified the season-offset and retention labels to fit the side-by-side Edit Show fields and removed the explanatory text beneath them.

- `app.py`, `templates/index.html`, `static/script.js`: Added per-show `Keep Released Episodes` retention beside Filename Season Offset. Positive limits keep the newest released episodes, preserve future/undated episodes, prune on save and TVmaze refresh, and prevent storage scans from re-adding pruned raw episodes; `0` keeps all.

- `app.py`, `templates/index.html`, `static/script.js`: Added a per-show Filename Season Offset setting. File scanning and file-existence icons normalize offset filename seasons to TVmaze seasons, while the episode copy button outputs the offset season used by torrent naming.

- `static/style.css`: Fixed Scheduled Episode Updates search filtering by explicitly hiding nonmatching flex rows.

- `templates/index.html`, `static/script.js`, `static/style.css`: Scheduled Episode Updates now has a live show-name search box that filters rows without affecting their schedule controls.

- `app.py`, `templates/movies.html`, `static/style.css`: Digital release badges now use Bangladesh local time for date comparison: green for today/past releases and pink for future releases.

- `app.py`, `templates/movies.html`, `static/style.css`: Movie metadata now reads TMDb digital release dates (release type 4), stores the earliest available date, and displays it as a `Digital: YYYY-MM-DD` badge below the Watched/Unwatched badge.

- `templates/movies.html`, `static/style.css`, `app.py`: Movie cards now group Radarr, TMDb, and IMDb links in the right-side action row. IMDb IDs are retained from Radarr sync and TMDb metadata refresh, and the IMDb button is shown only when an exact IMDb ID is available.

- `static/script.js`: Scheduled episode run results now show elapsed time (`just now`, `5m`, `3h 22m`, `2d 3h 55m`) instead of a locale timestamp. Only nonzero newly added episode counts are shown; zero-result runs omit the counters.
- `app.py`: Volatile per-show fields (`episodes_updated_at`, `last_run_result`, `episode_update_last_run`) moved out of `data.json` into a separate `C:\@delta\db\5011_tv_show\timestamps.json` file (not git-tracked). Added `load_timestamps`, `save_timestamps`, `get_show_ts`, `set_show_ts` helpers. All scheduler, manual update, and schedule API routes updated to read/write from the timestamps file. Eliminates constant `git status` noise from the main data file.
- `static/script.js`: Fixed `#refreshOpenEpisodes` button staying as a checkmark permanently after a successful update — the `setTimeout` restore was gated on `btn.disabled` which was already `false` by then; now always restores after 1.4s.
- `templates/index.html`, `static/script.js`, `static/style.css`: Replaced the two episode sort `<select>` elements (`#episodeSortType`, `#episodeSortOrder`) with a single icon button that opens an Android-style two-section chip panel. "Sort by" section has Order/Name chips; "Direction" section has ASC ↑/DESC ↓ chips. Each group is independent — selecting one chip applies immediately without closing the panel; panel closes on outside click. Hidden `<select>` elements retained so existing `saveEpisodeSort` logic works unchanged. Button is icon-only (funnel/lines SVG), no text label.
- `app.py`, `templates/index.html`, `static/script.js`, `static/style.css`: Added "Hide future episodes" toggle button (eye-slash icon) to the left of the sort button in the episodes modal. State is persisted per-show in `data.json` via `hide_future_episodes` field and a `POST /api/show/<id>/hide_future_episodes` route. Button syncs on modal open and after episode refresh. Active state turns button blue. Filter applied inside `renderEpisodes` — hides episodes with `air_date > today`.
- `templates/index.html`, `static/script.js`, `static/style.css`: "Shows" nav link converted to a dropdown (▾) with two items — "Shows" (normal view) and "Shows ✅" (completed-only view). Clicking "Shows ✅" toggles `body.view-completed` — hides all non-`ended-completed` cards and shows `ended-completed` cards as full TV cards in the main grid (no modal). Nav button label updates to "Shows ✅ ▾" when in completed mode; `active-item` class (green highlight) moves between items accordingly. Dropdown styled with dark `#16202e` bg, `rgba` border, scale+fade animation (`transform-origin: top left`), small upward arrow via `::before`, and outside-click close.
- `app.py`, `templates/index.html`, `static/script.js`, `static/style.css`: Archive feature — archive button (box icon) added in episodes modal after hide-future-episodes button. Clicking it calls `POST /api/show/<id>/archive` which toggles `archived` bool in `data.json`. Archived shows get `.archived` CSS class on their card (hidden from main view by default). Shows dropdown gains an "Archived 📦" item that sets `body.view-archived` to show only archived cards. Switching between Shows/Shows ✅/Archived clears the other active view. Nav button label and `active-item` highlight update accordingly. Archive button state syncs on episodes modal open. Active state uses orange/amber (`#fb923c`) via `aria-pressed="true"` CSS selector.
- `static/script.js`: Search `filterShows` overhauled — normalizes both query and card title by stripping all punctuation (`/[^a-z0-9\s]/g`), splits query into individual words, and requires all words to match anywhere in the title+year (`words.every`). Fixes cases like `"dr stone"` not matching `"Dr. STONE"`. Matched cards are force-shown as `display:flex` even if archived/hidden/completed; clearing search restores CSS-driven visibility.

# 5. Pending Task

- Fix `data.json` corruption on power cut: replace `save_data` / `save_movies` / `save_settings` with atomic write (write to `.tmp`, rotate to `.bak`, then rename) and harden `load_data` to fall back to `.bak` automatically if main file is empty/corrupt.
