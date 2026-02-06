# Git Time Machine // CYBERPUNK EDITION

A powerful and visually striking GUI tool for navigating Git history and restoring project states.

## Features

- **Cyberpunk UI**: A high-contrast, themed interface designed for developers.
- **Commit History**: Browse recent commits with details on hash, date, author, and messages.
- **Detailed Diffs**: Interactive diff viewer with syntax highlighting (additions/deletions) and expandable/collapsable file sections.
- **Selective Restoration**: 
    - **Single File Restore**: Right-click any file in the diff view to restore just that specific file to the selected commit's version.
    - **File Timeline**: Right-click any file in the diff view to see its complete history and restore it to *any* previous state, not just the currently selected commit.
    - **Full Restore**: Restore the entire repository directory to a specific commit point.
- **Editor Integration**: Open files directly in your preferred editor from the diff view.
- **Tree Browser**: Navigate your local directory structure to quickly switch between different Git repositories.
- **Customizable**: Adjust commit limits, window dimensions, and panel split ratios via integrated settings.

## Usage

1. Run the script:
   ```bash
   python git_history_restore.py
   ```
2. **Select Directory**: Use the "BROWSE" or "TREE VIEW" buttons to point to a Git repository.
3. **Load Commits**: Click "LOAD COMMITS" to fetch the history.
4. **View Changes**: Click any commit in the table to see the files changed and their specific diffs.
5. **Restore Options**:
   - **Restore current version**: Right-click a file and select "⏮️ Restore this File" to sync it with the currently selected commit.
   - **Restore from history**: Right-click a file and select "📜 View File Timeline" to browse all versions of that specific file and pick one to restore.
   - **Full Project Restore**: Select a commit and click "RESTORE SELECTED VERSION" at the bottom to revert the entire directory.

## Requirements

- Python 3.x
- PyQt6
- Git installed and available in the system PATH.