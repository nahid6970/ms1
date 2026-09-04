# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, and discovery.

# 2. Latest Implementation

- `app.py`: Added TMDb helpers, `/discover`, search/import APIs, duplicate detection, and whole-number TMDb 0–10 to app 1–5 rating conversion with legacy migration.
- `templates/discover.html`: Added the unified movie/TV discovery page.
- `static/discover.js`: Added search rendering, local add actions, sorting, and `Already Added` checkmarks.
- `templates/index.html`, `templates/movies.html`: Added Discover buttons and original TMDb score display.
- `templates/_settings_modal.html`: Added the masked TMDb API-key field.
- `static/script.js`: Added TMDb key loading and saving through settings.
- `static/style.css`: Added compact discovery controls, sorting layout, added-state, and TMDb score styling.

# 3. Critical Context

TMDb is metadata-only; adding content does not call Sonarr/Radarr. The key is stored in `C:\@delta\db\5011_tv_show\settings.json` as `tmdb_api_key`; requests run server-side. Movies use `movies.json`, shows use `data.json`, and catalogs are checked separately. Duplicate matching uses `tmdb_id`, then normalized title/year. App stars are whole-number 1–5; imported scores are rounded from 0–10 and preserved as `tmdb_rating`.

# 4. Pending Task

Run an end-to-end browser test: save the TMDb key, search both media types, add one movie and one show, verify duplicate handling, and confirm both appear in their library pages.
