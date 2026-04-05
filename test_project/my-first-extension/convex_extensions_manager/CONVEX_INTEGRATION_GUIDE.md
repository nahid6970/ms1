# Convex Integration Guide for Chrome Extensions

This project has been migrated from a local Python backup system to **Convex**, a hosted backend that provides persistent storage and easy synchronization.

## 🚀 Quick Start (One-Time Setup)

1. **Install Dependencies**:
   Open your terminal in the project root and run:
   ```bash
   npm install
   ```

2. **Start Convex Development**:
   Run the following command to initialize your Convex project and start the development server:
   ```bash
   npx convex dev
   ```
   - Follow the prompts to create an account/project.
   - Once running, it will provide a **Convex Deployment URL** (e.g., `https://happy-monkey-123.convex.cloud`).

3. **Configure Extensions**:
   Copy your **Convex Deployment URL** and replace `YOUR_CONVEX_URL_HERE` in the following files:
   - `SideBar/background.js`
   - `highlight/background.js`
   - `image_checker/background.js`
   - `tab_saver/background.js`

## ➕ Adding a New Extension

To add backup support to a new extension, follow these steps:

### 1. Update `manifest.json`
Add `type: "module"` to the background service worker and update `host_permissions`:

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

### 2. Implement Convex Logic in `background.js`
Import the `ConvexHttpClient` and implement `save` and `get` calls:

```javascript
import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

const CONVEX_URL = "YOUR_CONVEX_URL_HERE"; 
const EXTENSION_NAME = 'your_extension_unique_name';
const client = new ConvexHttpClient(CONVEX_URL);

// Save Function
async function saveToConvex(data) {
  return await client.mutation("functions:save", {
    extensionName: EXTENSION_NAME,
    data: data
  });
}

// Load Function
async function loadFromConvex() {
  return await client.query("functions:get", { 
    extensionName: EXTENSION_NAME 
  });
}

// Auto-save Example
chrome.storage.local.onChanged.addListener((changes) => {
  chrome.storage.local.get(null, (items) => {
    saveToConvex(items);
  });
});
```

### 3. (Optional) Manual Backup/Restore in Popup
In your `popup.js`, you can trigger these functions via `chrome.runtime.sendMessage`.

## 🛠️ Convex Backend Structure

The backend is located in the `convex/` folder:
- `schema.ts`: Defines the `backups` table with an index on `extensionName`.
- `functions.ts`: Contains the `save` mutation (handles create/update) and the `get` query.

## 📈 Deployment
When you are ready for production:
1. Run `npx convex deploy`.
2. Use the **Production URL** in your extension files.
3. This ensures your data remains even if you stop the `npx convex dev` command.
