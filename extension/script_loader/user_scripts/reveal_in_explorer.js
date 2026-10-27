// Reveal In Explorer — Ctrl+Shift+F hotkey on file:// pages.
// Primary handler is chrome.commands.onCommand in background.js (intercepts
// at browser level). This content script is a fallback for when the commands
// API isn't available or the script is injected dynamically.

(function () {
  if (window.__revealInExplorerLoaded) return;
  window.__revealInExplorerLoaded = true;

  document.addEventListener('keydown', (e) => {
    if (!e.ctrlKey || !e.shiftKey || e.key.toLowerCase() !== 'f') return;
    if (location.protocol !== 'file:') return;

    const tag = (e.target && e.target.tagName) || '';
    if (/^(INPUT|TEXTAREA|SELECT)$/i.test(tag) || e.target?.isContentEditable) return;

    e.preventDefault();
    e.stopPropagation();

    chrome.runtime.sendMessage(
      { type: 'REVEAL_IN_EXPLORER', url: location.href },
      (res) => {
        const err = chrome.runtime.lastError;
        if (err || (res && !res.ok)) {
          console.error('[Reveal In Explorer] Failed:', err?.message || res?.error);
        }
      }
    );
  }, true);
})();
