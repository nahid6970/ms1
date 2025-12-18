# Click-to-Edit Cursor Positioning Issue

## Problem Description

When clicking on rendered markdown text in the preview overlay, the cursor is positioned correctly in the raw markdown text, but the textarea scrolls to center the cursor line or make it visible. This causes the text to jump up or down from where the user clicked, requiring them to scroll to find their cursor position.

**Current Behavior:**
1. User clicks on text in markdown preview (e.g., at Y position 200px)
2. Cursor is correctly positioned in raw markdown text
3. `keepCursorCentered()` or `keepCursorVisible()` scrolls the textarea
4. Text jumps to a different position (e.g., cursor line now at Y position 100px or 300px)
5. User has to scroll to find where their cursor actually is

**Desired Behavior:**
1. User clicks on text in markdown preview at Y position 200px
2. Cursor is positioned in raw markdown text
3. Textarea scrolls so the cursor line appears at exactly Y position 200px (where user clicked)
4. No additional scrolling needed - cursor is exactly where user expects it

## Current Implementation

The click-to-edit functionality is handled in `handlePreviewMouseDown()` function in `static/script.js`:

```javascript
function handlePreviewMouseDown(e) {
    // ... cursor position calculation logic ...
    
    // 6. Manual scroll to ensure visibility
    if (input.tagName === 'TEXTAREA' && typeof keepCursorCentered === 'function') {
        keepCursorCentered(input);
        requestAnimationFrame(() => keepCursorCentered(input));
    }
}
```

The `keepCursorCentered()` function centers the cursor line in the middle of the textarea:

```javascript
function keepCursorCentered(textarea) {
    requestAnimationFrame(() => {
        const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 20;
        const lines = textarea.value.substr(0, textarea.selectionStart).split('\n');
        const wantedTop = (lines.length - 1) * lineHeight;
        textarea.scrollTop = wantedTop - textarea.clientHeight / 2 + lineHeight / 2;
    });
}
```

## Proposed Solutions

### Solution 1: Position Cursor Line at Mouse Click Position

Replace the centering behavior with exact positioning:

```javascript
function positionCursorAtMouseClick(textarea, mouseEvent) {
    requestAnimationFrame(() => {
        const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 20;
        const lines = textarea.value.substr(0, textarea.selectionStart).split('\n');
        const cursorLineIndex = lines.length - 1;
        const cursorLineTop = cursorLineIndex * lineHeight;
        
        // Get the mouse Y position relative to the textarea
        const textareaRect = textarea.getBoundingClientRect();
        const mouseY = mouseEvent.clientY - textareaRect.top;
        
        // Calculate scroll position so cursor line appears exactly at mouse Y position
        const targetScrollTop = cursorLineTop - mouseY;
        
        // Ensure we don't scroll beyond the content bounds
        const maxScrollTop = Math.max(0, textarea.scrollHeight - textarea.clientHeight);
        textarea.scrollTop = Math.max(0, Math.min(targetScrollTop, maxScrollTop));
    });
}
```

### Solution 2: Minimal Scroll Approach

Only scroll if the cursor is not visible, and when scrolling, position it at the click location:

```javascript
function keepCursorAtClickPosition(textarea, clickY) {
    requestAnimationFrame(() => {
        const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 20;
        const lines = textarea.value.substr(0, textarea.selectionStart).split('\n');
        const cursorLineTop = (lines.length - 1) * lineHeight;
        const cursorLineBottom = cursorLineTop + lineHeight;
        
        const currentScrollTop = textarea.scrollTop;
        const visibleTop = currentScrollTop;
        const visibleBottom = currentScrollTop + textarea.clientHeight;
        
        // If cursor is already visible, don't scroll
        if (cursorLineTop >= visibleTop && cursorLineBottom <= visibleBottom) {
            return;
        }
        
        // If cursor is not visible, position it at the click Y position
        const targetScrollTop = cursorLineTop - clickY;
        const maxScrollTop = Math.max(0, textarea.scrollHeight - textarea.clientHeight);
        textarea.scrollTop = Math.max(0, Math.min(targetScrollTop, maxScrollTop));
    });
}
```

### Solution 3: Preview-Textarea Coordinate Mapping

Map the click position from preview coordinates to textarea coordinates:

```javascript
function mapPreviewClickToTextarea(textarea, preview, mouseEvent) {
    requestAnimationFrame(() => {
        const previewRect = preview.getBoundingClientRect();
        const textareaRect = textarea.getBoundingClientRect();
        
        // Calculate relative click position in preview
        const clickYInPreview = mouseEvent.clientY - previewRect.top;
        const previewHeight = previewRect.height;
        const clickRatio = clickYInPreview / previewHeight;
        
        // Map to textarea coordinates
        const textareaHeight = textareaRect.height;
        const targetYInTextarea = clickRatio * textareaHeight;
        
        // Position cursor line at the mapped position
        const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 20;
        const lines = textarea.value.substr(0, textarea.selectionStart).split('\n');
        const cursorLineTop = (lines.length - 1) * lineHeight;
        
        const targetScrollTop = cursorLineTop - targetYInTextarea;
        const maxScrollTop = Math.max(0, textarea.scrollHeight - textarea.clientHeight);
        textarea.scrollTop = Math.max(0, Math.min(targetScrollTop, maxScrollTop));
    });
}
```

## Implementation Notes

### Key Considerations:
1. **Coordinate Systems**: Preview and textarea may have different coordinate systems due to different content heights
2. **Line Height Calculation**: Must accurately calculate line height and cursor line position
3. **Scroll Bounds**: Ensure scrolling doesn't go beyond content boundaries
4. **Timing**: Use `requestAnimationFrame` to ensure DOM updates are complete
5. **Browser Compatibility**: Handle different browsers' text selection APIs

### Files to Modify:
- `static/script.js`: Update `handlePreviewMouseDown()` function
- `static/script.js`: Replace or modify `keepCursorCentered()` function
- `export_static.py`: Apply same logic to static export if needed

### Testing Scenarios:
1. Click on text at top of preview
2. Click on text at bottom of preview  
3. Click on text in middle of preview
4. Test with long content that requires scrolling
5. Test with short content that doesn't need scrolling
6. Test with different markdown formatting (headers, lists, etc.)

## Alternative Approaches

### Option A: Visual Indicator
Instead of moving the text, add a visual indicator (like a temporary highlight or arrow) showing where the cursor was positioned.

### Option B: Smooth Animation
Animate the scroll transition so users can follow where their cursor went.

### Option C: Dual View Mode
Show both preview and raw text side by side, eliminating the need for click-to-edit positioning.

## Future Implementation Checklist

When implementing this feature:

- [ ] Choose one of the proposed solutions
- [ ] Update `handlePreviewMouseDown()` function
- [ ] Create or modify cursor positioning function
- [ ] Test with various content lengths and positions
- [ ] Ensure compatibility with existing keyboard shortcuts
- [ ] Update static export functionality if needed
- [ ] Test cross-browser compatibility
- [ ] Update developer documentation

## Related Code Locations

- `handlePreviewMouseDown()`: ~line 962 in `static/script.js`
- `keepCursorCentered()`: ~line 5340 in `static/script.js`
- Click handlers for textareas: ~lines 5617, 5712 in `static/script.js`
- Preview creation: ~line 1109 in `static/script.js`