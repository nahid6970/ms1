# Last Session Summary (Completed: 2026-08-11 00:10)

## Recent Implementation Context
- **All emojis replaced with crisp SVG icons** (no more clipped true-color emojis anywhere in the list):
  - Favourites, Startup & Exclusion keys use `🚀`/`🚫` Lucide SVGs rendered as `QTextDocument` image resources (`icon://rocket`, `icon://ban`), sized to the app font.
  - Rule sub-lines use small SVG badges: `Active in` → green check (`icon://check-sm`), `Inactive in` → red ban (`icon://ban-sm`).
  - Name column: favourite star (`icon://star`, yellow) and file-source (`icon://file`, cyan) icons, plus a larger star for the Favourites section header (`icon://star-lg`).
- **Rules-below layout for category rows**: Startup & Exclusion-Rules categories now show window context as dim `▸` sub-lines below the name (identical to Favourites), with a plain key cell (`🚀 Startup` / `🚫 Exclusion`), key column normalized to 170px, top-aligned cells.
- **Android-style toggle switches**: the enable/disable column now renders SVG pill toggles (knob slides left/right) instead of the ✅/❌ emoji, wrapped in the existing `toggle://` link.
  - **Configurable accent color**: Settings window → "Toggle Switch Color" (8 swatch options: Green/Blue/Cyan/Yellow/Orange/Red/Purple/Pink), default Green `#00E676`, persisted in `ahk_shortcuts.json` as `toggle_accent_color`, applied immediately via re-registered icon resources.
- **Row click targeting fix**: clicking empty space inside a row (right of short names, below rule sub-lines) now selects the row. `QTextBrowser` only fires `anchorClicked` for anchor text, so a new `_row_select_url_at(pos)` resolves the `select://` link from the document block under the cursor (verified against the block's layout rect so gaps between rows stay inert) and the viewport `eventFilter` routes non-anchor left-clicks to `handle_click`. Double-clicking empty space also opens the edit dialog. Toggle/section-header anchors and right-click menus are unaffected.
- **Infrastructure**: `render_svg_pixmap()` gained an optional `height` param for non-square pixmaps; icon sizes share helpers (`key_icon_size`, `rules_ban_size`, `name_icon_size`) so registered pixmaps always match `<img>` attrs; dead `.status-enabled/.status-disabled` CSS removed.
