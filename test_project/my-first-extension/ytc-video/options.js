document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.sync.get({
    saveDir: '',
    authMethod: 'none',
    browser: 'chrome',
    cookieFile: ''
  }, (settings) => {
    document.getElementById('saveDir').value = settings.saveDir;
    document.querySelector(`input[name="authMethod"][value="${settings.authMethod}"]`).checked = true;
    document.getElementById('browser').value = settings.browser;
    document.getElementById('cookieFile').value = settings.cookieFile;
    toggleAuthSections();
  });
});

document.querySelectorAll('input[name="authMethod"]').forEach(radio => {
  radio.addEventListener('change', toggleAuthSections);
});

function toggleAuthSections() {
  const authMethod = document.querySelector('input[name="authMethod"]:checked').value;
  document.getElementById('browserSection').style.display = authMethod === 'browser' ? 'block' : 'none';
  document.getElementById('cookieFileSection').style.display = authMethod === 'file' ? 'block' : 'none';
}

document.getElementById('browseSaveDir').addEventListener('click', () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.webkitdirectory = true;
  input.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      const path = e.target.files[0].path;
      const dirPath = path.substring(0, path.lastIndexOf('\\'));
      document.getElementById('saveDir').value = dirPath;
    }
  });
  input.click();
});

document.getElementById('browseCookieFile').addEventListener('click', () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.txt';
  input.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      document.getElementById('cookieFile').value = e.target.files[0].path;
    }
  });
  input.click();
});

document.getElementById('save').addEventListener('click', () => {
  const saveDir = document.getElementById('saveDir').value;
  const authMethod = document.querySelector('input[name="authMethod"]:checked').value;
  const browser = document.getElementById('browser').value;
  const cookieFile = document.getElementById('cookieFile').value;
  
  if (!saveDir) {
    setStatus('ERROR: Save directory is required!');
    return;
  }
  
  chrome.storage.sync.set({
    saveDir,
    authMethod,
    browser,
    cookieFile
  }, () => {
    setStatus('SETTINGS SAVED SUCCESSFULLY!');
    setTimeout(() => setStatus('Configure settings above'), 3000);
  });
});

function setStatus(message) {
  document.getElementById('status').textContent = message;
}
