# Recent Handoff

## 1. Project DNA (Permanent)
PyQt6 status bar desktop app (`mypygui_qt.py`) for system automation, script monitoring, and launcher controls, driven by config (`mypygui_config.json`) and pwsh-launching helpers (`run_command`, `open_git_cmd`).

## 2. Latest Implementation
All in `mypygui_qt.py`:
- **Reverted to komorebi workspace widget** (GlazeWM code removed, commit aedde00f7).
- KomorebiWidget layout label: left-click opens layout menu; right-click on label suppressed (PreventContextMenu); hover shows layout-only tooltip (e.g. "Layout: BSP") instead of the workspace list; widget/dots hover still shows workspace list.
- **NEW Komorebi workspace widget** (`KomorebiWidget`): 3 clickable dots + layout label, added in `_build_left` right after the uptime clock. Left-click dot → `komorebic focus-workspace N`. Left-click layout label or right-click dots → menu: change-layout (bsp/columns/rows/vertical-stack/horizontal-stack/ultrawide-vertical-stack/grid/right-main-vertical-stack) + Flip, Toggle Float/Monocle/Pause. Hover tooltip shows per-workspace name, window count (tiled only), layout, ACTIVE/idle. Polls `komorebic state` every 2s in a daemon thread → `_komorebi_queue` → `_drain_komorebi_queue` (300ms timer). **Fast-refresh kick**: every widget action calls `_kick_komorebi_refresh(8s)`; the loop polls 0.3s while kicked, and chunks idle sleep in 0.5s slices so a kick mid-sleep is noticed within ~0.5s. Contents margins (10,0,1,0) match the pagination arrows' padx.
- **NEW KomorebiAppsWidget** (next to the dots widget): 🖥 + count of ALL open windows across ALL workspaces. Left/right-click → menu grouped by workspace (plain text; ● active / ○ idle headers) listing every `exe — title`; click → `komorebic focus-workspace N` + delayed (250ms) `ShowWindow(SW_RESTORE)` + `SetForegroundWindow` to jump to that app. Hover tooltip lists them too. Fixes the duplicate-launch problem (taskbar hides inactive-workspace windows because komorebi config already has `window_hiding_behaviour: 'Cloak'`).
- Embedded the pwsh-profile `gitter` fn as `_GIT_SYNC_PS` + `git_sync(path)`; left-click commit now shows the branch.
- `git pull --rebase --autostash` before push; fixed infinite commit-retry loop on clean trees.
- Repo labels: no ⇡/⇣ arrows (they flashed mid-push); info still in hover tooltip.
- Right-click power menu `_show_git_menu`: Commit&Push, Pull, Push, Stash, Pop, Discard, Force Push (overwrite remote), Force Pull (overwrite local), Force Checkout (lazygit-F style, discards edits keeps commits), Delete Lock Files, Status&Diff, lazygit, GitHub, Switch Branch, Set/Reset Branch Dot Color.
- Branch indicator `GitIconLabel`: dot (bottom-right) or underline (Settings → BRANCH INDICATOR), colored via `branch_color` (config override → fixed palette → hash).
- Rich-text tooltip: status-colored files (A green, M yellow, D pink, ?? red, R/C cyan, U magenta) + `● branch` in its assigned color.

## 3. Critical Context
- `check_git_status` / `check_komorebi_status` (worker threads) queue dicts; `_drain_git_queue` / `_drain_komorebi_queue` (GUI timers) apply them. Komorebi queue item: {ok, workspaces(≤3), focused, focused_layout, paused}.
- `_GIT_SYNC_PS` = adjacent Python literals + `.replace("{path}", ...)` (not an f-string → braces literal).
- Native Qt tooltips need window focus here → custom `_TipFilter` + always-on-top `_tip_label` (`Qt.ToolTip`, WA_ShowWithoutActivating); git labels + komorebi widget/labels/buttons carry `_tip_text`.
- Komorebi layout label maps names via `_komorebi_layout_short` (BSP/COL/ROW/VSTK/HSTK/ULTW/GRID/RMAIN); shows ⏸ when paused; `focused_layout` reported separately so layout shows even when focused workspace is beyond the 3 visible dots.
- Config keys: `branch_colors`, `git_indicator_style`, `git_status_colors`.
- File is CRLF; multi-line edits are safest via temp fix scripts.

## 4. Pending Task
Run the GUI live and verify the komorebi widget (dots reflect workspaces, left-click switches, right-click changes layout); then consider making komorebi dot/label styling configurable via `static_bindings` like other widgets.
