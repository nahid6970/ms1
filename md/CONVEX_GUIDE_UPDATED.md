# Convex Project Setup Guide (Updated for Real-time)

## Project Structure
```
project/
├── convex/
│   └── functions.ts          # Backend functions (queries, mutations)
├── index.html                 # Frontend (can be any framework)
├── package.json
└── package-lock.json
```

## Initial Setup

### 1. Create `.gitignore`
```
node_modules/
.convex/
package-lock.json
```

### 2. Create package.json
```json
{
  "name": "project-name",
  "version": "1.0.0",
  "devDependencies": {
    "convex": "^1.16.0"
  }
}
```

### 3. Install Dependencies (Run Manually)
```bash
npm install
```

### 4. Initialize Convex (Run Manually)
```bash
npx convex dev
```

---

## Choosing the Right Client

| Feature | `ConvexHttpClient` | `ConvexClient` (Real-time) |
| :--- | :--- | :--- |
| **Best For** | Static pages, simple forms, blogs | Dashboards, Chat, File Managers, Games |
| **Update Style** | One-time fetch (manual refresh) | Automatic (WebSocket subscription) |
| **Resource Usage** | Lowest (no persistent connection) | Slightly higher (stays connected) |
| **Complexity** | Simple `async/await` | Uses callbacks for updates |

---

## Frontend Implementation

### Option 1: Static Fetch (`ConvexHttpClient`)
Use this for simple apps where real-time isn't critical.

```javascript
import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";
const client = new ConvexHttpClient("YOUR_CONVEX_URL_HERE");

async function loadData() {
  const data = await client.query("functions:list");
  // Render data...
}

// Manually call after mutation
async function addItem(title) {
  await client.mutation("functions:add", { title });
  loadData(); 
}
```

### Option 2: Real-time Subscription (`ConvexClient`)
Use this for interactive apps that should update instantly.

```javascript
import { ConvexClient } from "https://esm.sh/convex@1.16.0/browser";
const client = new ConvexClient("YOUR_CONVEX_URL_HERE");

// This runs automatically whenever data changes in the DB
client.onUpdate("functions:list", {}, (data) => {
  document.getElementById('app').innerHTML = data.map(item => 
    `<div>${item.title}</div>`
  ).join('');
});

// No need to call loadData() after mutation!
async function addItem(title) {
  await client.mutation("functions:add", { title });
}
```

---

## Troubleshooting

### Data not updating?
- **HttpClient**: Did you forget to call your load function after a mutation?
- **ConvexClient**: Check the browser console for WebSocket connection errors.
- **Both**: Ensure `npx convex dev` is running and your function names match the file names exactly (`file:function`).

### "ConvexClient is not a constructor"
- Ensure you are importing from `https://esm.sh/convex@1.16.0/browser`.
