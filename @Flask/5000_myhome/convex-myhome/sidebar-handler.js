let sidebarButtons = [];

// Load sidebar buttons
async function loadSidebarButtons() {
  try {
    const data = await window.convexClient.query("functions:getSidebarButtons");
    sidebarButtons = data;
    renderSidebarButtons();
  } catch (error) {
    console.error('Error loading sidebar buttons:', error);
  }
}

// Render sidebar buttons
function renderSidebarButtons() {
  const container = document.getElementById('sidebar-buttons-container');
  container.innerHTML = '';
  
  sidebarButtons.forEach((button, index) => {
    const btn = createSidebarButton(button, index);
    container.appendChild(btn);
  });
  
  // Add button
  const addBtn = document.createElement('a');
  addBtn.href = '#';
  addBtn.className = 'add-button';
  addBtn.innerHTML = '<i class="nf nf-fa-plus"></i>';
  addBtn.title = 'Add Button';
  addBtn.onclick = (e) => {
    e.preventDefault();
    showAddSidebarButtonPopup();
  };
  container.appendChild(addBtn);
}

// Create sidebar button
function createSidebarButton(button, index) {
  const btn = document.createElement('a');
  btn.href = button.url;
  btn.target = '_blank';
  btn.className = 'add-button';
  btn.title = button.name;
  btn.style.color = button.text_color;
  btn.style.backgroundColor = button.bg_color;
  btn.style.borderColor = button.border_color;
  btn.style.borderRadius = button.border_radius;
  btn.style.fontSize = button.font_size;
  
  // Content based on display type
  if (button.display_type === 'image' && button.img_src) {
    const img = document.createElement('img');
    img.src = button.img_src;
    img.style.width = '25px';
    img.style.height = '25px';
    btn.appendChild(img);
  } else if (button.display_type === 'svg' && button.svg_code) {
    const temp = document.createElement('div');
    temp.innerHTML = button.svg_code;
    const svg = temp.querySelector('svg');
    if (svg) {
      svg.style.width = '25px';
      svg.style.height = '25px';
      svg.style.fill = button.text_color;
      btn.appendChild(svg);
    } else {
      btn.innerHTML = button.svg_code;
    }
  } else {
    const icon = document.createElement('i');
    icon.className = button.icon_class || 'nf nf-fa-question';
    btn.appendChild(icon);
  }
  
  // Hover effect
  btn.addEventListener('mouseenter', () => {
    btn.style.backgroundColor = button.hover_color;
  });
  btn.addEventListener('mouseleave', () => {
    btn.style.backgroundColor = button.bg_color;
  });
  
  // Edit mode buttons
  if (window.editMode) {
    const editBtn = document.createElement('button');
    editBtn.className = 'edit-btn';
    editBtn.textContent = '✏';
    editBtn.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      openEditSidebarButtonPopup(button, index);
    };
    btn.appendChild(editBtn);
    
    const delBtn = document.createElement('button');
    delBtn.className = 'delete-btn';
    delBtn.textContent = '🗑';
    delBtn.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      deleteSidebarButton(button._id);
    };
    btn.appendChild(delBtn);
  }
  
  return btn;
}

// Add sidebar button popup
function showAddSidebarButtonPopup() {
  document.getElementById('add-sidebar-button-popup').classList.remove('hidden');
  document.getElementById('add-sidebar-button-form').reset();
}

document.getElementById('sidebar-button-display-type').addEventListener('change', (e) => {
  const iconInput = document.getElementById('sidebar-button-icon');
  const imgInput = document.getElementById('sidebar-button-img-src');
  const svgInput = document.getElementById('sidebar-button-svg-code');
  
  iconInput.style.display = e.target.value === 'icon' ? 'block' : 'none';
  imgInput.style.display = e.target.value === 'image' ? 'block' : 'none';
  svgInput.style.display = e.target.value === 'svg' ? 'block' : 'none';
});

document.getElementById('add-sidebar-button-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const newButton = {
    id: `btn-${Date.now()}`,
    name: document.getElementById('sidebar-button-name').value,
    url: document.getElementById('sidebar-button-url').value,
    display_type: document.getElementById('sidebar-button-display-type').value,
    icon_class: document.getElementById('sidebar-button-icon').value,
    img_src: document.getElementById('sidebar-button-img-src').value,
    svg_code: document.getElementById('sidebar-button-svg-code').value,
    text_color: document.getElementById('sidebar-button-text-color').value || '#000',
    bg_color: document.getElementById('sidebar-button-bg-color').value || '#fff',
    hover_color: document.getElementById('sidebar-button-hover-color').value || '#e0e0e0',
    border_color: document.getElementById('sidebar-button-border-color').value || '#ccc',
    border_radius: document.getElementById('sidebar-button-border-radius').value || '4px',
    font_size: document.getElementById('sidebar-button-font-size').value || '16px',
    has_notification: false
  };
  
  try {
    await window.convexClient.mutation("functions:addSidebarButton", newButton);
    document.getElementById('add-sidebar-button-popup').classList.add('hidden');
    await loadSidebarButtons();
    window.showNotification('Button added!');
  } catch (error) {
    console.error('Error adding button:', error);
    alert('Error adding button');
  }
});

