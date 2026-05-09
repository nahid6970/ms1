document.addEventListener('DOMContentLoaded', async () => {
  const contentDiv = document.getElementById('content');
  const fetchBtn = document.getElementById('fetchBtn');
  const copyBtn = document.getElementById('copyBtn');
  const sendBtn = document.getElementById('sendBtn');
  const promptSelect = document.getElementById('promptSelect');

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

  // Mode 1: Proactive Fetch
  fetchBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url.includes('youtube.com/watch')) {
      alert('PLEASE OPEN A YOUTUBE VIDEO TAB.');
      return;
    }

    fetchBtn.disabled = true;
    fetchBtn.textContent = '[ FETCHING SIGNAL... ]';
    contentDiv.textContent = 'CONNECTING TO DATA STREAM...';

    chrome.runtime.sendMessage({
      action: 'fetchSubtitles',
      url: tab.url
    }, (response) => {
      fetchBtn.disabled = false;
      fetchBtn.textContent = '[ FETCH CURRENT VIDEO SIGNAL ]';
      
      if (response && response.success) {
        contentDiv.textContent = response.content;
        copyBtn.disabled = false;
        sendBtn.disabled = false;
      } else {
        contentDiv.textContent = 'FETCH FAILED: ' + (response?.error || 'UNKNOWN ERROR');
        alert('SIGNAL LOST: ' + (response?.error || 'UNKNOWN ERROR'));
      }
    });
  });

  // Mode 2: Live Interceptor — only show subtitles captured AFTER popup opened
  const popupOpenTime = Date.now();
  function updateFromStorage() {
    chrome.storage.local.get(['interceptedSubtitles', 'lastInterceptTime'], (data) => {
      if (data.interceptedSubtitles && data.lastInterceptTime > popupOpenTime && !fetchBtn.disabled) {
        contentDiv.textContent = data.interceptedSubtitles;
        copyBtn.disabled = false;
        sendBtn.disabled = false;
      }
    });
  }

  setInterval(updateFromStorage, 2000);

  // Buttons
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(contentDiv.textContent).then(() => {
      const oldText = copyBtn.textContent;
      copyBtn.textContent = '[ COPIED! ]';
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
});
