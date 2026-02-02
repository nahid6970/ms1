// Background script for Python server integration
const PYTHON_SERVER = 'http://localhost:8765';
const EXTENSION_NAME = 'QuickSidebarPro'; 
const FILE_NAME = 'sidebar_links.json';

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

// Auto-save on storage changes (Only sync storage for this extension)
chrome.storage.sync.onChanged.addListener((changes, areaName) => {
  if (areaName === 'sync') {
    chrome.storage.sync.get(null, (items) => {
      sendDataToPython(items);
    });
  }
});

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

// Handle manual save/load requests from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveToPython') {
    sendDataToPython(message.data)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
  
  if (message.action === 'loadFromPython') {
    loadDataFromPython()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
});

// Initial health check
fetch(`${PYTHON_SERVER}/health`)
  .then(response => response.json())
  .then(data => console.log('Python server status:', data))
  .catch(error => console.log('Python server not available:', error.message));

// Context Menu Integration
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "add-to-sidebar",
    title: "Add to Quick Sidebar",
    contexts: ["page"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "add-to-sidebar") {
    addTabToSidebar(tab);
  }
});

function addTabToSidebar(tab) {
  if (!tab || !tab.url) return;

  chrome.storage.sync.get(['sidebar_links'], (result) => {
    const links = result.sidebar_links || [];
    
    let domain = '';
    try {
        domain = new URL(tab.url).hostname;
    } catch (e) {
        console.error('Invalid URL:', tab.url);
        return;
    }

    const newLink = {
      id: Date.now().toString(),
      title: tab.title || domain,
      url: tab.url,
      color: '#38bdf8', // Default color
      isSolid: false,
      icon: `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
    };

    links.push(newLink);

    chrome.storage.sync.set({ sidebar_links: links }, () => {
       console.log('Added to sidebar:', newLink);
    });
  });
}