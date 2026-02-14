let videoFormats = [];
let audioFormats = [];

document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const currentUrl = tab.url;
  document.getElementById('url').value = currentUrl;
  
  // Restore saved state
  chrome.storage.local.get(['videoFormats', 'audioFormats', 'selectedVideo', 'selectedAudio', 'lastUrl', 'isDownloading', 'downloadProgress'], (data) => {
    if (data.lastUrl === currentUrl && data.videoFormats && data.audioFormats) {
      videoFormats = data.videoFormats;
      audioFormats = data.audioFormats;
      
      const videoSelect = document.getElementById('videoFormat');
      const audioSelect = document.getElementById('audioFormat');
      
      videoSelect.innerHTML = '<option value="best">best</option>' + 
        videoFormats.map(f => `<option value="${f.id}">${f.id} | ${f.ext} | ${f.resolution} | ${f.size}</option>`).join('');
      
      audioSelect.innerHTML = '<option value="best">best</option>' + 
        audioFormats.map(f => `<option value="${f.id}">${f.id} | ${f.ext} | ${f.abr}k | ${f.size}</option>`).join('');
      
      videoSelect.disabled = false;
      audioSelect.disabled = false;
      document.getElementById('download').disabled = false;
      
      if (data.selectedVideo) videoSelect.value = data.selectedVideo;
      if (data.selectedAudio) audioSelect.value = data.selectedAudio;
      
      // Restore download state
      if (data.isDownloading) {
        document.getElementById('download').disabled = true;
        document.getElementById('progressContainer').style.display = 'block';
        setProgress(data.downloadProgress || 0, data.downloadProgress ? `${data.downloadProgress.toFixed(1)}%` : 'Downloading...');
        setStatus('DOWNLOADING...');
      } else {
        setStatus('READY');
      }
    }
  });
  
  chrome.storage.sync.get({
    downloadSubs: false,
    subLang: 'en'
  }, (settings) => {
    document.getElementById('downloadSubs').checked = settings.downloadSubs;
    document.getElementById('subLang').value = settings.subLang;
    toggleSubLangSection();
  });
});

document.getElementById('downloadSubs').addEventListener('change', toggleSubLangSection);

function toggleSubLangSection() {
  const checked = document.getElementById('downloadSubs').checked;
  document.getElementById('subLangSection').style.display = checked ? 'block' : 'none';
}

document.getElementById('fetchFormats').addEventListener('click', async () => {
  const url = document.getElementById('url').value;
  const settings = await chrome.storage.sync.get({ saveDir: '' });
  
  if (!settings.saveDir) {
    setStatus('ERROR: Set save directory in settings first!');
    return;
  }
  
  const fetchBtn = document.getElementById('fetchFormats');
  fetchBtn.disabled = true;
  setStatus('FETCHING FORMATS...');
  
  chrome.runtime.sendMessage({
    action: 'fetchFormats',
    data: { url, saveDir: settings.saveDir }
  }, (response) => {
    fetchBtn.disabled = false;
    
    if (response.success) {
      videoFormats = response.videoFormats;
      audioFormats = response.audioFormats;
      
      // Save state
      chrome.storage.local.set({
        videoFormats,
        audioFormats,
        lastUrl: url
      });
      
      const videoSelect = document.getElementById('videoFormat');
      const audioSelect = document.getElementById('audioFormat');
      
      videoSelect.innerHTML = '<option value="best">best</option>' + 
        videoFormats.map(f => `<option value="${f.id}">${f.id} | ${f.ext} | ${f.resolution} | ${f.size}</option>`).join('');
      
      audioSelect.innerHTML = '<option value="best">best</option>' + 
        audioFormats.map(f => `<option value="${f.id}">${f.id} | ${f.ext} | ${f.abr}k | ${f.size}</option>`).join('');
      
      videoSelect.disabled = false;
      audioSelect.disabled = false;
      document.getElementById('download').disabled = false;
      
      setStatus('FORMATS FETCHED SUCCESSFULLY');
    } else {
      setStatus(`ERROR: ${response.error}`);
    }
  });
});

document.getElementById('download').addEventListener('click', async () => {
  const url = document.getElementById('url').value;
  const videoFormat = document.getElementById('videoFormat').value;
  const audioFormat = document.getElementById('audioFormat').value;
  const downloadSubs = document.getElementById('downloadSubs').checked;
  const subLang = document.getElementById('subLang').value;
  
  chrome.storage.sync.set({ downloadSubs, subLang });
  
  const settings = await chrome.storage.sync.get({ saveDir: '' });
  
  if (!settings.saveDir) {
    setStatus('ERROR: Set save directory in settings first!');
    return;
  }
  
  const downloadBtn = document.getElementById('download');
  downloadBtn.disabled = true;
  document.getElementById('progressContainer').style.display = 'block';
  setProgress(0, 'Starting download...');
  setStatus('DOWNLOADING...');
  
  // Save download state
  chrome.storage.local.set({ isDownloading: true, downloadProgress: 0 });
  
  chrome.runtime.sendMessage({
    action: 'downloadVideo',
    data: {
      url,
      videoFormat,
      audioFormat,
      downloadSubs,
      subLang,
      saveDir: settings.saveDir
    }
  }, (response) => {
    downloadBtn.disabled = false;
    document.getElementById('progressContainer').style.display = 'none';
    
    // Clear download state
    chrome.storage.local.set({ isDownloading: false, downloadProgress: 0 });
    
    if (response.success) {
      setStatus('DOWNLOAD COMPLETE!');
      setTimeout(() => setStatus('READY'), 3000);
    } else {
      setStatus(`ERROR: ${response.error}`);
    }
  });
});

// Listen for progress updates
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'downloadProgress') {
    setProgress(message.percent, message.status);
    // Save progress
    chrome.storage.local.set({ downloadProgress: message.percent });
  }
});

function setProgress(percent, text) {
  document.getElementById('progressFill').style.width = percent + '%';
  document.getElementById('progressText').textContent = text;
}

document.getElementById('settingsLink').addEventListener('click', (e) => {
  e.preventDefault();
  chrome.runtime.openOptionsPage();
});

function setStatus(message) {
  document.getElementById('status').textContent = message;
}

// Save selection changes
document.getElementById('videoFormat')?.addEventListener('change', () => {
  chrome.storage.local.set({ selectedVideo: document.getElementById('videoFormat').value });
});

document.getElementById('audioFormat')?.addEventListener('change', () => {
  chrome.storage.local.set({ selectedAudio: document.getElementById('audioFormat').value });
});
