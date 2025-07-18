document.addEventListener('DOMContentLoaded', () => {
  const scriptListDiv = document.getElementById('scriptList');
  const statusText = document.getElementById('statusText');

  // Function to discover scripts dynamically
  async function discoverScripts() {
    const scripts = [];
    
    try {
      // Get all files in the user_scripts directory
      const response = await fetch(chrome.runtime.getURL('user_scripts/'));
      const text = await response.text();
      
      // Parse the directory listing (this approach works for packed extensions)
      // For unpacked extensions, we'll use a different approach
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, 'text/html');
      const links = doc.querySelectorAll('a[href$=".js"]');
      
      links.forEach(link => {
        const scriptPath = `user_scripts/${link.href.split('/').pop()}`;
        scripts.push(scriptPath);
      });
    } catch (error) {
      console.log('Directory listing not available, using fallback method');
      
      // Fallback: Try to load common script files
      const commonScripts = [
        'sample_script.js',
        'disable_youtube.js',
        'dark_mode_toggle.js',
        'text_highlighter.js',
        'youtube_ad_skipper.js',
        'auto_clicker.js',
        'page_monitor.js',
        'form_filler.js',
        'link_preview.js',
        'scroll_enhancer.js',
        'password_generator.js',
        'tab_manager.js',
        'image_lazy_loader.js',
        'notification_blocker.js',
        'theme_switcher.js'
      ];
      
      // Check which scripts actually exist
      for (const script of commonScripts) {
        try {
          const scriptPath = `user_scripts/${script}`;
          await fetch(chrome.runtime.getURL(scriptPath));
          scripts.push(scriptPath);
        } catch (e) {
          // Script doesn't exist, skip it
        }
      }
    }
    
    return scripts;
  }

  // Enhanced script discovery using manifest and file system
  async function getAvailableScripts() {
    const scripts = [];
    
    // Method 1: Read from a scripts manifest file if it exists
    try {
      const response = await fetch(chrome.runtime.getURL('user_scripts/@scripts.json'));
      const scriptsManifest = await response.json();
      return scriptsManifest.scripts.map(script => `user_scripts/${script}`);
    } catch (error) {
      console.log('No scripts.json found, using auto-discovery');
    }
    
    // Method 2: Try to discover scripts automatically
    return await discoverScripts();
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

  function createScriptItem(scriptPath, isEnabled) {
    const scriptInfo = generateScriptInfo(scriptPath);

    const scriptItem = document.createElement('div');
    scriptItem.className = `script-item ${isEnabled ? 'enabled' : 'disabled'}`;
    scriptItem.dataset.scriptPath = scriptPath;

    scriptItem.innerHTML = `
      <div class="script-info">
        <div class="script-icon">${isEnabled ? '✓' : '○'}</div>
        <div class="script-details">
          <div class="script-name">${scriptInfo.name}</div>
          <div class="script-path">${scriptInfo.description}</div>
        </div>
      </div>
      <button class="toggle-btn ${isEnabled ? 'active' : 'inactive'}" data-script="${scriptPath}">
        ${isEnabled ? 'ON' : 'OFF'}
      </button>
    `;

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
      
      chrome.storage.local.get(['enabledScripts'], (result) => {
        const enabledScripts = result.enabledScripts || {};
        
        // Clear existing items
        scriptListDiv.innerHTML = '';
        
        // Create script items
        availableScripts.forEach(scriptPath => {
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