// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractSubtitles') {
    extractSubtitles(request.data)
      .then((response) => sendResponse({ success: true, data: response }))
      .catch((error) => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'injectToAIStudio') {
    injectToAIStudio(request.prompt, request.subtitles);
    sendResponse({ success: true });
  }
});

async function injectToAIStudio(prompt, subtitles) {
  const tab = await chrome.tabs.create({ url: 'https://aistudio.google.com/prompts/new_chat' });
  
  // Wait for tab to load
  chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
    if (tabId === tab.id && info.status === 'complete') {
      chrome.tabs.onUpdated.removeListener(listener);
      
      // Inject script to find and fill the textarea + simulate file drop
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
              // 1. Inject the prompt text
              editor.focus();
              if (editor.getAttribute('contenteditable') === 'true') {
                document.execCommand('insertText', false, promptText);
              } else {
                editor.value = promptText;
                editor.dispatchEvent(new Event('input', { bubbles: true }));
              }

              // 2. Simulate dropping the subtitles as a file
              const blob = new Blob([subtitleText], { type: 'text/plain' });
              const file = new File([blob], 'subtitles.txt', { type: 'text/plain' });
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);
              
              const dropEvent = new DragEvent('drop', {
                bubbles: true,
                cancelable: true,
                dataTransfer: dataTransfer
              });
              
              // Dispatch drop on the editor or the body
              editor.dispatchEvent(dropEvent);
              
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
          }, 800);
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
    const settings = await chrome.storage.sync.get({ showViewer: true });
    if (settings.showViewer) {
      chrome.storage.local.set({ subtitleContent: response.content }, () => {
        chrome.windows.create({
          url: 'viewer.html',
          type: 'popup',
          width: 800,
          height: 600
        });
      });
    }
  }
  
  return response;
}
