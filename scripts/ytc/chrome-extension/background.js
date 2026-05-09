// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchSubtitles') {
    fetchDirectAPI(request.url)
      .then((content) => {
        chrome.storage.local.set({ 
          interceptedSubtitles: content,
          lastInterceptTime: Date.now()
        });
        sendResponse({ success: true, content });
      })
      .catch((error) => {
        console.error('DEBUG: fetchSubtitles error:', error);
        sendResponse({ success: false, error: error.message || 'Unknown error' });
      });
    return true;
  }
  
  if (request.action === 'injectToAIStudio') {
    injectToAIStudio(request.prompt, request.subtitles);
    sendResponse({ success: true });
  }
});

async function fetchDirectAPI(url) {
  const match = url.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  if (!match) throw new Error('Not a valid YouTube URL');
  const videoId = match[1];

  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const tabId = (tabs[0] && tabs[0].url.includes(videoId)) ? tabs[0].id : null;
  if (!tabId) throw new Error('Keep the YouTube tab active.');

  // Clear any previously intercepted subtitles so we can detect a fresh capture
  await chrome.storage.local.remove('interceptedSubtitles');

  // Trigger CC reload by simulating 'c' keypress (toggle off then on),
  // forcing the YouTube player to make a fresh timedtext network request
  // that inject.js will intercept automatically
  await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const fire = () => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'c', keyCode: 67, bubbles: true, cancelable: true }));
      fire(); // toggle off
      setTimeout(fire, 500); // toggle back on → triggers fresh timedtext fetch
    }
  });

  // Poll storage for up to 8 seconds waiting for inject.js to capture the subtitles
  for (let i = 0; i < 16; i++) {
    await new Promise(r => setTimeout(r, 500));
    const data = await chrome.storage.local.get('interceptedSubtitles');
    if (data.interceptedSubtitles && data.interceptedSubtitles.trim().length > 50) {
      return data.interceptedSubtitles;
    }
  }

  throw new Error('No subtitles captured. Make sure CC is ON for this video, then try again.');
}

async function injectToAIStudio(prompt, subtitles) {
  const tab = await chrome.tabs.create({ url: 'https://aistudio.google.com/prompts/new_chat' });
  chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
    if (tabId === tab.id && info.status === 'complete') {
      chrome.tabs.onUpdated.removeListener(listener);
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        args: [prompt, subtitles],
        func: (promptText, subtitleText) => {
          const tryInject = () => {
            const editor = document.querySelector('div[contenteditable="true"]') ||
                           document.querySelector('textarea') ||
                           document.querySelector('.prompt-textarea') ||
                           document.querySelector('ms-prompt-input');
            if (editor) {
              editor.focus();
              if (editor.getAttribute('contenteditable') === 'true') {
                document.execCommand('insertText', false, promptText || '');
              } else {
                editor.value = promptText || '';
                editor.dispatchEvent(new Event('input', { bubbles: true }));
              }
              const blob = new Blob([subtitleText], { type: 'text/plain' });
              const file = new File([blob], 'subtitles.txt', { type: 'text/plain' });
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);
              const dropEvent = new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer });
              editor.dispatchEvent(dropEvent);
              return true;
            }
            return false;
          };
          let attempts = 0;
          const interval = setInterval(() => {
            if (tryInject() || attempts > 30) clearInterval(interval);
            attempts++;
          }, 800);
        }
      });
    }
  });
}
