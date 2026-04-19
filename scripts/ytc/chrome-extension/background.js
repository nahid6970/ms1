// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractSubtitles') {
    extractSubtitles(request.data)
      .then((response) => sendResponse({ success: true, data: response }))
      .catch((error) => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'injectToAIStudio') {
    injectToAIStudio(request.text);
    sendResponse({ success: true });
  }
});

async function injectToAIStudio(text) {
  const tab = await chrome.tabs.create({ url: 'https://aistudio.google.com/prompts/new_chat' });
  
  // Wait for tab to load
  chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
    if (tabId === tab.id && info.status === 'complete') {
      chrome.tabs.onUpdated.removeListener(listener);
      
      // Inject script to find and fill the textarea
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        args: [text],
        func: (textToInject) => {
          // AI Studio uses a complex editor (ProseMirror/Lexical)
          // We'll try to find the contenteditable or textarea
          const tryInject = () => {
            const editor = document.querySelector('div[contenteditable="true"]') || 
                           document.querySelector('textarea') ||
                           document.querySelector('.prompt-textarea');
            
            if (editor) {
              editor.focus();
              
              // For contenteditable
              if (editor.getAttribute('contenteditable') === 'true') {
                document.execCommand('insertText', false, textToInject);
              } else {
                // For standard textarea
                editor.value = textToInject;
                editor.dispatchEvent(new Event('input', { bubbles: true }));
              }
              return true;
            }
            return false;
          };

          // Try several times as the UI loads dynamically
          let attempts = 0;
          const interval = setInterval(() => {
            if (tryInject() || attempts > 20) {
              clearInterval(interval);
            }
            attempts++;
          }, 500);
        }
      });
    }
  });
}

async function extractSubtitles(data) {
  const { url, language, format, autoSub, copyToClipboard, useTimeline, startTime, endTime, saveDir } = data;
  
  // Get authentication settings
  const settings = await chrome.storage.sync.get({
    authMethod: 'none',
    browser: 'chrome',
    cookieFile: ''
  });

  // Build yt-dlp command
  const cmd = ['yt-dlp', '--skip-download', '--write-subs', '--no-playlist'];
  
  // Add authentication
  if (settings.authMethod === 'browser') {
    cmd.push('--cookies-from-browser', settings.browser);
  } else if (settings.authMethod === 'file' && settings.cookieFile) {
    cmd.push('--cookies', settings.cookieFile);
  } else if (settings.authMethod === 'none') {
    // If none selected, we can try chrome but it might fail as user saw
    // Or we just don't add it. User explicitly said it wasn't showing before.
    // However, without it they get 429.
  }
  
  // Auto-generated subtitles
  if (autoSub) {
    cmd.push('--write-auto-subs');
  }
  
  // Format conversion
  if (format === 'txt') {
    cmd.push('--convert-subs', 'srt'); // Download as SRT first, convert later
  } else {
    cmd.push('--convert-subs', format);
  }
  
  // Language selection
  if (language === 'bn') {
    cmd.push('--sub-langs', 'bn');
  } else if (language === 'hi') {
    cmd.push('--sub-langs', 'hi');
  } else if (language === 'all') {
    cmd.push('--sub-langs', 'all');
  } else {
    cmd.push('--sub-langs', 'en.*');
  }
  
  // Output path
  cmd.push('-o', `${saveDir}/%(title)s.%(ext)s`);
  
  // Add URL
  cmd.push(url);
  
  // Send to native host
  const response = await chrome.runtime.sendNativeMessage(
    'com.ytc.subtitle_extractor',
    {
      command: cmd,
      format: format,
      copyToClipboard: copyToClipboard && format === 'txt',
      useTimeline: useTimeline,
      startTime: startTime,
      endTime: endTime,
      saveDir: saveDir
    }
  );
  
  if (!response.success) {
    throw new Error(response.error || 'Unknown error');
  }
  
  if (response.content) {
    chrome.storage.local.set({ subtitleContent: response.content }, () => {
      chrome.windows.create({
        url: 'viewer.html',
        type: 'popup',
        width: 800,
        height: 600
      });
    });
  }
  
  return response;
}
