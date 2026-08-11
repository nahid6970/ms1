# UI Visual Roadmap

This file tracks the next visual pass for the Python GUI.

## Direction

- Move from a stylized cyber look to a professional desktop product UI.
- Prioritize readability, hierarchy, and speed of use.
- Keep the app dense enough for power users, but remove visual noise.

## Problems To Fix

- Text is too small for comfortable scanning.
- The layout feels dense and repetitive.
- Related controls are not visually grouped enough.
- The toolbar is visually busy.
- The current color system does not communicate meaning clearly.

## Goals

- Make the UI readable at a glance.
- Improve hierarchy so important controls stand out.
- Use stronger spacing and section separation.
- Make the app feel polished, reliable, and intentional.
- Improve the overall layout without making the app slower to use.

## Typography

- Increase the base font size slightly across the app.
- Use a clearer typographic scale:
  - section titles larger
  - labels medium
  - inputs slightly larger than labels
- Add a font family dropdown in Settings so the user can choose a UI font.
- Prefer a professional UI font stack over decorative or high-contrast display styling.
- Keep monospace only where it helps with code or technical values.

## Color Semantics

- Use a neutral dark base with restrained contrast.
- Replace bright neon-heavy styling with a calmer professional palette.
- Surface colors:
  - app background: near-black charcoal
  - panels: slightly lighter charcoal
  - inputs: muted slate
- Semantic colors:
  - primary action: blue
  - success: green
  - warning: amber
  - destructive: red
  - info/focus: muted cyan
- Reserve strong accents for state, not decoration.
- Avoid using too many competing accent colors inside the same row.

## Suggested Changes

- Increase padding inside rows and panels.
- Add more vertical breathing room between rows.
- Group row controls into smaller visual clusters:
  - title block
  - payload block
  - action block
  - color/code block
- Make the toolbar smaller and cleaner.
- Use icon-only utility buttons with tooltips.
- Add stronger contrast between panel backgrounds and input fields.
- Use borders and separators sparingly.
- Keep highlighted borders only for active, selected, or hovered controls.
- Add a font family dropdown in Settings.
- Add a slightly larger default row height.

## Better Layout Ideas

- Replace the current long horizontal row layout with a card layout:
  - top line: title and row metadata
  - second line: label/text/action controls
- Or keep the single-line row, but split it into fixed-width columns:
  - title column
  - label/value column
  - action column
  - utilities column
- Add collapsible advanced sections for:
  - SVG editor
  - color pickers
  - trigger options
- Keep the default row editor simple and hide advanced controls unless needed.
- Consider a left-sidebar / right-workspace layout if the toolbar keeps growing.

## Component Style

- Use consistent button sizes and radii.
- Standardize spacing across all row controls.
- Make dropdowns, text fields, and action buttons visually aligned.
- Keep the profile selector prominent but not overpowering.
- Make the settings panel feel like a real preferences dialog instead of a hidden debug area.

## Future Refinements

- Add better row previews so users can identify content quickly.
- Add a tighter spacing mode for dense profiles.
- Add a larger readability mode for long editing sessions.
- Add hover highlighting for row sections.
- Add active-profile indicators in the toolbar.
- Add a cleaner empty-state message for new profiles and empty rows.
- Add a consistent icon set for toolbar and row utilities.
- Add a “compact / comfortable” density toggle.
- Add a better visual hierarchy for title rows versus action rows.

## Notes

- Any visual redesign should preserve the existing data model.
- Layout changes should not break saved profiles.
- The best path is probably an incremental UI pass, not a full rewrite.
- The new design should feel like a utility app, not a theme demo.
