# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, and discovery.

# 2. Latest Implementation

- `app.py`: Added TMDb helpers, paged search/import APIs, duplicate detection, rating conversion, and TVmaze episode/air-date merging.
- `templates/discover.html`: Added unified discovery, per-page count, type/sort selectors, and Previous/Next controls.
- `static/discover.js`: Added search rendering, local add actions, sorting, checkmarks, pagination, and remembered preferences.
- `templates/index.html`: Added Discover and TVmaze episode-update buttons plus original TMDb score display.
- `templates/movies.html`: Added Discover button and original TMDb score display.
- `templates/_settings_modal.html`: Added the masked TMDb API-key field.
- `static/script.js`: Added TMDb key loading/saving and TVmaze episode-update feedback.
- `static/style.css`: Added compact controls, sorting layout, added-state, TMDb score styling, card alignment, and update-button styling.

# 3. Critical Context

TMDb is metadata-only; adding content does not call Sonarr/Radarr. TVmaze is free/no-key and supplies episode schedules; updates merge by season/episode number while preserving watched/file fields. TMDb key is stored in `C:\@delta\db\5011_tv_show\settings.json`; requests run server-side. Discover remembers type, sort, and per-page count (max 100). App stars are whole-number 1–5; imported scores are preserved as `tmdb_rating`.

# 4. Pending Task

Run an end-to-end browser test: save the TMDb key, search both media types, add one movie and one show, verify duplicate handling, and confirm both appear in their library pages.
