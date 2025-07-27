// Create a div to hold the notes
const noteDiv = document.createElement('div');
noteDiv.id = 'note-taker-div';
document.body.appendChild(noteDiv);

// Function to display the note
const displayNote = (note) => {
  noteDiv.innerHTML = ''; // Clear previous note
  if (note) {
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
    noteDiv.style.display = 'none';
  }
};

// Load the note for the current page
const url = window.location.href;
chrome.storage.local.get([url], (result) => {
  displayNote(result[url]);
});

// Listen for messages from the popup to update the note
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'updateNote') {
    displayNote(request.note);
    sendResponse({ status: 'Note updated' });
  }
});
