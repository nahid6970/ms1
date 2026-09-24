# Forma — Implementation Handoff

## Goal

Forma is intended to be a lightweight, browser-based 3D modeling workspace inspired by the essential parts of Blender. It does not need Blender’s full feature set. A user should be able to create simple 3D structures, manipulate them visually, adjust basic materials, and save projects for reuse.

## Intended user experience

The application opens as a three-column studio:

- Left sidebar: creation and transform tools.
- Center: interactive 3D viewport.
- Right sidebar: scene tree and selected-object inspector.

The visual direction is a light, minimal editor with purple accent color, compact controls, and a canvas that shows a grid and soft lighting.

## Intended controls

### Add objects

The left sidebar should add these primitives to the scene:

- Cube
- Sphere
- Cylinder
- Torus

Keyboard shortcuts should also work:

- `1` — add cube
- `2` — add sphere
- `3` — add cylinder
- `4` — add torus

### Transform tools

- Select / `Q`: select an object in the viewport or scene tree.
- Move / `W`: use a 3D translation gizmo.
- Rotate / `E`: use a 3D rotation gizmo.
- Scale / `R`: use a 3D scale gizmo.
- Cut / `T`: use the highlighted cutter modifier and apply a Slice or Band operation.
- `R` while Cut is active: switch the cutter to rotate mode. Use the Move plane / Rotate plane buttons to switch gizmo modes.
- `S` while Cut is active: switch the cutter to scale mode and limit the cut to its resized footprint.
- `F`: frame the selected object with the camera.
- Delete / Backspace: remove the selected object.

The viewport should support orbiting with mouse drag and zooming with the mouse wheel.

### Scene tree

Each created object should appear in the right-side scene tree. Clicking a tree row should select that object and highlight the row.

### Inspector

When an object is selected, the inspector should allow editing:

- Object name
- Position X/Y/Z
- Rotation X/Y/Z in degrees
- Scale X/Y/Z
- Material color
- Metalness
- Roughness

Changes should update the object immediately in the viewport.

### Camera and viewport controls

- Perspective view
- Top view
- Front view
- Grid visibility toggle
- Frame selected object
- Download viewport as PNG

## Saving and loading

The app should support two forms of persistence:

1. Browser-local save using `localStorage`, so the last project returns when the app is reopened in the same browser.
2. Downloadable JSON scene export and JSON file import, so projects can be moved between computers or folders.

The scene JSON format should look like this:

```json
{
  "version": 1,
  "name": "Untitled structure",
  "objects": [
    {
      "name": "Cube 1",
      "type": "box",
      "position": [0, 0.75, 0],
      "rotation": [0, 0, 0],
      "scale": [1, 1, 1],
      "color": "#6f6cff",
      "metalness": 0.2,
      "roughness": 0.4
    }
  ]
}
```

## Current files

- `index.html` — application layout and import map.
- `style.css` — editor styling.
- `app.js` — Three.js scene, camera, controls, object creation, inspector, save/load, and exports.
- `README.md` — basic run instructions.
- `.gitignore` — standard generated-file exclusions.

## Current implementation approach

The app uses Three.js from a CDN import map:

- `three`
- `OrbitControls`
- `TransformControls`

There is no package build step. The intended launch command is:

```powershell
cd C:\@delta\ms1\temporary
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

Do not open `index.html` with a `file://` URL, because browser module imports and CDN requests may be blocked.

### Cut modifier implementation

The Cut tool uses a compact, bounded cutter box attached to a `cutFrame` object and a Three.js `TransformControls` gizmo. The modifier can be translated, rotated, or scaled independently of the selected object. Slice and Band CSG cutters inherit the modifier box position, quaternion, and footprint, so angled or partial cuts do not require rotating the source object. The old full-size translucent preview planes are not used.

## Known problem to investigate

The user reports that every button appears static and no button action works, even after using a local server. This indicates that `app.js` is probably failing before event listeners are registered. The first thing to check in the browser DevTools Console is the first red error, especially:

- CDN or import-map loading failure
- CORS or network failure for `https://unpkg.com`
- `TransformControls` or `OrbitControls` import failure
- A runtime exception while initializing the renderer

The app now contains a startup diagnostic that reveals itself after about 1.8 seconds if `window.__formaStarted` was not set by `app.js`. It is intentionally only a fallback; the next model should inspect the actual browser console error.

## Recommended repair path

1. Open the app through `http://localhost:8000`.
2. Open browser DevTools with `F12` and inspect the Console.
3. Fix the first module/runtime error before changing button handlers.
4. Add a visible test button or console log to confirm `app.js` reaches the event-binding section.
5. Verify that clicking Add Cube creates an object, the scene tree updates, and the inspector becomes active.
6. Verify save, export, load, delete, transform shortcuts, and viewport orbiting.

If CDN loading is unreliable, replace the import-map approach with locally vendored Three.js files or rewrite the prototype around a single self-contained dependency bundle.
