// Create div for domain-specific notes
const domainNoteDiv = document.createElement('div');
domainNoteDiv.id = 'domain-note-taker-div';
domainNoteDiv.className = 'note-taker-box'; // Add a class for styling
document.body.appendChild(domainNoteDiv);
domainNoteDiv.style.display = 'none'; // Hidden by default

// Create div for page-specific notes
const pageNoteDiv = document.createElement('div');
pageNoteDiv.id = 'page-note-taker-div';
pageNoteDiv.className = 'note-taker-box'; // Add a class for styling
document.body.appendChild(pageNoteDiv);
pageNoteDiv.style.display = 'none'; // Hidden by default

// Function to display a note in a specific div
const displayNoteInBox = (note, noteBox, title) => {
  noteBox.innerHTML = ''; // Clear previous note
  if (note) {
    const noteTitle = document.createElement('h4');
    noteTitle.textContent = title;
    noteTitle.style.color = '#569cd6';
    noteTitle.style.marginBottom = '5px';

    const noteContent = document.createElement('pre');
    noteContent.textContent = note;
    noteContent.style.whiteSpace = 'pre-wrap'; // Ensure text wraps
    noteContent.style.wordBreak = 'break-word'; // Break long words

    const closeButton = document.createElement('button');
    closeButton.textContent = 'x';
    closeButton.className = 'note-close-button'; // Add a class for styling
    closeButton.onclick = () => {
      noteBox.style.display = 'none';
    };

    noteBox.appendChild(closeButton);
    noteBox.appendChild(noteTitle);
    noteBox.appendChild(noteContent);
    noteBox.style.display = 'block';
  } else {
    noteBox.style.display = 'none';
  }
};

// Load notes for the current page
const url = window.location.href;
const hostname = window.location.hostname;

chrome.storage.local.get([hostname, url], (result) => {
  // Display domain note if exists
  if (result[hostname]) {
    displayNoteInBox(result[hostname], domainNoteDiv, 'Domain Note');
  }

  // Display page note if exists
  if (result[url]) {
    displayNoteInBox(result[url], pageNoteDiv, 'Page Note');
  }
});

// Listen for messages from the popup to update notes
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'updateDomainNote') {
    displayNoteInBox(request.note, domainNoteDiv, 'Domain Note');
    sendResponse({ status: 'Domain note updated' });
  } else if (request.action === 'updatePageNote') {
    displayNoteInBox(request.note, pageNoteDiv, 'Page Note');
    sendResponse({ status: 'Page note updated' });
  }
});

// Add some basic styling for the note boxes and close button
const style = document.createElement('style');
style.textContent = `
  .note-taker-box {
    position: fixed;
    top: 10px;
    right: 10px;
    width: 250px;
    max-height: 300px;
    overflow-y: auto;
    background-color: #2d2d30;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    z-index: 10000;
    color: #d4d4d4;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
  }
  #page-note-taker-div {
    top: 320px; /* Position below domain note if both exist */
  }
  .note-taker-box pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    color: white;
  }
  .note-close-button {
    position: absolute;
    top: 5px;
    right: 5px;
    background: none;
    border: none;
    color: #d4d4d4;
    font-size: 16px;
    cursor: pointer;
  }
  .note-close-button:hover {
    color: #fff;
  }
`;
document.head.appendChild(style);