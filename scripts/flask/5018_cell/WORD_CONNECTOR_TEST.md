# Word Connector Feature Test

## Syntax
```
[number]Word
```
- Use `[1]`, `[2]`, `[3]`, etc. before words
- Same number = words get connected with colored bracket line
- Line appears below text, connecting from center of each word

## Test Cases

### Test 1: Simple Connection
```
[1]Subject some words here [1]Verb
```
Expected: Blue bracket line connecting "Subject" and "Verb"

### Test 2: Multiple Connections
```
[1]Word1 some text [1]Word2 and more [2]Word3 here [2]Word4
```
Expected:
- Blue line connecting Word1 and Word2
- Red line connecting Word3 and Word4

### Test 3: Three Words Connected
```
[1]First some [1]Second more [1]Third
```
Expected: Blue lines connecting all three words in sequence

### Test 4: Different Colors
```
[1]Blue [2]Red [3]Green [4]Orange [5]Purple
```
Each number gets a different color automatically!

## Color Scheme
- [1] → Blue (#007bff)
- [2] → Red (#dc3545)
- [3] → Green (#28a745)
- [4] → Orange (#fd7e14)
- [5] → Purple (#6f42c1)
- [6] → Teal (#20c997)
- [7] → Pink (#e83e8c)
- [8] → Cyan (#17a2b8)
- [9+] → Cycles back to blue

## Implementation Details

✅ **Implemented in:**
1. static/script.js - parseMarkdownInline()
2. static/script.js - oldParseMarkdownBody()
3. static/script.js - checkHasMarkdown()
4. static/script.js - stripMarkdown()
5. static/script.js - drawWordConnectors() function
6. export_static.py - parseMarkdownInline()
7. export_static.py - oldParseMarkdownBody()
8. export_static.py - hasMarkdown detection
9. export_static.py - stripMarkdown()
10. export_static.py - drawWordConnectors() function
11. static/style.css - .word-connector styles
12. templates/index.html - Markdown Guide

## How It Works

1. **Parsing**: `[1]Word` → `<span class="word-connector" data-conn-id="1" data-conn-color="#007bff">Word</span>`
2. **Drawing**: JavaScript finds all connectors with same ID and draws SVG bracket lines between them
3. **Positioning**: Lines are drawn from center of each word, positioned below the text
4. **Colors**: Each connection ID gets a unique color from the palette

## Features
- ✅ Works in both live app and static export
- ✅ Multiple connections in same sentence
- ✅ Auto-colored by connection number
- ✅ Bracket lines positioned at word centers
- ✅ Search/sort strips the markers correctly
