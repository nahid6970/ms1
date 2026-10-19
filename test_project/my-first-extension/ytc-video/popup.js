let videoFormats = [];
let audioFormats = [];
let combinedFormats = [];

function isFacebookUrl(url) {
  return /^(https?:\/\/)?(www\.|m\.|web\.)?facebook\.com\/|^(https?:\/\/)?fb\.(watch|com)\//i.test(url);
}

function isFacebookGroupUrl(url) {
  return /facebook\.com\/groups\/|facebook\.com\/.*\/(permalink|posts)\//i.test(url);
}

function isYouTubeUrl(url) {
  return /^(https?:\/\/)?(www\.)?youtube\.com\/|^(https?:\/\/)?youtu\.be\//i.test(url);
}

document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const currentUrl = tab.url;
  document.getElementById('url').value = currentUrl;

  // Site-specific status hints
  if (isFacebookGroupUrl(currentUrl)) {
    setStatus('PRIVATE GROUP VIDEO? ENABLE AUTH IN SETTINGS (Firefox or Cookie File recommended)');
    document.getElementById('fbAuthHint').style.display = 'block';
    const hint = document.getElementById('fbAuthHint');
    if (hint) {
      hint.innerHTML =
        '⚠️ Private Facebook <strong>group</strong> videos require authentication.<br>' +
        'Use <strong>Firefox cookies</strong> or a <strong>Cookie File</strong> (Chrome cookies often fail).<br>' +
        '<a href="#" id="settingsLinkHint">Open Settings →</a>';
      document.getElementById('settingsLinkHint')?.addEventListener('click', (e) => {
        e.preventDefault();
        chrome.runtime.openOptionsPage();
      });
    }
  } else if (isFacebookUrl(currentUrl)) {
    setStatus('FACEBOOK VIDEO DETECTED — AUTH RECOMMENDED IN SETTINGS');
    document.getElementById('fbAuthHint').style.display = 'block';
  } else if (isYouTubeUrl(currentUrl)) {
    // Check if it's a playlist URL
    if (currentUrl.includes('list=')) {
      if (!currentUrl.includes('v=')) {
        setStatus('PLAYLISTS ARE IGNORED. Only individual videos are supported.');
        document.getElementById('fetchFormats').disabled = true;
      } else {
        setStatus('READY (Playlist detected - only this video will be downloaded)');
      }
    }
  }
  
  // Restore saved state for this URL
  chrome.storage.local.get(['videoFormats', 'audioFormats', 'combinedFormats', 'selectedVideo', 'selectedAudio', 'lastUrl'], (data) => {
    if (data.lastUrl === currentUrl && data.videoFormats && data.audioFormats) {
      videoFormats = data.videoFormats;
      audioFormats = data.audioFormats;
      combinedFormats = data.combinedFormats || [];
      
      populateFormatSelects();
      
      document.getElementById('videoFormat').disabled = false;
      document.getElementById('audioFormat').disabled = false;
      document.getElementById('download').disabled = false;
      
      if (data.selectedVideo) document.getElementById('videoFormat').value = data.selectedVideo;
      if (data.selectedAudio) document.getElementById('audioFormat').value = data.selectedAudio;
      
      setStatus('READY');
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

/**
 * Populate video and audio format dropdowns.
 * Combined (A+V) formats are shown at the top of the video list labeled [A+V].
 * When a combined format is selected as the video, the audio select is hidden
 * since the combined format already contains audio.
 */
function populateFormatSelects() {
  const videoSelect = document.getElementById('videoFormat');
  const audioSelect = document.getElementById('audioFormat');

  // Video dropdown: combined formats first (labeled [A+V]), then video-only
  const combinedOptions = combinedFormats.map(f =>
    `<option value="${f.id}" data-combined="true">[A+V] ${f.id} | ${f.ext} | ${f.resolution} | ${f.size}</option>`
  ).join('');

  const videoOnlyOptions = videoFormats.map(f =>
    `<option value="${f.id}">${f.id} | ${f.ext} | ${f.resolution} | ${f.size}</option>`
  ).join('');

  videoSelect.innerHTML =
    '<option value="best">best</option>' +
    combinedOptions +
    videoOnlyOptions;

  // Audio dropdown
  audioSelect.innerHTML =
    '<option value="best">best</option>' +
    audioFormats.map(f =>
      `<option value="${f.id}">${f.id} | ${f.ext} | ${f.abr}k | ${f.size}</option>`
    ).join('');

  updateAudioSelectVisibility();
}

/**
 * Hide the audio format section when a combined [A+V] format is selected
 * as the video, since it already has audio.
 */
function updateAudioSelectVisibility() {
  const videoSelect = document.getElementById('videoFormat');
  const selectedOption = videoSelect.options[videoSelect.selectedIndex];
  const isCombined = selectedOption && selectedOption.dataset.combined === 'true';

  document.getElementById('audioSection').style.display = isCombined ? 'none' : 'block';

  if (isCombined) {
    // Set audio to "best" internally so the format string works cleanly
    document.getElementById('audioFormat').value = 'best';
  }
}

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
      combinedFormats = response.combinedFormats || [];
      
      // Save state
      chrome.storage.local.set({
        videoFormats,
        audioFormats,
        combinedFormats,
        lastUrl: url
      });
      
      populateFormatSelects();
      
      document.getElementById('videoFormat').disabled = false;
      document.getElementById('audioFormat').disabled = false;
      document.getElementById('download').disabled = false;
      
      const totalFormats = videoFormats.length + audioFormats.length + combinedFormats.length;
      const hint = combinedFormats.length > 0
        ? ` (${combinedFormats.length} combined [A+V] format${combinedFormats.length > 1 ? 's' : ''} available)`
        : '';
      setStatus(`FORMATS FETCHED SUCCESSFULLY${hint}`);
    } else {
      setStatus(`ERROR: ${response.error}`);
    }
  });
});

