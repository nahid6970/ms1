document.addEventListener('DOMContentLoaded', () => {
  const scriptListDiv = document.getElementById('scriptList');
  const statusText = document.getElementById('statusText');
  const fallbackScriptPath = 'user_scripts/local_server_fallback.js';
  const defaultFallbackSettings = {
    localServerUrl: 'http://192.168.0.101:5000/',
    siteUrl: 'https://nahid6970.github.io/db/5000_myhome/myhome',
    mode: 'local'
  };

  function normalizeSettings(settings = {}) {
    return {
      localServerUrl: (settings.localServerUrl || defaultFallbackSettings.localServerUrl).trim(),
      siteUrl: (settings.siteUrl || defaultFallbackSettings.siteUrl).trim(),
      mode: ['local', 'site', 'chrome'].includes(settings.mode) ? settings.mode : defaultFallbackSettings.mode
    };
  }

  // Get all scripts from user_scripts folder
  async function getAvailableScripts() {
    const scripts = [];
    
    try {
      // Try to get directory listing
      const response = await fetch(chrome.runtime.getURL('user_scripts/'));
      const text = await response.text();
      
      // Parse directory listing to find .js files
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, 'text/html');
      const links = doc.querySelectorAll('a[href$=".js"]');
      
      links.forEach(link => {
        const fileName = link.href.split('/').pop();
        scripts.push(`user_scripts/${fileName}`);
      });
      
      return scripts;
    } catch (error) {
      console.log('Directory listing not available, using alternative method');
      
      // Alternative: Use chrome.runtime.getPackageDirectoryEntry (for unpacked extensions)
      if (chrome.runtime.getPackageDirectoryEntry) {
        return new Promise((resolve) => {
          chrome.runtime.getPackageDirectoryEntry((root) => {
            root.getDirectory('user_scripts', {}, (dirEntry) => {
              const reader = dirEntry.createReader();
              reader.readEntries((entries) => {
                const jsFiles = entries
                  .filter(entry => entry.isFile && entry.name.endsWith('.js'))
                  .map(entry => `user_scripts/${entry.name}`);
                resolve(jsFiles);
              });
            }, () => resolve([]));
          });
        });
      }
      
      // Final fallback: Return empty array
      return [];
    }
  }

  // Generate user-friendly names and descriptions
  function generateScriptInfo(scriptPath) {
    const fileName = scriptPath.split('/').pop();
    const scriptName = fileName.replace('.js', '').replace(/[_-]/g, ' ');
    
    // Capitalize first letter of each word
    const displayName = scriptName.split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    // Generate description based on filename
    const descriptions = {
      'disable_youtube': 'Disable YouTube - Redirects to Google',
      'youtube_ad_skipper': 'YouTube Ad Skipper - Skip/speed up ads',
      'auto_clicker': 'Auto Clicker - Automated clicking functionality',
      'page_monitor': 'Page Monitor - Track page changes',
      'form_filler': 'Form Filler - Auto-fill form fields',
      'link_preview': 'Link Preview - Preview links on hover',
      'scroll_enhancer': 'Scroll Enhancer - Smooth scrolling improvements',
      'password_generator': 'Password Generator - Generate secure passwords',
      'tab_manager': 'Tab Manager - Enhanced tab management',
      'image_lazy_loader': 'Image Lazy Loader - Optimize image loading',
      'notification_blocker': 'Notification Blocker - Block unwanted notifications',
      'theme_switcher': 'Theme Switcher - Quick theme changes',
      'open_links_in_new_tab': 'Open Links in New Tab - Forced new tab on left-click',
      'open_local_files_in_new_tab': 'Open Local Files in New Tab - Opens local file links in a new tab',
      'checkbox_auto_checker': 'Checkbox Auto Checker - Auto-checks all visible checkboxes when any checkbox is pressed',
      'form_draft_saver': 'Form Draft Saver - Automatically saves and restores typed form inputs',
      'copy_table_as_markdown': 'Copy Table As Markdown - Shows a button on table hover to copy HTML tables as Markdown',
      'link_text_extractor': 'Link Text Extractor - Copies the text of a link to your clipboard when holding Ctrl and clicking',
      'ai_studio_quick_delete': 'AI Studio Quick Tools - Delete, copy code blocks & bookmark turns in Google AI Studio',
      'youtube_swap_sections': 'YouTube Swap Sections - Swaps comments & video sidebar (Shortcut: Shift+F)',
      'element_hider': 'Element Hider - Hide any page element by port; click 👁 to pick elements visually',
      'force_visible_cursor': 'Force Visible Cursor - Restore the normal cursor when a page hides it'
    };
    
    const baseDescription = descriptions[scriptName.replace(/\s+/g, '_').toLowerCase()];
    return {
      name: displayName,
      description: baseDescription || `${displayName} - Custom user script`
    };
  }

  function createScriptItem(scriptPath, isEnabled, fallbackSettings, whitelistSettings, ytAnalyzerHotkey, elementHiderRules, cursorStyle, cursorColor, cursorSize, cursorTargets) {
    const scriptInfo = generateScriptInfo(scriptPath);
    const isFallbackScript = scriptPath === fallbackScriptPath;
    const isWhitelistScript = scriptPath === 'user_scripts/open_links_in_new_tab.js';
    const isYtAnalyzer = scriptPath === 'user_scripts/yt_analyzer.js';
    const isElementHider = scriptPath === 'user_scripts/element_hider.js';
    const isVisibleCursor = scriptPath === 'user_scripts/force_visible_cursor.js';
    
    const modeLabels = {
      local: 'LOCAL',
      site: 'SITE',
      chrome: 'CHROME'
    };
    const modeLabel = modeLabels[fallbackSettings.mode] || 'LOCAL';

    const scriptItem = document.createElement('div');
    scriptItem.className = `script-item ${isEnabled ? 'enabled' : 'disabled'}`;
    scriptItem.dataset.scriptPath = scriptPath;

    scriptItem.innerHTML = `
      <div class="script-main">
        <div class="script-info">
          <div class="script-icon">${isEnabled ? '✓' : '○'}</div>
          <div class="script-details">
            <div class="script-name">${scriptInfo.name}</div>
            <div class="script-desc">${scriptInfo.description}</div>
          </div>
        </div>
        <div class="script-actions">
          ${(isFallbackScript || isWhitelistScript || isYtAnalyzer || isElementHider || isVisibleCursor) ? `<button class="settings-btn" data-script="${scriptPath}" aria-expanded="false">SET</button>` : ''}
          ${isFallbackScript ? `<button class="mode-btn ${fallbackSettings.mode}" data-script="${scriptPath}">${modeLabel}</button>` : ''}
          <button class="toggle-btn ${isEnabled ? 'active' : 'inactive'}" data-script="${scriptPath}">
            ${isEnabled ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>
    `;

    if (isFallbackScript) {
      const fallbackSettingsDiv = document.createElement('div');
      fallbackSettingsDiv.className = 'fallback-settings hidden';
      fallbackSettingsDiv.innerHTML = `
        <label class="settings-label" for="localServerUrl">Local server URL</label>
        <input id="localServerUrl" class="settings-input" type="url" value="${fallbackSettings.localServerUrl}" placeholder="http://127.0.0.1:5000/">
        <label class="settings-label" for="siteUrl">Site URL</label>
        <input id="siteUrl" class="settings-input" type="url" value="${fallbackSettings.siteUrl}" placeholder="https://example.com">
        <div class="settings-hint">Mode LOCAL = try server first. Mode SITE = always open site URL. Mode CHROME = use Chrome's default new tab page.</div>
      `;
      scriptItem.appendChild(fallbackSettingsDiv);
    } else if (isWhitelistScript) {
      const whitelistSettingsDiv = document.createElement('div');
      whitelistSettingsDiv.className = 'fallback-settings hidden';
      whitelistSettingsDiv.innerHTML = `
        <label class="settings-label" for="domainWhitelist">Whitelisted Domains (comma separated)</label>
        <input id="domainWhitelist" class="settings-input" type="text" value="${whitelistSettings || ''}" placeholder="example.com, google.com">
        <div class="settings-hint">Leave empty to work on all sites.</div>
      `;
      scriptItem.appendChild(whitelistSettingsDiv);
    } else if (isYtAnalyzer) {
      const ytSettingsDiv = document.createElement('div');
      ytSettingsDiv.className = 'fallback-settings hidden';
      ytSettingsDiv.innerHTML = `
        <label class="settings-label" for="ytHotkeyInput">Hotkey (click then press a key)</label>
        <input id="ytHotkeyInput" class="settings-input" type="text" value="${ytAnalyzerHotkey || 'F9'}" placeholder="F9" readonly>
        <div class="settings-hint">Click the field and press any key to set the shortcut.</div>
      `;
      scriptItem.appendChild(ytSettingsDiv);
    } else if (isElementHider) {
      // Build a per-port rules table from elementHiderRules
      const rules = elementHiderRules || {};
      const portEntries = Object.entries(rules);

      let rulesHtml = '';
      if (portEntries.length === 0) {
        rulesHtml = '<div class="settings-hint" style="margin-top:4px;">No rules yet. Enable the script and use the 👁 button on any page to pick elements.</div>';
      } else {
        rulesHtml = portEntries.map(([port, portRule]) => {
          const selectors = (portRule.selectors || []).join('\n');
          const isOn = portRule.enabled !== false;
          return `
            <div class="eh-port-block" data-port="${port}" style="margin-bottom:10px;">
              <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                <span class="settings-label" style="flex:1;">Port ${port}</span>
                <button class="eh-port-toggle toggle-btn ${isOn ? 'active' : 'inactive'}" data-port="${port}" style="padding:3px 8px;min-width:36px;font-size:10px;">${isOn ? 'ON' : 'OFF'}</button>
                <button class="eh-port-clear toggle-btn inactive" data-port="${port}" style="padding:3px 8px;min-width:46px;font-size:10px;">CLEAR</button>
              </div>
              <textarea class="settings-input eh-selectors-input" data-port="${port}" rows="3" placeholder="CSS selectors (one per line)" style="resize:vertical;">${selectors}</textarea>
            </div>
          `;
        }).join('');
      }

      const ehSettingsDiv = document.createElement('div');
      ehSettingsDiv.className = 'fallback-settings hidden';
      ehSettingsDiv.innerHTML = `
        <div class="settings-hint" style="margin-bottom:6px;">Rules are created automatically when you pick elements on a page. You can also edit selectors manually below.</div>
        <div id="ehPortRules">${rulesHtml}</div>
      `;
      scriptItem.appendChild(ehSettingsDiv);
    } else if (isVisibleCursor) {
      const targetEntries = (cursorTargets || []).map((target, index) => `
        <div style="display:flex;align-items:center;gap:6px;margin:5px 0;">
          <span class="settings-hint" style="flex:1;overflow-wrap:anywhere;">${target.host}: ${target.selector}</span>
          <button class="cursor-target-remove toggle-btn inactive" data-index="${index}" style="min-width:48px;padding:3px 7px;">REMOVE</button>
        </div>`).join('');
      const cursorSettingsDiv = document.createElement('div');
      cursorSettingsDiv.className = 'fallback-settings hidden';
      cursorSettingsDiv.innerHTML = `
        <label class="settings-label" for="visibleCursorStyle">Cursor shown over the page</label>
        <select id="visibleCursorStyle" class="settings-input">
          <option value="arrow" ${cursorStyle === 'arrow' ? 'selected' : ''}>Arrow</option>
          <option value="crosshair" ${cursorStyle === 'crosshair' ? 'selected' : ''}>Crosshair</option>
          <option value="dot" ${cursorStyle === 'dot' ? 'selected' : ''}>Dot</option>
        </select>
        <label class="settings-label" for="visibleCursorColor">Cursor color</label>
        <input id="visibleCursorColor" class="settings-input" type="color" value="${cursorColor}">
        <label class="settings-label" for="visibleCursorSize">Cursor size: <span id="visibleCursorSizeValue">${cursorSize}%</span></label>
        <input id="visibleCursorSize" class="settings-input" type="range" min="60" max="200" step="10" value="${cursorSize}">
        <label class="settings-label">Target elements (optional)</label>
        <button class="settings-btn cursor-target-pick" type="button">PICK ELEMENT ON PAGE</button>
        <div class="settings-hint">${targetEntries ? 'When this site has targets, the overlay is limited to them.' : 'No targets saved. The overlay works across the whole page.'}</div>
        <div class="cursor-target-list">${targetEntries}</div>
        <div class="settings-hint">These settings update the pointer overlay while this script is enabled.</div>
      `;
      scriptItem.appendChild(cursorSettingsDiv);
    }

    return scriptItem;
  }

  function updateStatus(enabledScripts, totalScripts) {
    const enabledCount = Object.values(enabledScripts).filter(Boolean).length;
    statusText.textContent = `${enabledCount}/${totalScripts} script${totalScripts !== 1 ? 's' : ''} enabled`;
  }

  function toggleScript(scriptPath, currentState) {
    const newState = !currentState;
    
    chrome.storage.local.get(['enabledScripts'], (result) => {
      const enabledScripts = result.enabledScripts || {};
      enabledScripts[scriptPath] = newState;
      
      chrome.storage.local.set({ enabledScripts }, () => {
        console.log(`Script ${scriptPath} ${newState ? 'enabled' : 'disabled'}`);
        if (newState && scriptPath === 'user_scripts/force_visible_cursor.js') {
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const tab = tabs[0];
            if (!tab?.id || !/^https?:/.test(tab.url || '')) return;
            chrome.scripting.executeScript({
              target: { tabId: tab.id },
              files: [scriptPath]
            }).catch((error) => console.error(`Failed to inject ${scriptPath}:`, error));
          });
        }
        loadScriptList(); // Refresh the UI
      });
    });
  }

  function saveFallbackSettings(settings) {
    const normalized = normalizeSettings(settings);
    chrome.storage.local.set({ fallbackSettings: normalized }, () => {
      console.log('Fallback settings saved:', normalized);
    });
  }

  function saveWhitelistSettings(whitelist) {
    chrome.storage.local.set({ domainWhitelist: whitelist }, () => {
      console.log('Whitelist settings saved:', whitelist);
    });
  }

  function toggleFallbackMode(currentSettings) {
    const modeOrder = ['local', 'site', 'chrome'];
    const currentIndex = modeOrder.indexOf(currentSettings.mode);
    const nextMode = modeOrder[(currentIndex + 1) % modeOrder.length];
    saveFallbackSettings({
      ...currentSettings,
      mode: nextMode
    });
    loadScriptList();
  }

  function saveElementHiderRules(rules) {
    chrome.storage.local.set({ element_hider_rules: rules }, () => {
      console.log('Element hider rules saved:', rules);
    });
  }

  function attachSettingsHandlers(scriptItem, fallbackSettings, whitelistSettings, cursorTargets) {
    const localServerInput = scriptItem.querySelector('#localServerUrl');
    const siteUrlInput = scriptItem.querySelector('#siteUrl');
    const domainWhitelistInput = scriptItem.querySelector('#domainWhitelist');
    const ytHotkeyInput = scriptItem.querySelector('#ytHotkeyInput');
    const visibleCursorStyle = scriptItem.querySelector('#visibleCursorStyle');
    const visibleCursorColor = scriptItem.querySelector('#visibleCursorColor');
    const visibleCursorSize = scriptItem.querySelector('#visibleCursorSize');
    const visibleCursorSizeValue = scriptItem.querySelector('#visibleCursorSizeValue');
    const modeButton = scriptItem.querySelector('.mode-btn');
    const settingsButton = scriptItem.querySelector('.settings-btn');
    const settingsPanel = scriptItem.querySelector('.fallback-settings');

    if (settingsButton && settingsPanel) {
      settingsButton.addEventListener('click', () => {
        const isHidden = settingsPanel.classList.toggle('hidden');
        settingsButton.textContent = isHidden ? 'SET' : 'CLOSE';
        settingsButton.setAttribute('aria-expanded', String(!isHidden));
      });
    }

    if (localServerInput) {
      localServerInput.addEventListener('change', () => {
        saveFallbackSettings({
          ...fallbackSettings,
          localServerUrl: localServerInput.value
        });
      });
    }

    if (siteUrlInput) {
      siteUrlInput.addEventListener('change', () => {
        saveFallbackSettings({
          ...fallbackSettings,
          siteUrl: siteUrlInput.value
        });
      });
    }

    if (domainWhitelistInput) {
      domainWhitelistInput.addEventListener('change', () => {
        saveWhitelistSettings(domainWhitelistInput.value);
      });
    }

    if (ytHotkeyInput) {
      ytHotkeyInput.addEventListener('keydown', (e) => {
        e.preventDefault();
        const key = e.key;
        ytHotkeyInput.value = key;
        chrome.storage.local.set({ ytAnalyzerHotkey: key });
      });
    }

    if (visibleCursorStyle) {
      visibleCursorStyle.addEventListener('change', () => {
        chrome.storage.local.set({ visibleCursorStyle: visibleCursorStyle.value });
      });
    }

    if (visibleCursorColor) {
      visibleCursorColor.addEventListener('input', () => {
        chrome.storage.local.set({ visibleCursorColor: visibleCursorColor.value });
      });
    }

    if (visibleCursorSize) {
      visibleCursorSize.addEventListener('input', () => {
        visibleCursorSizeValue.textContent = `${visibleCursorSize.value}%`;
        chrome.storage.local.set({ visibleCursorSize: Number(visibleCursorSize.value) });
      });
    }

    const pickCursorTargetButton = scriptItem.querySelector('.cursor-target-pick');
    if (pickCursorTargetButton) {
      pickCursorTargetButton.addEventListener('click', () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          const tab = tabs[0];
          if (!tab?.id || !/^https?:/.test(tab.url || '')) return;
          chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: activateCursorTargetPicker
          }).catch((error) => console.error('Failed to start cursor target picker:', error));
        });
      });
    }

    scriptItem.querySelectorAll('.cursor-target-remove').forEach((button) => {
      button.addEventListener('click', () => {
        const nextTargets = (cursorTargets || []).filter((_, index) => index !== Number(button.dataset.index));
        chrome.storage.local.set({ visibleCursorTargets: nextTargets }, loadScriptList);
      });
    });

    if (modeButton) {
      modeButton.addEventListener('click', () => {
        toggleFallbackMode(fallbackSettings);
      });
    }

    // ── Element Hider handlers ──────────────────────────────────────────────
    // Selector textarea edits
    scriptItem.querySelectorAll('.eh-selectors-input').forEach(textarea => {
      textarea.addEventListener('change', () => {
        const port = textarea.dataset.port;
        const selectors = textarea.value.split('\n').map(s => s.trim()).filter(Boolean);
        chrome.storage.local.get(['element_hider_rules'], (result) => {
          const rules = result.element_hider_rules || {};
          if (!rules[port]) rules[port] = { enabled: true, selectors: [] };
          rules[port].selectors = selectors;
          saveElementHiderRules(rules);
        });
      });
    });

    // Per-port ON/OFF toggle
    scriptItem.querySelectorAll('.eh-port-toggle').forEach(btn => {
      btn.addEventListener('click', () => {
        const port = btn.dataset.port;
        chrome.storage.local.get(['element_hider_rules'], (result) => {
          const rules = result.element_hider_rules || {};
          if (!rules[port]) rules[port] = { enabled: true, selectors: [] };
          rules[port].enabled = !rules[port].enabled;
          saveElementHiderRules(rules);
          // Refresh UI to reflect new state
          loadScriptList();
        });
      });
    });

    // Per-port CLEAR button
    scriptItem.querySelectorAll('.eh-port-clear').forEach(btn => {
      btn.addEventListener('click', () => {
        const port = btn.dataset.port;
        chrome.storage.local.get(['element_hider_rules'], (result) => {
          const rules = result.element_hider_rules || {};
          delete rules[port];
          saveElementHiderRules(rules);
          loadScriptList();
        });
      });
    });
  }

  function activateCursorTargetPicker() {
    if (window.__cursorTargetPickerActive) return;
    window.__cursorTargetPickerActive = true;

    const highlight = document.createElement('div');
    highlight.style.cssText = 'position:fixed !important;z-index:2147483647 !important;pointer-events:none !important;border:2px solid #ff3b30 !important;background:rgba(255,59,48,.12) !important;box-sizing:border-box !important;display:none !important;';
    const banner = document.createElement('div');
    banner.textContent = 'Click an element to save it as a cursor target · Esc to cancel';
    banner.style.cssText = 'position:fixed !important;top:12px !important;left:50% !important;transform:translateX(-50%) !important;z-index:2147483647 !important;padding:10px 14px !important;border-radius:6px !important;background:#202124 !important;color:white !important;font:14px sans-serif !important;box-shadow:0 2px 12px #0008 !important;pointer-events:none !important;';
    (document.documentElement || document).append(highlight, banner);

    function selectorFor(element) {
      if (element.id) return `#${CSS.escape(element.id)}`;
      const parts = [];
      let current = element;
      while (current && current.nodeType === Node.ELEMENT_NODE && current !== document.documentElement) {
        if (current.id) {
          parts.unshift(`#${CSS.escape(current.id)}`);
          break;
        }
        const tag = current.localName;
        let index = 1;
        for (let sibling = current.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
          if (sibling.localName === tag) index += 1;
        }
        parts.unshift(`${tag}:nth-of-type(${index})`);
        current = current.parentElement;
      }
      return parts.join(' > ');
    }

    function elementAt(event) {
      const element = document.elementFromPoint(event.clientX, event.clientY);
      return element && element !== highlight && element !== banner ? element : null;
    }

    function onMove(event) {
      const element = elementAt(event);
      if (!element) return;
      const rect = element.getBoundingClientRect();
      highlight.style.setProperty('display', 'block', 'important');
      highlight.style.setProperty('left', `${rect.left}px`, 'important');
      highlight.style.setProperty('top', `${rect.top}px`, 'important');
      highlight.style.setProperty('width', `${rect.width}px`, 'important');
      highlight.style.setProperty('height', `${rect.height}px`, 'important');
    }

    function cleanup() {
      document.removeEventListener('pointermove', onMove, true);
      document.removeEventListener('click', onClick, true);
      document.removeEventListener('keydown', onKeyDown, true);
      highlight.remove();
      banner.remove();
      window.__cursorTargetPickerActive = false;
    }

    function onClick(event) {
      const element = elementAt(event);
      if (!element) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      const selector = selectorFor(element);
      chrome.storage.local.get(['visibleCursorTargets'], (result) => {
        const targets = result.visibleCursorTargets || [];
        const target = { host: location.hostname, selector };
        if (!targets.some((entry) => entry.host === target.host && entry.selector === target.selector)) {
          targets.push(target);
          chrome.storage.local.set({ visibleCursorTargets: targets });
        }
        cleanup();
      });
    }

    function onKeyDown(event) {
      if (event.key !== 'Escape') return;
      event.preventDefault();
      event.stopImmediatePropagation();
      cleanup();
    }

    document.addEventListener('pointermove', onMove, true);
    document.addEventListener('click', onClick, true);
    document.addEventListener('keydown', onKeyDown, true);
  }

  async function loadScriptList() {
    try {
      statusText.textContent = 'Discovering scripts...';
      
      // Get available scripts dynamically
      const availableScripts = await getAvailableScripts();
      
      if (availableScripts.length === 0) {
        scriptListDiv.innerHTML = '<div class="no-scripts">No scripts found in user_scripts folder</div>';
        statusText.textContent = 'No scripts available';
        return;
      }
      
      chrome.storage.local.get(['enabledScripts', 'fallbackSettings', 'domainWhitelist', 'ytAnalyzerHotkey', 'element_hider_rules', 'visibleCursorStyle', 'visibleCursorColor', 'visibleCursorSize', 'visibleCursorTargets'], (result) => {
        const enabledScripts = result.enabledScripts || {};
        const fallbackSettings = normalizeSettings(result.fallbackSettings);
        const domainWhitelist = result.domainWhitelist || '';
        const ytAnalyzerHotkey = result.ytAnalyzerHotkey || 'F9';
        const elementHiderRules = result.element_hider_rules || {};
        const cursorStyle = ['arrow', 'crosshair', 'dot'].includes(result.visibleCursorStyle) ? result.visibleCursorStyle : 'arrow';
        const cursorColor = /^#[0-9a-f]{6}$/i.test(result.visibleCursorColor || '') ? result.visibleCursorColor : '#ffffff';
        const cursorSize = Number.isFinite(Number(result.visibleCursorSize)) ? Math.min(200, Math.max(60, Number(result.visibleCursorSize))) : 100;
        const cursorTargets = Array.isArray(result.visibleCursorTargets) ? result.visibleCursorTargets : [];
        
        // Clear existing items
        scriptListDiv.innerHTML = '';
        
        // Create script items
        availableScripts.forEach(scriptPath => {
          const isEnabled = enabledScripts[scriptPath] || false;
          const scriptItem = createScriptItem(scriptPath, isEnabled, fallbackSettings, domainWhitelist, ytAnalyzerHotkey, elementHiderRules, cursorStyle, cursorColor, cursorSize, cursorTargets);
          
          // Add click handler to toggle button (only the main ON/OFF in script-actions)
          const toggleBtn = scriptItem.querySelector('.script-actions .toggle-btn');
          toggleBtn.addEventListener('click', () => {
            toggleScript(scriptPath, isEnabled);
          });

          attachSettingsHandlers(scriptItem, fallbackSettings, domainWhitelist, cursorTargets);
          
          scriptListDiv.appendChild(scriptItem);
        });
        
        // Update status
        updateStatus(enabledScripts, availableScripts.length);
      });
    } catch (error) {
      console.error('Error loading scripts:', error);
      scriptListDiv.innerHTML = '<div class="no-scripts">Error loading scripts</div>';
      statusText.textContent = 'Error loading scripts';
    }
  }

  // Load scripts when popup opens
  loadScriptList();

  
});
