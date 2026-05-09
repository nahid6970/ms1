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
        <button class="delete-prompt" data-index="${index}">×</button>
      </div>
      <div class="prompt-text-preview">${p.text}</div>
    `;
    list.appendChild(item);
  });
  
  // Add delete listeners
  document.querySelectorAll('.delete-prompt').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = parseInt(e.currentTarget.dataset.index);
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
    alert('Please enter both a name and the prompt text.');
  }
});

// Save settings
document.getElementById('save').addEventListener('click', () => {
  const settings = {
    prompts: currentPrompts,
    showViewer: document.getElementById('showViewer').checked
  };
  
  chrome.storage.sync.set(settings, () => {
    const status = document.getElementById('status');
    status.textContent = 'SETTINGS SAVED SUCCESSFULLY!';
    status.style.color = '#28a745';
    
    setTimeout(() => {
      status.textContent = '';
    }, 3000);
  });
});
