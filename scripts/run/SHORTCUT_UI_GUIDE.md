# Shortcut UI Guide

This document explains the shortcut-driven UI pattern used in [Run.py](C:\@delta\ms1\scripts\run\Run.py) so you can rebuild it in another project.

## Goal

The UI is a keyboard-first launcher built around `fzf`. It does four things well:

- Shows a searchable list of files and folders.
- Displays a clear shortcut/help header inside the picker.
- Adds rich key bindings for actions instead of forcing everything through Enter.
- Separates data feeding, preview, and actions into small scripts/state files.

That separation is the main reason the UI feels clean and reusable.

## Core Architecture

The implementation is split into these parts:

1. `fzf` main picker
2. Feeder script that prints display text + real path
3. Preview script for text/image preview
4. Toggle/state files for persistent UI modes
5. Action menu script for `Enter` on multi-select
6. Bookmark/config helpers

The list rows use this shape:

```text
<styled display text>\t<real full path>
```

`fzf` shows the first column and actions use the second column.

That is the key pattern to copy.

## Why The UI Feels Good

These design choices are what make the shortcut UI feel strong:

- The header immediately teaches the controls.
- The prompt is short and readable: `Search [?] >`.
- Preview is available but hidden by default, so the list stays focused.
- Common actions have direct key bindings: open, copy, run, bookmark, refresh.
- `Enter` opens a second action menu for multi-select workflows.
- Bookmarks appear first, which makes the list feel personalized.
- The view can switch between full path and compact name mode.

## Main `fzf` Setup

The core picker in `Run.py` is built with options like:

- `--ansi`
- `--multi`
- `--with-nth=1`
- `--delimiter=\t`
- `--prompt=Search [?] >`
- `--header-first`
- `--border`
- `--layout=reverse`
- `--preview=...`
- `--preview-window=right:50%:hidden`
- many `--bind=` entries

### Important option choices

- `--ansi`: allows colored row labels.
- `--multi`: enables Tab multi-select.
- `--delimiter=\t`: splits display text from true path.
- `--with-nth=1`: only show the pretty display column.
- `--preview-window=...:hidden`: preview exists but does not dominate by default.
- `--header-first`: keeps the help header anchored at the top.

## Display Row Pattern

The feeder script prints rows with:

```text
<colored label>\t<absolute path>
```

Example:

```text
* My Bookmark\C:\projects\app\main.py
```

Conceptually it should be:

```python
print(f"{display_text}\t{full_path}")
```

Then `fzf` actions reference:

- `{1}` for visible label
- `{2}` for actual path
- `{+2}` for all selected real paths

This is the most reusable idea in the whole file.

## Feeder Script Responsibilities

The feeder script in `Run.py` handles list generation. In another project, keep it responsible for:

- loading roots to search
- reading UI config
- reading bookmark data
- respecting ignore/visibility rules
- formatting display labels
- printing bookmarks first
- printing files/folders after that

### Good pattern to copy

Have the feeder own presentation logic for rows:

- marker for bookmark state
- compact name mode vs full path mode
- colors for folders/files/bookmarked items

That keeps the main launcher simpler.

## State Files

The current implementation uses small files to track UI mode:

- preview mode state
- view mode state

This is a pragmatic design. It works well because `fzf` bindings can execute external scripts, and those scripts need a shared place to read/write UI state.

### Modes used now

- Preview mode: `chafa` or `quicklook`
- View mode: `full` or `name`

Use the same approach in another project if you want toggleable UI behavior without building a full app framework.

## Preview System

The preview logic is intentionally externalized into a PowerShell script.

### Behavior

- If selected item is an image:
  - use `QuickLook` in one mode
  - use `chafa` or `viu` in another mode
  - fall back to metadata if no image preview tool exists
- If selected item is a text file:
  - use `bat`
  - fall back to `Get-Content`
- If selected item is binary:
  - show file metadata

### Why this works well

- `fzf` preview stays lightweight.
- The preview tool can evolve independently from the picker.
- Mode toggling is easy: update state file, then refresh preview.

## Shortcut Header

The UI uses a multiline ASCII header showing all important shortcuts.

That header is useful because:

- it makes the UI self-documenting
- users do not need external docs
- hidden features become discoverable

The implementation also binds:

