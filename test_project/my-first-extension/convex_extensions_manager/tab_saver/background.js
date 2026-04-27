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
    console.log('Context menu clicked for tab:', tab.id);
    
    // Attempt to inject the deadline modal
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        try {
          const id = 'tab-saver-deadline-modal';
          if (document.getElementById(id)) return;

          const overlay = document.createElement('div');
          overlay.id = id + '-overlay';
          overlay.style = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2147483646; transition: opacity 0.3s; pointer-events: auto;';
          
          const modal = document.createElement('div');
          modal.id = id;
          modal.style = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 25px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); z-index: 2147483647; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; gap: 15px; width: 320px; color: #333; line-height: 1.5; pointer-events: auto;';
          
          modal.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">⏰</span>
                <h3 style="margin:0; font-size: 18px; font-weight: 600; color: #333;">Set Deadline</h3>
              </div>
              <button id="closeBtn" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #999; padding: 5px;">&times;</button>
            </div>
            <p style="margin: 0; font-size: 13px; color: #666;">Optional: Track days left for this task.</p>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <label style="font-size: 12px; font-weight: 600; color: #444;">Days from today:</label>
              <input type="number" id="deadlineDays" min="1" style="padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; background: white; color: black; width: 100%;">
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <label style="font-size: 12px; font-weight: 600; color: #444;">Pick a date:</label>
              <input type="date" id="deadlineDate" style="padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; cursor: pointer; background: white; color: black; width: 100%;">
            </div>
            <div style="display: flex; gap: 12px; margin-top: 10px;">
              <button id="cancelBtn" style="flex: 1; padding: 12px; border: 1px solid #ddd; background: white; color: #666; font-weight: 600; border-radius: 8px; cursor: pointer; font-size: 14px;">Cancel</button>
              <button id="saveBtn" style="flex: 1.5; padding: 12px; border: none; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 600; border-radius: 8px; cursor: pointer; font-size: 14px;">Save & Close</button>
            </div>
          `;
          
          document.body.appendChild(overlay);
          document.body.appendChild(modal);

          const daysInput = modal.querySelector('#deadlineDays');
          const dateInput = modal.querySelector('#deadlineDate');
          daysInput.focus();

          daysInput.addEventListener('input', () => { if (daysInput.value) dateInput.value = ''; });
          dateInput.addEventListener('input', () => { if (dateInput.value) daysInput.value = ''; });

          const removeUI = () => {
            document.body.removeChild(modal);
            document.body.removeChild(overlay);
          };

          const finish = (deadline) => {
            chrome.runtime.sendMessage({ action: 'deadlineSelected', deadline: deadline });
            removeUI();
          };
          
          modal.querySelector('#cancelBtn').onclick = (e) => { e.stopPropagation(); removeUI(); };
          modal.querySelector('#closeBtn').onclick = (e) => { e.stopPropagation(); removeUI(); };
          
          modal.querySelector('#saveBtn').onclick = (e) => {
            e.stopPropagation();
            const days = daysInput.value;
            const date = dateInput.value;
            if (date) {
              const d = new Date(date);
              d.setHours(23, 59, 59, 999);
              finish(d.getTime());
            } else if (days) {
              const d = new Date();
              d.setDate(d.getDate() + parseInt(days));
              d.setHours(23, 59, 59, 999);
              finish(d.getTime());
            } else {
              // No input means no deadline, but still save and close
              finish(null);
            }
          };

          // Close on escape
          window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.getElementById(id)) {
              removeUI();
            }
          }, { once: true });

        } catch (e) {
          console.error('Modal injection error:', e);
          chrome.runtime.sendMessage({ action: 'deadlineSelected', deadline: null, error: e.message });
        }
      }
    }).catch((err) => {
      console.error('Failed to inject script:', err);
      handleTabSaving(tab, null);
    });
  }
});

// Main function to handle tab saving logic
function handleTabSaving(tab, deadline) {
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    let favicon = tab.favIconUrl || '';
    
    if (tab.url.includes('youtube.com/watch')) {
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const selectors = ['#owner #avatar img', 'ytd-video-owner-renderer #avatar img', '#channel-thumbnail img', 'yt-img-shadow img', '#avatar img'];
          for (const selector of selectors) {
            const img = document.querySelector(selector);
            if (img && img.src && !img.src.includes('data:')) return img.src;
          }
          return null;
        }
      }).then((results) => {
        const channelIcon = (results && results[0] && results[0].result) ? results[0].result : null;
        saveTab(savedTabs, tab, favicon, channelIcon, deadline);
      }).catch(() => {
        saveTab(savedTabs, tab, favicon, null, deadline);
      });
    } else {
      saveTab(savedTabs, tab, favicon, null, deadline);
    }
  });
}

// Helper function to save tab
function saveTab(savedTabs, tab, favicon, channelIcon = null, deadline = null) {
  const newTab = {
    id: Date.now(),
    title: tab.title,
    url: tab.url,
    favicon: favicon,
    channelIcon: channelIcon,
    savedAt: new Date().toISOString(),
    deadline: deadline
  };
  
  savedTabs.unshift(newTab);
  
  chrome.storage.local.set({ savedTabs: savedTabs }, () => {
    chrome.tabs.remove(tab.id);
  });
}

// Handle messages from injected scripts or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'deadlineSelected') {
    handleTabSaving(sender.tab, message.deadline);
  }
  
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
