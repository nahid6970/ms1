# Convex Project Setup Guide

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
- Creates a Convex account (if needed)
- Generates deployment URLs:
  - Dev: `https://xxx.convex.cloud` (for development)
  - Prod: `https://yyy.convex.cloud` (for production)

## Backend (Convex Functions)

### File Location
All backend code goes in `convex/` folder with `.ts` extension.

### Function Types

**Query** - Read data (no side effects)
```typescript
import { query } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("tableName").collect();
  },
});
```

**Mutation** - Write/modify data
```typescript
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const add = mutation({
  args: { title: v.string(), content: v.string() },
  handler: async (ctx, args) => {
    await ctx.db.insert("tableName", { 
      title: args.title, 
      content: args.content 
    });
  },
});

export const update = mutation({
  args: { id: v.id("tableName"), title: v.string() },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { title: args.title });
  },
});

export const remove = mutation({
  args: { id: v.id("tableName") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
```

### Function Naming
If file is `convex/functions.ts`, call functions as:
- `functions:list`
- `functions:add`
- `functions:update`

## Frontend (Separate Files)

### File Structure
```
project/
├── index.html
├── style.css
└── app.js
```

### index.html
```html
<!DOCTYPE html>
<html>
<head>
  <title>App</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div id="app"></div>
  <script type="module" src="app.js"></script>
</body>
</html>
```

### style.css
```css
body {
  font-family: Arial, sans-serif;
  padding: 20px;
}

.content {
  color: #666;
  margin: 10px 0;
}
```

### app.js
```javascript
import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

const client = new ConvexHttpClient("YOUR_CONVEX_URL_HERE");

// Query data
async function loadData() {
  const data = await client.query("functions:list");
  document.getElementById('app').innerHTML = data.map(item => 
    `<div>${item.title}</div>`
  ).join('');
}

// Mutate data
async function addItem(title, content) {
  await client.mutation("functions:add", { title, content });
  loadData();
}

loadData();
```

### With Markdown Support (Optional)
Add to `app.js`:
```javascript
import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";
import { marked } from "https://esm.sh/marked@11.1.1";

marked.setOptions({ gfm: true, breaks: true });

const client = new ConvexHttpClient("YOUR_CONVEX_URL_HERE");

async function loadData() {
  const data = await client.query("functions:list");
  document.getElementById('app').innerHTML = data.map(item => 
    `<div class="content">${marked.parse(item.content)}</div>`
  ).join('');
}

loadData();
```

## Deployment Workflow

### Development (Run Manually)
1. Run `npx convex dev` (auto-deploys on file changes)
2. Use dev URL in HTML for testing
3. Keep terminal open while developing

### Production (Run Manually)
1. Run `npx convex deploy` (manual deployment)
2. Update HTML with prod URL
3. Deploy HTML to GitHub Pages or any static host

## Important Notes

### Deployments
- **40 deployments/month** on free tier
- Only changes to `convex/` folder count as deployments
- HTML/CSS changes don't count
- Closing terminal doesn't count as deployment
- Backend stays live even when terminal is closed

### Database
- Tables are created automatically on first insert
- Old tables remain until manually deleted
- Check tables in Convex dashboard

### URLs
- **Dev URL**: For development, changes with `npx convex dev`
- **Prod URL**: For production, only changes with `npx convex deploy`
- Always use prod URL for public/GitHub Pages deployments

### GitHub Pages
- Only hosts the HTML/frontend
- Backend runs on Convex servers (free)
- They communicate via HTTPS
- No need to commit `node_modules/` or `convex/` to deploy frontend

## Common Patterns

### Auto-refresh Data
```javascript
loadData();
setInterval(loadData, 5000); // Refresh every 5 seconds
```

### Error Handling
```javascript
try {
  await client.mutation("functions:add", { title, content });
} catch (error) {
  console.error("Error:", error);
  alert("Failed to save");
}
```

### Escaping in Template Strings
```javascript
// Escape backticks and quotes in dynamic content
const html = `<div onclick="func('${id}', \`${text.replace(/`/g, '\\`')}\`)">`;
```

## Troubleshooting

### "Could not find public function"
- Function name doesn't match file name
- Forgot to run `npx convex dev`
- Using wrong URL (dev vs prod)

### Import errors in browser
- Wrong CDN path
- Try: `https://esm.sh/convex@1.16.0/browser`
- Enable GFM: `marked.setOptions({ gfm: true })`

### Data not updating
- Hard refresh browser (Ctrl+Shift+R)
- Check Convex dashboard for errors
- Verify function names match

## Quick Start Checklist
- [ ] Create `.gitignore` file (node_modules/, .convex/, package-lock.json)
- [ ] Create `package.json` with convex dependency
- [ ] Run `npm install` manually
- [ ] Run `npx convex dev` manually
- [ ] Create `convex/functions.ts` with queries/mutations
- [ ] Create `index.html` with simple HTML/JS (no framework)
- [ ] Replace `YOUR_CONVEX_URL_HERE` with actual URL
- [ ] Test locally by opening HTML in browser
- [ ] For production: run `npx convex deploy` manually and use prod URL
