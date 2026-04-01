# NEURAL ART V1.0 - SVG EDITOR

A Cyberpunk-themed SVG art tool designed for map alignment and smooth drawing.

## Key Features
- **Smooth Art:** Use the **PEN** tool for freehand drawing with a Cyberpunk aesthetic.
- **Map Alignment:**
    - **LOAD IMG:** Insert a map image behind your art.
    - **MOVE IMG:** Move only the background image to realign it with your SVG art.
    - **MOVE SVG:** Move all your SVG drawings to realign them with the map.
    - **Middle Mouse:** Pan the entire view (SVG + Image together).
    - **Scroll Wheel:** Zoom in/out for precise work.
- **Tools:**
    - **PEN:** Cyberpunk cyan pen.
    - **ERASER:** Removes any item it touches.
    - **RECT/CIRCLE/LINE:** Standard shapes.
    - **COLOR:** Pick your accent color.
    - **THICK:** Slider to adjust stroke width.
- **Save:** Export your creation as a standard `.svg` file.
- **System:**
    - **RESTART:** Hot-reload the application.
    - **SET:** Access system settings.

## Getting Started
Run the script using Python:
```bash
python svg_art.py
```

## Alignment Workflow
1. Load your map image using `LOAD IMG`.
2. Draw your section using the `PEN` or other tools.
3. If you need to "slide" the map for more space:
    - Use `MOVE IMG` to reposition the map while keeping your SVG fixed.
    - OR use `MOVE SVG` to move your drawings while keeping the map fixed.
    - Align the previous portion of your art with the new map section for seamless continuation.
