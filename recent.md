# Recent Handoff

## 1. Project DNA (Permanent)
PyQt6 status bar desktop app (`mypygui_qt.py`) for system automation, script monitoring, and launcher controls, driven by config (`mypygui_config.json`) and pwsh-launching helpers (`run_command`, `open_git_cmd`).

## 2. Latest Implementation
All in `mypygui_qt.py`:
- Embedded the pwsh-profile `gitter` fn as `_GIT_SYNC_PS` + `git_sync(path)`; left-click commit now shows the branch.
- `git pull --rebase --autostash` before push; fixed infinite commit-retry loop on clean trees.
- Repo labels show ahead/behind `⇡N⇣M`; custom focus-free hover tooltip (branch + changed files).
- Right-click power menu `_show_git_menu`: Commit&Push, Pull, Push, Stash, Pop, Discard, Status&Diff, lazygit, GitHub, Switch Branch (local/remote + New Branch), Set/Reset Branch Dot Color.
- Branch indicator `GitIconLabel`: dot (bottom-right) or underline (Settings → BRANCH INDICATOR), colored via `branch_color` (config override → fixed palette → hash).
- Rich-text tooltip: status-colored files (A green, M yellow, D pink, ?? red, R/C cyan, U magenta) + `● branch` in its assigned color.

## 3. Critical Context
- `check_git_status` (worker thread) queues dicts {name,text,color,branch,indicator_style,tooltip}; `_drain_git_queue` (GUI, 100ms timer) applies them.
- `_GIT_SYNC_PS` = adjacent Python literals + `.replace("{path}", ...)` (not an f-string → braces literal).
- Native Qt tooltips need window focus here → custom `_TipFilter` + always-on-top `_tip_label` (`Qt.ToolTip`, WA_ShowWithoutActivating); git labels carry `_tip_text`.
- Config keys: `branch_colors`, `git_indicator_style`, `git_status_colors`.
- File is CRLF; multi-line edits are safest via temp fix scripts.

## 4. Pending Task
Run the GUI live and verify dot/underline, tooltip colors, menus, branch switching, and settings; then consider syncing these git features to the other mypygui variants (Testing/, test_project/).
