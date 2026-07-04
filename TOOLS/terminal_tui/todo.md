# Task: File viewer panel (mini notepad) from explorer

## What was asked
- Add view button on each file row in the explorer panel
- Clicking opens a viewer with file content (read-only, like mini notepad++)

## Tasks
- [X] Add backend route: GET /api/project/<project>/file-content?path=<rel_path>
- [X] Add file viewer modal HTML (overlay with filename, content, close btn)
- [X] Add view (eye) button to each file row in renderFileTreeItems
- [X] Add openFileViewer(relPath) JS function that fetches and displays content
- [X] Line numbers, monospace, copy button, Escape/click-outside to close
