let links = [];
let draggedElement = null;

// Load links from Convex
async function loadLinks() {
  try {
    const data = await window.convexClient.query("functions:getLinks");
    links = data.sort((a, b) => (a._creationTime || 0) - (b._creationTime || 0));
    renderLinks();
  } catch (error) {
    console.error('Error loading links:', error);
  }
}

// Render links
function renderLinks() {
  const container = document.getElementById('links-container');
  container.innerHTML = '';
  
  const grouped = {};
  const collapsible = {};
  
  links.forEach((link, index) => {
    if (link.hidden && !window.editMode) return;
    
    const group = link.group || 'Ungrouped';
    if (!grouped[group]) grouped[group] = [];
    grouped[group].push({ link, index });
    
    if (link.collapsible) collapsible[group] = true;
  });
  
  // Render collapsible groups
  if (Object.keys(collapsible).length > 0) {
    const topContainer = document.createElement('div');
    topContainer.className = 'group_type_top-container';
    
    Object.keys(collapsible).forEach(groupName => {
      const groupDiv = createCollapsibleGroup(groupName, grouped[groupName]);
      topContainer.appendChild(groupDiv);
    });
    
    container.appendChild(topContainer);
  }
  
  // Render regular groups
  Object.keys(grouped).forEach(groupName => {
    if (collapsible[groupName]) return;
    
    const groupDiv = createRegularGroup(groupName, grouped[groupName]);
    container.appendChild(groupDiv);
  });
  
  // Add link button
  const addBtn = document.createElement('button');
  addBtn.className = 'add-button';
  addBtn.textContent = '+ Add Link';
  addBtn.onclick = () => showAddLinkPopup();
  container.appendChild(addBtn);
}

// Create collapsible group
function createCollapsibleGroup(groupName, items) {
  const div = document.createElement('div');
  div.className = 'group_type_top';
  div.dataset.groupName = groupName;
  
  const firstLink = items[0].link;
  const displayName = firstLink.top_name || groupName;
  
  const header = document.createElement('div');
  header.className = 'group_type_top-header';
  
  const title = document.createElement('h4');
  title.className = 'group_type_top-title';
  renderDisplayName(title, displayName);
  
  const toggleBtn = document.createElement('button');
  toggleBtn.className = 'group_type_top-toggle-btn';
  toggleBtn.textContent = '▼';
  
  header.appendChild(title);
  
  if (window.editMode) {
    const editBtn = document.createElement('button');
    editBtn.className = 'edit-btn';
    editBtn.textContent = '⚙';
    editBtn.onclick = (e) => {
      e.stopPropagation();
      openEditGroupPopup(groupName);
    };
    header.appendChild(editBtn);
  }
  
  header.appendChild(toggleBtn);
  
  const content = document.createElement('ul');
  content.className = 'group_type_top-content';
  
  items.forEach(({ link, index }) => {
    const item = createLinkItem(link, index);
    content.appendChild(item);
  });
  
  div.appendChild(header);
  div.appendChild(content);
  
  // Apply styling
  if (firstLink.top_bg_color) div.style.backgroundColor = firstLink.top_bg_color;
  if (firstLink.top_text_color) title.style.color = firstLink.top_text_color;
  if (firstLink.top_border_color) div.style.borderColor = firstLink.top_border_color;
  
  div.onclick = (e) => {
    if (e.target === toggleBtn || e.target === header) {
      if (firstLink.password_protect) {
        const pwd = prompt('Enter password:');
        if (pwd !== '1823') {
          alert('Incorrect password!');
          return;
        }
      }
      div.classList.toggle('expanded');
    }
  };
  
  // Context menu
  div.addEventListener('contextmenu', (e) => {
    showContextMenu(e, [
      { label: 'Edit', action: () => openEditGroupPopup(groupName) },
      { label: 'Delete', action: () => deleteGroup(groupName) }
    ]);
  });
  
  return div;
}

