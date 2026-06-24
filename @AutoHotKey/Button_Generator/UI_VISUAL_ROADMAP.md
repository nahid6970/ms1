# UI Visual Roadmap

This file tracks the next visual pass for the Python GUI.

## Problems To Fix

- Text is too small for comfortable scanning.
- The layout feels dense and repetitive.
- The current theme is functional but too flat.
- Related controls are not visually grouped enough.
- The toolbar could be clearer and easier to use.

## Goals

- Make the UI readable at a glance.
- Improve hierarchy so important controls stand out.
- Use stronger spacing and section separation.
- Keep the cyberpunk feel, but make it cleaner and less noisy.
- Improve the overall layout without making the app feel larger or slower.

## Suggested Changes

- Increase the base font size slightly across the app.
- Use a clearer typographic scale:
  - section titles larger
  - labels medium
  - inputs slightly larger than labels
- Increase padding inside rows and panels.
- Add more vertical breathing room between rows.
- Group row controls into smaller visual clusters:
  - title block
  - payload block
  - action block
  - color/code block
- Make the toolbar more compact and easier to scan.
- Use consistent icon-only utility buttons with tooltips.
- Add stronger contrast between panel backgrounds and input fields.
- Use highlighted accent borders only on active or important controls.
- Add a font family dropdown in Settings so the whole app can switch typefaces more easily.

## Better Layout Ideas

- Replace the current long horizontal row layout with a two-line card layout:
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

## Color Direction

- Keep the dark base, but use a softer panel contrast.
- Make cyan the primary interactive accent.
- Reserve yellow for headers and focus states.
- Use green only for success or generation states.
- Use orange/red sparingly for warnings and destructive actions.
- Reduce the number of competing accent colors in one row.
- Let the font family be configurable from the UI so readability and style can be tuned without editing code.

## Future Refinements

- Add better row previews so users can identify content quickly.
- Add a tighter spacing mode for dense profiles.
- Add a larger readability mode for long editing sessions.
- Add hover highlighting for row sections.
- Add active-profile indicators in the toolbar.
- Add a cleaner empty-state message for new profiles and empty rows.

## Notes

- Any visual redesign should preserve the existing data model.
- Layout changes should not break saved profiles.
- The best path is probably an incremental UI pass, not a full rewrite.
