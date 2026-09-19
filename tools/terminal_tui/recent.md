# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

# Latest Implementation
* **templates/index.html**:
    * Removed legacy hardcoded buttons (ESC, Ctrl+C, arrows, and scroll buttons) to prioritize custom user-defined shortcuts.
    * Refactored layout logic: custom buttons now render dynamically below the `+` (add) button.
    * Implemented drag-and-drop vertical reordering for custom buttons with immediate client-side re-rendering.
    * Fixed modal closure regression introduced during layout refactoring.

# Critical Context
* Custom buttons and their order are persisted globally in `tui_config.json`.
* `refreshAllPaneCustomButtons()` handles the DOM logic by clearing existing buttons and re-restoring them, ensuring style/order updates are applied without full page reloads.

# Pending Task
Verify persistence of drag-and-drop reordering across sessions and continue with any further UI/UX customizations.