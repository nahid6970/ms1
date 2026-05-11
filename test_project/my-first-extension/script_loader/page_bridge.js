window.addEventListener('message', (event) => {
  if (event.source !== window) {
    return;
  }

  const data = event.data;
  if (!data || data.source !== 'myhome-convex' || data.type !== 'OPEN_LOCAL_FILE') {
    return;
  }

  if (typeof data.url !== 'string' || !data.url.startsWith('file:///')) {
    window.postMessage({
      source: 'myhome-extension-bridge',
      type: 'OPEN_LOCAL_FILE_RESULT',
      requestId: data.requestId,
      ok: false,
      error: 'Invalid local file URL.'
    }, '*');
    return;
  }

  chrome.storage.local.get(['localFileBridgeEnabled'], (result) => {
    const bridgeEnabled = result.localFileBridgeEnabled !== false;
    if (!bridgeEnabled) {
      window.postMessage({
        source: 'myhome-extension-bridge',
        type: 'OPEN_LOCAL_FILE_RESULT',
        requestId: data.requestId,
        ok: false,
        error: 'Local file bridge is disabled in the extension popup.'
      }, '*');
      return;
    }

    chrome.runtime.sendMessage(
      {
        type: 'OPEN_LOCAL_FILE',
        url: data.url
      },
      (response) => {
        const lastError = chrome.runtime.lastError;
        window.postMessage({
          source: 'myhome-extension-bridge',
          type: 'OPEN_LOCAL_FILE_RESULT',
          requestId: data.requestId,
          ok: Boolean(response?.ok) && !lastError,
          error: lastError?.message || response?.error || null
        }, '*');
      }
    );
  });
});