// Create regular group
function createRegularGroup(groupName, items) {
  const div = document.createElement('div');
  div.className = 'link-group';
  div.dataset.groupName = groupName;
  
  const firstLink = items[0].link;
  const isHorizontal = firstLink.horizontal_stack;
  
  const title = document.createElement('h3');
  title.textContent = groupName;
  div.appendChild(title);
  
  if (window.editMode) {
    const editBtn = document.createElement('button');
    editBtn.className = 'edit-btn';
    editBtn.textContent = 'Edit Group';
    editBtn.onclick = () => openEditGroupPopup(groupName);
    div.appendChild(editBtn);
  }
  
  const ul = document.createElement('ul');
  if (isHorizontal) ul.className = 'horizontal-stack-group';
  
  const displayStyle = firstLink.display_style || 'flex';
  if (displayStyle === 'list-item') div.classList.add('list-style');
  
  items.forEach(({ link, index }) => {
    const item = createLinkItem(link, index);
    ul.appendChild(item);
  });
  
  div.appendChild(ul);
  
  // Context menu
  div.addEventListener('contextmenu', (e) => {
    if (e.target === div || e.target === title) {
      showContextMenu(e, [
        { label: 'Edit', action: () => openEditGroupPopup(groupName) },
        { label: 'Delete', action: () => deleteGroup(groupName) }
      ]);
    }
  });
  
  return div;
}

// Create link item
function createLinkItem(link, index) {
  const li = document.createElement('li');
  li.className = 'link-item';
  li.dataset.linkIndex = index;
  li.draggable = true;
  
  if (link.hidden) li.classList.add('hidden-item');
  
  const a = document.createElement('a');
  a.href = link.url;
  a.target = '_blank';
  a.title = link.title || link.name || '';
  
  // Render content based on type
  if (link.default_type === 'nerd-font' && link.icon_class) {
    const icon = document.createElement('i');
    icon.className = link.icon_class;
    a.appendChild(icon);
  } else if (link.default_type === 'img' && link.img_src) {
    const img = document.createElement('img');
    img.src = link.img_src;
    img.width = link.width || 50;
    img.height = link.height || 50;
    a.appendChild(img);
  } else if (link.default_type === 'svg' && link.svg_code) {
    const temp = document.createElement('div');
    temp.innerHTML = link.svg_code;
    const svg = temp.querySelector('svg');
    if (svg) {
      if (!svg.style.width && link.width) svg.style.width = link.width;
      if (!svg.style.height && link.height) svg.style.height = link.height;
      if (!svg.style.width) svg.style.width = '50px';
      if (!svg.style.height) svg.style.height = '50px';
      svg.style.fill = link.color || 'currentColor';
      a.appendChild(svg);
    } else {
      a.innerHTML = link.svg_code;
    }
  } else {
    a.textContent = link.text || link.name || 'Link';
  }
  
  // Apply styling
  if (link.color) a.style.color = link.color;
  if (link.background_color) a.style.backgroundColor = link.background_color;
  if (link.font_family) a.style.fontFamily = link.font_family;
  if (link.font_size) a.style.fontSize = link.font_size;
  if (link.width) a.style.width = link.width;
  if (link.height) a.style.height = link.height;
  if (link.border_radius) a.style.borderRadius = link.border_radius;
  
  if (link.li_bg_color) li.style.backgroundColor = link.li_bg_color;
  if (link.li_border_color) li.style.borderColor = link.li_border_color;
  if (link.li_border_radius) li.style.borderRadius = link.li_border_radius;
  if (link.li_width) li.style.minWidth = link.li_width;
  if (link.li_height) li.style.minHeight = link.li_height;
  
  if (link.li_hover_color) {
    li.addEventListener('mouseenter', () => li.style.backgroundColor = link.li_hover_color);
    li.addEventListener('mouseleave', () => li.style.backgroundColor = link.li_bg_color || '');
  }
  
  // Handle multiple URLs
  a.onclick = (e) => {
    if (link.urls && link.urls.length > 1) {
      e.preventDefault();
      window.open(link.urls[0], '_blank');
    }
  };
  
  li.appendChild(a);
  
  // Edit buttons
  if (window.editMode) {
    const editBtn = document.createElement('button');
    editBtn.className = 'edit-btn';
    editBtn.textContent = '✏';
    editBtn.onclick = (e) => {
      e.preventDefault();
      openEditLinkPopup(link, index);
    };
    li.appendChild(editBtn);
    
    const delBtn = document.createElement('button');
    delBtn.className = 'delete-btn';
    delBtn.textContent = '🗑';
    delBtn.onclick = (e) => {
      e.preventDefault();
      deleteLink(link._id);
    };
    li.appendChild(delBtn);
  }
  
  // Context menu
  li.addEventListener('contextmenu', (e) => {
    showContextMenu(e, [
      { label: 'New-Tab', action: () => window.open(link.url, '_blank') },
      { label: 'Edit', action: () => openEditLinkPopup(link, index) },
      { label: 'Copy', action: () => copyLink(link) },
      { label: 'Delete', action: () => deleteLink(link._id) }
    ]);
  });
  
  // Drag and drop
  li.addEventListener('dragstart', (e) => {
    draggedElement = li;
    li.classList.add('dragging');
  });
  
  li.addEventListener('dragover', (e) => {
    e.preventDefault();
  });
  
  li.addEventListener('drop', async (e) => {
    e.preventDefault();
    if (draggedElement && draggedElement !== li) {
      const fromIndex = parseInt(draggedElement.dataset.linkIndex);
      const toIndex = parseInt(li.dataset.linkIndex);
      await reorderLinks(fromIndex, toIndex);
    }
  });
  
  li.addEventListener('dragend', () => {
    li.classList.remove('dragging');
    draggedElement = null;
  });
  
  return li;
}

