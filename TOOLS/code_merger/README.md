# Code Merger

A PyQt6 GUI tool to prep local files for AI web UIs (Gemini, ChatGPT, etc.) and merge the AI's response back to disk.

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
1. Click **ADD FILES** (or **ADD DIR**) to load the files you want the AI to modify.
2. Use **RECENT** to quickly load previously used projects, rename their aliases, or open them in File Explorer.
3. Optionally type your task/instructions in the box.
4. For a brand-new project, click **ADD DIR / ROOT** and choose the empty folder you want to use as the project root.
5. Click **GENERATE PROMPT** → a full prompt is built even if no local files are present yet.
6. Use **NOTEBOOKLM PROMPT** when you want the same file context as the normal prompt, but with a shorter instruction header tuned for NotebookLM-style output.
7. Click **COPY TO CLIPBOARD** and paste into Gemini / ChatGPT / AI Studio.

### Step 2 — Ask the AI
The AI will respond using the `@@FILE` / `@@MODE` / `@@END` format defined in `PROMPT_GUIDE.md`.
The AI may also suggest shell commands for you to run.

### Step 3 — MERGE tab
1. Set **Project Root** to the folder that contains your files (paths in the AI response are relative to this).
2. Paste the AI's full response into the text box.
3. Click **PARSE CHANGES** to preview what will be modified.
4. Click **APPLY CHANGES** — done.

### Step 4 — COMMAND tab (Optional)
1. Run arbitrary shell commands (e.g., `git status`, `npm run test`) directly from the GUI.
2. The working directory defaults to your active project root.
3. Click **COPY OUTPUT** to quickly feed the results back to the AI.

---

## Change Format Reference

| Mode | Effect |
|------|--------|
| `replace_block` | Replaces an exact block of code within a file |
| `replace_file` | Rewrites the entire file |
| `insert_after` | Inserts lines after a specific anchor line |
| `delete_block` | Deletes an exact block of code |

Backups are created automatically as `filename.bak_YYYYMMDD_HHMMSS` (toggle in UI).

---

## Files

| File | Purpose |
|------|---------|
| `merge_gui.py` | Main GUI application |
| `PROMPT_GUIDE.md` | Format guide included in every generated prompt |
| `README.md` | This file |
