# Microsoft Word-Style Rich Text Editing Feature

## Problem Description

Currently, users must learn and type markdown syntax (`**bold**`, `==highlight==`) to format text. This creates barriers for non-technical users and slows down formatting workflows.

## Proposed Solution

Implement Microsoft Word-style rich text editing where users can:
1. Select text in a cell
2. Press F3 (Quick Formatter)
3. Click formatting buttons (Bold, Italic, etc.)
4. See immediate visual formatting without any syntax markers

**Example:**
- Instead of typing: `**bold text**`
- User selects "bold text" → Press F3 → Click Bold button → Text becomes **bold** directly

## Benefits

1. **User-Friendly**: No syntax to learn - just select and format
2. **Familiar**: Works like Word, Google Docs, etc.
3. **Visual**: See formatting immediately as you apply it
4. **Flexible**: Can mix multiple formats easily
5. **Intuitive**: F3 menu shows current formatting state
6. **Faster**: No need to type syntax markers

## Implementation Approaches

### Option 1: HTML-Based Cells (Recommended)

Replace textareas with `contenteditable` divs that support rich HTML:

```javascript
// Instead of: <textarea>**bold text**</textarea>
// Use: <div contenteditable="true"><b>bold text</b></div>

function applyDirectFormatting(formatType, event) {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        switch(formatType) {
            case 'bold':
                document.execCommand('bold');
                break;
            case 'italic':
                document.execCommand('italic');
                break;
            case 'underline':
                document.execCommand('underline');
                break;
            case 'highlight':
                document.execCommand('hiliteColor', false, '#ffeb3b');
                break;
        }
    }
}
```

**Pros:**
- Native rich text editing like Word
- No syntax to learn or remember
- WYSIWYG editing experience
- Can mix multiple formats easily
- Browser handles cursor positioning

**Cons:**
- More complex to implement
- Data storage becomes HTML instead of plain text
- Need to handle copy/paste of rich content

### Option 2: CSS-Only Formatting with Metadata

Keep textareas but store formatting information separately:

```javascript
// Text: "Hello world"
// Formatting: {0-4: {bold: true}, 6-10: {italic: true}}
// Result: "Hello world" (Hello is bold, world is italic)

cellData = {
    text: "Hello world",
    formatting: [
        {start: 0, end: 4, styles: {bold: true}},
        {start: 6, end: 10, styles: {italic: true}}
    ]
}
```

**Pros:**
- Keeps plain text data
- Compatible with existing system
- Easier search functionality

**Cons:**
- Complex to manage overlapping formats
- Harder to implement than HTML approach
- Need custom rendering logic

### Option 3: Hybrid Approach

Use contenteditable for editing, convert to/from a clean format for storage:

```javascript
// Storage: Clean JSON format with formatting metadata
// Editing: Rich HTML in contenteditable
// Display: Rendered HTML from stored data
```

## Recommended Implementation: Option 1 (HTML-Based)

### Step 1: Replace Textareas with ContentEditable

```javascript
// In renderTable(), instead of creating textarea:
if (wrapEnabled && isTextType) {
    input = document.createElement('div');
    input.contentEditable = true;
    input.className = 'rich-text-cell';
    input.innerHTML = cellValue; // HTML content
    
    input.oninput = (e) => {
        updateCell(rowIndex, colIndex, e.target.innerHTML);
    };
}
```

### Step 2: Update F3 Menu Functions

```javascript
// Replace existing markdown functions:
function applyBoldFormatting(event) {
    event.preventDefault();
    document.execCommand('bold');
    updateFormattingState();
}

function applyItalicFormatting(event) {
    event.preventDefault();
    document.execCommand('italic');
    updateFormattingState();
}

function applyHighlight(color, event) {
    event.preventDefault();
    document.execCommand('hiliteColor', false, color);
    updateFormattingState();
}

function clearAllFormatting(event) {
    event.preventDefault();
    document.execCommand('removeFormat');
    updateFormattingState();
}
```

### Step 3: Show Active Formatting State

```javascript
function updateFormattingState() {
    // Highlight active formatting buttons in F3 menu
    const boldBtn = document.querySelector('.format-btn[data-format="bold"]');
    const italicBtn = document.querySelector('.format-btn[data-format="italic"]');
    
    boldBtn.classList.toggle('active', document.queryCommandState('bold'));
    italicBtn.classList.toggle('active', document.queryCommandState('italic'));
}
```

### Step 4: Data Storage Updates

