# Project Template & Development Guide

This is a **reusable template** for setting up proper documentation and development workflow for any new project. Copy this to your project root and customize as needed.

---

## 📁 Project Structure

```
project-root/
├── dev.md                      # Main development guide
├── md/                         # Documentation folder
│   ├── RECENT.md               # All development sessions (full history, no archiving)
│   ├── PROBLEMS_AND_FIXES.md   # Bug tracking and solutions
│   ├── FEATURES.md             # Feature specifications
│   ├── UI_UX.md                # UI/UX design decisions and guidelines
│   ├── KEYBOARD_SHORTCUTS.md   # If applicable
│   └── [FEATURE_NAME].md       # Individual feature docs
```

---

## 📋 MD File Templates

### dev.md / DEVELOPER_GUIDE.md
Main guide for the project. Document architecture, setup, and link to other md files using `#[[file:md/RECENT.md]]`.

### md/RECENT.md
```
# Recent Development Log
All sessions recorded here — no archiving, full history in one place.
When giving AI context, reference only the last 5 sessions to avoid overloading context.

## [YYYY-MM-DD HH:MM] - Session Title
**What We Accomplished:**
- Feature/fix descriptions with timestamps
**Files Modified:**
- List of changed files
**Known Issues:**
- List current problems
*Next session: [What to work on next]*
```

### md/PROBLEMS_AND_FIXES.md
```
# Problems & Fixes Log
## [YYYY-MM-DD HH:MM] - Problem Title
**Problem:** Description of the issue
**Root Cause:** What was causing it
**Solution:** How it was fixed
**Files Modified:** List of changed files
```

### md/FEATURES.md
```
# Feature Specifications
## Feature Name
**Status:** ✅ Complete / 🚧 In Progress / 📋 Planned
**Description:** What this feature does
**Implementation:** Technical details
**Files Involved:** List of files
**Usage:** How to use the feature
**Dependencies:** Required components
```

### md/UI_UX.md
```
# UI/UX Design & Guidelines
## Component/Screen Name
**Layout:** Description of layout and structure
**Colors & Theme:** Color palette and theming decisions
**Typography:** Fonts, sizes, hierarchy
**Interactions:** Animations, transitions, user flows
**Accessibility:** A11y considerations
**Notes:** Design decisions and rationale
```

---

## 📋 Development Best Practices

### Documentation Rules
1. **Record all changes in RECENT.md** — full history, no archiving
2. **When giving AI context from RECENT.md**, only reference the last 5 sessions to keep context lean
3. **Document every bug fix in PROBLEMS_AND_FIXES.md**
4. **Use file references:** `#[[file:path/to/file.md]]`

### Session Management
1. **Start each session** by reading RECENT.md
2. **Update RECENT.md** at end of each session
3. **Include timestamps** for all work (HH:MM format)
4. **Track time spent** on each task
5. **List next steps** for continuity

### Code Organization
1. **Separate concerns** — UI, logic, data
2. **Document complex functions** inline
3. **Use consistent naming** conventions
4. **Keep files focused** — single responsibility
5. **Comment non-obvious code** thoroughly
6. **Use absolute paths** in scripts (resolved relative to the script file) so they work from any directory:
   `os.path.join(os.path.dirname(__file__), 'data.json')`

---

## 🎯 Project Customization

### Adapt This Template
1. **Replace placeholders** with your project specifics
2. **Add project-specific sections** to dev.md
3. **Create feature-specific** documentation files
4. **Customize file structure** for your technology stack

### Working with Existing Projects
- **Respect existing structure:** If a project lacks this MD structure and the user hasn't requested it, DO NOT impose it.
- **Adapt workflow:** Follow the project's established patterns unless explicitly asked to modernize them.

### Technology-Specific Additions
- **Web Projects:** Add API documentation, component guides. Always check for available ports before starting dev servers — do not hardcode ports.
- **Desktop Apps:** Add build instructions, deployment guides
- **Mobile Apps:** Add platform-specific setup, testing guides
- **Libraries:** Add usage examples, API reference
- **Scripts:** Add configuration options, usage scenarios

---

## 📚 File Templates

### README.md
```markdown
# Project Name

Brief description of what this project does.

## Setup
1. Clone the repository
2. Install dependencies
3. Run the application

## Usage
How to use the project

## Contributing
See dev.md for development workflow.
```

### .gitignore
```
# Dependencies
node_modules/
__pycache__/
*.pyc

# Environment
.env
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Build
dist/
build/
*.min.js
*.min.css
```

---

## 🎉 Getting Started

1. **Copy this file** to your new project root as `dev.md`
2. **Create the `md/` folder** and required files
3. **Create initial RECENT.md entry** for project setup
4. **Start following the workflow** from day one

**Remember:** Good documentation from the start saves hours of confusion later!

---

*This template is based on proven practices from real project development.*
*Customize it for your specific needs and technology stack.*
