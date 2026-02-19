# Project Features List

## Core Features
- Link management system with CRUD operations (Create, Read, Update, Delete)
- Sidebar button management with CRUD operations
- JSON-based data storage for links and sidebar buttons
- Auto-generate static HTML file after data updates

## Link Features
- Multiple URL support per link with dynamic URL field management (add/remove URL fields)
- Link grouping with custom group names
- Collapsible groups with toggle functionality at top
- Password-protected group expansion (hardcoded password: "1823")
- Horizontal stack layout option for groups
- Display styles: flex or list-item
- Hide/show individual links (edit mode only)
- Drag-and-drop reordering for links and groups
- Context menu (right-click) with New-Tab, Edit, Copy, Delete options
- Copy link functionality (duplicates link with all properties)
- Delete group functionality (removes entire group with confirmation)

## Link Display Types
- Text display
- NerdFont icons
- Image (URL-based)
- SVG code (inline)

## Link Styling
- Custom text color (solid or gradient with rotate/slide animations)
- Custom background color (solid or gradient with rotate/slide animations)
- Custom border color (solid or animated gradient)
- Custom border radius
- Custom font family and size
- Custom width and height
- Hover color effects
- Item-level background and border styling
- Animated gradient borders with configurable angles

## Group Styling
- Custom group display name (text, NerdFont, or SVG)
- Top group background color (solid or gradient)
- Top group text color (solid or gradient)
- Top group border color (solid or gradient)
- Top group hover color
- Top group width, height, font family, and font size
- Popup content styling (background, text, border colors and radius)
- Horizontal stack styling (separate colors for stacked layout)

## Sidebar Features
- Always-expanded sidebar at top
- Custom sidebar buttons with CRUD operations
- Notification badges on sidebar buttons
- Custom button styling (text color, background, hover, border, radius, font size)
- Display types: icon, image, or SVG
- API integration for notification counts
- Mark-as-seen functionality for notifications
- Auto-refresh notifications every 30 seconds

## Edit Mode
- Toggle edit mode with F1 key
- Show/hide edit controls
- Drag-and-drop reordering in edit mode
- Visual indicators for hidden items
- Edit and delete buttons for links and groups

## Color System
- Support for named colors, hex, rgb, rgba
- Gradient support with multiple colors
- Two animation modes: rotate (fade between colors) and slide (gradient position moves)
- Configurable gradient angles (e.g., 90deg, 180deg)
- Color preview in input fields
- Brightness-based text color adjustment for readability

## External Integrations
(Excluded from Convex version as per requirements)

## File Handling
- Open local files using system default application
- Support for file:// URLs
- URL encoding/decoding for file paths
- Cross-platform file path handling (Windows/Linux/macOS)

## UI/UX Features
- Responsive design
- Mobile-friendly context menus
- Popup forms for adding/editing links and groups
- Close popups with X button or click outside
- Tooltips on links
- Copy notification system with visual feedback
- Color input fields with live preview
- Collapsible settings sections in forms
- NerdFont icon picker with common icons

## Data Management
- Centralized JSON data file
- Automatic data persistence
- Group property inheritance for new links
- Maintain group ordering and consistency
