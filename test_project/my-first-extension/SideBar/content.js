(function () {
  // Prevent multiple injections
  if (document.getElementById('qs-sidebar-root')) return;

  let links = [];
  let isLeft = false;
  let isExpanded = false;

  const root = document.createElement('div');
  root.id = 'qs-sidebar-root';
  root.className = 'right'; // Default to right
  document.documentElement.appendChild(root);

  function updatePageShift() {
    const isHidden = root.classList.contains('qs-hidden');
    const width = isExpanded ? 280 : 60;

    const html = document.documentElement;
    const body = document.body;

    if (isHidden) {
      html.style.setProperty('margin-left', '0', 'important');
      html.style.setProperty('margin-right', '0', 'important');
      html.style.setProperty('width', '100%', 'important');
      // Reset YouTube specific fixed header
      const ytHeader = document.querySelector('#masthead-container');
      if (ytHeader) ytHeader.style.setProperty('left', '0', 'important');
    } else {
      html.style.setProperty('width', `calc(100% - ${width}px)`, 'important');
      if (isLeft) {
        html.style.setProperty('margin-left', `${width}px`, 'important');
        html.style.setProperty('margin-right', '0', 'important');

        // Push YouTube's fixed header
        const ytHeader = document.querySelector('#masthead-container');
        if (ytHeader) ytHeader.style.setProperty('left', `${width}px`, 'important');
      } else {
        html.style.setProperty('margin-left', '0', 'important');
        html.style.setProperty('margin-right', `${width}px`, 'important');

        // Reset YouTube header (it stays anchored to left normally)
        const ytHeader = document.querySelector('#masthead-container');
        if (ytHeader) ytHeader.style.setProperty('left', '0', 'important');
      }
    }
  }

  function updateLayout() {
    root.className = (isLeft ? 'left' : 'right') + (isExpanded ? ' expanded' : '');

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
      <div class="qs-logo">S</div>
      <div class="qs-actions">
        <button id="qs-add-toggle" class="qs-icon-btn" title="Add Link">
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" /></svg>
        </button>
        <button id="qs-side-toggle" class="qs-icon-btn" title="Toggle Left/Right">
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M15,5V11H21V5M10,11H15V5H10M16,18H21V12H16M10,18H15V12H10M4,18H9V12H4M4,11H9V5H4V11Z" /></svg>
        </button>
        <button id="qs-expand-toggle" class="qs-icon-btn" title="Expand/Collapse">
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M14,14H19V16H14V14M14,10H19V12H14V10M14,6H19V8H14V6M5,6H9V8H5V6M5,10H9V12H5V10M5,14H9V16H5V14Z" /></svg>
        </button>
      </div>
    </div>
    
    <div id="qs-add-form">
      <input type="text" id="qs-title-input" placeholder="Title">
      <input type="text" id="qs-url-input" placeholder="URL">
      <div class="qs-form-btns">
        <button id="qs-save-btn" class="qs-btn-primary">Save</button>
      </div>
    </div>

    <div id="qs-links-list"></div>
  `;

  const linksList = document.getElementById('qs-links-list');
  const addForm = document.getElementById('qs-add-form');
  const addToggle = document.getElementById('qs-add-toggle');
  const sideToggle = document.getElementById('qs-side-toggle');
  const expandToggle = document.getElementById('qs-expand-toggle');
  const titleInput = document.getElementById('qs-title-input');
  const urlInput = document.getElementById('qs-url-input');
  const saveBtn = document.getElementById('qs-save-btn');

  // Load state
  chrome.storage.sync.get(['sidebar_links', 'is_left'], (result) => {
    if (result.sidebar_links) links = result.sidebar_links;
    if (result.is_left !== undefined) isLeft = result.is_left;
    updateLayout();
    renderLinks();
  });

  // Event Listeners
  addToggle.addEventListener('click', () => {
    addForm.classList.toggle('visible');
    if (addForm.classList.contains('visible') && !isExpanded) {
      isExpanded = true;
      updateLayout();
    }
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

    if (!url) return;
    if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

    const domain = new URL(url).hostname;
    const newLink = {
      id: Date.now().toString(),
      title: title || domain,
      url: url,
      icon: `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
    };

    links.push(newLink);
    chrome.storage.sync.set({ sidebar_links: links });
    renderLinks();
    titleInput.value = '';
    urlInput.value = '';
    addForm.classList.remove('visible');
  });

  function renderLinks() {
    linksList.innerHTML = '';
    links.forEach(link => {
      const item = document.createElement('a');
      item.className = 'qs-link-item';
      item.href = link.url;
      item.target = '_blank';
      item.title = link.title;

      item.innerHTML = `
        <div class="qs-favicon">
          <img src="${link.icon}" onerror="this.src='https://www.google.com/s2/favicons?domain=google.com&sz=64'">
        </div>
        <div class="qs-link-text">${link.title}</div>
        <div class="qs-tooltip">${link.title}</div>
        <div class="qs-delete-btn" data-id="${link.id}">×</div>
      `;

      const delBtn = item.querySelector('.qs-delete-btn');
      delBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const id = delBtn.getAttribute('data-id');
        links = links.filter(l => l.id !== id);
        chrome.storage.sync.set({ sidebar_links: links });
        renderLinks();
      });

      linksList.appendChild(item);
    });
  }

  // Toggle visibility message
  chrome.runtime.onMessage.addListener((request) => {
    if (request.action === "toggle_sidebar") {
      const isHidden = root.classList.contains('qs-hidden');
      if (isHidden) {
        root.classList.remove('qs-hidden');
        root.style.transform = "translateX(0)";
      } else {
        root.classList.add('qs-hidden');
        root.style.transform = isLeft ? "translateX(-110%)" : "translateX(110%)";
      }
      updatePageShift();
    }
  });

  console.log("Quick Sidebar Pro: Injected successfully.");
})();
