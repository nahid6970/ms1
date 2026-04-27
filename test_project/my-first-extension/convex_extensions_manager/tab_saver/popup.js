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
  
  // Sort tabs by id descending (newest first)
  tabs.sort((a, b) => b.id - a.id);
  
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
    
    const isYouTube = tab.url.includes('youtube.com/watch');
    const favicon = tab.favicon || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><text y="20" font-size="20">🌐</text></svg>';
    
    let faviconHTML;
    if (isYouTube && tab.channelIcon) {
      faviconHTML = `
        <div class="tab-favicon-container">
          <img src="${favicon}" class="tab-favicon-yt" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>▶️</text></svg>'">
          <img src="${tab.channelIcon}" class="tab-favicon-channel" onerror="this.style.display='none'">
        </div>
      `;
    } else {
      faviconHTML = `<img src="${favicon}" class="tab-favicon" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>🌐</text></svg>'">`;
    }
    
    // Calculate days left for deadline
    let deadlineHTML = '';
    if (tab.deadline) {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
      const target = new Date(tab.deadline);
      const targetDate = new Date(target.getFullYear(), target.getMonth(), target.getDate()).getTime();
      
      const diffDays = Math.round((targetDate - today) / (1000 * 60 * 60 * 24));
      
      let badgeClass = 'tab-deadline';
      let text = '';
      
      if (diffDays < 0) {
        text = '!!';
        badgeClass += ' urgent';
      } else if (diffDays === 0) {
        text = '0';
        badgeClass += ' urgent';
      } else {
        text = `${diffDays}`;
        if (diffDays <= 3) badgeClass += ' urgent';
        else badgeClass += ' safe';
      }
      
      deadlineHTML = `<div class="${badgeClass}">${text}</div>`;
    }
    
    tabItem.innerHTML = `
      ${faviconHTML}
      <div class="tab-info" data-url="${tab.url}">
        <div class="tab-title">${tab.title}</div>
        <div class="tab-url">${tab.url}</div>
      </div>
      ${deadlineHTML}
      <button class="tab-remove" data-id="${tab.id}">×</button>
    `;
    
    const tabInfo = tabItem.querySelector('.tab-info');
    tabInfo.addEventListener('click', () => {
      chrome.tabs.create({ url: tab.url });
    });
    
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

// Add all currently open browser tabs
document.getElementById('addAllTabs').addEventListener('click', (e) => {
  const button = e.target;
  chrome.tabs.query({}, (browserTabs) => {
    chrome.storage.local.get(['savedTabs'], (result) => {
      const savedTabs = result.savedTabs || [];
      const existingUrls = new Set(savedTabs.map(t => t.url));
      const newTabs = browserTabs
        .filter(t => t.url && !existingUrls.has(t.url))
        .map(t => ({ id: Date.now() + Math.random(), title: t.title || t.url, url: t.url, favicon: t.favIconUrl || '' }));
      if (newTabs.length === 0) {
        showButtonFeedback(button, false, 'No new tabs');
        return;
      }
      chrome.storage.local.set({ savedTabs: [...savedTabs, ...newTabs] }, () => {
        showButtonFeedback(button, true, `Added ${newTabs.length}!`);
        loadTabs();
      });
    });
  });
});

// Clear all tabs
document.getElementById('clearAll').addEventListener('click', (e) => {
  const button = e.target;
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    
    if (savedTabs.length === 0) {
      showButtonFeedback(button, false, 'No tabs to clear');
      return;
    }
    
    chrome.storage.local.set({ savedTabs: [] }, () => {
      showButtonFeedback(button, true, 'Cleared!');
      loadTabs();
    });
  });
});

// Show button feedback
function showButtonFeedback(button, success, message) {
  const originalText = button.innerHTML;
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
    button.style.background = '';
    button.disabled = false;
  }, 2000);
}

