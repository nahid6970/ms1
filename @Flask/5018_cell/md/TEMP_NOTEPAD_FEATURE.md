# Temporary Notepad Feature Specification

## Overview
The **Temporary Notepad** is a floating utility tool that provides a quick, persistent scratchpad for users. It allows for jotting down notes, copying text between cells, or drafting content without modifying the actual spreadsheet data.

## Core Features

### 1. Independent Storage
*   **Persistence**: Content is saved to `localStorage` under the key `temp_notepad_content`.
*   **Isolation**: The notepad's data is completely separate from the main `tableData` and `data.json`. It does not auto-save to the backend and survives page refreshes.

### 2. UI/UX Design
*   **Access**: Toggled via a new "Memo" button (📝) in the sheet controls toolbar, located next to the Bookmark button.
*   **Popup**:
    *   **Position**: Fixed positioning (right-aligned, vertically centered).
    *   **Dimensions**: Slightly wider (400px) than the Bookmark popup to accommodate longer notes.
    *   **Styling**: Matches the application's aesthetic with a clean header and a resizeable textarea.
*   **Interaction**:
    *   **Auto-Focus**: Textarea focuses automatically 50ms after opening.
    *   **Click-Outside Close**: Closes automatically when clicking anywhere outside the popup or its toggle button.
    *   **Exclusive Open**: Opening the Notepad automatically closes the Bookmark popup (and vice versa) to prevent UI clutter.

### 3. Technical Implementation
*   **File**: Logic resides in `static/temp_notepad.js`.
*   **Styles**: Specific styles defined in `static/style.css` under `.temp-notepad-popup`.
*   **Dependencies**: Requires `static/style.css` for shared popup styles (`.recent-edits-popup`).

## Future Improvements
*   **Rich Text**: Support for basic markdown rendering within the notepad.
*   **Export**: Button to copy all content or export to a text file.
*   **Multiple Pages**: Support for multiple "pages" or tabs within the notepad.
