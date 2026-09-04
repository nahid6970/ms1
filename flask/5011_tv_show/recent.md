# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, and discovery.

# 2. Latest Implementation

- `app.py`: Added TMDb search/import, movie release dates, metadata refresh/editing, duplicate detection, rating conversion, TVmaze episode/air-date merging, and reliable library sorting.
- `templates/discover.html`, `static/discover.js`: Added unified discovery, type/sort/count controls, pagination, remembered preferences, and duplicate checkmarks.
- `templates/index.html`, `templates/movies.html`: Added Discover/TVmaze controls, TMDb score/date display, movie metadata refresh icon, and square movie cards.
- `templates/_settings_modal.html`, `static/script.js`, `static/movies.js`, `static/style.css`: Added aligned settings, responsive toolbar wrapping, movie refresh/edit date fields, episode metadata, and modern controls.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date` for same-year chronological sorting. TVmaze is free/no-key; episode updates merge by season/episode and preserve watched/file fields. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. App stars are whole-number 1–5; original scores remain `tmdb_rating`. Library defaults are server-side; “Last Episode” scans all episodes.

# 4. Pending Task

Run an end-to-end browser test at desktop and mobile widths: verify TMDb search/import, movie metadata refresh, release-date sorting, TVmaze updates, and responsive toolbar behavior.
