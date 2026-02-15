# Convex Migration Guide - MyHome Bookmark Manager

## Project Overview
Advanced bookmark manager with grouped links, extensive customization, and multiple display modes. Migrating from Flask + JSON to Convex serverless backend.

## Current Features
- **3 Group Display Types**:
  1. **Top Groups** - Collapsible buttons at the top (like folders)
  2. **Flex Groups** - Expanded grid layout with cards
  3. **List Groups** - Compact list view with truncated text
  
- **Icon Customization**:
  - NerdFont icons (e.g., `nf nf-fa-home`)
  - SVG code with custom width/height/color
  - Plain text labels
  
- **Advanced Styling**:
  - Gradient animations (slide/rotate modes with angles)
  - Per-item colors (background, border, text, hover)
  - Per-group colors (top bar, popup, horizontal items)
  - Border radius, width, height customization
  
- **Other Features**:
  - Drag-and-drop reordering (items & groups)
  - **Password protection** - Lock groups with password
  - Hidden items (visible only in edit mode)
  - Context menu (copy, edit, delete)
  - Multiple URL support per link

## Migration Strategy
Keep the frontend UI intact, replace Flask API with Convex backend.

---

## Setup

### 1. Create package.json
```json
{
  "name": "myhome-convex",
  "version": "1.0.0",
  "scripts": {
    "dev": "convex dev"
  },
  "devDependencies": {
    "convex": "^1.16.0"
  }
}
```

### 2. Install & Initialize
```bash
npm install
npx convex dev
```
Save the generated Convex URL (e.g., `https://xxx.convex.cloud`)

---

## Backend Implementation

### File: `convex/links.ts`

```typescript
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Link schema validator (all styling properties)
const linkValidator = v.object({
  name: v.string(),
  url: v.optional(v.string()),
  title: v.optional(v.string()),
  group: v.optional(v.string()),
  click_action: v.optional(v.string()), // 'url'
  default_type: v.optional(v.string()), // 'text', 'nerd-font', etc.
  icon_class: v.optional(v.string()),
  hidden: v.optional(v.boolean()),
  
  // Group display settings
  collapsible: v.optional(v.boolean()), // Show at top as collapsible button
  display_style: v.optional(v.string()), // 'flex' or 'list-item'
  horizontal_stack: v.optional(v.boolean()),
  password_protect: v.optional(v.boolean()),
  
  // Top group styling (for collapsible groups)
  top_name: v.optional(v.string()), // Custom display name (text/NF icon/SVG)
  top_bg_color: v.optional(v.string()),
  top_text_color: v.optional(v.string()),
  top_border_color: v.optional(v.string()),
  top_hover_color: v.optional(v.string()),
  
  // Popup styling (for expanded collapsible groups)
  popup_bg_color: v.optional(v.string()),
  popup_text_color: v.optional(v.string()),
  popup_border_color: v.optional(v.string()),
  popup_border_radius: v.optional(v.string()),
  
  // Horizontal item styling (items inside popup)
  horizontal_bg_color: v.optional(v.string()),
  horizontal_text_color: v.optional(v.string()),
  horizontal_border_color: v.optional(v.string()),
  horizontal_hover_color: v.optional(v.string()),
  
  // Individual link item styling
  li_bg_color: v.optional(v.string()),
  li_hover_color: v.optional(v.string()),
  li_border_color: v.optional(v.string()),
  li_border_radius: v.optional(v.string()),
  li_width: v.optional(v.string()),
  li_height: v.optional(v.string()),
  
  order: v.optional(v.number()),
});

## Key Styling Features Explained

### Gradient Colors
Colors support gradients with animation modes:
```javascript
// Slide mode (default) - gradient moves
"li_bg_color": "slide: 45deg: #ff0000, #00ff00, #0000ff"

// Rotate mode - colors fade in/out
"li_border_color": "rotate: #ff0000, #00ff00, #0000ff"

// Custom angle
"top_bg_color": "slide: 90deg: #ff0000, #00ff00"
```

### Display Name Options
The `top_name` field supports:
```javascript
// Plain text
"top_name": "My Bookmarks"

// NerdFont icon
"top_name": "nf nf-fa-folder"

