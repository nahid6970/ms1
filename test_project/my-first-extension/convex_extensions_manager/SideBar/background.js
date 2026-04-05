// Background script for Convex integration
import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

// Replace with your actual Convex URL from 'npx convex dev'
const CONVEX_URL = "https://joyous-stingray-672.convex.cloud"; 
const EXTENSION_NAME = 'QuickSidebarPro'; 

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
chrome.storage.sync.onChanged.addListener((changes, areaName) => {
  if (areaName === 'sync') {
    chrome.storage.sync.get(null, (items) => {
      sendDataToConvex(items);
    });
  }
});

// Handle manual save/load requests from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveToConvex') { // Keeping action name for compatibility or updating if preferred
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

// Context Menu Setup
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "add-to-sidebar",
    title: "Add to Quick Sidebar",
    contexts: ["page", "link"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "add-to-sidebar") {
    const urlToAdd = info.linkUrl || info.pageUrl || tab.url;
    const titleToAdd = info.selectionText || tab.title || "New Link";
    addUrlToSidebar(urlToAdd, titleToAdd, tab.favIconUrl);
  }
});

function addUrlToSidebar(url, title, favIconUrl) {
  if (!url) return;

  chrome.storage.sync.get(['sidebar_links'], (result) => {
    let links = result.sidebar_links || [];
    
    // Check if URL already exists
    if (links.some(l => l.url === url)) {
      console.log('Link already exists in sidebar');
      return;
    }

    let domain = '';
    try {
        domain = new URL(url).hostname;
    } catch (e) {
        console.error('Invalid URL:', url);
        return;
    }

    const newLink = {
      id: Date.now().toString(),
      title: title,
      url: url,
      color: '#38bdf8',
      isSolid: false,
      icon: favIconUrl || `https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=${url}&size=64`
    };

    links.push(newLink);

    chrome.storage.sync.set({ sidebar_links: links }, () => {
       console.log('Added to sidebar:', newLink);
    });
  });
}
