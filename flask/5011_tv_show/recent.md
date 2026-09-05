# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, discovery, and episode updates.

# 2. Latest Implementation

- `app.py`, `templates/index.html`, `static/script.js`: TV cards show released-only progress while future episodes remain in the list. Bottom-up Shift-click range marking is restored, with sequential requests preventing JSON save races.
- `app.py`: Added preset TMDb discovery modes for Popular, Top Rated, and monthly release/air-date trending; combined media results are ranked before pagination so high-rated TV shows are not hidden.
- `templates/discover.html`, `static/discover.js`: Added automatic preset loading without a query, remembered discovery mode, and compact labels: Search, Media, and Trending Month.
- `static/style.css`: Moved TV episode progress and movie watched/unwatched badges to the poster top-right; made metadata badges square, fully watched badges light green with black text, and rating stars left-aligned.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date`. TVmaze updates merge by season/episode, preserve watched/file fields, and refresh show poster/status. Per-show `episode_update_time` is local `HH:MM`; cadence supports daily, weekly weekday, or monthly day; blank disables it. APScheduler checks once per minute with a same-day guard. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. Stars are whole-number 1–5; original scores remain `tmdb_rating`.

# 4. Pending Task

Run an end-to-end browser test at desktop/mobile widths for discovery, imports, refresh, sorting, TVmaze updates, and responsive layout.
