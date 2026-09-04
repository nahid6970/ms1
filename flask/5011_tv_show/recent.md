# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, and discovery.

# 2. Latest Implementation

- `app.py`: Added TMDb search/import with movie release dates, movie metadata refresh, duplicate detection, rating conversion, TVmaze episode/air-date merging, and reliable library sorting.
- `templates/discover.html`, `static/discover.js`: Added unified discovery, type/sort/count controls, pagination, remembered preferences, and duplicate checkmarks.
- `templates/index.html`, `templates/movies.html`: Added Discover/TVmaze controls and TMDb score display; removed the conflicting home-page redirect.
- `templates/_settings_modal.html`, `static/script.js`, `static/movies.js`, `static/style.css`: Added TMDb settings, aligned General controls, movie refresh action, episode metadata, and modern card/control styling.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date` for same-year chronological sorting. TVmaze is free/no-key; episode updates merge by season/episode and preserve watched/file fields. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. App stars are whole-number 1–5; original scores remain `tmdb_rating`. Library defaults are server-side; “Last Episode” scans all episodes.

# 4. Pending Task

Run an end-to-end browser test: save the TMDb key, search both media types, add one movie and one show, verify duplicate handling, and confirm both appear in their library pages.
