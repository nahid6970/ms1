document.addEventListener('DOMContentLoaded', function () {
  const linksContainer = document.getElementById('links-container');
  const addLinkForm = document.getElementById('add-link-form');
  let links = []; // Declare links here so it's accessible globally

  // Function to fetch and display links
  async function fetchAndDisplayLinks() {
    try {
      const response = await fetch('/api/links');
      links = await response.json(); // Assign to the global links variable
      linksContainer.innerHTML = ''; // Clear existing links

      const groupedElements = {}; // Store HTML elements grouped by name
      const groupedLinks = {}; // Store original links grouped by name
      const collapsibleGroups = {}; // Store collapsible groups separately

      const groupStyles = {};
      links.forEach(link => {
        const groupName = link.group || 'Ungrouped';
        if (!groupStyles[groupName]) {
            const groupLink = links.find(l => (l.group || 'Ungrouped') === groupName && l.display_style);
            if (groupLink) {
                groupStyles[groupName] = groupLink.display_style;
            }
        }
      });

      links.forEach((link, index) => { // Use the index from the original links array
        // Skip hidden items unless in edit mode
        if (link.hidden && !document.querySelector('.flex-container2').classList.contains('edit-mode')) {
          return;
        }

        const groupName = link.group || 'Ungrouped';
        if (!groupedElements[groupName]) {
          groupedElements[groupName] = [];
          groupedLinks[groupName] = [];
        }

        const displayStyle = groupStyles[groupName] || 'flex';
        let elementToAdd;

        if (displayStyle === 'list-item') {
            const simpleListItem = document.createElement('li');
            simpleListItem.className = 'simple-link-item';

            const simpleLink = document.createElement('a');
            simpleLink.href = link.url;
            simpleLink.target = '_blank';

            if (link.name && link.name.trim() !== '') {
                const truncatedName = link.name.length > 25 ? link.name.substring(0, 25) + '...' : link.name;
                const truncatedUrl = link.url.length > 25 ? link.url.substring(0, 25) + '...' : link.url;
                simpleLink.innerHTML = `<span class="link-name">${truncatedName}</span><span class="link-separator"> </span><span class="link-url">${truncatedUrl}</span>`;
            } else {
                const truncatedUrl = link.url.length > 25 ? link.url.substring(0, 25) + '...' : link.url;
                simpleLink.textContent = truncatedUrl;
            }
            
            simpleListItem.appendChild(simpleLink);

            // Add context menu
            simpleListItem.addEventListener('contextmenu', (event) => {
                const items = [
                    { label: 'Edit', action: () => openEditLinkPopup(link, index) },
                    { label: 'Copy', action: () => copyLink(link, index) },
                    { label: 'Delete', action: () => deleteLink(index) }
                ];
                showContextMenu(event, items);
            });
            
            elementToAdd = simpleListItem;
        } else {
            const listItem = document.createElement('li');
            listItem.className = `link-item ${link.default_type ? 'link-type-' + link.default_type : 'link-type-default'}`;
            listItem.draggable = true;
            listItem.dataset.linkIndex = index;

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
              linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''} ${link.font_size ? `font-size: ${link.font_size};` : ''}" title="${link.title || link.name}"><i class="${link.icon_class}"></i></a>`;
            } else if (link.default_type === 'img' && link.img_src) {
              const width = link.width || '50';
              const height = link.height || '50';
              linkContent = `<a href="${link.url}" title="${link.title || link.name}"><img src="${link.img_src}" width="${width}" height="${height}"></a>`;
            } else if (link.default_type === 'text' && link.text) {
              linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''} ${link.font_size ? `font-size: ${link.font_size};` : ''}" title="${link.title || link.name}">${link.text}</a>`;
            } else {
              // Fallback if default_type is not set or doesn't match available content
              if (link.icon_class) {
                linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''} ${link.font_size ? `font-size: ${link.font_size};` : ''}" title="${link.title || link.name}"><i class="${link.icon_class}"></i></a>`;
              } else if (link.img_src) {
                const width = link.width || '50';
                const height = link.height || '50';
                linkContent = `<a href="${link.url}" title="${link.title || link.name}"><img src="${link.img_src}" width="${width}" height="${height}"></a>`;
              } else {
                linkContent = `<a href="${link.url}" style="text-decoration: none; color: ${link.color || 'inherit'}; ${link.background_color ? `background-color: ${link.background_color};` : ''} ${link.border_radius ? `border-radius: ${link.border_radius};` : ''} ${link.font_size ? `font-size: ${link.font_size};` : ''}" title="${link.title || link.name}">${link.name}</a>`;
              }
            }

            listItem.innerHTML = linkContent;

            listItem.addEventListener('contextmenu', (event) => {
                const items = [
                    {
                        label: 'Edit',
                        action: () => openEditLinkPopup(link, index)
                    },
                    {
                        label: 'Copy',
                        action: () => copyLink(link, index)
                    },
                    {
                        label: 'Delete',
                        action: () => deleteLink(index)
                    }
                ];
                showContextMenu(event, items);
            });
            elementToAdd = listItem;
        }

        groupedElements[groupName].push(elementToAdd);
        groupedLinks[groupName].push({ link, index });

        // Check if this group should be collapsible
        if (link.collapsible) {
          collapsibleGroups[groupName] = true;
        }
      });

      // Create collapsible groups container at the top
      const collapsibleGroupNames = Object.keys(collapsibleGroups);
      if (collapsibleGroupNames.length > 0) {
        const collapsibleContainer = document.createElement('div');
        collapsibleContainer.className = 'group_type_top-container';

        // Create regular row for collapsed groups
        const regularRow = document.createElement('div');
        regularRow.className = 'group_type_top-row regular-row';

        // Sort groups by their original order in the links array to maintain consistent positioning
        const sortedGroupNames = collapsibleGroupNames.sort((a, b) => {
          const aFirstIndex = links.findIndex(link => (link.group || 'Ungrouped') === a);
          const bFirstIndex = links.findIndex(link => (link.group || 'Ungrouped') === b);
          return aFirstIndex - bFirstIndex;
        });

        sortedGroupNames.forEach((groupName, index) => {
          if (groupedElements[groupName] && groupedElements[groupName].length > 0) {
            const collapsibleGroup = createCollapsibleGroup(groupName, groupedElements[groupName], groupedLinks[groupName], index);
            regularRow.appendChild(collapsibleGroup);
          }
        });

        collapsibleContainer.appendChild(regularRow);
        linksContainer.appendChild(collapsibleContainer);
      }

      // Now append the regular grouped elements to the container
      const groupNames = Object.keys(groupedElements);
      for (let i = 0; i < groupNames.length; i++) {
        const groupName = groupNames[i];

        // Skip collapsible groups as they're already rendered above
        if (collapsibleGroups[groupName]) {
          continue;
        }

        // Skip empty groups (when all items are hidden)
        if (groupedElements[groupName].length === 0) {
          continue;
        }

        const groupDiv = createRegularGroup(groupName, groupedElements[groupName], groupedLinks[groupName]);
        linksContainer.appendChild(groupDiv);
      }
    } catch (error) {
      console.error('Error fetching links:', error);
    }
  }

  // Function to create a collapsible group
  function createCollapsibleGroup(groupName, elements, links, originalIndex) {
    const collapsibleGroup = document.createElement('div');
    collapsibleGroup.className = 'group_type_top';
    collapsibleGroup.dataset.groupName = groupName;
    collapsibleGroup.draggable = true;

    // Store original position for proper restoration
    collapsibleGroup.dataset.originalIndex = originalIndex;

    // Add drag event listeners for the group itself
    collapsibleGroup.addEventListener('dragstart', handleGroupDragStart);
    collapsibleGroup.addEventListener('dragover', handleGroupDragOver);
    collapsibleGroup.addEventListener('drop', handleGroupDrop);
    collapsibleGroup.addEventListener('dragend', handleGroupDragEnd);

    const header = document.createElement('div');
    header.className = 'group_type_top-header';

    const title = document.createElement('h4');
    title.className = 'group_type_top-title';

    // Use custom top name if available, otherwise use group name
    const firstLink = links[0];
    const displayName = (firstLink && firstLink.link.top_name) ? firstLink.link.top_name : groupName;
    title.textContent = displayName;

    // Apply custom styling if available
    if (firstLink && firstLink.link) {
      const linkData = firstLink.link;

      // Apply background color
      if (linkData.top_bg_color) {
        collapsibleGroup.style.backgroundColor = linkData.top_bg_color;
      }

      // Apply text color
      if (linkData.top_text_color) {
        title.style.color = linkData.top_text_color;
      }

      // Apply border color
      if (linkData.top_border_color) {
        collapsibleGroup.style.border = `1px solid ${linkData.top_border_color}`;
      }

      // Apply hover color
      if (linkData.top_hover_color) {
        collapsibleGroup.addEventListener('mouseenter', () => {
          collapsibleGroup.style.backgroundColor = linkData.top_hover_color;
        });
        collapsibleGroup.addEventListener('mouseleave', () => {
          collapsibleGroup.style.backgroundColor = linkData.top_bg_color || '';
        });
      }
    }

    // Add edit buttons container
    const editButtons = document.createElement('div');
    editButtons.className = 'edit-buttons';

    const editBtn = document.createElement('button');
    editBtn.className = 'group_type_top-edit-btn';
    editBtn.textContent = ''; //⚙️
    editBtn.onclick = (e) => {
      e.stopPropagation();
      openEditGroupPopup(groupName);
    };
    editButtons.appendChild(editBtn);

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'group_type_top-toggle-btn';
    toggleBtn.textContent = '▼';

    header.appendChild(title);
    header.appendChild(editButtons);
    header.appendChild(toggleBtn);

    const content = document.createElement('ul');
    content.className = 'group_type_top-content';

    // Create elements for collapsible group with full functionality
    elements.forEach((element, index) => {
      const clonedElement = element.cloneNode(true);

      // Re-add drag functionality to cloned elements
      clonedElement.addEventListener('dragstart', handleDragStart);
      clonedElement.addEventListener('dragover', handleDragOver);
      clonedElement.addEventListener('drop', handleDrop);
      clonedElement.addEventListener('dragend', handleDragEnd);

      // Re-add context menu
      const linkInfo = links[index];
      clonedElement.addEventListener('contextmenu', (event) => {
        const items = [
            {
                label: 'Edit',
                action: () => openEditLinkPopup(linkInfo.link, linkInfo.index)
            },
            {
                label: 'Copy',
                action: () => copyLink(linkInfo.link, linkInfo.index)
            },
            {
                label: 'Delete',
                action: () => deleteLink(linkInfo.index)
            }
        ];
        showContextMenu(event, items);
      });

      // Keep edit buttons but update their functionality for top groups
      const buttons = clonedElement.querySelector('.link-buttons');
      if (buttons) {
        const editButton = buttons.querySelector('.edit-button');
        const deleteButton = buttons.querySelector('.delete-button');

        if (editButton) {
          const originalIndex = parseInt(clonedElement.dataset.linkIndex);
          editButton.onclick = () => openEditLinkPopup(links.find(l => l.index === originalIndex).link, originalIndex);
        }

        if (deleteButton) {
          const originalIndex = parseInt(clonedElement.dataset.linkIndex);
          deleteButton.onclick = () => deleteLink(originalIndex);
        }
      }

      content.appendChild(clonedElement);
    });

    // Add button for adding new links to this collapsible group
    const addLinkItem = document.createElement('li');
    addLinkItem.className = 'link-item add-link-item';

    const addLinkSpan = document.createElement('span');
    addLinkSpan.textContent = '+';
    addLinkSpan.style.cursor = 'pointer';
    addLinkSpan.style.fontFamily = 'jetbrainsmono nfp';
    addLinkSpan.style.fontSize = '25px';
    addLinkSpan.style.alignContent = 'center';

    addLinkItem.addEventListener('click', () => {
      document.getElementById('link-group').value = groupName === 'Ungrouped' ? '' : groupName;
      const addLinkPopup = document.getElementById('add-link-popup');
      addLinkPopup.classList.remove('hidden'); // Remove hidden class
      applyPopupStyling(groupName);
    });
    addLinkItem.appendChild(addLinkSpan);
    content.appendChild(addLinkItem);

    // Add toggle functionality with repositioning
    let isDragging = false;
    let dragTimeout = null;

    // Create a more robust drag state management
    const setDragState = (dragging) => {
      isDragging = dragging;
      if (dragging) {
        collapsibleGroup.classList.add('drag-active');
        // Clear any existing timeout
        if (dragTimeout) {
          clearTimeout(dragTimeout);
        }
      } else {
        // Use a longer timeout to ensure drag operations are complete
        dragTimeout = setTimeout(() => {
          isDragging = false;
          collapsibleGroup.classList.remove('drag-active');
        }, 300);
      }
    };

    // Track drag state on the content area
    content.addEventListener('dragstart', (e) => {
      setDragState(true);
      e.stopPropagation();
    });

    content.addEventListener('dragend', (e) => {
      setDragState(false);
    });

    // Prevent all drag-related events from bubbling to header
    content.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
    });

    content.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      // Reset drag state after drop
      setDragState(false);
    });

    // Also listen for mouse events during drag to prevent accidental clicks
    content.addEventListener('mousedown', (e) => {
      if (e.target.closest('.link-item')) {
        // Small delay to detect if this is start of a drag
        setTimeout(() => {
          if (document.querySelector('.link-item.dragging')) {
            setDragState(true);
          }
        }, 50);
      }
    });

    header.addEventListener('click', (e) => {
      // Don't trigger if clicking on edit button or during drag operations
      if (e.target.classList.contains('group_type_top-edit-btn') ||
        isDragging ||
        collapsibleGroup.classList.contains('drag-active')) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }

      const wasExpanded = content.classList.contains('expanded');

      // Close all other expanded groups first and properly restore them
      const allGroups = document.querySelectorAll('.group_type_top');
      const groupsToRestore = [];

      allGroups.forEach(group => {
        const groupContent = group.querySelector('.group_type_top-content');
        const groupToggle = group.querySelector('.group_type_top-toggle-btn');
        if (group !== collapsibleGroup) {
          // Always ensure proper state cleanup for all other groups
          groupContent.classList.remove('expanded');
          groupToggle.textContent = '▼';
          group.classList.remove('expanded');

          // Collect groups that need to be moved back
          if (group.closest('.expanded-row')) {
            groupsToRestore.push(group);
          }
        }
      });

      // Move all groups back to regular row in their original order
      groupsToRestore.forEach(group => {
        moveToRegularRowInOrder(group);
      });

      // Clean up empty expanded rows
      cleanupEmptyRows();

      // Toggle current group
      content.classList.toggle('expanded');
      toggleBtn.textContent = content.classList.contains('expanded') ? '▲' : '▼';

      // Move expanded group to top by adding expanded class
      if (content.classList.contains('expanded')) {
        collapsibleGroup.classList.add('expanded');
        // Move to expanded row
        moveToExpandedRow(collapsibleGroup);
      } else {
        collapsibleGroup.classList.remove('expanded');
        // Move back to regular row
        moveToRegularRow(collapsibleGroup);
        // Clean up empty rows after moving
        cleanupEmptyRows();
      }
    });

    collapsibleGroup.appendChild(header);
    collapsibleGroup.appendChild(content);

    return collapsibleGroup;
  }

  // Function to move group to expanded row (top)
  function moveToExpandedRow(group) {
    const container = document.querySelector('.group_type_top-container');
    let expandedRow = container.querySelector('.expanded-row');

    if (!expandedRow) {
      expandedRow = document.createElement('div');
      expandedRow.className = 'group_type_top-row expanded-row';
      container.insertBefore(expandedRow, container.firstChild);
    }

    expandedRow.appendChild(group);
  }

  // Function to move group back to regular row (maintain original position)
  function moveToRegularRow(group) {
    const container = document.querySelector('.group_type_top-container');
    let regularRow = container.querySelector('.regular-row');

    if (!regularRow) {
      regularRow = document.createElement('div');
      regularRow.className = 'group_type_top-row regular-row';
      container.appendChild(regularRow);
    }

    // Get the original index to maintain position
    const originalIndex = parseInt(group.dataset.originalIndex) || 0;
    const existingGroups = Array.from(regularRow.children);

    // Find the correct position to insert based on original index
    let insertPosition = 0;
    for (let i = 0; i < existingGroups.length; i++) {
      const existingIndex = parseInt(existingGroups[i].dataset.originalIndex) || 0;
      if (originalIndex < existingIndex) {
        insertPosition = i;
        break;
      }
      insertPosition = i + 1;
    }

    // Insert at the correct position
    if (insertPosition >= existingGroups.length) {
      regularRow.appendChild(group);
    } else {
      regularRow.insertBefore(group, existingGroups[insertPosition]);
    }
  }

  // Function to move group back to regular row maintaining original order
  function moveToRegularRowInOrder(group) {
    const container = document.querySelector('.group_type_top-container');
    let regularRow = container.querySelector('.regular-row');

    if (!regularRow) {
      regularRow = document.createElement('div');
      regularRow.className = 'group_type_top-row regular-row';
      container.appendChild(regularRow);
    }

    // Get the original index to maintain position
    const originalIndex = parseInt(group.dataset.originalIndex) || 0;
    const existingGroups = Array.from(regularRow.children);

    // Find the correct position to insert based on original index
    let insertPosition = 0;
    for (let i = 0; i < existingGroups.length; i++) {
      const existingIndex = parseInt(existingGroups[i].dataset.originalIndex) || 0;
      if (originalIndex < existingIndex) {
        insertPosition = i;
        break;
      }
      insertPosition = i + 1;
    }

    // Insert at the correct position
    if (insertPosition >= existingGroups.length) {
      regularRow.appendChild(group);
    } else {
      regularRow.insertBefore(group, existingGroups[insertPosition]);
    }
  }

  // Function to clean up empty rows
  function cleanupEmptyRows() {
    const container = document.querySelector('.collapsible-groups-container');
    if (!container) return;

    const expandedRows = container.querySelectorAll('.expanded-row');
    expandedRows.forEach(row => {
      if (row.children.length === 0) {
        row.remove();
      }
    });

    const regularRows = container.querySelectorAll('.regular-row');
    regularRows.forEach(row => {
      if (row.children.length === 0) {
        row.remove();
      }
    });
  }

    function createMultiColumnList(elements, groupName) {
    const container = document.createElement('div');
    container.className = 'multi-column-container';
    
    function buildColumns() {
        // Clear existing content
        container.innerHTML = '';
        
        const isSmallScreen = window.innerWidth <= 600;
        
        if (isSmallScreen) {
            // Single column for small screens
            container.style.display = 'flex';
            container.style.flexDirection = 'column';
            
            const column = document.createElement('div');
            column.style.display = 'flex';
            column.style.flexDirection = 'column';
            
            elements.forEach(element => {
                column.appendChild(element.cloneNode(true));
            });
            
            container.appendChild(column);
        } else {
            // Multi-column for larger screens
            container.style.display = 'flex';
            container.style.flexDirection = 'row';
            container.style.gap = '20px';
            
            let currentColumn = document.createElement('div');
            currentColumn.style.display = 'flex';
            currentColumn.style.flexDirection = 'column';
            container.appendChild(currentColumn);
            
            elements.forEach((element, index) => {
                if (index > 0 && index % 5 === 0) {
                    currentColumn = document.createElement('div');
                    currentColumn.style.display = 'flex';
                    currentColumn.style.flexDirection = 'column';
                    container.appendChild(currentColumn);
                }
                currentColumn.appendChild(element.cloneNode(true));
            });
        }
        
        // Add the '+' button to the last column
        const addLinkItem = document.createElement('li');
        addLinkItem.className = 'link-item add-link-item';
        addLinkItem.style.width = 'auto';
        addLinkItem.style.height = '30px';
        addLinkItem.style.minWidth = '30px';
        addLinkItem.style.minHeight = '30px';

        const addLinkSpan = document.createElement('span');
        addLinkSpan.textContent = '+';
        addLinkSpan.style.cursor = 'pointer';
        addLinkSpan.style.fontSize = '20px';
        addLinkSpan.style.display = 'flex';
        addLinkSpan.style.alignItems = 'center';
        addLinkSpan.style.justifyContent = 'center';
        addLinkSpan.style.width = '100%';
        addLinkSpan.style.height = '100%';

        addLinkItem.addEventListener('click', () => {
            document.getElementById('link-group').value = groupName === 'Ungrouped' ? '' : groupName;
            const addLinkPopup = document.getElementById('add-link-popup');
            addLinkPopup.classList.remove('hidden');
            applyPopupStyling(groupName);
        });

        addLinkItem.appendChild(addLinkSpan);
        
        // Add to the last column
        const lastColumn = container.lastElementChild;
        if (lastColumn) {
            lastColumn.appendChild(addLinkItem);
        }
    }
    
    // Initial build
    buildColumns();
    
    // Add resize listener to rebuild columns when window is resized
    const resizeHandler = () => {
        buildColumns();
    };
    
    window.addEventListener('resize', resizeHandler);
    
    // Store the resize handler so it can be removed if needed
    container._resizeHandler = resizeHandler;
    
    return container;
}

    function createRegularGroup(groupName, elements, linksInGroup) {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'link-group';
    groupDiv.dataset.groupName = groupName;
    groupDiv.draggable = true;

    // Add drag event listeners for the group itself
    groupDiv.addEventListener('dragstart', handleGroupDragStart);
    groupDiv.addEventListener('dragover', handleGroupDragOver);
    groupDiv.addEventListener('drop', handleGroupDrop);
    groupDiv.addEventListener('dragend', handleGroupDragEnd);

    const firstLinkInGroup = linksInGroup[0];
    if (firstLinkInGroup && firstLinkInGroup.link.horizontal_stack) {
      groupDiv.classList.add('group_type_box');
      
      // Apply custom horizontal stack styling
      const linkData = firstLinkInGroup.link;
      if (linkData.horizontal_bg_color) {
        groupDiv.style.setProperty('--horizontal-bg-color', linkData.horizontal_bg_color);
      }
      if (linkData.horizontal_text_color) {
        groupDiv.style.setProperty('--horizontal-text-color', linkData.horizontal_text_color);
      }
      if (linkData.horizontal_border_color) {
        groupDiv.style.setProperty('--horizontal-border-color', linkData.horizontal_border_color);
      }
      if (linkData.horizontal_hover_color) {
        groupDiv.style.setProperty('--horizontal-hover-color', linkData.horizontal_hover_color);
      }

      groupDiv.onclick = () => {
        const isPasswordProtected = firstLinkInGroup.link.password_protect;
        if (isPasswordProtected) {
          const password = prompt("Please enter the password to extend the group:");
          if (password !== "1823") {
            alert("Incorrect password!");
            return;
          }
        }

        const popup = document.getElementById('group_type_box-popup');
        const popupContent = popup.querySelector('.popup-content-inner');
        popupContent.innerHTML = '';
        elements.forEach(element => {
          const clonedElement = element.cloneNode(true);
          const linkIndex = parseInt(clonedElement.dataset.linkIndex);
          const linkData = linksInGroup.find(l => l.index === linkIndex);

          clonedElement.addEventListener('dragstart', handleDragStart);
          clonedElement.addEventListener('dragover', handleDragOver);
          clonedElement.addEventListener('drop', handleDrop);
          clonedElement.addEventListener('dragend', handleDragEnd);

          // Re-add context menu
          if (linkData) {
            clonedElement.addEventListener('contextmenu', (event) => {
                const items = [
                    {
                        label: 'Edit',
                        action: () => openEditLinkPopup(linkData.link, linkData.index)
                    },
                    {
                        label: 'Copy',
                        action: () => copyLink(linkData.link, linkData.index)
                    },
                    {
                        label: 'Delete',
                        action: () => deleteLink(linkData.index)
                    }
                ];
                showContextMenu(event, items);
            });
          }

          if (linkData.link.li_bg_color) {
            clonedElement.style.backgroundColor = linkData.link.li_bg_color;
          }
          if (linkData.link.li_hover_color) {
            clonedElement.addEventListener('mouseover', () => {
              clonedElement.style.backgroundColor = linkData.link.li_hover_color;
            });
            clonedElement.addEventListener('mouseout', () => {
              clonedElement.style.backgroundColor = linkData.link.li_bg_color || '';
            });
          }

          const editButton = clonedElement.querySelector('.edit-button');
          if (editButton && linkData) {
            editButton.onclick = () => openEditLinkPopup(linkData.link, linkIndex);
          }

          const deleteButton = clonedElement.querySelector('.delete-button');
          if (deleteButton) {
            deleteButton.onclick = () => deleteLink(linkIndex);
          }

          popupContent.appendChild(clonedElement);
        });

        const addLinkItem = document.createElement('li');
        addLinkItem.className = 'link-item add-link-item';
        addLinkItem.draggable = false;

        const addLinkSpan = document.createElement('span');
        addLinkSpan.textContent = '+';
        addLinkSpan.style.fontFamily = 'jetbrainsmono nfp';
        addLinkSpan.style.fontSize = '25px';
        addLinkSpan.style.width = '100%';
        addLinkSpan.style.height = '100%';
        addLinkSpan.style.display = 'flex';
        addLinkSpan.style.alignItems = 'center';
        addLinkSpan.style.justifyContent = 'center';

        addLinkItem.addEventListener('click', () => {
          document.getElementById('link-group').value = groupName === 'Ungrouped' ? '' : groupName;
          const addLinkPopup = document.getElementById('add-link-popup');
          addLinkPopup.classList.remove('hidden'); // Remove hidden class
          applyPopupStyling(groupName);
        });
        addLinkItem.appendChild(addLinkSpan);
        popupContent.appendChild(addLinkItem);

        popup.classList.remove('hidden');
        applyPopupStyling(groupName);
      };
    }

    const groupHeaderContainer = document.createElement('div');
    groupHeaderContainer.className = 'group-header-container';

    const groupTitle = document.createElement('h3');
    groupTitle.textContent = groupName;
    groupTitle.className = 'group-title';
    groupHeaderContainer.appendChild(groupTitle);

    const isPasswordProtected = firstLinkInGroup.link.password_protect;

    if (isPasswordProtected) {
      const lockIcon = document.createElement('span');
      lockIcon.className = 'lock-icon';
      lockIcon.innerHTML = '<i class="nf nf-fa-lock"></i>';
      groupTitle.appendChild(lockIcon);
    }

    // Add group reorder buttons
    const groupReorderButtons = document.createElement('div');
    groupReorderButtons.className = 'group-reorder-buttons';

    const groupUpButton = document.createElement('button');
    groupUpButton.textContent = ''; //↑
    groupUpButton.className = 'reorder-btn';
    groupUpButton.onclick = (e) => {
      e.stopPropagation();
      moveGroup(groupName, -1);
    };
    groupReorderButtons.appendChild(groupUpButton);

    const groupDownButton = document.createElement('button');
    groupDownButton.textContent = ''; //↓
    groupDownButton.className = 'reorder-btn';
    groupDownButton.onclick = (e) => {
      e.stopPropagation();
      moveGroup(groupName, 1);
    };
    groupReorderButtons.appendChild(groupDownButton);

    groupHeaderContainer.appendChild(groupReorderButtons);

    // Add edit group button (only visible in edit mode)
    const editGroupButton = document.createElement('button');
    editGroupButton.textContent = ''; //⚙️
    editGroupButton.className = 'edit-group-button';
    editGroupButton.onclick = () => openEditGroupPopup(groupName);
    groupHeaderContainer.appendChild(editGroupButton);

    groupDiv.appendChild(groupHeaderContainer);

    if (firstLinkInGroup && !firstLinkInGroup.link.horizontal_stack) {
      const groupLinkWithStyle = linksInGroup.find(l => l.link.display_style);
      const displayStyle = groupLinkWithStyle ? groupLinkWithStyle.link.display_style : 'flex';

      if (displayStyle === 'list-item') {
        const multiColumnList = createMultiColumnList(elements, groupName);
        groupDiv.appendChild(multiColumnList);
      } else {
        const groupList = document.createElement('ul');
        groupList.className = 'group_type_normal';
        groupList.style.display = displayStyle;

        elements.forEach(element => {
          groupList.appendChild(element);
        });

        // Add button for adding new links to this group
        const addLinkItem = document.createElement('li');
        addLinkItem.className = 'link-item add-link-item';
        addLinkItem.draggable = false;

        const addLinkSpan = document.createElement('span');
        addLinkSpan.textContent = '+';
        addLinkSpan.style.fontFamily = 'jetbrainsmono nfp';
        addLinkSpan.style.fontSize = '25px';
        addLinkSpan.style.width = '100%';
        addLinkSpan.style.height = '100%';
        addLinkSpan.style.display = 'flex';
        addLinkSpan.style.alignItems = 'center';
        addLinkSpan.style.justifyContent = 'center';

        addLinkItem.addEventListener('click', () => {
          document.getElementById('link-group').value = groupName === 'Ungrouped' ? '' : groupName;
          const addLinkPopup = document.getElementById('add-link-popup');
          addLinkPopup.classList.remove('hidden'); // Remove hidden class
          applyPopupStyling(groupName);
        });
        addLinkItem.appendChild(addLinkSpan);
        groupList.appendChild(addLinkItem);

        groupDiv.appendChild(groupList);
      }
    }

    return groupDiv;
  }
  // Function to open edit group popup
  function openEditGroupPopup(currentGroupName) {
    const editGroupPopup = document.getElementById('edit-group-popup');
    const editGroupNameInput = document.getElementById('edit-group-name');
    const editGroupOriginalName = document.getElementById('edit-group-original-name');
    const editGroupDisplaySelect = document.getElementById('edit-group-display');
    const editGroupCollapsibleCheckbox = document.getElementById('edit-group-collapsible');
    const editGroupHorizontalStackCheckbox = document.getElementById('edit-group-horizontal-stack');
    const editGroupPasswordProtectCheckbox = document.getElementById('edit-group-password-protect');
    const editGroupTopNameInput = document.getElementById('edit-group-top-name');
    const editGroupTopBgColorInput = document.getElementById('edit-group-top-bg-color');
    const editGroupTopTextColorInput = document.getElementById('edit-group-top-text-color');
    const editGroupTopBorderColorInput = document.getElementById('edit-group-top-border-color');
    const editGroupTopHoverColorInput = document.getElementById('edit-group-top-hover-color');
    const editGroupPopupBgColorInput = document.getElementById('edit-group-popup-bg-color');
    const editGroupPopupTextColorInput = document.getElementById('edit-group-popup-text-color');
    const editGroupPopupBorderColorInput = document.getElementById('edit-group-popup-border-color');
    const editGroupPopupBorderRadiusInput = document.getElementById('edit-group-popup-border-radius');
    const editGroupHorizontalBgColorInput = document.getElementById('edit-group-horizontal-bg-color');
    const editGroupHorizontalTextColorInput = document.getElementById('edit-group-horizontal-text-color');
    const editGroupHorizontalBorderColorInput = document.getElementById('edit-group-horizontal-border-color');
    const editGroupHorizontalHoverColorInput = document.getElementById('edit-group-horizontal-hover-color');
    const collapsibleRenameSection = document.getElementById('collapsible-rename-section');

    editGroupNameInput.value = currentGroupName === 'Ungrouped' ? '' : currentGroupName;
    editGroupOriginalName.value = currentGroupName;

    // Find a link in the current group to get its display_style, collapsible setting, and styling options
    const linksInGroup = links.filter(link => (link.group || 'Ungrouped') === currentGroupName);
    if (linksInGroup.length > 0) {
      editGroupDisplaySelect.value = linksInGroup[0].display_style || 'flex';
      editGroupCollapsibleCheckbox.checked = linksInGroup[0].collapsible || false;
      editGroupHorizontalStackCheckbox.checked = linksInGroup[0].horizontal_stack || false;
      editGroupPasswordProtectCheckbox.checked = linksInGroup[0].password_protect || false;
      editGroupTopNameInput.value = linksInGroup[0].top_name || '';
      editGroupTopBgColorInput.value = linksInGroup[0].top_bg_color || '#2d2d2d';
      editGroupTopTextColorInput.value = linksInGroup[0].top_text_color || '#ffffff';
      editGroupTopBorderColorInput.value = linksInGroup[0].top_border_color || '#444444';
      editGroupTopHoverColorInput.value = linksInGroup[0].top_hover_color || '#3a3a3a';
      editGroupPopupBgColorInput.value = linksInGroup[0].popup_bg_color || '#31343a';
      editGroupPopupTextColorInput.value = linksInGroup[0].popup_text_color || '#ffffff';
      editGroupPopupBorderColorInput.value = linksInGroup[0].popup_border_color || 'transparent';
      editGroupPopupBorderRadiusInput.value = linksInGroup[0].popup_border_radius || '8px';
      editGroupHorizontalBgColorInput.value = linksInGroup[0].horizontal_bg_color || '#2d2d2d';
      editGroupHorizontalTextColorInput.value = linksInGroup[0].horizontal_text_color || '#ffffff';
      editGroupHorizontalBorderColorInput.value = linksInGroup[0].horizontal_border_color || '#0056b3';
      editGroupHorizontalHoverColorInput.value = linksInGroup[0].horizontal_hover_color || '#3a3a3a';
    } else {
      editGroupDisplaySelect.value = 'flex'; // Default if no links in group
      editGroupCollapsibleCheckbox.checked = false;
      editGroupHorizontalStackCheckbox.checked = false;
      editGroupPasswordProtectCheckbox.checked = false;
      editGroupTopNameInput.value = '';
      editGroupTopBgColorInput.value = '#2d2d2d';
      editGroupTopTextColorInput.value = '#ffffff';
      editGroupTopBorderColorInput.value = '#444444';
      editGroupTopHoverColorInput.value = '#3a3a3a';
      editGroupPopupBgColorInput.value = '#31343a';
      editGroupPopupTextColorInput.value = '#ffffff';
      editGroupPopupBorderColorInput.value = 'transparent';
      editGroupPopupBorderRadiusInput.value = '8px';
      editGroupHorizontalBgColorInput.value = '#2d2d2d';
      editGroupHorizontalTextColorInput.value = '#ffffff';
      editGroupHorizontalBorderColorInput.value = '#0056b3';
      editGroupHorizontalHoverColorInput.value = '#3a3a3a';
    }

    // Show/hide the rename section based on collapsible checkbox
    function toggleRenameSection() {
      if (editGroupCollapsibleCheckbox.checked) {
        collapsibleRenameSection.style.display = 'block';
      } else {
        collapsibleRenameSection.style.display = 'none';
      }
    }

    // Show/hide styling sections based on group type
    function toggleStylingSections() {
      const horizontalStackStylingSection = document.getElementById('horizontal-stack-styling-section');
      
      // Show horizontal stack styling for horizontal stack groups, but not for collapsible groups
      if (editGroupHorizontalStackCheckbox.checked && !editGroupCollapsibleCheckbox.checked) {
        horizontalStackStylingSection.style.display = 'block';
      } else {
        horizontalStackStylingSection.style.display = 'none';
      }
    }

    // Initial toggle
    toggleRenameSection();
    toggleStylingSections();

    // Add event listener for checkbox changes
    editGroupCollapsibleCheckbox.addEventListener('change', () => {
      toggleRenameSection();
      toggleStylingSections();
    });
    
    editGroupHorizontalStackCheckbox.addEventListener('change', toggleStylingSections);

    editGroupPopup.classList.remove('hidden');
    applyPopupStyling(currentGroupName);
  }

  // Drag and Drop functionality for collapsible groups
  let draggedGroup = null;

  function handleGroupDragStart(e) {
    if (!document.querySelector('.flex-container2').classList.contains('edit-mode')) {
        e.preventDefault();
        return;
    }
    draggedGroup = this;
    this.style.opacity = '0.5';
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
  }

  function handleGroupDragOver(e) {
    if (e.preventDefault) {
      e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
  }

  function handleGroupDrop(e) {
    if (e.stopPropagation) {
      e.stopPropagation();
    }

    if (draggedGroup !== this) {
      const draggedGroupName = draggedGroup.dataset.groupName;
      const targetGroupName = this.dataset.groupName;
      
      if (draggedGroup.classList.contains('group_type_top')) {
        swapCollapsibleGroups(draggedGroupName, targetGroupName);
      } else {
        moveGroup(draggedGroupName, targetGroupName);
      }
    }
    return false;
  }

  function handleGroupDragEnd(e) {
    this.style.opacity = '';
    draggedGroup = null;
  }

  // Function to swap collapsible groups
  async function swapCollapsibleGroups(group1Name, group2Name) {
    try {
      const response = await fetch('/api/links');
      const links = await response.json();

      // Find all links in both groups
      const group1Links = [];
      const group2Links = [];
      const otherLinks = [];

      links.forEach((link, index) => {
        const linkGroup = link.group || 'Ungrouped';
        if (linkGroup === group1Name) {
          group1Links.push({ link, index });
        } else if (linkGroup === group2Name) {
          group2Links.push({ link, index });
        } else {
          otherLinks.push({ link, index });
        }
      });

      // Create new links array with swapped group positions
      const newLinks = [];

      // Add other groups first (maintain their positions)
      const processedGroups = new Set([group1Name, group2Name]);
      const groupOrder = [...new Set(links.map(link => link.group || 'Ungrouped'))];

      groupOrder.forEach(groupName => {
        if (groupName === group1Name) {
          group2Links.forEach(item => newLinks.push(item.link));
        } else if (groupName === group2Name) {
          group1Links.forEach(item => newLinks.push(item.link));
        } else {
          const groupLinks = links.filter(link => (link.group || 'Ungrouped') === groupName);
          groupLinks.forEach(link => newLinks.push(link));
        }
      });

      // Update the entire list of links on the server
      await fetch('/api/links', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLinks),
      });

      fetchAndDisplayLinks();

    } catch (error) {
      console.error('Error swapping collapsible groups:', error);
    }
  }

  // Function to update group name for all links in that group
  async function updateGroupName(originalGroupName, newGroupName, newDisplayStyle, isCollapsible, isHorizontalStack, isPasswordProtected, topName, topBgColor, topTextColor, topBorderColor, topHoverColor, popupBgColor, popupTextColor, popupBorderColor, popupBorderRadius, horizontalBgColor, horizontalTextColor, horizontalBorderColor, horizontalHoverColor) {
    try {
      const response = await fetch('/api/links');
      const links = await response.json();

      // Create a new array with the updated group names, display styles, collapsible setting, and styling options
      const newLinks = links.map(link => {
        const linkGroupName = link.group || 'Ungrouped';
        if (linkGroupName === originalGroupName) {
          const updatedLink = { ...link };
          if (newGroupName && newGroupName !== '') {
            updatedLink.group = newGroupName;
          } else {
            delete updatedLink.group; // For "Ungrouped"
          }
          updatedLink.display_style = newDisplayStyle;
          updatedLink.collapsible = isCollapsible;
          updatedLink.horizontal_stack = isHorizontalStack;
          updatedLink.password_protect = isPasswordProtected;

          // Handle top group styling options
          if (topName && topName !== '') {
            updatedLink.top_name = topName;
          } else {
            delete updatedLink.top_name;
          }

          updatedLink.top_bg_color = topBgColor || '#2d2d2d';
          updatedLink.top_text_color = topTextColor || '#ffffff';
          updatedLink.top_border_color = topBorderColor || '#444444';
          updatedLink.top_hover_color = topHoverColor || '#3a3a3a';

          // Handle popup styling options
          updatedLink.popup_bg_color = popupBgColor || '#31343a';
          updatedLink.popup_text_color = popupTextColor || '#ffffff';
          updatedLink.popup_border_color = popupBorderColor || 'transparent';
          updatedLink.popup_border_radius = popupBorderRadius || '8px';

          // Handle horizontal stack styling options
          updatedLink.horizontal_bg_color = horizontalBgColor || '#2d2d2d';
          updatedLink.horizontal_text_color = horizontalTextColor || '#ffffff';
          updatedLink.horizontal_border_color = horizontalBorderColor || '#0056b3';
          updatedLink.horizontal_hover_color = horizontalHoverColor || '#3a3a3a';

          return updatedLink;
        }
        return link;
      });

      // Update the entire list on the server
      const updateResponse = await fetch('/api/links', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLinks),
      });

      if (!updateResponse.ok) {
        throw new Error('Failed to update links on the server.');
      }

      return true;
    } catch (error) {
      console.error('Error updating group name:', error);
      return false;
    }
  }

  if (addLinkForm) {
    addLinkForm.addEventListener('submit', async function (event) {
      event.preventDefault();

      const groupName = document.getElementById('link-group').value || 'Ungrouped';

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
        font_size: document.getElementById('link-font-size').value || undefined,
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
          await fetchAndDisplayLinks(); // Refresh links

          // Re-open the top group if it was open
          const groupElement = document.querySelector(`.group_type_top[data-group-name="${groupName}"]`);
          if (groupElement) {
            const content = groupElement.querySelector('.group_type_top-content');
            const toggleBtn = groupElement.querySelector('.group_type_top-toggle-btn');
            if (content && toggleBtn) {
              content.classList.add('expanded');
              toggleBtn.textContent = '▲';
              groupElement.classList.add('expanded');
              moveToExpandedRow(groupElement);
            }
          }

          // Re-open the box popup if it was open
          const groupDiv = document.querySelector(`.link-group[data-group-name="${groupName}"]`);
          if (groupDiv && groupDiv.classList.contains('group_type_box')) {
            groupDiv.click();
          }
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
    document.getElementById('edit-link-width').value = link.width || '';
    document.getElementById('edit-link-height').value = link.height || '';
    document.getElementById('edit-link-text').value = link.text || '';
    document.getElementById('edit-link-default-type').value = link.default_type || 'nerd-font';
    document.getElementById('edit-link-background-color').value = link.background_color || '';
    document.getElementById('edit-link-border-radius').value = link.border_radius || '';
    document.getElementById('edit-link-title').value = link.title || '';
    document.getElementById('edit-link-font-size').value = link.font_size || '';
    document.getElementById('edit-link-li-bg-color').value = link.li_bg_color || '';
    document.getElementById('edit-link-li-hover-color').value = link.li_hover_color || '';
    document.getElementById('edit-link-hidden').checked = link.hidden || false;
    editLinkPopup.classList.remove('hidden');
    applyPopupStyling(link.group || 'Ungrouped');
  }

  if (editLinkForm) {
    if (!editLinkForm.hasAttribute('data-listener-attached')) {
      editLinkForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const linkId = editLinkIndexInput.value;
        const originalLink = links[linkId];
        const groupName = originalLink.group || 'Ungrouped';

        const updatedLink = {
          name: document.getElementById('edit-link-name').value,
          group: document.getElementById('edit-link-group').value || undefined,
          url: document.getElementById('edit-link-url').value,
          icon_class: document.getElementById('edit-link-icon-class').value || undefined,
          color: document.getElementById('edit-link-color').value || undefined,
          img_src: document.getElementById('edit-link-img-src').value || undefined,
          width: document.getElementById('edit-link-width').value || undefined,
          height: document.getElementById('edit-link-height').value || undefined,
          text: document.getElementById('edit-link-text').value || undefined,
          default_type: document.getElementById('edit-link-default-type').value || undefined,
          background_color: document.getElementById('edit-link-background-color').value || undefined,
          border_radius: document.getElementById('edit-link-border-radius').value || undefined,
          title: document.getElementById('edit-link-title').value || undefined,
          font_size: document.getElementById('edit-link-font-size').value || undefined,
          li_bg_color: document.getElementById('edit-link-li-bg-color').value || undefined,
          li_hover_color: document.getElementById('edit-link-li-hover-color').value || undefined,
          hidden: document.getElementById('edit-link-hidden').checked || undefined,
        };

        // Preserve group-level properties if not explicitly changed in link edit
        if (originalLink) {
          updatedLink.collapsible = originalLink.collapsible;
          updatedLink.display_style = originalLink.display_style;
          updatedLink.horizontal_stack = originalLink.horizontal_stack;
          updatedLink.password_protect = originalLink.password_protect;
          updatedLink.top_name = originalLink.top_name;
          updatedLink.top_bg_color = originalLink.top_bg_color;
          updatedLink.top_text_color = originalLink.top_text_color;
          updatedLink.top_border_color = originalLink.top_border_color;
          updatedLink.top_hover_color = originalLink.top_hover_color;
          updatedLink.popup_bg_color = originalLink.popup_bg_color;
          updatedLink.popup_text_color = originalLink.popup_text_color;
          updatedLink.popup_border_color = originalLink.popup_border_color;
          updatedLink.popup_border_radius = originalLink.popup_border_radius;
          updatedLink.horizontal_bg_color = originalLink.horizontal_bg_color;
          updatedLink.horizontal_text_color = originalLink.horizontal_text_color;
          updatedLink.horizontal_border_color = originalLink.horizontal_border_color;
          updatedLink.horizontal_hover_color = originalLink.horizontal_hover_color;
        }

        try {
          const response = await fetch(`/api/links/${linkId}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedLink),
          });

          if (response.ok) {
            editLinkPopup.classList.add('hidden');
            await fetchAndDisplayLinks();

            // Re-open the top group if it was open
            if (originalLink.collapsible) {
              const groupElement = document.querySelector(`.group_type_top[data-group-name="${groupName}"]`);
              if (groupElement) {
                const content = groupElement.querySelector('.group_type_top-content');
                const toggleBtn = groupElement.querySelector('.group_type_top-toggle-btn');
                if (content && toggleBtn) {
                  content.classList.add('expanded');
                  toggleBtn.textContent = '▲';
                  groupElement.classList.add('expanded');
                  moveToExpandedRow(groupElement);
                }
              }
            } else if (originalLink.horizontal_stack) {
              const groupDiv = document.querySelector(`.link-group[data-group-name="${groupName}"]`);
              if (groupDiv) {
                groupDiv.click();
              }
            }

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
      editGroupForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const originalGroupName = document.getElementById('edit-group-original-name').value;
        const newGroupName = document.getElementById('edit-group-name').value;
        const newDisplayStyle = document.getElementById('edit-group-display').value;
        const isCollapsible = document.getElementById('edit-group-collapsible').checked;
        const isHorizontalStack = document.getElementById('edit-group-horizontal-stack').checked;
        const isPasswordProtected = document.getElementById('edit-group-password-protect').checked;
        const topName = document.getElementById('edit-group-top-name').value;
        const topBgColor = document.getElementById('edit-group-top-bg-color').value;
        const topTextColor = document.getElementById('edit-group-top-text-color').value;
        const topBorderColor = document.getElementById('edit-group-top-border-color').value;
        const topHoverColor = document.getElementById('edit-group-top-hover-color').value;
        const popupBgColor = document.getElementById('edit-group-popup-bg-color').value;
        const popupTextColor = document.getElementById('edit-group-popup-text-color').value;
        const popupBorderColor = document.getElementById('edit-group-popup-border-color').value;
        const popupBorderRadius = document.getElementById('edit-group-popup-border-radius').value;
        const horizontalBgColor = document.getElementById('edit-group-horizontal-bg-color').value;
        const horizontalTextColor = document.getElementById('edit-group-horizontal-text-color').value;
        const horizontalBorderColor = document.getElementById('edit-group-horizontal-border-color').value;
        const horizontalHoverColor = document.getElementById('edit-group-horizontal-hover-color').value;

        try {
          const success = await updateGroupName(originalGroupName, newGroupName, newDisplayStyle, isCollapsible, isHorizontalStack, isPasswordProtected, topName, topBgColor, topTextColor, topBorderColor, topHoverColor, popupBgColor, popupTextColor, popupBorderColor, popupBorderRadius, horizontalBgColor, horizontalTextColor, horizontalBorderColor, horizontalHoverColor);
          if (success) {
            document.getElementById('edit-group-popup').classList.add('hidden');
            fetchAndDisplayLinks();
          } else {
            alert('Failed to update group settings.');
          }
        } catch (error) {
          console.error('Error updating group settings:', error);
          alert('Error updating group settings.');
        }
      });
      editGroupForm.setAttribute('data-listener-attached', 'true');
    }
  }

  // Copy Link functionality
  async function copyLink(linkToCopy, index) {
    const newLink = { ...linkToCopy };
    newLink.name = `${newLink.name} (copy)`;

    try {
        const response = await fetch('/api/links');
        const links = await response.json();

        links.splice(index + 1, 0, newLink);

        // Update the entire list on the server
        const updateResponse = await fetch('/api/links', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(links),
        });

        if (!updateResponse.ok) {
            throw new Error('Failed to update links on the server.');
        }

        fetchAndDisplayLinks();

    } catch (error) {
        console.error('Error copying link:', error);
        alert('Error copying link.');
    }
  }

  // Delete Link functionality
  async function deleteLink(linkId) {
    if (confirm('Are you sure you want to delete this link?')) {
      try {
        const linkToDelete = links[linkId];
        const groupName = linkToDelete.group || 'Ungrouped';

        const response = await fetch(`/api/links/${linkId}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          await fetchAndDisplayLinks();

          // Re-open the top group if it was open
          const groupElement = document.querySelector(`.group_type_top[data-group-name="${groupName}"]`);
          if (groupElement) {
            const content = groupElement.querySelector('.group_type_top-content');
            const toggleBtn = groupElement.querySelector('.group_type_top-toggle-btn');
            if (content && toggleBtn) {
              content.classList.add('expanded');
              toggleBtn.textContent = '▲';
              groupElement.classList.add('expanded');
              moveToExpandedRow(groupElement);
            }
          }

          const groupDiv = document.querySelector(`.link-group[data-group-name="${groupName}"]`);
          if (groupDiv && groupDiv.classList.contains('group_type_box')) {
            groupDiv.click();
          }
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
    editModeToggle.addEventListener('change', async function () {
      const expandedGroups = [];
      // Capture currently expanded groups before re-rendering
      document.querySelectorAll('.group_type_top.expanded').forEach(group => {
        expandedGroups.push(group.dataset.groupName);
      });

      if (this.checked) {
        flexContainer2.classList.add('edit-mode');
      } else {
        flexContainer2.classList.remove('edit-mode');
      }

      // Refresh the display when edit mode is toggled to show/hide items
      await fetchAndDisplayLinks();

      // Re-expand previously expanded groups
      expandedGroups.forEach(groupName => {
        const groupElement = document.querySelector(`.group_type_top[data-group-name="${groupName}"]`);
        if (groupElement) {
          const content = groupElement.querySelector('.group_type_top-content');
          const toggleBtn = groupElement.querySelector('.group_type_top-toggle-btn');
          if (content && toggleBtn) {
            content.classList.add('expanded');
            toggleBtn.textContent = '▲';
            groupElement.classList.add('expanded');
            // Move to expanded row if it's a top group
            moveToExpandedRow(groupElement);
          }
        }
      });
    });
  }

  // Drag and Drop functionality for links
  let draggedElement = null;
  let draggedIndex = null;

  function handleDragStart(e) {
    if (e.target.classList.contains('add-link-item') || e.target.classList.contains('extend-icon')) {
      e.preventDefault();
      return;
    }
    draggedElement = this;
    draggedIndex = parseInt(this.dataset.linkIndex);
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
    e.stopPropagation(); // Prevent bubbling to group header

    // Disable group toggle during drag
    document.body.classList.add('dragging-active');
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
      const targetIndex = parseInt(this.dataset.linkIndex);
      await reorderLink(draggedIndex, targetIndex);
    }
    return false;
  }

  function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedElement = null;
    draggedIndex = null;

    // Re-enable group toggle after drag
    document.body.classList.remove('dragging-active');
  }

  // Move link up or down within the same group
  async function moveLink(linkIndex, direction) {
    try {
      const response = await fetch('/api/links');
      const links = await response.json();

      const currentLink = links[linkIndex];
      const currentGroup = currentLink.group || 'Ungrouped';

      // Find all links in the same group
      const groupLinks = links.map((link, index) => ({ link, index }))
        .filter(item => (item.link.group || 'Ungrouped') === currentGroup);

      // Find current position within the group
      const currentGroupIndex = groupLinks.findIndex(item => item.index === linkIndex);
      const targetGroupIndex = currentGroupIndex + direction;

      // Check bounds
      if (targetGroupIndex < 0 || targetGroupIndex >= groupLinks.length) {
        return;
      }

      // Swap with target
      const targetLinkIndex = groupLinks[targetGroupIndex].index;
      reorderLink(linkIndex, targetLinkIndex);

    } catch (error) {
      console.error('Error moving link:', error);
    }
  }

  // Move entire group up or down
  async function moveGroup(draggedGroupName, targetGroupName) {
    try {
      const response = await fetch('/api/links');
      const links = await response.json();

      // Get all unique group names in their current order
      const groupNames = [...new Set(links.map(link => link.group || 'Ungrouped'))];
      
      const draggedIndex = groupNames.indexOf(draggedGroupName);
      const targetIndex = groupNames.indexOf(targetGroupName);

      // Remove the dragged group name and insert it at the target position
      groupNames.splice(draggedIndex, 1);
      groupNames.splice(targetIndex, 0, draggedGroupName);

      // Rebuild the links array based on the new group order
      const newLinks = [];
      const linksByGroup = links.reduce((acc, link) => {
        const group = link.group || 'Ungrouped';
        if (!acc[group]) {
          acc[group] = [];
        }
        acc[group].push(link);
        return acc;
      }, {});

      groupNames.forEach(group => {
        newLinks.push(...(linksByGroup[group] || []));
      });

      // Update the entire list of links on the server
      await fetch('/api/links', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLinks),
      });

      fetchAndDisplayLinks();

    } catch (error) {
      console.error('Error moving group:', error);
    }
  }

  // Reorder a link by moving it from oldIndex to newIndex
  async function reorderLink(oldIndex, newIndex) {
    try {
      // Ensure we have the latest links data
      const response = await fetch('/api/links');
      let currentLinks = await response.json();

      const movedLink = currentLinks[oldIndex];
      const groupName = movedLink.group || 'Ungrouped';

      // Preserve group-level properties
      const groupProperties = {
        collapsible: movedLink.collapsible,
        display_style: movedLink.display_style,
        horizontal_stack: movedLink.horizontal_stack,
        password_protect: movedLink.password_protect,
        top_name: movedLink.top_name,
        top_bg_color: movedLink.top_bg_color,
        top_text_color: movedLink.top_text_color,
        top_border_color: movedLink.top_border_color,
        top_hover_color: movedLink.top_hover_color,
      };

      // Remove the dragged link from its original position
      const [draggedLink] = currentLinks.splice(oldIndex, 1);

      // Insert the dragged link at the new position
      currentLinks.splice(newIndex, 0, draggedLink);

      // Update all links in the same group with the preserved properties
      currentLinks.forEach(link => {
        if ((link.group || 'Ungrouped') === groupName) {
          Object.assign(link, groupProperties);
        }
      });

      // Update the entire list of links on the server
      await fetch('/api/links', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(currentLinks),
      });

      await fetchAndDisplayLinks(); // Re-render the UI

      // Re-open the collapsible group if it was open
      const groupElement = document.querySelector(`.collapsible-group[data-group-name="${groupName}"]`);
      if (groupElement) {
        const content = groupElement.querySelector('.collapsible-group-content');
        const toggleBtn = groupElement.querySelector('.collapsible-toggle-btn');
        if (content && toggleBtn) {
          content.classList.add('expanded');
          toggleBtn.textContent = '▲';
          groupElement.classList.add('expanded');
          moveToExpandedRow(groupElement);
        }
      }

      // Re-open the popup if it was open
      const groupDiv = document.querySelector(`.link-group[data-group-name="${groupName}"]`);
      if (groupDiv && groupDiv.classList.contains('horizontal-stack')) {
        groupDiv.click();
      }

    } catch (error) {
      console.error('Error reordering link:', error);
    }
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