# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, discovery, and episode updates.

# 2. Latest Implementation

- `static/style.css`: Increased `#editShowModal > div` max-width from 450px to 620px for a wider edit modal.
- `app.py`, `static/script.js`: Edit show save now live-updates the card in-place (title, cover image, status badge, rating stars, and `data-*` filter attributes) without a page reload; `edit_show` POST JSON response now returns updated show fields.
- `static/style.css`: Show card hover buttons now have permanent per-button colors (sync → blue `#3b82f6`, episodes-update → emerald `#10b981`, folder → amber `#f59e0b`, list → green `#1db954`, edit → blue `#3b82f6`, sonarr → cyan `#06b6d4`, delete → red `#ef4444`); hover darkens each button slightly; overlay fades in on card hover, hidden by default.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date`. TVmaze updates merge by season/episode, preserve watched/file fields, and refresh show poster/status. Per-show `episode_update_time` is local `HH:MM`; cadence supports daily, weekly weekday, or monthly day; blank disables it. APScheduler checks once per minute. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. Stars are whole-number 1–5; original scores remain `tmdb_rating`.

# 4. Pending Task

Run an end-to-end browser test at desktop/mobile widths for discovery, imports, refresh, sorting, TVmaze updates, and responsive layout.
