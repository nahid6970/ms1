# 1. Project DNA (Permanent)

Flask/Python app with server-rendered HTML/Jinja templates, vanilla JavaScript, CSS, and JSON-backed local catalogs. Its goal is to manage and display a personal TV-show and movie library, including watched state, episode/file scans, metadata, and discovery.

# 2. Latest Implementation

- `app.py`: Added TMDb request helpers, `/discover`, TMDb search, and local movie/show import APIs with duplicate prevention and metadata persistence.
- `templates/discover.html`: Added the unified movie/TV discovery page.
- `static/discover.js`: Added TMDb search rendering and local add actions.
- `templates/index.html`: Added the Discover button after Add Show.
- `templates/_settings_modal.html`: Added the masked TMDb API-key field.
- `static/script.js`: Added TMDb key loading and saving through settings.
- `static/style.css`: Added TMDb settings styling and discovery-page layout.

# 3. Critical Context

TMDb is used only for metadata; adding content does not call Sonarr/Radarr. The key is stored in `C:\@delta\db\5011_tv_show\settings.json` as `tmdb_api_key`, and all TMDb requests run server-side. Movies save to `movies.json`; shows save to `data.json`; `tmdb_id` prevents duplicates. Existing JSON schemas and Sonarr/Radarr sync behavior must remain compatible.

# 4. Pending Task

Run an end-to-end browser test: save the TMDb key, search both media types, add one movie and one show, verify duplicate handling, and confirm both appear in their library pages.