document.getElementById('videoFormat').addEventListener('change', () => {
  updateAudioSelectVisibility();
  chrome.storage.local.set({ selectedVideo: document.getElementById('videoFormat').value });
});

document.getElementById('download').addEventListener('click', async () => {
  const url = document.getElementById('url').value;
  const videoSelect = document.getElementById('videoFormat');
  const selectedOption = videoSelect.options[videoSelect.selectedIndex];
  const isCombined = selectedOption && selectedOption.dataset.combined === 'true';

  const videoFormat = videoSelect.value;
  // If combined format selected, pass it as both video and audio so format string = "id+best/best"
  // native_host.py will handle it with the /best fallback
  const audioFormat = isCombined ? 'best' : document.getElementById('audioFormat').value;
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
  document.getElementById('downloadText').textContent = '[ DOWNLOADING 0% ]';
  document.getElementById('downloadProgress').style.width = '0%';
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
    
    if (response.success) {
      document.getElementById('downloadText').textContent = '[ ✓ COMPLETE ]';
      document.getElementById('downloadProgress').style.width = '100%';
      setStatus('DOWNLOAD COMPLETE!');
      setTimeout(() => {
        document.getElementById('downloadText').textContent = '[ DOWNLOAD VIDEO ]';
        document.getElementById('downloadProgress').style.width = '0%';
        setStatus('READY');
      }, 3000);
    } else {
      document.getElementById('downloadText').textContent = '[ DOWNLOAD VIDEO ]';
      document.getElementById('downloadProgress').style.width = '0%';
      setStatus(`ERROR: ${response.error}`);
    }
  });
});

// Listen for progress updates
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'downloadProgress') {
    document.getElementById('downloadText').textContent = `[ DOWNLOADING ${message.percent.toFixed(0)}% ]`;
    document.getElementById('downloadProgress').style.width = message.percent + '%';
  }
});

document.getElementById('settingsLink').addEventListener('click', (e) => {
  e.preventDefault();
  chrome.runtime.openOptionsPage();
});

document.getElementById('settingsLinkHint')?.addEventListener('click', (e) => {
  e.preventDefault();
  chrome.runtime.openOptionsPage();
});

function setStatus(message) {
  document.getElementById('status').textContent = message;
}

// Save audio selection changes
document.getElementById('audioFormat')?.addEventListener('change', () => {
  chrome.storage.local.set({ selectedAudio: document.getElementById('audioFormat').value });
});
