// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
    // Get enabled scripts from storage
    chrome.storage.local.get(['enabledScripts'], (result) => {
      const enabledScripts = result.enabledScripts || {};
      
      console.log('Tab updated:', tab.url);
      console.log('Enabled scripts:', enabledScripts);

      // Inject each enabled script
      for (const scriptPath in enabledScripts) {
        if (enabledScripts[scriptPath]) {
          console.log(`Injecting script: ${scriptPath}`);
          
          chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: [scriptPath]
          }).then(() => {
            console.log(`Successfully injected: ${scriptPath}`);
          }).catch(err => {
            console.error(`Failed to inject ${scriptPath}:`, err);
          });
        }
      }
    });
  }
});

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Script Manager Extension installed');
});

// Optional: Listen for storage changes to debug
chrome.storage.onChanged.addListener((changes, namespace) => {
  console.log('Storage changed:', changes);
});