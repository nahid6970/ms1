document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const svg = document.getElementById('main-svg');
    const drawingLayer = document.getElementById('drawing-layer');
    const overlayLayer = document.getElementById('overlay-layer');
    const guideLayer = document.getElementById('guide-layer');
    const bgRect = document.getElementById('svg-bg');

    const viewport = document.getElementById('viewport');
    const canvasContainer = document.getElementById('canvas-container');

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
    const transparentBgToggle = document.getElementById('check-transparent-bg');
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

    const btnStampsPopover = document.getElementById('btn-stamps-popover');
    const stampsPopover = document.getElementById('stamps-popover');
    const btnAddStamp = document.getElementById('btn-add-stamp');
    const contextMenu = document.getElementById('context-menu');
    const cmDelete = document.getElementById('cm-delete');
    const cmExportPng = document.getElementById('cm-export-png');

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
        maxHistory: 30,
        scale: 1,
        panX: 0,
        panY: 0,
        lastMouseX: 0,
        lastMouseY: 0,
        mirrorCount: 4,
        reflectType: 'horizontal',
        symmetry: 'none',
        symmetry: 'none',
        gridShow: false,
        gridSnap: false,
        gridSize: 40,
        transparentBg: false,
        points: [],
        multiLineCount: 3,
        stamps: [],
        selectedStamp: 'fa-star',
        unicodeCache: {},
        activeElement: null,
        polyPoints: [],
        curvePoints: []
    };

    const NS = "http://www.w3.org/2000/svg";

    // --- Functions ---

    function init() {
        centerCanvas();
        generateSwatches();
        loadSettings();
        loadIcons();
        saveHistory(); // Initial state
        drawSymmetryGuides();
        overlayLayer.style.pointerEvents = 'none';
        guideLayer.style.pointerEvents = 'none';
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
            el.onclick = () => setColor(c);
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
            reflectType: state.reflectType,
            multiLineCount: state.multiLineCount,
            transparentBg: state.transparentBg
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
            .then(s => {
                if (!s || Object.keys(s).length === 0) return;
                state.gridShow = s.gridShow ?? state.gridShow;
                state.gridSnap = s.gridSnap ?? state.gridSnap;
                state.gridSize = s.gridSize ?? state.gridSize;
                state.size = s.size ?? state.size;
                if (s.color) { state.color = s.color; colorPicker.value = s.color; }
                state.brushType = s.brushType ?? state.brushType;
                state.tool = s.tool ?? state.tool;
                state.symmetry = s.symmetry ?? state.symmetry;
                state.mirrorCount = s.mirrorCount ?? 4;
                state.reflectType = s.reflectType ?? 'horizontal';
                state.multiLineCount = s.multiLineCount ?? 3;
                state.transparentBg = s.transparentBg ?? false;

                gridShowToggle.checked = state.gridShow;
                gridSnapToggle.checked = state.gridSnap;
                transparentBgToggle.checked = state.transparentBg;
                updateBgTransparency();
                gridSizeInput.value = state.gridSize;
                gridSizeVal.textContent = state.gridSize;
                brushSizeInput.value = state.size;
                sizeValDisplay.textContent = state.size;

                setTool(state.tool);
                setBrushType(state.brushType);
                symRadialBtn.classList.toggle('active', state.symmetry === 'radial');
                symReflectBtn.classList.toggle('active', state.symmetry === 'reflect');
                updateGridView();
                drawSymmetryGuides();
            });
    }

    function loadIcons() {
        fetch('/get_icons').then(res => res.json()).then(icons => {
            state.stamps = icons;
            renderStamps();
        });
    }

    function saveIcons() {
        fetch('/save_icons', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state.stamps)
        });
    }

    function renderStamps() {
        const grid = document.getElementById('stamps-grid');
        grid.innerHTML = '';
        state.stamps.forEach(cl => {
            const b = document.createElement('button');
            b.className = 'tool-btn stamp-btn';
            if (state.tool === 'stamp' && state.selectedStamp === cl) b.classList.add('active');
            b.innerHTML = `<i class="fa-solid ${cl}"></i>`;
            b.onclick = () => {
                state.selectedStamp = cl;
                setTool('stamp');
                renderStamps();
                stampsPopover.classList.remove('visible');
            };
            b.oncontextmenu = (e) => {
                e.preventDefault();
                showContextMenu(e, 'stamp', cl);
            };
            grid.appendChild(b);
        });
    }

    let currentContextType = null; // 'stamp' or 'artwork'
    let currentContextData = null; // cl or src

    function showContextMenu(e, type, data) {
        currentContextType = type;
        currentContextData = data;

        // Only show Export option for artworks
        if (cmExportPng) cmExportPng.style.display = type === 'artwork' ? 'flex' : 'none';

        contextMenu.style.display = 'block';
        contextMenu.style.left = `${e.clientX}px`;
        contextMenu.style.top = `${e.clientY}px`;
    }

    function deleteStamp(cl) {
        if (!confirm(`Delete stamp ${cl}?`)) return;
        state.stamps = state.stamps.filter(s => s !== cl);
        if (state.selectedStamp === cl) state.selectedStamp = state.stamps[0] || '';
        saveIcons();
        renderStamps();
    }

    function setColor(c) {
        state.color = c;
        colorPicker.value = c;
        if (state.tool === 'eraser') setTool('brush');
        saveSettings();
    }

    function setTool(t) {
        if (state.activeElement) commitShape();
        state.tool = t;
        toolsBtns.forEach(b => {
            if (b.id && b.id.startsWith('tool-')) {
                b.classList.toggle('active', b.id === `tool-${t}`);
            }
        });
        btnStampsPopover.classList.toggle('active', t === 'stamp');
        overlayLayer.innerHTML = '';
        guideLayer.querySelectorAll('.poly-closer').forEach(e => e.remove());
        state.polyPoints = []; state.curvePoints = []; state.activeElement = null;
        saveSettings();
    }

    function setSymmetry(m) {
        if (state.symmetry === m) state.symmetry = 'none';
        else {
            state.symmetry = m;
            if (m === 'radial') {
                const i = prompt("Mirrors:", state.mirrorCount);
                if (parseInt(i)) state.mirrorCount = parseInt(i);
            } else if (m === 'reflect') {
                const i = prompt("(H)orizontal, (V)ertical, (B)oth:", "H");
                const c = (i || "").toLowerCase();
                if (c === 'v') state.reflectType = 'vertical';
                else if (c === 'b') state.reflectType = 'both';
                else state.reflectType = 'horizontal';
            }
        }
        symRadialBtn.classList.toggle('active', state.symmetry === 'radial');
        symReflectBtn.classList.toggle('active', state.symmetry === 'reflect');
        drawSymmetryGuides();
        saveSettings();
    }

    function setBrushType(t) {
        state.brushType = t;
        if (t === 'multiLine') {
            const i = prompt("Line count (2-10):", state.multiLineCount);
            if (parseInt(i)) state.multiLineCount = Math.min(10, Math.max(2, parseInt(i)));
        }
        ['marker', 'highlighter', 'pen', 'multiLine', 'calligraphy', 'airbrush'].forEach(type => {
            const b = document.getElementById(`type-${type}`);
            if (b) b.classList.toggle('active', type === t);
        });
        saveSettings();
    }

    function centerCanvas() {
        const vW = viewport.clientWidth, vH = viewport.clientHeight;
        const sW = 1920, sH = 1080;
        const sX = (vW - 80) / sW, sY = (vH - 80) / sH;
        state.scale = Math.min(sX, sY, 1);
        state.panX = (vW - sW * state.scale) / 2;
        state.panY = (vH - sH * state.scale) / 2;
        updateTransform();
    }

    function updateTransform() {
        canvasContainer.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.scale})`;
    }

    function saveHistory() {
        if (state.historyStep < state.history.length - 1) {
            state.history = state.history.slice(0, state.historyStep + 1);
        }
        state.history.push({
            drawing: drawingLayer.innerHTML,
            bg: bgRect.getAttribute('fill')
        });
        if (state.history.length > state.maxHistory) state.history.shift();
        else state.historyStep++;
    }

    function undo() {
        if (state.historyStep > 0) {
            state.historyStep--;
            const e = state.history[state.historyStep];
            drawingLayer.innerHTML = e.drawing;
            bgRect.setAttribute('fill', e.bg);
        }
    }

    function getPos(e) {
        const r = viewport.getBoundingClientRect();
        let x = (e.clientX - r.left - state.panX) / state.scale;
        let y = (e.clientY - r.top - state.panY) / state.scale;
        if (state.gridSnap) {
            x = Math.round(x / state.gridSize) * state.gridSize;
            y = Math.round(y / state.gridSize) * state.gridSize;
        }
        return { x, y };
    }

    function startDrawing(e) {
        if (state.tool === 'picker') {
            pickColor(e); return;
        }
        if (state.tool === 'fill') {
            const pos = getPos(e);
            const clickedEl = e.target.closest('#drawing-layer > *');
            
            // If clicked on an existing shape/path, change its fill color
            if (clickedEl && clickedEl !== bgRect) {
                const tagName = clickedEl.tagName.toLowerCase();
                
                // For paths, rects, circles, ellipses - set fill
                if (['path', 'rect', 'circle', 'ellipse', 'polygon'].includes(tagName)) {
                    clickedEl.setAttribute('fill', state.color);
                    saveHistory();
                    return;
                }
                
                // For lines - convert to path with stroke
                if (tagName === 'line') {
                    clickedEl.setAttribute('stroke', state.color);
                    saveHistory();
                    return;
                }
                
                // For groups containing images (previous fills) - replace
                if (tagName === 'g' || tagName === 'image') {
                    const parent = clickedEl.tagName === 'image' ? clickedEl.parentElement : clickedEl;
                    if (parent && parent.tagName === 'g') {
                        parent.remove();
                        // Continue to do a new fill at this location
                    }
                }
            }
            
            // Pixel-based flood fill for empty areas
            document.body.style.cursor = 'wait';
            const w = 1920, h = 1080;
            const finalX = Math.round(pos.x);
            const finalY = Math.round(pos.y);

            if (finalX < 0 || finalY < 0 || finalX >= w || finalY >= h) {
                document.body.style.cursor = 'crosshair';
                return;
            }

            // Rasterize SVG at higher resolution for better edge detection
            const scale = 2; // 2x resolution
            const sw = w * scale, sh = h * scale;
            const svgClone = svg.cloneNode(true);
            svgClone.setAttribute('width', sw);
            svgClone.setAttribute('height', sh);
            svgClone.setAttribute('viewBox', `0 0 ${w} ${h}`);
            
            const svgData = new XMLSerializer().serializeToString(svgClone);
            const img = new Image();
            const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
            const url = URL.createObjectURL(blob);

            img.onload = () => {
                const cvs = document.createElement('canvas');
                cvs.width = sw; cvs.height = sh;
                const ctx = cvs.getContext('2d', { willReadFrequently: true });
                ctx.drawImage(img, 0, 0, sw, sh);
                URL.revokeObjectURL(url);

                const pixels = ctx.getImageData(0, 0, sw, sh);
                const d = pixels.data;
                
                // Scale click position
                const sx = finalX * scale, sy = finalY * scale;
                const targetIdx = (sy * sw + sx) * 4;
                const tr = d[targetIdx], tg = d[targetIdx + 1], tb = d[targetIdx + 2], ta = d[targetIdx + 3];

                // Parse fill color
                const fillCvs = document.createElement('canvas');
                fillCvs.width = 1; fillCvs.height = 1;
                const fCtx = fillCvs.getContext('2d');
                fCtx.fillStyle = state.color;
                fCtx.fillRect(0, 0, 1, 1);
                const fData = fCtx.getImageData(0, 0, 1, 1).data;
                const fr = fData[0], fg = fData[1], fb = fData[2], fa = 255;

                // Flood fill at higher resolution
                const stack = [sx, sy];
                const seen = new Uint8Array(sw * sh);
                const resultData = new Uint8ClampedArray(sw * sh * 4);

                // Match function with good tolerance
                const tolerance = 40;
                function match(i) {
                    return Math.abs(d[i] - tr) < tolerance && 
                           Math.abs(d[i + 1] - tg) < tolerance && 
                           Math.abs(d[i + 2] - tb) < tolerance;
                }

                while (stack.length > 0) {
                    const y = stack.pop();
                    const x = stack.pop();
                    const idx = y * sw + x;

                    if (x < 0 || x >= sw || y < 0 || y >= sh || seen[idx]) continue;

                    let wx = x;
                    while (wx >= 0 && !seen[y * sw + wx] && match((y * sw + wx) * 4)) {
                        const widx = y * sw + wx;
                        seen[widx] = 1;
                        resultData[widx * 4] = fr;
                        resultData[widx * 4 + 1] = fg;
                        resultData[widx * 4 + 2] = fb;
                        resultData[widx * 4 + 3] = fa;

                        if (y > 0 && !seen[widx - sw] && match((widx - sw) * 4)) stack.push(wx, y - 1);
                        if (y < sh - 1 && !seen[widx + sw] && match((widx + sw) * 4)) stack.push(wx, y + 1);
                        wx--;
                    }

                    let ex = x + 1;
                    while (ex < sw && !seen[y * sw + ex] && match((y * sw + ex) * 4)) {
                        const eidx = y * sw + ex;
                        seen[eidx] = 1;
                        resultData[eidx * 4] = fr;
                        resultData[eidx * 4 + 1] = fg;
                        resultData[eidx * 4 + 2] = fb;
                        resultData[eidx * 4 + 3] = fa;

                        if (y > 0 && !seen[eidx - sw] && match((eidx - sw) * 4)) stack.push(ex, y - 1);
                        if (y < sh - 1 && !seen[eidx + sw] && match((eidx + sw) * 4)) stack.push(ex, y + 1);
                        ex++;
                    }
                }

                // Expand fill to cover anti-aliased edges (2 passes at high res)
                for (let pass = 0; pass < 3; pass++) {
                    for (let y = 1; y < sh - 1; y++) {
                        for (let x = 1; x < sw - 1; x++) {
                            const idx = (y * sw + x) * 4;
                            if (resultData[idx + 3] === 0) {
                                // Check 4 neighbors
                                const hasFilledNeighbor = 
                                    resultData[((y-1) * sw + x) * 4 + 3] > 0 ||
                                    resultData[((y+1) * sw + x) * 4 + 3] > 0 ||
                                    resultData[(y * sw + x-1) * 4 + 3] > 0 ||
                                    resultData[(y * sw + x+1) * 4 + 3] > 0;
                                
                                if (hasFilledNeighbor) {
                                    // Check if this pixel is not a hard edge (line)
                                    const pr = d[idx], pg = d[idx+1], pb = d[idx+2];
                                    const brightness = (pr + pg + pb) / 3;
                                    // Don't expand into very dark pixels (lines) unless filling with dark color
                                    const fillBrightness = (fr + fg + fb) / 3;
                                    if (brightness > 30 || fillBrightness < 50) {
                                        resultData[idx] = fr;
                                        resultData[idx + 1] = fg;
                                        resultData[idx + 2] = fb;
                                        resultData[idx + 3] = fa;
                                    }
                                }
                            }
                        }
                    }
                }

                // Downscale result back to original size
                const resCvs = document.createElement('canvas');
                resCvs.width = sw; resCvs.height = sh;
                resCvs.getContext('2d').putImageData(new ImageData(resultData, sw, sh), 0, 0);
                
                const finalCvs = document.createElement('canvas');
                finalCvs.width = w; finalCvs.height = h;
                const finalCtx = finalCvs.getContext('2d');
                finalCtx.drawImage(resCvs, 0, 0, w, h);

                const resImg = document.createElementNS(NS, 'image');
                resImg.setAttribute('x', 0); resImg.setAttribute('y', 0);
                resImg.setAttribute('width', w); resImg.setAttribute('height', h);
                resImg.setAttribute('href', finalCvs.toDataURL());

                const g = document.createElementNS(NS, 'g');
                g.classList.add('fill-layer');
                g.appendChild(resImg);
                if (drawingLayer.firstChild) {
                    drawingLayer.insertBefore(g, drawingLayer.firstChild);
                } else {
                    drawingLayer.appendChild(g);
                }

                saveHistory();
                document.body.style.cursor = 'crosshair';
            };
            img.src = url;
            return;
        }
        if (state.tool === 'eraser') {
            const el = e.target.closest('#drawing-layer > *');
            if (el) { el.remove(); saveHistory(); }
            return;
        }
        if (state.tool === 'text') {
            // Now handled by drag logic
        } else {
            // Normal drag tools
        }

        const pos = getPos(e);
        if (state.tool === 'poly') {
            handlePolyClick(pos); return;
        }
        if (state.tool === 'curve') {
            handleCurveClick(pos); return;
        }

        state.isDrawing = true;
        state.startX = pos.x; state.startY = pos.y;
        state.points = [pos];
        overlayLayer.innerHTML = '';
        state.activeElement = createSvgElement(pos);
        drawSymmetryPreview();
    }

    function createSvgElement(pos) {
        let el;
        const common = {
            'stroke': state.color,
            'stroke-width': state.size,
            'fill': 'none',
            'stroke-linecap': 'round',
            'stroke-linejoin': 'round'
        };

        if (state.brushType === 'highlighter') common['stroke-opacity'] = 0.4;

        if (state.tool === 'brush' || state.tool === 'poly' || state.tool === 'curve') {
            el = document.createElementNS(NS, 'path');
            if (state.tool === 'brush' && state.brushType === 'multiLine') {
                let d = "";
                for (let i = 0; i < state.multiLineCount; i++) {
                    const offset = (i - (state.multiLineCount - 1) / 2) * (state.size * 2.5);
                    d += `M ${pos.x + offset} ${pos.y + offset} `;
                }
                el.setAttribute('d', d);
            } else {
                el.setAttribute('d', `M ${pos.x} ${pos.y}`);
            }
        } else if (state.tool === 'line') {
            el = document.createElementNS(NS, 'line');
            el.setAttribute('x1', pos.x); el.setAttribute('y1', pos.y);
            el.setAttribute('x2', pos.x); el.setAttribute('y2', pos.y);
        } else if (state.tool === 'rect') {
            el = document.createElementNS(NS, 'rect');
            el.setAttribute('x', pos.x); el.setAttribute('y', pos.y);
            el.setAttribute('width', 0); el.setAttribute('height', 0);
        } else if (state.tool === 'circle') {
            el = document.createElementNS(NS, 'ellipse');
            el.setAttribute('cx', pos.x); el.setAttribute('cy', pos.y);
            el.setAttribute('rx', 0); el.setAttribute('ry', 0);
        } else if (state.tool === 'triangle') {
            el = document.createElementNS(NS, 'path');
            el.setAttribute('d', `M ${pos.x} ${pos.y} L ${pos.x} ${pos.y} L ${pos.x} ${pos.y} Z`);
        } else if (state.tool === 'stamp') {
            el = document.createElementNS(NS, 'text');
            const iconClass = state.selectedStamp;
            const isBrand = iconClass.includes('fa-brands') || ['github', 'twitter', 'facebook', 'instagram', 'linkedin', 'github-alt'].some(b => iconClass.includes(b));

            const temp = document.createElement('i');
            temp.className = `${isBrand ? 'fa-brands' : 'fa-solid'} ${iconClass}`;
            document.body.appendChild(temp);
            const style = window.getComputedStyle(temp, ':before');
            const content = style.content.replace(/"/g, '');
            document.body.removeChild(temp);

            el.textContent = content;
            el.setAttribute('x', 0); el.setAttribute('y', 0);
            el.setAttribute('font-family', isBrand ? '"Font Awesome 6 Brands"' : '"Font Awesome 6 Free"');
            el.setAttribute('font-weight', isBrand ? '400' : '900');
            el.setAttribute('font-size', '100');
            el.setAttribute('text-anchor', 'middle');
            el.setAttribute('dominant-baseline', 'middle');
            el.setAttribute('transform', `translate(${pos.x}, ${pos.y}) scale(0,0)`);
            common['fill'] = state.color;
            common['stroke'] = 'none';
        } else if (state.tool === 'text') {
            el = document.createElementNS(NS, 'text');
            el.textContent = "Text...";
            el.setAttribute('x', 0); el.setAttribute('y', 0);
            el.setAttribute('font-family', 'Outfit');
            el.setAttribute('font-weight', '500');
            el.setAttribute('font-size', '100');
            el.setAttribute('text-anchor', 'middle');
            el.setAttribute('dominant-baseline', 'middle');
            el.setAttribute('transform', `translate(${pos.x}, ${pos.y}) scale(0,0)`);
            common['fill'] = state.color;
            common['stroke'] = 'none';
        }

        if (state.brushType === 'airbrush' && el) el.style.filter = 'blur(5px)';

        for (const [k, v] of Object.entries(common)) {
            if (el) el.setAttribute(k, v);
        }
        overlayLayer.appendChild(el);
        return el;
    }

    function draw(e) {
        if (!state.activeElement && !state.isDrawing) return;
        const pos = getPos(e);

        if (state.isDrawing) {
            if (state.tool === 'brush') {
                state.points.push(pos);
                if (state.brushType === 'multiLine') {
                    let d = "";
                    const spacing = state.size * 2.5;
                    for (let i = 0; i < state.multiLineCount; i++) {
                        const offset = (i - (state.multiLineCount - 1) / 2) * spacing;
                        // Start each multi-line segment with 'M'
                        d += `M ${state.points[0].x + offset} ${state.points[0].y + offset} `;
                        // Add 'L' segments for subsequent points
                        for (let j = 1; j < state.points.length; j++) {
                            d += `L ${state.points[j].x + offset} ${state.points[j].y + offset} `;
                        }
                    }
                    state.activeElement.setAttribute('d', d);
                } else {
                    const d = state.activeElement.getAttribute('d');
                    state.activeElement.setAttribute('d', d + ` L ${pos.x} ${pos.y}`);
                }
            } else if (state.tool === 'line') {
                state.activeElement.setAttribute('x2', pos.x);
                state.activeElement.setAttribute('y2', pos.y);
            } else if (state.tool === 'rect') {
                const x = Math.min(pos.x, state.startX), y = Math.min(pos.y, state.startY);
                const w = Math.abs(pos.x - state.startX), h = Math.abs(pos.y - state.startY);
                state.activeElement.setAttribute('x', x);
                state.activeElement.setAttribute('y', y);
                state.activeElement.setAttribute('width', w);
                state.activeElement.setAttribute('height', h);
            } else if (state.tool === 'circle') {
                const cx = (state.startX + pos.x) / 2, cy = (state.startY + pos.y) / 2;
                const rx = Math.abs(pos.x - state.startX) / 2, ry = Math.abs(pos.y - state.startY) / 2;
                state.activeElement.setAttribute('cx', cx);
                state.activeElement.setAttribute('cy', cy);
                state.activeElement.setAttribute('rx', rx);
                state.activeElement.setAttribute('ry', ry);
            } else if (state.tool === 'triangle') {
                const x1 = state.startX, y1 = state.startY;
                const x2 = pos.x, y2 = pos.y;
                const topX = (x1 + x2) / 2;
                const d = `M ${topX} ${y1} L ${x1} ${y2} L ${x2} ${y2} Z`;
                state.activeElement.setAttribute('d', d);
            } else if (state.tool === 'stamp' || state.tool === 'text') {
                const w = pos.x - state.startX, h = pos.y - state.startY;
                const baseSize = 100;
                const sx = w / baseSize, sy = h / baseSize;
                state.activeElement.setAttribute('transform', `translate(${state.startX + w / 2}, ${state.startY + h / 2}) scale(${sx}, ${sy})`);
            }
        } else {
            // Previews for multi-click tools
            if (state.tool === 'poly' && state.polyPoints.length > 0) {
                let d = "";
                state.polyPoints.forEach((p, i) => d += (i === 0 ? "M" : "L") + ` ${p.x} ${p.y}`);
                d += ` L ${pos.x} ${pos.y}`;
                state.activeElement.setAttribute('d', d);
            } else if (state.tool === 'curve' && state.curvePoints.length > 0) {
                let d = "";
                if (state.curvePoints.length === 1) {
                    // Point 1: Start. Currently defining Point 2: End.
                    d = `M ${state.curvePoints[0].x} ${state.curvePoints[0].y} L ${pos.x} ${pos.y}`;
                } else if (state.curvePoints.length === 2) {
                    // Point 1 & 2: Start/End fixed. Currently defining Control Point (Flex).
                    d = `M ${state.curvePoints[0].x} ${state.curvePoints[0].y} Q ${pos.x} ${pos.y} ${state.curvePoints[1].x} ${state.curvePoints[1].y}`;
                }
                state.activeElement.setAttribute('d', d);
            }
        }
        drawSymmetryPreview();
    }

    function handlePolyClick(pos) {
        if (state.polyPoints.length === 0) {
            overlayLayer.innerHTML = '';
            state.activeElement = createSvgElement(pos);
            // Show closure dot
            const dot = document.createElementNS(NS, 'circle');
            dot.className = 'poly-closer';
            dot.setAttribute('cx', pos.x); dot.setAttribute('cy', pos.y);
            dot.setAttribute('r', 8 / state.scale);
            dot.setAttribute('fill', state.color);
            dot.setAttribute('stroke', '#ffffff');
            dot.setAttribute('stroke-width', 2 / state.scale);
            dot.style.pointerEvents = 'none';
            guideLayer.appendChild(dot);
        } else {
            const start = state.polyPoints[0];
            if (Math.hypot(pos.x - start.x, pos.y - start.y) < 20 / state.scale) {
                const d = state.activeElement.getAttribute('d');
                state.activeElement.setAttribute('d', d + ' Z');
                guideLayer.querySelectorAll('.poly-closer').forEach(e => e.remove());
                commitShape();
                state.polyPoints = []; return;
            }
            const d = state.activeElement.getAttribute('d');
            state.activeElement.setAttribute('d', d + ` L ${pos.x} ${pos.y}`);
        }
        state.polyPoints.push(pos);
        drawSymmetryPreview();
    }

    function handleCurveClick(pos) {
        if (state.curvePoints.length === 0) {
            overlayLayer.innerHTML = '';
            state.activeElement = createSvgElement(pos);
        }
        state.curvePoints.push(pos);
        if (state.curvePoints.length === 3) {
            // state.curvePoints = [Start, End, Control]
            const p0 = state.curvePoints[0], p2 = state.curvePoints[1], p1 = state.curvePoints[2];
            const d = `M ${p0.x} ${p0.y} Q ${p1.x} ${p1.y} ${p2.x} ${p2.y}`;
            state.activeElement.setAttribute('d', d);
            commitShape();
            state.curvePoints = [];
        } else {
            drawSymmetryPreview();
        }
    }

    function drawSymmetryPreview() {
        while (overlayLayer.childNodes.length > 1) overlayLayer.removeChild(overlayLayer.lastChild);
        if (state.symmetry === 'none' || !overlayLayer.firstChild) return;
        const orig = overlayLayer.firstChild;
        const origTr = orig.getAttribute('transform') || '';
        const cx = 1920 / 2, cy = 1080 / 2;

        if (state.symmetry === 'radial') {
            const step = 360 / state.mirrorCount;
            for (let i = 1; i < state.mirrorCount; i++) {
                const c = orig.cloneNode(true);
                c.setAttribute('transform', `rotate(${i * step}, ${cx}, ${cy}) ${origTr}`);
                overlayLayer.appendChild(c);
            }
        } else if (state.symmetry === 'reflect') {
            const tps = state.reflectType === 'both' ? ['h', 'v', 'b'] : [state.reflectType[0]];
            tps.forEach(t => {
                const c = orig.cloneNode(true);
                let symTr = '';
                if (t === 'h') symTr = `scale(-1, 1) translate(${-1920}, 0)`;
                else if (t === 'v') symTr = `scale(1, -1) translate(0, ${-1080})`;
                else if (t === 'b') symTr = `scale(-1, -1) translate(${-1920}, ${-1080})`;
                c.setAttribute('transform', `${symTr} ${origTr}`);
                overlayLayer.appendChild(c);
            });
        }
    }

    function commitShape() {
        if (!state.activeElement) return;
        guideLayer.querySelectorAll('.poly-closer').forEach(e => e.remove());
        while (overlayLayer.firstChild) drawingLayer.appendChild(overlayLayer.firstChild);
        state.activeElement = null;
        saveHistory();
    }

    function stopDrawing() {
        if (!state.isDrawing) return;
        state.isDrawing = false;

        if (state.tool === 'text' && state.activeElement) {
            const txt = prompt("Enter text:", "");
            if (!txt) {
                overlayLayer.innerHTML = '';
                state.activeElement = null;
                return;
            }
            state.activeElement.textContent = txt;
            drawSymmetryPreview(); // Refresh clones with the actual text
        }

        commitShape();
    }

    function drawSymmetryGuides() {
        guideLayer.innerHTML = '';
        if (state.symmetry === 'none') return;
        const cx = 1920 / 2, cy = 1080 / 2;
        const common = { 'stroke': 'rgba(0,0,0,0.1)', 'stroke-width': 1, 'stroke-dasharray': '10,10' };
        const h = document.createElementNS(NS, 'line');
        h.setAttribute('x1', 0); h.setAttribute('y1', cy); h.setAttribute('x2', 1920); h.setAttribute('y2', cy);
        const v = document.createElementNS(NS, 'line');
        v.setAttribute('x1', cx); v.setAttribute('y1', 0); v.setAttribute('x2', cx); v.setAttribute('y2', 1080);
        for (const [k, v_val] of Object.entries(common)) { h.setAttribute(k, v_val); v.setAttribute(k, v_val); }
        guideLayer.appendChild(h); guideLayer.appendChild(v);
        const c = document.createElementNS(NS, 'circle');
        c.setAttribute('cx', cx); c.setAttribute('cy', cy); c.setAttribute('r', 5);
        c.setAttribute('fill', 'rgba(0,0,0,0.2)');
        guideLayer.appendChild(c);
    }

    function pickColor(e) {
        const el = document.elementFromPoint(e.clientX, e.clientY);
        if (el && el.getAttribute('stroke') && el.getAttribute('stroke') !== 'none') setColor(el.getAttribute('stroke'));
        else if (el && el.getAttribute('fill') && el.getAttribute('fill') !== 'none') setColor(el.getAttribute('fill'));
    }

    function loadGallery() {
        galleryGrid.innerHTML = 'Loading...';
        fetch('/gallery').then(res => res.json()).then(ims => {
            galleryGrid.innerHTML = '';
            ims.forEach(src => {
                const it = document.createElement('div'); it.className = 'gallery-item';
                const img = document.createElement('img'); img.src = src; img.onclick = () => loadFromGallery(src);
                it.oncontextmenu = (e) => {
                    e.preventDefault();
                    showContextMenu(e, 'artwork', { src, element: it });
                };
                const del = document.createElement('div'); del.className = 'delete-btn';
                del.innerHTML = '<i class="fa-solid fa-trash"></i>';
                del.onclick = (e) => { e.stopPropagation(); deleteArtwork(src, it); };
                it.append(img, del); galleryGrid.append(it);
            });
        });
    }

    function deleteArtwork(src, it) {
        if (!confirm('Delete?')) return;
        fetch('/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename: src.split('/').pop() }) })
            .then(r => r.json()).then(d => { if (d.success) it.remove(); });
    }

    function loadFromGallery(src) {
        fetch(src).then(res => res.text()).then(svgStr => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(svgStr, 'image/svg+xml');
            const newDrawing = doc.getElementById('drawing-layer');
            const newBg = doc.getElementById('svg-bg');
            if (newDrawing) drawingLayer.innerHTML = newDrawing.innerHTML;
            if (newBg) bgRect.setAttribute('fill', newBg.getAttribute('fill'));
            saveHistory(); modal.classList.remove('open');
        });
    }

    function exportArtworkAsPng(src) {
        const w = parseInt(prompt("Export Width (px):", "1920"));
        if (!w) return;
        const h = Math.round((w * 1080) / 1920);
        const scale = w / 1920;

        fetch(src).then(res => res.text()).then(svgStr => {
            const parser = new DOMParser();
            const svgDoc = parser.parseFromString(svgStr, 'image/svg+xml');
            const svgEl = svgDoc.documentElement;

            // 1. Create a version without text to render paths/shapes
            const pathsOnlyDoc = svgDoc.cloneNode(true);
            const textNodes = pathsOnlyDoc.querySelectorAll('text');
            textNodes.forEach(n => n.remove());
            const pathsSvgStr = new XMLSerializer().serializeToString(pathsOnlyDoc);

            const blob = new Blob([pathsSvgStr], { type: 'image/svg+xml;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const img = new Image();

            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = w;
                canvas.height = h;
                const ctx = canvas.getContext('2d');

                // Draw paths/shapes first
                ctx.drawImage(img, 0, 0, w, h);

                // 2. Manually draw fonts/icons to bypass blob isolation
                const originalTextNodes = svgDoc.querySelectorAll('text');
                originalTextNodes.forEach(node => {
                    ctx.save();

                    const fill = node.getAttribute('fill') || '#000000';
                    const fontFamily = node.getAttribute('font-family') || 'Outfit';
                    const fontWeight = node.getAttribute('font-weight') || '500';
                    const fontSize = parseFloat(node.getAttribute('font-size') || '100');
                    const text = node.textContent;
                    const transformStr = node.getAttribute('transform') || '';

                    ctx.fillStyle = fill;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';

                    // Apply scale factor to the overall canvas context
                    ctx.scale(scale, scale);

                    // Robust transform parsing for multiple operations (rotate, scale, translate)
                    if (transformStr) {
                        const regex = /(\w+)\(([^)]+)\)/g;
                        let match;
                        while ((match = regex.exec(transformStr)) !== null) {
                            const type = match[1];
                            const args = match[2].split(/[,\s]+/).map(parseFloat);

                            if (type === 'translate') {
                                ctx.translate(args[0], args[1] || 0);
                            } else if (type === 'scale') {
                                ctx.scale(args[0], args[1] === undefined ? args[0] : args[1]);
                            } else if (type === 'rotate') {
                                if (args.length === 3) { // rotate(angle, cx, cy)
                                    ctx.translate(args[1], args[2]);
                                    ctx.rotate(args[0] * Math.PI / 180);
                                    ctx.translate(-args[1], -args[2]);
                                } else {
                                    ctx.rotate(args[0] * Math.PI / 180);
                                }
                            }
                        }
                    } else {
                        const x = parseFloat(node.getAttribute('x') || '0');
                        const y = parseFloat(node.getAttribute('y') || '0');
                        ctx.translate(x, y);
                    }

                    ctx.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
                    ctx.fillText(text, 0, 0);

                    ctx.restore();
                });

                const pngUrl = canvas.toDataURL('image/png');
                const link = document.createElement('a');
                link.download = `export_${Date.now()}.png`;
                link.href = pngUrl;
                link.click();
                URL.revokeObjectURL(url);
            };
            img.src = url;
        });
    }

    // Removed addTextPrompt - functionality merged into stopDrawing flow

    function updateGridView() {
        if (state.gridShow) {
            canvasContainer.classList.add('grid-active');
            canvasContainer.style.setProperty('--grid-size', state.gridSize + 'px');
        } else canvasContainer.classList.remove('grid-active');
    }

    function updateBgTransparency() {
        if (state.transparentBg) {
            bgRect.setAttribute('fill', 'none');
        } else {
            bgRect.setAttribute('fill', '#ffffff'); // Or restore specific fill if needed
        }
    }

    // --- Listeners ---
    toggleBtn.onclick = () => {
        sidebar.classList.toggle('collapsed');
        toggleBtn.innerHTML = sidebar.classList.contains('collapsed') ? '<i class="fa-solid fa-chevron-right"></i>' : '<i class="fa-solid fa-bars"></i>';
    };

    toolsBtns.forEach(b => {
        b.onclick = () => {
            if (b.id.startsWith('tool-')) setTool(b.id.replace('tool-', ''));
            else if (b.id.startsWith('type-')) setBrushType(b.id.replace('type-', ''));
        };
    });

    btnAddStamp.onclick = () => {
        let i = prompt("Icon name (e.g., star, ghost, apple):", "star");
        if (i) {
            if (!i.startsWith('fa-')) i = 'fa-' + i;
            if (!state.stamps.includes(i)) {
                state.stamps.push(i); saveIcons(); renderStamps();
            }
        }
    };

    btnStampsPopover.onclick = (e) => { e.stopPropagation(); stampsPopover.classList.toggle('visible'); };
    document.addEventListener('click', (e) => {
        if (!stampsPopover.contains(e.target) && e.target !== btnStampsPopover) stampsPopover.classList.remove('visible');
        contextMenu.style.display = 'none';
    });

    cmDelete.onclick = () => {
        if (currentContextType === 'stamp') deleteStamp(currentContextData);
        else if (currentContextType === 'artwork') deleteArtwork(currentContextData.src, currentContextData.element);
        contextMenu.style.display = 'none';
    };

    cmExportPng.onclick = () => {
        if (currentContextType === 'artwork') exportArtworkAsPng(currentContextData.src);
        contextMenu.style.display = 'none';
    };

    brushSizeInput.oninput = (e) => { state.size = e.target.value; sizeValDisplay.textContent = state.size; };
    colorPicker.oninput = (e) => setColor(e.target.value);
    toggleSwatchesBtn.onclick = () => {
        swatchesContainer.classList.toggle('visible');
        toggleSwatchesBtn.classList.toggle('active');
    };

    btnClear.onclick = () => {
        drawingLayer.innerHTML = ''; bgRect.setAttribute('fill', '#ffffff');
        saveHistory();
    };
    btnSave.onclick = () => {
        if (state.activeElement) commitShape();
        const clone = svg.cloneNode(true);
        const overlay = clone.getElementById('overlay-layer');
        const guide = clone.getElementById('guide-layer');
        if (overlay) overlay.innerHTML = '';
        if (guide) guide.innerHTML = '';

        const defs = document.createElementNS(NS, 'defs');
        const style = document.createElementNS(NS, 'style');
        style.textContent = `
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');
            text { white-space: pre; }
        `;
        defs.appendChild(style);
        clone.insertBefore(defs, clone.firstChild);

        const data = new XMLSerializer().serializeToString(clone);
        fetch('/save', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ image: data, type: 'svg' }) })
            .then(res => res.json())
            .then(d => { if (d.success) alert('Saved successfully!'); });
    };
    btnGallery.onclick = () => { modal.classList.add('open'); loadGallery(); };
    closeModal.onclick = () => modal.classList.remove('open');

    gridShowToggle.onchange = (e) => { state.gridShow = e.target.checked; updateGridView(); saveSettings(); };
    gridSnapToggle.onchange = (e) => { state.gridSnap = e.target.checked; saveSettings(); };
    transparentBgToggle.onchange = (e) => { state.transparentBg = e.target.checked; updateBgTransparency(); saveSettings(); };
    gridSizeInput.oninput = (e) => { state.gridSize = parseInt(e.target.value); gridSizeVal.textContent = state.gridSize; updateGridView(); };
    gridSizeInput.onchange = () => saveSettings();

    symRadialBtn.onclick = () => setSymmetry('radial');
    symReflectBtn.onclick = () => setSymmetry('reflect');

    viewport.onwheel = (e) => {
        e.preventDefault();
        const r = viewport.getBoundingClientRect();
        const mX = e.clientX - r.left, mY = e.clientY - r.top;
        const wX = (mX - state.panX) / state.scale, wY = (mY - state.panY) / state.scale;
        const z = e.deltaY < 0 ? 1.1 : 0.9;
        state.scale *= z;
        state.panX = mX - wX * state.scale;
        state.panY = mY - wY * state.scale;
        updateTransform();
    };

    viewport.onmousedown = (e) => {
        if (e.button === 1 || (e.button === 0 && e.ctrlKey)) {
            state.isPanning = true; state.lastMouseX = e.clientX; state.lastMouseY = e.clientY;
            viewport.style.cursor = 'grabbing';
        } else if (e.button === 0) startDrawing(e);
    };

    window.onmousemove = (e) => {
        if (state.isPanning) {
            state.panX += e.clientX - state.lastMouseX;
            state.panY += e.clientY - state.lastMouseY;
            state.lastMouseX = e.clientX; state.lastMouseY = e.clientY;
            updateTransform();
        } else draw(e);
    };

    window.onmouseup = () => { state.isPanning = false; viewport.style.cursor = 'crosshair'; stopDrawing(); };
    window.onkeydown = (e) => {
        if (state.activeElement && e.key === 'Escape') {
            overlayLayer.innerHTML = '';
            state.polyPoints = []; state.curvePoints = []; state.activeElement = null;
            return;
        }
        if (e.target.tagName === 'INPUT') return;
        if (e.ctrlKey && e.key === 'z') { e.preventDefault(); undo(); }
        if (e.ctrlKey && (e.key === 's' || e.key === 'S')) { e.preventDefault(); btnSave.click(); }
        const k = { 'b': 'brush', 'e': 'eraser', 'f': 'fill', 'i': 'picker', 't': 'text' };
        if (k[e.key.toLowerCase()]) setTool(k[e.key.toLowerCase()]);
    };

    init();
});
