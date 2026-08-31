# Notion Alt — Personal Workspace App

A Notion-like desktop app built with Electron + React + Convex.

## Features

- 📄 **Pages** — Create and organize pages in a tree hierarchy
- 📝 **Rich blocks** — Text, Headings (H1/H2/H3), To-do, Bulleted/Numbered lists, Toggle, Quote, Callout, Code, Divider
- 🖼 **Images** — Insert images from your local file system
- 📊 **Tables** — Inline editable tables with add/remove rows & columns
- 🔍 **Search** — Search pages by title
- ⭐ **Favorites** — Star pages for quick access
- 🗑️ **Trash** — Soft-delete with restore
- 🌓 **Dark/Light theme** — Toggle with a button
- ↕️ **Drag & Drop** — Reorder blocks within a page
- ⚡ **Slash commands** — Type `/` to open block menu
- 🔄 **Real-time sync** — Convex local database

## How to Run

### First time setup:

```bash
npm install --legacy-peer-deps
```

### Start the app (in two terminal windows):

**Terminal 1 — Start Convex backend:**
```bash
npx convex dev
```

**Terminal 2 — Start the Electron app:**
```bash
npx vite
```

Or use the combined command:
```bash
npm run dev
```

### Build for distribution:

```bash
npm run electron:build
```

## Usage

1. Click **New page** or use the `+` button in the sidebar
2. Click the page title to rename it
3. Click the emoji to change the page icon
4. Type `/` in the editor to open the block menu
5. Drag the ⠿ handle to reorder blocks
6. Use the sidebar to navigate pages, favorite them, or delete them
