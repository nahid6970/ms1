# 🎨 NeoPaint - Infinite Web Art Studio

NeoPaint is a modern, high-performance web-based drawing application built with **Flask** and **HTML5 Canvas**. It features an "infinite" canvas engine, advanced layer-like rendering for shapes, optimized drawing performance, and a sleek dark-mode interface.

## 🚀 Features

### 🖌️ Professional Tools
- **Brush & Eraser**: Smooth, pressure-simulated drawing curves.
- **Shape Tools**: Draw **Lines**, **Rectangles**, and **Circles** with real-time preview (using a lag-free overlay engine).
- **Flood Fill**: Advanced algorithm to fill bounded areas with color.
- **Color Picker**: Eyedropper tool to pick any color from the canvas.

### ♾️ Infinite Canvas Engine
- **Dynamic Expansion**: The canvas automatically grows by 800px if you draw near the edges (optimized for performance).
- **Pan & Zoom**:
  - **Pan**: Hold `Ctrl` + `Left Click` and drag to move around.
  - **Zoom**: Use the `Mouse Wheel` to zoom in/out relative to your cursor.
- **Optimized Rendering**: Uses a dual-canvas system (Drawing layer + Overlay layer) for high-performance updates.
- **Performance Optimizations**: 
  - Throttled drawing at 60+ FPS for smooth performance
  - Compressed history saving with JPEG format
  - Deferred expensive operations to prevent UI blocking
  - Optimized canvas context settings for better rendering

### 💾 Gallery System
- **Save Work**: Instantly save your masterpieces to the server.
- **Gallery Browser**: View all your saved artworks with previews.
- **Load System**: Click any artwork to load it back onto the canvas (auto-resizes viewport).
- **Management**: Delete old or unwanted artworks directly from the UI.

## 🛠️ Technology Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5, Vanilla JavaScript (ES6+), CSS3 (Variables, Flexbox/Grid)
- **Rendering**: HTML5 `<canvas>` API with 2D Context
- **Performance**: Optimized drawing engine with throttling, compressed history, and async operations

## 🎮 Controls & Shortcuts

| Action | Shortcut / Control |
|--------|-------------------|
| **Brush** | `B` |
| **Eraser** | `E` |
| **Fill Bucket** | `F` |
| **Eye Dropper** | `I` |
| **Undo** | `Ctrl + Z` |
| **Pan Canvas** | Hold `Ctrl` + `Drag Mouse` (or Middle Click drag) |
| **Zoom** | `Mouse Scroll` |

## 📦 How to Run

1. **Install Requirements**
   ```bash
   pip install flask
   ```

2. **Start the Server**
   ```bash
   python app.py
   ```

3. **Open in Browser**
   Navigate to `http://127.0.0.1:5004`

## 📂 Project Structure
- `app.py`: Flask server handling saves, loads, and deletions.
- `static/js/script.js`: Core engine logic with performance optimizations (input handling, rendering, state management).
- `static/css/style.css`: Modern styling with glassmorphism effects.
- `saved_art/`: Directory where user artworks are stored.

## ⚡ Performance Features
- **Lag-Free Drawing**: Optimized drawing engine prevents lag during continuous painting
- **Smart Canvas Management**: Starts with 1500x1500px canvas, expands dynamically as needed
- **Throttled Rendering**: 60+ FPS drawing with intelligent throttling
- **Compressed History**: JPEG compression reduces memory usage by 60-80%
- **Async Operations**: Non-blocking history saves and canvas expansions
- **Optimized Context**: Hardware-accelerated rendering with `desynchronized` mode
