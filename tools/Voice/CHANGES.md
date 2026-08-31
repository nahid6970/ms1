# Voice Input – Changes

## Button Vertical Alignment
- **Problem:** Language (BN/EN), G, C, and status buttons shifted vertically on startup or after clicking.
- **Fix:** Added `min-height/max-height` to inline stylesheets and call `setFixedSize` after every stylesheet update. All button sizes unified across `init_ui`, `_apply_button_geometry`, and `_set_status`.

## Window Position on Restart
- **Problem:** Closing in expanded mode and reopening in compact mode caused the window to appear at a different screen position.
- **Fix:** Saves `right_edge` (x + width) on every drag and on close. On startup, restores position as `right_edge - current_width`, keeping the window anchored to the right side regardless of mode.

## First Toggle Lag
- **Problem:** First expand/collapse after startup had a noticeable lag.
- **Fix:** Layout and position are computed before `show()` is called. A minimal deferred `_apply_button_geometry` call via `QTimer.singleShot(0)` handles the first-render alignment without causing window-level stutter.
- **Note:** A slight one-time lag on first toggle is a Qt widget initialization limitation, not fully eliminable.

## Status/Lang Gap Setting Not Applying
- **Problem:** Changing the status/lang gap in settings had no effect because `addSpacing` is a one-time layout insertion.
- **Fix:** Replaced `addSpacing` with a `QWidget` gap whose width is updated in `_apply_window_layout` whenever settings change.

## Right-Click Lang Button: Output Mode Toggle
- **Feature:** Right-clicking the `lang_btn` toggles between **Search** and **Clipboard** output mode without needing to expand the toolbar.
- **Search active** → orange border (`#FF8C00`)
- **Clipboard active** → cyan border (`#00BFFF`)
- Text color remains independent: `EN` = red, `BN` = green.
- State persists across restarts via config (`output_mode` key).
