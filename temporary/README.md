# Forma — Browser 3D Studio

Forma is a small, dependency-free-to-install browser 3D modeling workspace inspired by the essential parts of Blender: add primitives, select them in a scene tree, move/rotate/scale them, tune material appearance, and save reusable scenes locally.

## Run it

Because the app uses ES modules, serve this folder with any local static server. For example:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000` in a browser. No package download or build is required; Three.js is loaded from its browser CDN import map.

## Included

- Cube, sphere, cylinder, and torus primitives
- Orbit camera, perspective/top/front views, grid toggle, frame selection
- Select, move, rotate, and scale tools with keyboard shortcuts
- Scene tree and object inspector
- Position, rotation, scale, color, metalness, and roughness controls
- Browser-local save and automatic restore
- Downloadable JSON scene files and PNG viewport snapshots
