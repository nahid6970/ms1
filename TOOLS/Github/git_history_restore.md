# Git Time Machine // CYBERPUNK EDITION

A powerful and visually striking GUI tool for navigating Git history and restoring project states.

## Features

- **Cyberpunk UI**: A high-contrast, themed interface designed for developers.
- **Commit History**: Browse recent commits with details on hash, date, author, and messages.
- **Detailed Diffs**: Interactive diff viewer with syntax highlighting (additions/deletions) and expandable/collapsable file sections.
- **Selective Restoration**: 
    - **Single File Restore**: Right-click any file in the diff view to restore just that specific file to the selected commit's version.
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
5. **Restore**:
   - For a single file: Right-click the file header in the "CHANGES" panel and select "⏮️ Restore this File".
   - For the whole project: Select a commit and click "RESTORE SELECTED VERSION" at the bottom.

## Requirements

- Python 3.x
- PyQt6
- Git installed and available in the system PATH.
