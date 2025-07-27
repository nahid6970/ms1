// Function to display the note
const displayNote = (note) => {
  let noteDiv = document.getElementById('note-taker-div');

  if (note) {
    if (!noteDiv) {
      noteDiv = document.createElement('div');
      noteDiv.id = 'note-taker-div';
      document.body.appendChild(noteDiv);
    }
    noteDiv.innerHTML = ''; // Clear previous note
    const noteContent = document.createElement('pre');
    noteContent.textContent = note;
    const closeButton = document.createElement('button');
    closeButton.textContent = 'x';
    closeButton.onclick = () => {
      noteDiv.style.display = 'none';
    };
    noteDiv.appendChild(closeButton);
    noteDiv.appendChild(noteContent);
    noteDiv.style.display = 'block';
  } else {
    if (noteDiv) {
      noteDiv.style.display = 'none';
    }
  }
};

// Load the note for the current page
const url = window.location.href;
const hostname = window.location.hostname;

// Check for domain-specific note first, then page-specific
chrome.storage.local.get([hostname, url], (result) => {
  if (result[hostname]) {
    displayNote(result[hostname]);
  } else if (result[url]) {
    displayNote(result[url]);
  }
});

// Listen for messages from the popup to update the note
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'updateNote') {
    displayNote(request.note);
    sendResponse({ status: 'Note updated' });
  }
});
