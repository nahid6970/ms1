# Script Manager GUI Qt - Development Notes

## Issue 1: Height & Scroll Fix

### Problem
Items height was limited by window size - couldn't scroll when items were tall.

### Root Cause
CyberButton stylesheet had `min-height: 20px;` and `!important` on hover styles that weren't in the original working version.

### Fix
Reverted CyberButton stylesheet to match old_version.py exactly. Keep `SizePolicy.Expanding` for both directions.

---

## Issue 2: Row Span Fix

### Problem
Row span wasn't working properly - items didn't span multiple rows correctly.

### Fix
- Added `Qt.AlignmentFlag.AlignTop` to grid widget placement
- For row_span > 1, calculate total height as: `(item_h * r_span) + (spacing * (r_span - 1))`

---

## Issue 3: Icon Settings

### Features Added
- Icon width (W) - 0 = auto
- Icon height (H) - 0 = auto  
- Icon gap - space between icon and text (default: 2px)
- Icon position - top/left/right/bottom/center (center = icon only, no text)

### Reset Behavior
Both `reset_styles()` in EditDialog and `reset_item_styles()` in main window:
- **Preserve** `icon_path` (keeps the icon file)
- **Reset** icon settings to defaults: width=0, height=0, gap=2, position="top"

---

## Issue 4: Delete Dialog & Add Buttons

### Changes
- Replaced single "+" button with "+S" (green, add script) and "+F" (yellow, add folder)
- Custom styled delete dialog with cyberpunk theme (QDialog instead of QMessageBox)
- Context menu has "Add Script" and "Add Folder" options

---

## Issue 5: Settings Dialog

### Features Added
- Font family dropdown (QFontComboBox, non-editable, max-width ~180px)
- Bold checkbox
- Italic checkbox
- Checkbox styling matches Edit panel (yellow fill when checked)
- Hidden scrollbars
- Removed "Size:" label from window size row

---

## Issue 6: Context Menu

### Added Options
- "Reset Styles" - resets item to global defaults (preserves icon path)
