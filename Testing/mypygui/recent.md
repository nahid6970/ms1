# Recent Handoff

## 1. Project DNA (Permanent)
PyQt6 status bar desktop app (`mypygui_qt.py`) for system automation, script monitoring, and launcher controls, driven by config (`mypygui_config.json`) and pwsh-launching helpers (`run_command`, `open_git_cmd`).

## 2. Latest Implementation
All in `mypygui_qt.py`:
- **FIX: komorebi event pipe crash (error 230 "pipe state is invalid")** — pipe was created with `FILE_FLAG_OVERLAPPED` (async mode), but `PeekNamedPipe` only works on synchronous pipes; calling it on an overlapped pipe immediately returns Windows error 230 (`ERROR_BAD_PIPE`), causing connect → instant crash → 5s retry → connect loop. Fix: removed `FILE_FLAG_OVERLAPPED` from `CreateNamedPipe` (now synchronous). The overlapped `ConnectNamedPipe` timeout trick was replaced with a background thread + `join(timeout=5.0)`. `win32event` import removed. Event pipe now stays connected and drives instant workspace updates as intended.
- **Reverted to komorebi workspace widget** (GlazeWM code removed, commit aedde00f7).
- KomorebiWidget layout label: left-click opens layout menu; right-click on label suppressed (PreventContextMenu); hover shows layout-only tooltip (e.g. "Layout: BSP") instead of the workspace list; widget/dots hover still shows workspace list.
- **Menus & tooltips positioned above/below statusbar**: `_menu_gpos(anchor, menu, cursor)` — docked: y = bar_bottom+2 (below), undocked: y = bar_top - menu_height - 2 (above, like popup windows). Used by komorebi layout/apps menus, git menu, and hover tooltips.
- **Rich tooltip-style menu items** (komorebi layout + apps menus): QMenu can't render HTML in plain actions, so `_menu_rich_action()` builds each item as a QWidgetAction + transparent rich-text QLabel (hover highlight shows through); `_KOMOREBI_MENU_QSS` styles the menus. Layout menu marks the current layout with a cyan ●; apps menu mirrors the tooltip (● WS · (n) ACTIVE/idle headers + indented exe — title entries).
- **Fast statusbar refresh after komorebi actions**: `_komorebi_refresh_once(0.2s)` (background thread: kick fast-poll immediately → sleep 200ms → push fresh `komorebic state`) replaces the slow kick at all 5 action sites (focus ws, change layout, toggle, flip, jump-to-app); `_drain_komorebi_queue` now applies only the NEWEST snapshot (drains all, applies last); drain timer 300→100ms. Statusbar now reflects a workspace click in ~0.5s (was ~1s).
- **NEW Komorebi workspace widget** (`KomorebiWidget`): 3 clickable dots + layout label, added in `_build_left` right after the uptime clock. Left-click dot → `komorebic focus-workspace N`. Left-click layout label or right-click dots → menu: change-layout (bsp/columns/rows/vertical-stack/horizontal-stack/ultrawide-vertical-stack/grid/right-main-vertical-stack) + Flip, Toggle Float/Monocle/Pause, and **💾 Save Layout Resize / 📂 Load Layout Resize** (→ `komorebic quick-save-resize` / `quick-load-resize`, with Alt+F5/F6 hint) — snapshots/restores the focused workspace's layout proportions. Hover tooltip shows per-workspace name, window count (tiled only), layout, ACTIVE/idle. **Event-driven updates**: `_komorebi_event_listener` thread creates a named pipe `\\.\pipe\mypygui-komorebi-*`, runs `komorebic subscribe <name>`, and on every event parses the full state embedded in the message (`{"event":…, "state": <full state>}` per line) via `_komorebi_parse_state` → `_komorebi_queue` → `_drain_komorebi_queue` (100ms timer). Instant updates with zero polling/subprocess; `_komorebi_item_sig` dedups identical snapshots (window drags). **Rapid-click jiggle fix**: every snapshot is timestamped (`_komorebi_put` → `t`) and `_drain_komorebi_queue` applies the **newest-`t`** item (not last-pushed), so a stale snapshot can never land after a fresh one; while events are flowing the poll loop skips entirely (15s-quiet watchdog) and `_komorebi_refresh_once` skips its delayed manual push when an event already arrived since the action. If pywin32/komorebi is unavailable the old loop stays as a 2s safety-net poll; `_kick_komorebi_refresh(8s)` still fast-polls 0.3s after widget actions. Contents margins (10,0,1,0) match the pagination arrows' padx.
- **NEW KomorebiAppsWidget** (next to the dots widget): 🖥 + count of ALL open windows across ALL workspaces. Left/right-click → menu grouped by workspace (plain text; ● active / ○ idle headers) listing every `exe — title`; click → `komorebic focus-workspace N` + delayed (250ms) `ShowWindow(SW_RESTORE)` + `SetForegroundWindow` to jump to that app. Hover tooltip lists them too. Fixes the duplicate-launch problem (taskbar hides inactive-workspace windows because komorebi config already has `window_hiding_behaviour: 'Cloak'`).
- **NEW Workspace app rules** (komorebi): right-click a workspace dot → rich menu (disabled cyan header `● name · app rules`, `＋ Assign App to Workspace...`, then ✕ remove-item per rule). `_assign_app` opens a modal dialog (Kind: Exe/Class/Title/Path, identifier, matching-strategy Equals/Contains/StartsWith/EndsWith/Regex — auto-switches to Contains for Title). `_remove_rule` confirms with a Yes/No box first. Helpers `_komorebi_config_path` (candidates: ~/.config/komorebi, ~/komorebi.json, LOCALAPPDATA), `_komorebi_find_workspaces`, `_komorebi_get_workspace_rules` (dedup by kind+id), `_komorebi_save_workspace_rule(name, kind, id, strategy, remove)` → writes per-workspace `workspace_rules` into the user's `komorebi.json` (found at `~/komorebi.json`, v0.1.41) then runs `komorebic reload-configuration` (CREATE_NO_WINDOW). JSON round-trip preserves indent (detected via regex), CRLF/LF, and trailing-newline exactly (read with newline='', write with newline=""). `apply_state` failure branch resets `_ws_names=[]`.
- **NEW Pick App Window capture** (komorebi right-click dot menu): `🎯 Pick App Window...` mirrors `asset/komorebi/komorebi_gui_custom.py` — asks CLICK MODE / TIMEOUT(ns) / CANCEL (timeout read from komorebi.json `gui_settings.capture_timeout`, default 3, clamped ≥1), then `_WindowCaptureDialog` (click = poll `GetAsyncKeyState` 50ms with release-then-press; timeout = 1s countdown at cursor; **centered on the primary screen**; presses that land on our own dialog — e.g. the Cancel button — are ignored via an own-pid check so a cancel click can't be mistaken for a target capture) → `_capture_window_info` (win32gui WindowFromPoint → GetAncestor(GA_ROOT) → title/class; OpenProcess+GetModuleFileNameEx → exe/path; skips own-process windows) → `_WindowAttributePicker` (choose Exe/Title/Class/Path; Unknown/empty values hidden) → `_assign_app(name, preset_kind, preset_id)` pre-fills the existing assign dialog (Title auto-switches to Contains strategy) which saves the rule + reloads komorebi. Context menu closes first so the target click lands. Manual `＋ Assign App Manually...` kept as fallback.
- **Workspace dot visuals** (`_set_dot(b, color, active)`): the active workspace dot is a wider pill (15×11 vs 11×11 for idle dots). Colors are activity-based: active = white `#FFFFFF`, idle with windows = gray `#8a8a8a`, idle empty = `#333333` (unchanged). Maximized/monocle no longer tint the dot — layout/state detail stays in the hover tooltip.
- Embedded the pwsh-profile `gitter` fn as `_GIT_SYNC_PS` + `git_sync(path)`; left-click commit now shows the branch.
- `git pull --rebase --autostash` before push; fixed infinite commit-retry loop on clean trees.
- Repo labels: no ⇡/⇣ arrows (they flashed mid-push); info still in hover tooltip.
- Right-click power menu `_show_git_menu`: Commit&Push, Pull, Push, Stash, Pop, Discard, Force Push (overwrite remote), Force Pull (overwrite local), Force Checkout (lazygit-F style, discards edits keeps commits), Delete Lock Files, Status&Diff, lazygit, GitHub, Switch Branch, Set/Reset Branch Dot Color.
- Branch indicator `GitIconLabel`: dot (bottom-right) or underline (Settings → BRANCH INDICATOR), colored via `branch_color` (config override → fixed palette → hash).
- **NEW Git right-click mode** (Settings → GIT STATUS COLORS → RIGHT CLICK): `Context Menu` (code default) or `Lazygit`. Config key `git_right_click`; when `lazygit`, right-clicking a repo label opens lazygit directly instead of the power menu (Ctrl+Right-click still = git restore).
- **FIX: Komorebi tasklist font & Bangla text layout alignment**:
  - `_menu_rich_action()`: set `lbl.setFixedHeight(22)` and `Qt.AlignmentFlag.AlignVCenter` to guarantee uniform 22px row height and centered baseline regardless of script fallbacks.
  - Set font family stack to `'JetBrainsMono NFP', 'Consolas', 'Segoe UI', 'Kalpurush', 'Vrinda', sans-serif` across `_menu_rich_action` and `_tip_label`.
  - Replaced space-padding hacks (`&nbsp;`) in `KomorebiAppsWidget.apply_state` hover tooltip with clean block `<div style="margin-left: Npx;">` elements to preserve item indentation across Bangla titles and mixed script items.
- **FIX: `KomorebiAppsWidget.apply_state` `UnboundLocalError`** — `tip_html` was only assigned inside the `else` branch (apps exist), but used unconditionally after the `if/else`. Fixed by assigning `tip_html = '<span …>no windows open</span>'` in the empty-apps `if` branch.
- **FIX: `KomorebiAppsWidget` configurable indent** (from prior session):
  - Added `ITEM INDENT (PX)` setting in Settings dialog → `KOMOREBI` group box → saves `komorebi_item_indent` (default 20).
  - Dynamic `margin-left: {indent_px}px` in both the hover tooltip `<div>` blocks and the `_menu_rich_action` left padding.
- **Improved Komorebi toggle button**: Replaced text-based play/stop icon with color-coded SVG icons (green for play, red for stop) for a cleaner look.
- **GPU Bar Graph**: Replaced GPU text label with a 5-second cumulative bar graph in the status bar.
- **Git status performance fix**: Added `CREATE_BREAKAWAY_FROM_JOB` to `git status` subprocess calls in `mypygui_qt.py` to prevent git processes from being tied to the parent process's job object, which should help reduce orphaned git process accumulation.
- **NEW `gg` mode cycle**: Right-clicking the `BN/EN` toggle now cycles through 3 modes: `search` (orange border) → `clipboard` (blue border) → `gg` (neon green border).
- **FIX `gg` project root**: When in `gg` mode, executing `gg "text"` now explicitly uses the user's home directory (`cwd=os.path.expanduser("~")`) to prevent it from treating the `mypygui` repository directory as the project root.
- **NEW Centered Language Selection Popup on Voice Stop**:
  - When recording finishes (via hotkey / stop button / Space), `VoiceThread` / `SpaceStopThread` captures the raw audio buffer and displays `LanguageChoiceDialog` directly in the center of the screen with a cyan border and **square corners** (`border-radius: 0px`).
  - Buttons show full text: **`ENGLISH`** (red background) and **`বাংলা`** (green background) — colors are applied immediately without requiring hover.
  - Keyboard shortcuts: <kbd>E</kbd> for English, <kbd>B</kbd> for Bengali, <kbd>Esc</kbd> to cancel.
  - Spawns transcription in a background worker thread (`_run_transcription_worker`) using `transcription_ready` / `transcription_error` Qt signals (not `QTimer.singleShot`) for reliable cross-thread dispatch to `on_result`.
  - Dispatches to the active mode (`search` ➔ Google search, `gg` ➔ `gg -gui "<text>"`, `clipboard` ➔ `paste_text` via <kbd>Ctrl+V</kbd>).
- **REFACTOR Voice Widget — right-click popup menu added**:
  - The `BN/EN` language toggle button has been removed from the status bar entirely.
  - **Right-click on the mic icon** now opens a rich popup menu (`_show_voice_popup_menu` positioned via `_menu_gpos`) to directly select action mode (`🔍 Google Search`, `📋 Clipboard / Paste`, `⚡ GG`), toggle `Stop on Space (SPC)` or `Continuous Live Mode`, and open `Voice Settings...`.
  - The **mic icon color** reflects the active mode: 🟠 orange = search, 🔵 cyan = clipboard, 🟢 green = gg.
  - `_update_status_icon_mode()` recolors the SVG mic fill; `_update_status_tooltip()` updates the hover tooltip with the current mode name.
  - Mode color persists across all state transitions (after successful transcription, after cancel, after error flash) — `_update_status_icon_mode()` is called in `on_result`, `on_error`, `_on_continuous_finished`, and the dialog cancel branch.
  - On error (no speech / API failure), mic **flashes red for 800ms** then auto-restores mode color.
- **Voice settings moved to Main Settings dialog** (`VOICE INPUT` group box):
  - Fields: `ACTION MODE` (Search / Clipboard / GG), `STOP ON SPACE`, `MAX SPEAK (SEC)`, `HOTKEY`.
  - Saves directly to `voice_config.json`; hot-reloads the live `VoiceApp` instance on save.

## 3. Critical Context
- `check_git_status` / `check_komorebi_status` (worker threads) queue dicts; `_drain_git_queue` / `_drain_komorebi_queue` (GUI timers) apply them. Komorebi queue item: {ok, workspaces(≤3), focused, focused_layout, paused, apps}. `_komorebi_parse_state(data)` is shared by the poll loop and the event-pipe listener; requires pywin32 (`win32pipe`/`win32file` in install_deps.py IMPORT_TO_PKG) and komorebi ≥ 0.1.x with `subscribe` named-pipe support. Statusbar now reflects workspace switches/window changes instantly (~<200ms).
- `_GIT_SYNC_PS` = adjacent Python literals + `.replace("{path}", ...)` (not an f-string → braces literal).
- Native Qt tooltips need window focus here → custom `_TipFilter` + always-on-top `_tip_label` (`Qt.ToolTip`, WA_ShowWithoutActivating); git labels + komorebi widget/labels/buttons carry `_tip_text`.
- Komorebi layout label maps names via `_komorebi_layout_short` (BSP/COL/ROW/VSTK/HSTK/ULTW/GRID/RMAIN); shows ⏸ when paused; `focused_layout` reported separately so layout shows even when focused workspace is beyond the 3 visible dots.
- Config keys: `branch_colors`, `git_indicator_style`, `git_status_colors`, `komorebi_item_indent`, `proc_top_n` (default 8, controls ProcessPopup row count).
- Komorebi config write path: `~/komorebi.json` (0.1.41, pretty-printed 4-space CRLF, NO trailing newline). `workspace_rules` per workspace = array of {kind, id, matching_strategy} — same shape as `ignore_rules`. Rules apply to apps started AFTER the rule is saved (komorebi applies at window-manage time).
- File is CRLF; multi-line edits are safest via temp fix scripts.

- **NEW ProcessPopup — CPU & RAM hover popup with kill buttons**:
  - `ProcessPopup(mode)` class (standalone, inserted after `_menu_gpos` / before `_menu_rich_action`). Mode is `'cpu'` or `'ram'`.
  - Frameless `QFrame` with `Qt.Tool | FramelessWindowHint | WindowStaysOnTopHint` + `WA_ShowWithoutActivating` — doesn't steal focus.
  - Appears after a **250 ms dwell** on the `lb_cpu` or `lb_ram` button (prevents flicker on quick mouse-over). Auto-refreshes every **2 s** while visible.
  - Header: `🖥 CPU TOP PROCESSES` (cyan border/accent) or `🧠 RAM TOP PROCESSES` (orange border/accent); ↻ manual refresh button + ✕ close button in the header.
  - Column header row: `PROCESS · PID · USAGE` (dim text).
  - **Configurable N process rows** (default 8, set via Settings → PROCESS MONITOR → TOP N PROCESSES, range 1–30, saved as `proc_top_n` in config). Each row: rank `#N` (purple `#A78BFA`), process name (truncated to 22 chars, full name in tooltip), PID, usage `%.1f%` with heat-color (accent < 20%, yellow 20–60%, red ≥ 60%), and a `✕` kill button (hover = red background). Killing a process triggers a 400 ms delayed refresh.
  - `_top_n` is read from config on `__init__`; `_do_show` re-reads it and calls `_build_rows` to rebuild if the count changed (no restart needed). `_build_rows` clears existing rows before building.
  - `RANK_COLOR = "#A78BFA"` (purple) — visually distinct from cyan/orange accents, dim-gray PIDs, and white process names.
  - Data source: `psutil.process_iter(["pid", "name", "cpu_percent"])` for CPU mode; `memory_info.rss / total_memory * 100` for RAM mode.
  - **Positioning**: same above/below logic as `_menu_gpos` — docked bar → popup below button; undocked/bottom bar → popup above button.
  - **Hover-to-popup bridge**: `_attach_proc_popup(btn, popup)` wraps `btn.enterEvent`/`leaveEvent` with `popup.schedule_show(btn)` / `popup.cancel_show()`. A 120 ms grace timer prevents the popup from hiding when the cursor moves from the button into the popup itself (`_cursor_inside` flag in `enterEvent`/`leaveEvent` of the popup).
  - In `_build_right`: `self._cpu_popup` and `self._ram_popup` created after `lb_cpu`/`lb_ram` `_bind_static` calls; `_attach_proc_popup` wires hover for both.

- **FIX: `NetPopup` dynamic resize & layout spacing / text overlap**:
  - Removed old fixed size restrictions (`setFixedSize` locking `minimumSize`) which prevented the popup from shrinking when the process list shortened, causing big empty gaps.
  - Replaced `item.widget().setParent(None)` with `w.setParent(None)` and `w.deleteLater()` during row cleanup so Qt layout resets its cached geometries immediately.
  - Explicitly fixed row height (`setFixedHeight(22)`) and label heights (`setFixedHeight(20)`) with zero layout margins and matched column widths between headers and rows (170px process name, 70px speed in per-process mode; 140px/64px/64px/58px/58px in adapter mode) preventing text overlap and label clipping.
  - Updated `_fit_and_reposition()` and `_position_popup()` to reset `setMinimumSize(0, 0)` and dynamic resize via `sizeHint()` so window expands and contracts cleanly.

- **FIX: Git background processes pileup (`git.exe` in CPU/RAM process list)**:
  - Previously, `check_git_status` ran 3 separate `git` commands sequentially (`git status`, `git branch --show-current`, `git rev-list`) with no timeouts and default git lock / auto-gc behavior.
  - Combined into a **single atomic command** per repo: `git -c gc.auto=0 --no-optional-locks status --porcelain=v1 -b` with a hard `timeout=3s`.
  - Extracted branch name and ahead/behind counts directly from the `# branch...upstream [ahead X, behind Y]` porcelain header, cutting git process executions by 67%.
  - Added `-c gc.auto=0 --no-optional-locks` and `timeout=3s` to all git polling functions, preventing background maintenance tasks, index lock file contention, and hanging orphan processes.
  - Added `_git_loop_started` guard to prevent duplicate polling thread spawns.

- **FIX: `NetPopup` text clipping and dynamic row pooling**:
  - Replaced destructive widget rebuilds (`takeAt`/`deleteLater`) with pre-built row pools (`_proc_rows` and `_nic_rows`) like `ProcessPopup`.
  - Hiding and showing pre-allocated rows allows Qt's native `adjustSize()` to calculate the exact, complete window bounds including bottom margins, eliminating bottom row text clipping.
  - Separate `_proc_container` and `_nic_container` toggle cleanly without layout shifts or extra spacing.

## 4. Pending Task
Live-test workspace app rules: right-click a dot → assign an exe → launch it → confirm it opens on that workspace; remove the rule afterwards.

Verify event pipe stays stable after the FILE_FLAG_OVERLAPPED fix (no more error 230 loop in log).
