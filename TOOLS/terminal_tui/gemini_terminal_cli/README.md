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
- `prompt_toolkit` for the interactive input line
- First-time setup needs either a `GEMINI_API_KEY` environment variable, or `/addapi`
- API accounts are stored in an encrypted `api_accounts.lock` file and prompt for a password

Install the input dependency with:

```powershell
pip install prompt_toolkit
```

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

### Load a saved API account at startup

```powershell
python .\gemini_terminal_cli\gemini_cli.py --password mypass /loadapi 09
```

If you omit the account name, the CLI loads the first saved account from `api_accounts.lock`.
If you omit `--password`, the CLI prompts for it.
`--api-password` works the same as `--password`.

### Load a system instruction from a file

```powershell
python .\gemini_terminal_cli\gemini_cli.py /system .\system_instruction.md
```

## Commands inside the REPL

- `/help` - show commands
- `/exit` - quit
- `/reset` - clear conversation
- `/mm` - open the model picker
- `/test` - test all models and auto-hide failures
- `/addapi` - add a named API key
- `/loadapi` - load the first saved API account, or a named one
- `/loops <n>` - set the max tool-call loops for a turn
- `/failover` - open the auto-failover picker
- `/failover ...` - control automatic API account rotation on quota or rate-limit errors directly
- `/system <text|file>` - replace the system instruction or load it from a file
- `/tool` - open the categorized tool manager; browse by category, toggle with Space
- `/skill` - interactive browser for custom skill files inside the `skills/` directory
- `/resume`, `/r [file]` - open interactive picker to select and resume a recent conversation session

- `/save <file>` - write transcript JSON
- `/load <file>` - load transcript JSON

## Local Tools

Tool definitions are stored in **`tools.json`** — an editable JSON array. Each entry has:
- `name` — tool function name
- `category` — grouping shown in `/tool` menu
- `rating` — short advice shown in the info footer
- `description` — detailed explanation shown when selected

The `/tool` menu loads categories dynamically from `tools.json`. Adding a new category in the JSON will auto-create a new section in the menu.

### Tool Categories

**Inspection & File System** (read-only, safe):
- `read_file` — read file content (truncates at 12k chars)
- `list_directory` — list dir contents
- `get_system_info` — OS, Python version, cwd
- `search_file` — case-insensitive text search in files/dirs
- `search_web` — DuckDuckGo web search (no API key)
- `search_tavily` — Tavily web search (uses saved API keys)
- `delete_file` — delete file or directory (destructive)

**Code Modifications** (editing tools, toggleable):
- `fuzzy_apply_patch` — unified diff with ±50 line fuzzy search + normalized whitespace matching
- `smart_replace_block` — find-and-replace with 3-tier fallback (exact → CRLF normalized → trailing whitespace stripped)
- `replace_lines` — replace 1-indexed line range (lowest token cost)
- `replace_block` — strict exact find-and-replace (no fallback)
- `apply_patch` — strict unified diff (no fuzzy search)
- `insert_after` — insert text after exact anchor string
- `delete_block` — delete exact text block
- `write_file` — overwrite entire file (high token cost)
- `replace_file` — alias for write_file

**Execution & Shell**:
- `run_shell_command` — run shell commands via subprocess
- `run_powershell` — run PowerShell commands (preferred on Windows)

**Control Flow**:
- `request_follow_up` — request another AI turn for multi-step work

### Recommended Configuration

For best balance of reliability and token efficiency, enable only:
- ✅ `fuzzy_apply_patch` — resilient multi-file edits
- ✅ `smart_replace_block` — targeted single-file edits with fuzzy fallback
- ✅ `replace_lines` — low-token line-range replacement

Keep disabled:
- ❌ `apply_patch` — superseded by `fuzzy_apply_patch`
- ❌ `replace_block` — superseded by `smart_replace_block`
- ❌ `write_file` / `replace_file` — full-file overwrite, wastes tokens

### Tool State (on/off)

Disabled tools are stored in `model_prefs.json` under the `disabled_tools` array. Only disabled tool names are listed; if a tool is absent from the array, it's enabled. You can edit this manually or use `/tool` in the REPL.

## Notes

- `run_powershell` runs through `powershell.exe -NoProfile`. Use for `rg`, `Get-Content`, `git status`, and tests before editing. For literal searches with `Select-String`, prefer `-SimpleMatch` and single-quoted patterns.
- When an `apply_patch` or `fuzzy_apply_patch` call is shown in the terminal, removed diff lines render red and added diff lines render green.
- REPL input history is stored in `prompt_history.txt` so Up/Down history survives restarts.
- The CLI restores the last-used API account and model on startup when saved.
- `/failover` opens an interactive picker for project, session, and global failover scopes.
- Auto failover retries retryable quota/rate-limit errors, walking saved API accounts in circular order.
- `/failover on|off` stores a project-specific override; `/failover session on|off` is process-only; `/failover default on|off` sets the global default.
- The `/api` picker shows a `Failovers` column per account.
- The `/mm` picker shows cumulative model `Uses` counts.
- The tool-loop limit is stored in `model_prefs.json` and can be overridden with `--max-tool-loops`.
- `--password` or `--api-password` avoids interactive password prompts for locked API accounts.
- `/test` is the model testing command; `/mm test` remains an alias.

