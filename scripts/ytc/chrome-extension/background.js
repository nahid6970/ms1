import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

const CONVEX_URL = "https://joyous-stingray-672.convex.cloud";
const EXTENSION_NAME = "ytc_subtitle_interceptor";
const client = new ConvexHttpClient(CONVEX_URL);

async function sendDataToConvex(data) {
  try {
    const result = await client.mutation("functions:save", {
      extensionName: EXTENSION_NAME,
      data
    });
    return { success: true, result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function loadDataFromConvex() {
  try {
    const data = await client.query("functions:get", {
      extensionName: EXTENSION_NAME
    });
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'saveToConvex') {
    sendDataToConvex(request.data)
      .then(sendResponse)
      .catch((error) => sendResponse({ success: false, error: error.message }));
    return true;
  }

  if (request.action === 'loadFromConvex') {
    loadDataFromConvex()
      .then(sendResponse)
      .catch((error) => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

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

(async () => {
  try {
    await client.query("functions:get", { extensionName: "health_check" });
    console.log('Convex connection healthy');
  } catch (e) {
    console.log('Convex not available or not initialized:', e.message);
  }
})();

async function fetchDirectAPI(url) {
  const match = url.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  if (!match) throw new Error('Not a valid YouTube URL');
  const videoId = match[1];

  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const tabId = (tabs[0] && tabs[0].url.includes(videoId)) ? tabs[0].id : null;
  if (!tabId) throw new Error('Keep the YouTube tab active.');

  // Check if we already have the subtitles for this video in storage
  const existing = await chrome.storage.local.get(['interceptedSubtitles', 'interceptedVideoId']);
  if (existing.interceptedVideoId === videoId && existing.interceptedSubtitles && existing.interceptedSubtitles.trim().length > 50) {
    return existing.interceptedSubtitles;
  }

  // Clear any previously intercepted subtitles so we can detect a fresh capture
  await chrome.storage.local.remove(['interceptedSubtitles', 'interceptedVideoId']);

  // Trigger CC reload by simulating 'c' keypress in the page's main world
  // (MAIN world required so YouTube's player event listeners actually receive it)
  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: () => {
      const fire = () => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'c', keyCode: 67, bubbles: true, cancelable: true }));
      fire();
      setTimeout(fire, 600);
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
