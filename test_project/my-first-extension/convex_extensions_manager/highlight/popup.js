document.addEventListener('DOMContentLoaded', () => {
  const clearBtn = document.getElementById('clearBtn');
  const status = document.getElementById('status');
  const saveToPythonBtn = document.getElementById('saveToPython');
  const loadFromPythonBtn = document.getElementById('loadFromPython');
  const saveColorsBtn = document.getElementById('saveColors');
  const reloadExtensionBtn = document.getElementById('reloadExtension');

  // Reload extension logic
  if (reloadExtensionBtn) {
    reloadExtensionBtn.addEventListener('click', () => {
      chrome.runtime.reload();
    });
  }

  // Excluded Domains
  const excludedDomainsInput = document.getElementById('excludedDomains');
  const saveExclusionsBtn = document.getElementById('saveExclusions');

  // Color palette logic
  const colorGrid = document.getElementById('colorGrid');
  const addColorBtn = document.getElementById('addColorBtn');
  let currentColors = ['#ffff00', '#aaffaa', '#aaddff', '#ffaaaa'];

  function renderColors() {
    // Remove existing color items
    const existingItems = colorGrid.querySelectorAll('.color-item');
    existingItems.forEach(item => item.remove());

    currentColors.forEach((color, index) => {
      const colorItem = document.createElement('div');
      colorItem.className = 'color-item';

      const label = document.createElement('label');
      label.className = 'color-label';
      label.textContent = `C${index + 1}`;

      const input = document.createElement('input');
      input.type = 'color';
      input.value = color;
      input.addEventListener('change', (e) => {
        currentColors[index] = e.target.value;
      });

      const removeBtn = document.createElement('div');
      removeBtn.className = 'remove-color-btn';
      removeBtn.textContent = '×';
      removeBtn.title = 'Remove Color';
      removeBtn.addEventListener('click', () => {
        currentColors.splice(index, 1);
        renderColors();
      });

      colorItem.appendChild(label);
      colorItem.appendChild(input);
      colorItem.appendChild(removeBtn);
      
      // Insert before the add button
      colorGrid.insertBefore(colorItem, addColorBtn);
    });
  }

  // Load saved settings
  chrome.storage.local.get(['customColors', 'excludedDomains'], (result) => {
    if (result.customColors && Array.isArray(result.customColors)) {
      currentColors = result.customColors;
    }
    renderColors();

    if (result.excludedDomains) {
      excludedDomainsInput.value = result.excludedDomains.join('\n');
    }
  });

  // Add Color
  addColorBtn.addEventListener('click', () => {
    currentColors.push('#ffffff');
    renderColors();
  });

  // Save Exclusions
  saveExclusionsBtn.addEventListener('click', () => {
    const domains = excludedDomainsInput.value
      .split('\n')
      .map(d => d.trim())
      .filter(d => d.length > 0);

    chrome.storage.local.set({ excludedDomains: domains }, () => {
      showStatus('Exclusions saved! Refresh pages to apply.');
    });
  });

  // Save colors
  saveColorsBtn.addEventListener('click', () => {
    chrome.storage.local.set({ customColors: currentColors }, () => {
      showStatus('Colors saved! Refresh pages to see changes.');

      // Notify all tabs to refresh
      chrome.tabs.query({}, (tabs) => {
        tabs.forEach(tab => {
          chrome.tabs.sendMessage(tab.id, { action: "reload_colors" }).catch(() => { });
        });
      });
    });
  });

  function showStatus(msg, duration = 3000) {
    status.textContent = msg;
    setTimeout(() => status.textContent = '', duration);
  }

  // Save to Python server button
  if (saveToPythonBtn) {
    saveToPythonBtn.addEventListener('click', function () {
      const originalContent = saveToPythonBtn.innerHTML;
      saveToPythonBtn.classList.add('loading');
      saveToPythonBtn.innerHTML = '<span>⏳</span> Saving...';

      chrome.storage.local.get(null, function (items) {
        // Send message to background script to save
        chrome.runtime.sendMessage({
          action: 'saveToPython',
          data: items
        }, function (response) {
          saveToPythonBtn.classList.remove('loading');
          
          // Check if response exists and doesn't have success: false
          if (response && response.success !== false) {
            saveToPythonBtn.classList.add('success');
            saveToPythonBtn.innerHTML = '<span>✅</span> Saved!';
            showStatus('Data saved to Python server!');
            
            setTimeout(() => {
              saveToPythonBtn.classList.remove('success');
              saveToPythonBtn.innerHTML = originalContent;
            }, 2000);
          } else {
            saveToPythonBtn.innerHTML = '<span>❌</span> Failed';
            showStatus('Failed to save to Python server. Make sure the server is running.');
            
            setTimeout(() => {
              saveToPythonBtn.innerHTML = originalContent;
            }, 2000);
          }
        });
      });
    });
  }

  // Load from Python server button
  if (loadFromPythonBtn) {
    loadFromPythonBtn.addEventListener('click', function () {
      chrome.runtime.sendMessage({
        action: 'loadFromPython'
      }, function (response) {
        if (response && response.success !== false && response.data) {
          chrome.storage.local.set(response.data, () => {
            showStatus('Data loaded from Python server! Refresh pages to see changes.');
            // Notify all tabs to refresh
            chrome.tabs.query({}, (tabs) => {
              tabs.forEach(tab => {
                chrome.tabs.sendMessage(tab.id, { action: "refresh_highlights" }).catch(() => { });
              });
            });
          });
        } else {
          showStatus('Failed to load from Python server. Make sure the server is running.');
        }
      });
    });
  }

  clearBtn.addEventListener('click', () => {
    if (confirm("Are you sure you want to delete all highlights?")) {
      chrome.storage.local.clear(() => {
        showStatus('All data cleared.');
        // Optional: Send message to active tab to clear highlights immediately
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
          chrome.tabs.sendMessage(tabs[0].id, { action: "refresh_highlights" });
        });
      });
    }
  });
});
