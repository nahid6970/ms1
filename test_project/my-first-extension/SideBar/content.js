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
      <div class="qs-group">
        <label class="qs-label">Image URL (Optional)</label>
        <input type="text" id="qs-img-input" class="qs-input" placeholder="https://... (Leave empty for default)">
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
  const imgInput = document.getElementById('qs-img-input');
  const colorInput = document.getElementById('qs-color-input');
  const solidInput = document.getElementById('qs-solid-input');
  const saveBtn = document.getElementById('qs-save');
  const cancelBtn = document.getElementById('qs-cancel');

  // Settings Modal
  const settingsOverlay = document.createElement('div');
  settingsOverlay.id = 'qs-settings-overlay';
  settingsOverlay.classList.add('qs-modal-overlay-custom'); // Reusing some base styles if possible
  settingsOverlay.innerHTML = `
    <div id="qs-settings-content" class="qs-modal-content-custom">
      <div class="qs-modal-title">Settings</div>
      <div class="qs-settings-section">
        <p class="qs-label">Display Settings</p>
        <div class="qs-group">
          <label class="qs-label">Items per Row: <span id="qs-items-value">4</span></label>
          <input type="range" id="qs-items-slider" class="qs-slider" min="2" max="8" value="4" step="1">
          <div class="qs-slider-labels">
            <span>2</span>
            <span>3</span>
            <span>4</span>
            <span>5</span>
            <span>6</span>
            <span>7</span>
            <span>8</span>
          </div>
        </div>
      </div>
      <div class="qs-actions">
        <button id="qs-settings-close" class="qs-btn qs-primary" style="width: 100%;">Save & Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(settingsOverlay);

  const settingsClose = document.getElementById('qs-settings-close');
  const itemsSlider = document.getElementById('qs-items-slider');
  const itemsValue = document.getElementById('qs-items-value');

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'open_modal') {
      const link = request.link;
      if (link) {
        titleText.textContent = 'Edit Link';
        editIdInput.value = link.id;
        titleInput.value = link.title;
        urlInput.value = link.url;
        // Check if the current icon is a google favicon. If not, it's a custom image.
        const isGoogleFavicon = link.icon && link.icon.includes('google.com/s2/favicons');
        imgInput.value = isGoogleFavicon ? '' : (link.icon || '');
        colorInput.value = link.color || '#38bdf8';
        solidInput.checked = link.isSolid || false;
      } else {
        titleText.textContent = 'New Link';
        editIdInput.value = '';
        titleInput.value = document.title || '';
        urlInput.value = window.location.href;
        imgInput.value = '';
        colorInput.value = '#38bdf8';
        solidInput.checked = false;
      }
      overlay.classList.add('visible');
      titleInput.focus();
    } else if (request.action === 'open_settings') {
      // Load current items per row setting
      chrome.storage.sync.get(['itemsPerRow'], (result) => {
        const itemsPerRow = result.itemsPerRow || 4;
        itemsSlider.value = itemsPerRow;
        itemsValue.textContent = itemsPerRow;
      });
      settingsOverlay.classList.add('visible');
    }
  });

  // Items per row slider
  itemsSlider.oninput = () => {
    itemsValue.textContent = itemsSlider.value;
  };

  // Save settings and close
  settingsClose.onclick = () => {
    const itemsPerRow = parseInt(itemsSlider.value);
    chrome.storage.sync.set({ itemsPerRow: itemsPerRow }, () => {
      settingsOverlay.classList.remove('visible');
      // Notify popup to update
      chrome.runtime.sendMessage({ action: 'settings_updated' });
    });
  };
  
  settingsOverlay.onclick = (e) => { if (e.target === settingsOverlay) settingsOverlay.classList.remove('visible'); };

  saveBtn.onclick = () => {
    const title = titleInput.value.trim();
    let url = urlInput.value.trim();
    const imgUrl = imgInput.value.trim();
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
        icon: imgUrl || `https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=${url}&size=64`
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
