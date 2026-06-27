// Load and display saved tabs
function loadTabs() {
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    displayTabs(savedTabs);
  });
}

// Variables for context menu and modal
let currentRightClickedTabId = null;
let currentTabView = 'all';
let currentSearchQuery = '';
let outdatedThresholdDays = 2;
const customContextMenu = document.getElementById('customContextMenu');
const deadlineModal = document.getElementById('deadlineModal');
const editDeadlineDays = document.getElementById('editDeadlineDays');
const editDeadlineDate = document.getElementById('editDeadlineDate');
const editTag = document.getElementById('editTag');
const addTagBtn = document.getElementById('addTagBtn');
const newTagInputContainer = document.getElementById('newTagInputContainer');
const newTagName = document.getElementById('newTagName');
const newTagColor = document.getElementById('newTagColor');
const newTagBorderColor = document.getElementById('newTagBorderColor');
const saveNewTagBtn = document.getElementById('saveNewTagBtn');
const manageTagsList = document.getElementById('manageTagsList');
const viewAllTabsBtn = document.getElementById('viewAllTabs');
const viewOutdatedTabsBtn = document.getElementById('viewOutdatedTabs');
const allTabCount = document.getElementById('allTabCount');
const outdatedTabCount = document.getElementById('outdatedTabCount');
const tabSearch = document.getElementById('tabSearch');

// Tags management
let availableTags = [
  { name: 'applied', color: '#e3f2fd', borderColor: '#bbdefb' },
  { name: 'paid', color: '#c8e6c9', borderColor: '#a5d6a7' }
];

function loadTags() {
  chrome.storage.local.get(['availableTags'], (result) => {
    if (result.availableTags) {
      availableTags = result.availableTags;
      // Handle legacy format (strings or objects without borderColor)
      availableTags = availableTags.map(tag => {
        if (typeof tag === 'string') return { name: tag, color: '#e3f2fd', borderColor: '#bbdefb' };
        if (!tag.borderColor) return { ...tag, borderColor: tag.color }; // Default border to BG color if missing
        return tag;
      });
    }
    populateTagDropdown();
    renderManageTags();
  });
}

function populateTagDropdown() {
  const currentValue = editTag.value;
  editTag.innerHTML = '<option value="">No Tag</option>';
  availableTags.forEach(tag => {
    const option = document.createElement('option');
    option.value = tag.name;
    option.textContent = tag.name.charAt(0).toUpperCase() + tag.name.slice(1);
    editTag.appendChild(option);
  });
  if (availableTags.some(t => t.name === currentValue)) {
    editTag.value = currentValue;
  }
}

function renderManageTags() {
  if (!manageTagsList) return;
  manageTagsList.innerHTML = '';
  availableTags.forEach((tag, index) => {
    const tagItem = document.createElement('div');
    tagItem.className = 'tag-item';
    
    const nameLabel = document.createElement('span');
    nameLabel.textContent = tag.name;
    nameLabel.className = 'tag-name';
    
    const colorInputs = document.createElement('div');
    colorInputs.className = 'tag-colors';

    const bgPicker = document.createElement('input');
    bgPicker.type = 'color';
    bgPicker.value = tag.color;
    bgPicker.title = 'Background Color';
    bgPicker.className = 'theme-color-input tag-color-input';
    bgPicker.oninput = (e) => { availableTags[index].color = e.target.value; };
    bgPicker.onchange = () => { saveTagsAndRefresh(); };
    
    const borderPicker = document.createElement('input');
    borderPicker.type = 'color';
    borderPicker.value = tag.borderColor || tag.color;
    borderPicker.title = 'Border Color';
    borderPicker.className = 'theme-color-input tag-color-input';
    borderPicker.oninput = (e) => { availableTags[index].borderColor = e.target.value; };
    borderPicker.onchange = () => { saveTagsAndRefresh(); };
    
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = '×';
    deleteBtn.className = 'tag-delete-btn';
    deleteBtn.onclick = () => {
      if (confirm(`Delete tag "${tag.name}"?`)) {
        availableTags.splice(index, 1);
        saveTagsAndRefresh();
      }
    };
    
    colorInputs.appendChild(bgPicker);
    colorInputs.appendChild(borderPicker);
    tagItem.appendChild(nameLabel);
    tagItem.appendChild(colorInputs);
    tagItem.appendChild(deleteBtn);
    manageTagsList.appendChild(tagItem);
  });
}

