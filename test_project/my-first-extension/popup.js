document.addEventListener('DOMContentLoaded', () => {
  const scriptListDiv = document.getElementById('scriptList');
  const statusText = document.getElementById('statusText');



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

  const domainNoteInput = document.getElementById('domain-note-input');
  const saveDomainNoteBtn = document.getElementById('save-domain-note-btn');
  const pageNoteInput = document.getElementById('page-note-input');
  const savePageNoteBtn = document.getElementById('save-page-note-btn');

  let activeTabUrl = '';
  let activeTabHostname = '';

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0] && tabs[0].url) {
      const url = new URL(tabs[0].url);
      activeTabUrl = url.href;
      activeTabHostname = url.hostname;

      chrome.storage.local.get([activeTabUrl, activeTabHostname], (result) => {
        if (result[activeTabHostname]) {
          domainNoteInput.value = result[activeTabHostname];
        }
        if (result[activeTabUrl]) {
          pageNoteInput.value = result[activeTabUrl];
        }
      });
    }
  });

  saveDomainNoteBtn.addEventListener('click', () => {
    const noteText = domainNoteInput.value;
    if (activeTabHostname) {
      chrome.storage.local.set({ [activeTabHostname]: noteText }, () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          chrome.tabs.sendMessage(tabs[0].id, { action: 'updateDomainNote', note: noteText });
        });
        window.close();
      });
    }
  });

  savePageNoteBtn.addEventListener('click', () => {
    const noteText = pageNoteInput.value;
    if (activeTabUrl) {
      chrome.storage.local.set({ [activeTabUrl]: noteText }, () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          chrome.tabs.sendMessage(tabs[0].id, { action: 'updatePageNote', note: noteText });
        });
        window.close();
      });
    }
  });

  const importNotesBtn = document.getElementById('import-notes-btn');
  const exportNotesBtn = document.getElementById('export-notes-btn');
  const importNotesInput = document.getElementById('import-notes-input');

  exportNotesBtn.addEventListener('click', () => {
    chrome.storage.local.get(null, (items) => {
      const notes = {};
      for (const key in items) {
        if (key.startsWith('http')) {
          notes[key] = items[key];
        }
      }
      const blob = new Blob([JSON.stringify(notes, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      chrome.downloads.download({
        url: url,
        filename: 'notes.json'
      });
    });
  });

  importNotesBtn.addEventListener('click', () => {
    importNotesInput.click();
  });

  importNotesInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const notes = JSON.parse(e.target.result);
        chrome.storage.local.set(notes, () => {
          alert('Notes imported successfully!');
          // Refresh the note for the current page
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0] && tabs[0].url) {
              activeTabUrl = tabs[0].url;
              chrome.storage.local.get([activeTabUrl], (result) => {
                if (result[activeTabUrl]) {
                  noteInput.value = result[activeTabUrl];
                }
              });
            }
          });
        });
      };
      reader.readAsText(file);
    }
  });
});