# Forma — Browser 3D Studio

A lightweight, dependency-free-to-install browser 3D modeling workspace inspired by the essential parts of Blender.

## Run it

Serve this folder with any local static server:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000`. No package download or build required — Three.js and CSG libraries are vendored locally under `vendor/`.

## Features

### Primitives
- Cube, Sphere, Cylinder, Torus
- Keyboard shortcuts: `1` `2` `3` `4`

### Transform tools
- **Select** `Q` — click objects in viewport or scene tree
- **Move** `W` — 3D translation gizmo
- **Rotate** `E` — 3D rotation gizmo
- **Scale** `R` — 3D scale gizmo
- **Cut / Slice** `T` — slider-based cut tool (see below)
- `F` — frame selected object
- `Delete` / `Backspace` — remove selected object

### Cut / Slice tool (`T`)
Select an object, press `T`. The left panel shows:
- **Cut modifier box** — a compact highlighted cutter with transform arrows in the viewport
- **Move plane** — drag the colored arrows to position the cut
- **Rotate plane** — drag the rotation rings, or press `R` while Cut is active, to cut at any angle
- **Scale cutter** — resize the cutter box, or press `S` while Cut is active, to limit the operation to part of the object and adjust its visible thickness
- **Uniform size** — when Scale cutter is active, use the proportional size slider to shrink below `1.00×` or enlarge above `1.00×`
- **Shape: Box / Round** — use a rectangular cutter or a cylindrical round cutter
- **Y / X / Z** — quickly align the cutter to a world axis (auto-picks the longest dimension initially)
- **⊟ Slice** — splits object into two pieces at the cut position
- **⊠ Band** — removes a band of chosen thickness (e.g. cylinder → two rings)
- **Position slider** — drag to move the cut plane through the object
- **Gap slider** (Band mode) — set how thick the removed section is; the applied cut matches the cutter’s final visible thickness
- **✓ Apply cut** — executes the operation
- `Esc` — cancel

The object itself does not need to be rotated for angled cuts; rotate the cutter modifier instead. A resized cutter performs a partial slice or partial band removal within its footprint.
Generated cut pieces keep their own transform origin, so Move/Rotate/Scale gizmos appear on the selected piece after cutting, saving, or loading.

### Boolean operations
Select object A, then Shift+click object B. Three operations available:
- **Subtract** (A−B) — cuts B's shape out of A
- **Union** (A∪B) — merges both into one solid
- **Intersect** (A∩B) — keeps only the overlapping volume

### Copy / Paste
- `Ctrl+C` — copy selected object
- `Ctrl+V` — paste at same position (then move with `W`)

### Camera & viewport
- Orbit: mouse drag · Zoom: scroll wheel
- Perspective / Top / Front view buttons
- Grid toggle, frame selection, viewport PNG download

### Scene tree & inspector
- All objects listed in the right panel; click to select
- Edit name, position, rotation, scale, color, metalness, roughness

### Save & load
- **Save** (`⌘`) — saves to browser localStorage, restores on next visit
- **Export** — downloads scene as `.json`
- **Load** — imports a previously exported `.json`

## Vendored libraries
All under `vendor/` — no CDN required:
- `three@0.161.0`
- `three-mesh-bvh@0.6.8`
- `three-bvh-csg@0.0.17`
