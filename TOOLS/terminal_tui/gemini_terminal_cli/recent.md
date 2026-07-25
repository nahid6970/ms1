1. Project DNA (Permanent): Python-based terminal Gemini CLI for Windows. It uses a modular, tool-driven architecture with local file/system helpers, persistent model/API preferences, and an interactive TUI for model selection and chat.

2. Latest Implementation: Updated `gemini_terminal_cli/gemini_cli.py` to support locked API account storage in `api_accounts.lock`, password-protected load/save flows, `/loadapi <name>` startup parsing, `/system <text|file>`, and `/test` as the model test command.

3. Critical Context: Model and API state are stored in `model_prefs.json` and `api_accounts.lock`. The CLI remembers the last model and last API account across restarts; `/model` is arrow-key driven, `/test` auto-hides failing models, and `--password` / `--api-password` can bypass interactive prompts for the locked API file.

4. Pending Task: Decide whether the password flag should also be accepted from an environment variable for easier automation.
