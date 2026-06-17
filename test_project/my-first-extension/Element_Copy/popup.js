document.getElementById('btn').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  await chrome.scripting.insertCSS({ target: { tabId: tab.id }, files: ['styles.css'] });
  await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ['content.js'] });
  window.close();
});
