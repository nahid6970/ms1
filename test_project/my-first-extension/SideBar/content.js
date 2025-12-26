(function () {
  if (document.getElementById('qs-modal-overlay')) return;

  const overlay = document.createElement('div');
  overlay.id = 'qs-modal-overlay';
  overlay.innerHTML = `
    <div id="qs-modal-content">
      <div class="qs-modal-title" id="qs-title-text">New Link</div>
      <input type="hidden" id="qs-edit-id">
      <div class="qs-group">
        <label class="qs-label">Title</label>
        <input type="text" id="qs-title-input" class="qs-input" placeholder="e.g. GitHub">
      </div>
      <div class="qs-group">
        <label class="qs-label">URL</label>
        <input type="text" id="qs-url-input" class="qs-input" placeholder="https://...">
      </div>
      <div class="qs-group qs-style-row">
        <div class="qs-style-field">
          <label class="qs-label">Color</label>
          <input type="color" id="qs-color-input" class="qs-color-btn" value="#38bdf8">
        </div>
        <div class="qs-style-field">
          <label class="qs-checkbox">
            <input type="checkbox" id="qs-solid-input">
            <span class="qs-check-mark"></span>
            Solid
          </label>
        </div>
      </div>
      <div class="qs-actions">
        <button id="qs-cancel" class="qs-btn qs-secondary">Cancel</button>
        <button id="qs-save" class="qs-btn qs-primary">Save Link</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const titleText = document.getElementById('qs-title-text');
  const editIdInput = document.getElementById('qs-edit-id');
  const titleInput = document.getElementById('qs-title-input');
  const urlInput = document.getElementById('qs-url-input');
  const colorInput = document.getElementById('qs-color-input');
  const solidInput = document.getElementById('qs-solid-input');
  const saveBtn = document.getElementById('qs-save');
  const cancelBtn = document.getElementById('qs-cancel');

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'open_modal') {
      const link = request.link;
      if (link) {
        titleText.textContent = 'Edit Link';
        editIdInput.value = link.id;
        titleInput.value = link.title;
        urlInput.value = link.url;
        colorInput.value = link.color || '#38bdf8';
        solidInput.checked = link.isSolid || false;
      } else {
        titleText.textContent = 'New Link';
        editIdInput.value = '';
        titleInput.value = '';
        urlInput.value = '';
        colorInput.value = '#38bdf8';
        solidInput.checked = false;
      }
      overlay.classList.add('visible');
      titleInput.focus();
    }
  });

  saveBtn.onclick = () => {
    const title = titleInput.value.trim();
    let url = urlInput.value.trim();
    const color = colorInput.value;
    const isSolid = solidInput.checked;
    const editId = editIdInput.value;

    if (!url) return;
    if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

    let domain = '';
    try { domain = new URL(url).hostname; } catch (e) { return; }

    chrome.storage.sync.get(['sidebar_links'], (result) => {
      let links = result.sidebar_links || [];
      const linkData = {
        title: title || domain,
        url: url,
        color: color,
        isSolid: isSolid,
        icon: `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
      };

      if (editId) {
        links = links.map(l => l.id === editId ? { ...l, ...linkData } : l);
      } else {
        links.push({ id: Date.now().toString(), ...linkData });
      }

      chrome.storage.sync.set({ sidebar_links: links }, () => {
        overlay.classList.remove('visible');
      });
    });
  };

  cancelBtn.onclick = () => overlay.classList.remove('visible');
  overlay.onclick = (e) => { if (e.target === overlay) overlay.classList.remove('visible'); };
})();
