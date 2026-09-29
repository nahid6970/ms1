# Gemini CLI Termux input and scrollback fixes

## Changes made

The CLI code is in `ms1/tools/terminal_tui/gemini_terminal_cli/gemini_cli.py`.

- In Android mode, the main prompt uses ordinary terminal input instead of `prompt_toolkit` redraws. This is intended to stop Termux from pulling the viewport back to the prompt when you scroll up to read earlier output.
- On POSIX terminals, interactive menus now read key sequences directly in both PC and Android modes. Arrow keys should navigate menus instead of appearing as text such as `^[[A`.

The project issue note is `ms1/tools/terminal_tui/gemini_terminal_cli/mobile_autoscroll_issue.md`.

## Which mode to use

Use `/device android` on Termux for the scrollback-friendly prompt. The setting is saved in the CLI preferences. Use `/device pc` to restore the `prompt_toolkit` prompt.

Android mode has simpler input. These features are unavailable at the main prompt:

- Tab completion for slash commands and file paths
- In-session prompt history recalled with the up and down arrows

Arrow-key navigation still works inside interactive menus in either mode. The Android-mode limitation applies to the main text prompt, not menus.

## Check the fixes

Restart the CLI after updating the code. In Android mode, wait at the main prompt, scroll up in Termux, and check whether the viewport stays on earlier output. Open an interactive menu and use the arrow keys and Enter to navigate in either device mode.

Termux settings or a multiplexer such as `tmux` can still affect scrollback behavior.
