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
    const result = await client.query("functions:get", { extensionName: EXTENSION_NAME });
    console.log('Result loaded from Convex:', result);
    
    // If result is null, no record was found
    if (!result) return { success: true, data: null };

    // Try to find the storage object. If there is a 'data' field, it's likely a document record.
    // Otherwise, it might be the data object itself.
    let storageData = null;
    if (result.data && typeof result.data === 'object') {
      storageData = result.data;
    } else {
      // It might be the storage object directly, but let's filter out Convex internal fields
      storageData = { ...result };
      delete storageData._id;
      delete storageData._creationTime;
      delete storageData.extensionName;
    }

    return { success: true, data: storageData };
  } catch (error) {
    console.error('Failed to load data from Convex:', error);
    return { success: false, error: error.message };
  }
}

// Auto-save on storage changes
chrome.storage.onChanged.addListener((changes, areaName) => {
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
    return true; 
  }
  
  if (message.action === 'getSmartFavicon') {
    getSmartFavicon(message.url)
      .then(icon => sendResponse(icon));
    return true;
  }

  if (message.action === 'loadFromConvex') {
    loadDataFromConvex()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

// Context Menu Setup - Fixed to be more robust
function setupContextMenu() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "add-to-sidebar",
      title: "Add to Quick Sidebar",
      contexts: ["page", "link"]
    });
  });
}

chrome.runtime.onInstalled.addListener(setupContextMenu);
chrome.runtime.onStartup.addListener(setupContextMenu);

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "add-to-sidebar") {
    const urlToAdd = info.linkUrl || info.pageUrl || tab.url;
    const titleToAdd = info.selectionText || tab.title || "New Link";
    addUrlToSidebar(urlToAdd, titleToAdd);
  }
});


async function getSmartFavicon(url) {
  try {
    const urlObj = new URL(url);
    const domain = urlObj.hostname.replace('www.', '');

    // 1. Specialized logic for GitHub
    if (domain === 'github.com') {
      const parts = urlObj.pathname.split('/').filter(p => p);
      if (parts.length >= 1) return `https://github.com/${parts[0]}.png`;
    }

    // 2. Use Convex action for YouTube channels and Facebook (CORS bypass)
    const isYouTubeChannel = (domain.includes('youtube.com') || domain.includes('youtu.be')) && 
                             (urlObj.pathname.includes('/@') || urlObj.pathname.includes('/channel/') || urlObj.pathname.includes('/c/'));
    const isFacebook = domain.includes('facebook.com');

    if (isYouTubeChannel || isFacebook) {
      try {
        const icon = await client.action("actions:getFavicon", { url });
        if (icon) return icon;
      } catch (e) {
        console.error("Convex action failed for favicon:", e);
      }
    }

    // 3. Fallback to oEmbed for YouTube videos
    if (domain.includes('youtube.com') || domain.includes('youtu.be')) {
      try {
        const res = await fetch(`https://www.youtube.com/oembed?url=${encodeURIComponent(url)}&format=json`);
        if (res.ok) {
          const data = await res.json();
          if (data.thumbnail_url) return data.thumbnail_url;
        }
      } catch (e) {}
    }

    // 4. Google services icons
    const googleIcons = {
      'mail.google.com': 'https://ssl.gstatic.com/ui/v1/icons/mail/images/favicon5.ico',
      'drive.google.com': 'https://ssl.gstatic.com/images/branding/product/1x/drive_2020q4_48dp.png',
      'docs.google.com': 'https://ssl.gstatic.com/docs/documents/images/kix-favicon7.ico',
      'sheets.google.com': 'https://ssl.gstatic.com/docs/spreadsheets/favicon3.ico',
      'slides.google.com': 'https://ssl.gstatic.com/docs/presentations/images/favicon5.ico',
      'calendar.google.com': 'https://ssl.gstatic.com/calendar/images/favicon_v2014_15.ico',
      'meet.google.com': 'https://www.google.com/s2/favicons?domain=meet.google.com&sz=128',
      'photos.google.com': 'https://ssl.gstatic.com/social/white/br/p-v1.png',
    };
    if (googleIcons[urlObj.hostname]) return googleIcons[urlObj.hostname];

    // 5. Default Google Favicon Service
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=128`;
  } catch (e) {
    return `https://www.google.com/s2/favicons?domain=&sz=128`;
  }
}

async function addUrlToSidebar(url, title) {
  if (!url) return;

  chrome.storage.local.get(['sidebar_links'], async (result) => {
    let links = result.sidebar_links || [];
    if (links.some(l => l.url === url)) return;

    let domain = '';
    try { domain = new URL(url).hostname; } catch (e) { return; }

    const icon = await getSmartFavicon(url);

    const newLink = {
      id: Date.now().toString(),
      title: title,
      url: url,
      color: '#38bdf8',
      isSolid: false,
      newLine: false,
      icon
    };

    links.push(newLink);
    chrome.storage.local.set({ sidebar_links: links }, () => {
      console.log('Added to sidebar:', newLink);
    });
  });
}