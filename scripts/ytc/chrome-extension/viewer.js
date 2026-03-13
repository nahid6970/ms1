chrome.storage.local.get(['subtitleContent'], (result) => {
  document.getElementById('content').textContent = result.subtitleContent || 'No content available';
});
