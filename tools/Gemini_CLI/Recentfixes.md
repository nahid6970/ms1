# Terminal input and paste handling

## Implemented behavior

- Startup detects Windows, Android Termux, Linux, or another POSIX environment and selects the matching prompt input automatically. The banner and `/device` report the detected environment; old saved `device_mode` preferences do not override detection.
- All platforms use a prompt_toolkit `PromptSession` when prompt_toolkit is installed. This gives Up/Down arrow history navigation, Tab slash-completion, and bracketed-paste handling on Android Termux, Linux, and Windows.
- A single `InMemoryHistory` instance is created once before the REPL loop, pre-seeded with entries loaded from `prompt_history.txt`. The same object is passed to every `read_dynamic_prompt` call so arrow-key history accumulates across the whole session. After each submit, `append_string` adds the new entry so it is immediately available via Up arrow.
- A single `PromptSession` is built by `build_repl_prompt_session` before the REPL loop and passed to `read_dynamic_prompt` on every call. Reusing the session avoids recreating the terminal input object each turn, which was causing instability on some POSIX and SSH-connected terminals. The session's `message` is updated to a fresh lambda each call so the dynamic prompt prefix stays current.
- `append_prompt_history` writes back to `prompt_history.txt` after each submission, keeping the plain-text file as the persistent store across restarts. On next startup the file is read and used to seed a fresh `InMemoryHistory`.
- Windows additionally wraps a `Win32Input` instance (created once inside `build_repl_prompt_session`) and drains queued console events after Enter to combine multiline paste into a single request.
- When prompt_toolkit is **not** installed on POSIX/Termux, the fallback chain is:
  1. `_readline_prompt` — uses Python's built-in `readline` module (always available on Linux/macOS). Loads the current history list into readline so Up/Down arrow works via the standard line editor. Also registers a Tab completer for `/` slash commands.
  2. `read_posix_prompt` — raw bracketed-paste reader, used only when `readline` is also unavailable. Arrow keys and other CSI/SS3 escape sequences are now fully consumed and silently discarded instead of printing garbage bytes.

## What was broken and why

### Issue 1: Arrow keys printed garbage (`^[[A`, `^[[B`) on Android/Linux
`read_posix_prompt` operated in raw terminal mode and used a byte-level state machine to detect bracketed-paste markers (`\x1b[200~` / `\x1b[201~`). When an arrow key sequence arrived (`\x1b[A`), the old code accumulated `\x1b[` (which is a valid prefix of the paste markers), then on the final byte it found no match and called `marker_buffer.clear()` — but only *after* already having reached a branch that could forward the bytes to the display in some edge cases, and never consistently across all terminal multiplexers and SSH clients.

The new code uses a two-state ESC accumulator (`esc_buffer` + `in_csi` flag) that correctly identifies and drains:
- CSI sequences: `ESC [` … final byte in `0x40–0x7E` (covers all arrow/function/navigation keys)
- SS3 sequences: `ESC O` + one final byte (covers F1–F4)
- Plain two-byte ESC sequences
- Bracketed-paste markers (the only sequences actually forwarded)

### Issue 2: No Up/Down history and no Tab completions on Android/Linux without prompt_toolkit
The old POSIX fallback went straight to `read_posix_prompt`, which is a custom raw reader that provides only basic bracketed-paste support. It has no history, no completion, and no line-editing beyond backspace.

The new fallback first tries `_readline_prompt`: it uses Python's built-in `readline` (present on every Linux/macOS Python), loads history, and wires up a Tab completer for `/` commands — all without any extra dependencies.

### Issue 3: `PromptSession` recreated on every REPL turn
The previous REPL loop created a fresh `PromptSession` (and, on Windows, a fresh `Win32Input`) on every single call to `read_dynamic_prompt`. On prompt_toolkit versions that hold internal terminal state, this caused the terminal to reset between turns, breaking keyboard input on some POSIX terminals and SSH sessions.

The fix creates one `PromptSession` via `build_repl_prompt_session` before entering the REPL loop and passes it through as `pt_session`. `read_dynamic_prompt` reuses it every turn, updating only the `message` lambda to keep the dynamic prompt prefix current.

## Verify interactively

Start the CLI. Send a few prompts. Press Up to cycle through them. Type `/` and confirm command completions appear. Paste a multiline block and confirm it appears as one request. Restart the CLI and press Up — previous session prompts should still be available. Check `/device` reports the correct environment.

On Android Termux or Linux **without** `prompt_toolkit` installed, confirm:
- Up/Down arrow cycles through previous prompts (via readline)
- Tab after typing `/` shows slash-command completions
- Arrow key presses do not print garbage characters
