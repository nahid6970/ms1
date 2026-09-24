# recent.md — Forma Handoff

## 1. Project DNA
Vanilla JS + Three.js r161 (no build step), single-page 3D modeling studio. Three-column layout: left tools/primitives, center WebGL viewport, right scene tree + inspector. Run via `python -m http.server 8000`. All dependencies vendored locally under `vendor/`.

## 2. Latest Implementation

**`vendor/`** — Three.js r161, three-mesh-bvh@0.6.8, three-bvh-csg@0.0.17 all local.

**`app.js`** (full rewrite this session)
- Fixed `transform.getHelper()` crash (r161 API)
- Fixed PNG export (data URL direct, not in Blob)
- `clipboard` + `copySelected()` / `pasteObject()` — Ctrl+C / Ctrl+V, pastes at exact position
- `selected2` for boolean second operand; Shift+click to pick B
- `performBool(op)` — SUBTRACTION/ADDITION/INTERSECTION using `Brush` instances with baked world matrix
- **Cut/Slice tool (T)**: slider-based panel plus a compact cutter-box modifier with a 3D gizmo
  - Move plane mode uses translation arrows to position the cutter
  - Rotate plane mode uses rotation rings; `R` activates it while Cut is active
  - Scale cutter mode resizes the cutter footprint; `S` activates it while Cut is active
  - Shape selector supports Box and Round cylindrical cutters
  - Cutter rotation is independent of the selected object, allowing arbitrary-angle Slice and Band operations
  - A resized cutter limits Slice/Band to the covered portion of the object
  - Band CSG uses the cutter's final visible thickness, including Scale cutter adjustments, so it stays aligned with the preview instead of relying only on the raw Gap value
  - Legacy full-size preview planes were removed; only the bounded cutter box is shown
  - `initCutPanel()` — auto-detects longest axis, sets slider range from bbox
  - `updateCutPlanes()` — positions blue/orange preview planes from `cutPos` / `cutGap`
  - `performSlice()` — splits into 2 pieces with 0.12 gap nudge; switches back to select tool
  - `performBand()` — removes band of `cutGap` thickness centered on `cutPos`
  - Both use `toBakedBrush()` (applies `matrixWorld` to geometry before CSG)

**`index.html`**
- Cut tool card (`T`) added to tool grid (full width)
- `#cut-context` panel: Y/X/Z pills, Slice/Band mode, Position slider, Gap slider, Apply button
- Import map includes `three-mesh-bvh` and `three-bvh-csg`

**`style.css`** — cut-context panel styles, slider styles, bool hint, top-actions/text-btn fixes

## 3. Critical Context
- `three-mesh-bvh` MUST be **0.6.8** — 0.7.x breaks `three-bvh-csg@0.0.17`
- Boolean ops require `Brush` instances (not `mesh.clone()`) — evaluator calls `a.prepareGeometry()`
- Cut CSG uses `toBakedBrush()`: applies `mesh.matrixWorld` to geometry so world-space box cutter aligns correctly
- Cut panel auto-detects axis from longest bbox dimension on tool entry; axis pills override
- `cutPos` is the world-space center of the cut; `cutGap` is full thickness of band (centered, so ±gap/2)
- After apply, tool resets to `select` automatically

## 4. Current verification task
Test the cutter modifier on a cylinder: select → T → choose Box or Round → use Move plane to position the cutter → choose Rotate plane or press `R` → drag a rotation ring → choose Scale cutter or press `S` → resize the footprint/thickness → switch to Band → set Gap → Apply. The source object should remain unrotated while only the covered portion is cut and the result matches the visible cutter.
