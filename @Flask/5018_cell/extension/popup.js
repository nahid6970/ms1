document.getElementById('btn').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // Inject content script if not already there
  await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ['content.js'] });
  await chrome.scripting.insertCSS({ target: { tabId: tab.id }, files: ['styles.css'] });

  // Activate picker
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => window.__inspectorActivate?.(),
  });

  window.close();
});
