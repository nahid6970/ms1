# Task: Integrate Run Script into File Explorer

## Tasks
- [X] Removed the global "Run Debug Script" modal UI and its button in the sidebar.
- [X] Added a new `#explorer-run-modal` which mimics the layout of the `#split-select-modal` with card options.
- [X] Added a "Run" icon (play button) next to the "View" icon (eye button) for each file in the workspace file explorer.
- [X] Added JavaScript logic so clicking the Run icon opens the new modal, and selecting an execution card mode correctly runs the script in a new terminal tab based on the file extension.
