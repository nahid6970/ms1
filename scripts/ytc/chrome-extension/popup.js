document.addEventListener('DOMContentLoaded', () => {
  const contentDiv = document.getElementById('content');
  const statusDiv = document.getElementById('status');
  const copyBtn = document.getElementById('copy');
  const sendBtn = document.getElementById('send');

  function update() {
    chrome.storage.local.get(['interceptedSubtitles', 'lastInterceptTime'], (data) => {
      if (data.interceptedSubtitles) {
        contentDiv.textContent = data.interceptedSubtitles;
        const time = new Date(data.lastInterceptTime).toLocaleTimeString();
        statusDiv.textContent = `Last intercepted at ${time}`;
        copyBtn.disabled = false;
        sendBtn.disabled = false;
      } else {
        copyBtn.disabled = true;
        sendBtn.disabled = true;
      }
    });
  }

  update();
  setInterval(update, 1000);

  copyBtn.addEventListener('click', () => {
    const text = contentDiv.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const originalText = copyBtn.textContent;
      copyBtn.textContent = 'Copied!';
      setTimeout(() => copyBtn.textContent = originalText, 2000);
    });
  });

  sendBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({
      action: 'injectToAIStudio',
      subtitles: contentDiv.textContent
    });
  });
});
