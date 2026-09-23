# Unresolved Issue: Codex Resume Terminal Colors

**Status:** Open — implementation reverted for later investigation

**Reported:** 2026-09-24

## Symptoms

The issue only appears in the Codex main/resume terminal, especially the screen that lists conversations to resume. The resume list and bottom status line look much flatter and less colorful than they do in a normal Windows Terminal session.

The affected bottom status area contains information such as:

```text
GPT-5.5 medium · monthly 23% left · 841K used · 13.3M in · 55.8K out · warning · F2 to view
```

Normal terminals still display the expected colored text. This suggests the problem is specific to how the embedded terminal renders the Codex TUI, rather than a general Windows color configuration problem.

## Expected behavior

The embedded terminal should preserve the colors, emphasis, dim text, selection/reverse-video styling, and status colors produced by the Codex resume interface, as seen in Windows Terminal.

## Current behavior

The Codex resume interface renders with muted or bland colors in Terminal TUI. Conversation rows, metadata, highlighted rows, and the bottom usage/status line do not visually match the normal Windows Terminal appearance.

## Scope

- Affects: Codex main/resume terminal UI.
- Does not appear to affect: ordinary terminal commands or normal Windows Terminal sessions.
- The problem was still present after earlier frontend color changes, so those changes were reverted.

## Investigation notes

Potential areas to inspect later:

1. Compare the PTY environment between Windows Terminal and the embedded terminal, especially `TERM`, `COLORTERM`, `TERM_PROGRAM`, `WT_SESSION`, and color-related variables.
2. Check whether Codex chooses a different color mode when it detects the embedded PTY.
3. Inspect xterm.js handling of SGR colors, bold, dim, inverse/reverse video, and 256-color or truecolor escape sequences.
4. Compare the actual escape sequences emitted by the Codex resume screen in both terminals.
5. Check whether CSS, opacity, contrast, or theme configuration is muting xterm rows after ANSI styling is applied.
6. Verify whether the embedded terminal is using a different terminal type, font, or renderer than the normal Windows Terminal.
7. Test with a minimal ANSI color/attribute script to separate PTY color negotiation from frontend rendering.

## Reproduction checklist

1. Open Terminal TUI.
2. Start or open the Codex main terminal.
3. Open the Codex resume-previous-session screen.
4. Compare its project/conversation list and bottom usage/status line with the same screen in Windows Terminal.
5. Record the PTY environment and capture the emitted ANSI sequences in both environments.

## Related files to inspect

- `templates/index.html` — embedded xterm.js initialization and terminal theme.
- `app.py` — PTY/session creation and environment setup.
- `tui_config.json` — saved workspace and terminal theme configuration.

## Resolution criteria

The issue can be closed when the Codex resume screen in the embedded terminal visibly matches the normal Windows Terminal colors and emphasis, while ordinary terminal output and existing terminal themes continue to work.
