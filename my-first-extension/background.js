chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url.startsWith('http')) {
    chrome.storage.local.get(['enabledScripts'], (result) => {
      const enabledScripts = result.enabledScripts || {};

      // Iterate over the enabled scripts and inject them
      for (const scriptPath in enabledScripts) {
        if (enabledScripts[scriptPath]) {
          chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: [scriptPath] // scriptPath will be like 'user_scripts/sample_script_1/script.js'
          }).catch(err => console.error(`Failed to inject ${scriptPath}:`, err));
        }
      }
    });
  }
});