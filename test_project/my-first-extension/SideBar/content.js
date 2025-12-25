(function () {
  // Prevent multiple injections
  if (document.getElementById('qs-sidebar-root')) return;

  let links = [];
  let isLeft = false;
  let isExpanded = false;
  let isHidden = false;

  // Create Sidebar
  const root = document.createElement('div');
  root.id = 'qs-sidebar-root';
  root.className = 'right'; // Default to right
  document.documentElement.appendChild(root);

  // Create Modal (Separate from Sidebar)
  const modalRoot = document.createElement('div');
  modalRoot.id = 'qs-modal-root';
  document.documentElement.appendChild(modalRoot);

  function updatePageShift() {
    const isHidden = root.classList.contains('qs-hidden');
    const html = document.documentElement;

    // Reset classes
    html.classList.remove('qs-shift-left', 'qs-shift-right', 'qs-expanded');

    if (!isHidden) {
      html.classList.add(isLeft ? 'qs-shift-left' : 'qs-shift-right');
      if (isExpanded) html.classList.add('qs-expanded');
    }

    // YouTube Specific Header & Player Fix
    const ytHeader = document.querySelector('#masthead-container');
    const ytPlayer = document.querySelector('#content.ytd-app'); // Main content wrapper

    if (!isHidden) {
      const width = isExpanded ? 280 : 60;
      if (isLeft) {
        if (ytHeader) ytHeader.style.setProperty('left', `${width}px`, 'important');
        if (ytPlayer) ytPlayer.style.setProperty('margin-left', `${width}px`, 'important');
      } else {
        if (ytHeader) ytHeader.style.setProperty('left', '0', 'important');
        if (ytHeader) ytHeader.style.setProperty('right', `${width}px`, 'important');
        if (ytPlayer) ytPlayer.style.setProperty('margin-right', `${width}px`, 'important');
      }
    } else {
      if (ytHeader) {
        ytHeader.style.setProperty('left', '0', 'important');
        ytHeader.style.setProperty('right', '0', 'important');
      }
      if (ytPlayer) {
        ytPlayer.style.setProperty('margin-left', '0', 'important');
        ytPlayer.style.setProperty('margin-right', '0', 'important');
      }
    }

    // Force a resize event so YouTube/Google Maps etc. recalculate their UI
    window.dispatchEvent(new Event('resize'));
  }

  function updateLayout() {
    root.className = (isLeft ? 'left' : 'right') + (isExpanded ? ' expanded' : '') + (isHidden ? ' qs-hidden' : '');

    // Handle Transform for visibility
    if (isHidden) {
      root.style.transform = isLeft ? "translateX(-110%)" : "translateX(110%)";
    } else {
      root.style.transform = "translateX(0)";
    }

    // Update Side Toggle Icon (Arrow pointing to the opposite side)
    const sideToggle = document.getElementById('qs-side-toggle');
    if (sideToggle) {
      sideToggle.innerHTML = isLeft
        ? `<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z" /></svg>` // Arrow Right
        : `<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z" /></svg>`; // Arrow Left
    }

    // Update Expand Toggle Icon (Chevrons pointing in the expansion direction)
    const expandToggle = document.getElementById('qs-expand-toggle');
    if (expandToggle) {
      if (isLeft) {
        expandToggle.innerHTML = isExpanded
          ? `<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M18.41,16.59L13.82,12L18.41,7.41L17,6L11,12L17,18L18.41,16.59M11.41,16.59L6.82,12L11.41,7.41L10,6L4,12L10,18L11.41,16.59Z" /></svg>` // Double Left
          : `<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M5.59,16.59L10.18,12L5.59,7.41L7,6L13,12L7,18L5.59,16.59M12.59,16.59L17.18,12L12.59,7.41L14,6L20,12L14,18L12.59,16.59Z" /></svg>`; // Double Right
      } else {
        expandToggle.innerHTML = isExpanded
          ? `<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M5.59,16.59L10.18,12L5.59,7.41L7,6L13,12L7,18L5.59,16.59M12.59,16.59L17.18,12L12.59,7.41L14,6L20,12L14,18L12.59,16.59Z" /></svg>` // Double Right
          : `<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M18.41,16.59L13.82,12L18.41,7.41L17,6L11,12L17,18L18.41,16.59M11.41,16.59L6.82,12L11.41,7.41L10,6L4,12L10,18L11.41,16.59Z" /></svg>`; // Double Left
      }
    }

    updatePageShift();
  }

  // Initial markup
  root.innerHTML = `
    <div class="qs-header">
      <div class="qs-actions">
        <button id="qs-add-toggle" class="qs-icon-btn" title="Add Link">
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" /></svg>
        </button>
        <button id="qs-side-toggle" class="qs-icon-btn" title="Toggle Left/Right">
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M15,5V11H21V5M10,11H15V5H10M16,18H21V12H16M10,18H15V12H10M4,18H9V12H4M4,11H9V5H4V11Z" /></svg>
        </button>
        <button id="qs-expand-toggle" class="qs-icon-btn" title="Expand Labels">
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M14,14H19V16H14V14M14,10H19V12H14V10M14,6H19V8H14V6M5,6H9V8H5V6M5,10H9V12H5V10M5,14H9V16H5V14Z" /></svg>
        </button>
      </div>
    </div>
    <div id="qs-links-list"></div>
  `;

  modalRoot.innerHTML = `
    <div id="qs-modal-overlay">
      <div id="qs-modal-content">
        <h3 id="qs-modal-title">Add New Link</h3>
        <input type="hidden" id="qs-edit-id">
        <input type="text" id="qs-title-input" placeholder="Title (e.g. GitHub)">
        <input type="text" id="qs-url-input" placeholder="URL (https://...)">
        <div class="qs-input-group">
          <span>Tile Style</span>
          <div class="qs-color-controls">
            <input type="color" id="qs-color-input" value="#38bdf8" title="Pick Color">
            <label class="qs-checkbox-label">
              <input type="checkbox" id="qs-solid-input"> Solid
            </label>
          </div>
        </div>
        <div class="qs-form-btns">
          <button id="qs-save-btn" class="qs-btn-primary">Save Link</button>
          <button id="qs-cancel-btn" class="qs-btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

    <div id="qs-context-menu">
      <div class="qs-context-item" id="qs-ctx-edit">Edit</div>
      <div class="qs-context-item qs-danger" id="qs-ctx-delete">Delete</div>
    </div>
  `;

  const linksList = document.getElementById('qs-links-list');
  const modalOverlay = document.getElementById('qs-modal-overlay');
  const modalTitle = document.getElementById('qs-modal-title');
  const editIdInput = document.getElementById('qs-edit-id');
  const contextMenu = document.getElementById('qs-context-menu');
  const ctxEdit = document.getElementById('qs-ctx-edit');
  const ctxDelete = document.getElementById('qs-ctx-delete');
  const addToggle = document.getElementById('qs-add-toggle');
  const sideToggle = document.getElementById('qs-side-toggle');
  const expandToggle = document.getElementById('qs-expand-toggle');
  const titleInput = document.getElementById('qs-title-input');
  const urlInput = document.getElementById('qs-url-input');
  const colorInput = document.getElementById('qs-color-input');
  const solidInput = document.getElementById('qs-solid-input');
  const saveBtn = document.getElementById('qs-save-btn');
  const cancelBtn = document.getElementById('qs-cancel-btn');

  // Load state
  chrome.storage.sync.get(['sidebar_links', 'is_left', 'is_hidden'], (result) => {
    if (result.sidebar_links) links = result.sidebar_links;
    if (result.is_left !== undefined) isLeft = result.is_left;
    if (result.is_hidden !== undefined) isHidden = result.is_hidden;
    updateLayout();
    renderLinks();
  });

  // Event Listeners
  addToggle.addEventListener('click', () => {
    modalTitle.textContent = 'Add New Link';
    editIdInput.value = '';
    modalOverlay.classList.add('visible');
    titleInput.focus();
  });

  cancelBtn.addEventListener('click', () => {
    modalOverlay.classList.remove('visible');
    titleInput.value = '';
    urlInput.value = '';
  });

  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.classList.remove('visible');
      contextMenu.classList.remove('visible');
    }
  });

  // Close context menu on any click
  document.addEventListener('click', () => {
    contextMenu.classList.remove('visible');
  });

  sideToggle.addEventListener('click', () => {
    isLeft = !isLeft;
    chrome.storage.sync.set({ is_left: isLeft });
    updateLayout();
  });

  expandToggle.addEventListener('click', () => {
    isExpanded = !isExpanded;
    updateLayout();
  });

  saveBtn.addEventListener('click', () => {
    const title = titleInput.value.trim();
    let url = urlInput.value.trim();
    const color = colorInput.value;
    const isSolid = solidInput.checked;
    const editId = editIdInput.value;

    if (!url) return;
    if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

    const domain = new URL(url).hostname;

    if (editId) {
      links = links.map(l => l.id === editId ? {
        ...l,
        title: title || domain,
        url: url,
        color: color,
        isSolid: isSolid,
        icon: `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
      } : l);
    } else {
      links.push({
        id: Date.now().toString(),
        title: title || domain,
        url: url,
        color: color,
        isSolid: isSolid,
        icon: `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
      });
    }

    chrome.storage.sync.set({ sidebar_links: links });
    renderLinks();
    titleInput.value = '';
    urlInput.value = '';
    colorInput.value = '#38bdf8';
    solidInput.checked = false;
    editIdInput.value = '';
    modalOverlay.classList.remove('visible');
  });

  // Context Menu Actions
  let currentTargetId = null;

  ctxEdit.addEventListener('click', () => {
    const link = links.find(l => l.id === currentTargetId);
    if (link) {
      modalTitle.textContent = 'Edit Link';
      editIdInput.value = link.id;
      titleInput.value = link.title;
      urlInput.value = link.url;
      colorInput.value = link.color || '#38bdf8';
      solidInput.checked = link.isSolid || false;
      modalOverlay.classList.add('visible');
    }
    contextMenu.classList.remove('visible');
  });

  ctxDelete.addEventListener('click', () => {
    if (currentTargetId) {
      links = links.filter(l => l.id !== currentTargetId);
      chrome.storage.sync.set({ sidebar_links: links });
      renderLinks();
    }
    contextMenu.classList.remove('visible');
  });

  function renderLinks() {
    linksList.innerHTML = '';
    links.forEach(link => {
      const item = document.createElement('a');
      item.className = 'qs-link-item';
      item.href = link.url;
      item.title = link.title;
      item.draggable = true;

      if (link.color) {
        const bg = link.isSolid ? link.color : `${link.color}33`;
        item.style.setProperty('background', bg, 'important');
        item.style.setProperty('border-color', link.color, 'important');

        if (link.isSolid) {
          item.classList.add('qs-solid-item');
        } else {
          item.classList.remove('qs-solid-item');
        }
      }

      item.innerHTML = `
        <div class="qs-favicon">
          <img src="${link.icon}" onerror="this.src='https://www.google.com/s2/favicons?domain=google.com&sz=64'">
        </div>
        <div class="qs-link-text">${link.title}</div>
        <div class="qs-tooltip">${link.title}</div>
      `;

      // Drag and Drop Logic
      item.addEventListener('dragstart', (e) => {
        item.classList.add('qs-dragging');
        e.dataTransfer.setData('text/plain', link.id);
        e.dataTransfer.effectAllowed = 'move';
      });

      item.addEventListener('dragend', () => {
        item.classList.remove('qs-dragging');
        const draggingItems = document.querySelectorAll('.qs-dragging-over');
        draggingItems.forEach(el => el.classList.remove('qs-dragging-over'));
      });

      item.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        item.classList.add('qs-dragging-over');
      });

      item.addEventListener('dragleave', () => {
        item.classList.remove('qs-dragging-over');
      });

      item.addEventListener('drop', (e) => {
        e.preventDefault();
        item.classList.remove('qs-dragging-over');
        const draggedId = e.dataTransfer.getData('text/plain');
        if (draggedId === link.id) return;

        const draggedIndex = links.findIndex(l => l.id === draggedId);
        const targetIndex = links.findIndex(l => l.id === link.id);

        if (draggedIndex !== -1 && targetIndex !== -1) {
          const [draggedItem] = links.splice(draggedIndex, 1);
          links.splice(targetIndex, 0, draggedItem);
          chrome.storage.sync.set({ sidebar_links: links });
          renderLinks();
        }
      });

      item.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        currentTargetId = link.id;

        contextMenu.style.top = `${e.clientY}px`;
        const menuWidth = 100; // Expected width from CSS
        contextMenu.style.left = isLeft ? `${e.clientX}px` : `${e.clientX - menuWidth}px`;
        contextMenu.classList.add('visible');
      });

      linksList.appendChild(item);
    });
  }

  // Toggle visibility message
  chrome.runtime.onMessage.addListener((request) => {
    if (request.action === "toggle_sidebar") {
      isHidden = !isHidden;
      chrome.storage.sync.set({ is_hidden: isHidden });
      updateLayout();
    }
  });

  console.log("Quick Sidebar Pro: Injected successfully.");
})();
