(function() {
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    const url = args[0] instanceof Request ? args[0].url : args[0];

    if (typeof url === 'string' && url.includes('youtube.com/api/timedtext')) {
      // Clone response to read it without consuming the original stream
      const clone = response.clone();
      clone.text().then(content => {
        if (content && content.length > 0) {
          window.dispatchEvent(new CustomEvent('YTC_SUBTITLES_CAPTURED', {
            detail: { url, content }
          }));
        }
      });
    }
    return response;
  };

  // Also intercept XHR for older YouTube players or specific tracks
  const originalOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url) {
    if (typeof url === 'string' && url.includes('youtube.com/api/timedtext')) {
      this.addEventListener('load', function() {
        if (this.responseText && this.responseText.length > 0) {
          window.dispatchEvent(new CustomEvent('YTC_SUBTITLES_CAPTURED', {
            detail: { url, content: this.responseText }
          }));
        }
      });
    }
    return originalOpen.apply(this, arguments);
  };
})();
