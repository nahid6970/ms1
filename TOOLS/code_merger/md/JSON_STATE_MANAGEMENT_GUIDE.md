# Preventing Git Churn with Split JSON Configurations

When building applications that save state to a JSON file, a common issue is **Git churn**—where opening a project or slightly interacting with the UI causes Git to constantly detect changes, forcing you to make countless, meaningless commits.

## The Problem
Usually, developers start by saving all settings and session data into a single file (e.g., `config.json`).
*   **Permanent Data**: Global settings, known project paths, theme colors, SVG icons, etc.
*   **Volatile (Temporary) Data**: Recently opened files, click counts, window geometry, recency sorting order, local absolute paths that differ between machines.

If these are stored together, every UI click or app launch updates the volatile data, dirtying the entire file in Git. Furthermore, if you use this single file to sort lists (e.g., storing projects in the exact order they were opened), even if the data doesn't change, the *order* changes, which is a structural change in the JSON that Git detects.

## The Solution: Two JSON Files
To fix this, split the configuration into two explicitly purposed files.

### 1. `settings.json` (Permanent)
**Rules for this file:**
*   **Tracked in Git** (do not add to `.gitignore`).
*   Stores global user preferences, aesthetics, and structural paths.
*   **Must be structurally deterministic:** Any lists (like a list of known projects) MUST be sorted (e.g., alphabetically by path) before saving. This guarantees that loading a project doesn't reshuffle the list and cause a diff.
*   It should **only** change on disk when the user explicitly modifies a global setting or adds a brand-new project.

**Example Content:**
```json
{
  "theme": "dark",
  "font_size": 12,
  "projects": [
    { "path": "C:\\Projects\\AppA", "name": "App A" },
    { "path": "C:\\Projects\\AppB", "name": "App B" }
  ]
}
```

### 2. `session.json` (Temporary / Volatile)
**Rules for this file:**
*   **Ignored by Git** (add to `.gitignore`).
*   Stores all rapidly changing data: click metrics, recency/sort order, selected UI tabs, last opened files.
*   Relies on `settings.json` for base information. For example, it will store the recency list by referencing the `path` key from `settings.json`, and associate volatile states (like `clicks`) with it.

**Example Content:**
```json
{
  "last_sort_mode": "Recency",
  "project_states": [
    {
      "path": "C:\\Projects\\AppB",
      "files_open": ["main.py"],
      "clicks": 15
    },
    {
      "path": "C:\\Projects\\AppA",
      "files_open": ["utils.py"],
      "clicks": 3
    }
  ]
}
```

## Summary of Best Practices
1.  **Split by Volatility:** If a value changes without explicit user configuration (like click counts or recency), it goes in the `.gitignore` temporary JSON.
2.  **Sort Permanent Arrays:** If an array is stored in the permanent JSON, sort it alphabetically or by ID before saving. Never save it in recency order.
3.  **Merge at Runtime:** In your code, load both files and merge them in memory. Use the permanent file for core identities/settings, and layer the volatile session state on top for the UI logic.
