# 1. Project DNA (Permanent)

FCC Fixer is a dependency-light PyQt6 desktop GUI with a modular diagnostic/action layout. Its goal is to safely diagnose and repair common Free Claude Code (FCC) integration issues with Claude Code and Codex CLI without reinstalling either client.

# 2. Latest Implementation

- `main.py` — Added FCC health/path/model diagnostics; safe Claude Router conflict repair with timestamped backup; Codex FCC override cleanup and reversible cache quarantine; FCC server launcher; copy-command controls; general-first layout with initially unselected CODEX/CLAUDE tabs; active-tab highlighting; compact `X` close buttons.
- `README.md` — Documented usage, recovery workflow, Codex repair behavior, full-auto commands, and tab layout.
- `.gitignore` — Added Python cache, virtual environment, logs, build, and local-secret exclusions.

# 3. Critical Context

Use PyQt6 already available in the environment; do not add packages. FCC paths are derived from `Path.home()` and use `%USERPROFILE%\\.fcc`, `.claude`, and `.codex`. Claude repair removes only stale `apiKeyHelper` and old Router endpoint keys after backing up settings. Codex repair removes only recognizable FCC provider/catalog/Gemini overrides; cache quarantine moves `models_cache.json` instead of deleting it. Client tab pages start hidden because Qt tab widgets cannot have an unselected tab.

# 4. Pending Task

Launch the GUI and perform visual QA of the new CODEX/CLAUDE tab layout and compact close buttons on Windows.
