chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchFormats') {
    fetchFormats(request.data, sendResponse);
    return true;
  } else if (request.action === 'downloadVideo') {
    downloadVideo(request.data, sendResponse);
    return true;
  }
});

function fetchFormats(data, sendResponse) {
  chrome.runtime.sendNativeMessage(
    'com.ytc.video_downloader',
    {
      action: 'fetchFormats',
      url: data.url,
      saveDir: data.saveDir
    },
    (response) => {
      if (chrome.runtime.lastError) {
        sendResponse({ success: false, error: chrome.runtime.lastError.message });
      } else {
        sendResponse(response);
      }
    }
  );
}

function downloadVideo(data, sendResponse) {
  chrome.runtime.sendNativeMessage(
    'com.ytc.video_downloader',
    {
      action: 'downloadVideo',
      url: data.url,
      videoFormat: data.videoFormat,
      audioFormat: data.audioFormat,
      downloadSubs: data.downloadSubs,
      subLang: data.subLang,
      saveDir: data.saveDir
    },
    (response) => {
      if (chrome.runtime.lastError) {
        sendResponse({ success: false, error: chrome.runtime.lastError.message });
      } else {
        sendResponse(response);
      }
    }
  );
}
