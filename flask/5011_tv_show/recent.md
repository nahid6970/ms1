# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, and discovery.

# 2. Latest Implementation

- `app.py`: Added TMDb search/import, movie release dates/refresh, TVmaze episode/air-date merging plus show poster/status refresh, reliable sorting, and per-show daily/weekly/monthly scheduling.
- `templates/discover.html`, `static/discover.js`: Added unified discovery, type/sort/count controls, pagination, remembered preferences, and duplicate checkmarks.
- `templates/index.html`, `templates/movies.html`: Added Discover/TVmaze controls, TMDb score/date display, movie refresh icon, square cards, compact library titles, show schedule controls, and schedule window.
- `templates/_settings_modal.html`, `static/script.js`, `static/movies.js`, `static/style.css`: Added aligned settings, responsive toolbar, movie refresh/edit date fields, episode metadata, cadence UI, schedule-list UI, and equal-height flexible library cards.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date`. TVmaze updates merge by season/episode, preserve watched/file fields, and refresh the show poster/status. Per-show `episode_update_time` is local `HH:MM`; cadence supports daily, weekly weekday, or monthly day; blank disables it. APScheduler checks once per minute with a same-day guard. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. Stars are whole-number 1–5; original scores remain `tmdb_rating`.

# 4. Pending Task

Run an end-to-end browser test at desktop and mobile widths: verify TMDb search/import, movie metadata refresh, release-date sorting, TVmaze updates, and responsive toolbar behavior.
