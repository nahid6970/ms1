# recent.md — Forma Handoff

## 1. Project DNA
Vanilla JS + Three.js r161 (no build step), single-page 3D modeling studio inspired by Blender. Three-column layout: left tools/primitives, center WebGL viewport, right scene tree + inspector. Run via `python -m http.server 8000`.

## 2. Latest Implementation

**`vendor/three/`** — Three.js vendored locally (was CDN); `three.module.js`, `OrbitControls.js`, `TransformControls.js` downloaded from unpkg@0.161.0.

**`index.html`**
- Import map updated from `unpkg.com` URLs → `./vendor/three/...` local paths
- Footer hint updated to include `Ctrl+C` / `Ctrl+V` shortcuts

**`app.js`**
- Fixed crash: `transform.getHelper()` doesn't exist in r161 → replaced with `scene.add(transform)`
- Fixed PNG export: `toDataURL()` result now used directly as anchor `href` (was incorrectly wrapped in `Blob`)
- Added `clipboard` variable + `copySelected()` / `pasteObject()` functions
- Ctrl+C copies selected object's full state; Ctrl+V pastes with +0.5 X/Z offset and a fresh name

**`style.css`**
- `.top-actions` width `240px` → `auto` (buttons were wrapping to second line)
- `.text-btn` changed from `float:right` to flexbox (Clear scene icon was dropping below text)

## 3. Critical Context
- Three.js r161 API: `TransformControls` is added directly to scene — **no** `getHelper()` method (added in r169).
- All Three.js files are local under `vendor/`; do NOT switch back to CDN.
- `clipboard` is in-memory only (not persisted to localStorage).

## 4. Pending Task
Test the full feature set in-browser (add, select, transform, copy/paste, save/load, export PNG) and fix any remaining runtime issues.
