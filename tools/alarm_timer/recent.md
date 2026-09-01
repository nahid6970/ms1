# 1. Project DNA (Permanent)

PyQt6 desktop GUI in a modular single-file Python architecture, with JSON persistence in `alarm_state.json`. The app is a cyberpunk-themed multi-column alarm/countdown timer with editable timer and text cards.

# 2. Latest Implementation

- `alarm_timer.py`: stabilized startup layout updates by placing the checkmark button in a fixed 22px slot, changing its visibility only when a timer changes between active and fired, and sorting loaded cards once per column instead of after every card.

# 3. Critical Context

`MainWindow` loads saved state during construction, then shows exactly one top-level window. `TimerCard` uses a one-second `QTimer`; `_toggle_available` prevents repeated visibility/style/layout work. Windows restart is explicitly handled by `_on_restart` with `subprocess.Popen`, but it runs only when the Restart button is clicked. Direct launch testing showed one real `alarm_timer.py` process; repeated taskbar entries may therefore come from the launcher/shortcut or Python shim.

# 4. Pending Task

Identify how the GUI is launched (shortcut, pinned taskbar item, script, or `python` command) and inspect that launcher for repeated invocation; then retest the current `alarm_timer.py` directly with the Python executable path.