function saveTagsAndRefresh() {
  chrome.storage.local.set({ availableTags }, () => {
    populateTagDropdown();
    // We don't call renderManageTags() here on purpose to avoid destroying the color picker while open
    loadTabs(); // Refresh list to show new colors
  });
}

addTagBtn.onclick = () => {
  newTagInputContainer.style.display = newTagInputContainer.style.display === 'none' ? 'flex' : 'none';
  if (newTagInputContainer.style.display === 'flex') {
    newTagName.focus();
  }
};

saveNewTagBtn.onclick = () => {
  const tagName = newTagName.value.trim().toLowerCase();
  const color = newTagColor.value;
  const borderColor = newTagBorderColor.value;
  if (tagName && !availableTags.some(t => t.name === tagName)) {
    availableTags.push({ name: tagName, color: color, borderColor: borderColor });
    chrome.storage.local.set({ availableTags }, () => {
      populateTagDropdown();
      renderManageTags();
      editTag.value = tagName;
      newTagName.value = '';
      newTagInputContainer.style.display = 'none';
      loadTabs();
    });
  }
};

// Display tabs in the popup
function displayTabs(tabs) {
  const tabList = document.getElementById('tabList');

  const totalTabs = tabs.length;
  const outdatedTabs = tabs.filter(tab => isOutdatedDeadline(tab));
  const nonOutdatedTabs = tabs.filter(tab => !isOutdatedDeadline(tab));
  const filteredTabs = tabs.filter(tab => matchesSearch(tab, currentSearchQuery));
  const visibleTabs = currentTabView === 'outdated'
    ? filteredTabs.filter(tab => isOutdatedDeadline(tab))
    : filteredTabs.filter(tab => !isOutdatedDeadline(tab));

  allTabCount.textContent = nonOutdatedTabs.length;
  outdatedTabCount.textContent = outdatedTabs.length;

  setActiveViewButton(currentTabView);

  // Sort tabs: deadlines first (soonest first), then newest first for those without deadlines
  visibleTabs.sort((a, b) => {
    if (a.deadline && b.deadline) {
      return a.deadline - b.deadline;
    }
    if (a.deadline) return -1;
    if (b.deadline) return 1;
    return b.id - a.id;
  });

  if (totalTabs === 0) {
    tabList.innerHTML = `
      <div class="empty-state">
        <p>No saved tabs yet!</p>
        <p class="hint">Right-click on any page and select "Save & Close Tab"</p>
      </div>
    `;
    return;
  }

  if (visibleTabs.length === 0) {
    let noResults, noResultsHint;
    if (currentSearchQuery.trim()) {
      noResults = `No tabs match "${currentSearchQuery.trim()}".`;
      noResultsHint = 'Try a different title, URL, or tag.';
    } else if (currentTabView === 'outdated') {
      noResults = 'No outdated deadlines yet!';
      noResultsHint = `This view shows tabs whose deadlines are at least ${outdatedThresholdDays} days past due.`;
    } else {
      noResults = 'No active tabs here!';
      noResultsHint = 'All your saved tabs are in the outdated section.';
    }
    tabList.innerHTML = `
      <div class="empty-state">
        <p>${noResults}</p>
        <p class="hint">${noResultsHint}</p>
      </div>
    `;
    return;
  }

  tabList.innerHTML = '';

  visibleTabs.forEach((tab) => {
    const tabItem = document.createElement('div');
    tabItem.className = 'tab-item';
    
    // Custom context menu for tab items
    tabItem.oncontextmenu = (e) => {
      e.preventDefault();
      currentRightClickedTabId = tab.id;
      
      // Position menu
      customContextMenu.style.top = `${e.clientY}px`;
      customContextMenu.style.left = `${e.clientX}px`;
      customContextMenu.classList.add('show');
      
      // Close menu when clicking elsewhere
      const closeMenu = () => {
        customContextMenu.classList.remove('show');
        document.removeEventListener('click', closeMenu);
      };
      setTimeout(() => document.addEventListener('click', closeMenu), 10);
    };
    
    const isYouTube = tab.url.includes('youtube.com/watch');
    const fallbackGlobe = "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>🌐</text></svg>";
    const fallbackYT = "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>▶️</text></svg>";
    const favicon = tab.favicon || fallbackGlobe;

    let faviconHTML;
    if (isYouTube && tab.channelIcon) {
      faviconHTML = `
        <div class="tab-favicon-container">
          <img src="${favicon}" class="tab-favicon-yt" loading="lazy" decoding="async" onerror="this.src='${fallbackYT}'">
          <img src="${tab.channelIcon}" class="tab-favicon-channel" loading="lazy" decoding="async" onerror="this.style.display='none'">
        </div>
      `;
    } else {
      faviconHTML = `<img src="${favicon}" class="tab-favicon" loading="lazy" decoding="async" onerror="this.src='${fallbackGlobe}'">`;
    }
    
    // Tag HTML
    let tagHTML = '';
    if (tab.tag) {
      const tagInfo = availableTags.find(t => t.name === tab.tag);
      const color = tagInfo ? tagInfo.color : '#e3f2fd';
      const bColor = tagInfo ? (tagInfo.borderColor || tagInfo.color) : '#bbdefb';
      
      // Calculate a readable text color based on background
      const getContrastYIQ = (hexcolor) => {
        hexcolor = hexcolor.replace("#", "");
        const r = parseInt(hexcolor.substr(0, 2), 16);
        const g = parseInt(hexcolor.substr(2, 2), 16);
        const b = parseInt(hexcolor.substr(4, 2), 16);
        const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
        return (yiq >= 128) ? '#1a1a24' : '#ffffff';
      };
      const textColor = getContrastYIQ(color);
      
      tagHTML = `<div class="tab-tag" style="background-color: ${color} !important; color: ${textColor} !important; border: 1.5px solid ${bColor} !important; margin-left: auto; padding: 3px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase;">${tab.tag}</div>`;
    }

    // Calculate days left for deadline
    let deadlineHTML = '';
    if (tab.deadline) {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
      const target = new Date(tab.deadline);
      const targetDate = new Date(target.getFullYear(), target.getMonth(), target.getDate()).getTime();
      
      const diffDays = Math.round((targetDate - today) / (1000 * 60 * 60 * 24));
      
      let badgeClass = 'tab-deadline';
      let text = '';
      
      if (diffDays < 0) {
        text = '!!';
        badgeClass += ' urgent';
      } else if (diffDays === 0) {
        text = '0';
        badgeClass += ' urgent';
      } else {
        text = `${diffDays}`;
        if (diffDays <= 3) badgeClass += ' urgent';
        else badgeClass += ' safe';
      }
      
      deadlineHTML = `<div class="${badgeClass}" style="margin-left: 8px;">${text}</div>`;
    }
    
    tabItem.innerHTML = `
      ${faviconHTML}
      <div class="tab-info" data-url="${tab.url}">
        <div class="tab-title">${tab.title}</div>
        <div class="tab-url">${tab.url}</div>
      </div>
      ${tagHTML}
      ${deadlineHTML}
      <button class="tab-remove" data-id="${tab.id}">×</button>
    `;
    
    const tabInfo = tabItem.querySelector('.tab-info');
    tabInfo.title = `${tab.title}\n${tab.url}`;
    tabInfo.addEventListener('click', () => {
      chrome.tabs.create({ url: tab.url });
    });
    
    const removeBtn = tabItem.querySelector('.tab-remove');
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      removeTab(tab.id);
    });
    
    tabList.appendChild(tabItem);
  });
}

