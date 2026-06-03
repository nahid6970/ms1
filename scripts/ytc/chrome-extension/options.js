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
const backupFileInput = document.getElementById('backupFileInput');

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

document.getElementById('exportBackup').addEventListener('click', async () => {
  try {
    const [syncData, localData] = await Promise.all([
      storageGet('sync'),
      storageGet('local')
    ]);

    const backup = {
      version: 1,
      exportedAt: new Date().toISOString(),
      sync: syncData,
      local: localData
    };

    const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ytc-backup-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    setStatus('BACKUP EXPORTED SUCCESSFULLY!', '#00ff9f');
  } catch (error) {
    console.error('Backup export failed:', error);
    setStatus('BACKUP EXPORT FAILED!', '#ff003c', 4000);
  }
});

document.getElementById('importBackup').addEventListener('click', () => {
  backupFileInput.value = '';
  backupFileInput.click();
});

backupFileInput.addEventListener('change', async () => {
  const file = backupFileInput.files && backupFileInput.files[0];
  if (!file) return;

  try {
    const text = await file.text();
    const parsed = JSON.parse(text);

    const syncData = parsed.sync && typeof parsed.sync === 'object' ? parsed.sync : null;
    const localData = parsed.local && typeof parsed.local === 'object' ? parsed.local : null;

    if (!syncData || !localData) {
      throw new Error('Invalid backup file format.');
    }

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

    setStatus('BACKUP RESTORED SUCCESSFULLY!', '#00ff9f');
  } catch (error) {
    console.error('Backup restore failed:', error);
    setStatus(`RESTORE FAILED: ${error.message}`, '#ff003c', 5000);
  } finally {
    backupFileInput.value = '';
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