// SVG code (with custom size/color via CSS)
"top_name": "<svg width='24' height='24'>...</svg>"
```

### Group Display Types

**1. Collapsible (Top Groups)**
```javascript
{
  "collapsible": true,
  "display_style": "flex", // or "list-item"
  "top_name": "nf nf-fa-folder",
  "top_bg_color": "Yellow",
  "popup_bg_color": "#31343a"
}
```
Shows as button at top, expands to popup on click.

**2. Flex Groups (Expanded Grid)**
```javascript
{
  "collapsible": false,
  "display_style": "flex",
  "li_bg_color": "#474747",
  "li_width": "200px",
  "li_height": "100px"
}
```
Shows items as cards in grid layout.

**3. List Groups (Compact)**
```javascript
{
  "collapsible": false,
  "display_style": "list-item"
}
```
Shows items as compact list with truncated text.

### Password Protection
Lock groups with password:
```javascript
{
  "group": "Private",
  "password_protect": true,
  "collapsible": true
}
```
When clicked, prompts for password before showing group contents.

// Get all links
export const getLinks = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("links").order("by", "order", "asc").collect();
  },
});

// Add new link
export const addLink = mutation({
  args: { link: linkValidator },
  handler: async (ctx, args) => {
    const links = await ctx.db.query("links").collect();
    const maxOrder = Math.max(...links.map(l => l.order || 0), 0);
    
    await ctx.db.insert("links", {
      ...args.link,
      default_type: args.link.default_type || "text",
      horizontal_stack: args.link.horizontal_stack ?? false,
      order: maxOrder + 1,
    });
  },
});

// Update link
export const updateLink = mutation({
  args: { 
    id: v.id("links"),
    link: linkValidator 
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, args.link);
  },
});

// Delete link
export const deleteLink = mutation({
  args: { id: v.id("links") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// Reorder all links
export const reorderLinks = mutation({
  args: { 
    links: v.array(v.object({
      id: v.id("links"),
      order: v.number()
    }))
  },
  handler: async (ctx, args) => {
    for (const link of args.links) {
      await ctx.db.patch(link.id, { order: link.order });
    }
  },
});
```

---

## Frontend Migration

### Update `templates/index.html`

Replace Flask API calls with Convex client:

```html
<script type="module">
  import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";
  
  const client = new ConvexHttpClient("YOUR_CONVEX_URL_HERE");
  
  // Load links
  async function loadLinks() {
    try {
      const links = await client.query("links:getLinks");
      renderLinks(links);
    } catch (error) {
      console.error("Error loading links:", error);
    }
  }
  
  // Add link
  async function addLink(linkData) {
    try {
      await client.mutation("links:addLink", { link: linkData });
      await loadLinks();
    } catch (error) {
      console.error("Error adding link:", error);
    }
  }
  
  // Update link
  async function updateLink(id, linkData) {
    try {
      await client.mutation("links:updateLink", { id, link: linkData });
      await loadLinks();
    } catch (error) {
      console.error("Error updating link:", error);
    }
  }
  
  // Delete link
  async function deleteLink(id) {
    try {
      await client.mutation("links:deleteLink", { id });
      await loadLinks();
    } catch (error) {
      console.error("Error deleting link:", error);
    }
  }
  
  // Reorder links
  async function reorderLinks(linksArray) {
    try {
      await client.mutation("links:reorderLinks", { links: linksArray });
    } catch (error) {
      console.error("Error reordering links:", error);
    }
  }
  
  // Initial load
  loadLinks();
  
  // Auto-refresh every 30 seconds
  setInterval(loadLinks, 30000);
</script>
```

### Update Existing JavaScript Files

**In `static/links-handler.js`** - Replace fetch calls:

```javascript
// OLD (Flask)
fetch('/api/links')
  .then(res => res.json())
  .then(data => renderLinks(data));

// NEW (Convex)
const links = await client.query("links:getLinks");
renderLinks(links);
```

**In `static/main.js`** - Update CRUD operations:

```javascript
// OLD (Flask)
fetch('/api/add_link', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(linkData)
});

// NEW (Convex)
await client.mutation("links:addLink", { link: linkData });
```

---

## Data Migration

### Export existing data:
```bash
cat data.json > links_backup.json
```

### Import to Convex:

Create `convex/importData.ts`:

```typescript
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const importLinks = mutation({
  args: { links: v.any() },
  handler: async (ctx, args) => {
    for (let i = 0; i < args.links.length; i++) {
      await ctx.db.insert("links", {
        ...args.links[i],
        order: i
      });
    }
  },
});
```