function isOutdatedDeadline(tab) {
  if (!tab.deadline) return false;
  const deadline = Number(tab.deadline);
  if (Number.isNaN(deadline)) return false;
  const thresholdMs = outdatedThresholdDays * 24 * 60 * 60 * 1000;
  return Date.now() - deadline >= thresholdMs;
}

function matchesSearch(tab, query) {
  const value = query.trim().toLowerCase();
  if (!value) return true;
  const haystack = [
    tab.title || '',
    tab.url || '',
    tab.tag || ''
  ].join(' ').toLowerCase();
  return haystack.includes(value);
}

function setActiveViewButton(view) {
  const isOutdated = view === 'outdated';
  viewAllTabsBtn.classList.toggle('active', !isOutdated);
  viewOutdatedTabsBtn.classList.toggle('active', isOutdated);
  viewAllTabsBtn.setAttribute('aria-selected', String(!isOutdated));
  viewOutdatedTabsBtn.setAttribute('aria-selected', String(isOutdated));
}

viewAllTabsBtn.addEventListener('click', () => {
  currentTabView = 'all';
  loadTabs();
});

viewOutdatedTabsBtn.addEventListener('click', () => {
  currentTabView = 'outdated';
  loadTabs();
});

tabSearch.addEventListener('input', (e) => {
  currentSearchQuery = e.target.value;
  loadTabs();
});

