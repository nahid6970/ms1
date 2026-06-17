chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'inspect-element',
    title: '🔍 Inspect Element',
    contexts: ['all'],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== 'inspect-element') return;
  await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ['content.js'] });
  await chrome.scripting.insertCSS({ target: { tabId: tab.id }, files: ['styles.css'] });
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => window.__inspectorActivate?.(),
  });
});
