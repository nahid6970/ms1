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
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('wheel', handleZoom);


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
        return {
            x: (e.clientX - state.panX) / state.zoom,
            y: (e.clientY - state.panY) / state.zoom
        };
    }

    function startDrawing(e) {
        // Correct logic for text tool input persistence
        if (e.target.tagName === 'TEXTAREA') return;

        state.isDrawing = true;
        const pos = getMousePos(e);
        state.startX = pos.x;
        state.startY = pos.y;

        if (state.tool === 'pan') {
            canvas.style.cursor = 'grabbing';
            state.lastMouseX = e.clientX;
            state.lastMouseY = e.clientY;
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
        } else if (state.tool === 'text') {
            createTextInput(e.clientX, e.clientY, pos.x, pos.y);
            state.isDrawing = false;
            return;
        } else {
            state.currentElement = {
                type: state.tool,
                startX: pos.x,
                startY: pos.y,
                endX: pos.x,
                endY: pos.y,
                color: state.strokeColor,
                width: state.lineWidth, // Use slider width for shapes
                opacity: state.opacity
            };
        }
    }

    function draw(e) {
        if (!state.isDrawing) return;

        const pos = getMousePos(e);
        state.currentX = pos.x;
        state.currentY = pos.y;

        if (state.tool === 'pan') {
            const dx = e.clientX - state.lastMouseX;
            const dy = e.clientY - state.lastMouseY;
            state.panX += dx;
            state.panY += dy;
            state.lastMouseX = e.clientX;
            state.lastMouseY = e.clientY;
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
        // Draw current element temporarily on top
        drawElement(state.currentElement);
    }

    function stopDrawing() {
        if (!state.isDrawing) return;
        state.isDrawing = false;

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
            // Basic arrow implementation
            const headLength = el.width * 3; // Scale arrow head with width
            const angle = Math.atan2(el.endY - el.startY, el.endX - el.startX);

            ctx.moveTo(el.startX, el.startY);
            ctx.lineTo(el.endX, el.endY);
            ctx.stroke();

            // Arrowhead
            ctx.beginPath();
            ctx.moveTo(el.endX, el.endY);
            ctx.lineTo(el.endX - headLength * Math.cos(angle - Math.PI / 6), el.endY - headLength * Math.sin(angle - Math.PI / 6));
            ctx.lineTo(el.endX - headLength * Math.cos(angle + Math.PI / 6), el.endY - headLength * Math.sin(angle + Math.PI / 6));
            ctx.lineTo(el.endX, el.endY);
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
        input.style.zIndex = '1000'; // Ensure it's on top

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