// Save to Convex
document.getElementById('saveToConvex').addEventListener('click', (e) => {
  const button = e.target;
  chrome.storage.local.get(null, (items) => {
    chrome.runtime.sendMessage({
      action: 'saveToConvex',
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

// Load from Convex
document.getElementById('loadFromConvex').addEventListener('click', (e) => {
  const button = e.target;
  chrome.runtime.sendMessage({
    action: 'loadFromConvex'
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

// Settings functionality
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeModal = document.getElementById('closeModal');
const resetSettings = document.getElementById('resetSettings');

// Inputs
const ytIconSize = document.getElementById('ytIconSize');
const channelIconSize = document.getElementById('channelIconSize');
const ytIconValue = document.getElementById('ytIconValue');
const channelIconValue = document.getElementById('channelIconValue');

const urgentBg = document.getElementById('urgentBg');
const urgentFg = document.getElementById('urgentFg');
const urgentBorder = document.getElementById('urgentBorder');
const safeBg = document.getElementById('safeBg');
const safeFg = document.getElementById('safeFg');
const safeBorder = document.getElementById('safeBorder');

// Load saved settings
function loadSettings() {
  chrome.storage.local.get(['iconSettings', 'deadlineSettings'], (result) => {
    const iconSettings = result.iconSettings || { ytIconSize: 20, channelIconSize: 18 };
    const deadlineSettings = result.deadlineSettings || {
      urgentBg: '#ff4757', urgentFg: '#ffffff', urgentBorder: '#eb3b5a',
      safeBg: '#e3f2fd', safeFg: '#1976d2', safeBorder: '#bbdefb'
    };
    
    // Icons
    ytIconSize.value = iconSettings.ytIconSize;
    channelIconSize.value = iconSettings.channelIconSize;
    ytIconValue.textContent = iconSettings.ytIconSize + 'px';
    channelIconValue.textContent = iconSettings.channelIconSize + 'px';
    
    // Deadlines
    urgentBg.value = deadlineSettings.urgentBg;
    urgentFg.value = deadlineSettings.urgentFg;
    urgentBorder.value = deadlineSettings.urgentBorder;
    safeBg.value = deadlineSettings.safeBg;
    safeFg.value = deadlineSettings.safeFg;
    safeBorder.value = deadlineSettings.safeBorder;
    
    applySettings(iconSettings, deadlineSettings);
  });
}

// Apply settings to CSS
function applySettings(icons, deadlines) {
  const styleId = 'dynamic-settings-styles';
  let style = document.getElementById(styleId);
  if (style) style.remove();
  
  style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    .tab-favicon-container { width: ${icons.ytIconSize}px !important; height: ${icons.ytIconSize}px !important; }
    .tab-favicon-yt { width: ${icons.ytIconSize}px !important; height: ${icons.ytIconSize}px !important; }
    .tab-favicon-channel { width: ${icons.channelIconSize}px !important; height: ${icons.channelIconSize}px !important; }
    
    .tab-deadline.urgent { 
      background-color: ${deadlines.urgentBg} !important; 
      color: ${deadlines.urgentFg} !important; 
      border-color: ${deadlines.urgentBorder} !important; 
    }
    .tab-deadline.safe { 
      background-color: ${deadlines.safeBg} !important; 
      color: ${deadlines.safeFg} !important; 
      border-color: ${deadlines.safeBorder} !important; 
    }
  `;
  document.head.appendChild(style);
}

// Save settings
function saveAllSettings() {
  const iconSettings = {
    ytIconSize: parseInt(ytIconSize.value),
    channelIconSize: parseInt(channelIconSize.value)
  };
  const deadlineSettings = {
    urgentBg: urgentBg.value, urgentFg: urgentFg.value, urgentBorder: urgentBorder.value,
    safeBg: safeBg.value, safeFg: safeFg.value, safeBorder: safeBorder.value
  };
  
  chrome.storage.local.set({ iconSettings, deadlineSettings }, () => {
    applySettings(iconSettings, deadlineSettings);
  });
}

// Event Listeners
[ytIconSize, channelIconSize, urgentBg, urgentFg, urgentBorder, safeBg, safeFg, safeBorder].forEach(el => {
  el.addEventListener('input', () => {
    if (el === ytIconSize) ytIconValue.textContent = el.value + 'px';
    if (el === channelIconSize) channelIconValue.textContent = el.value + 'px';
    saveAllSettings();
  });
});

settingsBtn.addEventListener('click', () => settingsModal.classList.add('show'));
closeModal.addEventListener('click', () => settingsModal.classList.remove('show'));
settingsModal.addEventListener('click', (e) => { if (e.target === settingsModal) settingsModal.classList.remove('show'); });

resetSettings.addEventListener('click', () => {
  ytIconSize.value = 20;
  channelIconSize.value = 18;
  urgentBg.value = '#ff4757';
  urgentFg.value = '#ffffff';
  urgentBorder.value = '#eb3b5a';
  safeBg.value = '#e3f2fd';
  safeFg.value = '#1976d2';
  safeBorder.value = '#bbdefb';
  saveAllSettings();
  loadSettings();
});

// Initial load
loadTabs();
loadSettings();
