# FCC Fixer

Cyberpunk-themed PyQt6 utility for diagnosing and repairing common Free Claude Code (FCC) issues with Claude Code and Codex CLI.

## Features

- Checks FCC health at `http://127.0.0.1:8082/health`.
- Finds `fcc-server`, `fcc-claude`, `fcc-codex`, and normal `codex` on `PATH`.
- Shows the non-secret model routing values from `%USERPROFILE%\.fcc\.env`.
- Detects stale Claude Code Router settings in `%USERPROFILE%\.claude\settings.json`.
- Backs up `settings.json` before removing the old `apiKeyHelper` and `:3456` endpoint entries.
- Detects persistent FCC/Gemini provider, catalog, and model overrides in Codex `config.toml`.
- Backs up and removes only recognized FCC overrides from Codex configuration.
- Detects FCC/Gemini entries in Codex `models_cache.json` and can move that cache to a timestamped backup so normal Codex can rebuild it.
- Opens the Claude settings, Codex config, and FCC environment files.
- Starts `fcc-server` in a new Windows console when it is not already listening.
- Provides separate quick-command reminders for FCC Claude, FCC Codex, and normal OpenAI Codex.
- Provides one-click copy buttons for normal and full-auto FCC Claude/Codex commands, plus a Gemini 3.5 example.

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
6. If normal Codex ever shows FCC/Gemini models, close Codex and use `FIX CODEX FCC OVERRIDES` first.
7. If the issue remains and the GUI detects a contaminated cache, use `QUARANTINE CODEX CACHE`.
8. Use normal `codex` separately when you want OpenAI models directly.

All Codex repairs are confirmation-based and create recoverable backups. The GUI does not touch Codex authentication or unrelated configuration entries.

## Full-auto command names

The GUI copies the currently supported flags:

```text
fcc-claude --dangerously-skip-permissions
fcc-codex --dangerously-bypass-approvals-and-sandbox
```

These skip confirmation and sandbox protections. Use them only in a trusted, externally controlled environment. The normal commands remain available as safer copy options.
