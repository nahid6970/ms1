// Load settings on page load
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.sync.get({
    showViewer: true
  }, (settings) => {
    document.getElementById('showViewer').checked = settings.showViewer;
    chrome.storage.local.get({ prompts: null }, (localSettings) => {
      if (Array.isArray(localSettings.prompts)) {
        renderPrompts(localSettings.prompts);
        return;
      }

      // Migrate prompts saved by older versions from sync storage. Long prompts
      // belong in local storage because Chrome sync has a small per-item quota.
      chrome.storage.sync.get({ prompts: [] }, (legacySettings) => {
        const prompts = Array.isArray(legacySettings.prompts) ? legacySettings.prompts : [];
        renderPrompts(prompts);
        chrome.storage.local.set({ prompts });
      });
    });
  });
});

let currentPrompts = [];
let editingIndex = null;

function storageGet(area) {
  return new Promise((resolve) => chrome.storage[area].get(null, resolve));
}

function storageSet(area, data) {
  return new Promise((resolve, reject) => chrome.storage[area].set(data, () => {
    const error = chrome.runtime.lastError;
    if (error) reject(new Error(error.message));
    else resolve();
  }));
}

function storageClear(area) {
  return new Promise((resolve) => chrome.storage[area].clear(resolve));
}

function setStatus(message, color = '#00ff9f', clearAfterMs = 3000) {
  const status = document.getElementById('status');
  status.textContent = message;
  status.style.color = color;

  if (clearAfterMs) {
    setTimeout(() => {
      if (status.textContent === message) {
        status.textContent = '';
      }
    }, clearAfterMs);
  }
}

function sendRuntimeMessage(message) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(message, (response) => {
      resolve(response);
    });
  });
}

function renderPrompts(prompts) {
  currentPrompts = prompts || [];
  const list = document.getElementById('promptsList');
  list.innerHTML = '';
  
  if (currentPrompts.length === 0) {
    list.innerHTML = '<p style="text-align: center; color: #999; font-style: italic;">No prompts added yet.</p>';
    return;
  }

  currentPrompts.forEach((p, index) => {
    const item = document.createElement('div');
    item.className = 'prompt-item';
    const header = document.createElement('div');
    header.className = 'prompt-header';
    const name = document.createElement('span');
    name.className = 'prompt-name';
    name.textContent = p.name;
    const actions = document.createElement('div');
    actions.className = 'prompt-actions';
    const editButton = document.createElement('button');
    editButton.className = 'edit-prompt';
    editButton.dataset.index = index;
    editButton.title = 'Edit prompt';
    editButton.textContent = '✎';
    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-prompt';
    deleteButton.dataset.index = index;
    deleteButton.title = 'Delete prompt';
    deleteButton.textContent = '×';
    actions.append(editButton, deleteButton);
    header.append(name, actions);
    const preview = document.createElement('div');
    preview.className = 'prompt-text-preview';
    preview.textContent = p.text;
    item.append(header, preview);
    list.appendChild(item);
  });
  
  // Add edit listeners
  document.querySelectorAll('.edit-prompt').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = parseInt(e.currentTarget.dataset.index, 10);
      startEditingPrompt(index);
    });
  });

  // Add delete listeners
  document.querySelectorAll('.delete-prompt').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = parseInt(e.currentTarget.dataset.index, 10);
      if (editingIndex === index) {
        clearEditState();
      } else if (editingIndex !== null && index < editingIndex) {
        editingIndex -= 1;
      }
      currentPrompts.splice(index, 1);
      renderPrompts(currentPrompts);
    });
  });
}

