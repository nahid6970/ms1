# Git Ref Rescue GUI

A small Tkinter-based helper for repairing broken Git refs after a crash or interrupted write.

## What it does

- scans loose refs under `.git/refs`
- repairs broken refs from `packed-refs`, reflog entries, or `ORIG_HEAD`
- fetches `origin --prune`
- restores the current branch's upstream to `origin/<branch>`
- shows the current branch, upstream, HEAD, and local/remote ref state

## When to use it

Use it when Git starts showing symptoms like:

- `HEAD` or `origin/main` cannot be resolved
- `git branch -vv` shows `upstream gone`
- a crash or power loss leaves a ref file zeroed out or unreadable

## Run

```powershell
python .\TOOLS\Github\gitManager\git_ref_rescue_gui.py
```

## Buttons

- `Refresh` updates the status panel
- `Scan Broken Refs` repairs loose refs it can recover from local metadata
- `Repair Current Branch` runs the full recovery flow for the checked-out branch
- `Fetch Origin` refreshes remote tracking refs
- `Set Upstream` reattaches the current branch to `origin/<branch>`

## Notes

- The tool is conservative. It prefers recovering from local metadata before writing new ref values.
- It is meant for branch-based repositories, not detached HEAD workflows.
