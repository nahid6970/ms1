// Load settings and current URL
document.addEventListener('DOMContentLoaded', async () => {
  // Get current tab URL
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  document.getElementById('url').value = tab.url;
  
  // Extract timestamp from URL if present
  const timeMatch = tab.url.match(/[?&]t=(\d+)/);
  if (timeMatch) {
    document.getElementById('startTime').value = timeMatch[1];
    document.getElementById('useTimeline').checked = true;
    toggleTimelineInputs();
  }
  
  // Load saved settings
  chrome.storage.sync.get({
    language: 'en',
    format: 'srt',
    autoSub: false,
    useTimeline: false,
    startTime: '',
    endTime: '',
    saveDir: ''
  }, (settings) => {
    document.getElementById('language').value = settings.language;
    document.getElementById('format').value = settings.format;
    document.getElementById('autoSub').checked = settings.autoSub;
    
    // Only override timeline if no URL timestamp was found
    if (!timeMatch) {
      document.getElementById('useTimeline').checked = settings.useTimeline;
      document.getElementById('startTime').value = settings.startTime;
      document.getElementById('endTime').value = settings.endTime;
    }
    
    toggleTimelineInputs();
  });
});

// Toggle timeline inputs
document.getElementById('useTimeline').addEventListener('change', toggleTimelineInputs);

function toggleTimelineInputs() {
  const checked = document.getElementById('useTimeline').checked;
  document.getElementById('timelineInputs').style.display = checked ? 'block' : 'none';
}

// Extract button handler
document.getElementById('extract').addEventListener('click', async () => {
  const url = document.getElementById('url').value;
  const language = document.getElementById('language').value;
  const format = document.getElementById('format').value;
  const autoSub = document.getElementById('autoSub').checked;
  const useTimeline = document.getElementById('useTimeline').checked;
  const startTime = document.getElementById('startTime').value;
  const endTime = document.getElementById('endTime').value;
  
  // Save current settings
  chrome.storage.sync.set({
    language,
    format,
    autoSub,
    useTimeline,
    startTime,
    endTime
  });
  
  // Get save directory from settings
  const settings = await chrome.storage.sync.get({ saveDir: '' });
  
  if (!settings.saveDir) {
    setStatus('ERROR: Set save directory in settings first!');
    return;
  }
  
  // Disable button and show progress
  const extractBtn = document.getElementById('extract');
  extractBtn.disabled = true;
  setStatus('EXTRACTING...');
  
  // Send message to background script
  chrome.runtime.sendMessage({
    action: 'extractSubtitles',
    data: {
      url,
      language,
      format,
      autoSub,
      useTimeline,
      startTime,
      endTime,
      saveDir: settings.saveDir
    }
  }, (response) => {
    extractBtn.disabled = false;
    
    if (response.success) {
      setStatus('EXTRACTION COMPLETE!');
      setTimeout(() => setStatus('READY'), 3000);
    } else {
      setStatus(`ERROR: ${response.error}`);
    }
  });
});

// Settings link
document.getElementById('settingsLink').addEventListener('click', (e) => {
  e.preventDefault();
  chrome.runtime.openOptionsPage();
});

function setStatus(message) {
  document.getElementById('status').textContent = message;
}
