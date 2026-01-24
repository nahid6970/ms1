# Project Developer Guide & Documentation

This document serves as a high-level guide for understanding the project's architecture and the "Rule of 6" for consistent feature implementation. Detailed feature specifications are located in the `md/` directory.

## 🚨 IMPORTANT: Always Check Recent Work First
**Before starting any development session, read the recent work log to understand the current project state:**

#[[file:md/RECENT.md]]

This file contains the last 5 development sessions with timestamps, current status, known issues, and next steps. It provides essential context for continuing development work efficiently.

## Project Overview
This is a Flask-based web application providing a dynamic, markdown-enabled spreadsheet interface (`5018_cell`).

### Key Files
- **`app.py`**: Flask backend handling API endpoints for data persistence.
- **`static/script.js`**: Core logic engine (~11k+ lines). Handles rendering, state, and parsing.
- **`static/style.css`**: Application styling and theme definitions.
- **`templates/index.html`**: UI shell and modal structures.
- **`export_static.py`**: Standalone HTML export generator.

## 📋 Problems & Fixes Log
When encountering and fixing bugs or issues, document them in **`md/PROBLEMS_AND_FIXES.md`**.

### Purpose
- Track historical issues and their solutions
- Help AI assistants understand past problems and fixes
- Identify if old fixes might conflict with new features
- Provide context for debugging similar issues

### Format
Each entry should include:
```markdown
## [Date] - Brief Problem Title

**Problem:** Description of the issue

**Root Cause:** What was causing it

**Solution:** How it was fixed

**Files Modified:** List of changed files

**Related Issues:** Any connected problems or features
```

### When to Update
- After fixing any non-trivial bug
- When a fix involves multiple files or complex logic
- When a fix might affect other features
- When reverting or modifying a previous fix

See **[Problems & Fixes Log](md/PROBLEMS_AND_FIXES.md)** for the full history.

## 🔄 Recent Work Log (CRITICAL FOR SESSION CONTINUITY)
**ALWAYS maintain `md/RECENT.md`** to track recent development sessions. This file is **automatically referenced** at the top of this guide using `#[[file:md/RECENT.md]]` to ensure it's read first.

### Purpose
- **Session Continuity**: Provide immediate context when resuming development
- **AI Assistant Context**: Help AI understand current project state without re-explanation
- **Progress Tracking**: Track what was accomplished in recent sessions
- **Issue Awareness**: Identify current problems and their status
- **Next Steps Planning**: Clear direction for continuing development

### Format (Keep Last 5 Sessions)
```markdown
# Recent Development Log

## [YYYY-MM-DD HH:MM] - Session Summary

**What We Accomplished:**
- Feature/fix descriptions with timestamps

**Files Modified:**
- List of changed files with brief descriptions

**Next Steps:**
- Planned improvements or fixes

**Current Status:**
- Working features
- Known issues

**Time Spent:** X hours
```

