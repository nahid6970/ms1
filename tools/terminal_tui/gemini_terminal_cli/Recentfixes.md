# Terminal input and paste handling

## Implemented behavior

- Startup detects Windows, Android Termux, Linux, or another POSIX environment and selects the matching prompt input automatically. The banner and `/device` report the detected environment; old saved `device_mode` preferences do not override detection.
- All platforms now use a prompt_toolkit `PromptSession` with `FileHistory` when prompt_toolkit is installed. This gives Up/Down arrow history navigation and Tab slash-completion on Android Termux, Linux, and POSIX terminals, as well as Windows.
- Windows additionally wraps a `Win32Input` instance and drains queued console events after Enter to combine multiline paste into a single request.
- The raw `read_posix_prompt` (bracketed-paste only, no arrow history, no completion) is kept as a fallback for when prompt_toolkit is not installed on POSIX systems.
- POSIX menu redraws clear only the active screen, preserving scrollback. Arrow sequences are read in raw mode.
- `FileHistory` is used instead of `InMemoryHistory` so arrow-key history survives CLI restarts on all platforms.

## Input mode tradeoffs

prompt_toolkit's `PromptSession` provides Up/Down arrow history, Tab slash-completion, and bracketed-paste handling on every platform. The raw POSIX reader is only used when prompt_toolkit is absent; it preserves scrollback and handles bracketed paste but has no history navigation or completion.

## Verify interactively

Restart the CLI on Android Termux. Press Up to cycle through previous prompts. Type `/` and confirm command completions appear. Paste a multiline block and confirm it appears as one request. Check `/device` reports `android-termux`. On Windows, verify the same history and completion behavior is unchanged.
