# 1. Project DNA (Permanent)

Flask/Python app with server-rendered Jinja templates, vanilla JavaScript, CSS, and JSON-backed catalogs. It manages a personal TV-show and movie library with watched state, file scans, metadata, discovery, and episode updates.

# 2. Latest Implementation

- `app.py`, `templates/index.html`, `static/script.js`, `static/style.css`: Edit modal status checkbox is now locked (disabled) when the scheduler is active for a show, preventing the scheduler from overwriting a manually-set status; lock icon and tooltip added via CSS/JS.
- `app.py`, `static/script.js`, `static/style.css`: Added per-show "Clear Stats" button and a "Clear All" button in the Scheduled Updates modal to reset last-run result and timestamp for one or all shows.
- `app.py`, `static/script.js`, `static/style.css`: Improved scheduler — grace window skips update if show was manually refreshed recently; manual "Run Now" button triggers immediate update for a show; last run result (success/fail/skipped) displayed in the modal.
- `app.py`, `static/script.js`: Edit show form now submits via `fetch` instead of a full page reload, preserving the client-side search filter state after saving.
- `templates/index.html`, `templates/movies.html`: Discover is now a nav tab alongside Shows and Movies on all three pages; the toolbar icon button for Discover is removed.
- `static/script.js`: Blue dot beside each episode in the episodes modal now copies the full label (e.g. "Jujutsu Kaisen S03E05 Episode Title") to clipboard using `navigator.clipboard` with `execCommand` fallback; dot flashes green on success.

# 3. Critical Context

TMDb is metadata-only; imports do not call Sonarr/Radarr. Movie imports retain full TMDb `release_date`. TVmaze updates merge by season/episode, preserve watched/file fields, and refresh show poster/status. Per-show `episode_update_time` is local `HH:MM`; cadence supports daily, weekly weekday, or monthly day; blank disables it. APScheduler checks once per minute. The TMDb key is in `C:\@delta\db\5011_tv_show\settings.json`; requests are server-side. Stars are whole-number 1–5; original scores remain `tmdb_rating`.

# 4. Pending Task

Run an end-to-end browser test at desktop/mobile widths for discovery, imports, refresh, sorting, TVmaze updates, and responsive layout.
