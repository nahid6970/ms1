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
      'sample_script': 'Sample Script - Test script with alert',
      'disable_youtube': 'Disable YouTube - Redirects to Google',
      'dark_mode_toggle': 'Dark Mode - Inverts page colors',
      'text_highlighter': 'Text Highlighter - Highlight selected text',
      'youtube_ad_skipper': 'YouTube Ad Skipper - Skip/speed up ads',
      'element_popper': 'Element Popper - Pop out elements with Ctrl+Click',
      'auto_clicker': 'Auto Clicker - Automated clicking functionality',
      'page_monitor': 'Page Monitor - Track page changes',
      'form_filler': 'Form Filler - Auto-fill form fields',
      'link_preview': 'Link Preview - Preview links on hover',
      'scroll_enhancer': 'Scroll Enhancer - Smooth scrolling improvements',
      'password_generator': 'Password Generator - Generate secure passwords',
      'tab_manager': 'Tab Manager - Enhanced tab management',
      'image_lazy_loader': 'Image Lazy Loader - Optimize image loading',
      'notification_blocker': 'Notification Blocker - Block unwanted notifications',
      'theme_switcher': 'Theme Switcher - Quick theme changes'
    };
    
    const baseDescription = descriptions[scriptName.replace(/\s+/g, '_').toLowerCase()];
    return {
      name: displayName,
      description: baseDescription || `${displayName} - Custom user script`
    };
  }

  function createScriptItem(scriptPath, isEnabled, fallbackSettings) {
    const scriptInfo = generateScriptInfo(scriptPath);
    const isFallbackScript = scriptPath === fallbackScriptPath;
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
            <div class="script-path">${scriptInfo.description}</div>
          </div>
        </div>
        <div class="script-actions">
          ${isFallbackScript ? `<button class="settings-btn" data-script="${scriptPath}" aria-expanded="false">SET</button>` : ''}
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

  function attachFallbackSettingsHandlers(scriptItem, fallbackSettings) {
    const localServerInput = scriptItem.querySelector('#localServerUrl');
    const siteUrlInput = scriptItem.querySelector('#siteUrl');
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

    if (modeButton) {
      modeButton.addEventListener('click', () => {
        toggleFallbackMode(fallbackSettings);
      });
    }
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
      
      chrome.storage.local.get(['enabledScripts', 'fallbackSettings'], (result) => {
        const enabledScripts = result.enabledScripts || {};
        const fallbackSettings = normalizeSettings(result.fallbackSettings);
        
        // Clear existing items
        scriptListDiv.innerHTML = '';
        
        // Create script items
        availableScripts.forEach(scriptPath => {
          const isEnabled = enabledScripts[scriptPath] || false;
          const scriptItem = createScriptItem(scriptPath, isEnabled, fallbackSettings);
          
          // Add click handler to toggle button
          const toggleBtn = scriptItem.querySelector('.toggle-btn');
          toggleBtn.addEventListener('click', () => {
            toggleScript(scriptPath, isEnabled);
          });

          if (scriptPath === fallbackScriptPath) {
            attachFallbackSettingsHandlers(scriptItem, fallbackSettings);
          }
          
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