// Open deadline modal from context menu
document.getElementById('menuSetDeadline').onclick = () => {
  editDeadlineDays.value = '';
  editDeadlineDate.value = '';
  
  // Set current tag and deadline
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    const tab = savedTabs.find(t => t.id === currentRightClickedTabId);
    if (tab) {
      editTag.value = tab.tag || '';
      if (tab.deadline) {
        const date = new Date(tab.deadline);
        // Format to YYYY-MM-DD for the date input
        const yyyy = date.getFullYear();
        const mm = String(date.getMonth() + 1).padStart(2, '0');
        const dd = String(date.getDate()).padStart(2, '0');
        editDeadlineDate.value = `${yyyy}-${mm}-${dd}`;
      }
    }
  });
  
  newTagInputContainer.style.display = 'none';
  deadlineModal.classList.add('show');
};

// Handle deadline and tag update
document.getElementById('saveDeadlineBtn').onclick = () => {
  const days = editDeadlineDays.value;
  const date = editDeadlineDate.value;
  const tag = editTag.value;
  let deadline = null;
  
  if (date) {
    const d = new Date(date);
    d.setHours(23, 59, 59, 999);
    deadline = d.getTime();
  } else if (days) {
    const d = new Date();
    d.setDate(d.getDate() + parseInt(days));
    d.setHours(23, 59, 59, 999);
    deadline = d.getTime();
  }
  
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    const updatedTabs = savedTabs.map(tab => {
      if (tab.id === currentRightClickedTabId) {
        // Keep existing deadline if no new one provided
        const finalDeadline = (deadline !== null) ? deadline : tab.deadline;
        return { ...tab, deadline: finalDeadline, tag: tag };
      }
      return tab;
    });
    
    chrome.storage.local.set({ savedTabs: updatedTabs }, () => {
      deadlineModal.classList.remove('show');
      loadTabs();
    });
  });
};

// Close deadline modals
document.getElementById('closeDeadlineModal').onclick = () => deadlineModal.classList.remove('show');
document.getElementById('cancelDeadlineBtn').onclick = () => deadlineModal.classList.remove('show');

