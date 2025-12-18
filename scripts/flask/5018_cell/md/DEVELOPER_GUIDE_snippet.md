
### Dynamic Cursor & Click-to-Edit
**Purpose:** Improves the editing experience in cells with rendered markdown by ensuring precise cursor placement and visibility.

**Problem:** 
- Markdown cells display a *rendered preview* overlay on top of the raw text input.
- Clicking on the rendered preview (e.g., "Big Text") typically focuses the input at the *end* or an incorrect position because the rendered text size/layout differs from the raw markdown syntax characters.
- The default system cursor is often thin and hard to see in dense text.

**Solution Implementation:**
1.  **Smart Click Positioning (`handlePreviewMouseDown`):**
    - **Trigger:** Intercepts `mousedown` events on the `.markdown-preview` overlay.
    - **Logic:**
        - Prevents default browser focus (which causes jumping).
        - Identifies the exact text node and character offset clicked in the preview.
        - Calculates the "N-th occurrence" of that text segment in the preview.
        - Maps this to the corresponding N-th occurrence in the **raw markdown source** in the hidden input.
        - Synchronously focuses the input and sets `selectionStart` / `selectionEnd` to the calculated index.
        - Uses `focus({ preventScroll: true })` to stop the browser from scrolling wildly.
    - **Result:** Clicking a word in the preview places the cursor exactly at that word in the raw markdown.

2.  **Custom Block Cursor:**
    - **Visuals:** Replaces the native thin cursor (hidden via `caret-color: transparent`) with a **5px thick black blinking block** (`.custom-cursor`).
    - **Positioning (`updateCustomCursor`):**
        - Uses a "Mirror Element" technique: Creates an invisible duplicate of the textarea with identical font/wrapping styles.
        - Inserts text up to the cursor position into the mirror.
        - Appends a marker element (`|`) to find the exact pixel coordinates of the end of the text.
        - Calculates the **Absolute Document Position** by combining:
            - Mirror Element Position (Document Relative)
            - Internal Text Scrolloffset (`input.scrollTop`)
            - Window Scroll Position (`window.scrollY`)
        - Updates on `input`, `click`, `scroll` (window & element), and `selectionchange` events.
    - **Visibility:** Automatically hides if the cursor moves out of the visible viewport of the scrolling text box.

3.  **Scroll Stabilization:**
    - Uses `keepCursorCentered(textarea)` to manually scroll the textarea so the cursor line is always vertically centered after a click, ensuring the user immediately sees their edit point.
