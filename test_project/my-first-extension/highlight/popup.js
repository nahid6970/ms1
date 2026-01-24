document.addEventListener('DOMContentLoaded', () => {
  const exportBtn = document.getElementById('exportBtn');
  const importBtn = document.getElementById('importBtn');
  const clearBtn = document.getElementById('clearBtn');
  const status = document.getElementById('status');
  const saveToPythonBtn = document.getElementById('saveToPython');
  const loadFromPythonBtn = document.getElementById('loadFromPython');
  const saveColorsBtn = document.getElementById('saveColors');

  // Excluded Domains
  const excludedDomainsInput = document.getElementById('excludedDomains');
  const saveExclusionsBtn = document.getElementById('saveExclusions');

  // Color inputs
  const color1 = document.getElementById('color1');
  const color2 = document.getElementById('color2');
  const color3 = document.getElementById('color3');
  const color4 = document.getElementById('color4');

  // Load saved settings
  chrome.storage.local.get(['customColors', 'excludedDomains'], (result) => {
    if (result.customColors) {
      const colors = result.customColors;
      color1.value = colors[0] || '#ffff00';
      color2.value = colors[1] || '#aaffaa';
      color3.value = colors[2] || '#aaddff';
      color4.value = colors[3] || '#ffaaaa';
    }

    if (result.excludedDomains) {
      excludedDomainsInput.value = result.excludedDomains.join('\n');
    }
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
    const colors = [
      color1.value,
      color2.value,
      color3.value,
      color4.value
    ];

    chrome.storage.local.set({ customColors: colors }, () => {
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
      chrome.storage.local.get(null, function (items) {
        // Send message to background script to save
        chrome.runtime.sendMessage({
          action: 'saveToPython',
          data: items
        }, function (response) {
          // Check if response exists and doesn't have success: false
          if (response && response.success !== false) {
            showStatus('Data saved to Python server!');
          } else {
            showStatus('Failed to save to Python server. Make sure the server is running.');
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
        if (response && response.success && response.data) {
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

  exportBtn.addEventListener('click', () => {
    chrome.storage.local.get(null, (items) => {
      const dataStr = JSON.stringify(items, null, 2);
      const blob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(blob);

      // Create a dummy link to download
      const a = document.createElement('a');
      a.href = url;
      a.download = "highlights_backup.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showStatus('Export successful!');
    });
  });

  const fileInput = document.getElementById('fileInput');

  importBtn.addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result);
        if (typeof data !== 'object') throw new Error('Invalid JSON');

        chrome.storage.local.set(data, () => {
          showStatus('Import successful! Refresh pages to see changes.');
          fileInput.value = ''; // Reset input
        });
      } catch (err) {
        showStatus('Error: Invalid JSON file');
      }
    };
    reader.readAsText(file);
  });

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
