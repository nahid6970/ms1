# Git Time Machine // CYBERPUNK EDITION

A powerful and visually striking GUI tool for navigating Git history and restoring project states.

## Features

- **Cyberpunk UI**: A high-contrast, themed interface designed for developers.
- **Commit History**: Browse recent commits with details on hash, date, author, and messages.
- **Commit Explorer**: Browse the **entire repository structure** at any specific commit point in a themed tree view.
- **Detailed Diffs**: Interactive diff viewer with syntax highlighting (additions/deletions) and expandable/collapsable file sections.
- **Selective Restoration**: 
    - **Single File Restore**: Right-click any file in the diff view or explorer to restore just that specific file.
    - **Folder Restore**: Right-click any folder in the Commit Explorer to restore the entire folder to that commit's version.
    - **File Timeline**: Right-click any file to see its complete history and restore it to *any* previous state.
    - **Full Restore**: Restore the entire repository directory to a specific commit point.
- **Visual Feedback**: Active versions are highlighted with a **green border** in tables and an **ACTIVE** tag in the diff view.
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
4. **Explore & Restore**:
   - **Browse Repository**: Select a commit and click "EXPLORE COMMIT" to see the full project state at that time.
   - **Restore current version**: Right-click a file and select "⏮️ Restore this File".
   - **Restore from history**: Right-click a file and select "📜 View File Timeline".
   - **Restore Folder**: In the Commit Explorer, right-click a folder and select "📂 Restore Entire Folder".
   - **Full Project Restore**: Select a commit and click "RESTORE SELECTED VERSION" at the bottom.

## Requirements

- Python 3.x
- PyQt6
- Git installed and available in the system PATH.
