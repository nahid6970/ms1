# Problems & Fixes Log

---

## [2026-06-19 15:10] — Parser Failed on Gemini Inline Format

**Problem:** Pasting AI response from Gemini gave "No valid change blocks found" even though the response looked correct.

**Root Cause:** Gemini's "Copy as text" collapses the response onto single lines — `@@FILE: x.py @@MODE: replace_file @@TO: def foo()...` all on one line. The parser used `split('\n')` and regex anchored to line starts, so tokens were never found.

**Solution:** Added `_normalize()` to run before parsing:
1. Inserts `\n` before any `@@TOKEN` not already at line start
2. Moves inline content after `@@TO:` / `@@FROM:` to the next line

**Files Modified:** `merge_gui.py`

---

## [2026-06-19 15:18] — Code Indentation Lost After Merge

**Problem:** Merged files had all code on single lines — broken Python.

**Root Cause:** "Copy as text" from Gemini collapses newlines within code blocks, not just the `@@` tokens. Indentation spaces are preserved but line breaks are not.

**Solution:** Switched recommended copy method to **"Copy as markdown"**. Added markdown fence stripping (```` ``` ````) in `_normalize()`. Markdown copy preserves all newlines and indentation correctly.

**Files Modified:** `merge_gui.py`, `PROMPT_GUIDE.md`

---

## [2026-06-19 15:55] — Data Files Not Found When Launched from Different Directory

**Problem:** `session.json` and `recent_projects.json` not found when running the script from a directory other than `code_merger/`.

**Root Cause:** `os.path.dirname(__file__)` returns a relative path when the script is invoked with a relative path, resolving against cwd rather than the script's actual location.

**Solution:** Changed to `os.path.dirname(os.path.abspath(__file__))` stored in `_HERE` constant.

**Files Modified:** `merge_gui.py`

---

## [2026-06-19 16:00] — Duplicate Entries in Recent Projects List

**Problem:** Same directory appeared twice in the recent projects popup (e.g. `C:/@delta/ms1/TOOLS/ENV` shown twice).

**Root Cause:** Paths stored with different slash directions (`/` vs `\`) — string equality check treated them as different entries.

**Solution:** Applied `os.path.normpath()` to all paths in `add_recent()` and `load_recent()` before comparison. Also added deduplication pass in `load_recent()` to clean up existing corrupt entries.

**Files Modified:** `merge_gui.py`
