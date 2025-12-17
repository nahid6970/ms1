document.addEventListener('DOMContentLoaded', () => {
    const exportBtn = document.getElementById('exportBtn');
    const importBtn = document.getElementById('importBtn');
    const importContainer = document.getElementById('importContainer');
    const importData = document.getElementById('importData');
    const confirmImportBtn = document.getElementById('confirmImportBtn');
    const clearBtn = document.getElementById('clearBtn');
    const status = document.getElementById('status');
  
    function showStatus(msg, duration = 3000) {
      status.textContent = msg;
      setTimeout(() => status.textContent = '', duration);
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
  
    importBtn.addEventListener('click', () => {
      importContainer.style.display = importContainer.style.display === 'none' ? 'block' : 'none';
    });
  
    confirmImportBtn.addEventListener('click', () => {
      try {
        const data = JSON.parse(importData.value);
        if (typeof data !== 'object') throw new Error('Invalid JSON');
        
        chrome.storage.local.set(data, () => {
          showStatus('Import successful! Refresh pages to see changes.');
          importData.value = '';
          importContainer.style.display = 'none';
        });
      } catch (e) {
        showStatus('Error: Invalid JSON data');
      }
    });

    clearBtn.addEventListener('click', () => {
      if(confirm("Are you sure you want to delete all highlights?")) {
        chrome.storage.local.clear(() => {
          showStatus('All data cleared.');
          // Optional: Send message to active tab to clear highlights immediately
          chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
              chrome.tabs.sendMessage(tabs[0].id, {action: "refresh_highlights"});
          });
        });
      }
    });
  });
