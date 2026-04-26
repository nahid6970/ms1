# Duplicate Image Finder: AI Project Guide

This file is a fast handoff document for future AI/code assistants working on this project.

## Project Purpose

This is a standalone PyQt6 desktop app for finding duplicate or near-duplicate images across one or more folders.

It is designed for these user workflows:

- scan multiple folders at once
- detect exact duplicates and resized/visually similar duplicates
- show only matched images, not unmatched ones
- review duplicate groups visually in horizontal rows
- open, rename, or delete an image from the results
- temporarily disable folders without removing them from saved settings

## Main File

- [duplicate_image_finder.py](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder.py)

There is no multi-file package structure yet. Most logic lives in this single script.

## Dependencies

- `PyQt6`
- `Pillow`

Defined in:

- [requirements.txt](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/requirements.txt)

## Current Project Files

- [duplicate_image_finder.py](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder.py): main app
- [duplicate_image_finder_settings.json](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder_settings.json): persisted user state
- [duplicate_image_finder_icon.svg](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder_icon.svg): generated app icon source
- [duplicate_image_finder_icon.ico](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder_icon.ico): generated Windows icon
- [duplicate_image_finder_check.svg](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder_check.svg): generated yellow checkbox checkmark

## UI Layout

The UI is split into two panels:

- left panel: scan controls
- right panel: match results

### Left Panel

- add folders
- remove selected folders
- clear folders
- restart app
- settings dialog
- folder table with:
  - `USE` checkbox
  - folder path
  - `REMOVE` button
- match ratio slider/spinbox
- primary green scan button
- cancel button

### Right Panel

- only matched image groups are shown
- each result row contains a horizontal list of matching image tiles
- no extra `GROUP` or `LOWEST MATCH` columns are shown

### Status Bar

- scan progress text is shown in the bottom-left status bar
- scan progress bar is shown in the status bar during scans

## Matching Logic

Core scan worker:

- `ScanWorker` in [duplicate_image_finder.py](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder.py:386)

Implementation details:

- file discovery filters by image extension only
- non-image files like `.exe`, `.ps1`, `.txt`, `.zip` are ignored
- images are fingerprinted with:
  - SHA-1 digest for exact-file duplicate grouping
  - perceptual `dhash` for visual similarity
- a BK-tree is used to search near matches efficiently
- union-find merges related matches into groups

Important behavior:

- `100%` means the perceptual hash matched exactly
- same dimensions alone do **not** guarantee `100%`
- resized versions of the same image often score high, but not always exactly `100%`

## Folder Persistence Model

Saved state is defined through:

- `default_settings()` in [duplicate_image_finder.py](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder.py:301)

Current JSON shape:

```json
{
  "thumbnail_size": 140,
  "match_ratio": 92,
  "folders": [
    {
      "path": "C:/Images/FolderA",
      "enabled": true
    }
  ]
}
```

Compatibility note:

- older saved folder lists that were plain strings are still accepted and converted to `{path, enabled}` objects automatically

## Result Tile Behavior

Each image tile currently shows:

- image thumbnail
- filename
- resolution and file size
- match percentage
- parent folder name only, not full path

Color behavior:

- `100.0%` match is shown in green

Interaction behavior:

- double-click opens the image in the system default image viewer
- right-click menu includes:
  - `OPEN IMAGE`
  - `OPEN FOLDER`
  - `RENAME`
  - `DELETE`

Important delete behavior:

- delete is currently permanent via `os.remove(...)`
- there is no recycle bin integration

## Theme / Visual Decisions

This app follows the cyberpunk theme from:

- [THEME_GUIDE.md](C:/@delta/ms1/md/THEME_GUIDE.md)

Notable custom styling:

- primary scan button is green
- folder `USE` checkboxes are real `QCheckBox` widgets, not native table item check states
- checkboxes are square with a yellow check mark SVG

Checkbox reference doc:

- [cyberpunk_checkbox_guide.md](C:/@delta/ms1/md/cyberpunk_checkbox_guide.md)

## Windows Icon / Taskbar Behavior

The app includes explicit Windows taskbar identity handling:

- AppUserModelID is set
- icon is generated as SVG and ICO
- native window icon is pushed after window show

Relevant functions:

- `set_windows_app_id()`
- `make_app_icon()`
- `apply_windows_window_icon()`

If changing icon behavior, remember:

- Windows taskbar icon caching can make changes appear stale until the old process is fully closed

## Settings Dialog

There is a minimal settings dialog.

Current setting:

- thumbnail size

It is intentionally extensible but mostly empty right now.

## Restart Behavior

Restart uses detached relaunch via `QProcess.startDetached(...)`, then quits the current instance.

This is intentional because the earlier in-process restart path was unreliable on Windows.

## Known Constraints / Tradeoffs

1. The project is still a single large script.
2. Delete is permanent.
3. Folder label under tiles uses only the immediate parent folder name.
4. If two different paths end with the same folder name, the tile labels can look identical.
5. The results view is functional, but not yet virtualized for very large result sets.

## Suggested Safe Next Improvements

1. Move permanent delete to Recycle Bin.
2. Hide the right-panel table header for a cleaner results view.
3. Split the script into modules:
   - UI
   - scan engine
   - persistence
   - icon/theme helpers
4. Add tests for settings migration and matching logic.
5. Add explicit tooltip or status text for folder enable/disable semantics.

## Fast Entry Points for Future Work

If you are changing scanning behavior, start at:

- [duplicate_image_finder.py](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder.py:386)

If you are changing result tile UI, start at:

- [duplicate_image_finder.py](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder.py:518)

If you are changing main window layout or controls, start at:

- [duplicate_image_finder.py](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder.py:672)

If you are changing persistence or saved settings, start at:

- [duplicate_image_finder.py](C:/@delta/ms1/TOOLS/Duplicate%20Image%20Finder/duplicate_image_finder.py:301)

