document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const canvas = document.getElementById('drawing-canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });

    // Overlay Canvas for performance (shapes/preview)
    const overlayCanvas = document.getElementById('overlay-canvas');
    const ctxOverlay = overlayCanvas.getContext('2d');

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

    // Canvas Container for Transforms
    const canvasContainer = document.querySelector('.canvas-container');

    // Modal
    const modal = document.getElementById('gallery-modal');
    const closeModal = modal.querySelector('.close-modal');
    const galleryGrid = document.getElementById('gallery-grid');

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
        lastMouseY: 0
    };

    // Initialize
    function init() {
        // Start with a reasonably large size, but not huge to prevent memory issues initially
        // We will expand it dynamically.
        canvas.width = 3000;
        canvas.height = 3000;

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

        if (state.isPanning) {
            viewport.style.cursor = 'grabbing';
        } else {
            viewport.style.cursor = 'crosshair';
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
            if (b.id === `tool-${toolName}`) b.classList.add('active');
            else b.classList.remove('active');
        });
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

    // --- Dynamic Expansion ---
    function checkBoundsAndExpand(x, y) {
        // If x,y is close to edge or outside, expand canvas.
        // We will expand by chunks, e.g., 1000px.
        // This is a heavy operation, so we do it cautiously.
        // Ideally we do this BEFORE drawing starts, or AFTER.
        // Doing it during drag is tricky. We'll do it on mousedown if needed?
        // Or if user pans too far?

        let newWidth = canvas.width;
        let newHeight = canvas.height;
        let shiftX = 0;
        let shiftY = 0;
        const buffer = 500; // pixels buffer
        let expandInfo = "";

        // Check Right/Bottom
        if (x > canvas.width - buffer) {
            newWidth += 1000;
            expandInfo = "right";
        }
        if (y > canvas.height - buffer) {
            newHeight += 1000;
            expandInfo = "down";
        }
        // Check Left/Top (Harder because requires shifting context)
        // For simplicity in this version, we will only expand Right and Bottom.
        // To expand Left/Top we need to 'shift' the image data and state.panX/Y.

        if (x < buffer && x < 0) { // Only expand left if actually outside or very close to left edge
            // Expand Left
            const add = 1000;
            newWidth += add;
            shiftX = add;
            expandInfo = "left";
        }
        if (y < buffer && y < 0) { // Only expand top if actually outside or very close to top edge
            // Expand Top
            const add = 1000;
            newHeight += add;
            shiftY = add;
            expandInfo = "up";
        }

        if (newWidth !== canvas.width || newHeight !== canvas.height) {
            resizeCanvas(newWidth, newHeight, shiftX, shiftY);
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

    // --- History System ---
    function saveHistory() {
        if (state.historyStep < state.history.length - 1) {
            state.history = state.history.slice(0, state.historyStep + 1);
        }

        state.history.push(canvas.toDataURL());
        if (state.history.length > state.maxHistory) {
            state.history.shift();
        } else {
            state.historyStep++;
        }
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

        return {
            x: (viewportMouseX - state.panX) / state.scale,
            y: (viewportMouseY - state.panY) / state.scale
        };
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

        if (state.isDrawing) {
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

        // OPTIONAL: Check bounds on start and expand if user clicks in the void (conceptually)
        // But since we can't click outside canvas div, we rely on canvas being large.
        // However, if we implement "infinite", we should check if they are near edge.
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

        if (state.tool === 'brush' || state.tool === 'eraser') {
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
            // Draw single dot
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
        } else {
            // Shapes: Clear overlay
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
            ctxOverlay.beginPath();
        }
    }

    function draw(e) {
        if (!state.isDrawing) return;
        const pos = getPos(e);
        // Note: if we expanded canvas in mousedown, our coordinate system is fine directly via getPos
        // because getPos uses the current state.pan/scale which were updated in resizeCanvas.

        if (state.tool === 'brush' || state.tool === 'eraser') {
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            // Check dynamic expand during draw (throttled?)
            // Doing this every frame is expensive (resizeCanvas copies data).
            // A better infinite canvas implements tiled rendering.
            // For now, let's just let them draw. If they hit edge, it clips.
            // We expanded on mousedown, that helps.
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

        if (state.tool !== 'picker' && state.tool !== 'fill') {
            saveHistory();
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
                    item.appendChild(img);

                    item.addEventListener('click', () => {
                        loadFromGallery(src);
                    });

                    galleryGrid.appendChild(item);
                });
            });
    }

    function loadFromGallery(src) {
        if (!confirm("Load this image? Current artwork will be overwritten.")) return;

        const img = new Image();
        img.src = src;
        img.crossOrigin = "Anonymous";
        img.onload = () => {
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
            saveHistory();
            modal.classList.remove('open');
            showToast('Artwork loaded!');
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
        }
    });

    init();
});
