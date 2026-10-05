# recent.md — AI Session Handoff

## 1. Project DNA (Permanent)
Python/PyQt6 desktop notification system. A daemon (`notify_daemon.py`) watches a text file for changes and pops a styled notification; `notify_run.py` is the standalone test runner. Triggered by `update_notification.py` which writes a timestamp to `C:\Users\nahid\notification.txt`.

## 2. Latest Implementation
- **notify_daemon.py** — Full rewrite. Single top-level `QWidget` (no child widgets) with `WA_TranslucentBackground`. Paints everything in `paintEvent`: dark navy card, ✦ icon, text, a fully custom dismiss button (path-drawn ring + label, hover/press via `setMouseTracking`), and a rotating conical gradient aurora border. Smooth slide-up fade entrance animation.
- **notify_run.py** — Mirror of daemon's popup class for quick standalone testing.
- **AGENT.md** — Added `[ACTIVE]`/`[INACTIVE]` tag system with explanation header; added 4 Suggestion Style rules (all `[INACTIVE]`); added `Preview / Smoketest [ACTIVE]` rule.

## 3. Critical Context
- **No child widgets** — everything is painted manually. Any `QPushButton` or child `QWidget` causes square corner bleed even with `WA_TranslucentBackground`. Hover works only because `setMouseTracking(True)` is set.
- **Aurora border** uses `QConicalGradient` filled into an `outer_path - inner_path` ring. Speed controlled by `+= 0.003` per 16ms tick.
- `setMask()` was tried and abandoned — it polygonizes the path and destroys antialiasing.

## 4. Pending Task
Test the hover/press effect on the dismiss button and verify aurora border color cycling looks correct after the latest fixes.
