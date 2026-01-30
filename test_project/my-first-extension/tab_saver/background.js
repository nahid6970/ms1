// Background script for Tab Saver with Python server integration
const PYTHON_SERVER = 'http://localhost:8765';
const EXTENSION_NAME = 'tab_saver';
const FILE_NAME = 'saved_tabs.json';

// Send data to Python server
async function sendDataToPython(data) {
  try {
    const response = await fetch(PYTHON_SERVER, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        extension_name: EXTENSION_NAME,
        file_name: FILE_NAME,
        data: data
      })
    });
    
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Data saved to Python server:', result);
    return result;
  } catch (error) {
    console.error('Failed to send data to Python server:', error);
    return { success: false, error: error.message };
  }
}

// Load data from Python server
async function loadDataFromPython() {
  try {
    const response = await fetch(`${PYTHON_SERVER}/load?extension_name=${EXTENSION_NAME}&file_name=${FILE_NAME}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Data loaded from Python server:', result);
    return result;
  } catch (error) {
    console.error('Failed to load data from Python server:', error);
    return { success: false, error: error.message };
  }
}

// Auto-save on storage changes
chrome.storage.local.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local') {
    chrome.storage.local.get(null, (items) => {
      sendDataToPython(items);
    });
    
    // Update badge when storage changes
    updateBadge();
  }
});

// Update badge with tab count
function updateBadge() {
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    const count = savedTabs.length;
    
    if (count > 0) {
      chrome.action.setBadgeText({ text: count.toString() });
      chrome.action.setBadgeBackgroundColor({ color: '#667eea' });
    } else {
      chrome.action.setBadgeText({ text: '' });
    }
  });
}

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "saveAndCloseTab",
    title: "Save & Close Tab",
    contexts: ["page"]
  });
  
  // Update badge on install
  updateBadge();
});

// Handle context menu click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "saveAndCloseTab") {
    // Get current saved tabs
    chrome.storage.local.get(['savedTabs'], (result) => {
      const savedTabs = result.savedTabs || [];
      
      // Add current tab to list
      const newTab = {
        id: Date.now(),
        title: tab.title,
        url: tab.url,
        favicon: tab.favIconUrl || '',
        savedAt: new Date().toISOString()
      };
      
      savedTabs.push(newTab);
      
      // Save to storage
      chrome.storage.local.set({ savedTabs: savedTabs }, () => {
        console.log('Tab saved:', newTab);
        
        // Close the tab
        chrome.tabs.remove(tab.id);
      });
    });
  }
});

// Handle manual save/load requests from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveToPython') {
    sendDataToPython(message.data)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  
  if (message.action === 'loadFromPython') {
    loadDataFromPython()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

// Health check on startup
chrome.runtime.onStartup.addListener(() => {
  fetch(`${PYTHON_SERVER}/health`)
    .then(response => response.json())
    .then(data => console.log('Python server status:', data))
    .catch(error => console.log('Python server not available:', error.message));
});

// Initial health check
fetch(`${PYTHON_SERVER}/health`)
  .then(response => response.json())
  .then(data => console.log('Python server status:', data))
  .catch(error => console.log('Python server not available:', error.message));

// Update badge on startup
updateBadge();
