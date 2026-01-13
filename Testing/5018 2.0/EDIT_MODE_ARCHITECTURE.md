# Edit Mode Architecture: WYSIWYG with Visible Syntax

This document explains how the editor achieves a true WYSIWYG experience where formatted content remains visually styled during editing, while syntax markers become visible but unobtrusive.

---

## The Problem

Traditional markdown editors have two modes:
1. **Raw Mode**: You see `**bold**` as plain text
2. **Preview Mode**: You see **bold** rendered, but can't edit

This creates a jarring experience - switching between ugly raw text and beautiful preview.

**Goal**: Edit the rendered content directly, with syntax markers visible but styled content intact.

---

## The Solution: Single ContentEditable with Dual Rendering

Instead of a `<textarea>` (which only supports plain text), we use a `<div contenteditable="true">` which can contain styled HTML while remaining editable.

### Core Concept

```
┌─────────────────────────────────────────────────────────┐
│  BLUR STATE (Preview)                                   │
│  ─────────────────────                                  │
│  Content rendered with parseMarkdown()                  │
│  User sees: "This is bold text"  (bold styled)         │
│             └──────────┘                                │
└─────────────────────────────────────────────────────────┘
                          │
                          │ User clicks/focuses
                          ▼
┌─────────────────────────────────────────────────────────┐
│  FOCUS STATE (Edit)                                     │
│  ──────────────────                                     │
│  Content rendered with highlightSyntax()                │
│  User sees: "This is **bold** text"                     │
│                      ↑    ↑                             │
│              grey/faded   bold styled                   │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### 1. The Editor Element

```javascript
const editor = document.createElement('div');
editor.className = 'row-editor';
editor.contentEditable = true;
editor.innerHTML = parseMarkdown(row.content);  // Start with preview
editor._rawContent = row.content;               // Store raw markdown
```

Key points:
- `contentEditable = true` makes the div editable like a text field
- `_rawContent` stores the actual markdown string (source of truth)
- Initial display uses `parseMarkdown()` for full preview rendering

### 2. Focus Event: Switch to Edit Mode

```javascript
editor.addEventListener('focus', () => {
    editor.classList.add('editing');
    editor.innerHTML = highlightSyntax(editor._rawContent);
    placeCaretAtEnd(editor);
});
```

When user clicks to edit:
1. Add `.editing` class (optional visual feedback)
2. Replace innerHTML with `highlightSyntax()` output
3. Position cursor at end

### 3. Blur Event: Switch to Preview Mode

```javascript
editor.addEventListener('blur', () => {
    editor.classList.remove('editing');
    editor._rawContent = extractRawText(editor);  // Get plain markdown
    row.content = editor._rawContent;
    editor.innerHTML = parseMarkdown(editor._rawContent);  // Render preview
    saveData();
});
```

When user clicks away:
1. Extract raw markdown from the styled HTML
2. Update data model
3. Re-render as full preview
4. Save to backend

### 4. Input Event: Live Re-highlighting

```javascript
editor.addEventListener('input', () => {
    if (editor.classList.contains('editing')) {
        // Save cursor position
        const offset = getCaretCharacterOffset(editor);
        
        // Extract raw text and re-highlight
        editor._rawContent = extractRawText(editor);
        editor.innerHTML = highlightSyntax(editor._rawContent);
        
        // Restore cursor position
        setCaretPosition(editor, offset);
    }
});
```

On every keystroke:
1. Save cursor position (character offset)
2. Extract raw markdown from current HTML
3. Re-apply syntax highlighting
4. Restore cursor to same position

---

## The Two Rendering Functions

### parseMarkdown() - Full Preview Rendering

Used when NOT editing. Completely hides syntax markers.

```javascript
// Input:  "This is **bold** and ==highlighted== text"
// Output: "This is <span class="md-bold">bold</span> and 
//          <span class="md-hl-yellow">highlighted</span> text"
```

Markers (`**`, `==`) are completely removed, only styled content remains.

### highlightSyntax() - Edit Mode Rendering

Used when editing. Shows markers but keeps styling.

```javascript
// Input:  "This is **bold** and ==highlighted== text"
// Output: "This is <span class="md-bold">
//            <span class="syn-marker">**</span>
//            bold
//            <span class="syn-marker">**</span>
//          </span> and 
//          <span class="md-hl-yellow">
//            <span class="syn-marker">==</span>
//            highlighted
//            <span class="syn-marker">==</span>
//          </span> text"
```

Key difference: Markers are wrapped in `<span class="syn-marker">` INSIDE the styled span.

---

## CSS: Making Markers Unobtrusive

```css
/* The styled content uses same classes as preview */
.md-bold { font-weight: 700; }
.md-hl-yellow { background: #fef08a; color: #1a1a2e; }
.md-h1 { font-size: 2em; font-weight: 700; }

/* Markers are faded but inherit parent styling context */
.syn-marker {
    color: var(--text-secondary);
    opacity: 0.5;
    font-weight: normal;      /* Reset so ** doesn't look bold */
    font-style: normal;       /* Reset so @@ doesn't look italic */
    text-decoration: none;    /* Reset so __ doesn't look underlined */
    font-size: inherit;       /* Keep same size as surrounding text */
    vertical-align: baseline; /* Keep aligned with text */
}
```

The trick: `.syn-marker` resets font properties so the marker characters themselves don't inherit the styling (you don't want `**` to appear bold), while the parent span still applies styling to the content.

---

## Cursor Position Management

ContentEditable doesn't have simple `.selectionStart` like textarea. We need custom functions:

### Getting Cursor Position

```javascript
function getCaretCharacterOffset(element) {
    let caretOffset = 0;
    const sel = window.getSelection();
    if (sel.rangeCount > 0) {
        const range = sel.getRangeAt(0);
        const preCaretRange = range.cloneRange();
        preCaretRange.selectNodeContents(element);
        preCaretRange.setEnd(range.endContainer, range.endOffset);
        caretOffset = preCaretRange.toString().length;
    }
    return caretOffset;
}
```

Returns character offset as if it were plain text (ignoring HTML tags).

### Setting Cursor Position

```javascript
function setCaretPosition(element, offset) {
    const range = document.createRange();
    const sel = window.getSelection();
    let currentOffset = 0;
    let found = false;
    
    // Walk through text nodes until we reach target offset
    const walk = (node) => {
        if (found) return;
        if (node.nodeType === Node.TEXT_NODE) {
            if (currentOffset + node.length >= offset) {
                range.setStart(node, offset - currentOffset);
                range.collapse(true);
                found = true;
            } else {
                currentOffset += node.length;
            }
        } else {
            for (const child of node.childNodes) {
                walk(child);
                if (found) break;
            }
        }
    };
    
    walk(element);
    sel.removeAllRanges();
    sel.addRange(range);
}
```

Walks the DOM tree counting characters until it reaches the target offset.

---

## Extracting Raw Text

When the HTML contains styled spans, we need to extract just the text:

```javascript
function extractRawText(element) {
    let text = '';
    const walk = (node) => {
        if (node.nodeType === Node.TEXT_NODE) {
            text += node.textContent;
        } else if (node.nodeName === 'BR') {
            text += '\n';
        } else if (node.nodeName === 'DIV' && text.length > 0 && !text.endsWith('\n')) {
            text += '\n';  // ContentEditable uses DIVs for new lines
            node.childNodes.forEach(walk);
        } else {
            node.childNodes.forEach(walk);
        }
    };
    walk(element);
    return text;
}
```

This recursively walks the DOM and:
- Collects text from text nodes
- Converts `<br>` to `\n`
- Handles `<div>` elements (contenteditable creates these on Enter)

---

## Why This Works

1. **Same Visual Output**: Both `parseMarkdown()` and `highlightSyntax()` use the SAME CSS classes (`.md-bold`, `.md-hl-yellow`, etc.), so the content looks identical.

2. **Markers Inside Styled Spans**: By placing `<span class="syn-marker">**</span>` INSIDE `<span class="md-bold">`, the bold styling applies to the whole region, but the marker itself has its styles reset.

3. **Continuous Editing**: The input event re-highlights on every keystroke, so new syntax is immediately styled as you type.

4. **Cursor Preservation**: By saving/restoring cursor position as character offset, the cursor doesn't jump around when HTML is replaced.

---

## Visual Flow

```
User types: "Hello **wor"
                      ↑ cursor here

extractRawText() → "Hello **wor"
highlightSyntax() → "Hello <span class="md-bold"><span class="syn-marker">**</span>wor</span>"

Display:  Hello **wor
                ↑↑ grey, faded
                  ↑↑↑ bold (incomplete, still being typed)

User continues: "Hello **world**"

highlightSyntax() → "Hello <span class="md-bold"><span class="syn-marker">**</span>world<span class="syn-marker">**</span></span>"

Display:  Hello **world**
                ↑↑     ↑↑ grey, faded
                  ↑↑↑↑↑ bold

User clicks away (blur):

parseMarkdown() → "Hello <span class="md-bold">world</span>"

Display:  Hello world
                ↑↑↑↑↑ bold, no markers visible
```

---

## Summary

| Aspect | Traditional Editor | This Implementation |
|--------|-------------------|---------------------|
| Edit view | Raw text only | Styled + visible markers |
| Preview view | Fully rendered | Fully rendered |
| Transition | Jarring switch | Smooth (just markers appear/disappear) |
| Cursor handling | Native | Custom offset tracking |
| Element type | `<textarea>` | `<div contenteditable>` |

The key insight is that `contenteditable` allows HTML content while remaining editable, and by using the same CSS classes for both modes with markers wrapped in reset-styled spans, we achieve a seamless WYSIWYG experience.
