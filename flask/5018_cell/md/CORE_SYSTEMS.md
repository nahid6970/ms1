# Core Systems & Performance

## Font System
**Dual-Font Stack:** `Vrinda, 'Segoe UI', ...`
- **Vrinda:** Primary for Bangla.
- **Segoe UI:** Fallback/English.
- **JetBrains Mono:** Loaded via Google Fonts for code columns.
- **Nerd Font Support:** JetBrains Mono Nerd Font fallback added for icon glyphs (, , etc.)
  - Fallback chain: `'JetBrains Mono', 'JetBrainsMono Nerd Font', Vrinda, monospace`
  - Icons display if Nerd Font is installed locally
  - **Note:** Add a space after Nerd Font icons to prevent text overlap (e.g., " text" not "text")
**Toggle:** Disable Vrinda via Settings (applied as `.disable-vrinda`).

## Page Load Time Indicator
**Function:** Shows load time in sheet controls bar (e.g., "⏱️ 0.45s").
**Implementation:** Measured via `performance.now()` in `loadData()` after full render.

## Markdown Cell Height Adjustment
**Purpose:** Syncs height between raw input and markdown preview.
**Mechanism:** `adjustCellHeightForMarkdown()` measures both `scrollHeight`s and applies the `Math.max()` + 5px buffer to both.
**Details:** See `md/MARKDOWN_HEIGHT_FIX.md`.

## Dynamic Cursor & Click-to-Edit
**Purpose:** Precise cursor mapping from rendered preview back to raw text.
**Features:**
- Char-offset mapping in `handlePreviewMouseDown`.
- Custom 5px block cursor (`.custom-cursor`) via mirror element technique.
- Scroll stabilization via `keepCursorCentered`.
**Details:** See `md/CLICK_TO_EDIT_CURSOR_POSITIONING.md`.

## Settings & Global Preferences
- **Persistent:** Saved to `localStorage`.
- **Immediate:** Changes apply instantly to CSS variables (e.g., `--grid-line-color`).
