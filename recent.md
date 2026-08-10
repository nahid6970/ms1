# Recent Handoff

## 1. Project DNA (Permanent)
PyQt6 status bar desktop app (`mypygui_qt.py`) for system automation, script monitoring, and launcher controls, driven by config (`mypygui_config.json`) and pwsh-launching helpers (`run_command`, `open_git_cmd`).

## 2. Latest Implementation
**Switched WM: komorebi → GlazeWM.** All in `mypygui_qt.py` + `~/.glzr/glazewm/config.yaml`:
- **GlazeWM config** mirrors komorebi.json: `hide_method: cloak` + `show_all_in_taskbar: false` (was `window_hiding_behaviour: Cloak`), `inner_gap: 10px`, outer gaps 15/30/30/15, square borders 2px, `focus_follows_cursor: false`, workspaces 1–9 with display names I/II/III for 1–3, alt+1..9/alt+hjkl keybindings, and window_rules ported from komorebi `ignore_rules` (ignore) + `tray_and_multi_window_applications` (set-floating). Added missing: `CASCADIA_HOSTING_WINDOW_CLASS` + `explorer` → ignore, `WhatsApp.Root` → floating (user chose faithful port = terminal floats untiled, like komorebi). Live reloaded via `glazewm command wm-reload-config`.
- **`GlazeWmWidget`** (was KomorebiWidget): workspace dots + tiling-direction label (H/V/⏸). Left-click dot → `glazewm command focus --workspace N`; right-click menu → set/toggle tiling direction, set-floating/tiling, toggle-fullscreen, pause/reload/redraw. State from `glazewm sub --events workspace_activated,...` → `_glaze_queue` → `_drain_glaze_queue` (100ms timer).
- **NEW: always ≥3 workspace dots** — `_glaze_build_state` now pads to at least I/II/III (empty entries) when fewer workspaces are active, reads display names from config.yaml via `_glaze_workspace_display_names()` (mtime-cached `_glaze_display_cache`), sorts dots numerically. GlazeWM's `query workspaces` only returns ACTIVE workspaces, hence the padding.
- **FIXED slow workspace updates** — `glazewm sub --events` needs SPACE-separated names; the comma-joined list made the sub exit instantly (no live events), so the widget only refreshed via slow fallback polling. Now: space-separated events stream live, each event = ONE `query workspaces` (tilingDirection read from focused workspace JSON; removed `_glaze_focused_tiling_dir`), paused state cached (`_glaze_paused_cache`, refreshed on `pause_changed`), 120ms debounce collapses switch bursts to 1 rebuild, drain timer 100ms→40ms.
- **Layout label UX**: the H/V label's menu now opens on LEFT click (`_dir_lbl_left_click`), right-click on it does nothing (`PreventContextMenu`); menu no longer has the workspace switcher (dots handle switching) — only tiling direction, window state, and WM controls. Label tooltip is layout-only (`Tiling: Horizontal/Vertical/—`); the workspace-list tooltip stays on the widget/dots.
- **NEW `GlazeAppsWidget`** (next to the dots widget): 🖥 + count of ALL open windows across ALL workspaces. Left/right click → menu grouped by workspace (disabled header `N  I/II/III`, entries `exe — title`); click entry → `glazewm command focus --container-id <id>` + delayed (180ms) `ShowWindow(SW_RESTORE)` + `SetForegroundWindow(handle)` to jump to that exact window (glazewm auto-switches workspace). Hover tooltip lists them grouped (● active ws / ○ idle, ● focused window). Apps come from the SAME `query workspaces` poll (children) — zero extra subprocesses. Labels are `WA_TransparentForMouseEvents`; left-click handled via `mouseReleaseEvent` + right-click via `customContextMenuRequested`.
- Earlier session (komorebi era, still valid): gitter-embedded commit+push with branch display, `git pull --rebase --autostash`, force push/pull/lazygit-F checkout in right-click menu, `GitIconLabel` branch dot/underline + rich-text status tooltips.

## 3. Critical Context
- GlazeWM worker: `_glaze_poll()` (`glazewm query workspaces`), `_glaze_focused_tiling_dir()`, `_glaze_status_loop(q)` (sub event stream), `_glaze_build_state()` → queue item {ok, workspaces, focused_name, tiling_dir, paused}. Widget var is still `self.komorebi_widget` in `_build_left`.
- `_GIT_SYNC_PS` = adjacent Python literals + `.replace("{path}", ...)` (not an f-string → braces literal).
- Native Qt tooltips need window focus → custom `_TipFilter` + always-on-top `_tip_label`; widgets carry `_tip_text`.
- Config keys: `branch_colors`, `git_indicator_style`, `git_status_colors`.
- File is CRLF; multi-line edits are safest via temp fix scripts (run with python, then delete).

## 4. Pending Task
Restart the app to see the 3 workspace dots (I/II/III) now that GlazeWM is live; verify dot switching + tiling-direction label; confirm CASCADIA/terminal floats as intended after reload.
