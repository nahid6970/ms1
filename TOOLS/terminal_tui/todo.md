# Task: Colorful workspace selector dropdown

User wants #workspace-selector-dropdown-content to look like the F1 manager modal:
- Use proj.cardTheme (bgColor, accentColor, textColor) to color each row
- Active dot colored based on the workspace's color scheme
- Current workspace gets a ▶ arrow icon at the front

## Tasks
- [X] Rewrite updateWorkspaceSelectorDropdown() to use cardTheme colors per row
- [X] Add ▶ indicator for currently active workspace
- [X] Color the active dot using accentColor (or contrasting color based on bg)
- [X] Show category badge if present