```javascript
function updateCell(rowIndex, colIndex, htmlContent) {
    // Store both HTML and plain text
    const sheet = tableData.sheets[currentSheet];
    sheet.rows[rowIndex][colIndex] = htmlContent;
    
    // Extract plain text for search
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;
    sheet.plainTextCache = sheet.plainTextCache || {};
    sheet.plainTextCache[`${rowIndex}-${colIndex}`] = tempDiv.textContent;
    
    saveData();
}
```

### Step 5: CSS Styling

```css
.rich-text-cell {
    width: 100%;
    border: none;
    outline: none;
    background: transparent;
    font-family: inherit;
    font-size: inherit;
    line-height: 1.4;
    min-height: 20px;
    padding: 2px;
}

.rich-text-cell:focus {
    background: rgba(0, 123, 255, 0.1);
}

/* F3 Menu active state */
.format-btn.active {
    background: #007bff;
    color: white;
}
```

## Enhanced F3 Menu Features

### New Formatting Options:
- **Bold** (Ctrl+B equivalent)
- **Italic** (Ctrl+I equivalent)  
- **Underline** (Ctrl+U equivalent)
- **Strikethrough**
- **Highlight Colors** (Yellow, Red, Blue, Green)
- **Text Colors** (Black, Red, Blue, etc.)
- **Font Size** (Small, Normal, Large)
- **Clear All Formatting** (Remove all styles)

### Smart Features:
- **Toggle behavior**: Click Bold on bold text to remove bold
- **Active state**: Buttons highlight when cursor is on formatted text
- **Multi-format**: Apply multiple formats to same text
- **Partial selection**: Format only selected portion of text

## Migration Strategy

### Phase 1: Parallel Implementation
- Keep existing markdown system
- Add rich text editing as opt-in feature
- Allow users to choose per-cell or globally

### Phase 2: Data Migration
```javascript
function convertMarkdownToHTML(markdownText) {
    return markdownText
        .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
        .replace(/@@(.+?)@@/g, '<i>$1</i>')
        .replace(/__(.+?)__/g, '<u>$1</u>')
        .replace(/==(.+?)==/g, '<span style="background: #000; color: #fff; padding: 1px 4px;">$1</span>')
        .replace(/!!(.+?)!!/g, '<span style="background: #dc3545; color: #fff; padding: 1px 4px;">$1</span>')
        .replace(/\?\?(.+?)\?\?/g, '<span style="background: #007bff; color: #fff; padding: 1px 4px;">$1</span>');
}
```

### Phase 3: Full Migration
- Convert all existing markdown to HTML
- Remove markdown parsing functions
- Update static export to handle HTML

## Challenges & Solutions

### Challenge 1: Search Functionality
**Problem**: Can't search HTML tags
**Solution**: Maintain plain text cache for search

### Challenge 2: Copy/Paste
**Problem**: Users might paste rich content from other apps
**Solution**: Strip unwanted formatting, keep only supported styles

### Challenge 3: Data Size
**Problem**: HTML is larger than plain text
**Solution**: Compress HTML, use efficient storage

### Challenge 4: Static Export
**Problem**: Need to render HTML in static files
**Solution**: HTML works directly in static export

## Files to Modify

1. **`static/script.js`**:
   - Replace textarea creation with contenteditable divs
   - Update F3 menu functions to use `document.execCommand`
   - Add formatting state detection
   - Update `updateCell()` function

2. **`static/style.css`**:
   - Add `.rich-text-cell` styles
   - Add `.format-btn.active` styles
   - Style rich text content

3. **`templates/index.html`**:
   - Update F3 menu buttons with new functions
   - Add active state indicators

4. **`export_static.py`**:
   - Update to handle HTML content instead of markdown
   - Ensure rich text renders in static export

## Testing Checklist

- [ ] Bold/italic/underline formatting works
- [ ] Color highlighting works
- [ ] Clear formatting removes all styles
- [ ] F3 buttons show active state correctly
- [ ] Copy/paste works appropriately
- [ ] Search works with plain text extraction
- [ ] Static export renders rich text correctly
- [ ] Data saves and loads properly
- [ ] Performance is acceptable
- [ ] Works on mobile devices

## Future Enhancements

1. **Advanced Formatting**: Lists, links, tables within cells
2. **Keyboard Shortcuts**: Ctrl+B, Ctrl+I, etc.
3. **Format Painter**: Copy formatting from one cell to another
4. **Styles**: Predefined text styles (Heading 1, 2, etc.)
5. **Collaboration**: Real-time rich text editing
6. **Import/Export**: Support for Word documents, RTF files
