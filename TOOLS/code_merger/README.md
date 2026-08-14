# Code Merger // Cyberpunk Edition

A PyQt6 GUI tool to prep local files for AI web UIs (Gemini, ChatGPT, Claude, etc.) and merge the AI's response back to disk — with a full git workflow built in.

## Features

- **Interactive Projects Sidebar** — Pin projects with custom numeric pin indices, categorize with dynamic tags, assign custom icons (Emojis, Nerd Fonts, or SVG).
- **Advanced File Management** — Enable/disable files, toggle between Full and Outline (API skeleton) modes, minify code, filter by name or extension.
- **Smart / Fuzzy Code Matching** — Tolerates minor LLM whitespace or formatting divergences when merging changes.
- **Selective Diff Preview** — Review unified diffs block-by-block and selectively apply changes.
- **Built-in Command Runner** — Execute shell commands (`git status`, `npm test`, etc.) directly within the project directory.
- **Auto Git Commit** — After a successful merge, automatically stage only the changed files and commit. Unrelated dirty files in the repo are never touched.
- **One-click Push** — A PUSH button (enabled after auto-commit) opens a live progress dialog and runs `git push`. All you do is push.

## Requirements

```
pip install PyQt6
```

## Run

```
python merge_gui.py
```

---

## Workflow

### Step 1 — PREP tab
1. Click **NEW ROOT** or drop a folder/files to load your project.
2. Use the **PROJECTS** sidebar to switch between recent projects, pin/unpin, or edit project details (Alias, Category, Icon, Hidden Files).
3. Optionally type your task/instructions in the text box.
4. Click **GENERATE PROMPT** → a full prompt is built and auto-saved to disk.
5. Click **COPY TO CLIPBOARD** and paste into your AI web UI.

### Step 2 — Ask the AI
The AI responds using the `@@FILE` / `@@MODE` / `@@END` format (see `PROMPT_GUIDE.md`). Copy the full response.

### Step 3 — MERGE tab
1. Paste the AI response into the input box.
2. Click **🔍 PARSE CHANGES** to preview what will be modified.
3. Click **✔ APPLY CHANGES**:
   - If **Preview changes** is on, a diff dialog opens. Review block-by-block, check/uncheck individual changes, then click **APPLY SELECTED CHANGES**.
   - If preview is off, changes are applied immediately.
4. Only blocks that applied successfully (`✔`) are ever staged by git. Failed blocks are shown in the results and skipped.

### Step 4 — Git (optional but automatic)
Enable **Auto git add + commit after merge** in the Merge tab options. After a successful apply:
- A **Git Progress dialog** opens showing each `git add` and `git commit` step live.
- Only the merged files are staged — never `git add .`, never anything outside the project root.
- Once committed, the **⬆ PUSH** button lights up. Click it to push — another live progress dialog shows the output.
- If push fails, the button stays enabled so you can retry.

---

## Merge Modes

| Mode | What it does |
|---|---|
| `replace_block` | Replaces a specific block matched by exact or fuzzy search |
| `replace_file` | Overwrites the entire file |
| `insert_after` | Inserts lines after a matched anchor block |
| `delete_block` | Removes a matched block entirely |

---

## Git Safety

- `git add` is called per-file with the exact relative path — never `git add .`
- Files are checked to be inside the project root before staging
- If all merges fail, git is skipped entirely
- The commit runs at the repo root level (required by git), but only the staged files are included
- Other modified files in the same repo are left untouched

---

## Options (Merge Tab)

| Option | Default | Description |
|---|---|---|
| Create .bak backups | On | Saves a timestamped `.bak` copy before modifying any file |
| Preview changes before applying | On | Opens the diff review dialog before writing to disk |
| Auto git add + commit after merge | Off | Stages and commits merged files automatically |
