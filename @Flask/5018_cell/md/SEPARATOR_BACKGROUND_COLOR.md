# Separator Background Color Feature

## Overview
Enhance the horizontal separator feature to apply background colors to content that appears after the separator.

## Syntax

### Basic Patterns
- `-----` = Normal gray separator (existing)
- `R-----` = Red separator line (existing)
- `-----R` = Normal separator + RED background for content below
- `R-----G` = Red separator line + GREEN background for content below
- `-----R-K` = Normal separator + RED background with BLACK text
- `R-----G-W` = Red separator line + GREEN background with WHITE text
- `-----#514522` = Normal separator + custom hex background color
- `-----#514522-#000000` = Normal separator + custom hex background + custom text color
- `-----#f00-#fff` = Normal separator + red background (3-digit hex) + white text
- `G-----#514522-#000000` = Green separator + custom hex background + custom text color

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

### Custom Hex Colors
- **6-digit hex**: `#RRGGBB` (e.g., `#ff0000`, `#514522`)
- **3-digit hex**: `#RGB` (e.g., `#f00` = `#ff0000`, `#154` = `#115544`)
- Format: `-----#RRGGBB` or `-----#RGB` for background only
- Format: `-----#RRGGBB-#RRGGBB` or `-----#RGB-#RGB` for background + text color
- Can combine with separator line colors: `R-----#RRGGBB-#RRGGBB`

### Color Code Combinations (NEW!)
- **Background + Text**: Use two color codes separated by dash
- `-----R-W` = Red background with white text
- `-----G-K` = Green background with black text
- `-----B-Y` = Blue background with yellow text
- `R-----K-W` = Red separator + black background with white text

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

### Example 7: Custom Hex Background Color
```
Normal text
-----#ffcc00
This has custom yellow background (#ffcc00)
More custom colored text
```

### Example 8: Custom Hex Background + Text Color
```
Normal text
-----#2c3e50-#ecf0f1
Dark blue background with light gray text
Custom colors for better readability
```

### Example 9: Colored Separator + Custom Hex Colors
```
Normal text
R-----#1a1a1a-#ffffff
Red separator line
Black background with white text below
High contrast section
-----
Back to normal
```

### Example 10: Multiple Custom Colors
```
-----#ffebee-#c62828
Light red background with dark red text
-----#e8f5e9-#2e7d32
Light green background with dark green text
-----#e3f2fd-#1565c0
Light blue background with dark blue text
-----
End
```

### Example 11: Color Code Combinations (NEW!)
```
Normal text
-----R-W
Red background with white text
Easy to read!
-----G-K
Green background with black text
Another section
-----
Back to normal
```

### Example 12: 3-Digit Hex Colors (NEW!)
```
Normal text
-----#f00
Red background using shorthand (#f00 = #ff0000)
-----#0f0-#000
Green background with black text
-----#154-#fff
Dark teal background (#115544) with white text
-----
End
```

### Example 13: Mixed Formats
```
-----R-K
Color code: Red bg + black text
-----#f00-#fff
3-digit hex: Red bg + white text
-----#ff0000-#ffffff
6-digit hex: Red bg + white text
All three produce similar results!
-----
```

## How It Works

### Pattern Breakdown
- **Color BEFORE dashes** (`R-----`) = Changes the separator line color
- **Color AFTER dashes** (`-----R` or `-----#RRGGBB` or `-----#RGB`) = Applies background color to content below
- **Two colors after dashes** (`-----R-W` or `-----#RGB-#RGB`) = Background color + text color
- **Both** (`R-----G` or `G-----#RRGGBB`) = Colored separator line + background for content below
- **With text color** (`-----#RRGGBB-#RRGGBB`) = Background color + text color
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
- Regex pattern: `/^([A-Z]+)?-{5,}((?:[A-Z]+(?:-[A-Z]+)?)|(?:#[0-9a-fA-F]{3,6}(?:-#[0-9a-fA-F]{3,6})?))?$/gm`
  - Captures optional prefix color (separator line color): `[A-Z]+`
  - Captures optional suffix: color code(s) OR hex color(s)
  - Color code format: `R`, `G`, `B`, etc. OR `R-W`, `G-K` (bg-text)
  - Hex format: `#RGB` or `#RRGGBB` or `#RGB-#RGB` or `#RRGGBB-#RRGGBB` (bg-text)
  - 3-digit hex colors are automatically expanded (e.g., `#f00` → `#ff0000`)
- Post-processing wraps all content after colored separator in a `<div>` with background and optional text color
- Background wrapper has minimal padding (2px 6px) and no margin for natural flow
- No newlines added after separator or wrapper div to prevent gaps
- Text color is applied when format includes second color: `#bg-#text` or `BG-TEXT`

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
