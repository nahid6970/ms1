# Last Session Summary

## Core Accomplishments
1. **Side-by-Side Cascading Submenus**:
   - Replaced parent-hiding submenu flow and the `<-- Back` button with native-style side-by-side cascading submenus that open to the right.
   - Implemented automatic back-tracking: moving the mouse cursor back onto any parent menu window automatically hides its child submenus.
   - Bypassed backtrack closing when the pointer is hovering over the parent item that opened the current submenu.

2. **Hover Auto-Expansion & Validation**:
   - Submenus now automatically open on hover.
   - Prevented instant/accidental triggers by implementing a 400ms debouncing delay.
   - Added hover control verification: when the timer fires, the control under the cursor is checked to verify the mouse is still on the item.

3. **Layout Auto-Sizing**:
   - Removed hardcoded `w180` width limits which caused submenu arrows (`>`) to wrap.
   - Implemented dynamic layout calculations: controls render naturally, then their widths are updated to match the widest control + padding.

4. **Crash & Race Condition Fixes**:
   - Resolved AHK v2 "Error: Array is empty" in `GoBack()` by popping the stack parent atomically before any yield.
   - Resolved "Error: Gui has no window" by registering events immediately after GUI creation and wrapping the `.Show()` methods inside try-catch blocks.
   - Resolved AHK v2 "Error: Invalid callback function" by routing `SetTimer` through standard global proxy functions rather than static class methods.

## Files Modified
- `ahk_gui_pyqt.py`
