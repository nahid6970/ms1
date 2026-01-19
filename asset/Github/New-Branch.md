# Git Repository Optimization: Archive & Truncate History

Run the following block of commands in your terminal to move your current history to an archive branch and reset `main` to a single commit.

**Warning:** This uses a force push. Ensure your teammates are aware they will need to re-clone the repository.

```bash
# 1. Create a backup branch of your current full history
git branch archive-2026

# 2. Create a fresh branch with no history (orphan)
git checkout --orphan temp_main

# 3. Add all current files and create the new base commit
git add -A
git commit -m "New base commit: Truncated history for performance"

# 4. Replace the old main branch with the new one
git branch -D main
git branch -m main

# 5. Update the server (Warning: Overwrites history on 'main')
git push origin main --force
git push origin archive-2026

# 6. Local cleanup to immediately reclaim disk space
git reflog expire --expire=now --all
git gc --prune=now --aggressive
