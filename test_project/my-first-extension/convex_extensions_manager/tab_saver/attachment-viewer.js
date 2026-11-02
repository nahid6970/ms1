const params = new URLSearchParams(location.search);
const tabId = Number(params.get('tabId'));
const attachmentIndex = Number(params.get('attachmentIndex'));
const filename = document.getElementById('fileName');
const frame = document.getElementById('fileFrame');
const message = document.getElementById('message');

function showError(text) {
  frame.hidden = true;
  message.hidden = false;
  message.textContent = text;
}

function previewLocalData(dataUrl) {
  if (!dataUrl) return showError('The attachment could not be found in local storage.');
  fetch(dataUrl)
    .then(response => response.blob())
    .then(blob => { frame.src = URL.createObjectURL(blob); })
    .catch(() => showError('The attachment could not be opened.'));
}

chrome.storage.local.get(['savedTabs'], ({ savedTabs = [] }) => {
  const tab = savedTabs.find(item => item.id === tabId);
  const file = tab?.attachments?.[attachmentIndex];
  if (!file) return showError('This attachment could not be found.');

  const name = file.displayName || file.name || 'Attachment';
  filename.textContent = name;
  if (file.storageId) {
    chrome.runtime.sendMessage({ action: 'getAttachmentUrl', storageId: file.storageId }, response => {
      if (chrome.runtime.lastError || !response?.success || !response.url) {
        if (file.dataUrl) return previewLocalData(file.dataUrl);
        return showError(chrome.runtime.lastError?.message || response?.error || 'The Convex attachment URL could not be loaded.');
      }
      location.replace(response.url);
    });
    return;
  }
  const source = typeof file === 'string' ? file : (file.url || file.href || file.dataUrl || file.content);
  if (typeof source !== 'string' || !source) return showError('This attachment has no readable file data.');

  if (/^https?:\/\//i.test(source)) {
    location.replace(source);
    return;
  }

  (async () => {
    try {
      const blob = await (await fetch(source)).blob();
      // Text attachments that contain a URL should behave like a web link.
      if (blob.type.startsWith('text/')) {
        const text = (await blob.text()).trim();
        const urlLine = text.split(/\r?\n/).find(line => /^https?:\/\//i.test(line.trim()));
        if (urlLine) {
          location.replace(urlLine.trim());
          return;
        }
      }
      frame.src = URL.createObjectURL(blob);
    } catch (error) {
      showError('The attachment could not be opened.');
      console.error('Attachment preview failed:', error);
    }
  })();
});
