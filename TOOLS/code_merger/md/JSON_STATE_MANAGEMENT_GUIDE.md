# Preventing Git Churn with JSON Configs

Mixing permanent settings and volatile session data in a single JSON file causes constant Git churn because every minor UI interaction (like opening an item or changing sort order) dirties the file.

**The Solution:** Split your state into two explicit files.

### 1. `settings.json` (Permanent & Tracked)
*   **Purpose:** Global settings, aesthetics, and core structural entities.
*   **Git:** Tracked (do NOT ignore).
*   **Rule:** Arrays must be deterministically sorted (e.g., alphabetically by ID). It should only update when you explicitly change a global setting or add a brand-new entity.

### 2. `session.json` (Volatile & Ignored)
*   **Purpose:** Rapidly changing data (interaction metrics, recency/sort order, window positions).
*   **Git:** Add to `.gitignore`.
*   **Rule:** Reference entities from `settings.json` using their unique ID, and map them to their volatile states (like click counts or expanded UI states).

### Implementation
1. Load both files at runtime.
2. Merge them in memory using a common unique identifier.
3. Use `settings.json` for identity/configuration, and `session.json` for UI logic and session state.
