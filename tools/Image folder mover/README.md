# Image Folder Mover

A PyQt6 desktop app for quickly reviewing and moving images from source folders into categorized destination folders.

## Features

- **Scan** multiple source folders recursively for images
- **Preview** images with metadata (resolution, file size, source folder)
- **Thumbnail strip** for quick navigation
- **Move targets** — one-click buttons to move the current image to a destination folder
- **Keyboard navigation** — Left/Right arrow keys work regardless of focused widget
- **Settings** — toggle thumbnail visibility, set window height; persisted to JSON

## Requirements

```
pip install PyQt6 Pillow
```

## Usage

```
python image_folder_mover.py
```

1. Add source folders → click **SCAN**
2. Add move targets via **ADD TARGET** in the right panel
3. Browse images with arrow keys or the thumbnail strip
4. Click a target button to move the current image

## Supported Formats

`.jpg` `.jpeg` `.png` `.bmp` `.gif` `.webp` `.tif` `.tiff`

## Settings

Saved to `image_folder_mover_settings.json` next to the script.

| Setting | Description |
|---|---|
| `show_thumbnails` | Show/hide the thumbnail strip |
| `window_height` | Window height in pixels |
| `source_folders` | List of source folders with enabled state |
| `destination_folders` | List of move targets with name, path, and colors |
