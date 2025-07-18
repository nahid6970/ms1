document.addEventListener('DOMContentLoaded', () => {
  const scriptListDiv = document.getElementById('scriptList');
  const statusText = document.getElementById('statusText');

  const allAvailableScripts = [
    'user_scripts/sample_script.js',
    'user_scripts/disable_youtube.js',
    'user_scripts/dark_mode_toggle.js',
    'user_scripts/text_highlighter.js',
    'user_scripts/youtube_ad_skipper.js',
  ];

  // Script descriptions for better display
  const scriptDescriptions = {
    'user_scripts/sample_script.js': 'Sample Script - Test script with alert',
    'user_scripts/disable_youtube.js': 'Disable YouTube - Redirects to Google',
    'user_scripts/dark_mode_toggle.js': 'Dark Mode - Inverts page colors',
    'user_scripts/text_highlighter.js': 'Text Highlighter - Highlight selected text',
    'user_scripts/youtube_ad_skipper.js': 'YouTube Ad Skipper - Skip/speed up ads'
  };

  function createScriptItem(scriptPath, isEnabled) {
    const fileName = scriptPath.split('/').pop();
    const scriptName = fileName.replace('.js', '');
    const description = scriptDescriptions[scriptPath] || scriptPath;

    const scriptItem = document.createElement('div');
    scriptItem.className = `script-item ${isEnabled ? 'enabled' : 'disabled'}`;
    scriptItem.dataset.scriptPath = scriptPath;

    scriptItem.innerHTML = `
      <div class="script-info">
        <div class="script-icon">${isEnabled ? '✓' : '○'}</div>
        <div class="script-details">
          <div class="script-name">${scriptName}</div>
          <div class="script-path">${description}</div>
        </div>
      </div>
      <button class="toggle-btn ${isEnabled ? 'active' : 'inactive'}" data-script="${scriptPath}">
        ${isEnabled ? 'ON' : 'OFF'}
      </button>
    `;

    return scriptItem;
  }

  function updateStatus(enabledScripts) {
    const enabledCount = Object.values(enabledScripts).filter(Boolean).length;
    statusText.textContent = `${enabledCount} script${enabledCount !== 1 ? 's' : ''} enabled`;
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

  function loadScriptList() {
    chrome.storage.local.get(['enabledScripts'], (result) => {
      const enabledScripts = result.enabledScripts || {};
      
      // Clear existing items
      scriptListDiv.innerHTML = '';
      
      // Create script items
      allAvailableScripts.forEach(scriptPath => {
        const isEnabled = enabledScripts[scriptPath] || false;
        const scriptItem = createScriptItem(scriptPath, isEnabled);
        
        // Add click handler to toggle button
        const toggleBtn = scriptItem.querySelector('.toggle-btn');
        toggleBtn.addEventListener('click', () => {
          toggleScript(scriptPath, isEnabled);
        });
        
        scriptListDiv.appendChild(scriptItem);
      });
      
      // Update status
      updateStatus(enabledScripts);
    });
  }

  // Load scripts when popup opens
  loadScriptList();
});