# git mv — Move Files/Folders While Keeping History

## Command

```bash
# Move a file
git mv old/path/file.py new/path/file.py
git commit -m "move file to new location"

# Move a folder
git mv old/folder new/folder
git commit -m "move folder to new location"
```

## Viewing History After Move

```bash
# --follow is required to trace history through the rename
git log --follow new/path/file.py

# With patch (shows diffs too)
git log --follow -p new/path/file.py
```

Without `--follow`, `git log` only shows commits after the move.

---

## Caveats

**`--follow` required every time**
History won't show up without it in CLI. Most GUIs (GitHub web, GitLens, etc.) handle it automatically.

**Rename detection is heuristic**
Git doesn't actually store renames — it detects them by content similarity (default threshold: 50%). If you move AND heavily edit in the same commit, Git may not recognize it as a rename and history will appear broken.

Fix: split into two commits — move first, edit second.

**`--follow` doesn't work on folders**
Only works per-file. For a moved folder you'd run it on each file individually.

**GitHub web UI**
Doesn't always correctly follow renames in blame/history views even with a clean move commit.

**Rebase conflicts**
Rebasing branches that predate the move can confuse Git when resolving the path change.

---

## Tips

- Always use `git mv` instead of manually moving + `git add` — it explicitly records the rename intent
- Check detection worked: `git log --follow file` should show pre-move commits
- If history looks broken after moving, check with `git diff --stat HEAD~1` to confirm Git detected it as a rename (shows `rename old => new`)
