# Hidden Content Features (Collapsible & Correct Answer)

These two markdown syntaxes work together and are controlled by the same 👁️ button in the toolbar.

## Collapsible Text: `{{hidden text}}`
**Purpose:** Hides text behind individual toggle buttons that can be clicked to show/hide the content.
**Behavior:**
- Each `{{text}}` gets its own 👁️ toggle button
- Click the button to show/hide that specific text
- Useful for hints, explanations, or spoilers

**Implementation:**
- **Parsing:** In `parseMarkdown()`, the regex `/\{\{(.+?)\}\}/g` generates HTML with a button and hidden span
- **Detection:** Added `value.includes('{{')` to `hasMarkdown` checks
- **Stripping:** Added `.replace(/\{\{(.+?)\}\}/g, '$1')` to `stripMarkdown()`
- **CSS:** `.collapsible-wrapper`, `.collapsible-toggle`, `.collapsible-content` styles
- **Quick Formatter:** Added a 👁️ button to wrap selected text with `{{}}`
- **Static Export:** Full support in `export_static.py`

## Correct Answer: `[[correct answer]]`
**Purpose:** Marks correct answers in MCQ tests. Text appears normal until clicked, then reveals with green background.
**Behavior:**
- Text looks completely normal (no visual difference)
- Click the text itself to reveal green background
- Prevents students from identifying correct answers visually

**Implementation:**
- **Parsing:** `[[text]]` -> `<span class="correct-answer">$1</span>`
- **Styling:** Transparent by default, green (#29e372) when `.revealed` class is added
- **Detection:** Added `str.includes('[[')` to `checkHasMarkdown()`
- **Stripping:** Added `.replace(/\[\[(.+?)\]\]/g, '$1')` to `stripMarkdown()`
- **Static Export:** Full support with click-to-reveal behavior

## Global Toggle Button (👁️)
**Location:** Toolbar, next to row numbers and wrap toggles
**Function:** `toggleAllCollapsibles()`
**Behavior:**
- Shows/hides ALL collapsible text (`{{}}`) at once
- Reveals/hides ALL correct answers (`[[]]`) at once
- If any content is visible, clicking hides everything
- If all content is hidden, clicking reveals everything
- Shows alert "No hidden content found" if no `{{}}` or `[[]]` syntax exists

**Key Functions:**
- `toggleAllCollapsibles()` - Global toggle for both syntaxes
- `toggleCollapsible(id)` - Individual toggle for `{{}}` buttons
- Click event listener - Individual toggle for `[[]]` spans
