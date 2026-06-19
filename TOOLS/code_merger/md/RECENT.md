# Recent Development Log
All sessions recorded here — no archiving, full history in one place.

---

## [2026-06-19 14:52] — Initial Build

**What We Accomplished:**
- Designed the tool concept: PREP tab (local → AI) + MERGE tab (AI → local)
- Created `PROMPT_GUIDE.md` with `@@FILE` / `@@MODE` / `@@END` format spec
- Built `merge_gui.py` — full PyQt6 GUI with Cyberpunk theme from `THEME_GUIDE.md`
- PREP tab: add files / add dir, task input, generate prompt, copy to clipboard
- MERGE tab: project root, paste AI response, parse + apply changes
- Merge logic supports 4 modes: `replace_file`, `replace_block`, `insert_after`, `delete_block`
- Auto-backup as `.bak_YYYYMMDD_HHMMSS` with checkbox toggle
- RESTART button via `os.execv`

**Files Created:**
- `merge_gui.py`, `PROMPT_GUIDE.md`, `README.md`
- `demo_project/calculator.py`, `demo_project/main.py`

---

## [2026-06-19 15:00] — Multi-block Support & UX Fixes

**What We Accomplished:**
- Added **APPEND FROM CLIPBOARD** button in Merge tab — accumulate multiple partial AI responses before parsing
- Added `demo_project2/app.py` — white-themed Note Taker GUI for testing theme-change workflow
- Auto-populate Merge tab Project Root from PREP tab file selection (common parent dir)
- Moved task/instructions to **end** of generated prompt (better AI attention)
- PROMPT_GUIDE now instructs AI to always wrap response in markdown ` ``` ` fences
- Section header changed from `## MY REQUEST` to `## NOW DO THIS`
- Empty task box → no section added to prompt (clean output)

**Files Modified:**
- `merge_gui.py`, `PROMPT_GUIDE.md`

---

## [2026-06-19 15:10] — Parser Robustness

**What We Accomplished:**
- Fixed parser failing on Gemini's inline format (all `@@` tokens on one line)
- Added `_normalize()`: inserts newlines before `@@` tokens + moves inline content after `@@TO:` to next line
- Added markdown fence stripping in `_normalize()` — handles "Copy as markdown" output
- Confirmed "Copy as markdown" is the correct copy method (preserves indentation)

**Files Modified:**
- `merge_gui.py`

---

## [2026-06-19 15:55] — Session Persistence & Recent Projects

**What We Accomplished:**
- PREP tab file list now persists to `session.json` — restored on next startup
- Files no longer on disk are silently skipped on restore
- Added recent projects feature: directories saved to `recent_projects.json` (max 8)
- `🕘 RECENT` button in PREP tab opens `RecentPopup` — click path to load, ✕ to remove
- Path deduplication via `os.path.normpath()` — fixes slash-direction duplicates
- `load_recent()` deduplicates existing entries on read
- All data files anchored to `os.path.abspath(__file__)` — works from any working directory

**Files Modified:**
- `merge_gui.py`

*Next session: consider adding file removal (right-click or select + delete key) from the PREP tab source list*
