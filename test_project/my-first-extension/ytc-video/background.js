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

/**
 * Read auth settings from chrome.storage.sync and return them as a flat object.
 * These get merged into the native message so native_host.py can build auth args.
 */
function getAuthSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get({
      authMethod: 'none',
      browser: 'chrome',
      cookieFile: ''
    }, (settings) => {
      resolve({
        authMethod: settings.authMethod,
        browser: settings.browser,
        cookieFile: settings.cookieFile
      });
    });
  });
}

async function fetchFormats(data, sendResponse) {
  const auth = await getAuthSettings();

  chrome.runtime.sendNativeMessage(
    'com.ytc.video_downloader',
    {
      action: 'fetchFormats',
      url: data.url,
      saveDir: data.saveDir,
      // Auth settings passed so native_host.py can build --cookies-from-browser / --cookies args
      authMethod: auth.authMethod,
      browser: auth.browser,
      cookieFile: auth.cookieFile
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

async function downloadVideo(data, sendResponse) {
  const auth = await getAuthSettings();

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
      // Show notification on completion
      if (response.success) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon128.png',
          title: 'Download Complete',
          message: 'Video downloaded successfully!'
        });
      } else {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon128.png',
          title: 'Download Failed',
          message: response.error || 'Download failed'
        });
      }
      
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
    saveDir: data.saveDir,
    customTitle: data.customTitle || '',
    isPlaylist: data.isPlaylist || false,
    numberPlaylistItems: data.numberPlaylistItems || false,
    playlistQuality: data.playlistQuality || 'best',
    // Auth settings passed so native_host.py can build --cookies-from-browser / --cookies args
    authMethod: auth.authMethod,
    browser: auth.browser,
    cookieFile: auth.cookieFile
  });
}
