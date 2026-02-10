# Chrome Extension UI Design Guide

This guide documents the cyberpunk-themed UI design system used in the YTC Subtitle Extractor extension. Use this as a template for creating consistent, visually appealing Chrome extensions.

## Design Philosophy

- **Cyberpunk Aesthetic**: Dark backgrounds with neon accent colors
- **Monospace Typography**: Console/terminal feel using Consolas or Courier New
- **Clear Hierarchy**: Color-coded sections and labels
- **Minimal but Functional**: Clean layout with all necessary controls
- **Responsive Feedback**: Visual states for hover, disabled, and active elements

---

## Color Palette

```css
/* Core Colors */
BG_COLOR:        #050a0e  /* Deep dark blue-black background */
FG_COLOR:        #10161d  /* Slightly lighter for panels/cards */
TEXT_COLOR:      #e0e0e0  /* Light gray for body text */

/* Accent Colors */
ACCENT_GREEN:    #00ff9f  /* Neon green for primary actions */
ACCENT_CYAN:     #00f0ff  /* Cyan for inputs and info */
ACCENT_MAGENTA:  #ff003c  /* Magenta/red for section titles */

/* Usage Guide */
- Background:        BG_COLOR
- Panels/Cards:      FG_COLOR
- Body Text:         TEXT_COLOR
- Headers/Titles:    ACCENT_GREEN
- Section Labels:    ACCENT_MAGENTA
- Input Fields:      ACCENT_CYAN borders
- Primary Buttons:   ACCENT_GREEN borders
- Hover States:      Invert (background becomes accent color)
```

---

## Typography

```css
/* Font Stack */
font-family: "Consolas", "Courier New", monospace;

/* Font Sizes */
- Body Text:         10-11pt
- Section Titles:    10-11pt (bold)
- Headers:           16-20pt (bold)
- Buttons:           11-12pt (bold)
- Hints/Small Text:  9pt (italic)

/* Font Weights */
- Normal Text:       normal
- Titles/Buttons:    bold
```

---

## Component Patterns

### 1. Popup Window (popup.html/css)

**Dimensions**: 400px width, auto height

**Structure**:
```html
<div class="container">
  <h1 class="header">EXTENSION NAME</h1>
  
  <div class="section">
    <label class="section-title">LABEL:</label>
    <!-- Input/control here -->
  </div>
  
  <button class="extract-btn">[ ACTION BUTTON ]</button>
  <div class="status">STATUS MESSAGE</div>
  
  <div class="footer">
    <a href="#" id="settingsLink">⚙️ Settings</a>
  </div>
</div>
```

**Key Styles**:
```css
body {
  width: 400px;
  background-color: #050a0e;
  color: #e0e0e0;
  font-family: "Consolas", "Courier New", monospace;
  font-size: 11pt;
}

.container {
  padding: 20px;
}

.header {
  text-align: center;
  color: #00ff9f;
  font-size: 16pt;
  font-weight: bold;
  margin-bottom: 20px;
  text-shadow: 0 0 10px #00ff9f; /* Glow effect */
}

.section {
  margin-bottom: 15px;
}

.section-title {
  display: block;
  color: #ff003c;
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 10pt;
}
```

### 2. Settings Page (options.html/css)

**Dimensions**: Max-width 700px, centered

**Structure**:
```html
<div class="container">
  <h1 class="header">SETTINGS</h1>
  
  <div class="section">
    <label class="section-title">SETTING NAME:</label>
    <!-- Input controls -->
    <p class="hint">Helpful description text</p>
  </div>
  
  <button class="save-btn">[ SAVE SETTINGS ]</button>
  <div class="status">Feedback message</div>
  
  <div class="info-section">
    <h3>ADDITIONAL INFO:</h3>
    <ul>
      <li>Info point 1</li>
      <li>Info point 2</li>
    </ul>
  </div>
</div>
```

