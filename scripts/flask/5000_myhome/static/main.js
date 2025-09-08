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


// Function to apply popup styling based on group settings
function applyPopupStyling(groupName) {
  // Fetch current links to get group styling
  fetch('/api/links')
    .then(response => response.json())
    .then(links => {
      const groupLinks = links.filter(link => (link.group || 'Ungrouped') === groupName);
      if (groupLinks.length > 0) {
        const groupSettings = groupLinks[0];
        const popupContents = document.querySelectorAll('.popup-content');
        
        popupContents.forEach(popup => {
          if (groupSettings.popup_bg_color) {
            popup.style.setProperty('--popup-bg-color', groupSettings.popup_bg_color);
          }
          if (groupSettings.popup_text_color) {
            popup.style.setProperty('--popup-text-color', groupSettings.popup_text_color);
          }
          if (groupSettings.popup_border_color) {
            popup.style.setProperty('--popup-border-color', groupSettings.popup_border_color);
          }
          if (groupSettings.popup_border_radius) {
            popup.style.setProperty('--popup-border-radius', groupSettings.popup_border_radius);
          }
        });
      }
    })
    .catch(error => {
      console.error('Error fetching group settings for popup styling:', error);
    });
}

// Function to reset popup styling to defaults
function resetPopupStyling() {
  const popupContents = document.querySelectorAll('.popup-content');
  popupContents.forEach(popup => {
    popup.style.removeProperty('--popup-bg-color');
    popup.style.removeProperty('--popup-text-color');
    popup.style.removeProperty('--popup-border-color');
    popup.style.removeProperty('--popup-border-radius');
  });
}

// Popup functionality
document.addEventListener('DOMContentLoaded', () => {
  const addLinkPopup = document.getElementById('add-link-popup');
  const editLinkPopup = document.getElementById('edit-link-popup');
  const editGroupPopup = document.getElementById('edit-group-popup');
  const horizontalStackPopup = document.getElementById('horizontal-stack-popup');

  // Close buttons for addLinkPopup
  const addCloseButton = addLinkPopup ? addLinkPopup.querySelector('.close-button') : null;
  if (addCloseButton) {
    addCloseButton.addEventListener('click', () => {
      addLinkPopup.classList.add('hidden');
      resetPopupStyling();
    });
  }

  // Close buttons for editLinkPopup
  const editCloseButton = editLinkPopup ? editLinkPopup.querySelector('.close-button') : null;
  if (editCloseButton) {
    editCloseButton.addEventListener('click', () => {
      editLinkPopup.classList.add('hidden');
      resetPopupStyling();
    });
  }

  // Close buttons for editGroupPopup
  const editGroupCloseButton = editGroupPopup ? editGroupPopup.querySelector('.close-button') : null;
  if (editGroupCloseButton) {
    editGroupCloseButton.addEventListener('click', () => {
      editGroupPopup.classList.add('hidden');
      resetPopupStyling();
    });
  }

  // Close buttons for horizontalStackPopup
  const horizontalStackCloseButton = horizontalStackPopup ? horizontalStackPopup.querySelector('.close-button') : null;
  if (horizontalStackCloseButton) {
    horizontalStackCloseButton.addEventListener('click', () => {
      horizontalStackPopup.classList.add('hidden');
      resetPopupStyling();
    });
  }

  // Close popups when clicking outside
  window.addEventListener('click', (event) => {
    if (event.target === addLinkPopup) {
      addLinkPopup.classList.add('hidden');
      resetPopupStyling();
    }
    if (event.target === editLinkPopup) {
      editLinkPopup.classList.add('hidden');
      resetPopupStyling();
    }
    if (event.target === editGroupPopup) {
      editGroupPopup.classList.add('hidden');
      resetPopupStyling();
    }
    if (event.target === horizontalStackPopup) {
      horizontalStackPopup.classList.add('hidden');
      resetPopupStyling();
    }
  });

  // F1 key listener
  document.addEventListener('keydown', (event) => {
    if (event.key === 'F1') {
      event.preventDefault();
      const toggle = document.getElementById('edit-mode-toggle');
      if (toggle) {
        toggle.checked = !toggle.checked;
        const changeEvent = new Event('change');
        toggle.dispatchEvent(changeEvent);
      }
    }
  });

  // Edit mode toggle listener
  const editModeToggle = document.getElementById('edit-mode-toggle');
  if (editModeToggle) {
    editModeToggle.addEventListener('change', function() {
      if (typeof toggleSidebarEditMode === 'function') {
        toggleSidebarEditMode(this.checked);
      }
    });
  }

  // Add title attribute to inputs with placeholders for tooltips
  const inputs = document.querySelectorAll('input[placeholder]');
  inputs.forEach(input => {
    if (input.placeholder) {
      input.title = input.placeholder;
    }
  });
});

// Trigger scans function - triggers actual TV show and movie scans
async function triggerScans() {
  const scanButton = document.getElementById('scan-button');
  const scanStatus = document.getElementById('scan-status');

  // Show scanning status
  scanButton.disabled = true;
  scanButton.style.opacity = '0.6';
  scanStatus.textContent = 'TV...';
  scanStatus.style.display = 'inline';
  scanStatus.style.color = '#ffffff';

  try {
    console.log('Starting external scans...');

    // Trigger both TV show scan (blue button) and movie sync (green button)
    const response = await fetch('/api/trigger-scan', {
      method: 'POST'
    });

    if (response.ok) {
      const results = await response.json();
      console.log('Scan results:', results);

      // Update status to show movie scanning
      scanStatus.textContent = 'Movie...';

      // Wait a bit then show results
      setTimeout(() => {
        // Show success/failure status
        const tvSuccess = results.tv_scan.success;
        const movieSuccess = results.movie_scan.success;

        if (tvSuccess && movieSuccess) {
          scanStatus.textContent = '✓✓';
          scanStatus.style.color = '#4CAF50';
        } else if (tvSuccess || movieSuccess) {
          scanStatus.textContent = '✓✗';
          scanStatus.style.color = '#FFA500';
        } else {
          scanStatus.textContent = '✗✗';
          scanStatus.style.color = '#f44336';
        }

        // Show detailed results in console
        console.log('TV Scan:', results.tv_scan.message);
        console.log('Movie Scan:', results.movie_scan.message);

        setTimeout(() => {
          scanStatus.style.display = 'none';
          scanButton.disabled = false;
          scanButton.style.opacity = '1';
        }, 3000);
      }, 2000);

    } else {
      throw new Error('Scan request failed');
    }

  } catch (error) {
    console.error('Scan trigger failed:', error);

    // Show error status briefly
    scanStatus.textContent = '✗';
    scanStatus.style.color = '#f44336';

    setTimeout(() => {
      scanStatus.style.display = 'none';
      scanButton.disabled = false;
      scanButton.style.opacity = '1';
    }, 2000);
  }
}