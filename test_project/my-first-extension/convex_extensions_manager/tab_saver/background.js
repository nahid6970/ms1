// Replace with your actual Convex URL from 'npx convex dev'
const CONVEX_URL = "https://joyous-stingray-672.convex.cloud"; 
const EXTENSION_NAME = 'tab_saver';

async function convexFetch(type, path, args) {
  const url = `${CONVEX_URL}/api/${type}`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      path,
      args,
      format: "json"
    })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Convex HTTP error (${response.status}): ${text}`);
  }
  const result = await response.json();
  if (result && (result.status === "error" || result.errorMessage !== undefined)) {
    throw new Error(result.errorMessage || "Convex error");
  }
  return result.value;
}

// Send data to Convex
async function sendDataToConvex(data) {
  try {
    const result = await convexFetch("mutation", "functions:save", {
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
    const data = await convexFetch("query", "functions:get", { extensionName: EXTENSION_NAME });
    console.log('Raw data loaded from Convex:', JSON.stringify(data));
    return { success: true, data };
  } catch (error) {
    console.error('Failed to load data from Convex:', error);
    return { success: false, error: error.message };
  }
}


// Auto-save on storage changes (debounced to avoid rapid-fire Convex requests)
let autoSaveTimer = null;
chrome.storage.local.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local') {
    updateBadge();
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
      chrome.storage.local.get(null, (items) => {
        sendDataToConvex(items);
      });
    }, 1500);
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
      chrome.action.setBadgeBackgroundColor({ color: '#00f3ff' }); 
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
    (async () => {
      const sharedModalCss = await fetch(chrome.runtime.getURL('shared-modal.css')).then((response) => response.text());

      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        args: [sharedModalCss],
        func: (sharedModalCssText) => {
        try {
          const id = 'tab-saver-deadline-modal';
          if (document.getElementById(id)) return;

          let style = document.getElementById(id + '-style');
          if (!style) {
            style = document.createElement('style');
            style.id = id + '-style';
            style.textContent = sharedModalCssText;
            document.head.appendChild(style);
          }

          const overlay = document.createElement('div');
          overlay.id = id + '-overlay';
          overlay.className = 'shared-modal-overlay';
          
          const modal = document.createElement('div');
          modal.id = id;
          modal.className = 'shared-modal';
          
          modal.innerHTML = `
            <div class="modal-theme-header">
              <span class="modal-theme-title">Edit</span>
              <button id="closeBtn" class="close-btn modal-theme-close">&times;</button>
            </div>
            
            <div class="modal-theme-body">
              <div class="modal-field">
                <label for="deadlineDays">Days from today</label>
                <input type="number" id="deadlineDays" min="1" class="modal-input">
              </div>
              
              <div class="modal-field">
                <label for="deadlineDate">Pick a date</label>
                <input type="date" id="deadlineDate" class="modal-input modal-date-input">
              </div>

              <div class="modal-field">
                <label for="deadlineTag">Tag</label>
                <div class="modal-inline-row">
                  <select id="deadlineTag" class="modal-select">
                    <option value="">No Tag</option>
                  </select>
                  <button id="addTagBtn" class="modal-add-btn">+</button>
                </div>
              </div>

              <div id="newTagContainer" class="modal-field modal-new-tag" style="display: none;">
                <label for="newTagName">New Tag Name</label>
                <div class="modal-inline-row">
                  <input type="text" id="newTagName" placeholder="Enter tag name..." class="modal-input">
                  <button id="saveNewTagBtn" class="modal-primary-btn">Add</button>
                </div>
              </div>
              
              <div class="modal-actions">
                <button id="cancelBtn" class="btn btn-secondary">Cancel</button>
                <button id="saveBtn" class="btn btn-primary">Save & Close</button>
              </div>
            </div>
          `;
          
          document.body.appendChild(overlay);
          document.body.appendChild(modal);

          const daysInput = modal.querySelector('#deadlineDays');
          const dateInput = modal.querySelector('#deadlineDate');
          const tagSelect = modal.querySelector('#deadlineTag');
          const addTagBtn = modal.querySelector('#addTagBtn');
          const newTagContainer = modal.querySelector('#newTagContainer');
          const newTagName = modal.querySelector('#newTagName');
          const saveNewTagBtn = modal.querySelector('#saveNewTagBtn');
          const cancelBtn = modal.querySelector('#cancelBtn');
          const saveBtn = modal.querySelector('#saveBtn');

          // Load tags
          chrome.storage.local.get(['availableTags'], (result) => {
            const tags = result.availableTags || [{ name: 'applied', color: '#e3f2fd' }, { name: 'paid', color: '#c8e6c9' }];
            tags.forEach(tag => {
              const name = typeof tag === 'string' ? tag : tag.name;
              const option = document.createElement('option');
              option.value = name;
              option.textContent = name.charAt(0).toUpperCase() + name.slice(1);
              tagSelect.appendChild(option);
            });
          });

          addTagBtn.onclick = () => {
            newTagContainer.style.display = newTagContainer.style.display === 'none' ? 'flex' : 'none';
          };

          saveNewTagBtn.onclick = () => {
            const tagName = newTagName.value.trim().toLowerCase();
            if (tagName) {
              chrome.storage.local.get(['availableTags'], (result) => {
                const tags = result.availableTags || [{ name: 'applied', color: '#e3f2fd' }, { name: 'paid', color: '#c8e6c9' }];
                // Check if tag already exists (handling both strings and objects)
                const exists = tags.some(t => (typeof t === 'string' ? t : t.name) === tagName);
                if (!exists) {
                  tags.push({ name: tagName, color: '#e3f2fd' });
                  chrome.storage.local.set({ availableTags: tags }, () => {
                    const option = document.createElement('option');
                    option.value = tagName;
                    option.textContent = tagName.charAt(0).toUpperCase() + tagName.slice(1);
                    tagSelect.appendChild(option);
                    tagSelect.value = tagName;
                    newTagName.value = '';
                    newTagContainer.style.display = 'none';
                  });
                }
              });
            }
          };

          daysInput.focus();

          daysInput.addEventListener('input', () => { if (daysInput.value) dateInput.value = ''; });
          dateInput.addEventListener('input', () => { if (dateInput.value) daysInput.value = ''; });

          const removeUI = () => {
            document.body.removeChild(modal);
            document.body.removeChild(overlay);
          };

          const finish = (deadline, tag) => {
            chrome.runtime.sendMessage({ action: 'deadlineSelected', deadline: deadline, tag: tag });
            removeUI();
          };
          
          modal.querySelector('#cancelBtn').onclick = (e) => { e.stopPropagation(); removeUI(); };
          modal.querySelector('#closeBtn').onclick = (e) => { e.stopPropagation(); removeUI(); };
          
          modal.querySelector('#saveBtn').onclick = (e) => {
            e.stopPropagation();
            const days = daysInput.value;
            const date = dateInput.value;
            const tag = tagSelect.value;
            if (date) {
              const d = new Date(date);
              d.setHours(23, 59, 59, 999);
              finish(d.getTime(), tag);
            } else if (days) {
              const d = new Date();
              d.setDate(d.getDate() + parseInt(days));
              d.setHours(23, 59, 59, 999);
              finish(d.getTime(), tag);
            } else {
              finish(null, tag);
            }
          };

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
      });
    })().catch((err) => {
      console.error('Failed to inject script:', err);
      handleTabSaving(tab, null, null);
    });
  }
});

// Main function to handle tab saving logic
function handleTabSaving(tab, deadline, tag) {
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
        saveTab(savedTabs, tab, favicon, channelIcon, deadline, tag);
      }).catch(() => {
        saveTab(savedTabs, tab, favicon, null, deadline, tag);
      });
    } else {
      saveTab(savedTabs, tab, favicon, null, deadline, tag);
    }
  });
}

// Helper function to save tab
function saveTab(savedTabs, tab, favicon, channelIcon = null, deadline = null, tag = null) {
  const newTab = {
    id: Date.now(),
    title: tab.title,
    url: tab.url,
    favicon: favicon,
    channelIcon: channelIcon,
    savedAt: new Date().toISOString(),
    deadline: deadline,
    tag: tag
  };
  
  savedTabs.unshift(newTab);
  
  chrome.storage.local.set({ savedTabs: savedTabs }, () => {
    chrome.tabs.remove(tab.id);
  });
}

// Handle messages from injected scripts or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'deadlineSelected') {
    handleTabSaving(sender.tab, message.deadline, message.tag);
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



// Update badge on startup
updateBadge();