**Key Styles**:
```css
body {
  background-color: #050a0e;
  color: #e0e0e0;
  font-family: "Consolas", "Courier New", monospace;
  font-size: 11pt;
  padding: 20px;
}

.container {
  max-width: 700px;
  margin: 0 auto;
  padding: 30px;
  background-color: #10161d;
  border: 1px solid #333;
  border-radius: 8px;
}

.section {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #333;
}

.hint {
  color: #888;
  font-size: 9pt;
  margin-top: 5px;
  font-style: italic;
}
```

### 3. Input Fields

**Text Input**:
```css
.text-input {
  width: 100%;
  background-color: #050a0e;
  border: 1px solid #00f0ff;
  padding: 8-10px;
  color: #00f0ff;
  border-radius: 4px;
  font-family: inherit;
  font-size: 9-10pt;
}

.text-input:focus {
  outline: none;
  border-color: #00ff9f;
}
```

**Select Dropdown**:
```css
.select {
  width: 100%;
  background-color: #10161d;
  border: 1px solid #ff003c;
  padding: 8-10px;
  color: #e0e0e0;
  border-radius: 4px;
  font-family: inherit;
  cursor: pointer;
}

.select:focus {
  outline: none;
  border-color: #00ff9f;
}
```

**Checkbox**:
```css
.checkbox-label {
  display: flex;
  align-items: center;
  color: #e0e0e0;
  cursor: pointer;
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 8px;
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #00f0ff;
}
```

### 4. Buttons

**Primary Action Button**:
```css
.extract-btn {
  width: 100%;
  background-color: #10161d;
  border: 2px solid #00ff9f;
  color: #00ff9f;
  padding: 12-15px;
  font-weight: bold;
  font-family: inherit;
  font-size: 11-12pt;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}

.extract-btn:hover {
  background-color: #00ff9f;
  color: #050a0e;
  box-shadow: 0 0 15px #00ff9f;
}

.extract-btn:disabled {
  border-color: #555;
  color: #555;
  cursor: not-allowed;
  box-shadow: none;
}
```

**Secondary Button**:
```css
.browse-btn {
  background-color: #10161d;
  border: 1px solid #00ff9f;
  color: #00ff9f;
  padding: 10px 20px;
  font-weight: bold;
  font-family: inherit;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}

.browse-btn:hover {
  background-color: #00ff9f;
  color: #050a0e;
}
```

### 5. Status/Feedback Display

```css
.status {
  text-align: center;
  color: #00f0ff;
  margin-top: 15px;
  padding: 8-10px;
  background-color: #10161d;
  border-radius: 4px;
  font-size: 10pt;
  min-height: 30-40px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### 6. Collapsible Sections

```css
.timeline-section {
  background-color: #10161d;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #333;
}

.time-input-group {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.time-input-group label {
  color: #00f0ff;
  margin-right: 10px;
  min-width: 50px;
  font-size: 10pt;
}
```

### 7. Info Boxes

```css
.info-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #050a0e;
  border: 1px solid #00f0ff;
  border-radius: 4px;
}

.info-section h3 {
  color: #00ff9f;
  margin-bottom: 15px;
  font-size: 11pt;
}

.info-section ul {
  list-style: none;
  padding-left: 0;
}

.info-section li {
  color: #e0e0e0;
  margin-bottom: 8px;
  padding-left: 20px;
  position: relative;
  font-size: 10pt;
}

