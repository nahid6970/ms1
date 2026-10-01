# Terminal input and paste handling

## Implemented behavior

- Startup detects Windows, Android Termux, Linux, or another POSIX environment and selects the matching prompt input automatically. The banner and `/device` report the detected environment; old saved `device_mode` preferences do not override detection.
- All platforms use a prompt_toolkit `PromptSession` when prompt_toolkit is installed. This gives Up/Down arrow history navigation, Tab slash-completion, and bracketed-paste handling on Android Termux, Linux, and Windows.
- A single `InMemoryHistory` instance is created once before the REPL loop, pre-seeded with entries loaded from `prompt_history.txt`. The same object is passed to every `read_dynamic_prompt` call so arrow-key history accumulates across the whole session. After each submit, `append_string` adds the new entry so it is immediately available via Up arrow.
- `append_prompt_history` writes back to `prompt_history.txt` after each submission, keeping the plain-text file as the persistent store across restarts. On next startup the file is read and used to seed a fresh `InMemoryHistory`.
- Windows additionally wraps a `Win32Input` instance and drains queued console events after Enter to combine multiline paste into a single request.
- The raw `read_posix_prompt` (bracketed-paste only, no arrow history, no completion) is kept as a fallback for when prompt_toolkit is not installed on POSIX/Termux.

## What was broken and why

`InMemoryHistory` was being created fresh on every single call to `read_dynamic_prompt`. Each prompt iteration started with a blank history object, so Up/Down arrow produced nothing regardless of platform. On POSIX/Termux the problem was compounded by the input path skipping prompt_toolkit entirely and using a raw byte reader that silently discarded arrow escape sequences.

## Verify interactively

Start the CLI. Send a few prompts. Press Up to cycle through them. Type `/` and confirm command completions appear. Paste a multiline block and confirm it appears as one request. Restart the CLI and press Up — previous session prompts should still be available. Check `/device` reports the correct environment.
