# Terminal TUI - AI Copilot Enhancement Summary

This document provides a comprehensive summary of all changes, implementations, and configurations made to the Terminal TUI project. Use this as a starting point for future coding sessions.

---

## 🛠️ Features Implemented & Enhanced

### 1. Model Speed Selector & Categorization
- Added speed categories (`Fast`, `Medium`, `Slow`, `None`) inside the AI Model Visibility Settings modal (`#ai-model-filter-modal`), the Batch Tester modal, and bulk configuration controls.
- Kept neutral grey text styles for models categorized with a speed of `None`.

### 2. Daily Usage Percentage (`%`) Indicators
- Replaced normal text labels with color-coded remaining usage percentage tags based on **RPD (Requests Per Day)**.
  - **Green** (`#10b981` / `rgba(16, 185, 129, 0.15)` bg) $\rightarrow$ usage $> 50\%$.
  - **Yellow** (`#f59e0b` / `rgba(245, 158, 11, 0.15)` bg) $\rightarrow$ usage between $10\%$ and $50\%$.
  - **Red** (`#f87171` / `rgba(248, 113, 113, 0.15)` bg) $\rightarrow$ usage $< 10\%$.
- Calculated dynamic values by parsing specifications like `14.4K`, `1.5K`, or numbers, and subtracting the daily request logs count from `localStorage` usage history.
- Built a clean, crisp **vector SVG icon** to render the default infinity (`∞`) sign when no RPD limit is set.
- Extended the selected model trigger label (`#ai-model-dd-trigger`) to render the selected model name alongside its current remaining usage `%` and speed tags.

### 3. Custom Fallback & Direction Settings
- Added custom settings in the Settings Form (`#settings-form`):
  - **Custom Fallback Usage Sign Toggle & Textbox**: Lets users define a custom sign (e.g. `None`, `N/A`) instead of the default `∞` vector symbol.
  - **Show AI Dropdowns Above Trigger**: Class-driven styling `.ai-dropdown-reverse` that forces the provider/model dropdown options menu to slide up *above* the trigger element instead of downwards.

### 4. Visibility Settings Table Columns
- Added a **Used** (Used RPD) requests column immediately following the `RPD` spec column.
- Added a `%` remaining percentage column immediately following the `Speed` column.
- Configured sorting handlers for both `%` (`pct`) and `Used` (`used_rpd`) columns.
- Rearranged spec columns layout to match the sequence: `RPD` $\rightarrow$ `Used` $\rightarrow$ `RPM` $\rightarrow$ `TPD` $\rightarrow$ `TPM`.
- Built a new **Used daily requests editable helper** (`makeUsedRequestsCellEditable`) that sends a POST request to the python backend to rewrite usage log history on cell changes, refreshing stats instantly.

### 5. Persistent System Prompt buttons
- Replaced the old system prompt select dropdown with gracefully wrapping buttons.
- Added complete custom styling controls in `#ai-system-prompt-modal` to configure individual style attributes for both **Active** and **Inactive** button states:
  - Background (BG) & Foreground (FG) color chips.
  - Border Width, Border Radius, and Border Color.
  - Custom font family search selector widget (`#settings-font-select-trigger`).

---

## 💾 Storage & Backend Architecture

- **Local Storage Configurations**:
  - `ai-system-prompts`: Stores custom prompts as a JSON array of objects.
  - `terminal-font-family`: Global app font style.
  - `ai-dropdown-reverse`: Boolean toggled via settings checkbox.
  - `ai-custom-fallback-sign-toggle` & `ai-custom-fallback-sign-text`: Configures the fallback character.
- **Python Flask Backend (`app.py`)**:
  - GET `/api/ai-usage`: Loads usage stats from `ai_usage.json`.
  - POST `/api/ai-usage/set-requests`: Re-writes `ai_usage.json` for a specific model/provider by replacing the past 24 hours logs with the desired count of mock records to preserve frontend edits.

---

## 📁 Key File Locations

- **Main Frontend Interface**:
  - HTML & Scripts: [templates/index.html](file:///C:/@delta/ms1/TOOLS/terminal_tui/templates/index.html)
- **Backend Application**:
  - Server Routing: [app.py](file:///C:/@delta/ms1/TOOLS/terminal_tui/app.py)
- **Usage Database**:
  - JSON logs: [ai_usage.json](file:///C:/@delta/ms1/TOOLS/terminal_tui/ai_usage.json)
