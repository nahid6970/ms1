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

### 1. Create package.json
```json
{
  "name": "project-name",
  "version": "1.0.0",
  "scripts": {
    "dev": "convex dev"
  },
  "devDependencies": {
    "convex": "^1.16.0"
  }
}
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Initialize Convex
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

## Frontend (HTML)

### Basic Template
```html
<!DOCTYPE html>
<html>
<head>
  <title>App</title>
</head>
<body>
  <div id="app"></div>

  <script type="module">
    import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";
    
    const client = new ConvexHttpClient("YOUR_CONVEX_URL_HERE");
    
    // Query data
    async function loadData() {
      const data = await client.query("functions:list");
      console.log(data);
    }
    
    // Mutate data
    async function addItem() {
      await client.mutation("functions:add", { 
        title: "Test", 
        content: "Content" 
      });
    }
    
    loadData();
  </script>
</body>
</html>
```

### Markdown Support (Optional)
```html
<script type="module">
  import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";
  import { marked } from "https://esm.sh/marked@11.1.1";
  
  marked.setOptions({
    gfm: true,  // GitHub Flavored Markdown (tables, etc.)
    breaks: true
  });
  
  const client = new ConvexHttpClient("YOUR_CONVEX_URL");
  
  // Render markdown
  const html = marked.parse(markdownText);
</script>
```

### Markdown CSS Styling
```css
.content { color: #666; }
.content h1, .content h2, .content h3 { margin: 10px 0 5px 0; }
.content p { margin: 5px 0; }
.content code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
.content pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
.content pre code { background: none; padding: 0; }
.content ul, .content ol { margin-left: 20px; }
.content table { border-collapse: collapse; width: 100%; margin: 10px 0; }
.content table th, .content table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
.content table th { background: #f4f4f4; font-weight: bold; }
```

## Deployment Workflow

### Development
1. Run `npx convex dev` (auto-deploys on file changes)
2. Use dev URL in HTML for testing
3. Keep terminal open while developing

### Production
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
- [ ] Create `package.json` with convex dependency
- [ ] Run `npm install`
- [ ] Run `npx convex dev`
- [ ] Create `convex/functions.ts` with queries/mutations
- [ ] Create `index.html` with ConvexHttpClient
- [ ] Replace `YOUR_CONVEX_URL_HERE` with actual URL
- [ ] Test locally by opening HTML in browser
- [ ] For production: run `npx convex deploy` and use prod URL
