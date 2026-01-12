document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('whiteboard');
    const ctx = canvas.getContext('2d');

    // State
    const state = {
        tool: 'select', // select, pan, draw, rectangle, ellipse, arrow, line, text
        isDrawing: false,
        startX: 0,
        startY: 0,
        currentX: 0,
        currentY: 0,
        strokeColor: '#ffffff',
        bgColor: '#121212',
        lineWidth: 3,
        fontFamily: 'Caveat',
        fontSize: 24,
        opacity: 1,
        zoom: 1,
        panX: 0,
        panY: 0,
        elements: [], // Store drawn elements
        currentElement: null
    };

    // Resize Canvas
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        redraw();
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // Event Listeners
    canvas.addEventListener('mousedown', handleStart);
    canvas.addEventListener('mousemove', handleMove);
    canvas.addEventListener('mouseup', handleEnd);
    canvas.addEventListener('mouseout', handleEnd);
    canvas.addEventListener('wheel', handleZoom);

    // Touch Support
    canvas.addEventListener('touchstart', handleStart, { passive: false });
    canvas.addEventListener('touchmove', handleMove, { passive: false });
    canvas.addEventListener('touchend', handleEnd);


    // Tool Switching
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tool = btn.dataset.tool;
            const action = btn.dataset.action;

            if (action === 'clear') {
                state.elements = [];
                state.panX = 0;
                state.panY = 0;
                state.zoom = 1;
                updateZoomDisplay();
                redraw();
                return;
            }

            if (tool) {
                state.tool = tool;
                document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                canvas.style.cursor = tool === 'pan' ? 'grab' : (tool === 'text' ? 'text' : 'crosshair');
            }
        });
    });

    // Color Picker
    document.querySelectorAll('.color-picker:not(.bg-picker) .color-swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
            document.querySelectorAll('.color-picker:not(.bg-picker) .color-swatch').forEach(s => s.classList.remove('active'));
            swatch.classList.add('active');
            state.strokeColor = swatch.dataset.color;
        });
    });

    // Custom Color Picker
    document.getElementById('custom-color-picker').addEventListener('input', (e) => {
        state.strokeColor = e.target.value;
        // visual update could be added here
    });

    // Background Picker
    document.querySelectorAll('.bg-picker .color-swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
            document.querySelectorAll('.bg-picker .color-swatch').forEach(s => s.classList.remove('active'));
            swatch.classList.add('active');
            state.bgColor = swatch.dataset.bgcolor;
            document.body.style.backgroundColor = state.bgColor;
            redraw();
        });
    });


    // Font & Size
    document.querySelectorAll('.font-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.font-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.fontFamily = btn.dataset.font;
        });
    });

    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.fontSize = parseInt(btn.dataset.size);
        });
    });

    // Opacity
    document.getElementById('opacity-slider').addEventListener('input', (e) => {
        state.opacity = parseFloat(e.target.value);
    });

    // Thickness
    document.getElementById('thickness-slider').addEventListener('input', (e) => {
        state.lineWidth = parseInt(e.target.value);
    });

    // Zoom Controls
    document.getElementById('zoom-in').addEventListener('click', () => {
        changeZoom(0.1);
    });

    document.getElementById('zoom-out').addEventListener('click', () => {
        changeZoom(-0.1);
    });

    function changeZoom(delta) {
        state.zoom += delta;
        if (state.zoom < 0.1) state.zoom = 0.1;
        updateZoomDisplay();
        redraw();
    }

    function updateZoomDisplay() {
        document.getElementById('zoom-level').textContent = Math.round(state.zoom * 100) + '%';
    }

    function handleZoom(e) {
        if (e.ctrlKey) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            changeZoom(delta);
        }
    }


    // Drawing Logic
    function getMousePos(e) {
        let clientX, clientY;
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else {
            clientX = e.clientX;
            clientY = e.clientY;
        }

        return {
            x: (clientX - state.panX) / state.zoom,
            y: (clientY - state.panY) / state.zoom,
            clientX: clientX,
            clientY: clientY
        };
    }

    // Hit Testing
    function isPointInElement(x, y, el) {
        const padding = 10;
        if (el.type === 'rectangle' || el.type === 'ellipse' || el.type === 'text') { // Text uses x,y but we can approx
            // For text, we assume a box. Ideally we'd measure text, but for now approximation:
            let left, right, top, bottom;
            if (el.type === 'text') {
                left = el.x;
                top = el.y;
                right = el.x + (el.text.length * el.fontSize * 0.6); // Approx width
                bottom = el.y + el.fontSize;
            } else {
                left = Math.min(el.startX, el.endX);
                right = Math.max(el.startX, el.endX);
                top = Math.min(el.startY, el.endY);
                bottom = Math.max(el.startY, el.endY);
            }
            return x >= left - padding && x <= right + padding && y >= top - padding && y <= bottom + padding;
        } else if (el.type === 'line' || el.type === 'arrow') {
            // Distance to line segment
            const A = x - el.startX;
            const B = y - el.startY;
            const C = el.endX - el.startX;
            const D = el.endY - el.startY;
            const dot = A * C + B * D;
            const lenSq = C * C + D * D;
            let param = -1;
            if (lenSq !== 0) param = dot / lenSq;
            let xx, yy;
            if (param < 0) {
                xx = el.startX;
                yy = el.startY;
            } else if (param > 1) {
                xx = el.endX;
                yy = el.endY;
            } else {
                xx = el.startX + param * C;
                yy = el.startY + param * D;
            }
            const dx = x - xx;
            const dy = y - yy;
            return (dx * dx + dy * dy) < (padding * padding);
        } else if (el.type === 'draw') {
            // Simple check: minimal distance to any point
            for (let p of el.points) {
                if (Math.hypot(p.x - x, p.y - y) < padding) return true;
            }
            return false;
        }
        return false;
    }

    function handleStart(e) {
        if (e.type === 'touchstart') {
            // e.preventDefault(); // Prevent scrolling on touch
            // Only prevent if we are drawing or panning (not attempting to click ui?? UI is outside canvas)
            if (e.target === canvas) e.preventDefault();
        }

        if (e.target.tagName === 'TEXTAREA') return;

        state.isDrawing = true;
        const pos = getMousePos(e);
        state.startX = pos.x;
        state.startY = pos.y;

        if (state.tool === 'pan') {
            canvas.style.cursor = 'grabbing';
            state.lastMouseX = pos.clientX;
            state.lastMouseY = pos.clientY;
            return;
        }

        if (state.tool === 'select') {
            // Find element to move
            // Reverse order to check top-most first
            for (let i = state.elements.length - 1; i >= 0; i--) {
                if (isPointInElement(pos.x, pos.y, state.elements[i])) {
                    state.selectedElement = state.elements[i];
                    state.isDraggingElement = true;
                    // We don't return here? We might want to clear selection if we clicked empty space
                    redraw(); // To maybe show selection highlight later
                    return;
                }
            }
            state.selectedElement = null;
            redraw(); // Clear highlight if clicked empty space
            return;
        }

        // For Text tool, we create input on Mouse Up (Click) to avoid drag creation issues
        // OR we just do it here but ensure we don't draw dots.
        if (state.tool === 'text') {
            // We'll handle text creation in handleEnd to emulate a "click"
            // But we need to mark that we started a click
            state.isClickCandidate = true;
            return;
        }

        if (state.tool === 'draw') {
            state.currentElement = {
                type: 'draw',
                points: [{ x: pos.x, y: pos.y }],
                color: state.strokeColor,
                width: state.lineWidth,
                opacity: state.opacity
            };
        } else {
            state.currentElement = {
                type: state.tool,
                startX: pos.x,
                startY: pos.y,
                endX: pos.x,
                endY: pos.y,
                color: state.strokeColor,
                width: state.lineWidth,
                opacity: state.opacity
            };
        }
    }

    function handleMove(e) {
        if (!state.isDrawing) return;
        if (e.type === 'touchmove') e.preventDefault();

        const pos = getMousePos(e);

        // Handle Moving Elements
        if (state.tool === 'select' && state.isDraggingElement && state.selectedElement) {
            const diffX = pos.x - state.startX;
            const diffY = pos.y - state.startY;

            const el = state.selectedElement;
            if (el.type === 'draw') {
                el.points.forEach(p => { p.x += diffX; p.y += diffY; });
            } else if (el.type === 'text') {
                el.x += diffX;
                el.y += diffY;
            } else {
                el.startX += diffX;
                el.startY += diffY;
                el.endX += diffX;
                el.endY += diffY;
            }

            // Reset start to current for next frame
            state.startX = pos.x;
            state.startY = pos.y;

            redraw();
            return;
        }


        state.currentX = pos.x;
        state.currentY = pos.y;

        // If moved significantly, it's not a click
        if (state.isClickCandidate && (Math.abs(state.startX - pos.x) > 5 || Math.abs(state.startY - pos.y) > 5)) {
            state.isClickCandidate = false;
        }
        if (state.tool === 'text') return; // Don't do anything while dragging in text mode

        if (state.tool === 'pan') {
            const dx = pos.clientX - state.lastMouseX;
            const dy = pos.clientY - state.lastMouseY;
            state.panX += dx;
            state.panY += dy;
            state.lastMouseX = pos.clientX;
            state.lastMouseY = pos.clientY;
            redraw();
            return;
        }

        if (state.tool === 'draw') {
            state.currentElement.points.push({ x: pos.x, y: pos.y });
        } else if (['rectangle', 'ellipse', 'line', 'arrow'].includes(state.tool)) {
            state.currentElement.endX = pos.x;
            state.currentElement.endY = pos.y;
        }

        redraw();
        drawElement(state.currentElement);
    }

    function handleEnd(e) {
        if (!state.isDrawing) return;
        state.isDrawing = false; // Reset immediately

        if (state.tool === 'select') {
            state.isDraggingElement = false;
            return;
        }

        if (state.tool === 'text' && state.isClickCandidate) {
            // It was a click!
            // We need coordinates. For touchend, e.touches is empty, use changedTouches
            let clientX, clientY;
            if (e.changedTouches && e.changedTouches.length > 0) {
                clientX = e.changedTouches[0].clientX;
                clientY = e.changedTouches[0].clientY;
            } else {
                clientX = e.clientX;
                clientY = e.clientY;
            }

            // Recalculate canvas pos
            const x = (clientX - state.panX) / state.zoom;
            const y = (clientY - state.panY) / state.zoom;

            createTextInput(clientX, clientY, x, y);
            state.isClickCandidate = false;
            return;
        }

        if (state.tool === 'pan') {
            canvas.style.cursor = 'grab';
            return;
        }

        if (state.currentElement) {
            state.elements.push(state.currentElement);
            state.currentElement = null;
            redraw();
        }
    }

    function redraw() {
        // Clear screen considering the infinite canvas illusion
        ctx.save();
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Background color
        ctx.fillStyle = state.bgColor;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Apply zoom and pan
        ctx.translate(state.panX, state.panY);
        ctx.scale(state.zoom, state.zoom);

        // Draw all saved elements
        state.elements.forEach(el => drawElement(el));

        // Highlight selected
        if (state.selectedElement && state.tool === 'select') {
            drawSelectionHighlight(state.selectedElement);
        }

        ctx.restore();
    }

    function drawSelectionHighlight(el) {
        ctx.save();
        ctx.strokeStyle = '#00a8ff'; // Selection color
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 3]);
        const padding = 5;

        let minX, minY, maxX, maxY;

        if (el.type === 'draw') {
            const xs = el.points.map(p => p.x);
            const ys = el.points.map(p => p.y);
            minX = Math.min(...xs); maxX = Math.max(...xs);
            minY = Math.min(...ys); maxY = Math.max(...ys);
        } else if (el.type === 'text') {
            minX = el.x;
            minY = el.y;
            maxX = el.x + (el.text.length * el.fontSize * 0.6);
            maxY = el.y + el.fontSize;
        } else {
            minX = Math.min(el.startX, el.endX);
            maxX = Math.max(el.startX, el.endX);
            minY = Math.min(el.startY, el.endY);
            maxY = Math.max(el.startY, el.endY);
        }

        ctx.strokeRect(minX - padding, minY - padding, (maxX - minX) + padding * 2, (maxY - minY) + padding * 2);
        ctx.restore();
    }

    function drawElement(el) {
        if (!el) return;

        ctx.save();
        ctx.globalAlpha = el.opacity;
        ctx.strokeStyle = el.color;
        ctx.fillStyle = el.color;
        ctx.lineWidth = el.width;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        ctx.beginPath();

        if (el.type === 'draw') {
            if (el.points.length < 2) return;
            ctx.moveTo(el.points[0].x, el.points[0].y);
            for (let i = 1; i < el.points.length; i++) {
                ctx.lineTo(el.points[i].x, el.points[i].y);
            }
            ctx.stroke();
        } else if (el.type === 'rectangle') {
            ctx.strokeRect(el.startX, el.startY, el.endX - el.startX, el.endY - el.startY);
        } else if (el.type === 'ellipse') {
            const radiusX = Math.abs((el.endX - el.startX) / 2);
            const radiusY = Math.abs((el.endY - el.startY) / 2);
            const centerX = Math.min(el.startX, el.endX) + radiusX;
            const centerY = Math.min(el.startY, el.endY) + radiusY;
            ctx.ellipse(centerX, centerY, radiusX, radiusY, 0, 0, 2 * Math.PI);
            ctx.stroke();
        } else if (el.type === 'line') {
            ctx.moveTo(el.startX, el.startY);
            ctx.lineTo(el.endX, el.endY);
            ctx.stroke();
        } else if (el.type === 'text') {
            ctx.font = `${el.fontFamily === 'Inter' ? '' : ''} ${el.fontSize}px ${el.fontFamily}`;
            ctx.fillStyle = el.color; // Use stroke color for text
            ctx.textBaseline = 'top'; // Easier positioning
            ctx.fillText(el.text, el.x, el.y);
        } else if (el.type === 'arrow') {
            const headLength = Math.max(10, el.width * 3); // Slightly larger head
            const angle = Math.atan2(el.endY - el.startY, el.endX - el.startX);

            ctx.moveTo(el.startX, el.startY);
            ctx.lineTo(el.endX, el.endY);
            ctx.stroke();

            // Better Arrowhead (Triangle)
            ctx.beginPath();
            ctx.moveTo(el.endX, el.endY);
            ctx.lineTo(el.endX - headLength * Math.cos(angle - Math.PI / 6), el.endY - headLength * Math.sin(angle - Math.PI / 6));
            ctx.lineTo(el.endX - headLength * Math.cos(angle + Math.PI / 6), el.endY - headLength * Math.sin(angle + Math.PI / 6));
            ctx.closePath(); // Close triangle
            ctx.fillStyle = el.color;
            ctx.fill();
        }

        ctx.restore();
    }

    function createTextInput(screenX, screenY, canvasX, canvasY) {
        const input = document.createElement('textarea');
        input.className = 'text-input-box';
        input.style.left = screenX + 'px';
        input.style.top = screenY + 'px';
        input.style.color = state.strokeColor;
        input.style.fontSize = state.fontSize + 'px';
        input.style.fontFamily = state.fontFamily;
        input.style.zIndex = '10000'; // Ensure it's on top
        // Add semi-transparent background to make it visible
        const r = parseInt(state.bgColor.slice(1, 3), 16);
        const g = parseInt(state.bgColor.slice(3, 5), 16);
        const b = parseInt(state.bgColor.slice(5, 7), 16);
        // Inverse contrast or just a slight box? Let's use a border and slight fill
        input.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        input.style.backdropFilter = 'blur(2px)';

        document.body.appendChild(input);

        // Auto-expand/focus
        input.focus();

        // Handle blur/enter to finalize text
        const finalize = () => {
            const text = input.value;
            if (text.trim()) {
                state.elements.push({
                    type: 'text',
                    text: text,
                    x: canvasX,
                    y: canvasY,
                    color: state.strokeColor,
                    fontSize: state.fontSize,
                    fontFamily: state.fontFamily,
                    opacity: state.opacity,
                    width: 1
                });
                redraw();
            }
            if (input.parentNode) {
                document.body.removeChild(input);
            }
        };

        input.addEventListener('blur', finalize);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                input.blur();
            }
        });
    }

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch (e.key.toLowerCase()) {
            case 'v': document.querySelector('[data-tool="select"]').click(); break;
            case ' ': document.querySelector('[data-tool="pan"]').click(); break;
            case 'p': document.querySelector('[data-tool="draw"]').click(); break;
            case 'r': document.querySelector('[data-tool="rectangle"]').click(); break;
            case 'o': document.querySelector('[data-tool="ellipse"]').click(); break;
            case 'l': document.querySelector('[data-tool="line"]').click(); break;
            case 't': document.querySelector('[data-tool="text"]').click(); break;
            case 'a': document.querySelector('[data-tool="arrow"]').click(); break;
        }
    });

});