// Render display name (text, icon, or SVG)
function renderDisplayName(element, name) {
  element.innerHTML = '';
  
  if (name.startsWith('nf nf-')) {
    const icon = document.createElement('i');
    icon.className = name;
    element.appendChild(icon);
  } else if (name.startsWith('<svg')) {
    const temp = document.createElement('div');
    temp.innerHTML = name;
    const svg = temp.querySelector('svg');
    if (svg) {
      if (!svg.style.width) svg.style.width = '1em';
      if (!svg.style.height) svg.style.height = '1em';
      svg.style.display = 'inline-block';
      svg.style.verticalAlign = 'middle';
      svg.style.fill = 'currentColor';
      element.appendChild(svg);
    } else {
      element.textContent = name;
    }
  } else {
    element.textContent = name;
  }
}

// Add link popup
function showAddLinkPopup() {
  document.getElementById('add-link-popup').classList.remove('hidden');
  document.getElementById('add-link-form').reset();
}

document.getElementById('add-link-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const urls = getAllUrls(false);
  const typeRadios = document.querySelectorAll('input[name="link-type"]');
  let defaultType = 'text';
  typeRadios.forEach(r => { if (r.checked) defaultType = r.value; });
  
  const newLink = {
    name: document.getElementById('link-name').value,
    group: document.getElementById('link-group').value,
    urls,
    url: urls[0],
    default_type: defaultType,
    text: document.getElementById('link-text').value,
    icon_class: document.getElementById('link-icon-class').value,
    img_src: document.getElementById('link-img-src').value,
    svg_code: document.getElementById('link-svg-code').value,
    width: document.getElementById('link-width').value,
    height: document.getElementById('link-height').value,
    color: document.getElementById('link-color').value,
    background_color: document.getElementById('link-background-color').value,
    font_family: document.getElementById('link-font-family').value,
    font_size: document.getElementById('link-font-size').value,
    li_width: document.getElementById('link-li-width').value,
    li_height: document.getElementById('link-li-height').value,
    li_bg_color: document.getElementById('link-li-bg-color').value,
    li_hover_color: document.getElementById('link-li-hover-color').value,
    li_border_color: document.getElementById('link-li-border-color').value,
    li_border_radius: document.getElementById('link-li-border-radius').value,
    border_radius: document.getElementById('link-border-radius').value,
    title: document.getElementById('link-title').value,
    hidden: document.getElementById('link-hidden').checked
  };
  
  try {
    await window.convexClient.mutation("functions:addLink", newLink);
    document.getElementById('add-link-popup').classList.add('hidden');
    await loadLinks();
    window.showNotification('Link added!');
  } catch (error) {
    console.error('Error adding link:', error);
    alert('Error adding link');
  }
});