// Clear inputs when one is used
editDeadlineDays.addEventListener('input', () => { if (editDeadlineDays.value) editDeadlineDate.value = ''; });
editDeadlineDate.addEventListener('input', () => { if (editDeadlineDays.value) editDeadlineDays.value = ''; });

// Remove a tab from the list
function removeTab(tabId) {
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    const updatedTabs = savedTabs.filter(tab => tab.id !== tabId);
    
    chrome.storage.local.set({ savedTabs: updatedTabs }, () => {
      loadTabs();
    });
  });
}

// Save the current active tab
document.getElementById('saveCurrentTab').addEventListener('click', (e) => {
  const button = e.target;
  chrome.tabs.query({ active: true, currentWindow: true }, (browserTabs) => {
    const tab = browserTabs[0];
    if (!tab || !tab.url) {
      showButtonFeedback(button, false, 'No tab');
      return;
    }
    chrome.storage.local.get(['savedTabs'], (result) => {
      const savedTabs = result.savedTabs || [];
      if (savedTabs.some(t => t.url === tab.url)) {
        showButtonFeedback(button, false, 'Already saved');
        return;
      }
      const newTab = { id: Date.now(), title: tab.title || tab.url, url: tab.url, favicon: tab.favIconUrl || '' };
      chrome.storage.local.set({ savedTabs: [...savedTabs, newTab] }, () => {
        showButtonFeedback(button, true, 'Saved!');
        loadTabs();
        // Open deadline modal for the newly saved tab
        currentRightClickedTabId = newTab.id;
        editDeadlineDays.value = '';
        editDeadlineDate.value = '';
        editTag.value = '';
        newTagInputContainer.style.display = 'none';
        deadlineModal.classList.add('show');
      });
    });
  });
});

// Add all currently open browser tabs
document.getElementById('addAllTabs').addEventListener('click', (e) => {
  const button = e.target;
  chrome.tabs.query({}, (browserTabs) => {
    chrome.storage.local.get(['savedTabs'], (result) => {
      const savedTabs = result.savedTabs || [];
      const existingUrls = new Set(savedTabs.map(t => t.url));
      const newTabs = browserTabs
        .filter(t => t.url && !existingUrls.has(t.url))
        .map(t => ({ id: Date.now() + Math.random(), title: t.title || t.url, url: t.url, favicon: t.favIconUrl || '' }));
      if (newTabs.length === 0) {
        showButtonFeedback(button, false, 'No new tabs');
        return;
      }
      chrome.storage.local.set({ savedTabs: [...savedTabs, ...newTabs] }, () => {
        showButtonFeedback(button, true, `Added ${newTabs.length}!`);
        loadTabs();
      });
    });
  });
});

// Clear all tabs
document.getElementById('clearAll').addEventListener('click', (e) => {
  const button = e.target;
  chrome.storage.local.get(['savedTabs'], (result) => {
    const savedTabs = result.savedTabs || [];
    
    if (savedTabs.length === 0) {
      showButtonFeedback(button, false, 'No tabs to clear');
      return;
    }
    
    chrome.storage.local.set({ savedTabs: [] }, () => {
      showButtonFeedback(button, true, 'Cleared!');
      loadTabs();
    });
  });
});

// Show button feedback
function showButtonFeedback(button, success, message) {
  const originalText = button.innerHTML;
  if (success) {
    button.innerHTML = '✓ ' + message;
    button.style.background = '#4CAF50';
  } else {
    button.innerHTML = '✗ ' + message;
    button.style.background = '#f44336';
  }
  button.disabled = true;
  setTimeout(() => {
    button.innerHTML = originalText;
    button.style.background = '';
    button.disabled = false;
  }, 2000);
}

// Save to Convex
document.getElementById('saveToConvex').addEventListener('click', (e) => {
  const button = e.target;
  chrome.storage.local.get(null, (items) => {
    chrome.runtime.sendMessage({
      action: 'saveToConvex',
      data: items
    }, (response) => {
      if (response && response.success !== false) {
        showButtonFeedback(button, true, 'Saved!');
      } else {
        showButtonFeedback(button, false, 'Failed');
      }
    });
  });
});

