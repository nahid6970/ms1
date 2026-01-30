// Load and display saved tabs
function loadTabs() {
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    displayTabs(savedTabs);
  });
}

// Display tabs in the popup
function displayTabs(tabs) {
  const tabList = document.getElementById('tabList');
  const tabCount = document.getElementById('tabCount');
  
  tabCount.textContent = tabs.length;
  
  if (tabs.length === 0) {
    tabList.innerHTML = `
      <div class="empty-state">
        <p>No saved tabs yet!</p>
        <p class="hint">Right-click on any page and select "Save & Close Tab"</p>
      </div>
    `;
    return;
  }
  
  tabList.innerHTML = '';
  
  tabs.forEach((tab) => {
    const tabItem = document.createElement('div');
    tabItem.className = 'tab-item';
    
    const favicon = tab.favicon || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><text y="20" font-size="20">🌐</text></svg>';
    
    tabItem.innerHTML = `
      <img src="${favicon}" class="tab-favicon" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>🌐</text></svg>'">
      <div class="tab-info" data-url="${tab.url}">
        <div class="tab-title">${tab.title}</div>
        <div class="tab-url">${tab.url}</div>
      </div>
      <button class="tab-remove" data-id="${tab.id}">×</button>
    `;
    
    // Click on tab info to open URL
    const tabInfo = tabItem.querySelector('.tab-info');
    tabInfo.addEventListener('click', () => {
      chrome.tabs.create({ url: tab.url });
    });
    
    // Click on remove button to delete tab
    const removeBtn = tabItem.querySelector('.tab-remove');
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      removeTab(tab.id);
    });
    
    tabList.appendChild(tabItem);
  });
}

// Remove a tab from the list
function removeTab(tabId) {
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    const updatedTabs = savedTabs.filter(tab => tab.id !== tabId);
    
    chrome.storage.local.set({ savedTabs: updatedTabs }, () => {
      loadTabs();
    });
  });
}

// Clear all tabs
document.getElementById('clearAll').addEventListener('click', () => {
  if (confirm('Are you sure you want to clear all saved tabs?')) {
    chrome.storage.local.set({ savedTabs: [] }, () => {
      loadTabs();
    });
  }
});

// Show button feedback
function showButtonFeedback(button, success, message) {
  const originalText = button.innerHTML;
  const originalClass = button.className;
  
  if (success) {
    button.innerHTML = '✓ ' + message;
    button.style.background = '#4CAF50';
  } else {
    button.innerHTML = '✗ ' + message;
    button.style.background = '#f44336';
  }
  
  button.disabled = true;
  
  setTimeout(() => {
    button.innerHTML = originalText;
    button.className = originalClass;
    button.style.background = '';
    button.disabled = false;
  }, 2000);
}

// Save to Python server
document.getElementById('saveToPython').addEventListener('click', (e) => {
  const button = e.target;
  chrome.storage.local.get(null, (items) => {
    chrome.runtime.sendMessage({
      action: 'saveToPython',
      data: items
    }, (response) => {
      if (response && response.success !== false) {
        showButtonFeedback(button, true, 'Saved!');
      } else {
        showButtonFeedback(button, false, 'Failed');
      }
    });
  });
});

// Load from Python server
document.getElementById('loadFromPython').addEventListener('click', (e) => {
  const button = e.target;
  chrome.runtime.sendMessage({
    action: 'loadFromPython'
  }, (response) => {
    if (response && response.success && response.data) {
      chrome.storage.local.set(response.data, () => {
        showButtonFeedback(button, true, 'Loaded!');
        loadTabs();
      });
    } else {
      showButtonFeedback(button, false, 'Failed');
    }
  });
});

// Load tabs when popup opens
loadTabs();
