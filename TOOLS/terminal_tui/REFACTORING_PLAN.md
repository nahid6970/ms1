# Architectural Refactoring Plan: Terminal TUI

Currently, the application relies on a single, monolithic `index.html` file (14,000+ lines) containing structure (HTML), styling (CSS), and logic (JS). This document outlines a phased approach to breaking down the application into a maintainable, modern modular structure.

## End Goal Architecture
We will migrate to a modern web development stack:
- **Build Tool:** Vite (for fast, modular bundling)
- **Language:** TypeScript (for type safety and better IDE support)
- **Styling:** Modular CSS / SCSS
- **Structure:** ES Modules (breaking logic into separate, focused files)

---

## Phase 1: CSS Extraction
*Goal: Separate concerns and clean up the HTML file.*

1. **Create `styles/` Directory:**
   - Extract all global CSS from the `<style>` blocks in `index.html` into `styles/global.css`.
   - Extract component-specific styles into separate files (e.g., `styles/modals.css`, `styles/tooltips.css`).
2. **Link CSS:** 
   - Update `index.html` to load these external stylesheets via `<link>`.
3. **Clean Up Inline Styles:**
   - Systematically move inline `style="..."` attributes into dedicated CSS classes in the respective stylesheets.

---

## Phase 2: JavaScript Modularization (Vanilla JS)
*Goal: Break the massive script block into logical ES modules without changing the build process yet.*

1. **Create `js/` Directory:**
   - Set up `type="module"` in `index.html` for script execution.
2. **Extract State Management:**
   - Create `js/state.js` to handle all `localStorage` reads/writes, `aiChatHistory`, and active application state variables.
3. **Extract API & Network Logic:**
   - Create `js/api.js` for all `fetch` calls, streaming logic, and server communications.
4. **Extract UI & DOM Manipulation:**
   - Create focused modules:
     - `js/modals.js` (opening/closing/rendering settings, filters, etc.)
     - `js/chat.js` (rendering chat messages, handling input)
     - `js/sidebar.js` (handling workspaces and navigation)
5. **Extract Utilities:**
   - Create `js/utils.js` for generic helper functions (e.g., formatters, cryptology, event debouncing).

---

## Phase 3: Build System Integration (Vite + TypeScript)
*Goal: Introduce a bundler and strict typing for long-term scalability.*

1. **Initialize Vite:**
   - Run `npm create vite@latest` to set up the build environment.
2. **Convert JS to TS:**
   - Rename `.js` files to `.ts`.
   - Define interfaces for core data structures (e.g., `ChatMessage`, `ModelSpec`, `AccountSettings`).
3. **Fix Type Errors:**
   - Address the implicit `any` errors and null-checks required by TypeScript.
4. **Bundle Application:**
   - Point Vite to `index.html` as the entry point and build the optimized production assets.

---

## Phase 4: Framework Consideration (Optional but Recommended)
*Goal: Drastically simplify complex DOM updates and state synchronization.*

Given the heavy amount of dynamic DOM rendering (modals, dropdowns, chat history updates), maintaining Vanilla TS will still require manual DOM manipulation.
- **Migrate to React or Vue:** 
  - Convert HTML templates into JSX/Components.
  - Replace manual DOM updates with reactive state variables.
  - (This phase can be planned in more detail once Phase 1-3 are complete).

---

## Next Steps
When you are ready to begin, we will start strictly with **Phase 1: CSS Extraction** to minimize risk and ensure the UI doesn't break during the transition.
