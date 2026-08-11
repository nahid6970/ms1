# Separator Background Color Test Cases

## Test 1: Basic Background Color
```
Normal text here
-----R
This should have RED background
More red background text
```

**Expected:** Text after `-----R` has red background.

---

## Test 2: Ending Background Color
```
Normal text
-----G
Green background text
-----
Back to normal (no background)
```

**Expected:** Green background starts after first separator, ends at second separator.

---

## Test 3: Multiple Color Sections
```
Normal text
-----R
Red background section
-----B
Blue background section
-----Y
Yellow background section
-----
Back to normal
```

**Expected:** Each section has its respective background color, last separator ends all coloring.

---

## Test 4: Colored Separator Line + Background
```
Normal text
R-----G
Red separator line + Green background below
More green background
```

**Expected:** Red separator line, green background for content below.

---

## Test 5: Combined Features
```
Normal text
G-----R
Green separator line + Red background
Red background continues
B-----Y
Blue separator line + Yellow background
Yellow background continues
-----
End all backgrounds
```

**Expected:** Each separator has its line color, content below has different background color.

---

## Test 6: Just Colored Separator (Existing Feature)
```
Normal text
R-----
Just a red separator line (no background change)
Normal text continues
```

**Expected:** Red separator line only, no background color change.

---

## Test 7: All Colors
```
-----R
Red background
-----G
Green background
-----B
Blue background
-----Y
Yellow background
-----O
Orange background
-----P
Purple background
-----C
Cyan background
-----W
White background
-----K
Black background
-----GR
Gray background
-----
End
```

**Expected:** Each color code produces correct background color.

---

## Test 8: With Other Markdown
```
Normal text
-----R
**Bold text** with red background
@@Italic text@@ with red background
##Heading## with red background
-----
Normal text
```

**Expected:** All markdown formatting works inside colored background sections.

---

## Test 9: With Tables
```
-----B
Table*2
Name, Age
John, 25
Jane, 30
-----
Normal text
```

**Expected:** Table renders with blue background.

---

## Test 10: Nested Separators
```
Text 1
-----R
Red section 1
-----G
Green section (red ends, green starts)
-----B
Blue section (green ends, blue starts)
-----
All colors end
```

**Expected:** Each new colored separator closes previous background and starts new one.

---

## Test 11: No Gap After Separator
```
R-----G
Immediate text after separator
```

**Expected:** No large gap between separator and text below.

---

## Test 12: Multiple Lines in Color Section
```
-----R
Line 1 with red background
Line 2 with red background
Line 3 with red background
-----
Normal
```

**Expected:** All three lines have red background with proper line spacing.

---

## Test 13: Custom Hex Background
```
Normal text
-----#ffcc00
Custom yellow background
More custom colored text
-----
Normal
```

**Expected:** Content has custom hex background color #ffcc00.

---

## Test 14: Custom Hex Background + Text Color
```
Normal text
-----#2c3e50-#ecf0f1
Dark blue background with light gray text
Custom colors for readability
-----
Normal
```

**Expected:** Dark blue background (#2c3e50) with light gray text (#ecf0f1).

---

## Test 15: Colored Separator + Custom Hex
```
R-----#1a1a1a-#ffffff
Red separator line
Black background with white text
High contrast
-----
Normal
```

**Expected:** Red separator line, then black background with white text.

---

## Test 16: Multiple Custom Hex Colors
```
-----#ffebee-#c62828
Light red bg, dark red text
-----#e8f5e9-#2e7d32
Light green bg, dark green text
-----#e3f2fd-#1565c0
Light blue bg, dark blue text
-----
End
```

**Expected:** Each section has its custom background and text colors.

---

## Test 17: Hex Without Text Color
```
-----#ff9800
Orange background only
Text color unchanged
-----
Normal
```

**Expected:** Orange background, default text color.

---

## Color Reference
- **R** = Red (#ff0000)
- **G** = Green (#00ff00)
- **B** = Blue (#0000ff)
- **Y** = Yellow (#ffff00)
- **O** = Orange (#ff8800)
- **P** = Purple/Magenta (#ff00ff)
- **C** = Cyan (#00ffff)
- **W** = White (#ffffff)
- **K** = Black (#000000)
- **GR** = Gray (#808080)
