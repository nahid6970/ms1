# Web Highlighter Chrome Extension

## Overview
A Chrome extension that allows users to highlight text on any website with customizable colors. Highlights are saved and persist across page reloads. The extension provides a modern, intuitive UI for managing highlights.

## Features
- 🎨 **Text Highlighting**: Select text and choose from preset or custom colors
- 💾 **Persistence**: Highlights are saved per domain and restored on page reload
- 🔄 **Domain-Wide**: Highlights appear on all pages of the same domain
- 🎯 **Context Menu**: Click highlighted text to change color, delete, or open links
- 📤 **Import/Export**: Backup and restore highlights via JSON
- 🔗 **Link Detection**: Automatically detects and provides quick link access

## Project Structure

```
highlight/
├── manifest.json          # Extension configuration
├── background.js          # Service worker (minimal functionality)
├── content.js            # Main highlighting logic (injected into pages)
├── styles.css            # Styling for highlight UI elements
├── popup.html            # Extension popup interface
├── popup.js              # Popup logic (import/export)
└── README.md             # This file
```

## Architecture

### 1. Manifest (manifest.json)
- **Manifest Version**: 3 (latest Chrome extension format)
- **Permissions**: 
  - `storage` - Save highlights to Chrome's local storage
  - `activeTab` - Access current tab content
  - `scripting` - Inject content scripts
- **Host Permissions**: `<all_urls>` - Works on any website
- **Content Scripts**: Automatically injects `content.js` and `styles.css` into all pages

### 2. Content Script (content.js)
The core of the extension. Runs on every webpage.

#### Key Constants
```javascript
const COLORS = ['#ffff00', '#aaffaa', '#aaddff', '#ffaaaa']; // Preset colors
let currentURL = window.location.hostname; // Domain-based storage key
```

#### Important Functions

##### `generateId()`
- Generates unique IDs for each highlight
- Uses random base36 string

##### `getDomPath(element)`
- Creates CSS selector path for elements
- Uses `:nth-of-type()` for specificity
- Enables precise highlight restoration

##### `highlightSelection(color)`
- Main highlighting function
- Creates `<span>` wrapper around selected text
- Saves highlight data to storage
- **Data Structure**:
  ```javascript
  {
    id: string,        // Unique identifier
    text: string,      // Highlighted text content
    color: string,     // Hex color code
    path: string       // CSS selector for parent element
  }
  ```

##### `applyHighlight(h)`
- Restores saved highlights from storage
- **Two-stage restoration**:
  1. Try exact DOM path match
  2. Fallback to full body search
- Prevents double-highlighting via ID check

##### `wrapTextInParent(parent, h)`
- Helper for `applyHighlight`
- Uses `TreeWalker` to find text nodes
- Wraps matched text in styled span

##### `removeHighlight(element)`
- Removes highlight from DOM
- Deletes from storage
- Normalizes parent node to merge text nodes

##### `changeHighlightColor(element, newColor)`
- Updates highlight color in DOM and storage
- Triggered from context menu

##### `findLinkElement(element)`
- Checks if highlight is inside or contains a link
- Used to show "Open Link" button

##### `showColorChangeMenu(highlightElement)`
- Displays color picker in context menu
- Shows preset colors + custom picker

#### UI Components

**Highlight Menu** (`menu`)
- Floating color picker
- Appears above selected text
- Contains preset color buttons + custom color picker

**Context Menu** (`contextMenu`)
- Appears when clicking existing highlights
- Three actions:
  - 🎨 Change Color
  - 🗑️ Delete
  - 🔗 Open Link (if applicable)

#### Event Listeners

1. **mouseup**: Shows highlight menu when text is selected
2. **click**: Shows context menu for existing highlights
3. **Storage restoration**: Loads and applies highlights on page load

### 3. Popup (popup.html + popup.js)
User interface for managing highlights.

#### Functions

##### `showStatus(msg, duration)`
- Displays temporary status messages

##### Export Functionality
- Retrieves all storage data
- Creates downloadable JSON file

##### Import Functionality
- Accepts JSON input
- Validates and loads into storage
- Refreshes affected tabs

##### Clear All
- Deletes all stored highlights
- Sends refresh message to active tab

