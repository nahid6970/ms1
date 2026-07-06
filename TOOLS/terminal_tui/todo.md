# Task: Add Frontend Framework Quick Initializer

## Tasks
- [X] Added a file deletion API endpoint `POST /api/project/<project>/file-delete` in `app.py`.
- [X] Added a Delete icon button (trash icon) next to the View icon in the file explorer in `index.html`.
- [X] Added `deleteExplorerFile()` JS function which prompts for confirmation and then calls the backend to delete the file and refreshes the tree.
- [X] Removed the extra "Add current command to bookmark" header button.
- [X] Added a fixed bottom input row `bookmark-add-row` inside the main bookmark custom dropdown content.
- [X] Updated the backend `/api/projects/<project>/bookmarks` POST endpoint to accept and save a custom name parameter.
- [X] Added `addBookmarkFromInput()` JS function to handle inline bookmark creation, supporting `label::command` formatting.
- [X] Updated `toggleBookmarkDropdown` to prefill the inline bookmark input field with the active command from the terminal.
- [X] Fixed the close-on-outside-click handler for the bookmark dropdown by checking for the `flex` display value.
- [X] Added a `+` button in the header (after bookmarks) styled like the old add button for framework initialization.
- [X] Added a custom framework selection modal `framework-select-modal` supporting React, Vue 3, Svelte, AngularJS, and Tailwind HTML templates.
- [X] Implemented the backend API endpoint `/api/project/<project>/init-framework` in `app.py` to create the essential starter files for each framework.
- [X] Linked the modal selection to the backend endpoint and set up the explorer tree to auto-refresh on successful initialization.
