# Code Merger // Cyberpunk Edition

A PyQt6 GUI tool to prep local files for AI web UIs (Gemini, ChatGPT, Claude, etc.) and merge the AI's response back to disk.

## Features

- **Interactive Projects Sidebar**: Pin projects with custom numeric pin indices, categorize them with dynamic tags, and assign custom icons (Emojis, Nerd Fonts, or SVG).
- **Advanced File Management**: Enable/disable files, toggle between Full and Outline (API skeleton) modes, minify code, and filter by name or extension.
- **Smart / Fuzzy Code Matching**: Tolerates minor LLM whitespace or formatting divergences when merging changes.
- **Selective Diff Preview**: Review unified diffs block-by-block and selectively apply changes.
- **Built-in Command Runner**: Execute shell commands (`git status`, `npm test`, etc.) directly within the project directory.

## Requirements

pip install PyQt6

## Run

python merge_gui.py

---

## Workflow

### Step 1 — PREP tab
1. Click **NEW ROOT** or drop a folder/files to load your project.
2. Use the **PROJECTS** sidebar to switch between recent projects, pin/unpin them, or edit project details (Alias, Category, Icon, Hidden Files).
3. Optionally type your task/instructions in the box.
4. Click **GENERATE PROMPT** → a full prompt is built and auto-saved to disk.
5. Click **COPY TO CLIPBOARD** and paste into your AI web UI.

### Step 2 — Ask the AI
The AI will respond using the `
@@FILE` / `
@@MODE` / `