// Edit sidebar button popup
function openEditSidebarButtonPopup(button, index) {
  document.getElementById('edit-sidebar-button-id').value = button._id;
  document.getElementById('edit-sidebar-button-name').value = button.name;
  document.getElementById('edit-sidebar-button-url').value = button.url;
  document.getElementById('edit-sidebar-button-display-type').value = button.display_type;
  document.getElementById('edit-sidebar-button-icon').value = button.icon_class || '';
  document.getElementById('edit-sidebar-button-img-src').value = button.img_src || '';
  document.getElementById('edit-sidebar-button-svg-code').value = button.svg_code || '';
  document.getElementById('edit-sidebar-button-text-color').value = button.text_color;
  document.getElementById('edit-sidebar-button-bg-color').value = button.bg_color;
  document.getElementById('edit-sidebar-button-hover-color').value = button.hover_color;
  document.getElementById('edit-sidebar-button-border-color').value = button.border_color;
  document.getElementById('edit-sidebar-button-border-radius').value = button.border_radius;
  document.getElementById('edit-sidebar-button-font-size').value = button.font_size;
  
  const iconInput = document.getElementById('edit-sidebar-button-icon');
  const imgInput = document.getElementById('edit-sidebar-button-img-src');
  const svgInput = document.getElementById('edit-sidebar-button-svg-code');
  
  iconInput.style.display = button.display_type === 'icon' ? 'block' : 'none';
  imgInput.style.display = button.display_type === 'image' ? 'block' : 'none';
  svgInput.style.display = button.display_type === 'svg' ? 'block' : 'none';
  
  document.getElementById('edit-sidebar-button-popup').classList.remove('hidden');
}

document.getElementById('edit-sidebar-button-display-type').addEventListener('change', (e) => {
  const iconInput = document.getElementById('edit-sidebar-button-icon');
  const imgInput = document.getElementById('edit-sidebar-button-img-src');
  const svgInput = document.getElementById('edit-sidebar-button-svg-code');
  
  iconInput.style.display = e.target.value === 'icon' ? 'block' : 'none';
  imgInput.style.display = e.target.value === 'image' ? 'block' : 'none';
  svgInput.style.display = e.target.value === 'svg' ? 'block' : 'none';
});

document.getElementById('edit-sidebar-button-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const dbId = document.getElementById('edit-sidebar-button-id').value;
  const button = sidebarButtons.find(b => b._id === dbId);
  
  const updatedButton = {
    dbId,
    id: button.id,
    name: document.getElementById('edit-sidebar-button-name').value,
    url: document.getElementById('edit-sidebar-button-url').value,
    display_type: document.getElementById('edit-sidebar-button-display-type').value,
    icon_class: document.getElementById('edit-sidebar-button-icon').value,
    img_src: document.getElementById('edit-sidebar-button-img-src').value,
    svg_code: document.getElementById('edit-sidebar-button-svg-code').value,
    text_color: document.getElementById('edit-sidebar-button-text-color').value,
    bg_color: document.getElementById('edit-sidebar-button-bg-color').value,
    hover_color: document.getElementById('edit-sidebar-button-hover-color').value,
    border_color: document.getElementById('edit-sidebar-button-border-color').value,
    border_radius: document.getElementById('edit-sidebar-button-border-radius').value,
    font_size: document.getElementById('edit-sidebar-button-font-size').value,
    has_notification: button.has_notification || false
  };
  
  try {
    await window.convexClient.mutation("functions:updateSidebarButton", updatedButton);
    document.getElementById('edit-sidebar-button-popup').classList.add('hidden');
    await loadSidebarButtons();
    window.showNotification('Button updated!');
  } catch (error) {
    console.error('Error updating button:', error);
    alert('Error updating button');
  }
});

// Delete sidebar button
async function deleteSidebarButton(id) {
  if (!confirm('Delete this button?')) return;
  
  try {
    await window.convexClient.mutation("functions:deleteSidebarButton", { id });
    await loadSidebarButtons();
    window.showNotification('Button deleted!');
  } catch (error) {
    console.error('Error deleting button:', error);
    alert('Error deleting button');
  }
}

// Edit mode listener
document.addEventListener('editModeChanged', loadSidebarButtons);

window.loadSidebarButtons = loadSidebarButtons;
window.openEditSidebarButtonPopup = openEditSidebarButtonPopup;
window.deleteSidebarButton = deleteSidebarButton;
