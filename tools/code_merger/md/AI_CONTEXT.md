# AI_CONTEXT — Code Merger

## What it is
A PyQt6 desktop GUI tool that:
1. **PREP tab** — packages local source files into a structured prompt ready to paste into any web AI.
2. **MERGE tab** — parses the AI's response and applies changes back to local files on disk.
3. **COMMAND tab** — integrated shell runner for executing commands in the project directory.

## Entry Point
python merge_gui.py

## File Structure
code_merger/
├── merge_gui.py           # Single-file app — all GUI + logic
├── PROMPT_GUIDE.md        # Format rules embedded in every generated prompt
├── settings.json          # Persistent settings, projects, and active session state
└── md/
    └── AI_CONTEXT.md      # This file

## Key Features & Components
- **Projects Sidebar**: Pinned projects with contiguous numeric pin indices, custom icons (Emoji/SVG), category tags with dynamic dropdown selectors, and elided path displays.
- **Source Files Panel**: File toggling, Full/Outline mode selection, minification, drag-and-drop support, token estimation, and sorting.
- **Diff Preview Dialog**: Visual unified diff preview with selective block application.
- **Matching Engines**: Exact Match and conservative Whitespace-Tolerant Match. The tolerant matcher accepts harmless line formatting differences but rejects ambiguous or low-confidence matches.

## Critical Invariants
- `_HERE = os.path.dirname(os.path.abspath(__file__))` — all data files use this as base.
- `add_recent()` normalizes paths with `os.path.normpath()` to prevent duplicate entries.
- Backups created as `filename.bak_YYYYMMDD_HHMMSS`.
