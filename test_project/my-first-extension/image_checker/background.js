// Background script for Python server integration
const PYTHON_SERVER = 'http://localhost:8765';
const EXTENSION_NAME = 'image_checker';
const FILE_NAME = 'image_checker_data.json';

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
    // Don't throw - extension should work even if server is down
    return { success: false, error: error.message };
  }
}

// Auto-save on storage changes
chrome.storage.local.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local') {
    // Get all data and send to server
    chrome.storage.local.get(null, (items) => {
      sendDataToPython(items);
    });
  }
});

// Health check on startup
chrome.runtime.onStartup.addListener(() => {
  fetch(`${PYTHON_SERVER}/health`)
    .then(response => response.json())
    .then(data => console.log('Python server status:', data))
    .catch(error => console.log('Python server not available:', error.message));
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
