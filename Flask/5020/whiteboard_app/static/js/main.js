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
        currentElement: null,
        selectedElement: null,
        isDraggingElement: false,
        isRotatingElement: false,
        selectionHandle: null, // 'rotate'
        clipboard: null
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
            const id = btn.id;
            if (id === 'btn-copy') {
                copySelected();
                pasteClipboard(); // Auto-paste for "Duplicate" effect
                return;
            }
            if (id === 'btn-delete') {
                deleteSelected();
                return;
            }

            const tool = btn.dataset.tool;
            const action = btn.dataset.action;

            if (action === 'clear') {
                state.elements = []; // Clear
                state.selectedElement = null;
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

        const pos = getMousePos(e);
        state.isDrawing = true;
        state.startX = pos.x;
        state.startY = pos.y;

        if (state.tool === 'pan') {
            canvas.style.cursor = 'grabbing';
            state.lastMouseX = pos.clientX;
            state.lastMouseY = pos.clientY;
            return;
        }

        if (state.tool === 'select') {
            // Check for rotation handle hit if element selected
            if (state.selectedElement) {
                const center = getElementCenter(state.selectedElement);
                // Rotate handle position: roughly Top Center - 30px offset, rotated
                // We need to know current rotation to position handle accurately for hit test
                // Simpler: Just check distance to the visual handle we draw
                // WE NEED TO DEFINE ROTATION PROP IF NOT PRESENT
                if (state.selectedElement.rotation === undefined) state.selectedElement.rotation = 0;

                // For hit testing, we need the transformed handle position
                // This is getting complex mathematically.
                // Let's do a simpler hit test for rotation: if we are close to the handle
                // The handle is drawn relative to center.
                // We'll calculate the handle world position
                const bounds = getElementBounds(state.selectedElement);
                if (bounds) {
                    const cx = (bounds.minX + bounds.maxX) / 2;
                    const cy = (bounds.minY + bounds.maxY) / 2;
                    const handleDist = 30; // Distance above top
                    // Rotate the point (cx, bounds.minY - handleDist) around (cx, cy) by el.rotation
                    const angle = state.selectedElement.rotation || 0;
                    const hx_local = 0;
                    const hy_local = -(bounds.maxY - bounds.minY) / 2 - 30;

                    const hx_world = cx + hx_local * Math.cos(angle) - hy_local * Math.sin(angle);
                    const hy_world = cy + hx_local * Math.sin(angle) + hy_local * Math.cos(angle);

                    if (Math.hypot(pos.x - hx_world, pos.y - hy_world) < 15) {
                        state.isRotatingElement = true;
                        state.lastRotationAngle = Math.atan2(pos.y - cy, pos.x - cx);
                        return; // Handle hit
                    }
                }
            }

            // Find element to select/move
            // Reverse order to check top-most first
            for (let i = state.elements.length - 1; i >= 0; i--) {
                // Hit test considering rotation?
                // For now, hit test un-rotated bounding box for simplicity? 
                // Or implementing robust OBB hit test?
                // Lets start with unrotated for simplicity of "isPointInElement" 
                // but actually, we should inversely rotate the point to check against AABB
                const el = state.elements[i];
                // Inverse rotate point if element has rotation
                let testX = pos.x, testY = pos.y;
                if (el.rotation) {
                    const center = getElementCenter(el);
                    const dx = pos.x - center.x;
                    const dy = pos.y - center.y;
                    const angle = -el.rotation;
                    testX = center.x + dx * Math.cos(angle) - dy * Math.sin(angle);
                    testY = center.y + dx * Math.sin(angle) + dy * Math.cos(angle);
                }

                if (isPointInElement(testX, testY, el)) {
                    state.selectedElement = el;
                    state.isDraggingElement = true;
                    if (state.selectedElement.rotation === undefined) state.selectedElement.rotation = 0;
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
                opacity: state.opacity,
                rotation: 0
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
                opacity: state.opacity,
                rotation: 0
            };
        }
    }

    function handleMove(e) {
        if (!state.isDrawing) return;
        if (e.type === 'touchmove') e.preventDefault();

        const pos = getMousePos(e);

        // Handle Moving Elements
        if (state.tool === 'select') {
            if (state.isRotatingElement && state.selectedElement) {
                const center = getElementCenter(state.selectedElement);
                const angle = Math.atan2(pos.y - center.y, pos.x - center.x);
                // Snap to 15 deg steps if Shift pressed? Not implemented yet.
                // Rotation delta
                // const delta = angle - state.lastRotationAngle;
                // state.selectedElement.rotation += delta;
                // state.lastRotationAngle = angle;

                // Absolute rotation based on handle: Handle is "up" (-90deg), so offset
                // Actually simple atan2 gives absolute angle from center. 
                // We want the object's "top" to follow the mouse.
                // So rotation = angle + 90deg (PI/2)
                state.selectedElement.rotation = angle + Math.PI / 2;

                redraw();
                return;
            }

            if (state.isDraggingElement && state.selectedElement) {
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
            state.isRotatingElement = false;
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
            // Assign default rotation if missing
            state.currentElement.rotation = 0;
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

    function getElementBounds(el) {
        if (!el) return null;
        if (el.type === 'draw') {
            const xs = el.points.map(p => p.x);
            const ys = el.points.map(p => p.y);
            return { minX: Math.min(...xs), maxX: Math.max(...xs), minY: Math.min(...ys), maxY: Math.max(...ys) };
        } else if (el.type === 'text') {
            const width = el.text.length * el.fontSize * 0.6;
            return { minX: el.x, maxX: el.x + width, minY: el.y, maxY: el.y + el.fontSize };
        } else {
            return {
                minX: Math.min(el.startX, el.endX),
                maxX: Math.max(el.startX, el.endX),
                minY: Math.min(el.startY, el.endY),
                maxY: Math.max(el.startY, el.endY)
            };
        }
    }

    function getElementCenter(el) {
        const bounds = getElementBounds(el);
        return { x: (bounds.minX + bounds.maxX) / 2, y: (bounds.minY + bounds.maxY) / 2 };
    }

    function drawSelectionHighlight(el) {
        ctx.save();

        // Rotation for highlight
        const center = getElementCenter(el);
        if (el.rotation) {
            ctx.translate(center.x, center.y);
            ctx.rotate(el.rotation);
            ctx.translate(-center.x, -center.y);
        }

        ctx.strokeStyle = '#00a8ff';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 3]);
        const padding = 5;

        // Get Local Bounds (unrotated relative to center) 
        // Logic: All shapes are defined by coordinates matching unrotated state 
        // EXCEPT 'draw' which stores raw points. 
        // For 'draw', points are raw. If we rotate with ctx.rotate, we are rotating the visual representation.
        // So the bounds calculation using raw points matches the "local" bounds if we assume raw points are "model space".
        // BUT for 'draw' we modify points directly on move...
        // Let's rely on getElementBounds returning the axis aligned bounds of the data
        const bounds = getElementBounds(el);
        if (!bounds) { ctx.restore(); return; }

        ctx.strokeRect(bounds.minX - padding, bounds.minY - padding, (bounds.maxX - bounds.minX) + padding * 2, (bounds.maxY - bounds.minY) + padding * 2);

        // Draw Rotation Handle
        ctx.beginPath();
        const topY = bounds.minY - padding;
        const midX = (bounds.minX + bounds.maxX) / 2;
        ctx.moveTo(midX, topY);
        ctx.lineTo(midX, topY - 20);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(midX, topY - 25, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#00a8ff';
        ctx.fill();

        ctx.restore();
    }

    function drawElement(el) {
        if (!el) return;

        ctx.save();

        // Apply Rotation if exists
        if (el.rotation) {
            const center = getElementCenter(el);
            ctx.translate(center.x, center.y);
            ctx.rotate(el.rotation);
            ctx.translate(-center.x, -center.y);
        }

        ctx.globalAlpha = el.opacity;
        ctx.strokeStyle = el.color;
        ctx.fillStyle = el.color;
        ctx.lineWidth = el.width;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        ctx.beginPath();

        if (el.type === 'draw') {
            if (el.points.length < 2) { ctx.restore(); return; }
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
        // Allow shortcuts unless typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        const key = e.key.toLowerCase();

        // Delete (Del or Backspace)
        if (key === 'delete' || key === 'backspace') {
            e.preventDefault(); // Prevent browser back navigation
            deleteSelected();
        }

        // Copy (Ctrl+C)
        if ((e.ctrlKey || e.metaKey) && key === 'c') {
            e.preventDefault();
            copySelected();
        }

        // Paste (Ctrl+V)
        if ((e.ctrlKey || e.metaKey) && key === 'v') {
            // Allow default paste? No, we handle our own clipboard
            e.preventDefault();
            pasteClipboard();
        }

        // Tools
        switch (key) {
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

    // Actions
    function deleteSelected() {
        if (state.selectedElement) {
            state.elements = state.elements.filter(el => el !== state.selectedElement);
            state.selectedElement = null;
            redraw();
        }
    }

    function copySelected() {
        if (state.selectedElement) {
            state.clipboard = JSON.parse(JSON.stringify(state.selectedElement));
            console.log('Copied element to clipboard');
        }
    }

    function pasteClipboard() {
        if (state.clipboard) {
            const newEl = JSON.parse(JSON.stringify(state.clipboard));
            // Offset new element slightly
            const offset = 20;
            if (newEl.type === 'draw') {
                newEl.points.forEach(p => { p.x += offset; p.y += offset; });
            } else if (newEl.type === 'text') {
                newEl.x += offset;
                newEl.y += offset;
            } else {
                newEl.startX += offset;
                newEl.startY += offset;
                newEl.endX += offset;
                newEl.endY += offset;
            }
            state.elements.push(newEl);
            state.selectedElement = newEl;
            redraw();
            console.log('Pasted element');
        }
    }

});
