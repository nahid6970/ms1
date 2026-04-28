# MD Launcher

A cyberpunk-themed floating file launcher built with PyQt5. Shows a searchable vertical list of files from configured folders, stays on top, and closes when focus is lost.

## Usage

```
run.bat
```

- **Type** to search/filter files
- **↑ / ↓** to navigate
- **Enter** to open selected file
- **ESC** to close
- **⚙** to open settings

## Settings

| Setting | Description |
|---|---|
| Width / Height | Window size in pixels |
| X / Y | Window position on screen |
| Row height | Height of each file row (px) |
| Gap | Spacing between rows (px) |
| Folders | Folders to scan (recursive) |
| File types | Extensions to show e.g. `.md, .py` — empty = all |
| Font family | File list font |
| Font size | File list font size (pt) |

## Config

Saved to `md_launcher_config.json` next to the script.

```json
{
    "folders": ["C:/@delta/ms1/md"],
    "win_w": 600,
    "win_h": 400,
    "win_x": 660,
    "win_y": 10,
    "row_height": 25,
    "row_spacing": 0,
    "file_types": [".md"],
    "font_family": "Consolas",
    "font_size": 10
}
```

## Requirements

```
pip install PyQt5
```
