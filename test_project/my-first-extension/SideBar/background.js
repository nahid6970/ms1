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

// Auto-save on storage changes (Listening to both local and sync)
chrome.storage.onChanged.addListener((changes, areaName) => {
  chrome.storage[areaName].get(null, (items) => {
    sendDataToPython(items);
  });
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
