# AI_CONTEXT — Code Merger

## What it is
A PyQt6 desktop GUI tool that:
1. **PREP tab** — packages local source files into a structured prompt (with format guide) ready to paste into any web AI (Gemini, ChatGPT, AI Studio, etc.)
2. **MERGE tab** — parses the AI's response and applies changes back to local files on disk

## Entry Point
```
python merge_gui.py
```

## File Structure
```
code_merger/
├── merge_gui.py           # Single-file app — all GUI + logic
├── PROMPT_GUIDE.md        # Format rules embedded in every generated prompt
├── session.json           # Auto-saved PREP tab file list (restored on startup)
├── recent_projects.json   # Recently used project root directories
├── demo_project/          # Demo: simple calculator (Python)
└── demo_project2/         # Demo: white-themed Note Taker GUI (for theme-change testing)
```

## Architecture
Everything is in `merge_gui.py`:
- **Top-level functions:** `parse_ai_response()`, `apply_changes()`, `_normalize()`, `load_recent()`, `save_recent()`, `add_recent()`
- **Classes:** `RecentPopup`, `PrepTab`, `MergeTab`, `MainWindow`
- **Theme:** Cyberpunk palette (`CP_BG`, `CP_CYAN`, `CP_YELLOW`, etc.) applied via single `THEME` QSS string on `MainWindow`

## Change Format
The AI responds using `@@FILE` / `@@MODE` / `@@TO` / `@@FROM` / `@@END` markers.
Supported modes: `replace_file`, `replace_block`, `insert_after`, `delete_block`.
Parser normalizes inline tokens (Gemini collapses newlines) and strips markdown fences before parsing.

## Critical Invariants
- `_HERE = os.path.dirname(os.path.abspath(__file__))` — all data files use this as base, never cwd
- `add_recent()` normalizes paths with `os.path.normpath()` to prevent slash-direction duplicates
- Session restore skips files that no longer exist on disk
- Backups created as `filename.bak_YYYYMMDD_HHMMSS` (toggled via checkbox)

## What Not to Break
- `_normalize()` must run before any regex parsing — it fixes both inline tokens and inline content after `@@TO:`
- `set_root()` in MergeTab also calls `add_recent()` — don't bypass it
- `_load_session()` is called after `_build()` in PrepTab init — order matters

## Preferred Workflow for New Features
1. Add UI elements in the relevant tab's `_build()` method
2. Add logic as methods on the same tab class
3. Cross-tab communication goes through `MainWindow._build()` via callbacks
4. Keep all file paths anchored to `_HERE`
