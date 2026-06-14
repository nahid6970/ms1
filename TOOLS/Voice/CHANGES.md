# Voice Input – Recent Fixes

## Button Vertical Alignment
- **Problem:** Language (BN/EN), G, and C buttons appeared slightly lower than the status icon on startup and after clicking.
- **Fix:** Added `min-height: 18px; max-height: 18px` to inline button stylesheets, and re-apply `setFixedSize(..., 18)` after every stylesheet update so Qt can't override the height.

## Window Position on Restart
- **Problem:** Closing in expanded mode and reopening in compact mode (or vice versa) caused the window to appear at a different screen position.
- **Fix:** Now saves `right_edge` (x + width) instead of left `x` on every drag and on close. On startup, position is restored as `right_edge - current_width`, keeping the window anchored to the same right-side position regardless of mode.

## First Toggle Lag
- **Problem:** The first expand/collapse after startup had a noticeable lag; subsequent ones were fast.
- **Cause:** Qt lazily initializes hidden widgets on first paint. Layout and position are now fully computed before `show()` is called, eliminating the post-render relayout stutter.
- **Note:** A very slight one-time lag may still occur due to Qt's internal widget initialization — this is a Qt limitation and not fully eliminable without complex workarounds.
