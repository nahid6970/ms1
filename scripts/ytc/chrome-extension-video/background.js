let downloadPort = null;
let downloadCallback = null;

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
  downloadCallback = sendResponse;
  downloadPort = chrome.runtime.connectNative('com.ytc.video_downloader');
  
  downloadPort.onMessage.addListener((response) => {
    if (response.progress) {
      chrome.runtime.sendMessage({
        action: 'downloadProgress',
        percent: response.percent,
        status: response.status
      });
    } else {
      if (downloadCallback) {
        downloadCallback(response);
        downloadCallback = null;
      }
      if (downloadPort) {
        downloadPort.disconnect();
        downloadPort = null;
      }
    }
  });
  
  downloadPort.onDisconnect.addListener(() => {
    if (chrome.runtime.lastError && downloadCallback) {
      downloadCallback({ success: false, error: chrome.runtime.lastError.message });
      downloadCallback = null;
    }
  });
  
  downloadPort.postMessage({
    action: 'downloadVideo',
    url: data.url,
    videoFormat: data.videoFormat,
    audioFormat: data.audioFormat,
    downloadSubs: data.downloadSubs,
    subLang: data.subLang,
    saveDir: data.saveDir
  });
}
