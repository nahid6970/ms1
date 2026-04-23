// Load settings on page load
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.sync.get({
    saveDir: '',
    authMethod: 'none',
    browser: 'chrome',
    cookieFile: '',
    prompts: []
  }, (settings) => {
    document.getElementById('saveDir').value = settings.saveDir;
    document.getElementById('authMethod').value = settings.authMethod;
    document.getElementById('browser').value = settings.browser;
    document.getElementById('cookieFile').value = settings.cookieFile;
    
    renderPrompts(settings.prompts);
    toggleAuthSections();
  });
});

let currentPrompts = [];

function renderPrompts(prompts) {
  currentPrompts = prompts || [];
  const list = document.getElementById('promptsList');
  list.innerHTML = '';
  
  currentPrompts.forEach((p, index) => {
    const item = document.createElement('div');
    item.className = 'prompt-item';
    item.innerHTML = `
      <div class="prompt-header">
        <span class="prompt-name">${p.name}</span>
        <button class="delete-prompt" data-index="${index}">×</button>
      </div>
      <div class="prompt-text-preview">${p.text}</div>
    `;
    list.appendChild(item);
  });
  
  // Add delete listeners
  document.querySelectorAll('.delete-prompt').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = parseInt(e.target.dataset.index);
      currentPrompts.splice(index, 1);
      renderPrompts(currentPrompts);
    });
  });
}

document.getElementById('addPrompt').addEventListener('click', () => {
  const nameInput = document.getElementById('newPromptName');
  const textInput = document.getElementById('newPromptText');
  const name = nameInput.value.trim();
  const text = textInput.value.trim();
  
  if (name && text) {
    currentPrompts.push({ name, text });
    renderPrompts(currentPrompts);
    nameInput.value = '';
    textInput.value = '';
  } else {
    alert('Please enter both name and prompt text.');
  }
});

// Auth method change handler
document.getElementById('authMethod').addEventListener('change', toggleAuthSections);

function toggleAuthSections() {
  const method = document.getElementById('authMethod').value;
  document.getElementById('browserSection').style.display = method === 'browser' ? 'block' : 'none';
  document.getElementById('cookieFileSection').style.display = method === 'file' ? 'block' : 'none';
}

// Browse buttons (Note: Chrome extensions can't directly browse filesystem)
// These would need to be handled by the native host
document.getElementById('browseSaveDir').addEventListener('click', () => {
  alert('Please manually enter the full path to your save directory.\n\nExample: C:\\Downloads\\Subtitles');
});

document.getElementById('browseCookieFile').addEventListener('click', () => {
  alert('Please manually enter the full path to your cookie file.\n\nExample: C:\\path\\to\\cookies.txt');
});

// Save settings
document.getElementById('save').addEventListener('click', () => {
  const settings = {
    saveDir: document.getElementById('saveDir').value,
    authMethod: document.getElementById('authMethod').value,
    browser: document.getElementById('browser').value,
    cookieFile: document.getElementById('cookieFile').value,
    prompts: currentPrompts
  };
  
  chrome.storage.sync.set(settings, () => {
    const status = document.getElementById('status');
    status.textContent = 'SETTINGS SAVED!';
    status.style.color = '#00ff9f';
    
    setTimeout(() => {
      status.textContent = '';
    }, 3000);
  });
});
