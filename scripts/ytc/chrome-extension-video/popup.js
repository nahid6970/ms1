let videoFormats = [];
let audioFormats = [];

document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  document.getElementById('url').value = tab.url;
  
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
