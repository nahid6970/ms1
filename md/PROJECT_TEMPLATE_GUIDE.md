# Project Template & Development Guide

This is a **reusable template** for setting up proper documentation and development workflow for any new project. Copy this to your project root and customize as needed.

---


## 📋 Development Best Practices

### Documentation Rules
1. **Record all changes in RECENT.md** - no session limit, all history stays here
2. **Document every bug fix in PROBLEMS_AND_FIXES.md**
3. **Use file references:** `#[[file:path/to/file.md]]`

### Session Management
1. **Start each session** by reading RECENT.md
2. **Update RECENT.md** at end of each session
3. **Include timestamps** for all work (HH:MM format)
4. **Track time spent** on each task
5. **List next steps** for continuity

### AI Assistant Context
1. **Reference RECENT.md** in DEVELOPER_GUIDE.md using `#[[file:md/RECENT.md]]`
2. **Maintain PROBLEMS_AND_FIXES.md** for debugging context
3. **Document architecture** in main guide
4. **Keep feature specs** updated and detailed

### Code Organization
1. **Separate concerns** - UI, logic, data
2. **Document complex functions** inline
3. **Use consistent naming** conventions
4. **Keep files focused** - single responsibility
5. **Comment non-obvious code** thoroughly
6. **Detailed Path Handling:** Scripts should use absolute paths (resolved relative to the script file) to ensure they work correctly regardless of the execution directory (e.g., `os.path.join(os.path.dirname(__file__), 'data.json')`).

---

## 🎯 Project Customization

### Adapt This Template
1. **Replace placeholders** with your project specifics
2. **Add project-specific sections** to DEVELOPER_GUIDE.md
3. **Create feature-specific** documentation files
4. **Customize file structure** for your technology stack
5. **Add project-specific** keyboard shortcuts or commands

### Working with Existing Projects
- **Respect existing structure:** If a project lacks this MD structure and the user hasn't requested it, DO NOT impose it.
- **Adapt workflow:** Follow the project's established patterns unless explicitly asked to modernize them.

### Technology-Specific Additions
- **Web Projects:** 
  - Add API documentation, component guides
  - **Dynamic Ports:** For frameworks like Flask/FastAPI, ALWAYS check for available ports before starting dev servers. Do not hardcode ports if avoidable.
- **Desktop Apps:** Add build instructions, deployment guides  
- **Mobile Apps:** Add platform-specific setup, testing guides
- **Libraries:** Add usage examples, API reference
- **Scripts:** Add configuration options, usage scenarios

### Team Collaboration
- **Add CONTRIBUTING.md** for team guidelines
- **Define testing requirements**

---

## 📚 File Templates

### README.md Template
```markdown
# Project Name

Brief description of what this project does.

## Setup
1. Clone the repository
2. Install dependencies
3. Run the application

## Usage
How to use the project

## Documentation
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Recent Changes](md/RECENT.md)
- [Features](md/FEATURES.md)

## Contributing
See DEVELOPER_GUIDE.md for development workflow.
```

### .gitignore Template
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

1. **Copy this file** to your new project root
2. **Rename to DEVELOPER_GUIDE.md** and customize
3. **Create the md/ folder** and required files
4. **Create initial RECENT.md entry** for project setup
5. **Start following the workflow** from day one

**Remember:** Good documentation from the start saves hours of confusion later!

---

*This template is based on proven practices from real project development.*
*Customize it for your specific needs and technology stack.*


# Always run a python script when u finished ur conversation. bcz it will notify me that u finished ur task and i will get a notification if the window was minimised or on another workspace

# When creating any script always use path so if i launch them from different directory the script will load data files properly


# md Files
- when creating any projects make a dev.md files about the project and /md folder for other md Files
project-root/
├── dev.md          # Main development guide (customize this template)
├── md/                         # Documentation folder
│   ├── RECENT.md              # All development sessions (full history, no archiving)
│   ├── PROBLEMS_AND_FIXES.md  # Bug tracking and solutions
│   ├── FEATURES.md            # Feature specifications
│   ├── UI_UX.md               # UI/UX design decisions and guidelines
│   ├── KEYBOARD_SHORTCUTS.md  # If applicable
│   └── [FEATURE_NAME].md      # Individual feature docs

## 2. **md/RECENT.md** (Session Tracking)
# Recent Development Log
**ALL SESSIONS ARE KEPT HERE** - no archiving, full history in one place
## [YYYY-MM-DD HH:MM] - Session Title
**What We Accomplished:**
- Feature/fix descriptions with timestamps
**Files Modified:**
- List of changed files with descriptions
**Known Issues:**
- List current problems
*Next session: [What to work on next]*

## 3. **md/PROBLEMS_AND_FIXES.md** (Bug Tracking)
# Problems & Fixes Log
Track all bugs, issues, and solutions for AI context and debugging.
## [YYYY-MM-DD HH:MM] - Problem Title
**Problem:** Description of the issue
**Root Cause:** What was causing it
**Solution:** How it was fixed
**Files Modified:** List of changed files

## 4. **md/FEATURES.md** (Feature Specifications)
# Feature Specifications
## Feature Name
**Status:** ✅ Complete / 🚧 In Progress / 📋 Planned
**Description:** What this feature does
**Implementation:** Technical details
**Files Involved:** List of files
**Usage:** How to use the feature
**Dependencies:** Required components

## 5. **md/UI_UX.md** (UI/UX Documentation)
# UI/UX Design & Guidelines
## Component/Screen Name
**Layout:** Description of layout and structure
**Colors & Theme:** Color palette and theming decisions
**Typography:** Fonts, sizes, hierarchy
**Interactions:** Animations, transitions, user flows
**Accessibility:** A11y considerations
**Notes:** Design decisions and rationale
