1. Project DNA (Permanent): Python-based Windows terminal Gemini CLI with a modular, tool-driven architecture, interactive prompt/TUI, local file/system helpers, and persistent model/API preferences. Its primary goal is practical interactive chat and coding assistance from the terminal.

2. Latest Implementation: Modified `gemini_cli.py` to consume Windows extended arrow-key sequences and restore Up/Down command history without leaking H/P/K/M into input; force API retry cooldowns to a one-minute countdown; and write `YYYY-MM-DD-HH:MM` to `C:\Users\nahid\notification.txt` on successful completion, quota errors, empty responses, max tool-loop exit, and cooldown expiry.

3. Critical Context: `read_dynamic_prompt` owns prompt redraw and history; `command_history` is session-only and removes consecutive duplicates. `model_cooldowns` stores expiry datetimes, but retry responses always become exactly 60 seconds. Notification writes are intentionally best-effort and silent. Persistent state remains in `model_prefs.json` and `api_accounts.lock`.

4. Pending Task: Manually verify arrow-key history, the fixed `01:00` cooldown display, and notification-file triggers in a real Windows console.
