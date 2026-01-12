# Problems & Fixes Log

This document tracks historical bugs, issues, and their solutions. Use this to:
- Understand past problems and how they were resolved
- Check if old fixes might conflict with new features
- Debug similar issues by referencing past solutions

---

## [2026-01-12] - List Item Tab Alignment & Hanging Indent Issues

**Problem:** 
1. Tab characters within list items (`- item`) weren't aligning properly across different list items
2. When list content wrapped to the next line, it didn't indent to align with text after the bullet
3. Longer words like `সম্প্রসারণ` needed extra tabs to align with shorter words

**Root Cause:**
List items were using `display: inline-flex` with `width: 100%` and `flex: 1` on the content span. Flex containers don't preserve tab alignment the same way as normal text flow.

**Solution:**
Changed list rendering to use:
- `display: inline-block; width: 100%` instead of `display: inline-flex`
- `text-indent: -1em; margin-left: 1em` for proper hanging indent
- `white-space: pre-wrap` on content to preserve tabs
- Added `tab-size: 8` to CSS for consistent tab rendering

**Files Modified:**
- `static/script.js` - List parsing in `oldParseMarkdownBody()` (~line 2253)
- `static/style.css` - Added `tab-size` to `td input`, `td textarea`, `.markdown-preview`
- `export_static.py` - Matching list parsing updates

**Related Issues:** None

---

## [2026-01-12] - Raw Mode Showing Text Twice

**Problem:**
When markdown preview was disabled (raw mode), cell content appeared twice - both the input/textarea and a preview overlay were visible.

**Root Cause:**
The CSS that hid the markdown preview in raw mode was commented out, but the `applyMarkdownFormatting()` function was still creating preview elements even in raw mode.

**Solution:**
Updated `applyMarkdownFormatting()` to check `isMarkdownEnabled` early and:
- Remove existing preview element
- Remove `has-markdown` class from input
- Return early without creating new preview

The CSS `.hide-markdown-preview .markdown-preview { display: none }` was kept commented out since previews are no longer created in raw mode.

**Files Modified:**
- `static/script.js` - Early return in `applyMarkdownFormatting()` (~line 1380)

**Related Issues:** Raw mode cell height (see below)

---

## [2026-01-12] - Raw Mode Cell Height Not Adjusting

**Problem:**
In raw mode (markdown preview disabled), cells weren't expanding to show all content. The last lines of text were cut off.

**Root Cause:**
`adjustCellHeightForMarkdown()` required both an input AND a preview element to exist, and checked for `has-markdown` class. In raw mode, previews are removed and `has-markdown` class is removed, so the function returned early without adjusting height.

**Solution:**
Updated `adjustCellHeightForMarkdown()` to:
1. Check if markdown is enabled
2. In raw mode (no preview), resize textareas based on `scrollHeight` directly
3. Updated `adjustAllMarkdownCells()` to process all textareas in raw mode, not just those with `has-markdown` class

**Files Modified:**
- `static/script.js` - `adjustCellHeightForMarkdown()` (~line 9727), `adjustAllMarkdownCells()` (~line 9798)

**Related Issues:** Raw mode text showing twice (fixed above)

---

## Template for New Entries

```markdown
## [YYYY-MM-DD] - Brief Problem Title

**Problem:** 
Description of the issue observed

**Root Cause:** 
What was actually causing the problem

**Solution:** 
How it was fixed (include key code changes)

**Files Modified:**
- `file1.js` - Brief description of change
- `file2.css` - Brief description of change

**Related Issues:** Links to related problems or "None"
```
