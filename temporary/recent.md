# recent.md — Forma Handoff

## 1. Project DNA
Vanilla JS + Three.js r161 (no build step), single-page 3D modeling studio. Three-column layout: left tools/primitives, center WebGL viewport, right scene tree + inspector. Run via `python -m http.server 8000`.

## 2. Latest Implementation

**`vendor/`** — Three.js r161, three-mesh-bvh@0.6.8, three-bvh-csg@0.0.17 all vendored locally.

**`index.html`**
- Import map: all three libs point to `./vendor/...`
- Added CUT/SLICE section in left panel (axis pills Y/X/Z, position, thickness, two action buttons)
- Added BOOLEAN OPS section (Subtract/Union/Intersect, requires Shift+click second object)

**`app.js`**
- Fixed `transform.getHelper()` crash (r161 API — use `scene.add(transform)` directly)
- Fixed PNG export (data URL used directly, not wrapped in Blob)
- `clipboard` + `copySelected()` / `pasteObject()` — Ctrl+C / Ctrl+V, pastes at exact position
- `selected2` for second boolean operand; Shift+click to select B
- `performBool(op)` — uses `Brush` instances (not `.clone()`), SUBTRACTION/ADDITION/INTERSECTION
- `cutAxis`, `csgSubtractBox()` helper, `performSlice()` (splits into 2 halves), `performBand()` (removes a thickness band)

**`style.css`** — cut panel styles, bool hint, top-actions width fix, text-btn flex fix

## 3. Critical Context
- `three-mesh-bvh` MUST be **0.6.8** — 0.7.x breaks `three-bvh-csg@0.0.17` (`prepareGeometry` API changed)
- `TransformControls` r161: add to scene directly, NO `getHelper()` method
- Boolean ops require `Brush` instances, NOT `mesh.clone()` — evaluator calls `a.prepareGeometry()`
- All libs are local under `vendor/`; do NOT switch to CDN

## 4. Pending Task
Test cut/slice on a cylinder: select it, pick Y axis, set position to the center Y, click "Remove band" to get two rings. Verify boolean subtract still works after the three-mesh-bvh downgrade.
