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
2. Optionally type your task/instructions in the box.
3. Click **GENERATE PROMPT** → a full prompt is built including the format guide + your file contents.
4. Click **COPY TO CLIPBOARD** and paste into Gemini / ChatGPT / AI Studio.

### Step 2 — Ask the AI
The AI will respond using the `@@FILE` / `@@MODE` / `@@END` format defined in `PROMPT_GUIDE.md`.

### Step 3 — MERGE tab
1. Set **Project Root** to the folder that contains your files (paths in the AI response are relative to this).
2. Paste the AI's full response into the text box.
3. Click **PARSE CHANGES** to preview what will be modified.
4. Click **APPLY CHANGES** — done.

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