- `?` to toggle the header
- `start:toggle-header`

That creates a nice behavior: shortcuts are available without permanently occupying space.

## Key Bindings Pattern

These bindings are the core interaction model:

- `Enter`: execute action menu for selected items
- `Ctrl-N`: open in editor
- `Ctrl-O`: open containing folder
- `Ctrl-C`: copy path
- `Ctrl-R`: run item
- `Ctrl-P`: toggle preview
- `F2`: switch image preview mode
- `F3`: switch list display mode
- `F4`: reload list
- `F5`: toggle bookmark
- `F6`: rename bookmark
- `F7`: open configuration UI
- `Alt-Up/Alt-Down`: reorder bookmarks
- `?`: toggle help header

### Reusable design rule

Map each shortcut to one of these categories:

- immediate action on current row
- action on selected rows
- UI mode toggle
- data reload
- settings/help

That structure keeps the keyboard model predictable.

## Action Menu On Enter

Instead of hardcoding Enter to a single behavior, `Run.py` launches a second `fzf` menu for selected items.

Actions there include:

- Run
- Editor
- Folder
- Terminal
- Copy path
- Delete

This is a strong pattern when:

- single-key shortcuts cover the fast path
- Enter should expose a broader action palette
- multi-select needs different action targets

If you want the same feel in another project, keep Enter as an action chooser, not just “open file”.

## Bookmarks

Bookmarks are not just favorites; they shape the top of the UI.

Current bookmark behavior:

- toggle bookmark with `F5`
- prompt for optional custom bookmark name
- rename with `F6`
- reorder with `Alt-Up` and `Alt-Down`
- render bookmarks first in the list
- display bookmark marker and custom label

This is why the launcher feels personalized rather than just searchable.

## Color And Labeling

The implementation uses ANSI colors and icons in both the main list and action menu.

Important ideas:

- folders and files have different colors
- bookmarked items have separate highlight colors
- actions use distinct colors and icons
- display text is padded for cleaner scanning

You do not need the exact same palette, but keep semantic color differences:

- folder vs file
- bookmarked vs normal
- destructive vs safe action

## Minimal Reusable Blueprint

If rebuilding in another project, use this structure:

```text
project/
  launcher.py
  feeder.py
  preview.ps1
  actions.py
  config.json
  bookmarks.json
  ui_state/
    preview_mode.txt
    view_mode.txt
```

### Responsibilities

- `launcher.py`: builds `fzf` args and bindings
- `feeder.py`: prints rows as `display<TAB>path`
- `preview.ps1`: renders preview based on file type + mode
- `actions.py`: runs action menu or direct file actions
- `config.json`: colors, roots, ignored items
- `bookmarks.json`: ordered bookmarked entries

## Implementation Steps

1. Build a feeder that prints `display<TAB>path`.
2. Add `fzf` with `--ansi`, `--delimiter`, `--with-nth`, `--multi`.
3. Add a preview script and wire it with `--preview`.
4. Add a help header that lists the shortcuts.
5. Add direct key bindings for the most common actions.
6. Add state files for toggles like preview/view mode.
7. Add bookmarks and make them render first.
8. Add an Enter action menu for multi-select operations.

## Practical Tips

- Keep the real path out of the visible label when possible.
- Use reload bindings instead of rebuilding the whole app process.
- Put complex shell logic in helper scripts, not inline in every `--bind`.
- Store persistent UI state outside the process when toggles matter.
- Prefer bookmarks-first ordering over raw filesystem ordering.
- Hide preview by default if the list itself is the primary task.

## Things To Improve If You Rebuild It

The current design is good, but if you reimplement it elsewhere, these upgrades would make it cleaner:

- move temp helper scripts into real project files instead of generating them dynamically
- centralize config paths instead of hardcoding Windows-specific locations
- avoid embedding large script bodies as Python strings
- use safer quoting for clipboard/run/delete actions
- separate UI styling constants from business logic

## Recommendation

If your next project wants the same UX, copy the pattern, not the file.

Specifically copy:

- `display<TAB>real_path`
- external feeder/preview/action scripts
- persistent mode toggles via small state files
- a visible shortcut header
- direct key bindings plus an Enter action palette
- bookmarks-first ordering

That combination is what gives `Run.py` its shortcut-heavy, polished feel.
