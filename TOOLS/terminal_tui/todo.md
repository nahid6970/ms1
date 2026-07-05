# Task: Browse and restore files at a past commit (no checkout/detach)

## What was asked
- Add ability to browse files at any past commit without detaching HEAD
- Use git ls-tree to list files at that commit
- Use git show hash:path to view file contents (read-only)
- Use git checkout hash -- path to restore specific files (like git_history_restore.py does)
- Add "browse" button on each commit row in graph panel

## Tasks
- [X] Add backend route GET /api/project/<project>/git/tree?hash=<hash> (git ls-tree)
- [X] Add backend route GET /api/project/<project>/git/show?hash=<hash>&path=<file> (git show)
- [X] Add backend route POST /api/project/<project>/git/restore-file (git checkout hash -- path)
- [X] Add "browse" button on each commit row in renderGitGraph
- [X] Add JS: openCommitBrowser(hash, msg) — shows modal with file tree
- [X] Add JS: viewFileAtCommit(hash, path) — opens file content in modal
- [X] Add JS: restoreFileFromCommit(hash, path) — restores file without checkout
- [X] Add click-outside and Escape key close handlers
