# Project Template & Development Guide

This is a **reusable template** for setting up proper documentation and development workflow for any new project. Copy this to your project root and customize as needed.

---



## 🚀 Git Commit Workflow Template

### Commit Rules
- **⛔ CRITICAL: NEVER COMMIT WITHOUT EXPLICIT INSTRUCTION**
  - Some AI models have a bad habit of auto-committing. **THIS IS STRICTLY FORBIDDEN.**
  - You must receive a clear command (e.g., "commit this", "save changes to git") before running `git commit`.
  - Updating documentation does NOT authorize a git commit of code or docs unless requested.
- **Update documentation FIRST** before Git operations
- **One-line commit messages** with emojis
- **Complete sequence:** add → commit → push

### Pre-Commit Documentation Updates
1. **md/RECENT.md** - Current session details
2. **md/PROBLEMS_AND_FIXES.md** - Any bugs fixed
3. **md/FEATURES.md** - New features added
4. **DEVELOPER_GUIDE.md** - Architecture changes
5. **Other relevant docs** - As needed

### Commit Message Emojis
- ✅ Bug fixes and issue resolution
- ⚠️ Known issues or warnings  
- 🎯 New features and implementations
- 📝 Documentation updates
- 🔧 Code improvements and refactoring
- 🧹 Code cleanup and removal
- 🚀 Performance improvements
- 🎨 UI/UX improvements
- 🔒 Security fixes
- 📦 Dependencies and packages
- 🌐 Internationalization
- ♿ Accessibility improvements

### Git Workflow Commands
```bash
git add .
git commit -m "emoji one-line description"
git push
```

---

## 📋 Development Best Practices

### Documentation Rules
1. **Always update docs before committing**
2. **Keep RECENT.md to 5 sessions max**
3. **Archive older sessions, don't delete**
4. **Document every bug fix in PROBLEMS_AND_FIXES.md**
5. **Use file references:** `#[[file:path/to/file.md]]`

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
- **Create issue templates** for GitHub
- **Document code review** process
- **Establish branch naming** conventions
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
4. **Set up Git repository** with proper .gitignore
5. **Create initial RECENT.md entry** for project setup
6. **Start following the workflow** from day one

**Remember:** Good documentation from the start saves hours of confusion later!

---

*This template is based on proven practices from real project development.*
*Customize it for your specific needs and technology stack.*









# Always run a python script when u finished ur conversation. bcz it will notify me that u finished ur task and i will get a notification if the window was minimised or on another workspace

# Commit & md Files
- When i explicitly say to "commit" then u will comiit the changes with 1 line message. Also use emoji etc to make the message look better
- when creating any projects make a dev.md files about the project and /md folder for other md Files
```
project-root/
├── dev.md          # Main development guide (customize this template)
├── md/                         # Documentation folder
│   ├── RECENT.md              # Last 5 development sessions
│   ├── ARCHIVE_RECENT.md      # Older sessions archive
│   ├── PROBLEMS_AND_FIXES.md  # Bug tracking and solutions
│   ├── FEATURES.md            # Feature specifications
│   ├── KEYBOARD_SHORTCUTS.md  # If applicable
│   └── [FEATURE_NAME].md      # Individual feature docs


## 🔄 Recent Work Log (CRITICAL FOR SESSION CONTINUITY)
Maintain `md/RECENT.md` with last 5 sessions for AI context.

## 📋 Problems & Fixes Log
Document all bugs and solutions in `md/PROBLEMS_AND_FIXES.md`.

## Feature Documentation Index
- [List your feature documentation files]

#### 2. **md/RECENT.md** (Session Tracking)
```markdown
# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older to ARCHIVE_RECENT.md

---

## [YYYY-MM-DD HH:MM] - Session Title

**Session Duration:** X hours

**What We Accomplished:**
- Feature/fix descriptions with timestamps

**Files Modified:**
- List of changed files with descriptions

**Next Steps:**
- Planned improvements

**Current Status:**
- Working features
- Known issues

**Known Issues:**
- List current problems

---

*Next session: [What to work on next]*
```

#### 3. **md/PROBLEMS_AND_FIXES.md** (Bug Tracking)
```markdown
# Problems & Fixes Log

Track all bugs, issues, and solutions for AI context and debugging.

---

## [YYYY-MM-DD HH:MM] - Problem Title

**Problem:** Description of the issue

**Root Cause:** What was causing it

**Solution:** How it was fixed

**Files Modified:** List of changed files

**Related Issues:** Connected problems

**Result:** Outcome and verification

---
```

#### 4. **md/FEATURES.md** (Feature Specifications)
```markdown
# Feature Specifications

## Feature Name
**Status:** ✅ Complete / 🚧 In Progress / 📋 Planned

**Description:** What this feature does

**Implementation:** Technical details

**Files Involved:** List of files

**Usage:** How to use the feature

**Dependencies:** Required components

---
```

#### 5. **md/ARCHIVE_RECENT.md** (Session Archive)
```markdown
# Archived Development Sessions

Older sessions moved from RECENT.md to maintain focus.

---

## ARCHIVED [YYYY-MM-DD HH:MM] - Session Title
[Same format as RECENT.md but with ARCHIVED prefix]

---
```

---

# When creating any script always use path so if i launch them from different directory the script will load data files properly

#