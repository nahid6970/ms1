document.addEventListener('DOMContentLoaded', () => {
  const domainNoteInput = document.getElementById('domain-note-input');
  const pageNoteInput = document.getElementById('page-note-input');
  const saveAllNotesBtn = document.getElementById('save-all-notes-btn');

  let activeTabUrl = '';
  let activeTabHostname = '';

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0] && tabs[0].url) {
      const url = new URL(tabs[0].url);
      activeTabUrl = url.href;
      activeTabHostname = url.hostname;

      chrome.storage.local.get([activeTabUrl, activeTabHostname], (result) => {
        if (result[activeTabHostname]) {
          domainNoteInput.value = result[activeTabHostname];
        }
        if (result[activeTabUrl]) {
          pageNoteInput.value = result[activeTabUrl];
        }
      });
    }
  });

  saveAllNotesBtn.addEventListener('click', () => {
    const domainNoteText = domainNoteInput.value;
    const pageNoteText = pageNoteInput.value;

    const itemsToSet = {};
    if (activeTabHostname) {
      itemsToSet[activeTabHostname] = domainNoteText;
    }
    if (activeTabUrl) {
      itemsToSet[activeTabUrl] = pageNoteText;
    }

    if (Object.keys(itemsToSet).length > 0) {
      chrome.storage.local.set(itemsToSet, () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (activeTabHostname) {
            chrome.tabs.sendMessage(tabs[0].id, { action: 'updateDomainNote', note: domainNoteText });
          }
          if (activeTabUrl) {
            chrome.tabs.sendMessage(tabs[0].id, { action: 'updatePageNote', note: pageNoteText });
          }
        });
        window.close();
      });
    }
  });

  const importNotesBtn = document.getElementById('import-notes-btn');
  const exportNotesBtn = document.getElementById('export-notes-btn');
  const importNotesInput = document.getElementById('import-notes-input');

  exportNotesBtn.addEventListener('click', () => {
    chrome.storage.local.get(null, (items) => {
      const notes = {};
      for (const key in items) {
        // Include both URLs (page-specific) and hostnames (domain-specific)
        if (key.startsWith('http') || key.includes('.')) { // Simple check for hostname (contains a dot)
          notes[key] = items[key];
        }
      }
      const blob = new Blob([JSON.stringify(notes, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      chrome.downloads.download({
        url: url,
        filename: 'notes.json'
      });
    });
  });

  importNotesBtn.addEventListener('click', () => {
    importNotesInput.click();
  });

  importNotesInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const notes = JSON.parse(e.target.result);
        chrome.storage.local.set(notes, () => {
          alert('Notes imported successfully!');
          // Refresh the notes for the current page
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0] && tabs[0].url) {
              const url = new URL(tabs[0].url);
              activeTabUrl = url.href;
              activeTabHostname = url.hostname;
              chrome.storage.local.get([activeTabUrl, activeTabHostname], (result) => {
                if (result[activeTabHostname]) {
                  domainNoteInput.value = result[activeTabHostname];
                } else {
                  domainNoteInput.value = '';
                }
                if (result[activeTabUrl]) {
                  pageNoteInput.value = result[activeTabUrl];
                } else {
                  pageNoteInput.value = '';
                }
              });
            }
          });
        });
      };
      reader.readAsText(file);
    }
  });
});