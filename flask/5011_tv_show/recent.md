# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, discovery, and episode updates.

# 2. Latest Implementation

- `static/style.css`: Increased `#editShowModal > div` max-width from 450px to 620px for a wider edit modal.
- `app.py`, `static/script.js`: Edit show save now live-updates the card in-place (title, cover image, status badge, rating stars, and `data-*` filter attributes) without a page reload; `edit_show` POST JSON response now returns updated show fields.
- `static/style.css`: Show card hover buttons now have permanent per-button colors (sync/edit → blue `#3b82f6`, episodes-update → emerald, folder → amber, list → green, sonarr → cyan, delete → red); hover darkens each; overlay fades in on card hover, hidden by default. First two buttons (sync + episodes-update) are on the same row via `.hover-btn-row`.
- `app.py`, `static/script.js`, `templates/index.html`, `templates/_settings_modal.html`, `static/style.css`: Episode file-existence icons in episodes modal — `GET /api/episode_file_check/<show_id>` scans the show's `directory_path` for video files matching `SxxExx` (or a per-show custom regex saved as `episode_file_pattern`); a yellow folder icon (Windows Explorer `#ffc83d`) appears after the episode title for matched episodes; global toggle "Episode File Icons" in Settings; per-show "File Pattern" field in Edit Show modal; `currentEpisodeFileSet` preserved across sort/bulk re-renders.
- `app.py`, `templates/index.html`, `static/script.js`: Fixed file sync duplicates — `scan_and_update_episodes` now extracts `SxxExx` from filenames and matches against existing TVmaze episodes by `(season_number, episode_number)`, setting `has_file=True` / `file_name` instead of creating a duplicate row. Falls back to exact title match only when no SxxExx found. Per-show "File Scan Mode" added to Edit Show modal (`sxxexx` default vs `title` for non-standard naming shows); saved as `scan_mode` on each show.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date`. TVmaze updates merge by season/episode, preserve watched/file fields, and refresh show poster/status. Per-show `episode_update_time` is local `HH:MM`; cadence supports daily, weekly weekday, or monthly day; blank disables it. APScheduler checks once per minute. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. Stars are whole-number 1–5; original scores remain `tmdb_rating`.

# 4. Pending Task

Run an end-to-end browser test at desktop/mobile widths for discovery, imports, refresh, sorting, TVmaze updates, and responsive layout.
