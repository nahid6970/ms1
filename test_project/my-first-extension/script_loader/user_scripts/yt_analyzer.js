// YT Analyzer — configurable hotkey (default F9) on YouTube pages.
// Change the shortcut via the SET button in Script Manager popup.

(function () {
  if (window.__ytAnalyzerLoaded) return;
  window.__ytAnalyzerLoaded = true;

  document.addEventListener('keydown', (e) => {
    if (!location.hostname.includes('youtube.com')) return;

    chrome.storage.local.get(['ytAnalyzerHotkey'], (result) => {
      const hotkey = result.ytAnalyzerHotkey || 'F9';
      if (e.key !== hotkey) return;

      e.preventDefault();
      chrome.runtime.sendMessage(
        { type: 'LAUNCH_YT_ANALYZER', url: location.href },
        (res) => {
          if (chrome.runtime.lastError || (res && !res.ok)) {
            console.error('[YT Analyzer] Failed to launch:', chrome.runtime.lastError?.message || res?.error);
          }
        }
      );
    });
  });
})();