// Load from Convex
document.getElementById('loadFromConvex').addEventListener('click', (e) => {
  const button = e.target;
  chrome.runtime.sendMessage({ action: 'loadFromConvex' }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('loadFromConvex runtime error:', chrome.runtime.lastError.message);
      showButtonFeedback(button, false, 'Error');
      return;
    }
    console.log('loadFromConvex response:', response);
    if (response && response.success && response.data) {
      // response.data may be the full storage object or just { savedTabs: [...] }
      const dataToSet = (typeof response.data === 'object' && !Array.isArray(response.data))
        ? response.data
        : { savedTabs: response.data };
      chrome.storage.local.set(dataToSet, () => {
        showButtonFeedback(button, true, 'Loaded!');
        loadTabs();
      });
    } else {
      console.error('loadFromConvex failed:', response);
      showButtonFeedback(button, false, response?.error || 'Failed');
    }
  });
});

// Settings functionality
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeModal = document.getElementById('closeModal');
const resetSettings = document.getElementById('resetSettings');

// Inputs
const ytIconSize = document.getElementById('ytIconSize');
const channelIconSize = document.getElementById('channelIconSize');
const ytIconValue = document.getElementById('ytIconValue');
const channelIconValue = document.getElementById('channelIconValue');
const outdatedThreshold = document.getElementById('outdatedThreshold');
const outdatedThresholdValue = document.getElementById('outdatedThresholdValue');
const outdatedTabLabel = document.getElementById('outdatedTabLabel');

const urgentBg = document.getElementById('urgentBg');
const urgentFg = document.getElementById('urgentFg');
const urgentBorder = document.getElementById('urgentBorder');
const urgentBold = document.getElementById('urgentBold');

const safeBg = document.getElementById('safeBg');
const safeFg = document.getElementById('safeFg');
const safeBorder = document.getElementById('safeBorder');
const safeBold = document.getElementById('safeBold');

// Load saved settings
function loadSettings() {
  chrome.storage.local.get(['iconSettings', 'deadlineSettings'], (result) => {
    const iconSettings = result.iconSettings || { ytIconSize: 20, channelIconSize: 18 };
    const deadlineSettings = result.deadlineSettings || {
      urgentBg: '#ff4757', urgentFg: '#ffffff', urgentBorder: '#eb3b5a', urgentBold: true,
      safeBg: '#e3f2fd', safeFg: '#1976d2', safeBorder: '#bbdefb', safeBold: false,
      outdatedThreshold: 2
    };
    if (deadlineSettings.outdatedThreshold === undefined) {
      deadlineSettings.outdatedThreshold = 2;
    }
    
    // Set global threshold
    outdatedThresholdDays = deadlineSettings.outdatedThreshold;
    
    // Icons
    ytIconSize.value = iconSettings.ytIconSize;
    channelIconSize.value = iconSettings.channelIconSize;
    ytIconValue.textContent = iconSettings.ytIconSize + 'px';
    channelIconValue.textContent = iconSettings.channelIconSize + 'px';
    
    // Deadlines
    urgentBg.value = deadlineSettings.urgentBg;
    urgentFg.value = deadlineSettings.urgentFg;
    urgentBorder.value = deadlineSettings.urgentBorder;
    urgentBold.checked = deadlineSettings.urgentBold;
    
    safeBg.value = deadlineSettings.safeBg;
    safeFg.value = deadlineSettings.safeFg;
    safeBorder.value = deadlineSettings.safeBorder;
    safeBold.checked = deadlineSettings.safeBold;
    
    // Outdated Threshold
    outdatedThreshold.value = deadlineSettings.outdatedThreshold;
    outdatedThresholdValue.textContent = deadlineSettings.outdatedThreshold + ' days';
    if (outdatedTabLabel) {
      outdatedTabLabel.textContent = `Outdated +${deadlineSettings.outdatedThreshold}d`;
    }
    
    applySettings(iconSettings, deadlineSettings);
  });
}

