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
            Solid
          </label>
        </div>
        <div class="qs-style-field">
          <label class="qs-checkbox">
            <input type="checkbox" id="qs-newline-input">
            New Line
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
  const newLineInput = document.getElementById('qs-newline-input');
  const saveBtn = document.getElementById('qs-save');
  const cancelBtn = document.getElementById('qs-cancel');

  // Settings Modal
  const settingsOverlay = document.createElement('div');
  settingsOverlay.id = 'qs-settings-overlay';
  settingsOverlay.innerHTML = `
    <div id="qs-settings-content">
      <div class="qs-modal-title">Settings</div>
      <div class="qs-settings-section">
        <p class="qs-label">Display Settings</p>
        <div class="qs-group">
          <label class="qs-label">Items per Row: <span id="qs-items-value">4</span></label>
          <input type="range" id="qs-items-slider" class="qs-slider" min="2" max="8" value="4" step="1">
          <div class="qs-slider-labels">
            <span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span>
          </div>
        </div>
        <div class="qs-group" style="margin-top: 16px;">
          <label class="qs-label">Extra Padding (px): <span id="qs-padding-value">20</span></label>
          <input type="range" id="qs-padding-slider" class="qs-slider" min="0" max="50" value="20" step="2">
        </div>
        
        <p class="qs-label" style="margin-top: 24px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 16px;">Icon Style</p>
        
        <div class="qs-group">
          <label class="qs-label">Icon Size: <span id="qs-icon-size-value">28</span>px</label>
          <input type="range" id="qs-icon-size-slider" class="qs-slider" min="16" max="56" value="28" step="2">
        </div>

        <div class="qs-group">
          <label class="qs-label">Border Radius: <span id="qs-radius-value">8</span>px</label>
          <input type="range" id="qs-radius-slider" class="qs-slider" min="0" max="28" value="8" step="1">
        </div>

        <div class="qs-group">
          <label class="qs-label">Border Opacity: <span id="qs-opacity-value">100</span>%</label>
          <input type="range" id="qs-opacity-slider" class="qs-slider" min="0" max="100" value="100" step="5">
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
  const paddingSlider = document.getElementById('qs-padding-slider');
  const paddingValue = document.getElementById('qs-padding-value');
  
  const iconSizeSlider = document.getElementById('qs-icon-size-slider');
  const iconSizeValue = document.getElementById('qs-icon-size-value');
  const radiusSlider = document.getElementById('qs-radius-slider');
  const radiusValue = document.getElementById('qs-radius-value');
  const opacitySlider = document.getElementById('qs-opacity-slider');
  const opacityValue = document.getElementById('qs-opacity-value');

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'open_modal') {
      const link = request.link;
      if (link) {
        titleText.textContent = 'Edit Link';
        editIdInput.value = link.id;
        titleInput.value = link.title;
        urlInput.value = link.url;
        const isGoogleFavicon = link.icon && link.icon.includes('google.com/s2/favicons');
        imgInput.value = isGoogleFavicon ? '' : (link.icon || '');
        colorInput.value = link.color || '#38bdf8';
        solidInput.checked = link.isSolid || false;
        newLineInput.checked = link.newLine || false;
      } else {
        titleText.textContent = 'New Link';
        editIdInput.value = '';
        titleInput.value = document.title || '';
        urlInput.value = window.location.href;
        colorInput.value = '#38bdf8';
        solidInput.checked = false;
        newLineInput.checked = false;
        chrome.runtime.sendMessage({ action: 'getSmartFavicon', url: window.location.href }, (icon) => {
          if (icon) imgInput.value = icon;
        });
      }
      overlay.classList.add('visible');
      titleInput.focus();
    } else if (request.action === 'open_settings') {
      chrome.storage.local.get(['itemsPerRow', 'extraPadding', 'iconSize', 'borderRadius', 'borderOpacity'], (result) => {
        itemsSlider.value = result.itemsPerRow || 4;
        itemsValue.textContent = itemsSlider.value;
        paddingSlider.value = result.extraPadding || 20;
        paddingValue.textContent = paddingSlider.value;
        
        iconSizeSlider.value = result.iconSize || 28;
        iconSizeValue.textContent = iconSizeSlider.value;
        radiusSlider.value = result.borderRadius !== undefined ? result.borderRadius : 8;
        radiusValue.textContent = radiusSlider.value;
        opacitySlider.value = result.borderOpacity !== undefined ? result.borderOpacity : 100;
        opacityValue.textContent = opacitySlider.value;
      });
      settingsOverlay.classList.add('visible');
    }
  });

  itemsSlider.oninput = () => itemsValue.textContent = itemsSlider.value;
  paddingSlider.oninput = () => paddingValue.textContent = paddingSlider.value;
  iconSizeSlider.oninput = () => iconSizeValue.textContent = iconSizeSlider.value;
  radiusSlider.oninput = () => radiusValue.textContent = radiusSlider.value;
  opacitySlider.oninput = () => opacityValue.textContent = opacitySlider.value;

  settingsClose.onclick = () => {
    const settings = {
      itemsPerRow: parseInt(itemsSlider.value),
      extraPadding: parseInt(paddingSlider.value),
      iconSize: parseInt(iconSizeSlider.value),
      borderRadius: parseInt(radiusSlider.value),
      borderOpacity: parseInt(opacitySlider.value)
    };
    chrome.storage.local.set(settings, () => {
      settingsOverlay.classList.remove('visible');
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
    const newLine = newLineInput.checked;
    const editId = editIdInput.value;

    if (!url) return;
    if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

    let domain = '';
    try { domain = new URL(url).hostname; } catch (e) { return; }

    chrome.storage.local.get(['sidebar_links'], (result) => {
      let links = result.sidebar_links || [];
      const linkData = {
        title: title || domain,
        url: url,
        color: color,
        isSolid: isSolid,
        newLine: newLine,
        icon: imgUrl || `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
      };

      if (editId) {
        links = links.map(l => l.id === editId ? { ...l, ...linkData } : l);
      } else {
        links.push({ id: Date.now().toString(), ...linkData });
      }

      chrome.storage.local.set({ sidebar_links: links }, () => {
        overlay.classList.remove('visible');
      });
    });
  };

  cancelBtn.onclick = () => overlay.classList.remove('visible');
  overlay.onclick = (e) => { if (e.target === overlay) overlay.classList.remove('visible'); };
})();