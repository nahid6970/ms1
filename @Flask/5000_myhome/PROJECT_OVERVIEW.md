# MyHome Dashboard Project

A sophisticated, highly customizable personal home dashboard built with Flask and modern web technologies. This project serves as a central hub for various local services, links, and personal notes, featuring a unique cyberpunk/neon aesthetic.

## 🚀 Current Features

### 1. Central Hub & Dashboard
- **Dynamic Link Management**: Organize your favorite services and tools with custom links.
- **Grouping & Categorization**: Group related links together with support for:
  - Collapsible groups.
  - Custom group styling (colors, borders, backgrounds).
  - Horizontal or vertical stacking.
  - Password protection for sensitive groups.
- **Rich Visuals**: Support for Nerd Fonts, custom images, SVG icons, and CSS gradients.

### 2. Sidebar Controls
- **Custom Sidebar Buttons**: Configurable buttons at the top/sidebar for quick access to main applications.
- **Notification Badges**: Real-time notification counters fetched from external APIs (e.g., TV show and Movie services).
- **Mark as Seen**: Integrated functionality to clear notifications directly from the dashboard.

### 3. Integrated Services
- **External Service Scanners**: Trigger media scans for TV shows and Movies hosted on other local ports.
- **Local File Access**: Specialized API to open local files on the host machine directly from the web interface.
- **Static Site Generation**: Capability to "bake" the dynamic dashboard into a standalone static HTML file for portable use.

### 4. Note Taking & Markdown
- **Markdown Notes**: Attach notes to links with full Markdown support.
- **Live Preview**: Dedicated Markdown previewer to see rendered notes before saving.
- **Markdown Tables**: Support for rendering complex Markdown tables within the dashboard.

### 5. Advanced UI/UX
- **Edit Mode**: Toggleable edit mode (via `F1` key) for rearranging and managing content.
- **Drag & Drop**: Reorder links and groups intuitively.
- **Context Menus**: Custom right-click menus for quick editing and management.
- **Live Color Previews**: Input fields for colors provide immediate visual feedback.
- **Cyberpunk Aesthetic**: High-contrast, neon-styled interface with smooth transitions and glassmorphism elements.

---

## 🛠 Planned Transition to Convex

The next phase of this project involves migrating from a Flask/JSON-file backend to **Convex**, a powerful backend-as-a-service.

### Key Benefits of Convex Migration:
- **Real-time Synchronization**: Every change made by one client will instantly reflect across all open dashboard instances without refreshing.
- **Robust Database**: Replace `data.json` and `sidebar_buttons.json` with a managed document database.
- **Serverless Functions**: Move backend logic (link CRUD, grouping logic) to Convex Functions (Query, Mutation, Action).
- **Automatic Scaling**: No need to manage a local Flask server for multi-user/multi-device environments.
- **Built-in Auth**: Easier implementation of user accounts and private dashboards.
- **Simplified File Storage**: Use Convex's built-in file storage for icons and images.

### Transition Roadmap:
1. **Schema Definition**: Define Convex tables for `links`, `sidebarButtons`, and `settings`.
2. **Data Migration**: Create a script to import existing JSON data into Convex.
3. **Frontend Integration**: Replace `fetch` calls in `main.js` and `links-handler.js` with Convex `useQuery` and `useMutation` (or the JavaScript client equivalent).
4. **Notification Refactoring**: Use Convex Actions to fetch notification counts from external APIs and push updates to the UI.
5. **Static Generation 2.0**: Update the generation script to pull data from Convex via the HTTP API.
