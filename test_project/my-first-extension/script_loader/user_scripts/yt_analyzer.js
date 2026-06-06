// YT Analyzer — press F10 on any YouTube page to open the Like/Dislike GUI
// Enable/disable via the Script Manager popup like any other script.

(function () {
  if (window.__ytAnalyzerLoaded) return;
  window.__ytAnalyzerLoaded = true;

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'F9') return;
    if (!location.hostname.includes('youtube.com')) return;

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
})();
