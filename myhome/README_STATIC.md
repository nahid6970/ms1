# Static HTML Generator for MyHome

This project includes functionality to generate a standalone static HTML file (`myhome.html`) that can be uploaded to GitHub Pages or any static hosting service.

## Features

### 🔄 **Automatic Generation**
- Static HTML is automatically generated whenever you make changes through the web interface
- Updates happen in real-time when you add, edit, or delete links

### 📁 **Manual Generation**
- Run `python generate_static.py` to manually generate the static HTML
- Visit `http://localhost:5000/generate-static` to trigger generation via web interface

### 🌐 **Static HTML Features**
- **Fully Standalone**: All CSS and JavaScript embedded
- **All Functionality**: Collapsible groups, custom colors, drag & drop (view-only)
- **GitHub Pages Ready**: Upload `myhome.html` directly to your repository
- **No Server Required**: Works completely offline
- **Edit Mode Disabled**: Clean interface for public viewing

## Usage

### For GitHub Pages:
1. Make changes in your local MyHome interface
2. The `myhome.html` file is automatically updated
3. Commit and push `myhome.html` to your GitHub repository
4. Enable GitHub Pages in repository settings
5. Your homepage is live!

### Manual Generation:
```bash
# Generate static HTML manually
python generate_static.py
```

### Web Interface Generation:
Visit: `http://localhost:5000/generate-static`

## File Structure
```
myhome/
├── app.py                 # Main Flask application
├── generate_static.py     # Static HTML generator
├── myhome.html           # Generated static HTML (auto-updated)
├── templates/
│   └── index.html        # Template for dynamic version
└── static/
    ├── style.css         # Embedded in static version
    ├── main.js           # Embedded in static version
    └── links-handler.js  # Embedded in static version
```

## What's Included in Static Version

✅ **All Visual Features**:
- Collapsible top groups with custom colors
- Horizontal expansion layout
- Custom group names and styling
- Responsive design

✅ **Interactive Features**:
- Group expand/collapse
- Hover effects
- Link navigation

❌ **Disabled in Static Version**:
- Edit mode toggle (hidden)
- Add/edit/delete buttons
- Drag & drop functionality
- Settings panels

## GitHub Pages Setup

1. **Create Repository**: Create a new repository or use existing one
2. **Upload File**: Add `myhome.html` to your repository
3. **Enable Pages**: Go to Settings → Pages → Source: Deploy from branch
4. **Select Branch**: Choose main/master branch
5. **Access**: Your site will be available at `https://username.github.io/repository-name/myhome.html`

## Auto-Update Workflow

1. **Make Changes**: Use your local MyHome interface to add/edit links
2. **Auto-Generate**: `myhome.html` updates automatically
3. **Git Commit**: Commit the updated file
4. **Push**: Push to GitHub
5. **Live Update**: GitHub Pages automatically updates

## Customization

The static generator reads from:
- `data.json` - Your links and settings
- `templates/index.html` - HTML structure
- `static/style.css` - Styling
- `static/*.js` - JavaScript functionality

Any changes to these files will be reflected in the next generation.

---

**Generated**: This file is automatically updated when you generate static HTML.
**Last Updated**: Check the timestamp in the generated `myhome.html` file.