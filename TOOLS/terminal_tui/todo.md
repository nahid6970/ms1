# Task: Fix workspace selector dropdown issues

## Issues
1. Active dot color clashes with bg (yellow dot on yellow bg) - need contrasting dot color
2. ▶ arrow takes up space and shifts all non-current rows - fix with overlay/no-width approach
3. Add setting to hide category badge in the dropdown

## Tasks
- [X] Fix active dot: use white or dark color based on bg luminance, not accent color
- [X] Fix ▶ arrow: overlay it so it takes no layout space (non-current rows unaffected)
- [X] Add toggle in settings to hide/show category badge in workspace selector dropdown
