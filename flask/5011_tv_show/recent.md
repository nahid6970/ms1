# 1. Project DNA (Permanent)

Flask/Python app with server-rendered HTML/Jinja templates, vanilla JavaScript, CSS, and JSON-backed local catalogs. Its goal is to manage and display a personal TV-show and movie library, including watched state, episode/file scans, metadata, and discovery.

# 2. Latest Implementation

- `app.py`: Added TMDb request helpers, `/discover`, TMDb search, local movie/show import APIs, and duplicate detection by TMDb ID or normalized title/year.
- `templates/discover.html`: Added the unified movie/TV discovery page.
- `static/discover.js`: Added TMDb search rendering, local add actions, result sorting, and `Already Added` checkmarks.
- `templates/index.html`, `templates/movies.html`: Added Discover buttons to both library toolbars.
- `templates/_settings_modal.html`: Added the masked TMDb API-key field.
- `static/script.js`: Added TMDb key loading and saving through settings.
- `static/style.css`: Added TMDb settings styling, compact discovery controls, result sorting layout, and added-state styling.

# 3. Critical Context

TMDb is used only for metadata; adding content does not call Sonarr/Radarr. The key is stored in `C:\@delta\db\5011_tv_show\settings.json` as `tmdb_api_key`, and all TMDb requests run server-side. Movies save to `movies.json`; shows save to `data.json`; catalogs are checked separately. Duplicate matching uses `tmdb_id`, then normalized title/year for manually added records. Existing JSON schemas and Sonarr/Radarr sync behavior must remain compatible.

# 4. Pending Task

Run an end-to-end browser test: save the TMDb key, search both media types, add one movie and one show, verify duplicate handling, and confirm both appear in their library pages.
