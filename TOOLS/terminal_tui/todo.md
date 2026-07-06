# Task: Make Debug Script Runner Execute in a New Pane

## Tasks
- [X] Update the `handleRunDebugScript` JavaScript function to use `splitTerminal('tabs', ...)` instead of `socket.emit` so that launching a debug script opens in a new tab, preventing interference with running agent CLIs in the active pane.
