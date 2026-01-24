// Background script for Python server integration
const PYTHON_SERVER = 'http://localhost:8765';
const EXTENSION_NAME = 'highlighter';
const FILE_NAME = 'highlights.json';

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

// Auto-save on storage changes
chrome.storage.local.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local') {
    chrome.storage.local.get(null, (items) => {
      sendDataToPython(items);
    });
  }
});

// Handle manual save requests from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveToPython') {
    sendDataToPython(message.data)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
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

chrome.runtime.onInstalled.addListener(() => {
    console.log("Highlighter Extension Installed");
});
