# Find & Replace Syntax Feature

**Location:** F3 Quick Formatter → 🔄 Button

Replace syntax patterns across an entire cell with a different syntax pattern while preserving the content.

---

## Overview

The Find & Replace Syntax feature allows you to convert one markdown/formatting syntax to another throughout an entire cell. This is useful when you want to change the styling of multiple text segments at once.

**Key Capabilities:**
- **Standard Conversion:** Change `**bold**` to `@@italic@@`.
- **Side-Specific Replacement:** Change only the left or right side of a syntax.
- **Syntax Removal:** Strip markers while keeping the text (e.g., `[text]` → `text`).
- **Smart History:** Quickly re-use your last 5 successful replacements.

---

## How to Use

1. **Select any text** in a cell and press **F3** to open Quick Formatter.
2. Click the **🔄 Find & Replace Syntax** button.
3. **Select or type** the syntax pattern to find (must use `text` as placeholder).
4. **Choose Replacement:**
   - Type a custom pattern in the "Replace With" box.
   - Click a **Quick Button** (Bold, Italic, Red, etc.).
   - Click **Remove Syntax** or leave the box empty to strip the markers.
5. **Select Replace Side:**
   - **Both:** Standard replacement for both delimiters.
   - **Left:** Replaces/Removes only the left side (e.g., `[fff]` → `->fff`).
   - **Right:** Replaces/Removes only the right side.
6. **Preview** the changes in the live preview window.
7. Click **Replace All** to apply.

---

## Interface Components

### Find Syntax Section
- **Dropdown Menu:** Automatically scans the cell and lists detected syntaxes.
- **Manual Input:** Type custom patterns using the `text` placeholder.

### Replace With Section
- **Remove Syntax Button:** Sets replacement to empty for stripping markers.
- **Quick Buttons:** Presets for common highlights and standard syntaxes.
- **Recent History:** Lists the last 5 successful replacements. Click any to re-apply all settings (Find, Replace, and Side).

### Replace Side Toggle
- **Both (Default):** Replaces the entire syntax.
- **Left:** Targets only the left delimiter. Useful for converting `[text]` to `->text`.
- **Right:** Targets only the right delimiter.

### Live Preview
Shows:
- Number of occurrences found.
- Before/after example of the first match.
- Updates in real-time as you change patterns or toggles.

---

## Smart Features

### Content Preservation
The system ensures your text is never lost, even if you forget the `text` placeholder in your replacement:
- In **Left/Both** modes: A replacement like `->` is automatically treated as a prefix (`->text`).
- In **Right** mode: A replacement like `<-` is treated as a suffix (`text<-`).

### History Management
- Stores the last **5 unique replacements**.
- Includes the specific side toggle used.
- Click the **×** on a history item to remove it.

---

## Examples

### Example 1: Brackets to Arrow (Left Only)
- **Find:** `[text]`
- **Replace:** `->`
- **Side:** `Left`
- **Result:** `[fff]` becomes `->fff`

### Example 2: Remove Specific Marker
- **Find:** `**text**`
- **Replace:** (Empty)
- **Side:** `Both`
- **Result:** `**Hello**` becomes `Hello`

### Example 3: Change Color but Keep Bold
- **Find:** `{fg:#ff0000}**text**{/}`
- **Replace:** `==text==`
- **Result:** Red bold text becomes black highlighted text (removes both original markers).

---

## Important Notes

1. **Whole Cell Scope:** Operates on entire cell content, not just selection.
2. **Placeholder Logic:** The `find` pattern **must** contain `text`. The `replace` pattern is optional.
3. **Exclusive Sides:** Selecting "Left" or "Right" results in a single-sided syntax in the output.
4. **Preserves Content:** Content remains intact regardless of marker changes.
5. **Undo:** Changes are applied immediately to the cell - use preview to verify.

---

## Related Features

- **F3 Quick Formatter:** Main formatting interface.
- **🔍➡️ Find & Replace Text:** Literal text replacement tool.
- **🔧 Syntax Inspector:** Reorder nested syntaxes.
- **Custom Syntax Manager:** Add/edit custom syntax markers.
