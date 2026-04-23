# NEURAL ART V1.6.2 - SYNCED SVG EDITOR

A high-fidelity, Cyberpunk-themed SVG art and neural vectorization tool designed for seamless drawing, map alignment, and image-to-shader processing.

## 🚀 Key Features

### 🎨 Drawing & Neural Shaders
- **Smooth Art:** Antialiased drawing with Marker, Airbrush, Multiline, and Highlighter brush types.
- **Neural Scanner (New!):**
    - **SCAN:** Automatically transform any background image into a stylized grid of vector shapes.
    - **AUTO Mode:** High-fidelity 8-bit color binning (256 groups) to capture every single pixel perfectly.
    - **Smart Cycling:** "Cycle" mode automatically rotates between Rectangle, Circle, and Triangle shaders.
    - **Custom Shaders:** Use your own **Custom Shapes** library to rebuild images with specific logos or designs.
- **Group Recolor:** Manage entire detected color groups instantly. Change every "forest green" grid item to "neon pink" with one click.

### 📐 Positioning & Move Mode (New!)
- **Dedicated Move Toolbar:** Separate toolbar for positioning to prevent conflicts with drawing tools.
- **Move Modes:**
    - **None:** Locked mode for safe painting.
    - **Image:** Move and scale just the background.
    - **SVG:** Move and scale only your art layers.
    - **Both:** Move everything together.
    - **Symmetry Center:** Interactively reposition the center of your radial/reflection symmetry.

### 🔍 Advanced Scaling & Zoom
- **Targeted Zoom:** Choose exactly what to scale (**Both**, **Image**, or **SVG**) using the **TARGET** dropdown.
- **Manual Control:**
    - **VAL%:** Type an exact percentage (1% to 5000%) for numerical precision.
    - **STEP%:** Customize how much each zoom increment adds/removes (Default: 5%).
- **Shortcuts:** **Ctrl + Plus (+)** and **Ctrl + Minus (-)** for rapid navigation.

### 🛠️ Toolset & Customization
- **Shapes:** Rect, Circle, Triangle, and Polygon tools.
- **Custom Shapes:** Save any selection of your art as a reusable custom shape or import external SVG path data.
- **Symmetry:** Radial (up to 100 mirrors) and Reflection (H, V, Both) support.
- **Grid System:** Toggleable grid with snapping and custom sizing.
- **Backgrounds:** Change canvas background color or load/remove images (Red **X** button).

## ⌨️ Keyboard Shortcuts
- **Ctrl + Z / Y:** Undo / Redo (Supports batch undo for image scans).
- **Ctrl + Plus (+):** Zoom In (Target-aware).
- **Ctrl + Minus (-):** Zoom Out (Target-aware).
- **Escape:** Cancel current Polygon/Curve drawing.
- **Middle Mouse:** Pan the entire workspace.

## 🛠️ Getting Started
Run the script using Python 3 and PyQt6:
```bash
python svg_art.py
```

## 📋 Neural Workflow
1. **Load Image:** Use the cyan **IMAGE** button on the right.
2. **Align:** Select **MOVE MODE: Image** to position and scale your background.
3. **Scan:** Set your **DEN** (Density) and check **AUTO**. Select a **SHP** (Shape) and click **SCAN**.
4. **Recolor:** Use the **PALETTE** icon to tweak the color groups.
5. **Draw:** Switch **MOVE MODE** to **None** and use the **PEN** or **POLY** tools to finish your piece.
6. **Export:** Click the green **SAVE** disk icon to get your standard `.svg` file.
