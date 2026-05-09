chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'injectToAIStudio') {
    injectToAIStudio(request.subtitles);
    sendResponse({ success: true });
  }
});

async function injectToAIStudio(subtitles) {
  const tab = await chrome.tabs.create({ url: 'https://aistudio.google.com/prompts/new_chat' });
  
  chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
    if (tabId === tab.id && info.status === 'complete') {
      chrome.tabs.onUpdated.removeListener(listener);
      
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        args: [subtitles],
        func: (subtitleText) => {
          const tryInject = () => {
            const editor = document.querySelector('div[contenteditable="true"]') || 
                           document.querySelector('textarea') ||
                           document.querySelector('.prompt-textarea');
            
            if (editor) {
              editor.focus();
              const blob = new Blob([subtitleText], { type: 'text/plain' });
              const file = new File([blob], 'subtitles.txt', { type: 'text/plain' });
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);
              
              const dropEvent = new DragEvent('drop', {
                bubbles: true,
                cancelable: true,
                dataTransfer: dataTransfer
              });
              
              editor.dispatchEvent(dropEvent);
              return true;
            }
            return false;
          };

          let attempts = 0;
          const interval = setInterval(() => {
            if (tryInject() || attempts > 20) clearInterval(interval);
            attempts++;
          }, 800);
        }
      });
    }
  });
}