.info-section li:before {
  content: "▸";
  color: #00f0ff;
  position: absolute;
  left: 0;
}
```

---

## Layout Patterns

### Popup Layout (400px width)

```
┌─────────────────────────────────────┐
│         EXTENSION NAME              │ ← Header (green, glowing)
├─────────────────────────────────────┤
│ LABEL:                              │ ← Section title (magenta)
│ [Input Field                     ]  │ ← Input (cyan border)
├─────────────────────────────────────┤
│ LABEL:                              │
│ [Dropdown ▼                      ]  │
├─────────────────────────────────────┤
│ ☐ Checkbox Option                   │
├─────────────────────────────────────┤
│ [ PRIMARY ACTION BUTTON ]           │ ← Full width (green)
├─────────────────────────────────────┤
│         Status Message              │ ← Centered feedback
├─────────────────────────────────────┤
│            ⚙️ Settings               │ ← Footer link
└─────────────────────────────────────┘
```

### Settings Layout (700px max-width, centered)

```
┌───────────────────────────────────────────────┐
│                  SETTINGS                     │ ← Header
├───────────────────────────────────────────────┤
│ SECTION 1:                                    │
│ [Input Field              ] [Browse Button]   │
│ Helpful hint text                             │
├───────────────────────────────────────────────┤
│ SECTION 2:                                    │
│ [Dropdown ▼                                ]  │
├───────────────────────────────────────────────┤
│ DEFAULT VALUES:                               │
│   Language: [Dropdown ▼                    ]  │
│   Format:   [Dropdown ▼                    ]  │
│   ☐ Option checkbox                           │
├───────────────────────────────────────────────┤
│         [ SAVE SETTINGS ]                     │
├───────────────────────────────────────────────┤
│         Feedback message                      │
├───────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐  │
│ │ ADDITIONAL INFO:                        │  │
│ │ ▸ Info point 1                          │  │
│ │ ▸ Info point 2                          │  │
│ └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

---

## JavaScript Patterns

### Settings Management

```javascript
// Load settings on page load
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.sync.get({
    setting1: 'default1',
    setting2: false,
    setting3: 'default3'
  }, (settings) => {
    document.getElementById('setting1').value = settings.setting1;
    document.getElementById('setting2').checked = settings.setting2;
    document.getElementById('setting3').value = settings.setting3;
  });
});

// Save settings
document.getElementById('save').addEventListener('click', () => {
  const settings = {
    setting1: document.getElementById('setting1').value,
    setting2: document.getElementById('setting2').checked,
    setting3: document.getElementById('setting3').value
  };
  
  chrome.storage.sync.set(settings, () => {
    showStatus('SETTINGS SAVED!', '#00ff9f');
  });
});

// Show status message
function showStatus(message, color = '#00f0ff') {
  const status = document.getElementById('status');
  status.textContent = message;
  status.style.color = color;
  
  setTimeout(() => {
    status.textContent = '';
  }, 3000);
}
```

### Toggle Visibility

```javascript
// Toggle sections based on checkbox
document.getElementById('enableFeature').addEventListener('change', () => {
  const enabled = document.getElementById('enableFeature').checked;
  document.getElementById('featureOptions').style.display = enabled ? 'block' : 'none';
});

// Toggle sections based on dropdown
document.getElementById('mode').addEventListener('change', () => {
  const mode = document.getElementById('mode').value;
  document.getElementById('modeAOptions').style.display = mode === 'a' ? 'block' : 'none';
  document.getElementById('modeBOptions').style.display = mode === 'b' ? 'block' : 'none';
});
```

### Button States

```javascript
// Disable button during operation
async function performAction() {
  const btn = document.getElementById('actionBtn');
  btn.disabled = true;
  setStatus('PROCESSING...');
  
  try {
    await doSomething();
    setStatus('SUCCESS!');
  } catch (error) {
    setStatus(`ERROR: ${error.message}`);
  } finally {
    btn.disabled = false;
  }
}
```

---

## Manifest.json Template

```json
{
  "manifest_version": 3,
  "name": "Extension Name",
  "version": "1.0.0",
  "description": "Extension description",
  "permissions": [
    "activeTab",
    "storage"
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "background": {
    "service_worker": "background.js"
  },
  "options_page": "options.html",
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

---

## File Structure

```
extension-name/
├── manifest.json
├── popup.html
├── popup.css
├── popup.js
├── options.html
├── options.css
├── options.js
├── background.js
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```

---

## Icon Design

**Style**: Cyberpunk theme with neon colors

**Specifications**:
- Sizes: 16x16, 48x48, 128x128 pixels
- Background: Dark (#050a0e)
- Border: Neon green (#00ff9f)
- Text/Symbol: Cyan (#00f0ff)
- Font: Monospace/bold

**SVG Template**:
```svg
<svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">
  <rect width="128" height="128" fill="#050a0e"/>
  <rect x="8" y="8" width="112" height="112" fill="none" stroke="#00ff9f" stroke-width="4"/>
  <text x="64" y="80" font-family="monospace" font-size="48" fill="#00f0ff" text-anchor="middle" font-weight="bold">ABC</text>