// Edit link popup
function openEditLinkPopup(link, index) {
  document.getElementById('edit-link-id').value = link._id;
  document.getElementById('edit-link-name').value = link.name || '';
  document.getElementById('edit-link-group').value = link.group || '';
  
  // Populate URL fields
  populateUrlFields(link.urls || [link.url], true);
  
  document.getElementById('edit-link-text').value = link.text || '';
  document.getElementById('edit-link-icon-class').value = link.icon_class || '';
  document.getElementById('edit-link-img-src').value = link.img_src || '';
  document.getElementById('edit-link-svg-code').value = link.svg_code || '';
  document.getElementById('edit-link-width').value = link.width || '';
  document.getElementById('edit-link-height').value = link.height || '';
  document.getElementById('edit-link-color').value = link.color || '';
  document.getElementById('edit-link-background-color').value = link.background_color || '';
  document.getElementById('edit-link-font-family').value = link.font_family || '';
  document.getElementById('edit-link-font-size').value = link.font_size || '';
  document.getElementById('edit-link-li-width').value = link.li_width || '';
  document.getElementById('edit-link-li-height').value = link.li_height || '';
  document.getElementById('edit-link-li-bg-color').value = link.li_bg_color || '';
  document.getElementById('edit-link-li-hover-color').value = link.li_hover_color || '';
  document.getElementById('edit-link-li-border-color').value = link.li_border_color || '';
  document.getElementById('edit-link-li-border-radius').value = link.li_border_radius || '';
  document.getElementById('edit-link-border-radius').value = link.border_radius || '';
  document.getElementById('edit-link-title').value = link.title || '';
  document.getElementById('edit-link-hidden').checked = link.hidden || false;
  
  const typeRadios = document.querySelectorAll('input[name="edit-link-type"]');
  typeRadios.forEach(r => r.checked = r.value === link.default_type);
  
  const svgTextarea = document.getElementById('edit-link-svg-code');
  svgTextarea.style.display = link.default_type === 'svg' ? 'block' : 'none';
  
  document.getElementById('edit-link-popup').classList.remove('hidden');
}

document.getElementById('edit-link-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const id = document.getElementById('edit-link-id').value;
  const urls = getAllUrls(true);
  const typeRadios = document.querySelectorAll('input[name="edit-link-type"]');
  let defaultType = 'text';
  typeRadios.forEach(r => { if (r.checked) defaultType = r.value; });
  
  const updatedLink = {
    id,
    name: document.getElementById('edit-link-name').value,
    group: document.getElementById('edit-link-group').value,
    urls,
    url: urls[0],
    default_type: defaultType,
    text: document.getElementById('edit-link-text').value,
    icon_class: document.getElementById('edit-link-icon-class').value,
    img_src: document.getElementById('edit-link-img-src').value,
    svg_code: document.getElementById('edit-link-svg-code').value,
    width: document.getElementById('edit-link-width').value,
    height: document.getElementById('edit-link-height').value,
    color: document.getElementById('edit-link-color').value,
    background_color: document.getElementById('edit-link-background-color').value,
    font_family: document.getElementById('edit-link-font-family').value,
    font_size: document.getElementById('edit-link-font-size').value,
    li_width: document.getElementById('edit-link-li-width').value,
    li_height: document.getElementById('edit-link-li-height').value,
    li_bg_color: document.getElementById('edit-link-li-bg-color').value,
    li_hover_color: document.getElementById('edit-link-li-hover-color').value,
    li_border_color: document.getElementById('edit-link-li-border-color').value,
    li_border_radius: document.getElementById('edit-link-li-border-radius').value,
    border_radius: document.getElementById('edit-link-border-radius').value,
    title: document.getElementById('edit-link-title').value,
    hidden: document.getElementById('edit-link-hidden').checked
  };
  
  try {
    await window.convexClient.mutation("functions:updateLink", updatedLink);
    document.getElementById('edit-link-popup').classList.add('hidden');
    await loadLinks();
    window.showNotification('Link updated!');
  } catch (error) {
    console.error('Error updating link:', error);
    alert('Error updating link');
  }
});

// Delete link
async function deleteLink(id) {
  if (!confirm('Delete this link?')) return;
  
  try {
    await window.convexClient.mutation("functions:deleteLink", { id });
    await loadLinks();
    window.showNotification('Link deleted!');
  } catch (error) {
    console.error('Error deleting link:', error);
    alert('Error deleting link');
  }
}

// Copy link
async function copyLink(link) {
  const { _id, _creationTime, ...newLink } = link;
  newLink.name = (newLink.name || '') + ' (Copy)';
  
  try {
    await window.convexClient.mutation("functions:addLink", newLink);
    await loadLinks();
    window.showNotification('Link copied!');
  } catch (error) {
    console.error('Error copying link:', error);
    alert('Error copying link');
  }
}

// Reorder links
async function reorderLinks(fromIndex, toIndex) {
  const newLinks = [...links];
  const [moved] = newLinks.splice(fromIndex, 1);
  newLinks.splice(toIndex, 0, moved);
  
  try {
    await window.convexClient.mutation("functions:updateAllLinks", { links: newLinks });
    await loadLinks();
  } catch (error) {
    console.error('Error reordering:', error);
  }
}

