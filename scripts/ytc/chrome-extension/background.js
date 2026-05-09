chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'injectToAIStudio') {
    injectToAIStudio(request.prompt, request.subtitles);
    sendResponse({ success: true });
  }
});

async function injectToAIStudio(prompt, subtitles) {
  console.log('DEBUG: Opening AI Studio...');
  const tab = await chrome.tabs.create({ url: 'https://aistudio.google.com/prompts/new_chat' });
  
  chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
    if (tabId === tab.id && info.status === 'complete') {
      chrome.tabs.onUpdated.removeListener(listener);
      
      console.log('DEBUG: Tab loaded, injecting script...');
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        args: [prompt, subtitles],
        func: (promptText, subtitleText) => {
          const tryInject = () => {
            console.log('DEBUG [Tab]: Attempting injection...');
            
            // Find prompt input
            const editor = document.querySelector('div[contenteditable="true"]') || 
                           document.querySelector('textarea') ||
                           document.querySelector('.prompt-textarea') ||
                           document.querySelector('ms-prompt-input');
            
            if (editor) {
              console.log('DEBUG [Tab]: Found editor, inserting prompt...');
              // 1. Inject the prompt text
              editor.focus();
              if (editor.getAttribute('contenteditable') === 'true') {
                document.execCommand('insertText', false, promptText || '');
              } else {
                editor.value = promptText || '';
                editor.dispatchEvent(new Event('input', { bubbles: true }));
              }

              // 2. Simulate dropping the subtitles as a file
              console.log('DEBUG [Tab]: Simulating file drop...');
              const blob = new Blob([subtitleText], { type: 'text/plain' });
              const file = new File([blob], 'subtitles.txt', { type: 'text/plain' });
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);
              
              const dropEvent = new DragEvent('drop', {
                bubbles: true,
                cancelable: true,
                dataTransfer: dataTransfer
              });
              
              // Dispatch drop on both the editor and the document to be sure
              editor.dispatchEvent(dropEvent);
              document.dispatchEvent(dropEvent);
              
              console.log('DEBUG [Tab]: Injection complete.');
              return true;
            }
            return false;
          };

          let attempts = 0;
          const interval = setInterval(() => {
            if (tryInject() || attempts > 30) {
              clearInterval(interval);
              console.log('DEBUG [Tab]: Stopped attempts after', attempts, 'tries');
            }
            attempts++;
          }, 1000);
        }
      }).catch(err => console.error('DEBUG: executeScript error:', err));
    }
  });
}
