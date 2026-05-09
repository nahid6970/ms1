document.addEventListener('DOMContentLoaded', () => {
  const contentDiv = document.getElementById('content');
  const statusDiv = document.getElementById('status');
  const copyBtn = document.getElementById('copy');
  const sendBtn = document.getElementById('send');
  const promptSelect = document.getElementById('promptSelect');
  const settingsLink = document.getElementById('settingsLink');

  let currentPrompts = [];

  // Load prompts and settings
  chrome.storage.sync.get({
    prompts: [],
    lastSelectedPrompt: ''
  }, (settings) => {
    currentPrompts = settings.prompts || [];
    
    // Populate dropdown
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

  // Save selection change
  promptSelect.addEventListener('change', () => {
    chrome.storage.sync.set({ lastSelectedPrompt: promptSelect.value });
  });

  function update() {
    chrome.storage.local.get(['interceptedSubtitles', 'lastInterceptTime'], (data) => {
      if (data.interceptedSubtitles) {
        contentDiv.textContent = data.interceptedSubtitles;
        const time = new Date(data.lastInterceptTime).toLocaleTimeString();
        statusDiv.textContent = `Last intercepted at ${time}`;
        copyBtn.disabled = false;
        sendBtn.disabled = false;
      } else {
        copyBtn.disabled = true;
        sendBtn.disabled = true;
      }
    });
  }

  update();
  setInterval(update, 2000);

  copyBtn.addEventListener('click', () => {
    const text = contentDiv.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const originalText = copyBtn.textContent;
      copyBtn.textContent = 'Copied!';
      setTimeout(() => copyBtn.textContent = originalText, 2000);
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

  settingsLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
  });
});
