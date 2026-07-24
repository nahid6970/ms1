# Gemini Terminal CLI

A small, self-contained terminal assistant for Google Gemini.

It is designed to feel closer to a CLI tool than a web app:
- interactive chat loop
- local file tools
- shell command execution
- optional transcript save/load
- Gemini function-calling loop

## Requirements

- Python 3.10+
- First-time setup needs either a `GEMINI_API_KEY` environment variable, or `/addapi`

## Run

```powershell
python .\gemini_terminal_cli\gemini_cli.py
```

### One-shot prompt

```powershell
python .\gemini_terminal_cli\gemini_cli.py -p "Summarize this repo"
```

### Set a project root

```powershell
python .\gemini_terminal_cli\gemini_cli.py --project-root C:\path\to\project
```

### Set the tool-loop limit

```powershell
python .\gemini_terminal_cli\gemini_cli.py --max-tool-loops 12
```

### Load a transcript

```powershell
python .\gemini_terminal_cli\gemini_cli.py --load-transcript .\gemini_terminal_cli\transcripts\latest.json
```

## Commands inside the REPL

- `/help` - show commands
- `/exit` - quit
- `/reset` - clear conversation
- `/model` - open the model picker
- `/model test` - test all models and auto-hide failures
- `/addapi` - add a named API key
- `/loadapi` - load a saved API account
- `/loops <n>` - set the max tool-call loops for a turn
- `/system <text>` - replace the system instruction
- `/tools on|off` - enable or disable local tools
- `/save <file>` - write transcript JSON
- `/load <file>` - load transcript JSON

## Local tools

The CLI exposes only local, standard-library tools:
- `read_file`
- `write_file`
- `delete_file`
- `list_directory`
- `run_shell_command`
- `get_system_info`
- `request_follow_up`

## Notes

- The CLI does not depend on the Flask app.
- It uses Gemini's function-calling API directly over HTTP.
- Shell commands are intentionally explicit; the model must ask for them through the tool loop.
- Hidden models, last model, and speed tags are stored in `model_prefs.json`.
- Named API accounts are stored in `api_accounts.json`.
- The CLI restores the last-used API account and model on startup when they have been saved.
- The tool-loop limit is stored in `model_prefs.json` and can be overridden with `--max-tool-loops`.