Run in browser console:
```javascript
const backupData = [...]; // Paste your JSON data
await client.mutation("importData:importLinks", { links: backupData });
```

---

## Deployment

### Development
1. Run `npx convex dev` (keep terminal open)
2. Open `index.html` in browser
3. Changes to `convex/` auto-deploy

### Production
1. Run `npx convex deploy`
2. Update HTML with production URL
3. Deploy HTML to GitHub Pages or static host

---

## Key Differences from Flask

| Feature | Flask | Convex |
|---------|-------|--------|
| Data Storage | JSON file | Cloud database |
| API Endpoints | `/api/links` | `links:getLinks` |
| Server | Local (port 5000) | Serverless cloud |
| Deployment | Manual restart | Auto-deploy |
| Scaling | Single instance | Auto-scales |

---

## Features NOT Migrated

These require separate services (not part of Convex migration):

- **Sidebar buttons** (`sidebar_buttons.json`) - Keep as separate Convex table
- **Notification APIs** (TV/Movie notifications) - External services, keep proxy endpoints
- **File operations** (`/open-file`) - Not possible in browser, remove or use desktop app
- **Static HTML generation** (`generate_static.py`) - Not needed with Convex

---

## Sidebar Buttons Migration

### File: `convex/sidebar.ts`

```typescript
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const buttonValidator = v.object({
  id: v.string(),
  name: v.string(),
  display_type: v.string(),
  icon_class: v.optional(v.string()),
  img_src: v.optional(v.string()),
  url: v.string(),
  has_notification: v.optional(v.boolean()),
  notification_api: v.optional(v.string()),
  mark_seen_api: v.optional(v.string()),
  text_color: v.optional(v.string()),
  bg_color: v.optional(v.string()),
  hover_color: v.optional(v.string()),
  border_color: v.optional(v.string()),
  border_radius: v.optional(v.string()),
  font_size: v.optional(v.string()),
  order: v.optional(v.number()),
});

export const getButtons = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("sidebar_buttons").order("by", "order", "asc").collect();
  },
});

export const addButton = mutation({
  args: { button: buttonValidator },
  handler: async (ctx, args) => {
    const buttons = await ctx.db.query("sidebar_buttons").collect();
    const maxOrder = Math.max(...buttons.map(b => b.order || 0), 0);
    
    await ctx.db.insert("sidebar_buttons", {
      ...args.button,
      order: maxOrder + 1,
    });
  },
});

export const updateButton = mutation({
  args: { 
    id: v.id("sidebar_buttons"),
    button: buttonValidator 
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, args.button);
  },
});

export const deleteButton = mutation({
  args: { id: v.id("sidebar_buttons") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
```

---

## Testing Checklist

- [ ] Links load on page load
- [ ] Add new link works
- [ ] Edit link updates correctly
- [ ] Delete link removes from UI
- [ ] Reordering persists
- [ ] Group styling applies correctly
- [ ] Sidebar buttons load
- [ ] Notifications still work (external APIs)
- [ ] No console errors
- [ ] Works after page refresh

---

## Troubleshooting

### Links not loading
- Check Convex URL is correct
- Open browser console for errors
- Verify `npx convex dev` is running

### "Function not found" error
- Ensure file is `convex/links.ts`
- Call as `links:getLinks` not `getLinks`
- Check function is exported

### Data not persisting
- Check Convex dashboard for errors
- Verify mutation completed successfully
- Hard refresh browser (Ctrl+Shift+R)

### Old Flask endpoints still called
- Search for `fetch('/api/` in all JS files
- Replace with Convex client calls
- Check browser Network tab for 404s

---

## Production Deployment

1. **Deploy Convex backend:**
   ```bash
   npx convex deploy
   ```

2. **Update HTML with production URL:**
   ```javascript
   const client = new ConvexHttpClient("https://your-prod-url.convex.cloud");
   ```

3. **Deploy frontend to GitHub Pages:**
   - Push `index.html` and `static/` folder
   - Enable GitHub Pages in repo settings
   - Access at `https://username.github.io/repo-name`

4. **No server needed** - Everything runs in browser + Convex cloud

---

## Cost & Limits (Free Tier)

- **40 deployments/month** (only `convex/` changes count)
- **1GB database storage**
- **1M function calls/month**
- **10GB bandwidth/month**

This project will easily fit within free tier limits.
