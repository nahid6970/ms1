# Vertical Side Button Pattern

This file documents the vertical side button pattern used for the `+` add control in the Python GUI.

## Purpose

- Provide a compact action button that sits beside a stacked control list.
- Use the full height of the control stack instead of occupying horizontal row space.
- Keep the main content area clean while still making the action easy to find.

## Visual Behavior

- The button is placed at the far right of the stacked list.
- The button text is rotated 90 degrees so it reads vertically.
- The button spans the full height of the stack.
- The label is minimal, often just `+`.
- Hover styling should remain simple and consistent with the rest of the UI.

## Layout Strategy

- Wrap the stacked controls and the vertical button in a single horizontal container.
- Give the stacked controls the stretch priority.
- Give the vertical button a fixed width and a dynamic height.
- Recalculate the height whenever items are added or removed from the stack.

## Qt/Python Notes

- A custom `QPushButton` paint event is useful when stylesheet rotation is not enough.
- Use a rotated painter transform to draw the label vertically.
- Use a `QStyleOptionButton` base render so the control still looks native.
- Keep the vertical label short to avoid clipping.

## HTML/CSS Notes

- A similar effect can be built with:
  - `writing-mode: vertical-rl;`
  - `transform: rotate(180deg);`
  - a fixed narrow width
  - a height that matches the stacked container
- If the button must span dynamic content, place it inside the same flex row or grid row as the stack and size it with the stack height.

## Reuse Checklist

- Decide whether the button should be:
  - a `+` only control
  - a text label
  - an icon
- Put it at the edge of the control cluster.
- Keep its width fixed.
- Compute height from the content stack.
- Ensure the click target stays large enough to use comfortably.
- Keep the rotated text short to prevent clipping.

## Practical Recommendation

- Use this pattern for "add", "insert", or "create" actions where the control applies to an entire stacked group.
- Avoid using it for dense text labels or long actions.
- Keep it as a secondary control, not the primary workflow entry point.
