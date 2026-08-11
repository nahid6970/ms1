# UI/UX Design & Guidelines

## Overall Style

**Theme:** Dark cyberpunk style with cyan, yellow, red, green, and orange accents.

**General Rules:**

- Keep the interface sharp-edged.
- Avoid rounded boilerplate panel design.
- Use visible contrast for selected and disabled states.
- Prefer clear functional labeling over decorative text.

## Main Layout

**Structure:**

- Top toolbar with add, group toggle, colors, settings, restart, search, and generate actions
- Main `QTextBrowser` area showing shortcut lists
- Category grouping toggle changes how sections are rendered

**Sections:**

- Script shortcuts
- Context shortcuts
- Exclusion rules
- Background scripts
- Text shortcuts
- File shortcuts

## Shortcut Builder

**Layout:**

- Preview panel at the top
- Main keyboard grid in the center
- Navigation cluster and numpad cluster on the side
- Generic modifier strip at the bottom

**Behavior Notes:**

- Key buttons should not shift size when selected.
- Checked and unchecked states must keep the same geometry.
- Special keys like Backspace, Enter, and `\` need stable sizing.

## Color Rules

**Theme Palette:**

- Background: near-black
- Panels: dark gray / blue-black
- Accent cyan: primary interactive highlight
- Yellow: emphasis and generate actions
- Red: destructive or warning state
- Green: success and enabled state

**Guideline:**

- Keep selected states visible without changing control size.
- Disabled entries should stay readable, not washed out.

## Typography

**Preferred Fonts:**

- Consolas or similar monospaced font for code and shortcut labels
- UI labels can use system UI, but keep the overall tone consistent

## Interaction Rules

- Double-click selects and edits a shortcut.
- Right-click on a selected shortcut opens edit/duplicate/remove actions.
- Toggle icons should clearly show enabled vs disabled.
- Search should not destroy scroll position.

## Notes For Future UI Changes

- If a new control affects size hints, test selected and hovered states.
- If a button looks like it is shrinking, verify both CSS and Qt size policy.
- Keep new panels consistent with the existing dark theme.

