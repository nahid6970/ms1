# Issue: Codex Resume Terminal Colors

**Status:** ✅ Resolved — 2026-09-24

**Reported:** 2026-09-24

## Symptoms

The issue only appeared in the Codex main/resume terminal, especially the screen that lists conversations to resume. The resume list and bottom status line looked much flatter and less colorful than they did in a normal Windows Terminal session.

The affected bottom status area contains information such as:

```text
GPT-5.5 medium · monthly 23% left · 841K used · 13.3M in · 55.8K out · warning · F2 to view
```

Normal terminals displayed the expected colored text. The problem was specific to how the embedded terminal rendered the Codex TUI, not a general Windows color configuration problem.

## Root Cause

The PTY session launched by `app.py` did not set terminal color capability environment variables. Codex (and other TUI apps like `fzf`, `bat`, `less`) interrogate the environment at startup to decide which color mode to use:

- `COLORTERM=truecolor` → full 24-bit color
- `TERM=xterm-256color` → 256-color fallback
- Neither set → 16-color or monochrome fallback

In a real Windows Terminal session, `WT_SESSION`, `COLORTERM=truecolor`, and `TERM=xterm-256color` are present. In the embedded winpty shell, none of these were set, so Codex fell back to a muted, low-color rendering mode.

The xterm.js frontend was not the problem — it can render truecolor correctly. The issue was that Codex never emitted the right escape sequences because it didn't know the terminal supported them.

## Fix Applied

Added the following to the top of the PowerShell profile template in `app.py` (`system_template`):

```powershell
# Terminal color capability declarations so TUI apps (Codex, fzf, etc.) use full color
$env:TERM = "xterm-256color"
$env:COLORTERM = "truecolor"
$env:TERM_PROGRAM = "xterm-256color"
```

These are written into every project's `profile.ps1` and loaded automatically when a terminal pane opens.

## Files Modified

- `app.py` — added `TERM`, `COLORTERM`, `TERM_PROGRAM` env vars to `system_template`

## Verification

Confirmed fixed after restarting the terminal and opening the Codex resume screen — colors and emphasis now match the normal Windows Terminal appearance.
