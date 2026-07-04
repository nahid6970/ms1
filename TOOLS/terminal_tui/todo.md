# Task: Snippet bg/fg color support

User wants to be able to specify background and foreground colors for snippets using the `;;` syntax:
- `command ;; description bg=red fg=green`
- `command ;; description bg=#445869 fg=#998689`
- Colors can be CSS color names or hex codes
- Both `bg` and `fg` are optional and independent

## Tasks
- [X] Parse `bg=` and `fg=` from the snippet label/description part in `addSnippet()`
- [X] Store `bg` and `fg` on the snippet object in localStorage
- [X] Apply colors when rendering snippet rows in `renderSnippetList()`
- [X] Update the format hint in the popover UI to show the new syntax
