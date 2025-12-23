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

    // Actions
    const btnClear = document.getElementById('btn-clear');
    const btnSave = document.getElementById('btn-save');
    const btnGallery = document.getElementById('btn-gallery');

    // Grid Settings
    const gridShowToggle = document.getElementById('grid-show');
    const gridSnapToggle = document.getElementById('grid-snap');
    const gridSizeInput = document.getElementById('grid-size');
    const gridSizeVal = document.getElementById('grid-size-val');

    // Canvas Container for Transforms
    const canvasContainer = document.querySelector('.canvas-container');

    // Modal
    const modal = document.getElementById('gallery-modal');
    const closeModal = modal.querySelector('.close-modal');
    const galleryGrid = document.getElementById('gallery-grid');

    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');

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
        color: '#00d2ff',
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

        // Curve State
        curvePoints: [],

        // Grid State
        gridShow: false,
        gridSnap: false,
        gridSize: 40
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
        ctx.strokeStyle = state.tool === 'eraser' ? '#ffffff' : state.color;
        ctx.fillStyle = state.tool === 'eraser' ? '#ffffff' : state.color;

        // Overlay (always same props, except eraser acts effectively as white brush for preview if needed, 
        // but typically overlay is for shapes. For eraser trace we might want outline?)
        ctxOverlay.lineCap = 'round';
        ctxOverlay.lineJoin = 'round';
        ctxOverlay.lineWidth = state.size;
        ctxOverlay.strokeStyle = state.color; // Eraser doesn't use overlay usually
        ctxOverlay.fillStyle = state.color;

        // Update cursor only when needed
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
        if (toolName === 'mirror') {
            const input = prompt("Enter number of mirror folders (e.g. 4, 6, 8, 12):", "4");
            const val = parseInt(input);
            if (val && val > 0) {
                state.mirrorCount = val;
            } else {
                if (!state.mirrorCount) state.mirrorCount = 4;
            }
        }

        if (toolName === 'reflect') {
            const input = prompt("Mirror Type? (H)orizontal, (V)ertical, or (B)oth/Opposite:", "H");
            const choice = (input || "").toLowerCase();
            if (choice === 'v' || choice === 'vertical') state.reflectType = 'vertical';
            else if (choice === 'b' || choice === 'both') state.reflectType = 'both';
            else state.reflectType = 'horizontal';
        }

        toolsBtns.forEach(b => {
            if (b.id === `tool-${toolName}`) b.classList.add('active');
            else b.classList.remove('active');
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

        if (state.tool === 'brush' || state.tool === 'eraser') {
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
            // Draw single dot for immediate feedback
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
        } else {
            // Shapes: Clear overlay
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
            ctxOverlay.beginPath();
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
            // Draw preview line from last point to current mouse
            if (state.polyPoints.length > 0) {
                ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

                // Redraw existing lines
                ctxOverlay.beginPath();
                ctxOverlay.moveTo(state.polyPoints[0].x, state.polyPoints[0].y);
                for (let i = 1; i < state.polyPoints.length; i++) {
                    ctxOverlay.lineTo(state.polyPoints[i].x, state.polyPoints[i].y);
                }

                // Draw preview line
                const last = state.polyPoints[state.polyPoints.length - 1];
                ctxOverlay.lineTo(pos.x, pos.y);
                ctxOverlay.stroke();

                // Highlight start point
                const start = state.polyPoints[0];

                // 1. Always show start point (Big)
                ctxOverlay.fillStyle = state.color;
                ctxOverlay.beginPath();
                ctxOverlay.arc(start.x, start.y, 8, 0, Math.PI * 2);
                ctxOverlay.fill();

                // 2. Show big closer indicator if nearby
                const dist = Math.sqrt(Math.pow(pos.x - start.x, 2) + Math.pow(pos.y - start.y, 2));
                if (dist < 20) {
                    ctxOverlay.fillStyle = 'rgba(0, 255, 0, 0.3)';
                    ctxOverlay.beginPath();
                    ctxOverlay.arc(start.x, start.y, 20, 0, Math.PI * 2);
                    ctxOverlay.fill();
                    ctxOverlay.fillStyle = state.color; // reset
                }
            }
            return;
        }

        if (state.tool === 'curve') {
            if (state.curvePoints.length > 0) {
                ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
                ctxOverlay.beginPath();
                const p0 = state.curvePoints[0];

                if (state.curvePoints.length === 1) {
                    // Preview line towards end point
                    ctxOverlay.moveTo(p0.x, p0.y);
                    ctxOverlay.lineTo(pos.x, pos.y);
                } else if (state.curvePoints.length === 2) {
                    // Preview quadratic curve using mouse as control point
                    const p1 = state.curvePoints[1];
                    ctxOverlay.moveTo(p0.x, p0.y);
                    ctxOverlay.quadraticCurveTo(pos.x, pos.y, p1.x, p1.y);
                }
                ctxOverlay.stroke();

                // Draw helper dots
                ctxOverlay.fillStyle = state.color;
                state.curvePoints.forEach(p => {
                    ctxOverlay.beginPath();
                    ctxOverlay.arc(p.x, p.y, 4, 0, Math.PI * 2);
                    ctxOverlay.fill();
                });
            }
            return;
        }

        if (state.tool === 'brush' || state.tool === 'eraser') {
            // Simple line drawing - keep it working!
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
        } else if (state.tool === 'reflect') {
            const w = canvas.width;
            const h = canvas.height;

            // Draw original
            ctx.beginPath();
            ctx.moveTo(state.startX, state.startY);
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();

            // Draw reflected
            ctx.beginPath();
            let mStartX, mStartY, mPosX, mPosY;

            if (state.reflectType === 'horizontal') {
                mStartX = w - state.startX;
                mStartY = state.startY;
                mPosX = w - pos.x;
                mPosY = pos.y;
            } else if (state.reflectType === 'vertical') {
                mStartX = state.startX;
                mStartY = h - state.startY;
                mPosX = pos.x;
                mPosY = h - pos.y;
            } else { // both / opposite
                mStartX = w - state.startX;
                mStartY = h - state.startY;
                mPosX = w - pos.x;
                mPosY = h - pos.y;
            }

            ctx.moveTo(mStartX, mStartY);
            ctx.lineTo(mPosX, mPosY);
            ctx.stroke();

            // Update last pos
            state.startX = pos.x;
            state.startY = pos.y;
        } else if (state.tool === 'mirror') {
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            const angleStep = (Math.PI * 2) / state.mirrorCount;

            ctx.save();
            for (let i = 0; i < state.mirrorCount; i++) {
                ctx.setTransform(1, 0, 0, 1, 0, 0); // Reset transform
                ctx.translate(cx, cy);
                ctx.rotate(angleStep * i);
                ctx.translate(-cx, -cy);

                ctx.beginPath();
                ctx.moveTo(state.startX, state.startY);
                ctx.lineTo(pos.x, pos.y);
                ctx.stroke();
            }
            ctx.restore();

            // Update last pos
            state.startX = pos.x;
            state.startY = pos.y;
        } else {
            // Shapes: Draw to Overlay
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

            if (state.tool === 'line') {
                ctxOverlay.beginPath();
                ctxOverlay.moveTo(state.startX, state.startY);
                ctxOverlay.lineTo(pos.x, pos.y);
                ctxOverlay.stroke();
            } else if (state.tool === 'rect') {
                ctxOverlay.beginPath();
                let w = pos.x - state.startX;
                let h = pos.y - state.startY;
                ctxOverlay.strokeRect(state.startX, state.startY, w, h);
            } else if (state.tool === 'circle') {
                ctxOverlay.beginPath();
                let r = Math.sqrt(Math.pow(pos.x - state.startX, 2) + Math.pow(pos.y - state.startY, 2));
                ctxOverlay.arc(state.startX, state.startY, r, 0, 2 * Math.PI);
                ctxOverlay.stroke();
            }
        }
    }

    function stopDrawing() {
        if (!state.isDrawing) return;
        state.isDrawing = false;

        if (['line', 'rect', 'circle'].includes(state.tool)) {
            // Commit overlay to main
            ctx.drawImage(overlayCanvas, 0, 0);
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
            const t = btn.id.replace('tool-', '');
            setTool(t);
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
        btnSave.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

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
                btnSave.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save';
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
            case 'm': setTool('mirror'); break;
            case 'v': setTool('reflect'); break;
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
                ctx.beginPath();
                ctx.moveTo(state.polyPoints[0].x, state.polyPoints[0].y);
                for (let i = 1; i < state.polyPoints.length; i++) {
                    ctx.lineTo(state.polyPoints[i].x, state.polyPoints[i].y);
                }
                ctx.closePath();
                ctx.stroke();

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
        ctxOverlay.beginPath();
        if (state.polyPoints.length > 0) {
            ctxOverlay.moveTo(state.polyPoints[0].x, state.polyPoints[0].y);
            for (let i = 1; i < state.polyPoints.length; i++) {
                ctxOverlay.lineTo(state.polyPoints[i].x, state.polyPoints[i].y);
            }
            ctxOverlay.stroke();
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

            ctx.beginPath();
            ctx.moveTo(p0.x, p0.y);
            ctx.quadraticCurveTo(p2.x, p2.y, p1.x, p1.y);
            ctx.stroke();

            state.curvePoints = [];
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
            saveHistory();
        }
    }

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
