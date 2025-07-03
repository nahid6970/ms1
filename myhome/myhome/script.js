/* For Showing Markdown Table in HTML properly but lines also show */
 function parseMarkdownTable(markdown) {
  const rows = markdown.trim().split('\n');
  const headers = rows[1].split('|').map(header => header.trim()).filter(Boolean);
  const data = rows.slice(2, -1).map(row => row.split('|').map(cell => cell.trim()).filter(Boolean));

  return { headers, data };
}

function renderTable(headers, data) {
  const tableElement = document.createElement('table');
  const theadElement = document.createElement('thead');
  const tbodyElement = document.createElement('tbody');

  const headerRow = document.createElement('tr');
  headers.forEach(header => {
      const thElement = document.createElement('th');
      thElement.textContent = header;
      headerRow.appendChild(thElement);
  });

  theadElement.appendChild(headerRow);

  data.forEach(rowData => {
      const rowElement = document.createElement('tr');
      rowData.forEach(cellData => {
          const tdElement = document.createElement('td');
          tdElement.textContent = cellData;
          rowElement.appendChild(tdElement);
      });
      tbodyElement.appendChild(rowElement);
  });

  tableElement.appendChild(theadElement);
  tableElement.appendChild(tbodyElement);

  return tableElement;
}

function convertMarkdownTables() {
  const elements = document.querySelectorAll('[id^="markdown-table-"]');
  elements.forEach(element => {
      const markdownContent = element.innerHTML;
      const { headers, data } = parseMarkdownTable(markdownContent);
      const tableElement = renderTable(headers, data);
      element.innerHTML = ''; // Clear the original content
      element.appendChild(tableElement);
  });
}
// Call the function to convert Markdown tables on page load
window.addEventListener('load', convertMarkdownTables); 
 

/* // Get all the spans
const spans = document.querySelectorAll('span');

// Find the span with the maximum width
let maxWidth = 0;
spans.forEach(span => {
  const width = span.offsetWidth;
  if (width > maxWidth) {
    maxWidth = width;
  }
});

// Set the width of all spans to the maximum width
spans.forEach(span => {
  span.style.width = `${maxWidth}px`;
}); */


// Popup functionality
document.addEventListener('DOMContentLoaded', () => {
  const addLinkPopup = document.getElementById('add-link-popup');
  const editLinkPopup = document.getElementById('edit-link-popup');

  // Close buttons for addLinkPopup
  const addCloseButton = addLinkPopup ? addLinkPopup.querySelector('.close-button') : null;
  if (addCloseButton) {
    addCloseButton.addEventListener('click', () => {
      addLinkPopup.classList.add('hidden');
    });
  }

  // Close buttons for editLinkPopup
  const editCloseButton = editLinkPopup ? editLinkPopup.querySelector('.close-button') : null;
  if (editCloseButton) {
    editCloseButton.addEventListener('click', () => {
      editLinkPopup.classList.add('hidden');
    });
  }

  // Close popups when clicking outside
  window.addEventListener('click', (event) => {
    if (event.target === addLinkPopup) {
      addLinkPopup.classList.add('hidden');
    }
    if (event.target === editLinkPopup) {
      editLinkPopup.classList.add('hidden');
    }
  });
});