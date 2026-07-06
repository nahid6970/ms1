# UI/UX Design & Guidelines

## Design Philosophy
Dark-themed, compact, power-user focused. Every pixel serves a purpose. Icons over text where possible. Hover-reveal for secondary actions to keep the UI clean.

---

## Color Palette & Theme

### CSS Custom Properties
```css
--bg-main         /* Main background */
--bg-sidebar      /* Sidebar / panel backgrounds */
--bg-card         /* Card / dropdown backgrounds */
--bg-card-hover   /* Card hover state */
--border-color    /* All borders */
--text-primary    /* Primary text */
--text-secondary  /* Secondary / muted text */
--text-muted      /* Very low emphasis text */
--accent-color    /* Primary accent (links, focus states) */
```

### Accent Colors by Function
| Color | Hex | Usage |
|-------|-----|-------|
| Blue | `#3b82f6` | Default accent, links, focus rings |
| Sky Blue | `#38bdf8` | Directory names, project name |
| Purple | `#a78bfa` | Screenshot button, debug features |
| Green | `#10b981` | Success states, git clean, run button hover |
| Yellow | `#fbbf24` | Schedule button, warnings |
| Red | `#ef4444` | Delete hover, errors, kill actions |
| Cyan | `#06b6d4` | Mobile keyboard button |
| Pink | `#f472b6` | Snippets button |

---

## Typography
- **Primary font**: System font stack (customizable via Settings)
- **Monospace font**: `'Fira Code', monospace` — used in terminal, file viewer, code inputs
- **Headings**: `'Outfit', sans-serif` — used in panel headers
- **Font sizes**: Range from `0.68rem` (path labels) to `1.1rem` (modal headers)

---

## Layout Structure

### Main Layout
```
┌──────────────────────────────────────────────┐
│ Sidebar (left, collapsible)                  │
│ ┌──────────┐ ┌─────────────────────────────┐ │
│ │ Workspace│ │ Terminal Panes               │ │
│ │ Cards    │ │ (split: vert/horiz/quad/tab) │ │
│ │          │ │                               │ │
│ └──────────┘ └─────────────────────────────┘ │
│ Status Bar (bottom)                          │
└──────────────────────────────────────────────┘
```

### Sidebar
- Fixed width, collapsible via toggle button
- Contains: workspace selector, toolbar buttons, workspace cards
- Toolbar: explorer, workspace selector, branch info, path opener, bookmarks, split, search, scratchpad, settings, reset

### Status Bar
- Anchored to bottom
- Left: Git info badge (clickable → git modal)
- Right: Screenshot, mobile keyboard, schedule, quick tools, snippets, project name, auto-scroll toggle

---

## Component Patterns

### Modals
- **Overlay**: `.modal-overlay` — full-screen dark backdrop, `z-index: 1000+`
- **Content**: `.modal-content` — centered card with `max-width`, `padding: 24px`, `border-radius: 12px`
- **Show/hide**: `.classList.add('show')` / `.remove('show')`
- **Close**: Click overlay (outside content), ✕ button, or Escape key

### Card-Style Selection (Split Modal Pattern)
```
┌─────────┐ ┌─────────┐
│  Icon   │ │  Icon   │
│  Title  │ │  Title  │
│  Desc   │ │  Desc   │
└─────────┘ └─────────┘
```
- `display: grid; grid-template-columns: 1fr 1fr`
- Each card: `border: 1px solid var(--border-color)`, `border-radius: 10px`
- Hover: `borderColor → accent`, `backgroundColor → card-hover`
- Used for: Split layout selector, Run Script mode selector

### Status Bar Popovers
- Absolute positioned above the status bar
- Class: `.sbpop-*` — consistent styling
- Close button: `.sbpop-close` (✕ in top-right)
- Used for: Schedule, Quick Tools, Snippets, Mobile Input

### Action Buttons (Explorer)
- Hidden by default (`opacity: 0`)
- Revealed on parent row hover (`opacity: 1`)
- Each button: `background:none; border:none;` with SVG icon
- Color change on hover (green=run, blue=view, red=delete)

### Form Inputs
- Class: `.form-input`
- Dark background: `var(--bg-main)`
- Border: `1px solid var(--border-color)` → `var(--accent-color)` on focus
- Border radius: `8px`
- Font: Monospace for code inputs, system font for labels

---

## Interactions & Animations

### Transitions
- **Default**: `all 0.2s` for most interactive elements
- **Sidebar slide**: `left 0.3s cubic-bezier(0.4, 0, 0.2, 1)` for explorer/scratchpad panels
- **Opacity reveal**: `opacity 0.15s` for hover-reveal action buttons
- **Background color**: `background-color 0.15s` for list item hover

### Hover Effects
- Buttons: border color → accent, text color brighten
- List items: background → `var(--bg-card-hover)`
- Action icons: color change (functional colors: green/blue/red)

### Click Feedback
- Modal show/hide with backdrop fade
- Button text momentarily changes (e.g., "Copy" → "✓ Copied")

---

## Mobile Considerations
- **Touch targets**: Minimum 34px height for buttons
- **Mobile controls**: Right-side buttons on terminal panes (ESC, ^C, arrows, custom)
- **Input tray**: Persistent text input for Gboard spacebar-slide cursor movement
- **Status bar**: Compact icons, git dot indicator instead of full text on small screens

---

## Accessibility Notes
- All interactive elements have `title` attributes for tooltips
- SVG icons use `stroke="currentColor"` to inherit text color
- Focus states via `outline` or `border-color` change
- High contrast text on dark backgrounds
- Keyboard shortcuts: Ctrl+F (search), standard terminal keybindings
