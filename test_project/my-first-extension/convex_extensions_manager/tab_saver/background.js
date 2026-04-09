// Background script for Convex integration
import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

// Replace with your actual Convex URL from 'npx convex dev'
const CONVEX_URL = "https://joyous-stingray-672.convex.cloud"; 
const EXTENSION_NAME = 'tab_saver';

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
      // Show 9+ for counts over 9
      const badgeText = count > 9 ? '9+' : count.toString();
      chrome.action.setBadgeText({ text: badgeText });
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
      
      // Get custom favicon for YouTube
      let favicon = tab.favIconUrl || '';
      
      // For YouTube videos, try to get channel icon
      if (tab.url.includes('youtube.com/watch')) {
        // Execute script to get channel icon from the page
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => {
            // Try multiple selectors to get channel avatar
            const selectors = [
              '#owner #avatar img',
              'ytd-video-owner-renderer #avatar img',
              '#channel-thumbnail img',
              'yt-img-shadow img',
              '#avatar img'
            ];
            
            for (const selector of selectors) {
              const img = document.querySelector(selector);
              if (img && img.src && !img.src.includes('data:')) {
                return img.src;
              }
            }
            return null;
          }
        }).then((results) => {
          const channelIcon = (results && results[0] && results[0].result) ? results[0].result : null;
          console.log('Channel icon found:', channelIcon);
          
          // Add tab with both YouTube favicon and channel icon
          saveTab(savedTabs, tab, favicon, channelIcon);
        }).catch((error) => {
          console.error('Failed to get channel icon:', error);
          // If script fails, use default favicon only
          saveTab(savedTabs, tab, favicon, null);
        });
      } else {
        // For non-YouTube tabs, save immediately
        saveTab(savedTabs, tab, favicon, null);
      }
    });
  }
});

// Helper function to save tab
function saveTab(savedTabs, tab, favicon, channelIcon = null) {
  const newTab = {
    id: Date.now(),
    title: tab.title,
    url: tab.url,
    favicon: favicon,
    channelIcon: channelIcon, // Store channel icon separately
    savedAt: new Date().toISOString()
  };
  
  savedTabs.unshift(newTab);
  
  // Save to storage
  chrome.storage.local.set({ savedTabs: savedTabs }, () => {
    console.log('Tab saved:', newTab);
    
    // Close the tab
    chrome.tabs.remove(tab.id);
  });
}

// Handle manual save/load requests from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveToConvex') {
    sendDataToConvex(message.data)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  
  if (message.action === 'loadFromConvex') {
    loadDataFromConvex()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
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

// Update badge on startup
updateBadge();
