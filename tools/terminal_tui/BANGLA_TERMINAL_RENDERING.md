# Bangla Rendering in Terminal Panes

## Status

**Working fix implemented (2026-10-12):** Bangla text now renders correctly inline in the main terminal. No toggle button, no separate view — it just works automatically.

## Why xterm.js Breaks Bangla

xterm.js assigns each character to a fixed-width cell. Bangla shaping requires combining multiple codepoints (base chars + matras + hasants) into single glyphs that can reorder visually — this is fundamentally incompatible with the cell model. No font choice fixes this.

Previous attempts that did not work:
1. Vrinda / Nirmala UI in the terminal font stack — glyphs present but spacing broken.
2. xterm.js Unicode 11 width handling — no effect on shaping.
3. Canvas/WebGL renderer — still cell-based.
4. Full-screen overlay panel — worked for reading but was a separate view, not inline.

## The Inline Row Overlay Fix

After each `pty-output` write and on every scroll/resize, `renderBanglaRows(term, paneDiv)` runs. It:

1. Reads the xterm.js buffer for only the **currently visible rows** via `buf.getLine(r)` / `line.getCell(c)`.
2. For each visible row, builds an HTML string by concatenating cell characters with inline SGR color spans (16-color palette + RGB truecolor + bold/italic/underline).
3. If the row contains **any Bangla character** (U+0980–U+09FF), creates an absolutely-positioned `<div class="bangla-row-overlay">` inside `.xterm-screen` at the exact pixel position of that row, using the cell height from `term._core._renderService.dimensions`.
4. The overlay div uses `font-family: 'Nirmala UI', 'Vrinda', ...` so the browser shapes the entire Bangla text run correctly.
5. Rows with no Bangla are left completely alone — xterm.js renders them normally.
6. Overlays are `pointer-events: none` so all keyboard input and mouse interaction passes through to xterm.

The result: Bangla rows show correctly shaped text in the main terminal. English rows, prompts, ANSI box-drawing, colors — everything else is untouched.

## Hooks

- `pty-output` write callback → `renderBanglaRows`
- `.xterm-viewport` scroll event → `renderBanglaRows`
- `paneTerm.onResize` → `renderBanglaRows`

## Files Modified

- `templates/index.html` — CSS (`.bangla-row-overlay`), `renderBanglaRows()`, `_banglaRowHtml()`, `BANGLA_RE`, `BANGLA_ANSI_FG` constants, three hook call sites.
- `BANGLA_TERMINAL_RENDERING.md` — this file.
