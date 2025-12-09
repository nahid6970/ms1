# Separator Background Color Feature

## Overview
Enhance the horizontal separator feature to apply background colors to content that appears after the separator.

## Syntax

### Basic Patterns
- `-----` = Normal gray separator (existing)
- `R-----` = Red separator line (existing)
- `-----R` = Normal separator + RED background for content below (NEW)
- `R-----G` = Red separator line + GREEN background for content below (NEW)

### Color Codes
- **R** = Red (#ff0000)
- **G** = Green (#00ff00)
- **B** = Blue (#0000ff)
- **Y** = Yellow (#ffff00)
- **O** = Orange (#ff8800)
- **P** = Purple/Magenta (#ff00ff)
- **C** = Cyan (#00ffff)
- **W** = White (#ffffff)
- **K** = Black (#000000)
- **GR** = Gray (#808080)

## Usage Examples

### Example 1: Basic Background Color
```
Normal text here
-----R
This text has RED background
More red background text
```

### Example 2: Ending Background Color
```
Normal text
-----G
Green background text
-----
Back to normal (no background)
```

### Example 3: Multiple Color Sections
```
Normal text
-----R
Red background section
-----B
Blue background section
-----Y
Yellow background section
-----
Back to normal
```

### Example 4: Colored Separator + Background
```
Normal text
R-----G
Red separator line + Green background below
More green background
```

### Example 5: Switching Colors
```
Normal text
G-----R
Green separator line + Red background
Red background continues
B-----Y
Blue separator line + Yellow background
Yellow background continues
-----
End all backgrounds
```

### Example 6: Just Colored Separator (Existing Feature)
```
Normal text
R-----
Just a red separator line (no background change)
Normal text continues
```

## How It Works

### Pattern Breakdown
- **Color BEFORE dashes** (`R-----`) = Changes the separator line color
- **Color AFTER dashes** (`-----R`) = Applies background color to content below
- **Both** (`R-----G`) = Colored separator line + background for content below
- **Plain separator** (`-----`) = Ends any active background color section

### Behavior
1. When `-----COLOR` is encountered, all subsequent content gets that background color
2. The background continues until:
   - Another separator is encountered (which can change to a different color)
   - A plain `-----` separator ends the coloring
   - The end of the cell is reached
3. Background colors can be nested/changed multiple times in one cell

## Implementation Details

### Files Modified
1. **static/script.js**
   - Updated separator regex to capture both prefix and suffix colors
   - Added post-processing to wrap content in background divs
   - Updated `checkHasMarkdown()` to detect new patterns
   - Updated `stripMarkdown()` to remove all separator variations

2. **export_static.py**
   - Same regex and post-processing logic for static HTML export
   - Updated `hasMarkdown` detection
   - Ensures feature works in exported standalone HTML files

3. **static/style.css**
   - Reduced separator margin from 12px to 6px for better spacing
   - Removed duplicate CSS definitions

### Technical Implementation
- Regex pattern: `/^([A-Z]+)?-{5,}([A-Z]+)?$/gm`
  - Captures optional prefix color (separator line color)
  - Captures optional suffix color (background color)
- Post-processing wraps all content after colored separator in a `<div>` with background color
- Background wrapper has minimal padding (2px 6px) and no margin for natural flow
- No newlines added after separator or wrapper div to prevent gaps

## Styling
- **Background wrapper**: `padding: 2px 6px; margin: 0;`
- **Separator**: `margin: 6px 0;` (reduced from 12px)
- Background color applies to all content until closed

## Testing
See `md/SEPARATOR_BG_TEST.md` for comprehensive test cases.

## Notes
- Works with all existing markdown features (bold, italic, tables, etc.)
- Background colors can be combined with colored separator lines
- Multiple color sections can exist in one cell
- Plain separator `-----` acts as a "reset" to end background coloring
