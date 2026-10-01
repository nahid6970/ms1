# Terminal input and paste handling

## Implemented behavior

- Startup detects Windows, Android Termux, Linux, or another POSIX environment and selects the matching prompt input automatically. The banner and `/device` report the detected environment; old saved `device_mode` preferences do not override detection.
- POSIX terminals use raw input with bracketed-paste capture. Multiline pasted text stays within one prompt, and normal input submits only when Enter is pressed after the paste.
- Windows uses `PromptSession` with prompt-toolkit's `Win32Input` for the main prompt. It enables paste recognition and briefly drains queued console events after Enter, combining separately delivered pasted lines into that same request instead of launching one request per line.
- POSIX menu redraws clear only the active screen, preserving scrollback. Arrow sequences are read in raw mode.

## Input mode tradeoffs

The POSIX raw prompt preserves scrollback and groups bracketed paste, but does not provide tab completion or main-prompt up/down history. Windows retains prompt-toolkit editing features.

## Verify interactively

Restart the CLI on Windows and POSIX. Paste a multiline block and confirm it appears as one request; press Enter once to submit. Check `/device` reports the detected platform. On Termux, also check scrollback and menu arrow navigation. Terminal multiplexers and terminal apps can affect bracketed-paste support.
