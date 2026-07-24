1. Project DNA (Permanent): Python-based terminal Gemini CLI for Windows. It uses a modular, tool-driven architecture with local file/system helpers, persistent model/API preferences, and an interactive TUI for model selection and chat.

2. Latest Implementation: Modified `gemini_terminal_cli/gemini_cli.py` to add persistent tool-loop limits, a `/loops <n>` command, and `--max-tool-loops` startup override. Updated `gemini_terminal_cli/README.md` to document the new limit controls and saved-state behavior.

3. Critical Context: Model and API state are stored in `model_prefs.json` and `api_accounts.json`, and both are already gitignored. The CLI now remembers the last model, last API account, and tool-loop limit across restarts; `/model` is arrow-key driven and `/model test` auto-hides failing models.

4. Pending Task: Verify the `/loops` behavior in a live terminal session and decide whether the tool list picker should also expose a dedicated "more models" flow.
