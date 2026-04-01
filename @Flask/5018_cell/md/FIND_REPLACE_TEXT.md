# Find & Replace Text Feature

**Location:** F3 Quick Formatter → 🔍➡️ SVG Button

Simple text search and replace across an entire cell content.

---

## Overview

The Find & Replace Text feature allows you to perform literal text replacement within a cell. This is useful for correcting typos, renaming items, or batch-updating specific words without affecting the surrounding markdown syntax (unless you explicitly search for it).

## How to Use

1. Click on any cell to select it.
2. Press **F3** to open the Quick Formatter.
3. Click the **🔍➡️ Find & Replace Text** button.
4. In the modal that appears:
    - **Find Text:** Enter the text you want to search for.
    - **Replace With:** Enter the text you want to replace it with.
    - **Case Sensitive:** Check this if you want the search to be case-sensitive.
5. Review the **Preview** section to see how many occurrences were found and an example of the first replacement.
6. Click **Replace All** to apply the changes to the cell.

## Features

- **Real-time Preview:** See the number of matches and a "before/after" snippet as you type.
- **Case Sensitivity Toggle:** Option to match exact casing or ignore it.
- **Regex-Safe:** Special characters in the "Find Text" box are automatically escaped so they are treated as literal text.
- **Undo Support:** Since this updates the cell content and triggers an `input` event, it integrates with the existing undo/redo system (if applicable) and ensures the sheet's "unsaved changes" state is updated.

---

## Related Features

- **F3 Quick Formatter:** Main formatting interface
- **🔄 Find & Replace Syntax:** Replace markdown patterns while preserving content
- **🎯 Select All Matching:** Multi-cursor editing for occurrences
