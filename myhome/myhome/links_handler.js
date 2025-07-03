document.addEventListener('DOMContentLoaded', function() {
  const linksContainer = document.getElementById('links-container');
  const addLinkForm = document.getElementById('add-link-form');

  // Function to fetch and display links
  async function fetchAndDisplayLinks() {
    try {
      const response = await fetch('/api/links');
      const links = await response.json();
      linksContainer.innerHTML = ''; // Clear existing links

      const groupedLinks = {};
      links.forEach(link => {
        const groupName = link.group || 'Ungrouped';
        if (!groupedLinks[groupName]) {
          groupedLinks[groupName] = [];
        }
        groupedLinks[groupName].push(link);
      });

      for (const groupName in groupedLinks) {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'link-group';

        const groupTitle = document.createElement('h3');
        groupTitle.textContent = groupName;
        groupDiv.appendChild(groupTitle);

        const groupContentDiv = document.createElement('div');
        groupContentDiv.className = 'link-group-content';
        groupContentDiv.style.display = 'flex';
        groupContentDiv.style.flexWrap = 'wrap';
        groupContentDiv.style.justifyContent = 'left';

        groupedLinks[groupName].forEach(link => {
          const span = document.createElement('span');
          let linkContent;

          if (link.icon_class) {
            linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''}" ${link.title ? `title="${link.title}"` : ''}><i class="${link.icon_class}"></i>${link.text ? link.text : ''}</a>`;
          } else if (link.img_src) {
            linkContent = `<a href="${link.url}"><img src="${link.img_src}" width="50" height="50"></a>`;
          } else {
            linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''}" ${link.title ? `title="${link.title}"` : ''}>${link.name}</a>`;
          }

          span.innerHTML = linkContent;
          const editButton = document.createElement('button');
          editButton.textContent = 'Edit';
          editButton.className = 'edit-button';
          editButton.onclick = () => openEditLinkPopup(link, index);
          span.appendChild(editButton);

          const deleteButton = document.createElement('button');
          deleteButton.textContent = 'Delete';
          deleteButton.className = 'delete-button';
          deleteButton.onclick = () => deleteLink(index);
          span.appendChild(deleteButton);

          // Apply font-size for text-based links if not image/icon
          if (!link.icon_class && !link.img_src) {
            span.style.fontSize = '40px';
          }
          groupContentDiv.appendChild(span);
        });
        groupDiv.appendChild(groupContentDiv);
        linksContainer.appendChild(groupDiv);
      }
    } catch (error) {
      console.error('Error fetching links:', error);
    }
  }

  // Handle form submission for adding new links
  if (addLinkForm) {
    addLinkForm.addEventListener('submit', async function(event) {
      event.preventDefault();

      const newLink = {
        name: document.getElementById('link-name').value,
        group: document.getElementById('link-group').value || undefined,
        url: document.getElementById('link-url').value,
        icon_class: document.getElementById('link-icon-class').value || undefined,
        color: document.getElementById('link-color').value || undefined,
        img_src: document.getElementById('link-img-src').value || undefined,
        text: document.getElementById('link-text').value || undefined,
        background_color: document.getElementById('link-background-color').value || undefined,
        border_radius: document.getElementById('link-border-radius').value || undefined,
        title: document.getElementById('link-title').value || undefined,
      };

      // Clean up empty strings for optional fields
      Object.keys(newLink).forEach(key => {
        if (newLink[key] === '') {
          delete newLink[key];
        }
      });

      try {
        const response = await fetch('/api/add_link', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newLink),
        });

        if (response.ok) {
          alert('Link added successfully!');
          addLinkForm.reset(); // Clear form
          fetchAndDisplayLinks(); // Refresh links
        } else {
          alert('Failed to add link.');
        }
      } catch (error) {
        console.error('Error adding link:', error);
        alert('Error adding link.');
      }
    });
  }

  // Edit Link functionality
  const editLinkPopup = document.getElementById('edit-link-popup');
  const editLinkForm = document.getElementById('edit-link-form');
  const editLinkIndexInput = document.getElementById('edit-link-index');

  function openEditLinkPopup(link, index) {
    editLinkIndexInput.value = index;
    document.getElementById('edit-link-name').value = link.name || '';
    document.getElementById('edit-link-group').value = link.group || '';
    document.getElementById('edit-link-url').value = link.url || '';
    document.getElementById('edit-link-icon-class').value = link.icon_class || '';
    document.getElementById('edit-link-color').value = link.color || '';
    document.getElementById('edit-link-img-src').value = link.img_src || '';
    document.getElementById('edit-link-text').value = link.text || '';
    document.getElementById('edit-link-background-color').value = link.background_color || '';
    document.getElementById('edit-link-border-radius').value = link.border_radius || '';
    document.getElementById('edit-link-title').value = link.title || '';
    editLinkPopup.style.display = 'block';
  }

  if (editLinkForm) {
    editLinkForm.addEventListener('submit', async function(event) {
      event.preventDefault();

      const linkId = editLinkIndexInput.value;
      const updatedLink = {
        name: document.getElementById('edit-link-name').value,
        group: document.getElementById('edit-link-group').value || undefined,
        url: document.getElementById('edit-link-url').value,
        icon_class: document.getElementById('edit-link-icon-class').value || undefined,
        color: document.getElementById('edit-link-color').value || undefined,
        img_src: document.getElementById('edit-link-img-src').value || undefined,
        text: document.getElementById('edit-link-text').value || undefined,
        background_color: document.getElementById('edit-link-background-color').value || undefined,
        border_radius: document.getElementById('edit-link-border-radius').value || undefined,
        title: document.getElementById('edit-link-title').value || undefined,
      };

      Object.keys(updatedLink).forEach(key => {
        if (updatedLink[key] === '') {
          delete updatedLink[key];
        }
      });

      try {
        const response = await fetch(`/api/links/${linkId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updatedLink),
        });

        if (response.ok) {
          alert('Link updated successfully!');
          editLinkPopup.style.display = 'none';
          fetchAndDisplayLinks();
        } else {
          alert('Failed to update link.');
        }
      } catch (error) {
        console.error('Error updating link:', error);
        alert('Error updating link.');
      }
    });
  }

  // Delete Link functionality
  async function deleteLink(linkId) {
    if (confirm('Are you sure you want to delete this link?')) {
      try {
        const response = await fetch(`/api/links/${linkId}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          alert('Link deleted successfully!');
          fetchAndDisplayLinks();
        } else {
          alert('Failed to delete link.');
        }
      } catch (error) {
        console.error('Error deleting link:', error);
        alert('Error deleting link.');
      }
    }
  }

  // Initial fetch and display of links
  fetchAndDisplayLinks();
});

// Functions from original index.js
function updateSearchEngine() {
  var selectedEngine = document.getElementById('search-engine').value;
  document.getElementById('current-search-engine').textContent = selectedEngine;
}

function checkEnter(event) {
  if (event.key === 'Enter') {
    search();
  }
}

function search() {
  var query = document.getElementById('searchQuery').value;
  var selectedEngine = document.getElementById('search-engine').value;

  if (query) {
    window.location.href = 'https://' + selectedEngine + '.com/search?q=' + encodeURIComponent(query);
  }
}

function updateDateTime() {
  const now = new Date();
  const optionsDate = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const optionsTime = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
  document.getElementById('currentDate').innerText = now.toLocaleDateString('en-US', optionsDate);
  document.getElementById('currentTime').innerText = now.toLocaleTimeString('en-US', optionsTime);
}

// Update the date and time on page load
updateDateTime();

// Update the time every second
setInterval(updateDateTime, 1000);