### Critical Rules
- **Always include timestamps** in HH:MM format for each session
- **Keep only the last 5 sessions** in RECENT.md for quick reference
- **Archive older sessions** by moving them to `md/ARCHIVE_RECENT.md` (don't delete!)
- **Update at the END of each session** with accurate time tracking
- **Include specific file paths** and what was changed in each
- **List known issues** and their current status
- **Reference this file** at the top of DEVELOPER_GUIDE.md using `#[[file:md/RECENT.md]]`

### Archiving Process (When you have 6+ sessions)
1. **Create/Update `md/ARCHIVE_RECENT.md`** if it doesn't exist
2. **Move the oldest session** from RECENT.md to the top of ARCHIVE_RECENT.md
3. **Keep the format** but add "ARCHIVED" prefix to session titles
4. **Don't delete anything** - maintain complete development history
5. **RECENT.md stays focused** on last 5 sessions for quick context

### When to Update
- **End of every development session** (mandatory)
- After completing major features
- When encountering new issues
- Before taking breaks from the project

**The Recent.md file is automatically included when reading this developer guide, ensuring session continuity.**

## 🚀 Git Commit Workflow (CRITICAL)
**IMPORTANT:** Follow this exact workflow when committing changes to maintain proper documentation and version control.

### Commit Command
- **Only commit when explicitly instructed** - Wait for the command "commit"
- **Never auto-commit** - Always wait for explicit instruction

### Pre-Commit Process (MANDATORY)
1. **Wait for "commit" command**: Documentation files (like `md/RECENT.md`, `md/PROBLEMS_AND_FIXES.md`) must ONLY be updated when the user explicitly says "commit". Do NOT update them during active development steps.
2. **Update documentation files FIRST** (after the "commit" command):
   - `md/RECENT.md` - Add/update current session details with timestamps
   - `md/PROBLEMS_AND_FIXES.md` - Document any bugs fixed or issues resolved
   - `md/KEYBOARD_SHORTCUTS.md` - Update if shortcuts changed
   - Any other relevant feature documentation files
   - `DEVELOPER_GUIDE.md` - Update if architecture changed

2. **Verify all changes are documented** before proceeding to Git operations

### Git Operations Sequence
```bash
git add .
git commit -m "emoji one-line message"
git push
```

### Commit Message Format
- **One line only** - No multi-line commit messages
- **Start with appropriate emoji**:
  - ✅ Bug fixes and issue resolution
  - ⚠️ Known issues or warnings
  - 🎯 New features and implementations
  - 📝 Documentation updates
  - 🔧 Code improvements and refactoring
  - 🧹 Code cleanup and removal
  - 🚀 Performance improvements
  - 🎨 UI/UX improvements

### Example Workflow
```
User: "commit"
AI: 
1. Updates md/RECENT.md with session details
2. Updates md/PROBLEMS_AND_FIXES.md if bugs were fixed
3. Updates other relevant documentation
4. git add .
5. git commit -m "✅ Fixed F3 formatter contentEditable support"
6. git push
```

### Critical Rules
- **Documentation first, Git second** - Always update docs before committing
- **Wait for "commit" command** - Never commit automatically
- **One-line messages** - Keep commit messages concise and clear
- **Appropriate emojis** - Use emojis to categorize the type of change
- **Complete workflow** - Always add, commit, and push in sequence

## ⚡ Critical Implementation Rule: "The Rule of 6"
When adding new **Markdown Syntax** or **Cell Formatting**, you **MUST** update these 6 locations:

1.  **Parsing Logic (`static/script.js`):** Add regex to `parseMarkdownInline()` and `oldParseMarkdownBody()`.
2.  **Detection (`static/script.js`):** Update `checkHasMarkdown(value)`.
3.  **Stripping (`static/script.js`):** Update `stripMarkdown(text)` to remove syntax for search/sort.
4.  **Static Detection (`export_static.py`):** Update `hasMarkdown` in the rendering logic.
5.  **Static Parsing (`export_static.py`):** Add Python-escaped regex to both `parseMarkdown` functions.
6.  **User Guide (`templates/index.html`):** Add examples to the "Markdown Formatting Guide" modal.

### Core Architectural Concepts

### View Modes (Critical)
The application operates in two distinct view modes, toggled by the **Page Icon (📄)** in the toolbar (`toggleMarkdownPreview()`):

1.  **Raw Mode (Preview Disabled)**:
    *   **Visual**: Displays the raw `<input>` or `<textarea>` directly.
    *   **Content**: Shows raw syntax symbols (e.g., `**bold**`, `\(math\)`) as plain text.
    *   **Behavior**: No HTML rendering or overlays. Fast and direct.
    *   **Use Case**: Deep editing, debugging syntax, or bulk text improvements.

2.  **Markdown Mode (Preview Enabled)**:
    *   **Visual**: Renders a **Preview Overlay** (`.markdown-preview`) *on top* of the text input.
    *   **Content**: Shows processed HTML (Bold, Colors, Math, Tables).
    *   **Behavior**: The underlying input becomes transparent. Typing happens "through" the preview.
    *   **Use Case**: Reading, presenting, and "Rich-Text" style editing.

### Edit Mode Architecture (ContentEditable)
When a cell is focused for editing in Markdown Mode, it transitions to **Edit Mode** using `contentEditable`:

1.  **Preview to Edit Transition**:
    *   On focus, the preview div becomes `contentEditable="true"` and adds class `editing`.
    *   Content switches from `parseMarkdown()` (hidden syntax) to `highlightSyntax()` (visible syntax with styling).
    *   Syntax markers like `**`, `@@`, `##` are shown with `.syn-marker` class (dimmed appearance).
    *   User can see and edit the raw syntax while still seeing formatting applied.

2.  **WYSIWYG with Visible Syntax**:
    *   Unlike traditional WYSIWYG, syntax markers remain visible but styled differently.
    *   Example: `**bold text**` shows as **`**`**`bold text`**`**`** (markers dimmed, content bold).
    *   This allows users to understand and modify the markdown syntax directly.

3.  **Sync with Underlying Input**:
    *   The contentEditable div is the editing surface, but the `<input>` or `<textarea>` remains the source of truth.
    *   On every change, `extractRawText()` extracts plain text from contentEditable and updates the input.
    *   On blur, the preview switches back to `parseMarkdown()` rendering (syntax hidden).

4.  **Key Features in Edit Mode**:
    *   **F3 Quick Formatter**: Works with contentEditable using Range API for selections.
    *   **Keyboard Shortcuts**: Tab, F9 (swap words), Ctrl+Shift+D (multi-cursor) adapted for contentEditable.
    *   **Click-to-Edit**: Clicking preview enters edit mode with cursor at click position (see CLICK_TO_EDIT_CURSOR_POSITIONING.md).
    *   **Link Handling**: Links are intercepted to open in new tab instead of entering edit mode.

5.  **Related Documentation**:
    *   **[WYSIWYG Edit Mode](md/WYSIWYG_EDIT_MODE.md):** Detailed architecture and implementation.
    *   **[Edit Mode Architecture](md/EDIT_MODE_ARCHITECTURE.md):** Technical deep-dive.
    *   **[Click-to-Edit Cursor Positioning](md/CLICK_TO_EDIT_CURSOR_POSITIONING.md):** Cursor mapping challenges.
    *   **[Keyboard Shortcuts](md/KEYBOARD_SHORTCUTS.md):** All keyboard shortcuts including edit mode support.

### Data Structure (`tableData`)
The state is managed in a central object synced with persistence files:
- **`data.json`:** Content (Sheets, Rows, Columns, Styles).
- **`sheet_active.json`:** Application State (Active Sheet index).
- **Sheets:** Rows, columns, and `cellStyles` (keyed by `"row-col"`).
- **Categories:** Organization for sheets.
- **Metadata:** Nicknames, parent/sub-sheet relationships.

### Component Logic
- **Rendering:** `renderTable()` uses `DocumentFragment` for performance.
- **Formatting:** `applyMarkdownFormatting()` bridges raw input and rendered preview.
- **Shortcuts:** Managed in `handleKeyboardShortcuts` (F1-F4, Alt+M, etc.).

## Feature Documentation Index (See `md/` folder)

### User Interface & Navigation
- **[Navigation & UX](md/UX_NAVIGATION.md):** Sidebar, Tree View, F1/F2 Popups, Sub-sheets.
- **[F1 Quick Navigation](md/F1_QUICK_NAVIGATION.md):** Category and Sheet management.
- **[Recent Sheets (F2)](md/RECENT_SHEETS.md):** Navigation history.

### Cell & Formatting Features
- **[Cell-Specific Features](md/CELL_FEATURES.md):** Checkmarks, Sort Rank, Color History, Single Row View, Raw Mode.
- **[Cell Justify Alignment](md/CELL_JUSTIFY_ALIGN.md):** Justify text alignment via context menu (like Microsoft Word).
- **[Hidden Content](md/HIDDEN_CONTENT.md):** Collapsible `{{}}` and MCQ `[[]]` logic.
- **[Special Markdown](md/MARKDOWN_SPECIAL.md):** Lists, Small text, custom headings, border boxes, underlines.
- **[Highlight Shortcuts](md/COLOR_HIGHLIGHT_SHORTCUTS.md):** `==`, `!!`, `??` syntaxes.
- **[Custom Color Syntaxes](md/CUSTOM_SYNTAX.md):** Dynamic user-defined highlighting.

### Advanced Editing Tools
- **[Editing Extensions](md/EDITING_EXTENSIONS.md):** Search, Line tools, Case conversion, Multi-cursor.
- **[Advanced Tables](md/TABLE_ADVANCED.md):** Pipe tables, Rowspan `^^`, Auto-formatting.
- **[Math & KaTeX](md/KATEX_MATH.md):** LaTeX representation and smart fraction conversion.
- **[Keyboard Shortcuts](md/KEYBOARD_SHORTCUTS.md):** Complete reference for all keyboard shortcuts.

### Edit Mode & Architecture
- **[Markdown View Modes](md/MARKDOWN_MODES.md):** 3-state system (Raw, Standard, Clean).
- **[WYSIWYG Edit Mode](md/WYSIWYG_EDIT_MODE.md):** ContentEditable interface with visible syntax markers.
- **[Edit Mode Architecture](md/EDIT_MODE_ARCHITECTURE.md):** Technical deep-dive into contentEditable implementation.
    *   **[Click-to-Edit Cursor Positioning](md/CLICK_TO_EDIT_CURSOR_POSITIONING.md):** Cursor mapping between preview and edit mode (RESOLVED).

### Backend & Core Systems
- **[Core Systems](md/CORE_SYSTEMS.md):** Font system, Load timing, Height adjustment, Cursors.
- **[PDF & Static Export](md/CELL_PDF_EXPORT_FEATURE.md):** Visual capture and standalone generation.
- **[Clipboard Tools](md/COPY_SHEET_CONTENT.md):** Sheet content copying logic.
- **[Markdown Height Fix](md/MARKDOWN_HEIGHT_FIX.md):** Cell height adjustment for markdown and raw mode.

### Troubleshooting
- **[Problems & Fixes Log](md/PROBLEMS_AND_FIXES.md):** Historical bug fixes and solutions.
- **[Recent Work Log](md/RECENT.md):** Latest development sessions and current project state.
- **[Archived Sessions](md/ARCHIVE_RECENT.md):** Older development sessions (6+ sessions old).

---
*For specific layout features (Timeline, Word Connectors), search for their respective logic in `static/script.js`.*