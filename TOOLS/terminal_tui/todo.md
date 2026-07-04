# Task: Branch Management UI in Git Modal

User wants to manage git branches directly from the git modal:
- Create new branches
- Switch between branches
- Merge a branch into the current branch
- Simple, beginner-friendly UI

## Tasks
- [X] Add backend route: GET /api/project/<project>/git/branches (list all branches)
- [X] Add backend route: POST /api/project/<project>/git/branch/create (create + switch to new branch)
- [X] Add backend route: POST /api/project/<project>/git/branch/switch (switch to existing branch)
- [X] Add backend route: POST /api/project/<project>/git/branch/merge (merge branch into current)
- [X] Add "Branches" collapsible section to git modal HTML (below Past Commits)
- [X] Add JS: loadBranches(), createBranch(), switchBranch(), mergeBranch()
