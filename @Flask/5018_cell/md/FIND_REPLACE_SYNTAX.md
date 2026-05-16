# Find & Replace Syntax Feature

**Location:** F3 Quick Formatter → 🔄 Button

Replace syntax patterns across an entire cell with a different syntax pattern while preserving the content.

---

## Overview

The Find & Replace Syntax feature allows you to convert one markdown/formatting syntax to another throughout an entire cell. This has been enhanced into a powerful **Template Engine** that supports multiple capture groups.

**Key Capabilities:**
- **Numbered Placeholders (Templates):** Capture multiple parts of a line using `text1`, `text2`, etc.
- **Side-Specific Replacement:** Change only the left or right side of a syntax.
- **Syntax Removal:** Strip markers while keeping the text (e.g., `[text]` → `text`).
- **Smart History:** Quickly re-use your last 5 successful replacements.
- **Greedy End-Matching:** Placeholders at the end of a pattern automatically capture the remainder of the line.

---

## How to Use

1. **Select any text** in a cell and press **F3** to open Quick Formatter.
2. Click the **🔄 Find & Replace Syntax** button.
3. **Select or type** the syntax pattern to find.
   - Use `text` or `text1` for a single capture.
   - Use `text1`, `text2`, etc., for multiple parts (e.g., `text1 -> text2`).
4. **Choose Replacement (Template):**
   - Type a custom template using the placeholders (e.g. `text1 (text2)`).
   - Click a **Quick Button** (Bold, Italic, Red, etc.).
   - Click **Remove Syntax** or leave the box empty to strip the markers.
5. **Select Replace Side:**
   - **Both:** Standard replacement for both delimiters.
   - **Left:** Exclusive replacement of the left side (removes original right side).
   - **Right:** Exclusive replacement of the right side (removes original left side).
6. **Preview** the changes in the live preview window.
7. Click **Replace All** to apply.

---

## Template Engine Logic

### Numbered Placeholders
You can use up to 9 numbered placeholders (`text1` through `text9`) in your search pattern.
- **Search Pattern:** `id: text1 | name: text2`
- **Replace Template:** `User #text1 is text2`
- **Result:** `id: 123 | name: John` becomes `User #123 is John`.

### Greedy vs. Non-Greedy
- **Middle Placeholders:** Are "non-greedy" (`(.*?)`). They stop at the first occurrence of the next part of your pattern.
- **End Placeholders:** If a placeholder is at the very end of your "Find" pattern, it becomes "greedy" (`(.*)`). This ensures it captures everything until the end of the line (crucial for translations and trailing text).

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

### Example 1: Translation Formatting (Greedy End)
- **Original:** `To Genuflect -> সম্মান প্রদর্শন`
- **Find:** `text1 -> text2`
- **Replace:** `text1 (text2)`
- **Result:** `To Genuflect (সম্মান প্রদর্শন)`

### Example 2: Brackets to Arrow (Left Only)
- **Find:** `[text]`
- **Replace:** `->`
- **Side:** `Left`
*Result: `[fff]` becomes `->fff` (the right bracket is removed because "Left" mode is exclusive).*

---

## Important Notes

1. **Whole Cell Scope:** Operates on entire cell content.
2. **Exclusive Sides:** Selecting "Left" or "Right" results in a single-sided syntax.
3. **Regex Escaping:** The system automatically escapes special characters in your patterns, so you can search for things like `[`, `(`, or `$` without manually escaping them.
