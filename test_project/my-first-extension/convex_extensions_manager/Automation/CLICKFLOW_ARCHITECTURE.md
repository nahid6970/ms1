# ClickFlow Automator — Technical Architecture Guide

This document provides a comprehensive overview of the ClickFlow Automator Chrome Extension architecture, data schemas, and execution model to help future development cycles build on top of this structure without breaking existing sequences.

---

## 1. Core Architecture Overview
ClickFlow is a Manifest V3 Chrome Extension designed for complex, sequential page automations. It consists of three primary modules:
*   **Popup Window (`popup.html` / `popup.js`)**: The user control center where you create project profiles, manage automation configurations, configure standard or conditional steps, and trigger runs.
*   **Content Script (`content.js`)**: The active runtime execution engine injected directly into target pages. It executes step sequences, runs evaluations, handles page-load resume logic, and interfaces with the web DOM.
*   **Background Worker (`background.js`)**: Operates as a light-weight relay. It handles notification dispatch, manages active element-picking states across tabs, and programmatically reopens the popup when element selection completes.

---

## 2. Storage Schema & Profiles Model
The state is managed inside `chrome.storage.local`. To maintain backwards compatibility with existing content script lookups and Convex Cloud backup modules, the active profile is mirrored dynamically at the storage root.

{
  "activeProjectId": "proj_1709230000000",
  "projects": [
    {
      "id": "proj_1709230000000",
      "name": "Default Profile",
      "steps": [],
      "loopCount": 1,
      "loopDelay": 1.0,
      "waitTimeout": 0
    }
  ],
  "steps": [],
  "loopCount": 1,
  "loopDelay": 1.0,
  "waitTimeout": 0,
  "automationState": {
    "status": "idle",
    "currentLoop": 0,
    "currentStep": 0,
    "logs": []
  }
}

Whenever edits are performed or settings are updated in the popup, changes are saved via `saveToActiveProjectAndStorage(changes)`, which writes them to both the active item inside the `projects` array and mirrors them as root keys. This ensures that `content.js` always loads the active profile using simple, lightweight lookups.

---

## 3. Automation Steps & Conditional Branching Model
Standard steps execute sequentially. To support complex branching, a special `'branch'` action step evaluates conditions concurrently to avoid unnecessary waiting.

### Step Object Schema
{
  "id": 2,
  "action": "branch",
  "timeout": 5,                 // Wait timeout for conditions to be resolved
  "logicMode": "all",           // IF match rules: 'all' (AND) or 'any' (OR)
  "conditions": [               // IF condition list
    {
      "type": "visible",
      "selector": "#mdm-stats",
      "value": ""
    }
  ],
  "thenSteps": [                // Infinitely nestable sub-steps
    { "action": "click", "selector": ".btn-success", "delay": 0.5 }
  ],
  "elseIfLogicMode": "all",     // ELSE-IF match rules
  "elseIfConditions": [         // ELSE-IF condition list
    {
      "type": "visible",
      "selector": "#mdm-no-stats",
      "value": ""
    }
  ],
  "elseIfSteps": [              // Infinitely nestable sub-steps
    { "action": "click", "selector": ".btn-alternate", "delay": 0.5 }
  ],
  "elseSteps": [                // Default fallback if neither condition is met on timeout
    { "action": "navigate", "value": "https://example.com/reset", "delay": 1.0 }
  ]
}

### Condition Types
*   `exists`, `visible`, `clickable` (checks element states via selector).
*   `text_contains`, `text_equals` (checks element text content).
*   `url_contains`, `url_equals` (checks current page location).
*   `value_contains`, `value_equals` (checks element input fields).

### Execution Engine (`content.js` - `evaluateConcurrentConditions`)
The engine executes branching rules concurrently. In a continuous `while` loop until `timeoutSeconds` expires:
1. It evaluates the `IF` (THEN) conditions. If they match, it instantly terminates and runs `thenSteps`.
2. It evaluates the `ELSE-IF` conditions. If they match, it instantly terminates and runs `elseIfSteps`.
3. If neither matches, it yields for `500ms` and retries.
4. If the timeout expires without matches, it falls back to executing the `elseSteps`.

This concurrent check removes layout-trapping lag, meaning that if `#mdm-no-stats` appears after only 1 second, the engine immediately switches paths without wasting the rest of the timeout duration.

---

## 4. UI Layout & Sizing Engineering
Chromium enforces a hard limit of `800px` width by `600px` height on popups. To maximize visual real-estate, prevent double scrollbar conflicts, and optimize performance:

*   **No Redundant Vertical Rows**: The "Start/Stop Automation" controls (`#toggleBtn`) are integrated directly into the header adjacent to the Profile dropdown and Backup actions.
*   **Window Constraints**: The body has `overflow: hidden !important` and `.steps-list` is capped at a strict height of `410px` with `scroll-behavior: smooth;`. This guarantees that only a single, unified scrollbar is rendered, eliminating mouse-wheel focus traps.
*   **Space-Saving Collapsible Editors**: Branch step cards use native, hardware-accelerated HTML `<details>` and `<summary>` components to collapse optional paths (ELSE-IF, ELSE) by default. Cards only expand when custom pathways are actively configured.
*   **GPU Rendering Optimization**: The `.step-card` class applies `transform: translate3d(0, 0, 0);` to force GPU compositing. This prevents paint recalculation bottlenecks when scrolling large, expanded branching elements.
*   **Responsive Input Flexbox**: Squeezed, inline pixel widths on input fields are replaced with flexbox weightings (`flex: 2` for selectors, `flex: 1` for values) allowing inputs to dynamically stretch across the entire `800px` width.

---

## 5. Developer Cheat-Sheet for Next AI Session

### Adding a New Simple Action Type
1. Add the option to the `.step-action-select` inside `popup.js`'s `renderSteps()`.
2. Add the corresponding evaluation rules inside `content.js`'s `executeStandardAction(step, label, waitTimeout, selectorMode)`.

### Modifying Element Pickers
*   When picking is triggered, `startPickMode()` sets `pickingStepId`.
*   If picking for standard steps, it sets a simple ID like `1`.
*   If picking for branches, it passes a composite token: `cond_stepId_condType_condIdx` or `substep_stepId_subStepType_subIdx`.
*   `background.js` parses this token, traverses the correct nested JSON fields, performs the write, updates the active project in the `projects` list, and calls `chrome.action.openPopup()` to automatically bring the extension interface back to the foreground.