// Edit group popup
function openEditGroupPopup(groupName) {
  const groupLinks = links.filter(l => (l.group || 'Ungrouped') === groupName);
  const firstLink = groupLinks[0] || {};
  
  document.getElementById('edit-group-original-name').value = groupName;
  document.getElementById('edit-group-name').value = groupName;
  document.getElementById('edit-group-top-name').value = firstLink.top_name || '';
  document.getElementById('edit-group-collapsible').checked = firstLink.collapsible || false;
  document.getElementById('edit-group-horizontal-stack').checked = firstLink.horizontal_stack || false;
  document.getElementById('edit-group-password-protect').checked = firstLink.password_protect || false;
  
  const displayRadios = document.querySelectorAll('input[name="edit-group-display"]');
  displayRadios.forEach(r => r.checked = r.value === (firstLink.display_style || 'flex'));
  
  document.getElementById('edit-group-top-bg-color').value = firstLink.top_bg_color || '';
  document.getElementById('edit-group-top-text-color').value = firstLink.top_text_color || '';
  document.getElementById('edit-group-top-border-color').value = firstLink.top_border_color || '';
  document.getElementById('edit-group-top-hover-color').value = firstLink.top_hover_color || '';
  document.getElementById('edit-group-top-width').value = firstLink.top_width || '';
  document.getElementById('edit-group-top-height').value = firstLink.top_height || '';
  document.getElementById('edit-group-top-font-family').value = firstLink.top_font_family || '';
  document.getElementById('edit-group-top-font-size').value = firstLink.top_font_size || '';
  document.getElementById('edit-group-popup-bg-color').value = firstLink.popup_bg_color || '';
  document.getElementById('edit-group-popup-text-color').value = firstLink.popup_text_color || '';
  document.getElementById('edit-group-popup-border-color').value = firstLink.popup_border_color || '';
  document.getElementById('edit-group-popup-border-radius').value = firstLink.popup_border_radius || '';
  document.getElementById('edit-group-horizontal-bg-color').value = firstLink.horizontal_bg_color || '';
  document.getElementById('edit-group-horizontal-text-color').value = firstLink.horizontal_text_color || '';
  document.getElementById('edit-group-horizontal-border-color').value = firstLink.horizontal_border_color || '';
  document.getElementById('edit-group-horizontal-hover-color').value = firstLink.horizontal_hover_color || '';
  
  document.getElementById('edit-group-popup').classList.remove('hidden');
  
  // Show/hide sections
  const collapsible = document.getElementById('edit-group-collapsible').checked;
  const horizontal = document.getElementById('edit-group-horizontal-stack').checked;
  document.getElementById('collapsible-settings').style.display = collapsible ? 'block' : 'none';
  document.getElementById('horizontal-settings').style.display = horizontal ? 'block' : 'none';
}

document.getElementById('edit-group-collapsible').addEventListener('change', (e) => {
  document.getElementById('collapsible-settings').style.display = e.target.checked ? 'block' : 'none';
});

document.getElementById('edit-group-horizontal-stack').addEventListener('change', (e) => {
  document.getElementById('horizontal-settings').style.display = e.target.checked ? 'block' : 'none';
});

document.getElementById('edit-group-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const originalName = document.getElementById('edit-group-original-name').value;
  const newName = document.getElementById('edit-group-name').value;
  
  const displayRadios = document.querySelectorAll('input[name="edit-group-display"]');
  let displayStyle = 'flex';
  displayRadios.forEach(r => { if (r.checked) displayStyle = r.value; });
  
  const groupSettings = {
    collapsible: document.getElementById('edit-group-collapsible').checked,
    display_style: displayStyle,
    horizontal_stack: document.getElementById('edit-group-horizontal-stack').checked,
    password_protect: document.getElementById('edit-group-password-protect').checked,
    top_name: document.getElementById('edit-group-top-name').value,
    top_bg_color: document.getElementById('edit-group-top-bg-color').value,
    top_text_color: document.getElementById('edit-group-top-text-color').value,
    top_border_color: document.getElementById('edit-group-top-border-color').value,
    top_hover_color: document.getElementById('edit-group-top-hover-color').value,
    top_width: document.getElementById('edit-group-top-width').value,
    top_height: document.getElementById('edit-group-top-height').value,
    top_font_family: document.getElementById('edit-group-top-font-family').value,
    top_font_size: document.getElementById('edit-group-top-font-size').value,
    popup_bg_color: document.getElementById('edit-group-popup-bg-color').value,
    popup_text_color: document.getElementById('edit-group-popup-text-color').value,
    popup_border_color: document.getElementById('edit-group-popup-border-color').value,
    popup_border_radius: document.getElementById('edit-group-popup-border-radius').value,
    horizontal_bg_color: document.getElementById('edit-group-horizontal-bg-color').value,
    horizontal_text_color: document.getElementById('edit-group-horizontal-text-color').value,
    horizontal_border_color: document.getElementById('edit-group-horizontal-border-color').value,
    horizontal_hover_color: document.getElementById('edit-group-horizontal-hover-color').value
  };
  
  try {
    const updatedLinks = links.map(link => {
      if ((link.group || 'Ungrouped') === originalName) {
        return { ...link, group: newName, ...groupSettings };
      }
      return link;
    });
    
    await window.convexClient.mutation("functions:updateAllLinks", { links: updatedLinks });
    document.getElementById('edit-group-popup').classList.add('hidden');
    await loadLinks();
    window.showNotification('Group updated!');
  } catch (error) {
    console.error('Error updating group:', error);
    alert('Error updating group');
  }
});

