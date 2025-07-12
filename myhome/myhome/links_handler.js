document.addEventListener('DOMContentLoaded', function() {
  const linksContainer = document.getElementById('links-container');
  const addLinkForm = document.getElementById('add-link-form');

  // Function to fetch and display links
  async function fetchAndDisplayLinks() {
    try {
      const response = await fetch('/api/groups');
      const groups = await response.json();
      linksContainer.innerHTML = ''; // Clear existing links

      groups.forEach(group => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'link-group';
        groupDiv.dataset.groupName = group.name;
        groupDiv.dataset.displayType = group.display_type || 'normal'; // Store display type

        const groupHeaderContainer = document.createElement('div');
        groupHeaderContainer.className = 'group-header-container';

        const groupTitle = document.createElement('h3');
        groupTitle.textContent = group.name;
        groupTitle.className = 'group-title';
        groupHeaderContainer.appendChild(groupTitle);

        // Add group reorder buttons
        const groupReorderButtons = document.createElement('div');
        groupReorderButtons.className = 'group-reorder-buttons';
        
        const groupUpButton = document.createElement('button');
        groupUpButton.textContent = '↑';
        groupUpButton.className = 'reorder-btn';
        groupUpButton.onclick = (e) => {
          e.stopPropagation();
          moveGroup(group.name, -1);
        };
        groupReorderButtons.appendChild(groupUpButton);
        
        const groupDownButton = document.createElement('button');
        groupDownButton.textContent = '↓';
        groupDownButton.className = 'reorder-btn';
        groupDownButton.onclick = (e) => {
          e.stopPropagation();
          moveGroup(group.name, 1);
        };
        groupReorderButtons.appendChild(groupDownButton);
        
        groupHeaderContainer.appendChild(groupReorderButtons);

        // Add edit group button (only visible in edit mode)
        const editGroupButton = document.createElement('button');
        editGroupButton.textContent = '';
        editGroupButton.className = 'edit-group-button';
        editGroupButton.onclick = () => openEditGroupPopup(group.name, group.display_type);
        groupHeaderContainer.appendChild(editGroupButton);

        groupDiv.appendChild(groupHeaderContainer);

        const groupList = document.createElement('ul');
        groupList.className = 'link-group-content';

        // Apply display type specific styling
        if (group.display_type === 'website-list') {
          groupList.classList.add('website-list-layout');
        } else {
          groupList.classList.add('normal-layout');
        }

        group.links.forEach((link, index) => {
          // Skip hidden items unless in edit mode
          if (link.hidden && !document.querySelector('.flex-container2').classList.contains('edit-mode')) {
            return;
          }

          const listItem = document.createElement('li');
          listItem.className = 'link-item';
          listItem.draggable = true;
          // We need a global index for links for drag/drop and edit/delete
          // This will be handled by the backend when fetching links flat
          // For now, we'll use a temporary index within the group
          listItem.dataset.linkIndex = `${group.name}-${index}`;
          
          // Add drag event listeners
          listItem.addEventListener('dragstart', handleDragStart);
          listItem.addEventListener('dragover', handleDragOver);
          listItem.addEventListener('drop', handleDrop);
          listItem.addEventListener('dragend', handleDragEnd);
          
          // Add visual indicator for hidden items in edit mode
          if (link.hidden && document.querySelector('.flex-container2').classList.contains('edit-mode')) {
            listItem.classList.add('hidden-item');
            listItem.style.opacity = '0.5';
            listItem.style.border = '2px dashed #666';
          }
          
          if (link.li_bg_color) {
            listItem.style.backgroundColor = link.li_bg_color;
          }
          if (link.li_hover_color) {
            listItem.addEventListener('mouseover', () => {
              listItem.style.backgroundColor = link.li_hover_color;
            });
            listItem.addEventListener('mouseout', () => {
              listItem.style.backgroundColor = link.li_bg_color || '';
            });
          }

          let linkContent;

          if (link.default_type === 'nerd-font' && link.icon_class) {
            linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''}" ${link.title ? `title="${link.title}"` : ''}><i class="${link.icon_class}"></i></a>`;
          } else if (link.default_type === 'img' && link.img_src) {
            linkContent = `<a href="${link.url}"><img src="${link.img_src}" width="50" height="50"></a>`;
          } else if (link.default_type === 'text' && link.text) {
            linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''}" ${link.title ? `title="${link.title}"` : ''}>${link.text}</a>`;
          } else {
            // Fallback if default_type is not set or doesn't match available content
            if (link.icon_class) {
              linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''}" ${link.title ? `title="${link.title}"` : ''}><i class="${link.icon_class}"></i></a>`;
            } else if (link.img_src) {
              linkContent = `<a href="${link.url}"><img src="${link.img_src}" width="50" height="50"></a>`;
            } else {
              linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''}" ${link.title ? `title="${link.title}"` : ''}>${link.name}</a>`;
            }
          }

          listItem.innerHTML = linkContent;
          // Apply font size if it's a text-based link (either default_type text or fallback to name)
          if (link.default_type === 'text' || link.default_type === 'nerd-font' || (!link.default_type && (link.icon_class || (!link.icon_class && !link.img_src)))) {
            listItem.style.fontSize = '40px';
          }

          const buttonContainer = document.createElement('div');
          buttonContainer.className = 'link-buttons';

          // Add reorder buttons
          const reorderButtonsContainer = document.createElement('div');
          reorderButtonsContainer.className = 'reorder-buttons';
          
          const upButton = document.createElement('button');
          upButton.textContent = '↑';
          upButton.className = 'reorder-btn';
          upButton.onclick = (e) => {
            e.stopPropagation();
            moveLink(link.group || 'Ungrouped', index, -1);
          };
          reorderButtonsContainer.appendChild(upButton);
          
          const downButton = document.createElement('button');
          downButton.textContent = '↓';
          downButton.className = 'reorder-btn';
          downButton.onclick = (e) => {
            e.stopPropagation();
            moveLink(link.group || 'Ungrouped', index, 1);
          };
          reorderButtonsContainer.appendChild(downButton);
          
          buttonContainer.appendChild(reorderButtonsContainer);

          const editButton = document.createElement('button');
          editButton.textContent = '';
          editButton.className = 'edit-button';
          editButton.onclick = () => openEditLinkPopup(link, index); // Pass original index
          buttonContainer.appendChild(editButton);

          const deleteButton = document.createElement('button');
          deleteButton.textContent = '';
          deleteButton.className = 'delete-button';
          deleteButton.onclick = () => deleteLink(link.group || 'Ungrouped', index); // Pass original index
          buttonContainer.appendChild(deleteButton);

          listItem.appendChild(buttonContainer);
          groupList.appendChild(listItem);
        });

        // Add button for adding new links to this group
        const addLinkItem = document.createElement('li');
        addLinkItem.className = 'link-item add-link-item';

        const addLinkSpan = document.createElement('span');
        addLinkSpan.textContent = '+';
        addLinkSpan.style.cursor = 'pointer';
        addLinkSpan.style.fontFamily = 'jetbrainsmono nfp';
        addLinkSpan.style.fontSize = '25px';
        addLinkSpan.style.alignContent = 'center';

        addLinkSpan.addEventListener('click', () => {
          document.getElementById('link-group').value = group.name === 'Ungrouped' ? '' : group.name;
          const addLinkPopup = document.getElementById('add-link-popup');
          addLinkPopup.classList.remove('hidden'); // Remove hidden class
        });
        addLinkItem.appendChild(addLinkSpan);
        groupList.appendChild(addLinkItem);

        groupDiv.appendChild(groupList);
        linksContainer.appendChild(groupDiv);
      });
    } catch (error) {
      console.error('Error fetching groups:', error);
    }
  }

  // Function to open edit group popup
  function openEditGroupPopup(currentGroupName, currentDisplayType) {
    const editGroupPopup = document.getElementById('edit-group-popup');
    const editGroupNameInput = document.getElementById('edit-group-name');
    const editGroupOriginalName = document.getElementById('edit-group-original-name');
    const editGroupDisplayType = document.getElementById('edit-group-display-type');
    
    editGroupNameInput.value = currentGroupName === 'Ungrouped' ? '' : currentGroupName;
    editGroupOriginalName.value = currentGroupName;
    editGroupDisplayType.value = currentDisplayType || 'normal';
    editGroupPopup.classList.remove('hidden');
  }

  // Function to update group name and display type
  async function updateGroup(originalGroupName, newGroupName, newDisplayType) {
    try {
      const response = await fetch(`/api/groups/${originalGroupName}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_name: newGroupName,
          display_type: newDisplayType
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update group on the server.');
      }

      return true;
    } catch (error) {
      console.error('Error updating group:', error);
      return false;
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
        default_type: document.getElementById('link-default-type').value || undefined,
        background_color: document.getElementById('link-background-color').value || undefined,
        border_radius: document.getElementById('link-border-radius').value || undefined,
        title: document.getElementById('link-title').value || undefined,
        li_bg_color: document.getElementById('link-li-bg-color').value || undefined,
        li_hover_color: document.getElementById('link-li-hover-color').value || undefined,
        hidden: document.getElementById('link-hidden').checked || undefined,
      };

      // Clean up empty strings and false values for optional fields
      Object.keys(newLink).forEach(key => {
        if (newLink[key] === '' || newLink[key] === false) {
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
    document.getElementById('edit-link-default-type').value = link.default_type || 'nerd-font';
    document.getElementById('edit-link-background-color').value = link.background_color || '';
    document.getElementById('edit-link-border-radius').value = link.border_radius || '';
    document.getElementById('edit-link-title').value = link.title || '';
    document.getElementById('edit-link-li-bg-color').value = link.li_bg_color || '';
    document.getElementById('edit-link-li-hover-color').value = link.li_hover_color || '';
    document.getElementById('edit-link-hidden').checked = link.hidden || false;
    editLinkPopup.classList.remove('hidden');
  }

  if (editLinkForm) {
    if (!editLinkForm.hasAttribute('data-listener-attached')) {
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
                default_type: document.getElementById('edit-link-default-type').value || undefined,
                background_color: document.getElementById('edit-link-background-color').value || undefined,
                border_radius: document.getElementById('edit-link-border-radius').value || undefined,
                title: document.getElementById('edit-link-title').value || undefined,
                li_bg_color: document.getElementById('edit-link-li-bg-color').value || undefined,
                li_hover_color: document.getElementById('edit-link-li-hover-color').value || undefined,
                hidden: document.getElementById('edit-link-hidden').checked || undefined,
            };

            // Clean up empty strings and false values for optional fields
            Object.keys(updatedLink).forEach(key => {
                if (updatedLink[key] === '' || updatedLink[key] === false) {
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
                    editLinkPopup.classList.add('hidden');
                    fetchAndDisplayLinks();
                } else {
                    alert('Failed to update link.');
                }
            } catch (error) {
                console.error('Error updating link:', error);
                alert('Error updating link.');
            }
        });
        editLinkForm.setAttribute('data-listener-attached', 'true');
    }
  }

  // Edit Group functionality
  const editGroupForm = document.getElementById('edit-group-form');
  if (editGroupForm) {
    if (!editGroupForm.hasAttribute('data-listener-attached')) {
      editGroupForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const originalGroupName = document.getElementById('edit-group-original-name').value;
        const newGroupName = document.getElementById('edit-group-name').value;
        const newDisplayType = document.getElementById('edit-group-display-type').value;

        if (originalGroupName === newGroupName && newDisplayType === (await getGroupDisplayType(originalGroupName))) {
          alert('No changes made to group.');
          document.getElementById('edit-group-popup').classList.add('hidden');
          return;
        }

        try {
          const success = await updateGroup(originalGroupName, newGroupName, newDisplayType);
          if (success) {
            alert('Group updated successfully!');
            document.getElementById('edit-group-popup').classList.add('hidden');
            fetchAndDisplayLinks();
          } else {
            alert('Failed to update group.');
          }
        } catch (error) {
          console.error('Error updating group:', error);
          alert('Error updating group.');
        }
      });
      editGroupForm.setAttribute('data-listener-attached', 'true');
    }
  }

  // Helper to get current group display type (for comparison)
  async function getGroupDisplayType(groupName) {
    try {
      const response = await fetch('/api/groups');
      const groups = await response.json();
      const group = groups.find(g => g.name === groupName);
      return group ? group.display_type : 'normal';
    } catch (error) {
      console.error('Error fetching group display type:', error);
      return 'normal';
    }
  }

  // Delete Link functionality
  async function deleteLink(groupName, linkIndexInGroup) {
    if (confirm('Are you sure you want to delete this link?')) {
      try {
        const response = await fetch('/api/groups');
        const groups = await response.json();
        
        const targetGroup = groups.find(g => g.name === groupName);
        if (!targetGroup) {
          alert('Group not found.');
          return;
        }

        const globalLinkIndex = groups.slice(0, groups.indexOf(targetGroup))
                                      .reduce((acc, g) => acc + g.links.length, 0) + linkIndexInGroup;

        const deleteResponse = await fetch(`/api/links/${globalLinkIndex}`, {
          method: 'DELETE',
        });

        if (deleteResponse.ok) {
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

  // Edit Mode Toggle functionality
  const editModeToggle = document.getElementById('edit-mode-toggle');
  const flexContainer2 = document.querySelector('.flex-container2');

  if (editModeToggle && flexContainer2) {
    editModeToggle.addEventListener('change', function() {
      if (this.checked) {
        flexContainer2.classList.add('edit-mode');
      } else {
        flexContainer2.classList.remove('edit-mode');
      }
      // Refresh the display when edit mode is toggled to show/hide items
      fetchAndDisplayLinks();
    });
  }

  // Drag and Drop functionality for links
  let draggedElement = null;
  let draggedIndex = null;

  function handleDragStart(e) {
    draggedElement = this;
    draggedIndex = this.dataset.linkIndex; // Store as string "groupName-index"
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
  }

  function handleDragOver(e) {
    if (e.preventDefault) {
      e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
  }

  async function handleDrop(e) {
    if (e.stopPropagation) {
      e.stopPropagation();
    }
    
    if (draggedElement !== this) {
      const [draggedGroup, draggedLinkIndexInGroup] = draggedIndex.split('-');
      const [targetGroup, targetLinkIndexInGroup] = this.dataset.linkIndex.split('-');

      // Fetch all groups to get the global indices
      const response = await fetch('/api/groups');
      const groups = await response.json();

      let globalDraggedIndex = -1;
      let globalTargetIndex = -1;
      let currentGlobalIndex = 0;

      for (const group of groups) {
        for (let i = 0; i < group.links.length; i++) {
          if (group.name === draggedGroup && i === parseInt(draggedLinkIndexInGroup)) {
            globalDraggedIndex = currentGlobalIndex;
          }
          if (group.name === targetGroup && i === parseInt(targetLinkIndexInGroup)) {
            globalTargetIndex = currentGlobalIndex;
          }
          currentGlobalIndex++;
        }
      }
      
      if (globalDraggedIndex !== -1 && globalTargetIndex !== -1) {
        swapLinks(globalDraggedIndex, globalTargetIndex);
      }
    }
    return false;
  }

  function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedElement = null;
    draggedIndex = null;
  }

  // Move link up or down within the same group
  async function moveLink(groupName, linkIndexInGroup, direction) {
    try {
      const response = await fetch('/api/groups');
      const groups = await response.json();
      
      const targetGroup = groups.find(g => g.name === groupName);
      if (!targetGroup) {
        alert('Group not found.');
        return;
      }

      const linksInGroup = targetGroup.links;
      const targetIndexInGroup = linkIndexInGroup + direction;
      
      // Check bounds
      if (targetIndexInGroup < 0 || targetIndexInGroup >= linksInGroup.length) {
        return;
      }
      
      // Calculate global indices for the swap
      let globalIndex1 = 0;
      let globalIndex2 = 0;
      let currentGlobalIndex = 0;

      for (const group of groups) {
        for (let i = 0; i < group.links.length; i++) {
          if (group.name === groupName && i === linkIndexInGroup) {
            globalIndex1 = currentGlobalIndex;
          }
          if (group.name === groupName && i === targetIndexInGroup) {
            globalIndex2 = currentGlobalIndex;
          }
          currentGlobalIndex++;
        }
      }

      await swapLinks(globalIndex1, globalIndex2);
      
    } catch (error) {
      console.error('Error moving link:', error);
    }
  }

  // Move entire group up or down
  async function moveGroup(groupName, direction) {
    try {
      const response = await fetch('/api/groups');
      const groups = await response.json();
      
      const currentIndex = groups.findIndex(g => g.name === groupName);
      const targetIndex = currentIndex + direction;
      
      // Check bounds
      if (targetIndex < 0 || targetIndex >= groups.length) {
        return;
      }
      
      // Swap the groups in the array
      [groups[currentIndex], groups[targetIndex]] = [groups[targetIndex], groups[currentIndex]];
      
      // Update the entire list of groups on the server
      await fetch('/api/groups', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(groups),
      });
      
      fetchAndDisplayLinks();
      
    } catch (error) {
      console.error('Error moving group:', error);
    }
  }

  // Swap two links by their indices
  async function swapLinks(index1, index2) {
    try {
      const response = await fetch('/api/links'); // Fetch flat links for easy swapping
      const links = await response.json();
      
      // Swap the links
      [links[index1], links[index2]] = [links[index2], links[index1]];
      
      // Update the entire list of links on the server
      await fetch('/api/links', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(links),
      });
      
      fetchAndDisplayLinks();
      
    } catch (error) {
      console.error('Error swapping links:', error);
    }
  }

  // Swap all links between two groups (This function is likely no longer needed with group reordering)
  async function swapGroups(group1Name, group2Name) {
    console.warn('swapGroups function is deprecated and may not work as expected with new data structure.');
    // This function would need to be re-evaluated if group content swapping is still desired.
  }
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