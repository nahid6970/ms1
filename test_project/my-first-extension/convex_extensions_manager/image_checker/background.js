// Background script for Convex integration
import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

// Replace with your actual Convex URL from 'npx convex dev'
const CONVEX_URL = "https://joyous-stingray-672.convex.cloud"; 
const EXTENSION_NAME = 'image_checker';

const client = new ConvexHttpClient(CONVEX_URL);

// Send data to Convex
async function sendDataToConvex(data) {
  try {
    const result = await client.mutation("functions:save", {
      extensionName: EXTENSION_NAME,
      data: data
    });
    console.log('Data saved to Convex:', result);
    return { success: true, result };
  } catch (error) {
    console.error('Failed to send data to Convex:', error);
    return { success: false, error: error.message };
  }
}

// Load data from Convex
async function loadDataFromConvex() {
  try {
    const data = await client.query("functions:get", { extensionName: EXTENSION_NAME });
    console.log('Data loaded from Convex:', data);
    return { success: true, data };
  } catch (error) {
    console.error('Failed to load data from Convex:', error);
    return { success: false, error: error.message };
  }
}

// Auto-save on storage changes
chrome.storage.local.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local') {
    chrome.storage.local.get(null, (items) => {
      sendDataToConvex(items);
    });
  }
});

// Handle manual save/load requests from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveToConvex') {
    sendDataToConvex(message.data)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
  
  if (message.action === 'loadFromConvex') {
    loadDataFromConvex()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
});

// Initial health check
(async () => {
    try {
        await client.query("functions:get", { extensionName: "health_check" });
        console.log('Convex connection healthy');
    } catch (e) {
        console.log('Convex not available or not initialized:', e.message);
    }
})();
