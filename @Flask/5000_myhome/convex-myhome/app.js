import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

const client = new ConvexHttpClient("https://lovable-wildcat-595.convex.cloud");

window.convexClient = client;
window.editMode = false;

// F1 key toggle edit mode
document.addEventListener('keydown', (e) => {
  if (e.key === 'F1') {
    e.preventDefault();
    window.editMode = !window.editMode;
    document.querySelector('.flex-container2').classList.toggle('edit-mode', window.editMode);
    document.dispatchEvent(new CustomEvent('editModeChanged', { detail: { isEditMode: window.editMode } }));
  }
});

// Close popups
document.querySelectorAll('.close-button').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.closest('.popup-container').classList.add('hidden');
  });
});

window.addEventListener('click', (e) => {
  if (e.target.classList.contains('popup-container')) {
    e.target.classList.add('hidden');
  }
});

// Show notification
window.showNotification = (message, type = 'success') => {
  const notif = document.getElementById('copy-notification');
  notif.textContent = message;
  notif.className = `copy-notification ${type} show`;
  setTimeout(() => notif.classList.remove('show'), 2000);
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  if (typeof loadLinks === 'function') loadLinks();
  if (typeof loadSidebarButtons === 'function') loadSidebarButtons();
  setupColorPreview();
});

// Color preview system
function setupColorPreview() {
  document.addEventListener('input', (e) => {
    if (e.target.classList.contains('color-input') || 
        e.target.placeholder?.toLowerCase().includes('color')) {
      applyColorPreview(e.target);
    }
  });
  
  // Apply to existing inputs
  document.querySelectorAll('.color-input, input[placeholder*="olor"], input[placeholder*="Color"]').forEach(input => {
    applyColorPreview(input);
  });
}

function applyColorPreview(input) {
  const value = input.value.trim();
  if (!value) {
    input.style.backgroundColor = '';
    input.style.color = '';
    input.classList.remove('color-preview');
    return;
  }
  
  // Test if valid color
  const test = document.createElement('div');
  test.style.color = value;
  if (test.style.color || value.match(/^#[0-9A-Fa-f]{3,6}$/)) {
    input.style.backgroundColor = value;
    input.style.color = getContrastColor(value);
    input.classList.add('color-preview');
  } else {
    input.style.backgroundColor = '';
    input.style.color = '';
    input.classList.remove('color-preview');
  }
}

function getContrastColor(color) {
  let r, g, b;
  
  if (color.startsWith('#')) {
    const hex = color.slice(1);
    if (hex.length === 3) {
      r = parseInt(hex[0] + hex[0], 16);
      g = parseInt(hex[1] + hex[1], 16);
      b = parseInt(hex[2] + hex[2], 16);
    } else {
      r = parseInt(hex.slice(0, 2), 16);
      g = parseInt(hex.slice(2, 4), 16);
      b = parseInt(hex.slice(4, 6), 16);
    }
  } else {
    const test = document.createElement('div');
    test.style.color = color;
    document.body.appendChild(test);
    const computed = window.getComputedStyle(test).color;
    document.body.removeChild(test);
    
    const match = computed.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      r = parseInt(match[1]);
      g = parseInt(match[2]);
      b = parseInt(match[3]);
    } else {
      return '#fff';
    }
  }
  
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness > 128 ? '#000' : '#fff';
}