// Apply settings to CSS
function applySettings(icons, deadlines) {
  const styleId = 'dynamic-settings-styles';
  let style = document.getElementById(styleId);
  if (style) style.remove();
  
  style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    .tab-favicon-container { width: ${icons.ytIconSize}px !important; height: ${icons.ytIconSize}px !important; }
    .tab-favicon-yt { width: ${icons.ytIconSize}px !important; height: ${icons.ytIconSize}px !important; }
    .tab-favicon-channel { width: ${icons.channelIconSize}px !important; height: ${icons.channelIconSize}px !important; }
    
    .tab-deadline.urgent { 
      background-color: ${deadlines.urgentBg} !important; 
      color: ${deadlines.urgentFg} !important; 
      border-color: ${deadlines.urgentBorder} !important; 
      font-weight: ${deadlines.urgentBold ? '900' : '500'} !important;
    }
    .tab-deadline.safe { 
      background-color: ${deadlines.safeBg} !important; 
      color: ${deadlines.safeFg} !important; 
      border-color: ${deadlines.safeBorder} !important; 
      font-weight: ${deadlines.safeBold ? '900' : '500'} !important;
    }
  `;
  document.head.appendChild(style);
}

// Save settings
function saveAllSettings() {
  const iconSettings = {
    ytIconSize: parseInt(ytIconSize.value),
    channelIconSize: parseInt(channelIconSize.value)
  };
  const deadlineSettings = {
    urgentBg: urgentBg.value, urgentFg: urgentFg.value, urgentBorder: urgentBorder.value, urgentBold: urgentBold.checked,
    safeBg: safeBg.value, safeFg: safeFg.value, safeBorder: safeBorder.value, safeBold: safeBold.checked,
    outdatedThreshold: parseInt(outdatedThreshold.value)
  };
  
  // Update global variable
  outdatedThresholdDays = deadlineSettings.outdatedThreshold;
  if (outdatedTabLabel) {
    outdatedTabLabel.textContent = `Outdated +${outdatedThresholdDays}d`;
  }
  
  chrome.storage.local.set({ iconSettings, deadlineSettings }, () => {
    applySettings(iconSettings, deadlineSettings);
    loadTabs(); // Refresh the tab lists to reflect changes with new threshold
  });
}

// Event Listeners
[ytIconSize, channelIconSize, outdatedThreshold, urgentBg, urgentFg, urgentBorder, urgentBold, safeBg, safeFg, safeBorder, safeBold].forEach(el => {
  const eventType = el.type === 'checkbox' ? 'change' : 'input';
  el.addEventListener(eventType, () => {
    if (el === ytIconSize) ytIconValue.textContent = el.value + 'px';
    if (el === channelIconSize) channelIconValue.textContent = el.value + 'px';
    if (el === outdatedThreshold) outdatedThresholdValue.textContent = el.value + ' days';
    saveAllSettings();
  });
});

settingsBtn.addEventListener('click', () => settingsModal.classList.add('show'));
closeModal.addEventListener('click', () => settingsModal.classList.remove('show'));
settingsModal.addEventListener('click', (e) => { if (e.target === settingsModal) settingsModal.classList.remove('show'); });

resetSettings.addEventListener('click', () => {
  ytIconSize.value = 20;
  channelIconSize.value = 18;
  outdatedThreshold.value = 2;
  urgentBg.value = '#ff4757';
  urgentFg.value = '#ffffff';
  urgentBorder.value = '#eb3b5a';
  urgentBold.checked = true;
  safeBg.value = '#e3f2fd';
  safeFg.value = '#1976d2';
  safeBorder.value = '#bbdefb';
  safeBold.checked = false;
  saveAllSettings();
  loadSettings();
});

// Initial load
loadTabs();
loadSettings();
loadTags();
