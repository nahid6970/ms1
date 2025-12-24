document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const canvas = document.getElementById('drawing-canvas');
    const ctx = canvas.getContext('2d', {
        willReadFrequently: true,
        alpha: false
    });

    const overlayCanvas = document.getElementById('overlay-canvas');
    const ctxOverlay = overlayCanvas.getContext('2d');

    const guideCanvas = document.getElementById('guide-canvas');
    const ctxGuide = guideCanvas.getContext('2d');

    const viewport = document.getElementById('viewport');
    const canvasContainer = document.querySelector('.canvas-container');

    // Inputs
    const toolsBtns = document.querySelectorAll('.tool-btn');
    const brushSizeInput = document.getElementById('brush-size');
    const sizeValDisplay = document.getElementById('size-val');
    const colorPicker = document.getElementById('color-picker');
    const swatchesContainer = document.getElementById('color-swatches');
    const toggleSwatchesBtn = document.getElementById('toggle-swatches');

    // Grid Settings
    const gridShowToggle = document.getElementById('grid-show');
    const gridSnapToggle = document.getElementById('grid-snap');
    const gridSizeInput = document.getElementById('grid-size');
    const gridSizeVal = document.getElementById('grid-size-val');
    const snapIndicator = document.getElementById('snap-indicator');

    // Actions
    const btnClear = document.getElementById('btn-clear');
    const btnSave = document.getElementById('btn-save');
    const btnGallery = document.getElementById('btn-gallery');

    // Sidebar
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');

    // Symmetry
    const symRadialBtn = document.getElementById('sym-radial');
    const symReflectBtn = document.getElementById('sym-reflect');

    // Modal
    const modal = document.getElementById('gallery-modal');
    const closeModal = modal.querySelector('.close-modal');
    const galleryGrid = document.getElementById('gallery-grid');

    // --- State ---
    const state = {
        isDrawing: false,
        isPanning: false,
        tool: 'brush',
        brushType: 'marker',
        color: '#000000',
        size: 5,
        startX: 0,
        startY: 0,
        lastX: 0,
        lastY: 0,
        history: [],
        historyStep: -1,
        maxHistory: 20,
        scale: 1,
        panX: 0,
        panY: 0,
        lastMouseX: 0,
        lastMouseY: 0,
        lastDrawTime: 0,
        pendingHistorySave: false,
        polyPoints: [],
        curvePoints: [],
        mirrorCount: 4,
        reflectType: 'horizontal',
        symmetry: 'none',
        gridShow: false,
        gridSnap: false,
        gridSize: 40,
        points: []
    };

    // --- Functions ---

    function init() {
        canvas.width = 1500;
        canvas.height = 1500;
        syncOverlay();
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        updateContext();
        saveHistory();
        generateSwatches();
        centerCanvas();
        loadSettings();
    }

    function syncOverlay() {
        overlayCanvas.width = canvas.width;
        overlayCanvas.height = canvas.height;
        guideCanvas.width = canvas.width;
        guideCanvas.height = canvas.height;
        updateContext();
    }

    function generateSwatches() {
        const colors = [
            '#ffffff', '#000000', '#808080', '#c0c0c0',
            '#ff0000', '#ffff00', '#00ff00', '#00ffff', '#0000ff', '#ff00ff',
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

    function saveSettings() {
        const settings = {
            gridShow: state.gridShow,
            gridSnap: state.gridSnap,
            gridSize: state.gridSize,
            size: state.size,
            color: state.color,
            brushType: state.brushType,
            tool: state.tool,
            symmetry: state.symmetry,
            mirrorCount: state.mirrorCount,
            reflectType: state.reflectType
        };
        fetch('/save_settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
    }

    function loadSettings() {
        fetch('/get_settings')
            .then(res => res.json())
            .then(settings => {
                if (!settings || Object.keys(settings).length === 0) return;
                if (settings.gridShow !== undefined) state.gridShow = settings.gridShow;
                if (settings.gridSnap !== undefined) state.gridSnap = settings.gridSnap;
                if (settings.gridSize !== undefined) state.gridSize = settings.gridSize;
                if (settings.size !== undefined) state.size = settings.size;
                if (settings.color !== undefined) {
                    state.color = settings.color;
                    colorPicker.value = settings.color;
                }
                if (settings.brushType !== undefined) state.brushType = settings.brushType;
                if (settings.tool !== undefined) state.tool = settings.tool;
                if (settings.symmetry !== undefined) {
                    state.symmetry = settings.symmetry;
                    state.mirrorCount = settings.mirrorCount || 4;
                    state.reflectType = settings.reflectType || 'horizontal';
                }

                gridShowToggle.checked = state.gridShow;
                gridSnapToggle.checked = state.gridSnap;
                gridSizeInput.value = state.gridSize;
                gridSizeVal.textContent = state.gridSize;
                brushSizeInput.value = state.size;
                sizeValDisplay.textContent = state.size;

                setTool(state.tool);
                setBrushType(state.brushType);
                symRadialBtn.classList.toggle('active', state.symmetry === 'radial');
                symReflectBtn.classList.toggle('active', state.symmetry === 'reflect');
                updateGridView();
                updateContext();
            });
    }

    function updateContext() {
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.lineWidth = state.size;
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1.0;

        const isEraser = state.tool === 'eraser';
        if (!isEraser) {
            if (state.brushType === 'airbrush') {
                ctx.shadowBlur = state.size;
                ctx.shadowColor = state.color;
            } else if (state.brushType === 'pencil') {
                ctx.globalAlpha = 0.5; // Increased from 0.2 for better visibility
                ctx.shadowBlur = 0.5;
                ctx.shadowColor = state.color;
            } else if (state.brushType === 'highlighter') {
                ctx.globalAlpha = 0.4;
            }
        }

        ctx.strokeStyle = isEraser ? '#ffffff' : state.color;
        ctx.fillStyle = isEraser ? '#ffffff' : state.color;

        ctxOverlay.lineCap = 'round';
        ctxOverlay.lineJoin = 'round';
        ctxOverlay.lineWidth = state.size;
        ctxOverlay.strokeStyle = state.color;
        ctxOverlay.fillStyle = state.color;
        ctxOverlay.shadowBlur = isEraser ? 0 : ctx.shadowBlur;
        ctxOverlay.shadowColor = isEraser ? 'transparent' : ctx.shadowColor;
        ctxOverlay.globalAlpha = isEraser ? 1.0 : ctx.globalAlpha;
    }

    function setColor(color) {
        state.color = color;
        colorPicker.value = color;
        if (state.tool === 'eraser') setTool('brush');
        updateContext();
        saveSettings();
    }

    function setTool(toolName) {
        state.tool = toolName;
        toolsBtns.forEach(b => {
            if (b.id.startsWith('tool-')) {
                b.classList.toggle('active', b.id === `tool-${toolName}`);
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
                const input = prompt("Enter number of mirror folders:", state.mirrorCount);
                const val = parseInt(input);
                if (val && val > 0) state.mirrorCount = val;
            } else if (mode === 'reflect') {
                const input = prompt("Mirror Type? (H)orizontal, (V)ertical, or (B)oth:", "H");
                const choice = (input || "").toLowerCase();
                if (choice === 'v' || choice === 'vertical') state.reflectType = 'vertical';
                else if (choice === 'b' || choice === 'both') state.reflectType = 'both';
                else state.reflectType = 'horizontal';
            }
        }
        symRadialBtn.classList.toggle('active', state.symmetry === 'radial');
        symReflectBtn.classList.toggle('active', state.symmetry === 'reflect');
        ctxGuide.clearRect(0, 0, guideCanvas.width, guideCanvas.height);
        drawSymmetryGuides();
        saveSettings();
    }

    function setBrushType(type) {
        state.brushType = type;
        const types = ['marker', 'highlighter', 'pen', 'pencil', 'calligraphy', 'airbrush'];
        types.forEach(t => {
            const btn = document.getElementById(`type-${t}`);
            if (btn) btn.classList.toggle('active', t === type);
        });
        updateContext();
        saveSettings();
    }

    function centerCanvas() {
        const vW = viewport.clientWidth;
        const vH = viewport.clientHeight;
        state.panX = (vW - canvas.width) / 2;
        state.panY = (vH - canvas.height) / 2;
        state.scale = 0.8;
        updateTransform();
    }

    function updateTransform() {
        canvasContainer.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.scale})`;
    }

    function checkBoundsAndExpand(x, y) {
        let newWidth = canvas.width, newHeight = canvas.height;
        let shiftX = 0, shiftY = 0;
        const buffer = 300;

        if (x > canvas.width - buffer) newWidth += 800;
        if (y > canvas.height - buffer) newHeight += 800;
        if (x < buffer) { newWidth += 800; shiftX = 800; }
        if (y < buffer) { newHeight += 800; shiftY = 800; }

        if (newWidth !== canvas.width || newHeight !== canvas.height) {
            resizeCanvas(newWidth, newHeight, shiftX, shiftY);
            return { shiftX, shiftY };
        }
        return { shiftX: 0, shiftY: 0 };
    }

    function resizeCanvas(w, h, shiftX, shiftY) {
        const copy = document.createElement('canvas');
        copy.width = canvas.width; copy.height = canvas.height;
        copy.getContext('2d').drawImage(canvas, 0, 0);

        canvas.width = w; canvas.height = h;
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, w, h);
        ctx.drawImage(copy, shiftX, shiftY);

        syncOverlay();

        if (shiftX !== 0 || shiftY !== 0) {
            state.panX -= shiftX * state.scale;
            state.panY -= shiftY * state.scale;
            updateTransform();
        }
    }

    function saveHistory() {
        if (state.pendingHistorySave) return;
        state.pendingHistorySave = true;
        requestAnimationFrame(() => {
            if (state.historyStep < state.history.length - 1) {
                state.history = state.history.slice(0, state.historyStep + 1);
            }
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
            state.history.push(dataUrl);
            if (state.history.length > state.maxHistory) state.history.shift();
            else state.historyStep++;
            state.pendingHistorySave = false;
        });
    }

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

    function getPos(e) {
        const rect = viewport.getBoundingClientRect();
        let x = (e.clientX - rect.left - state.panX) / state.scale;
        let y = (e.clientY - rect.top - state.panY) / state.scale;
        if (state.gridSnap) {
            x = Math.round(x / state.gridSize) * state.gridSize;
            y = Math.round(y / state.gridSize) * state.gridSize;
        }
        return { x, y };
    }

    function startDrawing(e) {
        let pos = getPos(e);
        const shift = checkBoundsAndExpand(pos.x, pos.y);
        if (shift.shiftX || shift.shiftY) {
            pos.x += shift.shiftX;
            pos.y += shift.shiftY;
        }

        state.isDrawing = true;
        state.startX = pos.x;
        state.startY = pos.y;
        state.lastX = pos.x;
        state.lastY = pos.y;
        state.points = [pos];

        if (state.tool === 'fill') {
            fill(pos.x, pos.y, state.color);
            saveHistory();
            state.isDrawing = false;
        } else if (state.tool === 'picker') {
            pickColor(pos.x, pos.y);
            state.isDrawing = false;
        } else if (state.tool === 'text') {
            addTextPrompt(e);
            state.isDrawing = false;
        } else if (state.tool === 'poly') {
            handlePolyClick(pos);
            state.isDrawing = false;
        } else if (state.tool === 'curve') {
            handleCurveClick(pos);
            state.isDrawing = false;
        } else if (state.tool === 'brush') {
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
        }
    }

    function draw(e) {
        if (!state.isDrawing && state.tool !== 'poly' && state.tool !== 'curve') return;
        const now = performance.now();
        if (now - state.lastDrawTime < 8) return;
        state.lastDrawTime = now;
        const pos = getPos(e);

        if (state.tool === 'poly') {
            if (state.polyPoints.length > 0) {
                ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
                drawSymmetric(ctxOverlay, (c) => {
                    c.beginPath();
                    c.moveTo(state.polyPoints[0].x, state.polyPoints[0].y);
                    state.polyPoints.forEach(p => c.lineTo(p.x, p.y));
                    c.lineTo(pos.x, pos.y);
                    c.stroke();
                });
                ctxOverlay.fillStyle = state.color;
                ctxOverlay.beginPath();
                ctxOverlay.arc(state.polyPoints[0].x, state.polyPoints[0].y, 8, 0, Math.PI * 2);
                ctxOverlay.fill();
            }
        } else if (state.tool === 'curve') {
            if (state.curvePoints.length > 0) {
                ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
                drawSymmetric(ctxOverlay, (c) => {
                    c.beginPath();
                    if (state.curvePoints.length === 1) {
                        c.moveTo(state.curvePoints[0].x, state.curvePoints[0].y);
                        c.lineTo(pos.x, pos.y);
                    } else if (state.curvePoints.length === 2) {
                        c.moveTo(state.curvePoints[0].x, state.curvePoints[0].y);
                        c.quadraticCurveTo(pos.x, pos.y, state.curvePoints[1].x, state.curvePoints[1].y);
                    }
                    c.stroke();
                });
            }
        } else if (state.tool === 'brush') {
            state.points.push(pos);
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
            drawSymmetric(ctxOverlay, (c) => {
                const pts = state.points;
                c.beginPath();
                if (state.brushType === 'marker' || state.brushType === 'highlighter') {
                    if (pts.length > 2) {
                        c.moveTo(pts[0].x, pts[0].y);
                        for (let i = 1; i < pts.length - 2; i++) {
                            const mid = { x: (pts[i].x + pts[i + 1].x) / 2, y: (pts[i].y + pts[i + 1].y) / 2 };
                            c.quadraticCurveTo(pts[i].x, pts[i].y, mid.x, mid.y);
                        }
                        c.quadraticCurveTo(pts[pts.length - 2].x, pts[pts.length - 2].y, pts[pts.length - 1].x, pts[pts.length - 1].y);
                    } else if (pts.length === 2) {
                        c.moveTo(pts[0].x, pts[0].y);
                        c.lineTo(pts[1].x, pts[1].y);
                    }
                } else if (state.brushType === 'pencil') {
                    // Stable sketchy effect: multiple thin lines with fixed offsets
                    const passes = 3;
                    for (let j = 0; j < passes; j++) {
                        c.save();
                        c.beginPath();
                        c.lineWidth = 1; // Pencils are always thin
                        const offset = (j - 1) * 1.5; // Stable offsets ( -1.5, 0, 1.5 )
                        c.moveTo(pts[0].x + offset, pts[0].y + offset);
                        for (let i = 1; i < pts.length; i++) {
                            c.lineTo(pts[i].x + offset, pts[i].y + offset);
                        }
                        c.stroke();
                        c.restore();
                    }
                } else if (state.brushType === 'calligraphy') {
                    const nib = state.size;
                    const ang = -Math.PI / 4;
                    const nx = Math.cos(ang) * nib, ny = Math.sin(ang) * nib;
                    for (let i = 1; i < pts.length; i++) {
                        const p1 = pts[i - 1], p2 = pts[i];
                        c.beginPath();
                        c.moveTo(p1.x - nx, p1.y - ny);
                        c.lineTo(p1.x + nx, p1.y + ny);
                        c.lineTo(p2.x + nx, p2.y + ny);
                        c.lineTo(p2.x - nx, p2.y - ny);
                        c.closePath();
                        c.fill(); c.stroke();
                    }
                } else {
                    c.moveTo(pts[0].x, pts[0].y);
                    pts.forEach(p => c.lineTo(p.x, p.y));
                }
                c.stroke();
            });
        } else if (state.tool === 'eraser') {
            drawSymmetric(ctx, (c) => {
                c.beginPath();
                c.moveTo(state.lastX, state.lastY);
                c.lineTo(pos.x, pos.y);
                c.stroke();
            });
        } else {
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
        state.lastX = pos.x;
        state.lastY = pos.y;
    }

    function stopDrawing() {
        if (!state.isDrawing) return;
        state.isDrawing = false;
        if (['line', 'rect', 'circle', 'brush'].includes(state.tool)) {
            ctx.save();
            ctx.globalAlpha = 1.0;
            ctx.drawImage(overlayCanvas, 0, 0);
            ctx.restore();
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        }
        saveHistory();
    }

    function drawSymmetric(targetCtx, actionFn) {
        if (state.symmetry === 'none') {
            actionFn(targetCtx);
        } else if (state.symmetry === 'radial') {
            const step = (Math.PI * 2) / state.mirrorCount;
            const cx = canvas.width / 2, cy = canvas.height / 2;
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
            actionFn(targetCtx);
            targetCtx.save();
            if (state.reflectType === 'horizontal') { targetCtx.translate(canvas.width, 0); targetCtx.scale(-1, 1); }
            else if (state.reflectType === 'vertical') { targetCtx.translate(0, canvas.height); targetCtx.scale(1, -1); }
            else { targetCtx.translate(canvas.width, canvas.height); targetCtx.scale(-1, -1); }
            actionFn(targetCtx);
            targetCtx.restore();
        }
    }

    function drawSymmetryGuides() {
        if (state.symmetry === 'none') return;
        const cx = canvas.width / 2, cy = canvas.height / 2;
        ctxGuide.save();
        ctxGuide.setTransform(1, 0, 0, 1, 0, 0);
        ctxGuide.strokeStyle = 'rgba(0,0,0,0.1)';
        ctxGuide.setLineDash([15, 15]);
        ctxGuide.lineWidth = 1 / state.scale;
        ctxGuide.beginPath();
        ctxGuide.moveTo(cx, 0); ctxGuide.lineTo(cx, canvas.height);
        ctxGuide.moveTo(0, cy); ctxGuide.lineTo(canvas.width, cy);
        ctxGuide.stroke();
        ctxGuide.fillStyle = 'rgba(0,0,0,0.15)';
        ctxGuide.beginPath();
        ctxGuide.arc(cx, cy, 4 / state.scale, 0, Math.PI * 2);
        ctxGuide.fill();
        ctxGuide.restore();
    }

    function pickColor(x, y) {
        if (x < 0 || y < 0 || x >= canvas.width || y >= canvas.height) return;
        const p = ctx.getImageData(x, y, 1, 1).data;
        const hex = "#" + ("000000" + ((p[0] << 16) | (p[1] << 8) | p[2]).toString(16)).slice(-6);
        setColor(hex);
        setTool('brush');
        showToast(`Color picked: ${hex}`, 'info');
    }

    function fill(x, y, fillColor) {
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        x = Math.floor(x); y = Math.floor(y);
        const startPos = (y * canvas.width + x) * 4;
        const startR = data[startPos], startG = data[startPos + 1], startB = data[startPos + 2], startA = data[startPos + 3];

        const temp = document.createElement('div'); temp.style.color = fillColor; document.body.appendChild(temp);
        const rgb = window.getComputedStyle(temp).color.match(/\d+/g); document.body.removeChild(temp);
        const r = parseInt(rgb[0]), g = parseInt(rgb[1]), b = parseInt(rgb[2]), a = 255;
        if (startR === r && startG === g && startB === b && startA === a) return;

        const stack = [[x, y]];
        while (stack.length) {
            let [cx, cy] = stack.pop();
            let pos = (cy * canvas.width + cx) * 4;
            while (cy >= 0 && data[pos] === startR && data[pos + 1] === startG && data[pos + 2] === startB && data[pos + 3] === startA) { cy--; pos -= canvas.width * 4; }
            cy++; pos += canvas.width * 4;
            let left = false, right = false;
            while (cy < canvas.height && data[pos] === startR && data[pos + 1] === startG && data[pos + 2] === startB && data[pos + 3] === startA) {
                data[pos] = r; data[pos + 1] = g; data[pos + 2] = b; data[pos + 3] = a;
                if (cx > 0) {
                    if (data[pos - 4] === startR && data[pos - 3] === startG && data[pos - 2] === startB && data[pos - 1] === startA) {
                        if (!left) { stack.push([cx - 1, cy]); left = true; }
                    } else left = false;
                }
                if (cx < canvas.width - 1) {
                    if (data[pos + 4] === startR && data[pos + 5] === startG && data[pos + 6] === startB && data[pos + 7] === startA) {
                        if (!right) { stack.push([cx + 1, cy]); right = true; }
                    } else right = false;
                }
                cy++; pos += canvas.width * 4;
            }
        }
        ctx.putImageData(imageData, 0, 0);
    }

    function loadGallery() {
        galleryGrid.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</div>';
        fetch('/gallery').then(res => res.json()).then(images => {
            galleryGrid.innerHTML = '';
            if (images.length === 0) {
                galleryGrid.innerHTML = '<div style="grid-column:1/-1;text-align:center;">No drawings yet.</div>';
                return;
            }
            images.forEach(src => {
                const item = document.createElement('div');
                item.className = 'gallery-item';

                const img = document.createElement('img');
                img.src = src;
                img.onclick = () => loadFromGallery(src);

                const actions = document.createElement('div');
                actions.className = 'gallery-actions';

                const del = document.createElement('div');
                del.className = 'delete-btn';
                del.innerHTML = '<i class="fa-solid fa-trash"></i>';
                del.onclick = (e) => { e.stopPropagation(); deleteArtwork(src, item); };

                actions.append(del);
                item.append(img, actions);
                galleryGrid.append(item);
            });
        });
    }

    function deleteArtwork(src, item) {
        if (!confirm('Delete?')) return;
        fetch('/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename: src.split('/').pop() }) })
            .then(res => res.json()).then(data => { if (data.success) item.remove(); });
    }

    function loadFromGallery(src) {
        const img = new Image(); img.src = src; img.crossOrigin = "Anonymous";
        img.onload = () => {
            canvas.width = img.width; canvas.height = img.height;
            syncOverlay();
            centerCanvas();
            ctx.drawImage(img, 0, 0);
            saveHistory();
            modal.classList.remove('open');
        };
    }

    function showToast(msg, type = 'success') {
        const t = document.createElement('div'); t.className = `toast ${type}`;
        t.innerText = msg;
        document.getElementById('toast-container').appendChild(t);
        setTimeout(() => t.remove(), 3000);
    }

    function addTextPrompt(e) {
        const pos = getPos(e);
        const input = document.createElement('input');
        input.type = 'text';
        input.style.position = 'fixed';
        input.style.left = e.clientX + 'px';
        input.style.top = e.clientY + 'px';
        input.style.background = 'transparent';
        input.style.border = '1px dashed ' + state.color;
        input.style.color = state.color;
        const fontSize = Math.max(14, state.size * 2);
        input.style.font = `bold ${fontSize}px 'Outfit', sans-serif`;
        input.style.zIndex = 1000;
        input.style.outline = 'none';
        input.style.padding = '0';
        input.style.margin = '0';

        document.body.appendChild(input);
        setTimeout(() => input.focus(), 10);

        let done = false;
        const cleanup = () => {
            if (done) return;
            done = true;
            if (input.value) {
                ctx.font = `bold ${fontSize}px 'Outfit', sans-serif`;
                ctx.fillStyle = state.color;
                ctx.textBaseline = 'top';
                ctx.fillText(input.value, pos.x, pos.y);
                saveHistory();
            }
            input.remove();
        };
        input.onblur = cleanup;
        input.onkeydown = (ev) => { if (ev.key === 'Enter') cleanup(); };
    }

    function handlePolyClick(pos) {
        if (state.polyPoints.length > 2) {
            const start = state.polyPoints[0];
            if (Math.hypot(pos.x - start.x, pos.y - start.y) < 20) {
                drawSymmetric(ctx, (c) => {
                    c.beginPath(); c.moveTo(start.x, start.y);
                    state.polyPoints.forEach(p => c.lineTo(p.x, p.y));
                    c.closePath(); c.stroke();
                });
                state.polyPoints = [];
                ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
                saveHistory(); return;
            }
        }
        state.polyPoints.push(pos);
    }

    function handleCurveClick(pos) {
        state.curvePoints.push(pos);
        if (state.curvePoints.length === 3) {
            drawSymmetric(ctx, (c) => {
                c.beginPath(); c.moveTo(state.curvePoints[0].x, state.curvePoints[0].y);
                c.quadraticCurveTo(state.curvePoints[2].x, state.curvePoints[2].y, state.curvePoints[1].x, state.curvePoints[1].y);
                c.stroke();
            });
            state.curvePoints = [];
            ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
            saveHistory();
        }
    }

    function updateGridView() {
        if (state.gridShow) {
            canvasContainer.classList.add('grid-active');
            canvasContainer.style.setProperty('--grid-size', state.gridSize + 'px');
        } else {
            canvasContainer.classList.remove('grid-active');
        }
    }

    // --- Listeners ---

    toggleBtn.onclick = () => {
        sidebar.classList.toggle('collapsed');
        toggleBtn.innerHTML = sidebar.classList.contains('collapsed') ? '<i class="fa-solid fa-chevron-right"></i>' : '<i class="fa-solid fa-bars"></i>';
    };

    toolsBtns.forEach(btn => {
        btn.onclick = () => {
            if (btn.id.startsWith('tool-')) {
                setTool(btn.id.replace('tool-', ''));
                saveSettings();
            } else if (btn.id.startsWith('type-')) {
                setBrushType(btn.id.replace('type-', ''));
            }
        };
    });

    brushSizeInput.oninput = (e) => { state.size = e.target.value; sizeValDisplay.textContent = state.size; updateContext(); };
    brushSizeInput.onchange = () => saveSettings();

    colorPicker.oninput = (e) => setColor(e.target.value);

    toggleSwatchesBtn.onclick = () => {
        swatchesContainer.classList.toggle('visible');
        toggleSwatchesBtn.classList.toggle('active');
    };

    btnClear.onclick = () => {
        // Reset context state to ensure full opaque white clear
        ctx.save();
        ctx.globalAlpha = 1.0;
        ctx.shadowBlur = 0;
        ctx.globalCompositeOperation = 'source-over';
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.restore();

        ctxOverlay.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
        ctxGuide.clearRect(0, 0, guideCanvas.width, guideCanvas.height);

        state.polyPoints = [];
        state.curvePoints = [];

        updateContext();
        saveHistory();
        showToast('Canvas cleared!');
    };
    btnSave.onclick = () => {
        btnSave.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        fetch('/save', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ image: canvas.toDataURL() }) })
            .then(() => showToast('Saved!')).finally(() => btnSave.innerHTML = '<i class="fa-solid fa-floppy-disk"></i>');
    };
    btnGallery.onclick = () => { modal.classList.add('open'); loadGallery(); };
    closeModal.onclick = () => modal.classList.remove('open');

    gridShowToggle.onchange = (e) => { state.gridShow = e.target.checked; updateGridView(); saveSettings(); };
    gridSnapToggle.onchange = (e) => { state.gridSnap = e.target.checked; saveSettings(); };
    gridSizeInput.oninput = (e) => { state.gridSize = parseInt(e.target.value); gridSizeVal.textContent = state.gridSize; updateGridView(); };
    gridSizeInput.onchange = () => saveSettings();

    symRadialBtn.onclick = () => setSymmetry('radial');
    symReflectBtn.onclick = () => setSymmetry('reflect');

    viewport.onwheel = (e) => {
        e.preventDefault();
        const rect = viewport.getBoundingClientRect();
        const mouseX = e.clientX - rect.left, mouseY = e.clientY - rect.top;
        const worldX = (mouseX - state.panX) / state.scale, worldY = (mouseY - state.panY) / state.scale;
        const zoom = e.deltaY < 0 ? 1.1 : 0.9;
        state.scale *= zoom;
        state.panX = mouseX - worldX * state.scale;
        state.panY = mouseY - worldY * state.scale;
        updateTransform();
    };

    viewport.onmousedown = (e) => {
        if (e.button === 1 || (e.button === 0 && e.ctrlKey)) {
            state.isPanning = true;
            state.lastMouseX = e.clientX; state.lastMouseY = e.clientY;
            viewport.style.cursor = 'grabbing';
        } else if (e.button === 0) startDrawing(e);
    };

    window.onmousemove = (e) => {
        if (state.isPanning) {
            state.panX += e.clientX - state.lastMouseX;
            state.panY += e.clientY - state.lastMouseY;
            state.lastMouseX = e.clientX; state.lastMouseY = e.clientY;
            updateTransform();
        } else {
            draw(e);
            ctxGuide.clearRect(0, 0, guideCanvas.width, guideCanvas.height);
            drawSymmetryGuides();
            if (state.gridSnap) {
                const pos = getPos(e);
                snapIndicator.style.display = 'block';
                snapIndicator.style.left = pos.x + 'px'; snapIndicator.style.top = pos.y + 'px';
            } else snapIndicator.style.display = 'none';
        }
    };

    window.onmouseup = () => { state.isPanning = false; viewport.style.cursor = 'crosshair'; stopDrawing(); };

    window.onkeydown = (e) => {
        if (e.target.tagName === 'INPUT') return;
        if (e.ctrlKey && e.key === 'z') { e.preventDefault(); undo(); }
        const keys = { 'b': 'brush', 'e': 'eraser', 'f': 'fill', 'i': 'picker', 't': 'text', 'p': 'poly', 'c': 'curve' };
        if (keys[e.key.toLowerCase()]) setTool(keys[e.key.toLowerCase()]);
        if (e.key.toLowerCase() === 'm') setSymmetry('radial');
        if (e.key.toLowerCase() === 'v') setSymmetry('reflect');
    };

    init();
});
