# Convex Integration Guide for Chrome Extensions

This project uses **Convex** as a hosted backend for persistent storage and easy synchronization across extensions.

## 🚀 Quick Start (One-Time Setup)

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Convex Development**:
   ```bash
   npx convex dev
   ```
   - Follow the prompts to create an account/project.
   - Once running, it will provide a **Convex Deployment URL** (e.g., `https://happy-monkey-123.convex.cloud`).

3. **Configure Extensions**:
   Replace `YOUR_CONVEX_URL_HERE` in each extension's `background.js` with your Convex URL.

---

## ➕ Adding a New Extension

### 1. Update `manifest.json`

```json
{
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "host_permissions": [
    "https://*.convex.cloud/*"
  ]
}
```

### 2. Add to `background.js`

```javascript
import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

const CONVEX_URL = "YOUR_CONVEX_URL_HERE";
const EXTENSION_NAME = 'your_extension_unique_name'; // must be unique per extension
const client = new ConvexHttpClient(CONVEX_URL);

async function sendDataToConvex(data) {
  try {
    const result = await client.mutation("functions:save", { extensionName: EXTENSION_NAME, data });
    return { success: true, result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function loadDataFromConvex() {
  try {
    const data = await client.query("functions:get", { extensionName: EXTENSION_NAME });
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Auto-save on storage changes
chrome.storage.local.onChanged.addListener(() => {
  chrome.storage.local.get(null, (items) => sendDataToConvex(items));
});

// Handle manual backup/restore from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveToConvex') {
    sendDataToConvex(message.data)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  if (message.action === 'loadFromConvex') {
    loadDataFromConvex()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});
```

### 3. Add Backup/Restore Buttons to `popup.html`

Add these buttons wherever you want them in your popup:

```html
<button id="saveToConvex" class="btn-convex-save">💾 Backup</button>
<button id="loadFromConvex" class="btn-convex-load">📂 Restore</button>
```

Add these styles:

```css
.btn-convex-save { background: #9C27B0; color: white; }
.btn-convex-load { background: #673AB7; color: white; }
```

### 4. Add Button Logic to `popup.js`

Drop this block in — no popups, button text gives all the feedback:

```javascript
const saveToConvexBtn = document.getElementById('saveToConvex');
const loadFromConvexBtn = document.getElementById('loadFromConvex');

if (saveToConvexBtn) {
  saveToConvexBtn.addEventListener('click', function () {
    const original = saveToConvexBtn.innerHTML;
    saveToConvexBtn.innerHTML = '⏳ Saving...';

    chrome.storage.local.get(null, (items) => {
      chrome.runtime.sendMessage({ action: 'saveToConvex', data: items }, (response) => {
        if (response && response.success !== false) {
          saveToConvexBtn.innerHTML = '✅ Saved!';
        } else {
          saveToConvexBtn.innerHTML = '❌ Failed';
        }
        setTimeout(() => { saveToConvexBtn.innerHTML = original; }, 2000);
      });
    });
  });
}

if (loadFromConvexBtn) {
  loadFromConvexBtn.addEventListener('click', function () {
    const original = loadFromConvexBtn.innerHTML;
    loadFromConvexBtn.innerHTML = '⏳ Loading...';

    chrome.runtime.sendMessage({ action: 'loadFromConvex' }, (response) => {
      if (response && response.success !== false && response.data) {
        chrome.storage.local.set(response.data, () => {
          loadFromConvexBtn.innerHTML = '✅ Restored!';
          setTimeout(() => { loadFromConvexBtn.innerHTML = original; }, 2000);
        });
      } else {
        loadFromConvexBtn.innerHTML = '❌ Failed';
        setTimeout(() => { loadFromConvexBtn.innerHTML = original; }, 2000);
      }
    });
  });
}
```

> If your extension uses `chrome.storage.sync` instead of `local`, replace `chrome.storage.local` with `chrome.storage.sync` in both files.

---

## 🛠️ Convex Backend Structure

Located in the `convex/` folder at the project root (shared by all extensions):
- `schema.ts` — defines the `backups` table with an index on `extensionName`
- `functions.ts` — contains the `save` mutation and `get` query

---

## 📈 Deployment

```bash
npx convex deploy
```

Use the **Production URL** in your extension files so data persists without `npx convex dev` running.
