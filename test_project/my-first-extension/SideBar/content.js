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
        <p class="qs-label">Backup & Restore</p>
        <div class="qs-settings-btns">
          <button id="qs-export-btn" class="qs-btn qs-secondary" style="margin-bottom: 10px; width: 100%;">Export Links (.json)</button>
          <button id="qs-import-btn" class="qs-btn qs-secondary" style="width: 100%;">Import Links (.json)</button>
          <input type="file" id="qs-import-file" style="display: none;" accept=".json">
        </div>
      </div>
      <div class="qs-actions">
        <button id="qs-settings-close" class="qs-btn qs-primary" style="width: 100%;">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(settingsOverlay);

  const settingsClose = document.getElementById('qs-settings-close');
  const exportBtn = document.getElementById('qs-export-btn');
  const importBtn = document.getElementById('qs-import-btn');
  const importFile = document.getElementById('qs-import-file');

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
        titleInput.value = '';
        urlInput.value = '';
        imgInput.value = '';
        colorInput.value = '#38bdf8';
        solidInput.checked = false;
      }
      overlay.classList.add('visible');
      titleInput.focus();
    } else if (request.action === 'open_settings') {
      settingsOverlay.classList.add('visible');
    }
  });

  // Export Logic
  exportBtn.onclick = () => {
    chrome.storage.sync.get(['sidebar_links'], (result) => {
      const links = result.sidebar_links || [];
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(links, null, 2));
      const downloadAnchorNode = document.createElement('a');
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute("download", "quicklinks_backup.json");
      document.body.appendChild(downloadAnchorNode);
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
    });
  };

  // Import Logic
  importBtn.onclick = () => importFile.click();
  importFile.onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const importedLinks = JSON.parse(event.target.result);
        if (Array.isArray(importedLinks)) {
          chrome.storage.sync.set({ sidebar_links: importedLinks }, () => {
            alert('Links imported successfully!');
            settingsOverlay.classList.remove('visible');
          });
        } else {
          alert('Invalid backup file format.');
        }
      } catch (err) {
        alert('Error parsing backup file.');
      }
    };
    reader.readAsText(file);
  };

  settingsClose.onclick = () => settingsOverlay.classList.remove('visible');
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
        icon: imgUrl || `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
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
