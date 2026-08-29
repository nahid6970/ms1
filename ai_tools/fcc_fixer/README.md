# FCC Fixer

Cyberpunk-themed PyQt6 utility for diagnosing and repairing common Free Claude Code (FCC) issues with Claude Code and Codex CLI.

## Features

- Checks FCC health at `http://127.0.0.1:8082/health`.
- Finds `fcc-server`, `fcc-claude`, `fcc-codex`, and normal `codex` on `PATH`.
- Shows the non-secret model routing values from `%USERPROFILE%\.fcc\.env`.
- Detects stale Claude Code Router settings in `%USERPROFILE%\.claude\settings.json`.
- Backs up `settings.json` before removing the old `apiKeyHelper` and `:3456` endpoint entries.
- Opens the Claude settings, Codex config, and FCC environment files.
- Starts `fcc-server` in a new Windows console when it is not already listening.
- Provides separate quick-command reminders for FCC Claude, FCC Codex, and normal OpenAI Codex.

The GUI never displays API-key values and does not automatically rewrite Codex configuration because Codex settings may contain unrelated user customizations.

## Run

PyQt6 is already available in the current Python installation:

```powershell
cd C:\@delta\ms1\ai_tools\fcc_fixer
python .\main.py
```

If launching with another Python environment that does not have PyQt6, install it yourself in that environment with your preferred package workflow, then run `main.py` again.

## Recommended workflow

1. Start the GUI.
2. Click `REFRESH DIAGNOSTICS`.
3. Start `fcc-server` if the FCC health check is offline.
4. Use `FIX CLAUDE ROUTER CONFLICT` only when the warning is present; a timestamped backup is created first.
5. Use `fcc-claude` or `fcc-codex` only while `fcc-server` is running.
6. Use normal `codex` separately when you want OpenAI models directly.