</svg>
```

---

## Accessibility Considerations

1. **Color Contrast**: All text meets WCAG AA standards
   - Light text (#e0e0e0) on dark background (#050a0e)
   - Accent colors are bright and visible

2. **Focus States**: All interactive elements have visible focus states
   ```css
   input:focus, select:focus, button:focus {
     outline: 2px solid #00ff9f;
     outline-offset: 2px;
   }
   ```

3. **Labels**: All inputs have associated labels
   ```html
   <label for="inputId">Label Text:</label>
   <input id="inputId" type="text">
   ```

4. **Button States**: Disabled buttons are clearly indicated
   ```css
   button:disabled {
     opacity: 0.5;
     cursor: not-allowed;
   }
   ```

---

## Animation & Transitions

**Smooth Transitions**:
```css
button, input, select {
  transition: all 0.3s ease;
}
```

**Hover Effects**:
```css
button:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 15px currentColor;
}
```

**Glow Effects**:
```css
.header {
  text-shadow: 0 0 10px #00ff9f;
}

button:hover {
  box-shadow: 0 0 15px #00ff9f;
}
```

---

## Best Practices

1. **Consistent Spacing**: Use 15-25px margins between sections
2. **Full-Width Buttons**: Primary action buttons should span full width
3. **Clear Hierarchy**: Use color to distinguish different types of content
4. **Feedback**: Always show status messages after actions
5. **Persistence**: Save user preferences using chrome.storage.sync
6. **Responsive**: Test at different zoom levels
7. **Loading States**: Disable buttons and show status during operations
8. **Error Handling**: Display clear error messages in the status area

---

## Quick Start Checklist

- [ ] Copy color palette to CSS
- [ ] Set up base typography (Consolas/Courier New)
- [ ] Create container with padding
- [ ] Add header with glow effect
- [ ] Create sections with magenta titles
- [ ] Style inputs with cyan borders
- [ ] Create primary button with green accent
- [ ] Add status display area
- [ ] Implement settings persistence
- [ ] Add hover states to all interactive elements
- [ ] Test all states (normal, hover, disabled, focus)
- [ ] Create icons in 16x16, 48x48, 128x128

---

## Example: Minimal Extension

**popup.html**:
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Extension Name</title>
  <link rel="stylesheet" href="popup.css">
</head>
<body>
  <div class="container">
    <h1 class="header">EXTENSION NAME</h1>
    
    <div class="section">
      <label class="section-title">INPUT:</label>
      <input type="text" id="input1" class="text-input" placeholder="Enter value...">
    </div>

    <div class="section">
      <label class="checkbox-label">
        <input type="checkbox" id="option1">
        Enable Feature
      </label>
    </div>

    <button id="action" class="extract-btn">[ EXECUTE ]</button>
    <div id="status" class="status">READY</div>
  </div>
  <script src="popup.js"></script>
</body>
</html>
```

**popup.css**: Use the styles from this guide

**popup.js**:
```javascript
document.getElementById('action').addEventListener('click', async () => {
  const input = document.getElementById('input1').value;
  const option = document.getElementById('option1').checked;
  
  document.getElementById('status').textContent = 'PROCESSING...';
  
  // Your logic here
  
  document.getElementById('status').textContent = 'COMPLETE!';
});
```

---

This design system creates a cohesive, professional-looking Chrome extension with a distinctive cyberpunk aesthetic. All components are reusable and can be mixed and matched for different extension types.
