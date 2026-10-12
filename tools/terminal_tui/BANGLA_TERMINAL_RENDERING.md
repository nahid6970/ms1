# Bangla Rendering in Terminal Panes

## Status

Bangla still appears with broken spacing/shaping in the main Xterm.js terminal. The separate **বাং** view renders the same terminal buffer as browser text and displays Bangla correctly. A font-only fix for the main Xterm.js renderer has not been found.

**Rollback planned:** The user said they are going to revert the implementation changes. This note records the investigation and should be kept as the issue history. Until that revert is made, the current working tree still contains the font stack and **বাং** view changes in `templates/index.html`.

## Why the Two Views Differ

The **বাং** view reads text from Xterm.js's active buffer and puts the resulting text in a normal HTML `<pre>` element. The browser can shape a whole Bangla text run using Vrinda or Nirmala UI.

The main terminal is a VT-style terminal emulator. It assigns output to fixed character cells so it can track the cursor, columns, scrolling, colors, and terminal control sequences. Bangla shaping can reorder marks and combine glyphs across characters, which does not fit reliably into those independent cells. Selecting a Bangla font supplies glyphs but does not change this cell model.

Xterm.js 5.3 already uses its built-in DOM renderer by default. Its Canvas and WebGL renderers still render terminal cells, so switching among those renderers is not expected to provide full Bangla shaping.

## Attempts So Far

1. Added Vrinda and Nirmala UI to the terminal font fallback stack. Bangla glyphs remained incorrectly spaced/shaped in the main terminal.
2. Tried Xterm.js Unicode 11 width handling. It did not fix shaping and was removed after terminal initialization trouble.
3. Added the **বাং** view. It reads up to 3,000 rows from the active Xterm.js buffer and renders them as browser text. This displays Bangla correctly, but it is read-only and does not preserve ANSI colors or interactive TUI behavior.
4. Checked renderer alternatives available in the current Xterm.js setup. The default is already the DOM renderer; Canvas/WebGL are not complex-script shaping renderers.

## Files Involved

- `templates/index.html` — terminal font stack and **বাং** buffer view
- `md/RECENT.md` — session history
- `md/PROBLEMS_AND_FIXES.md` — issue history

## Rollback Scope

When reverting the implementation, remove the terminal font-stack helper/application and the **বাং** button, buffer-view functions, and related CSS from `templates/index.html`. Keep this document if the goal is to retain the diagnosis and record of attempted approaches. The issue will remain unresolved in the main terminal after rollback.

## What a Full Main-Terminal Fix Would Require

A full fix needs a renderer that supports complex-script shaping while preserving terminal cursor and cell behavior, or a custom HTML overlay that mirrors the terminal buffer and reproduces terminal colors, cursor behavior, selection, and scrolling. Neither is a font setting or a small Xterm.js configuration change. The current **বাং** view is the working reading view for Bangla output; use the main terminal for input and interactive terminal programs.
