document.addEventListener('DOMContentLoaded', () => {
  const addBtn = document.getElementById('add-btn');
  const addForm = document.getElementById('add-form');
  const saveBtn = document.getElementById('save-btn');
  const cancelBtn = document.getElementById('cancel-btn');
  const titleInput = document.getElementById('link-title');
  const urlInput = document.getElementById('link-url');
  const linksContainer = document.getElementById('links-container');
  const emptyState = document.getElementById('empty-state');
  const viewToggle = document.getElementById('view-toggle');

  let links = [];
  let isCompact = false;

  // Load links and view mode from storage
  chrome.storage.sync.get(['sidebar_links', 'is_compact'], (result) => {
    if (result.sidebar_links) {
      links = result.sidebar_links;
    }
    if (result.is_compact !== undefined) {
      isCompact = result.is_compact;
      if (isCompact) linksContainer.classList.add('compact');
    }
    renderLinks();
  });

  // Toggle view mode
  viewToggle.addEventListener('click', () => {
    isCompact = !isCompact;
    linksContainer.classList.toggle('compact');
    chrome.storage.sync.set({ is_compact: isCompact });
  });

  // Toggle form
  addBtn.addEventListener('click', () => {
    addForm.classList.toggle('hidden');
    if (!addForm.classList.contains('hidden')) {
      titleInput.focus();
    }
  });

  cancelBtn.addEventListener('click', () => {
    addForm.classList.add('hidden');
    clearForm();
  });

  // Save new link
  saveBtn.addEventListener('click', () => {
    const title = titleInput.value.trim();
    let url = urlInput.value.trim();

    if (!url) return;

    // Basic URL validation/fixing
    if (!/^https?:\/\//i.test(url)) {
      url = 'https://' + url;
    }

    const newLink = {
      id: Date.now().toString(),
      title: title || new URL(url).hostname,
      url: url,
      icon: getIconUrl(url)
    };

    links.push(newLink);
    saveLinks();
    renderLinks();
    addForm.classList.add('hidden');
    clearForm();
  });

  function clearForm() {
    titleInput.value = '';
    urlInput.value = '';
  }

  function saveLinks() {
    chrome.storage.sync.set({ sidebar_links: links });
  }

  function getIconUrl(url) {
    try {
      const domain = new URL(url).hostname;
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=64`;
    } catch (e) {
      return 'icons/icon48.png'; // Fallback
    }
  }

  function renderLinks() {
    linksContainer.innerHTML = '';

    if (links.length === 0) {
      emptyState.classList.remove('hidden');
      return;
    }

    emptyState.classList.add('hidden');

    links.forEach(link => {
      const linkEl = document.createElement('div');
      linkEl.className = 'link-item-container'; // Wrapper for layout if needed

      linkEl.innerHTML = `
        <a href="${link.url}" target="_blank" class="link-item" title="${link.title}">
          <div class="favicon-wrapper">
            <img src="${link.icon}" alt="" onerror="this.src='icons/icon48.png'">
          </div>
          <div class="link-info">
            <div class="link-title">${link.title}</div>
            <div class="link-url">${link.url}</div>
          </div>
          <button class="delete-btn" data-id="${link.id}" title="Delete Link">
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19V4M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" />
            </svg>
          </button>
        </a>
      `;

      // Handle delete
      const deleteBtn = linkEl.querySelector('.delete-btn');
      deleteBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const id = deleteBtn.getAttribute('data-id');
        links = links.filter(l => l.id !== id);
        saveLinks();
        renderLinks();
      });

      linksContainer.appendChild(linkEl);
    });
  }
});
