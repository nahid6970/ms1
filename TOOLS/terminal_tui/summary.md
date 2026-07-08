# Terminal TUI - AI Copilot Enhancement Summary

This document provides a comprehensive summary of all changes, implementations, and configurations made to the Terminal TUI project. Use this as a starting point for future coding sessions.

---

## 🛠️ Features Implemented & Enhanced

### 1. Settings Dashboard with Sub-Window Navigation
- **SVG Icon Tabs Bar**: Added a row of 7 large, clean, animated vector SVG buttons at the top of the global settings modal, allowing users to toggle between individual settings pages instead of navigating a single giant vertical form.
- **Sections**: Created separate sub-windows for General & Typography, Sidebar & Layout, Terminal & Editor Behavior, Voice Recording Settings, AI Copilot Settings, and Current Workspace Badge.
- **Direct Icon Mapping Link**: Hooked the 7th tab button (Custom Extension Icons) to directly trigger the Extension Icons Modal window for immediate file mapping configurations.

### 2. Chat Font Sizing & Relative Markdown Scaling
- **Chat Font Size setting**: Added a settings input to dynamically scale `#ai-chat-history` text size.
- **Relative EM Sizing**: Converted hardcoded font-sizes on headings (`h1`-`h6`), inline code tags, and code blocks (`pre code`) inside the markdown rendering stylesheet from absolute `rem` values to relative `em` percentages. This allows all formatted AI output text to scale perfectly along with the user's custom font size.
- **Table Support**: Removed the hardcoded `0.72rem` font size on markdown tables, setting it to `inherit` so table headers and contents match the font-size chosen in settings.

### 3. Dynamic Chat & Popover Sizing
- **Dynamic Growth Height**: Configured `#ai-copilot-popover` to stretch dynamically as the chat thread expands, capped up to the user-defined **Max Height** setting or the top boundary of the browser window (`calc(100vh - 50px)`). Once it hits the boundary, `#ai-chat-history` scrolls internally.
- **Blue Border Outline**: Added a sleek `1.5px solid var(--accent-color)` themed border outline around the active copilot popover window.

### 4. Visibility Settings Table Columns & Width Adjustment
- **Increased Modal Width**: Expanded the width of `#ai-model-filter-modal` to `850px` (with `95vw` max-width), providing plenty of room for all spec columns (RPD, Used, RPM, TPD, TPM, Speed, and %) and entirely eliminating horizontal scrollbars.
- **Used RPD Edits**: Enabled manual used requests cell edits (`makeUsedRequestsCellEditable`) which posts transaction logs to the backend to rewrite local usage statistics.

### 5. Model Speed Selector & Categorization
- Added speed categories (`Fast`, `Medium`, `Slow`, `None`) inside the AI Model Visibility Settings modal (`#ai-model-filter-modal`), the Batch Tester modal, and bulk configuration controls.
- Kept neutral grey text styles for models categorized with a speed of `None`.

### 6. Daily Usage Percentage (`%`) Indicators
- Replaced normal text labels with color-coded remaining usage percentage tags based on **RPD (Requests Per Day)**.
- Calculated dynamic values by parsing specifications like `14.4K`, `1.5K`, or numbers, and subtracting the daily request logs count from `localStorage` usage history.
- Built a clean, crisp **vector SVG icon** to render the default infinity (`∞`) sign when no RPD limit is set.
- Extended the selected model trigger label (`#ai-model-dd-trigger`) to render the selected model name alongside its current remaining usage `%` and speed tags.

### 7. Custom Fallback & Direction Settings
- Added custom settings in the Settings Form (`#settings-form`):
  - **Custom Fallback Usage Sign Toggle & Textbox**: Lets users define a custom sign (e.g. `None`, `N/A`) instead of the default `∞` vector symbol.
  - **Show AI Dropdowns Above Trigger**: Class-driven styling `.ai-dropdown-reverse` that forces the provider/model dropdown options menu to slide up *above* the trigger element instead of downwards.

### 8. Persistent System Prompt buttons
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
