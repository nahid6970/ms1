(function() {
  function normalizeFileUrl(input) {
    const raw = (input || '').trim();
    if (!raw) return '';

    if (raw.startsWith('file:///')) {
      return raw;
    }

    if (/^[a-zA-Z]:[\\/]/.test(raw)) {
      return `file:///${raw.replace(/\\/g, '/')}`;
    }

    return '';
  }

  function openLocalFile(url) {
    const normalized = normalizeFileUrl(url);
    if (!normalized) {
      return false;
    }

    chrome.runtime.sendMessage(
      {
        type: 'OPEN_LOCAL_FILE',
        url: normalized
      },
      (response) => {
        const lastError = chrome.runtime.lastError;
        if (lastError) {
          console.warn('Local file open failed:', lastError.message);
          return;
        }

        if (!response?.ok) {
          console.warn('Local file open rejected:', response?.error || 'Unknown error');
        }
      }
    );

    return true;
  }

  document.addEventListener('click', (event) => {
    if (event.button !== 0) return;
    if (event.ctrlKey || event.shiftKey || event.altKey || event.metaKey) return;

    const link = event.target.closest('a[href]');
    if (!link) return;

    const href = link.getAttribute('href') || '';
    if (!href.startsWith('file:') && !/^[a-zA-Z]:[\\/]/.test(href)) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    openLocalFile(href);
  }, true);

  console.log('Open Local Files In New Tab script enabled');
})();