### 4. Background Script (background.js)
Minimal implementation - only logs installation event.

### 5. Styles (styles.css)
Modern UI styling with:
- Glassmorphism effects
- Gradient backgrounds
- Smooth animations
- Responsive hover states

## Data Storage

### Storage Key Structure
```
{
  "example.com": [
    {
      id: "abc123",
      text: "highlighted text",
      color: "#ffff00",
      path: "body > div:nth-of-type(1) > p:nth-of-type(2)"
    },
    // ... more highlights
  ],
  "another-site.com": [ ... ]
}
```

### Storage Scope
- **Domain-based**: Uses `window.location.hostname`
- All pages on same domain share highlights
- Ignores URL query parameters and hash fragments

## Key Design Decisions

### 1. Domain-Wide Highlights
**Why**: Users often want highlights to persist across different pages of the same site (e.g., job listings, documentation).

**Implementation**: Use `hostname` instead of `href` as storage key.

### 2. Fallback Restoration
**Why**: Page structures change between routes, making exact path matching unreliable.

**Implementation**: Two-stage restoration:
1. Try exact CSS selector (`h.path`)
2. Fallback to body-wide text search

### 3. Text-Based Matching
**Why**: DOM structure can vary, but text content is more stable.

**Limitation**: Multiple identical text strings may cause ambiguity. First match wins.

### 4. Icon-Only Context Menu
**Why**: Cleaner, more modern UX with minimal visual clutter.

**Implementation**: Circular buttons with emoji icons and gradient background.

## Extension Workflow

### Highlighting New Text
1. User selects text → `mouseup` event fires
2. Highlight menu appears with color options
3. User clicks color → `highlightSelection(color)` called
4. Text wrapped in `<span>` with `web-highlighter-span` class
5. Data saved to storage with unique ID

### Restoring Highlights
1. Page loads → content script runs
2. Fetches highlights for current domain from storage
3. For each highlight:
   - Tries to find parent element via CSS path
   - Searches for text within parent (or body as fallback)
   - Wraps text in styled span

### Managing Highlights
1. User clicks highlighted text → context menu appears
2. User selects action:
   - **Change Color**: Shows color picker
   - **Delete**: Removes from DOM and storage
   - **Open Link**: Opens associated URL

### Import/Export
1. User opens popup
2. Click "Export" → Downloads JSON file
3. Click "Import" → Shows textarea
4. Paste JSON → Click "Load Data" → Highlights restored

## Important Notes for AI Assistants

### When Modifying Restoration Logic
- Always check for existing highlights to avoid duplicates
- Use `TreeWalker` with `NodeFilter.SHOW_TEXT` for text node iteration
- Call `parent.normalize()` after DOM manipulation to merge text nodes

### When Adding Features
- Maintain backwards compatibility with existing storage format
- Test across dynamic websites (SPAs, infinite scroll, etc.)
- Consider z-index conflicts with existing page elements

### Common Issues
1. **Cross-element selection**: `range.surroundContents()` fails if selection spans multiple block elements
2. **Dynamic content**: Highlights may not restore on dynamically loaded content (requires MutationObserver)
3. **Security**: Color picker input must be triggered by user gesture

### Storage Limitations
- Chrome local storage limit: ~5MB
- Large highlight datasets may need optimization
- Consider periodic cleanup of old/unused highlights

## Future Enhancement Ideas
- Highlight categories/tags
- Search within highlights
- Sync across devices via Chrome sync storage
- Note-taking on highlights
- Export to PDF with highlights preserved
- Collaborative highlighting
- Keyboard shortcuts
- MutationObserver for dynamic content

## Development Tips

### Testing
1. Load unpacked extension from `chrome://extensions`
2. Test on various website types (static, SPA, etc.)
3. Verify storage updates in DevTools → Application → Storage

### Debugging
- Use `console.log()` in content script (visible in page console)
- Check background script logs in extension's service worker inspector
- Inspect storage: DevTools → Application → Local Storage → Extension

### Common Modifications
- **Add new color**: Update `COLORS` array in `content.js`
- **Change storage scope**: Modify `currentURL` assignment
- **Adjust UI positioning**: Update CSS in `styles.css` or inline styles in `content.js`

## License
Open source - feel free to modify and extend.
