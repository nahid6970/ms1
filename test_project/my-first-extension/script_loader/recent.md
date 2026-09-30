# Project Handoff

## 1. Project DNA (Permanent)
Manifest V3 Chrome extension written in vanilla JavaScript and HTML. The popup manages enabled user scripts; a service worker injects them from `user_scripts/` to make custom browser automation easy to toggle.

## 2. Latest Implementation
- `user_scripts/youtube_swap_sections.js` — At viewport width ≥1800 px, moves comments to the right sidebar and suggested videos below the player; below that width, restores the sections and enables YouTube theater mode. Shift+F manually toggles the section swap.

## 3. Critical Context
- Theater mode hides YouTube’s sidebar, so the automatic narrow-window theater layout and the comments/sidebar swap are separate modes.
- YouTube renders pages as an SPA; the script uses navigation events, a mutation observer, and retry polling for late-rendered sections. Resizing returns to the automatic layout.

## 4. Pending Task
Manually verify on YouTube that full-width layout swaps the sections and resizing below 1800 px enables theater mode; test Shift+F in both layouts.
