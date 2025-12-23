document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const canvas = document.getElementById('drawing-canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const viewport = document.getElementById('viewport');

    // Inputs
    const toolsBtns = document.querySelectorAll('.tool-btn');
    const brushSizeInput = document.getElementById('brush-size');
    const sizeValDisplay = document.getElementById('size-val');
    const colorPicker = document.getElementById('color-picker');
    const swatchesContainer = document.getElementById('color-swatches');

    // Actions
    const btnClear = document.getElementById('btn-clear');
    const btnExpand = document.getElementById('btn-expand');
    const btnSave = document.getElementById('btn-save');
    const btnGallery = document.getElementById('btn-gallery');

    // Modal
    const modal = document.getElementById('gallery-modal');
    const closeModal = modal.querySelector('.close-modal');
    const galleryGrid = document.getElementById('gallery-grid');

    // --- State ---
    const state = {
        isDrawing: false,
        tool: 'brush', // brush, eraser, line, rect, circle, fill, picker
        color: '#00d2ff',
        size: 5,
        startX: 0,
        startY: 0,
        snapshot: null, // ImageData for shape preview
        history: [],
        historyStep: -1,
        maxHistory: 20
    };

    // Initialize
    function init() {
        // Set initial canvas size
        canvas.width = 1200;
        canvas.height = 800;

        // White bg
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        updateContext();
        saveHistory(); // Initial state
        generateSwatches();
        centerCanvas();
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

    function updateContext() {
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.lineWidth = state.size;
        ctx.strokeStyle = state.tool === 'eraser' ? '#ffffff' : state.color;
        ctx.fillStyle = state.tool === 'eraser' ? '#ffffff' : state.color;
    }

    function setColor(color) {
        state.color = color;
        colorPicker.value = color; // might fail if color not hex, but swatches are hex
        // If eraser was active, switch back to brush
        if (state.tool === 'eraser') {
            setTool('brush');
        } else {
            updateContext();
        }
    }

    function setTool(toolName) {
        state.tool = toolName;
        // Visual update
        toolsBtns.forEach(b => {
            if (b.id === `tool-${toolName}`) b.classList.add('active');
            else b.classList.remove('active');
        });
        updateContext();
    }

    function centerCanvas() {
        // Scroll viewport to center
        const vW = viewport.clientWidth;
        const vH = viewport.clientHeight;
        const cW = canvas.width;
        const cH = canvas.height;

        viewport.scrollTop = (cH - vH) / 2;
        viewport.scrollLeft = (cW - vW) / 2;
    }

    // --- History System ---
    function saveHistory() {
        // Removing future states if we were in middle of history
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

    // Ctrl+Z handler can be added easily with this system
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
            e.preventDefault();
            undo();
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

    // --- Drawing Logic ---
    function getPos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    window.addEventListener('mouseup', stopDrawing);

    function startDrawing(e) {
        if (e.target !== canvas) return;
        state.isDrawing = true;
        const pos = getPos(e);
        state.startX = pos.x;
        state.startY = pos.y;

        // Tools logic
        if (state.tool === 'fill') {
            fill(pos.x, pos.y, state.color);
            saveHistory();
            state.isDrawing = false; // Fill is one-time action
            return;
        }

        if (state.tool === 'picker') {
            pickColor(pos.x, pos.y);
            state.isDrawing = false;
            return;
        }

        ctx.beginPath();
        ctx.moveTo(pos.x, pos.y);

        // Save snapshot for shapes
        if (['line', 'rect', 'circle'].includes(state.tool)) {
            state.snapshot = ctx.getImageData(0, 0, canvas.width, canvas.height);
        } else {
            // Brush/Eraser: just draw a dot incase it's a click
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
        }
    }

    function draw(e) {
        if (!state.isDrawing) return;
        const pos = getPos(e);

        if (state.tool === 'brush' || state.tool === 'eraser') {
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
        } else if (state.tool === 'line') {
            ctx.putImageData(state.snapshot, 0, 0);
            ctx.beginPath();
            ctx.moveTo(state.startX, state.startY);
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
        } else if (state.tool === 'rect') {
            ctx.putImageData(state.snapshot, 0, 0);
            ctx.beginPath();
            let w = pos.x - state.startX;
            let h = pos.y - state.startY;
            ctx.strokeRect(state.startX, state.startY, w, h); // could be fillRect based on preference
        } else if (state.tool === 'circle') {
            ctx.putImageData(state.snapshot, 0, 0);
            ctx.beginPath();
            let r = Math.sqrt(Math.pow(pos.x - state.startX, 2) + Math.pow(pos.y - state.startY, 2));
            ctx.arc(state.startX, state.startY, r, 0, 2 * Math.PI);
            ctx.stroke();
        }
    }

    function stopDrawing() {
        if (!state.isDrawing) return;
        state.isDrawing = false;
        if (state.tool !== 'picker' && state.tool !== 'fill') {
            ctx.closePath();
            saveHistory();
        }
    }

    // --- Tools Imp ---
    function pickColor(x, y) {
        const p = ctx.getImageData(x, y, 1, 1).data;
        const hex = "#" + ("000000" + rgbToHex(p[0], p[1], p[2])).slice(-6);
        setColor(hex);
        setTool('brush'); // Auto switch back
        showToast(`Color picked: ${hex}`, 'info');
    }

    function rgbToHex(r, g, b) {
        if (r > 255 || g > 255 || b > 255)
            throw "Invalid color component";
        return ((r << 16) | (g << 8) | b).toString(16);
    }

    // Flood Fill (simplified stack-based)
    function fill(x, y, fillColor) {
        // Get image data
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        // Target color
        x = Math.floor(x);
        y = Math.floor(y);
        const startPos = (y * canvas.width + x) * 4;
        const startR = data[startPos];
        const startG = data[startPos + 1];
        const startB = data[startPos + 2];
        const startA = data[startPos + 3];

        // Parse fill color
        // This is tricky without a library, so we'll use a temp canvas or parse hex
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

        // Optimization: if colors match, don't fill
        if (startR === fillR && startG === fillG && startB === fillB && startA === fillA) return;

        const stack = [[x, y]];

        // Helper to check match
        function match(pos) {
            return data[pos] === startR && data[pos + 1] === startG && data[pos + 2] === startB && data[pos + 3] === startA;
        }

        // Helper to color
        function colorPixel(pos) {
            data[pos] = fillR;
            data[pos + 1] = fillG;
            data[pos + 2] = fillB;
            data[pos + 3] = fillA;
        }

        while (stack.length) {
            let [cx, cy] = stack.pop();
            let pixelPos = (cy * canvas.width + cx) * 4;

            // Go up as long as it matches
            while (cy >= 0 && match(pixelPos)) {
                cy--;
                pixelPos -= canvas.width * 4;
            }
            cy++;
            pixelPos += canvas.width * 4;

            let reachLeft = false;
            let reachRight = false;

            // Go down
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
    // Tool buttons
    toolsBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const t = btn.id.replace('tool-', '');
            setTool(t);
        });
    });

    // Brush Size
    brushSizeInput.addEventListener('input', (e) => {
        state.size = e.target.value;
        sizeValDisplay.textContent = state.size;
        updateContext();
    });

    // Color Picker
    colorPicker.addEventListener('input', (e) => {
        setColor(e.target.value);
    });

    // Actions
    btnClear.addEventListener('click', () => {
        // Removed confirm dialog for smoother UX and robustness
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Reset context to ensure state is consistent
        updateContext();
        saveHistory();
        showToast('Canvas cleared!');
    });

    btnExpand.addEventListener('click', () => {
        const oldData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const add = 400;
        canvas.width += add;
        canvas.height += add;

        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.putImageData(oldData, 0, 0);

        updateContext();
        saveHistory();
        showToast(`Canvas expanded to ${canvas.width}x${canvas.height}`);
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

    // Gallery
    btnGallery.addEventListener('click', () => {
        modal.classList.add('open');
        loadGallery();
    });

    closeModal.addEventListener('click', () => {
        modal.classList.remove('open');
    });

    // Close modal on click outside
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
        img.src = src; // this is a URL
        img.crossOrigin = "Anonymous"; // just in case
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            updateContext(); // reset context
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

    // Shortcuts
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
