// Load settings on page load
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.sync.get({
    saveDir: '',
    authMethod: 'none',
    browser: 'chrome',
    cookieFile: '',
    defaultLanguage: 'en',
    defaultFormat: 'srt',
    defaultAutoSub: false
  }, (settings) => {
    document.getElementById('saveDir').value = settings.saveDir;
    document.getElementById('authMethod').value = settings.authMethod;
    document.getElementById('browser').value = settings.browser;
    document.getElementById('cookieFile').value = settings.cookieFile;
    document.getElementById('defaultLanguage').value = settings.defaultLanguage;
    document.getElementById('defaultFormat').value = settings.defaultFormat;
    document.getElementById('defaultAutoSub').checked = settings.defaultAutoSub;
    
    toggleAuthSections();
  });
});

// Auth method change handler
document.getElementById('authMethod').addEventListener('change', toggleAuthSections);

function toggleAuthSections() {
  const method = document.getElementById('authMethod').value;
  document.getElementById('browserSection').style.display = method === 'browser' ? 'block' : 'none';
  document.getElementById('cookieFileSection').style.display = method === 'file' ? 'block' : 'none';
}

// Browse buttons (Note: Chrome extensions can't directly browse filesystem)
// These would need to be handled by the native host
document.getElementById('browseSaveDir').addEventListener('click', () => {
  alert('Please manually enter the full path to your save directory.\n\nExample: C:\\Downloads\\Subtitles');
});

document.getElementById('browseCookieFile').addEventListener('click', () => {
  alert('Please manually enter the full path to your cookie file.\n\nExample: C:\\path\\to\\cookies.txt');
});

// Save settings
document.getElementById('save').addEventListener('click', () => {
  const settings = {
    saveDir: document.getElementById('saveDir').value,
    authMethod: document.getElementById('authMethod').value,
    browser: document.getElementById('browser').value,
    cookieFile: document.getElementById('cookieFile').value,
    defaultLanguage: document.getElementById('defaultLanguage').value,
    defaultFormat: document.getElementById('defaultFormat').value,
    defaultAutoSub: document.getElementById('defaultAutoSub').checked
  };
  
  chrome.storage.sync.set(settings, () => {
    const status = document.getElementById('status');
    status.textContent = 'SETTINGS SAVED!';
    status.style.color = '#00ff9f';
    
    setTimeout(() => {
      status.textContent = '';
    }, 3000);
  });
});
