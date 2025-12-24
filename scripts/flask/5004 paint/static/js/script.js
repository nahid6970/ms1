document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const canvas = document.getElementById('drawing-canvas');
    const ctx = canvas.getContext('2d', {
        willReadFrequently: true,
        alpha: false // Disable alpha channel for better performance
        // desynchronized: true removed to fix rendering sync issues
    });

    // Overlay Canvas for performance (shapes/preview)
    const overlayCanvas = document.getElementById('overlay-canvas');
    const ctxOverlay = overlayCanvas.getContext('2d', {
        alpha: true // Overlay needs transparency
        // desynchronized: true removed
    });

    const viewport = document.getElementById('viewport');

    // Inputs
    const toolsBtns = document.querySelectorAll('.tool-btn');
    const brushSizeInput = document.getElementById('brush-size');
    const sizeValDisplay = document.getElementById('size-val');
    const colorPicker = document.getElementById('color-picker');
    const swatchesContainer = document.getElementById('color-swatches');
    const toggleSwatchesBtn = document.getElementById('toggle-swatches');

    // Actions
    const btnClear = document.getElementById('btn-clear');
    const btnSave = document.getElementById('btn-save');
    const btnGallery = document.getElementById('btn-gallery');

    // Grid Settings
    const gridShowToggle = document.getElementById('grid-show');
    const gridSnapToggle = document.getElementById('grid-snap');
    const gridSizeInput = document.getElementById('grid-size');
    const gridSizeVal = document.getElementById('grid-size-val');
    const snapIndicator = document.getElementById('snap-indicator');

    // Canvas Container for Transforms
    const canvasContainer = document.querySelector('.canvas-container');

    // Modal
    const modal = document.getElementById('gallery-modal');
    const closeModal = modal.querySelector('.close-modal');
    const galleryGrid = document.getElementById('gallery-grid');

    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');

    // Symmetry Settings
    const symRadialBtn = document.getElementById('sym-radial');
    const symReflectBtn = document.getElementById('sym-reflect');

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        const isCollapsed = sidebar.classList.contains('collapsed');
        toggleBtn.innerHTML = isCollapsed ? '<i class="fa-solid fa-chevron-right"></i>' : '<i class="fa-solid fa-bars"></i>';
    });

    // --- State ---
    const state = {
        isDrawing: false,
        isPanning: false,
        tool: 'brush', // brush, eraser, line, rect, circle, fill, picker
        brushType: 'marker', // marker, highlighter, pen, pencil, calligraphy, airbrush
        color: '#000000',
        size: 5,
        startX: 0,
        startY: 0,
        // Snapshot removed, we use overlay now
        history: [],
        historyStep: -1,
        maxHistory: 20,

        // Viewport / Camera State
        scale: 1,
        panX: 0,
        panY: 0,
        lastMouseX: 0,
        lastMouseY: 0,

        // Performance optimizations
        lastDrawTime: 0,
        pendingHistorySave: false,

        // Polygon State
        polyPoints: [],

        // Mirror State
        mirrorCount: 4,
        reflectType: 'horizontal', // horizontal, vertical, both
        symmetry: 'none', // none, radial, reflect

        // Curve State
        curvePoints: [],

        // Grid State
        gridShow: false,
        gridSnap: false,
        gridSize: 40,
        points: [] // stores points for smoothing
    };

    // Initialize
    function init() {
        // Start with a smaller, more reasonable size for better performance
        canvas.width = 1500;
        canvas.height = 1500;

        syncOverlay();

        // White bg for main canvas
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        updateContext();
        saveHistory();
        generateSwatches();
        centerCanvas();
    }

    function syncOverlay() {
        overlayCanvas.width = canvas.width;
        overlayCanvas.height = canvas.height;
        updateContext(); // Re-apply styles to both contexts
    }

    function generateSwatches() {
        const colors = [
            '#ffffff', '#000000', '#808080', '#c0c0c0',
            '#ff0000', '#ffff00', '#00ff00', '#00ff00', '#00ffff', '#0000ff', '#ff00ff',
            '#800000', '#808000', '#008000', '#008080', '#000080', '#800080',
            '#ffa500', '#ffc0cb', '#00d2ff', '#795548'
        ];

        swatchesContainer.innerHTML = '';
        colors.forEach(c => {
            const el = document.createElement('div');
            el.className = 'swatch';
            el.style.backgroundColor = c;
            el.dataset.color = c;
            el.addEventListener('click', () => setColor(c));
            swatchesContainer.appendChild(el);
        });
    }

    function updateContext() {
        // Main
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.lineWidth = state.size;

        // Reset effects
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1.0;

        const isEraser = state.tool === 'eraser';

        if (!isEraser) {
            if (state.brushType === 'airbrush') {
                ctx.shadowBlur = state.size;
                ctx.shadowColor = state.color;
            } else if (state.brushType === 'pencil') {
                ctx.globalAlpha = 0.2; // Very faint for layering
                ctx.shadowBlur = 1;
                ctx.shadowColor = state.color;
            } else if (state.brushType === 'highlighter') {
                ctx.globalAlpha = 0.4;
            } else if (state.brushType === 'pen') {
                ctx.shadowBlur = 0; // Crisp
            }
        }

        ctx.strokeStyle = isEraser ? '#ffffff' : state.color;
        ctx.fillStyle = isEraser ? '#ffffff' : state.color;

        // Overlay context should match current style 
        ctxOverlay.lineCap = 'round';
        ctxOverlay.lineJoin = 'round';
        ctxOverlay.lineWidth = state.size;
        ctxOverlay.strokeStyle = state.color;
        ctxOverlay.fillStyle = state.color;
        ctxOverlay.shadowBlur = isEraser ? 0 : ctx.shadowBlur;
        ctxOverlay.shadowColor = isEraser ? 'transparent' : ctx.shadowColor;
        ctxOverlay.globalAlpha = isEraser ? 1.0 : ctx.globalAlpha;
    }

    function updateCursor() {
        const newCursor = state.isPanning ? 'grabbing' : 'crosshair';
        if (viewport.style.cursor !== newCursor) {
            viewport.style.cursor = newCursor;
        }
    }

    function setColor(color) {
        state.color = color;
        colorPicker.value = color;
        if (state.tool === 'eraser') {
            setTool('brush');
        } else {
            updateContext();
        }
    }

    function setTool(toolName) {
        state.tool = toolName;

        toolsBtns.forEach(b => {
            if (b.id.startsWith('tool-')) {
                if (b.id === `tool-${toolName}`) b.classList.add('active');
                else b.classList.remove('active');
            }
        });

        if (toolName !== 'poly') {
            state.polyPoints = [];
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        }
        if (toolName !== 'curve') {
            state.curvePoints = [];
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        }

        updateContext();
    }

    function setSymmetry(mode) {
        if (state.symmetry === mode) {
            state.symmetry = 'none';
        } else {
            state.symmetry = mode;
            if (mode === 'radial') {
                const input = prompt("Enter number of mirror folders (e.g. 4, 6, 8, 12):", state.mirrorCount);
                const val = parseInt(input);
                if (val && val > 0) state.mirrorCount = val;
            } else if (mode === 'reflect') {
                const input = prompt("Mirror Type? (H)orizontal, (V)ertical, or (B)oth/Opposite:", "H");
                const choice = (input || "").toLowerCase();
                if (choice === 'v' || choice === 'vertical') state.reflectType = 'vertical';
                else if (choice === 'b' || choice === 'both') state.reflectType = 'both';
                else state.reflectType = 'horizontal';
            }
        }

        // Update UI
        symRadialBtn.classList.toggle('active', state.symmetry === 'radial');
        symReflectBtn.classList.toggle('active', state.symmetry === 'reflect');
    }

    symRadialBtn.addEventListener('click', () => setSymmetry('radial'));
    symReflectBtn.addEventListener('click', () => setSymmetry('reflect'));

    function setBrushType(type) {
        state.brushType = type;
        const types = ['marker', 'highlighter', 'pen', 'pencil', 'calligraphy', 'airbrush'];
        types.forEach(t => {
            const btn = document.getElementById(`type-${t}`);
            if (btn) btn.classList.toggle('active', t === type);
        });
        updateContext();
    }

    ['marker', 'highlighter', 'pen', 'pencil', 'calligraphy', 'airbrush'].forEach(t => {
        const btn = document.getElementById(`type-${t}`);
        if (btn) btn.addEventListener('click', () => setBrushType(t));
    });

    function centerCanvas() {
        const vW = viewport.clientWidth;
        const vH = viewport.clientHeight;
        // Center the canvas
        state.panX = (vW - canvas.width) / 2;
        state.panY = (vH - canvas.height) / 2;
        state.scale = 0.8;
        updateTransform();
    }

    function updateTransform() {
        // Pixel-perfect rendering when not zooming? 
        // CSS translate allows subpixels, but that's fine for smooth pan.
        canvasContainer.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.scale})`;
    }

    // --- Dynamic Expansion (Optimized) ---
    function checkBoundsAndExpand(x, y) {
        // Only expand on mousedown, not during drawing to prevent lag
        // If x,y is close to edge or outside, expand canvas.
        let newWidth = canvas.width;
        let newHeight = canvas.height;
        let shiftX = 0;
        let shiftY = 0;
        const buffer = 300; // Reduced buffer for less aggressive expansion
        let expandInfo = "";

        // Check Right/Bottom
        if (x > canvas.width - buffer) {
            newWidth += 800; // Smaller expansion chunks
            expandInfo = "right";
        }
        if (y > canvas.height - buffer) {
            newHeight += 800;
            expandInfo = "down";
        }

        // Check Left/Top (Harder because requires shifting context)
        if (x < buffer && x < 0) {
            const add = 800;
            newWidth += add;
            shiftX = add;
            expandInfo = "left";
        }
        if (y < buffer && y < 0) {
            const add = 800;
            newHeight += add;
            shiftY = add;
            expandInfo = "up";
        }

        if (newWidth !== canvas.width || newHeight !== canvas.height) {
            // Defer expansion to avoid blocking drawing
            requestAnimationFrame(() => {
                resizeCanvas(newWidth, newHeight, shiftX, shiftY);
            });
            return { shiftX, shiftY };
        }
        return { shiftX: 0, shiftY: 0 };
    }

    function resizeCanvas(w, h, shiftX, shiftY) {
        // Save current content
        const copy = document.createElement('canvas');
        copy.width = canvas.width;
        copy.height = canvas.height;
        copy.getContext('2d').drawImage(canvas, 0, 0);

        // Resize
        canvas.width = w;
        canvas.height = h;

        // Restore background
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, w, h);

        // Restore content
        ctx.drawImage(copy, shiftX, shiftY);

        // Update overlay
        syncOverlay();

        // Adjust view if we shifted left/top so user doesn't lose position
        if (shiftX !== 0 || shiftY !== 0) {
            state.panX -= shiftX * state.scale;
            state.panY -= shiftY * state.scale;
            updateTransform();
        }

        if (shiftX !== 0) showToast("Canvas expanded left");
        else if (shiftY !== 0) showToast("Canvas expanded up");
        else showToast("Canvas expanded");
    }

    // --- History System (Optimized) ---
    function saveHistory() {
        // Debounce history saving to avoid excessive operations
        if (state.pendingHistorySave) return;

        state.pendingHistorySave = true;

        // Use requestAnimationFrame to defer the expensive operation
        requestAnimationFrame(() => {
            if (state.historyStep < state.history.length - 1) {
                state.history = state.history.slice(0, state.historyStep + 1);
            }

            // Only save smaller canvas regions when possible, or compress the data
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8); // Use JPEG with compression
            state.history.push(dataUrl);

            if (state.history.length > state.maxHistory) {
                state.history.shift();
            } else {
                state.historyStep++;
            }

            state.pendingHistorySave = false;
        });
    }

    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
            e.preventDefault();
            undo();
        }
        if (e.key === 'Control') {
            viewport.style.cursor = 'grab';
        }
    });

    document.addEventListener('keyup', (e) => {
        if (e.key === 'Control') {
            viewport.style.cursor = 'crosshair';
        }
    });

    function undo() {
        if (state.historyStep > 0) {
            state.historyStep--;
            const img = new Image();
            img.src = state.history[state.historyStep];
            img.onload = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
            };
        }
    }

    // --- Coordinate System ---
    function getPos(e) {
        const rect = viewport.getBoundingClientRect();
        const viewportMouseX = e.clientX - rect.left;
        const viewportMouseY = e.clientY - rect.top;

        let x = (viewportMouseX - state.panX) / state.scale;
        let y = (viewportMouseY - state.panY) / state.scale;

        if (state.gridSnap) {
            x = Math.round(x / state.gridSize) * state.gridSize;
            y = Math.round(y / state.gridSize) * state.gridSize;
        }

        return { x, y };
    }

    // --- Input Handling ---

    viewport.addEventListener('wheel', (e) => {
        e.preventDefault();
        const rect = viewport.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const worldX = (mouseX - state.panX) / state.scale;
        const worldY = (mouseY - state.panY) / state.scale;

        const zoomIntensity = 0.1;
        const wheel = e.deltaY < 0 ? 1 : -1;
        const newScale = Math.min(Math.max(0.1, state.scale + wheel * zoomIntensity * state.scale), 5);

        state.panX = mouseX - worldX * newScale;
        state.panY = mouseY - worldY * newScale;
        state.scale = newScale;

        updateTransform();
    }, { passive: false });

    viewport.addEventListener('mousedown', (e) => {
        // Middle mouse or Ctrl+Left to pan
        if (e.button === 1 || (e.button === 0 && (e.ctrlKey || e.metaKey))) {
            state.isPanning = true;
            state.lastMouseX = e.clientX;
            state.lastMouseY = e.clientY;
            viewport.style.cursor = 'grabbing';
            e.preventDefault();
            return;
        }

        if (e.button === 0) {
            startDrawing(e);
        }
    });

    window.addEventListener('mousemove', (e) => {
        if (state.isPanning) {
            const dx = e.clientX - state.lastMouseX;
            const dy = e.clientY - state.lastMouseY;
            state.panX += dx;
            state.panY += dy;
            state.lastMouseX = e.clientX;
            state.lastMouseY = e.clientY;
            updateTransform();

            // Auto expand while panning if we reach edge??
            // Maybe not, too aggressive.
            return;
        }

        if (state.isDrawing || state.tool === 'poly' || state.tool === 'curve') {
            draw(e);
        }

        // Show snap indicator if snapping is on
        if (state.gridSnap) {
            const pos = getPos(e);
            snapIndicator.style.display = 'block';
            snapIndicator.style.left = pos.x + 'px';
            snapIndicator.style.top = pos.y + 'px';
        } else {
            snapIndicator.style.display = 'none';
        }
    });

    window.addEventListener('mouseup', (e) => {
        if (state.isPanning) {
            state.isPanning = false;
            viewport.style.cursor = e.ctrlKey ? 'grab' : 'crosshair';
            return;
        }
        stopDrawing();
    });

    function startDrawing(e) {
        let pos = getPos(e);

        // Check bounds and expand if needed
        const shift = checkBoundsAndExpand(pos.x, pos.y);

        // If shifted, update pos
        if (shift.shiftX !== 0 || shift.shiftY !== 0) {
            pos.x += shift.shiftX;
            pos.y += shift.shiftY;
        }

        state.isDrawing = true;
        state.startX = pos.x;
        state.startY = pos.y;
        state.lastX = pos.x;
        state.lastY = pos.y;
        state.points = [pos];

        // Tools logic
        if (state.tool === 'fill') {
            fill(pos.x, pos.y, state.color);
            saveHistory();
            state.isDrawing = false;
            return;
        }

        if (state.tool === 'picker') {
            pickColor(pos.x, pos.y);
            state.isDrawing = false;
            return;
        }

        if (state.tool === 'text') {
            addTextPrompt(e);
            state.isDrawing = false;
            return;
        }

        if (state.tool === 'poly') {
            handlePolyClick(pos);
            state.isDrawing = false; // Poly is click-based, not drag-based
            return;
        }

        if (state.tool === 'curve') {
            handleCurveClick(pos);
            state.isDrawing = false;
            return;
        }

        if (state.tool === 'brush') {
            drawSymmetric(ctxOverlay, (c) => {
                c.beginPath();
                c.moveTo(pos.x, pos.y);
                c.lineTo(pos.x, pos.y);
                c.stroke();
            });
        } else if (state.tool === 'eraser') {
            drawSymmetric(ctx, (c) => {
                c.beginPath();
                c.moveTo(pos.x, pos.y);
                c.lineTo(pos.x, pos.y);
                c.stroke();
            });
        } else {
            // Shapes: Clear overlay
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        }
    }

    function drawSymmetric(targetCtx, actionFn) {
        const w = canvas.width;
        const h = canvas.height;

        if (state.symmetry === 'none') {
            actionFn(targetCtx);
        } else if (state.symmetry === 'radial') {
            const cx = w / 2;
            const cy = h / 2;
            const step = (Math.PI * 2) / state.mirrorCount;
            targetCtx.save();
            for (let i = 0; i < state.mirrorCount; i++) {
                targetCtx.setTransform(1, 0, 0, 1, 0, 0);
                targetCtx.translate(cx, cy);
                targetCtx.rotate(step * i);
                targetCtx.translate(-cx, -cy);
                actionFn(targetCtx);
            }
            targetCtx.restore();
        } else if (state.symmetry === 'reflect') {
            // Original
            actionFn(targetCtx);

            // Reflected
            targetCtx.save();
            if (state.reflectType === 'horizontal') {
                targetCtx.translate(w, 0);
                targetCtx.scale(-1, 1);
            } else if (state.reflectType === 'vertical') {
                targetCtx.translate(0, h);
                targetCtx.scale(1, -1);
            } else if (state.reflectType === 'both') {
                targetCtx.translate(w, h);
                targetCtx.scale(-1, -1);
            }
            actionFn(targetCtx);
            targetCtx.restore();
        }
    }

    function draw(e) {
        if (!state.isDrawing && state.tool !== 'poly' && state.tool !== 'curve') return;

        // Light throttling for better performance (reduced from 16ms to 8ms for more responsiveness)
        const now = performance.now();
        if (now - state.lastDrawTime < 8) return;
        state.lastDrawTime = now;

        const pos = getPos(e);

        if (state.tool === 'poly') {
            if (state.polyPoints.length > 0) {
                ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
                const last = state.polyPoints[state.polyPoints.length - 1];

                drawSymmetric(ctxOverlay, (c) => {
                    c.beginPath();
                    c.moveTo(state.polyPoints[0].x, state.polyPoints[0].y);
                    for (let i = 1; i < state.polyPoints.length; i++) {
                        c.lineTo(state.polyPoints[i].x, state.polyPoints[i].y);
                    }
                    c.lineTo(pos.x, pos.y);
                    c.stroke();
                });

                // Start point highlighter (draw normally, not symmetric for less clutter)
                const start = state.polyPoints[0];
                ctxOverlay.fillStyle = state.color;
                ctxOverlay.beginPath();
                ctxOverlay.arc(start.x, start.y, 8, 0, Math.PI * 2);
                ctxOverlay.fill();

                const dist = Math.sqrt(Math.pow(pos.x - start.x, 2) + Math.pow(pos.y - start.y, 2));
                if (dist < 20) {
                    ctxOverlay.fillStyle = 'rgba(0, 255, 0, 0.3)';
                    ctxOverlay.beginPath();
                    ctxOverlay.arc(start.x, start.y, 20, 0, Math.PI * 2);
                    ctxOverlay.fill();
                }
            }
            return;
        }

        if (state.tool === 'curve') {
            if (state.curvePoints.length > 0) {
                ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
                const p0 = state.curvePoints[0];

                drawSymmetric(ctxOverlay, (c) => {
                    c.beginPath();
                    if (state.curvePoints.length === 1) {
                        c.moveTo(p0.x, p0.y);
                        c.lineTo(pos.x, pos.y);
                    } else if (state.curvePoints.length === 2) {
                        const p1 = state.curvePoints[1];
                        c.moveTo(p0.x, p0.y);
                        c.quadraticCurveTo(pos.x, pos.y, p1.x, p1.y);
                    }
                    c.stroke();
                });

                // Draw dots (unsymmetric)
                ctxOverlay.fillStyle = state.color;
                state.curvePoints.forEach(p => {
                    ctxOverlay.beginPath();
                    ctxOverlay.arc(p.x, p.y, 4, 0, Math.PI * 2);
                    ctxOverlay.fill();
                });
            }
            return;
        }

        if (state.tool === 'brush') {
            state.points.push(pos);
            const pts = state.points;
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

            drawSymmetric(ctxOverlay, (c) => {
                c.beginPath();
                if (state.brushType === 'marker' || state.brushType === 'highlighter') {
                    if (pts.length > 2) {
                        c.moveTo(pts[0].x, pts[0].y);
                        for (let i = 1; i < pts.length - 2; i++) {
                            const mid = { x: (pts[i].x + pts[i + 1].x) / 2, y: (pts[i].y + pts[i + 1].y) / 2 };
                            c.quadraticCurveTo(pts[i].x, pts[i].y, mid.x, mid.y);
                        }
                        // last segments
                        const p1 = pts[pts.length - 2];
                        const p2 = pts[pts.length - 1];
                        c.quadraticCurveTo(p1.x, p1.y, p2.x, p2.y);
                    } else if (pts.length === 2) {
                        c.moveTo(pts[0].x, pts[0].y);
                        c.lineTo(pts[1].x, pts[1].y);
                    }
                    c.stroke();
                } else if (state.brushType === 'pencil') {
                    // Graphite texture: multiple thin jittered passes
                    const passes = 3;
                    for (let j = 0; j < passes; j++) {
                        c.beginPath();
                        c.lineWidth = 1;
                        const offX = (Math.random() - 0.5) * state.size;
                        const offY = (Math.random() - 0.5) * state.size;

                        c.moveTo(pts[0].x + offX, pts[0].y + offY);
                        for (let i = 1; i < pts.length; i++) {
                            const jitterX = (Math.random() - 0.5) * (state.size / 3);
                            const jitterY = (Math.random() - 0.5) * (state.size / 3);
                            c.lineTo(pts[i].x + offX + jitterX, pts[i].y + offY + jitterY);
                        }
                        c.stroke();
                    }
                } else if (state.brushType === 'calligraphy') {
                    const nibSize = state.size;
                    const angle = -Math.PI / 4;
                    const nx = Math.cos(angle) * nibSize;
                    const ny = Math.sin(angle) * nibSize;
                    for (let i = 1; i < pts.length; i++) {
                        const pPrev = pts[i - 1];
                        const pCurr = pts[i];
                        c.moveTo(pPrev.x - nx, pPrev.y - ny);
                        c.lineTo(pPrev.x + nx, pPrev.y + ny);
                        c.lineTo(pCurr.x + nx, pCurr.y + ny);
                        c.lineTo(pCurr.x - nx, pCurr.y - ny);
                        c.closePath();
                        c.fill();
                        c.stroke();
                    }
                } else {
                    // Pen, Pencil, and everything else path-based
                    c.moveTo(pts[0].x, pts[0].y);
                    for (let i = 1; i < pts.length; i++) {
                        c.lineTo(pts[i].x, pts[i].y);
                    }
                    c.stroke();
                }
            });
            state.lastX = pos.x;
            state.lastY = pos.y;
        } else if (state.tool === 'eraser') {
            const last = { x: state.lastX, y: state.lastY };
            drawSymmetric(ctx, (c) => {
                c.beginPath();
                c.moveTo(last.x, last.y);
                c.lineTo(pos.x, pos.y);
                c.stroke();
            });
            state.lastX = pos.x;
            state.lastY = pos.y;
        } else {
            // Shapes: Draw to Overlay
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
            drawSymmetric(ctxOverlay, (c) => {
                c.beginPath();
                if (state.tool === 'line') {
                    c.moveTo(state.startX, state.startY);
                    c.lineTo(pos.x, pos.y);
                } else if (state.tool === 'rect') {
                    c.strokeRect(state.startX, state.startY, pos.x - state.startX, pos.y - state.startY);
                } else if (state.tool === 'circle') {
                    const r = Math.sqrt(Math.pow(pos.x - state.startX, 2) + Math.pow(pos.y - state.startY, 2));
                    c.arc(state.startX, state.startY, r, 0, 2 * Math.PI);
                }
                c.stroke();
            });
        }
    }

    function stopDrawing() {
        if (!state.isDrawing) return;
        state.isDrawing = false;
        state.points = [];

        if (['line', 'rect', 'circle', 'brush'].includes(state.tool)) {
            // Commit overlay to main
            // CRITICAL: Reset globalAlpha for the commit, otherwise 
            // transparency is applied twice (once in overlay, once in drawImage)
            ctx.save();
            ctx.globalAlpha = 1.0;
            ctx.globalCompositeOperation = 'source-over';
            ctx.drawImage(overlayCanvas, 0, 0);
            ctx.restore();

            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        } else {
            ctx.closePath();
        }

        if (state.tool !== 'picker' && state.tool !== 'fill' && state.tool !== 'text' && state.tool !== 'poly' && state.tool !== 'mirror' && state.tool !== 'reflect' && state.tool !== 'curve') {
            // Defer history saving to avoid blocking the UI
            setTimeout(() => saveHistory(), 50);
        } else if (state.tool === 'mirror' || state.tool === 'reflect') {
            setTimeout(() => saveHistory(), 50);
        }
    }

    // --- Tools Imp ---
    function pickColor(x, y) {
        if (x < 0 || y < 0 || x >= canvas.width || y >= canvas.height) return;
        const p = ctx.getImageData(x, y, 1, 1).data;
        const hex = "#" + ("000000" + rgbToHex(p[0], p[1], p[2])).slice(-6);
        setColor(hex);
        setTool('brush');
        showToast(`Color picked: ${hex}`, 'info');
    }

    function rgbToHex(r, g, b) {
        if (r > 255 || g > 255 || b > 255)
            throw "Invalid color component";
        return ((r << 16) | (g << 8) | b).toString(16);
    }

    function fill(x, y, fillColor) {
        if (x < 0 || y < 0 || x >= canvas.width || y >= canvas.height) return;

        // Fill logic (Standard Flood Fill)
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        x = Math.floor(x);
        y = Math.floor(y);
        const startPos = (y * canvas.width + x) * 4;
        const startR = data[startPos];
        const startG = data[startPos + 1];
        const startB = data[startPos + 2];
        const startA = data[startPos + 3];

        const tempDiv = document.createElement('div');
        tempDiv.style.color = fillColor;
        document.body.appendChild(tempDiv);
        const style = window.getComputedStyle(tempDiv);
        const rgb = style.color.match(/\d+/g);
        document.body.removeChild(tempDiv);
        const fillR = parseInt(rgb[0]);
        const fillG = parseInt(rgb[1]);
        const fillB = parseInt(rgb[2]);
        const fillA = 255;

        if (startR === fillR && startG === fillG && startB === fillB && startA === fillA) return;

        const stack = [[x, y]];

        function match(pos) {
            return data[pos] === startR && data[pos + 1] === startG && data[pos + 2] === startB && data[pos + 3] === startA;
        }

        function colorPixel(pos) {
            data[pos] = fillR;
            data[pos + 1] = fillG;
            data[pos + 2] = fillB;
            data[pos + 3] = fillA;
        }

        while (stack.length) {
            let [cx, cy] = stack.pop();
            let pixelPos = (cy * canvas.width + cx) * 4;

            while (cy >= 0 && match(pixelPos)) {
                cy--;
                pixelPos -= canvas.width * 4;
            }
            cy++;
            pixelPos += canvas.width * 4;

            let reachLeft = false;
            let reachRight = false;

            while (cy < canvas.height && match(pixelPos)) {
                colorPixel(pixelPos);

                if (cx > 0) {
                    if (match(pixelPos - 4)) {
                        if (!reachLeft) {
                            stack.push([cx - 1, cy]);
                            reachLeft = true;
                        }
                    } else if (reachLeft) {
                        reachLeft = false;
                    }
                }

                if (cx < canvas.width - 1) {
                    if (match(pixelPos + 4)) {
                        if (!reachRight) {
                            stack.push([cx + 1, cy]);
                            reachRight = true;
                        }
                    } else if (reachRight) {
                        reachRight = false;
                    }
                }

                cy++;
                pixelPos += canvas.width * 4;
            }
        }

        ctx.putImageData(imageData, 0, 0);
    }

    // --- UI Events ---
    toolsBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (btn.id.startsWith('tool-')) {
                const t = btn.id.replace('tool-', '');
                setTool(t);
            }
        });
    });

    brushSizeInput.addEventListener('input', (e) => {
        state.size = e.target.value;
        sizeValDisplay.textContent = state.size;
        updateContext();
    });

    colorPicker.addEventListener('input', (e) => {
        setColor(e.target.value);
    });

    btnClear.addEventListener('click', () => {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        updateContext();
        saveHistory();
        showToast('Canvas cleared!');
    });

    btnSave.addEventListener('click', () => {
        const dataURL = canvas.toDataURL('image/png');
        btnSave.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

        fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataURL })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast('Masterpiece saved successfully!');
                } else {
                    showToast('Failed to save.', 'error');
                }
            })
            .catch(err => showToast('Error saving: ' + err, 'error'))
            .finally(() => {
                btnSave.innerHTML = '<i class="fa-solid fa-floppy-disk"></i>';
            });
    });

    btnGallery.addEventListener('click', () => {
        modal.classList.add('open');
        loadGallery();
    });

    closeModal.addEventListener('click', () => {
        modal.classList.remove('open');
    });

    modal.querySelector('.modal-overlay').addEventListener('click', () => {
        modal.classList.remove('open');
    });

    function loadGallery() {
        galleryGrid.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</div>';

        fetch('/gallery')
            .then(res => res.json())
            .then(images => {
                galleryGrid.innerHTML = '';
                if (images.length === 0) {
                    galleryGrid.innerHTML = '<div style="grid-column:1/-1;text-align:center;">No drawings yet. Time to create!</div>';
                    return;
                }

                images.forEach(src => {
                    const item = document.createElement('div');
                    item.className = 'gallery-item';

                    const img = document.createElement('img');
                    img.src = src;

                    // Click on image to load
                    img.addEventListener('click', () => {
                        loadFromGallery(src);
                    });

                    // Delete button
                    const actions = document.createElement('div');
                    actions.className = 'gallery-actions';

                    const delBtn = document.createElement('div');
                    delBtn.className = 'delete-btn';
                    delBtn.innerHTML = '<i class="fa-solid fa-trash"></i>';
                    delBtn.title = "Delete Artwork";

                    delBtn.addEventListener('click', (e) => {
                        e.stopPropagation(); // prevent load
                        deleteArtwork(src, item);
                    });

                    actions.appendChild(delBtn);
                    item.appendChild(img);
                    item.appendChild(actions);

                    galleryGrid.appendChild(item);
                });
            });
    }

    function deleteArtwork(src, itemElement) {
        if (!confirm('Delete this artwork permanently?')) return;

        const filename = src.split('/').pop();

        fetch('/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    itemElement.remove();
                    showToast('Artwork deleted.');
                } else {
                    showToast('Failed to delete: ' + data.error, 'error');
                }
            })
            .catch(err => showToast('Error: ' + err, 'error'));
    }

    function loadFromGallery(src) {
        if (!confirm("Load this image? Current artwork will be overwritten.")) return;

        const img = new Image();
        img.src = src;
        img.crossOrigin = "Anonymous";
        img.onload = () => {
            // Resize canvas to match the saved image exactly so it fits perfectly
            // This is safer than trying to center on a potentially huge canvas
            canvas.width = img.width;
            canvas.height = img.height;

            // Sync overlay size
            const overlayCanvas = document.getElementById('overlay-canvas');
            if (overlayCanvas) {
                overlayCanvas.width = canvas.width;
                overlayCanvas.height = canvas.height;
            }

            // Reset view to center of new canvas
            // We need to fetch viewport dimensions again since we are in a closure
            const vW = document.getElementById('viewport').clientWidth;
            const vH = document.getElementById('viewport').clientHeight;

            state.panX = (vW - canvas.width) / 2;
            state.panY = (vH - canvas.height) / 2;
            state.scale = 0.8;
            updateTransform();

            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);

            // Re-apply context settings because resizing resets context
            updateContext();

            saveHistory();
            modal.classList.remove('open');
            showToast('Artwork loaded!');
        };
        img.onerror = () => {
            showToast('Failed to load image.', 'error');
        };
    }

    function showToast(msg, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        let icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        if (type === 'info') icon = 'fa-info-circle';

        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${msg}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s reverse forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    window.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT') return;
        switch (e.key.toLowerCase()) {
            case 'b': setTool('brush'); break;
            case 'e': setTool('eraser'); break;
            case 'f': setTool('fill'); break;
            case 'i': setTool('picker'); break;
            case 't': setTool('text'); break;
            case 'p': setTool('poly'); break;
            case 'm': setSymmetry('radial'); break;
            case 'v': setSymmetry('reflect'); break;
            case 'c': setTool('curve'); break;
        }
    });

    function addTextPrompt(e) {
        const pos = getPos(e);
        const mouseX = e.clientX;
        const mouseY = e.clientY;

        const input = document.createElement('input');
        input.type = 'text';
        input.style.position = 'fixed';
        input.style.left = mouseX + 'px';
        input.style.top = mouseY + 'px';
        input.style.background = 'transparent';
        input.style.border = '1px dashed ' + state.color;
        input.style.color = state.color;

        // Scale font size so 5px brush isnt invisible text
        // Minimum 14px, otherwise brushSize * 2
        const fontSize = Math.max(14, state.size * 2);
        input.style.font = `${fontSize}px 'Outfit', sans-serif`;
        input.style.zIndex = 1000;
        input.style.padding = '0';
        input.style.margin = '0';
        input.style.outline = 'none';

        document.body.appendChild(input);

        // Auto focus
        setTimeout(() => input.focus(), 10);

        let active = true;

        const cleanup = () => {
            if (!active) return;
            active = false;

            const text = input.value;
            if (text) {
                ctx.font = `bold ${fontSize}px 'Outfit', sans-serif`;
                ctx.fillStyle = state.color;
                ctx.textBaseline = 'top';
                ctx.fillText(text, pos.x, pos.y);
                saveHistory();
            }

            input.remove();

            // Restore tool if needed, or just keep as text
            state.isDrawing = false;
        };

        input.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter') {
                cleanup();
            }
        });

        input.addEventListener('blur', () => {
            cleanup();
        });
    }

    function handlePolyClick(pos) {
        // If clicking near first point (within 10px), close functionality
        if (state.polyPoints.length > 2) {
            const start = state.polyPoints[0];
            const dist = Math.sqrt(Math.pow(pos.x - start.x, 2) + Math.pow(pos.y - start.y, 2));
            if (dist < 20) {
                // Close shape
                drawSymmetric(ctx, (c) => {
                    c.beginPath();
                    c.moveTo(state.polyPoints[0].x, state.polyPoints[0].y);
                    for (let i = 1; i < state.polyPoints.length; i++) {
                        c.lineTo(state.polyPoints[i].x, state.polyPoints[i].y);
                    }
                    c.closePath();
                    c.stroke();
                });

                state.polyPoints = [];
                ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
                saveHistory();
                return;
            }
        }

        // Add point
        state.polyPoints.push(pos);

        // Draw current state on overlay
        ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        if (state.polyPoints.length > 0) {
            drawSymmetric(ctxOverlay, (c) => {
                c.beginPath();
                c.moveTo(state.polyPoints[0].x, state.polyPoints[0].y);
                for (let i = 1; i < state.polyPoints.length; i++) {
                    c.lineTo(state.polyPoints[i].x, state.polyPoints[i].y);
                }
                c.stroke();
            });
        }

        // Always draw big start point so it's visible immediately
        if (state.polyPoints.length > 0) {
            ctxOverlay.fillStyle = state.color;
            ctxOverlay.beginPath();
            ctxOverlay.arc(state.polyPoints[0].x, state.polyPoints[0].y, 8, 0, Math.PI * 2);
            ctxOverlay.fill();
        }
    }

    function handleCurveClick(pos) {
        state.curvePoints.push(pos);

        if (state.curvePoints.length === 3) {
            // Finalize curve: P0=Start, P1=End, P2=Control
            const p0 = state.curvePoints[0];
            const p1 = state.curvePoints[1];
            const p2 = state.curvePoints[2];

            drawSymmetric(ctx, (c) => {
                c.beginPath();
                c.moveTo(p0.x, p0.y);
                c.quadraticCurveTo(p2.x, p2.y, p1.x, p1.y);
                c.stroke();
            });

            state.curvePoints = [];
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
            saveHistory();
        }
    }

    toggleSwatchesBtn.addEventListener('click', () => {
        swatchesContainer.classList.toggle('visible');
        toggleSwatchesBtn.classList.toggle('active');
    });

    gridShowToggle.addEventListener('change', (e) => {
        state.gridShow = e.target.checked;
        updateGridView();
    });

    gridSnapToggle.addEventListener('change', (e) => {
        state.gridSnap = e.target.checked;
    });

    gridSizeInput.addEventListener('input', (e) => {
        state.gridSize = parseInt(e.target.value);
        gridSizeVal.textContent = state.gridSize;
        updateGridView();
    });

    function updateGridView() {
        if (state.gridShow) {
            canvasContainer.classList.add('grid-active');
            canvasContainer.style.setProperty('--grid-size', state.gridSize + 'px');
        } else {
            canvasContainer.classList.remove('grid-active');
        }
    }

    init();
});
