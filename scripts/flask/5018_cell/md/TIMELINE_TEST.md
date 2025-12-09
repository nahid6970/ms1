# Timeline Feature Test

## Test Case 1: Basic Timeline (Top-aligned)
```
Timeline*Event Name
- First item
- Second item
- Third item
```

Expected Output:
- Left column: "Event Name" (bold, 150px wide, top-aligned)
- Middle: Vertical line separator (2px, gray)
- Right column: Bullet list with items

## Test Case 2: Centered Timeline
```
TimelineC*Centered Event
- Item 1
- Item 2
```

Expected Output:
- Same as above but vertically centered (align-items: center)

## Test Case 3: Timeline with Sub-items
```
Timeline*Main Event
- Main item 1
-- Sub item 1
-- Sub item 2
- Main item 2
```

Expected Output:
- Should show both • and ◦ bullets properly aligned

## Test Case 4: Multiple Timelines
```
Timeline*Event 1
- Item A
- Item B

Timeline*Event 2
- Item C
- Item D
```

Expected Output:
- Two separate timeline blocks, each properly closed

## Implementation Checklist (Rule of 6):

✅ 1. **static/script.js - parseMarkdownInline()**: Added Timeline regex parsing
✅ 2. **static/script.js - oldParseMarkdownBody()**: Added Timeline regex parsing
✅ 3. **static/script.js - checkHasMarkdown()**: Added `str.match(/^Timeline(?:C)?\*/m)`
✅ 4. **static/script.js - stripMarkdown()**: Added Timeline stripping
✅ 5. **export_static.py - parseMarkdownInline()**: Added Timeline parsing
✅ 6. **export_static.py - oldParseMarkdownBody()**: Added Timeline parsing
✅ 7. **export_static.py - hasMarkdown**: Added Timeline detection
✅ 8. **export_static.py - stripMarkdown()**: Added Timeline stripping
✅ 9. **static/style.css**: Added .md-timeline CSS classes
✅ 10. **templates/index.html**: Added to Markdown Guide
✅ 11. **DEVELOPER_GUIDE.md**: Documented the feature

## How to Test:

1. Open the app
2. Create a new cell
3. Type:
   ```
   Timeline*My Event
   - Item 1
   - Item 2
   ```
4. Click outside the cell
5. Verify the timeline layout appears with:
   - "My Event" on the left (bold, 150px)
   - Vertical gray line in the middle
   - Bullet list on the right

6. Test search/sort to ensure stripMarkdown works
7. Export static HTML and verify it works there too
