// Load settings on page load
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.sync.get({
    prompts: [],
    showViewer: true
  }, (settings) => {
    document.getElementById('showViewer').checked = settings.showViewer;
    renderPrompts(settings.prompts);
  });
});

let currentPrompts = [];
let editingIndex = null;

function storageGet(area) {
  return new Promise((resolve) => chrome.storage[area].get(null, resolve));
}

function storageSet(area, data) {
  return new Promise((resolve) => chrome.storage[area].set(data, resolve));
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
    item.innerHTML = `
      <div class="prompt-header">
        <span class="prompt-name">${p.name}</span>
        <div class="prompt-actions">
          <button class="edit-prompt" data-index="${index}" title="Edit prompt">✎</button>
          <button class="delete-prompt" data-index="${index}" title="Delete prompt">×</button>
        </div>
      </div>
      <div class="prompt-text-preview">${p.text}</div>
    `;
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

    await Promise.all([
      storageClear('sync'),
      storageClear('local')
    ]);

    await Promise.all([
      storageSet('sync', syncData),
      storageSet('local', localData)
    ]);

    const restoredPrompts = Array.isArray(syncData.prompts) ? syncData.prompts : [];
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
document.getElementById('save').addEventListener('click', () => {
  const settings = {
    prompts: currentPrompts,
    showViewer: document.getElementById('showViewer').checked
  };
  
  chrome.storage.sync.set(settings, () => {
    setStatus('SETTINGS SAVED SUCCESSFULLY!', '#28a745');
  });
});
