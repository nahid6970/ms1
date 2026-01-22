# Keyboard Shortcuts Reference

Complete guide to all keyboard shortcuts available in the application.

---

## 🎯 Navigation & Sheet Management

| Shortcut | Description |
|----------|-------------|
| **F1** | Open Quick Navigation popup (Categories & Sheets) |
| **F2** | Open Recent Sheets popup |
| **F4** | Toggle top ribbons (hide/show header controls) |
| **Alt+M** | Toggle between current and previous sheet |
| **Alt+N** | Add new row to current sheet |
| **Tab** | Move to next cell (in cell editing mode) |
| **Shift+Tab** | Move to previous cell (in cell editing mode) |

---

## ✏️ Text Editing & Formatting

### Basic Editing
| Shortcut | Description |
|----------|-------------|
| **F3** | Open Quick Markdown Formatter (with text selected) |
| **F8** | Search word under cursor/selection and copy to clipboard |
| **F9** | Swap two words separated by space/comma (with text selected) |
| **Ctrl+S** | Save data (manual save) |

### Quick Formatter (F3) Features
When text is selected, press F3 to open the formatter with these options:
- **Bold** (`**text**`)
- **Italic** (`@@text@@`)
- **Underline** (`__text__`)
- **Strikethrough** (`~~text~~`)
- **Heading** (`##text##`)
- **Small text** (`..text..`)
- **Code** (`` `text` ``)
- **Superscript** (`^text^`)
- **Subscript** (`~text~`)
- **Highlight** (`==text==`)
- **Red highlight** (`!!text!!`)
- **Blue highlight** (`??text??`)
- **Links** (`{link:url}text{/}`)
- **Colors** (custom foreground/background)
- **Border box** (`#R#text#/#`)
- **Variable font size** (`#2#text#/#`)
- **Square root** (`\(\sqrt{text}\)`)
- **Smart math** (converts fractions to LaTeX)
- **Superscript** (`^text^`)
- **Subscript** (`~text~`)
- **📊 Format pipe table** - Auto-align table columns
- **🧹 Remove formatting** - Strip all markdown syntax
- **ABC/abc/Abc** - Change text case (UPPER/lower/Proper)
- **Lines ↔ Comma** - Convert between formats
- **🔍 Search in Google** - Search selected text
- **🎯 Select all matching** - Multi-cursor for all occurrences

---

## 🎨 Multi-Cursor Editing

### Select Next Occurrence (Ctrl+Shift+D)
**Mode:** Raw mode only (📄 button)

| Shortcut | Description |
|----------|-------------|
| **Ctrl+Shift+D** | Select next occurrence of selected text |
| **Ctrl+Shift+D** (repeat) | Add more occurrences to selection |
| **Home** | Move all cursors to line start (consolidates per line) |
| **End** | Move all cursors to line end (consolidates per line) |
| **Arrow keys** | Move all cursors |
| **Type** | Replace all selected occurrences |
| **Escape** | Exit multi-cursor mode |

### Multi-Line Cursors (Ctrl+Alt+Arrows)
**Mode:** Raw mode only (📄 button), Textarea cells only

| Shortcut | Description |
|----------|-------------|
| **Ctrl+Alt+Down** | Add cursor on line below |
| **Ctrl+Alt+Up** | Add cursor on line above |
| **Arrow Left/Right** | Move all cursors left/right |
| **Home** | Move all cursors to line start |
| **End** | Move all cursors to line end |
| **Shift+Arrow** | Extend selection on all lines |
| **Shift+Home** | Select from cursor to line start on all lines |
| **Shift+End** | Select from cursor to line end on all lines |
| **Ctrl+Space** | Move cursors to next word boundary |
| **Type** | Insert text at all cursor positions |
| **Backspace/Delete** | Delete at all cursor positions |
| **Escape** | Exit multi-line cursor mode |

---

## 📝 Line Manipulation

| Shortcut | Description |
|----------|-------------|
| **Alt+Up** | Move selected lines up |
| **Alt+Down** | Move selected lines down |
| **Ctrl+D** | Duplicate current line |
| **Ctrl+Shift+K** | Delete current line |

---

## 🔍 Search & Replace

| Shortcut | Description |
|----------|-------------|
| **Ctrl+F** | Focus search box |
| **F8** | Search word under cursor and copy to clipboard |
| **Ctrl+Shift+D** | Select next occurrence (multi-cursor) |

---

## 📄 Raw Mode vs Markdown Preview Mode

### Toggle Modes
| Shortcut | Description |
|----------|-------------|
| **📄 Button** | Toggle Raw Mode (show markdown syntax) |

### Mode-Specific Features

**Raw Mode (📄 enabled):**
- See all markdown syntax
- Multi-cursor features work (Ctrl+Shift+D, Ctrl+Alt+arrows)
- Direct text editing
- Cell height adjusts to content

**Markdown Preview Mode (default):**
- See rendered markdown
- Click-to-edit with cursor positioning
- Links are clickable (don't enter edit mode)
- F3 formatter works
- F9 word swap works
- Multi-cursor features show message to switch to raw mode

---

## 🎯 Context Menu Actions

**Right-click on cell:**
- Set cell color
- Set text color
- Set font size
- Set sort rank
- Clear formatting
- Export cell to PDF

**Right-click on column header:**
- Rename column
- Delete column
- Set column color
- Set column text color

---

## 💡 Tips

1. **Multi-cursor consolidation:** When using Ctrl+Shift+D with multiple occurrences on the same line, pressing Home or End will consolidate to one cursor per line.

2. **F3 Formatter scroll:** The scroll position is maintained when applying formatting with F3.

3. **Word boundaries:** Ctrl+Space in multi-line cursor mode moves to the next space or special character.

4. **Selection visualization:** Multi-line cursors show blue selection highlights on all lines except the last (which shows native selection).

5. **Raw mode for advanced editing:** Switch to raw mode (📄) for multi-cursor features and direct syntax editing.

6. **Link clicking:** In markdown preview mode, click links to open them without entering edit mode.

---

## 🚫 Disabled Browser Shortcuts

These shortcuts are intercepted to prevent browser defaults:
- **Ctrl+Shift+D** - Prevented (Chrome bookmark shortcut)
- **Ctrl+Alt+Arrows** - Prevented (Windows screen rotation)
- **F9** - Prevented (browser default)

---

*Last updated: 2026-01-16*
