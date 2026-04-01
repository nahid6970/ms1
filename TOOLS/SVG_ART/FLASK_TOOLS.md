# Flask Paint Project - Tool Audit

This list contains all the tools and features identified in `C:\@delta\ms1\@Flask\5004 paint`. 

## 1. Brushes & Strokes
- **Marker (Default):** Standard solid stroke.
- **Airbrush:** Soft, blurred stroke using SVG filters.
- **Multi-line:** Draws 3 parallel lines simultaneously with adjustable spacing.
- **Highlighter:** Semi-transparent stroke (0.4 opacity).
- **Brush Size:** Adjustable via slider (linked to `stroke-width`).

## 2. Shapes & Path Tools
- **Line:** Straight line between two points.
- **Rectangle:** Draggable box.
- **Circle (Ellipse):** Draggable ellipse.
- **Triangle:** 3-point closed path.
- **Poly-Shape:** Multi-click path tool that closes on the start point.
- **Curve (Quadratic):** 3-click tool (Start -> End -> Control Point) for smooth Bezier curves.

## 3. Interactive Tools
- **Eraser:** Removes specific SVG elements on click.
- **Flood Fill (BFS):** Image-based bucket fill that creates an SVG image layer from pixel data.
- **Color Picker (Eyedropper):** Samples color from existing SVG elements.
- **Text Tool:** Click to place, prompts for text input, supports custom fonts (Outfit).
- **Stamps:** FontAwesome icon injector (star, ghost, etc.) with scale-on-drag.

## 4. Visual Guides & Symmetry
- **Radial Symmetry:** Mirrored drawing around a center point (adjustable mirror count).
- **Reflective Symmetry:** Horizontal, Vertical, or Both (quadrant mirroring).
- **Grid System:** Toggleable background grid with adjustable size and "Snap to Grid" logic.
- **Transparency Toggle:** Switch between a white background and a transparent (checkerboard style) canvas.

## 5. System Features
- **History Engine:** Undo/Redo support (up to 30 steps).
- **Gallery System:** Save to server, load from gallery, and delete artwork.
- **Export Engine:** 
    - Save as raw SVG.
    - Export as PNG with custom resolution (manual font rendering to bypass blob limitations).
- **Pan & Zoom:** Smooth viewport navigation.
- **Persistence:** Saves/Loads settings (colors, grid, tool states) via JSON API.
