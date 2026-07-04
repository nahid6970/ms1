# Task: Drag-to-reorder bookmarks

User wants to drag bookmark rows to reorder them.

## Tasks
- [X] Add drag-and-drop attributes to bookmark rows in renderBookmarkDropdown/updateBookmarksDropdown
- [X] Add drag event handlers (dragstart, dragover, drop) to reorder bookmarks
- [X] Call existing /api/projects/<project>/bookmarks/<index>/edit with newIndex to persist order
- [X] Add visual drag handle icon to each owned bookmark row