function startEditingPrompt(index) {
  const prompt = currentPrompts[index];
  if (!prompt) return;

  editingIndex = index;
  document.getElementById('newPromptName').value = prompt.name;
  document.getElementById('newPromptText').value = prompt.text;

  const addButton = document.getElementById('addPrompt');
  const cancelButton = document.getElementById('cancelEdit');
  addButton.textContent = '[ UPDATE_PROMPT ]';
  cancelButton.hidden = false;
  document.querySelector('.add-prompt-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function clearEditState() {
  editingIndex = null;
  document.getElementById('newPromptName').value = '';
  document.getElementById('newPromptText').value = '';
  document.getElementById('addPrompt').textContent = '[ + ADD_TO_DATABASE ]';
  document.getElementById('cancelEdit').hidden = true;
}

document.getElementById('addPrompt').addEventListener('click', () => {
  const nameInput = document.getElementById('newPromptName');
  const textInput = document.getElementById('newPromptText');
  const name = nameInput.value.trim();
  const text = textInput.value.trim();
  
  if (name && text) {
    const newPrompt = { name, text };

    if (editingIndex === null) {
      currentPrompts.push(newPrompt);
    } else {
      currentPrompts[editingIndex] = newPrompt;
      editingIndex = null;
      document.getElementById('addPrompt').textContent = '[ + ADD_TO_DATABASE ]';
      document.getElementById('cancelEdit').hidden = true;
    }

    renderPrompts(currentPrompts);
    nameInput.value = '';
    textInput.value = '';
  } else {
    alert('Please enter both a name and the prompt text.');
  }
});

document.getElementById('cancelEdit').addEventListener('click', () => {
  clearEditState();
});

document.getElementById('saveToConvex').addEventListener('click', async () => {
  const button = document.getElementById('saveToConvex');
  const originalText = button.textContent;

  try {
    button.disabled = true;
    button.textContent = '[ SAVING... ]';

    const [syncData, localData] = await Promise.all([
      storageGet('sync'),
      storageGet('local')
    ]);

    const response = await sendRuntimeMessage({
      action: 'saveToConvex',
      data: {
        sync: syncData,
        local: localData
      }
    });

    if (response && response.success !== false) {
      setStatus('BACKUP SAVED TO CONVEX!', '#00ff9f');
    } else {
      throw new Error(response?.error || 'Unknown error');
    }
  } catch (error) {
    console.error('Backup to Convex failed:', error);
    setStatus(`BACKUP FAILED: ${error.message}`, '#ff003c', 5000);
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
});

document.getElementById('loadFromConvex').addEventListener('click', async () => {
  const button = document.getElementById('loadFromConvex');
  const originalText = button.textContent;

  try {
    button.disabled = true;
    button.textContent = '[ LOADING... ]';

    const response = await sendRuntimeMessage({ action: 'loadFromConvex' });
    const data = response && response.success !== false ? response.data : null;

    if (!data || typeof data !== 'object') {
      throw new Error(response?.error || 'No backup found in Convex.');
    }

    const syncData = data.sync && typeof data.sync === 'object' ? data.sync : {};
    const localData = data.local && typeof data.local === 'object' ? data.local : {};
    const restoredPrompts = Array.isArray(localData.prompts)
      ? localData.prompts
      : (Array.isArray(syncData.prompts) ? syncData.prompts : []);
    delete syncData.prompts;
    localData.prompts = restoredPrompts;

    await Promise.all([
      storageClear('sync'),
      storageClear('local')
    ]);

    await Promise.all([
      storageSet('sync', syncData),
      storageSet('local', localData)
    ]);

    renderPrompts(restoredPrompts);
    document.getElementById('showViewer').checked = syncData.showViewer !== false;
    clearEditState();

    setStatus('CONVEX BACKUP RESTORED!', '#00ff9f');
  } catch (error) {
    console.error('Restore from Convex failed:', error);
    setStatus(`RESTORE FAILED: ${error.message}`, '#ff003c', 5000);
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
});

// Save settings
document.getElementById('save').addEventListener('click', async () => {
  const button = document.getElementById('save');
  button.disabled = true;
  try {
    await Promise.all([
      storageSet('local', { prompts: currentPrompts }),
      storageSet('sync', { showViewer: document.getElementById('showViewer').checked })
    ]);
    setStatus('SETTINGS SAVED SUCCESSFULLY!', '#28a745');
  } catch (error) {
    setStatus(`SAVE FAILED: ${error.message}`, '#ff003c', 5000);
  } finally {
    button.disabled = false;
  }
});
