document.addEventListener('DOMContentLoaded', () => {
  const contentDiv = document.getElementById('content');
  const statusDiv = document.getElementById('status');
  const copyBtn = document.getElementById('copyBtn');
  const sendBtn = document.getElementById('sendBtn');
  const promptSelect = document.getElementById('promptSelect');
  const settingsLink = document.getElementById('settingsLink');

  let currentPrompts = [];

  // Load prompts and settings
  chrome.storage.sync.get({
    prompts: [],
    lastSelectedPrompt: ''
  }, (settings) => {
    currentPrompts = settings.prompts || [];
    
    currentPrompts.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = p.name;
      promptSelect.appendChild(opt);
    });
    
    if (settings.lastSelectedPrompt) {
      promptSelect.value = settings.lastSelectedPrompt;
    }
  });

  function update() {
    chrome.storage.local.get(['interceptedSubtitles', 'lastInterceptTime'], (data) => {
      if (data.interceptedSubtitles) {
        contentDiv.textContent = data.interceptedSubtitles;
        const time = new Date(data.lastInterceptTime).toLocaleTimeString();
        statusDiv.textContent = `Captured at ${time}`;
        statusDiv.style.color = '#28a745';
        copyBtn.disabled = false;
        sendBtn.disabled = false;
      } else {
        copyBtn.disabled = true;
        sendBtn.disabled = true;
      }
    });
  }

  update();
  setInterval(update, 1000);

  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(contentDiv.textContent).then(() => {
      const oldText = copyBtn.textContent;
      copyBtn.textContent = 'Copied!';
      setTimeout(() => copyBtn.textContent = oldText, 2000);
    });
  });

  sendBtn.addEventListener('click', () => {
    const selectedPromptName = promptSelect.value;
    const promptObj = currentPrompts.find(p => p.name === selectedPromptName);
    const promptText = promptObj ? promptObj.text : '';

    chrome.runtime.sendMessage({
      action: 'injectToAIStudio',
      prompt: promptText,
      subtitles: contentDiv.textContent
    });
  });

  promptSelect.addEventListener('change', () => {
    chrome.storage.sync.set({ lastSelectedPrompt: promptSelect.value });
  });

  settingsLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
  });
});