// Delete group
async function deleteGroup(groupName) {
  if (!confirm(`Delete group "${groupName}" and all its links?`)) return;
  
  try {
    const remaining = links.filter(l => (l.group || 'Ungrouped') !== groupName);
    await window.convexClient.mutation("functions:updateAllLinks", { links: remaining });
    await loadLinks();
    window.showNotification('Group deleted!');
  } catch (error) {
    console.error('Error deleting group:', error);
    alert('Error deleting group');
  }
}

// SVG textarea toggle
document.querySelectorAll('input[name="link-type"]').forEach(radio => {
  radio.addEventListener('change', () => {
    document.getElementById('link-svg-code').style.display = radio.value === 'svg' ? 'block' : 'none';
  });
});

document.querySelectorAll('input[name="edit-link-type"]').forEach(radio => {
  radio.addEventListener('change', () => {
    document.getElementById('edit-link-svg-code').style.display = radio.value === 'svg' ? 'block' : 'none';
  });
});

// URL field management
window.addUrlField = () => {
  const container = document.getElementById('urls-container');
  const group = document.createElement('div');
  group.className = 'url-input-group';
  
  const input = document.createElement('input');
  input.type = 'url';
  input.className = 'url-input';
  input.placeholder = 'URL';
  
  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'remove-btn';
  removeBtn.textContent = '−';
  removeBtn.onclick = () => group.remove();
  
  group.appendChild(input);
  group.appendChild(removeBtn);
  container.appendChild(group);
};

window.addEditUrlField = () => {
  const container = document.getElementById('edit-urls-container');
  const group = document.createElement('div');
  group.className = 'url-input-group';
  
  const input = document.createElement('input');
  input.type = 'url';
  input.className = 'url-input';
  input.placeholder = 'URL';
  
  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'remove-btn';
  removeBtn.textContent = '−';
  removeBtn.onclick = () => group.remove();
  
  group.appendChild(input);
  group.appendChild(removeBtn);
  container.appendChild(group);
};

function getAllUrls(isEdit = false) {
  const container = document.getElementById(isEdit ? 'edit-urls-container' : 'urls-container');
  const inputs = container.querySelectorAll('.url-input');
  return Array.from(inputs).map(input => input.value).filter(url => url.trim());
}

function populateUrlFields(urls, isEdit = false) {
  const container = document.getElementById(isEdit ? 'edit-urls-container' : 'urls-container');
  container.innerHTML = '';
  
  if (!urls || urls.length === 0) urls = [''];
  
  urls.forEach((url, index) => {
    const group = document.createElement('div');
    group.className = 'url-input-group';
    
    const input = document.createElement('input');
    input.type = 'url';
    input.className = 'url-input';
    input.placeholder = 'URL';
    input.value = url;
    if (index === 0) input.required = true;
    
    const addBtn = document.createElement('button');
    addBtn.type = 'button';
    addBtn.textContent = '+';
    addBtn.onclick = isEdit ? window.addEditUrlField : window.addUrlField;
    
    group.appendChild(input);
    
    if (index > 0) {
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'remove-btn';
      removeBtn.textContent = '−';
      removeBtn.onclick = () => group.remove();
      group.appendChild(removeBtn);
    } else {
      group.appendChild(addBtn);
    }
    
    container.appendChild(group);
  });
}

// Edit mode listener
document.addEventListener('editModeChanged', loadLinks);

window.loadLinks = loadLinks;
window.openEditLinkPopup = openEditLinkPopup;
window.openEditGroupPopup = openEditGroupPopup;
window.deleteLink = deleteLink;
window.deleteGroup = deleteGroup;
window.copyLink = copyLink;
