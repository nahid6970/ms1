# Canvas-Based Text Editor

## Overview
Replace the current markdown-enabled spreadsheet with a canvas-based editor for more flexible text styling and manipulation.

## Current Limitations
- Markdown syntax constraints
- Limited visual formatting options
- Complex parsing logic for every feature
- Fixed cell-based layout

## Canvas-Based Advantages
- Freehand text placement
- Custom brush styles and effects
- Real-time visual feedback
- Layered composition support
- Custom shapes, arrows, connectors
- No syntax parsing required

## Proposed Features

### 1. Text Tools
- Free text input anywhere on canvas
- Text stroke/outline with variable thickness
- Custom font sizes and families
- Text rotation and positioning
- Text grouping and alignment

### 2. Drawing Tools
- Freehand drawing with brush styles
- Shape tools (rectangles, circles, arrows)
- Connector lines between elements
- Custom stroke colors and widths
- Fill patterns and gradients

### 3. Text Styling (Current → Canvas)
| Current Syntax | Canvas Implementation |
|---------------|----------------------|
| `**bold**` | Bold button in text toolbar |
| `*italic*` | Italic button in text toolbar |
| `_R_text__` | Color picker for underline |
| `ŝŝtextŝŝ` | Text stroke thickness selector |
| `:::Title:::` | Title style preset |
| `#R#text#/#` | Border color picker |

### 4. Canvas Features
- Zoom/pan navigation
- Undo/redo history
- Layer management
- Export to PNG/SVG/HTML
- Import existing markdown (auto-convert)

## Implementation Plan

### Phase 1: Basic Canvas Setup
- [ ] Create HTML canvas element
- [ ] Implement basic drawing (lines, shapes)
- [ ] Add text input mode
- [ ] Implement selection/dragging

### Phase 2: Text Tools
- [ ] Text input with formatting toolbar
- [ ] Font size/color pickers
- [ ] Text stroke/outline controls
- [ ] Text alignment options

### Phase 3: Drawing Tools
- [ ] Brush tool with customizable settings
- [ ] Shape tools (rect, circle, arrow)
- [ ] Connector lines
- [ ] Custom stroke styles

### Phase 4: Advanced Features
- [ ] Layer management
- [ ] Grouping/ungrouping
- [ ] Undo/redo system
- [ ] Export functionality

### Phase 5: Migration
- [ ] Import existing markdown cells
- [ ] Maintain data.json compatibility
- [ ] Export to static HTML
- [ ] Update UI/UX

## Technical Considerations

### Canvas Libraries
- **Fabric.js**: Full-featured, good for complex objects
- **Konva.js**: Good performance, layer support
- **Paper.js**: Vector-based, path-focused
- **Plain Canvas**: Full control, more work

### Data Structure
```javascript
{
  elements: [
    { type: 'text', x, y, content, style },
    { type: 'shape', x, y, width, height, style },
    { type: 'line', x1, y1, x2, y2, style }
  ],
  layers: [...],
  history: [...]
}
```

### Export Options
- PNG (raster image)
- SVG (vector, editable)
- HTML (canvas element)
- JSON (editable data)

## Next Steps
1. Choose canvas library
2. Create prototype with basic text + drawing
3. Test performance with large documents
4. Implement import from existing markdown
5. Build out full feature set
