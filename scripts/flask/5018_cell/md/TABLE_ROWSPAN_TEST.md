# Table Rowspan Test Cases

## Test 1: Basic Pipe Table Rowspan

|Header1|Header2|Header3|Header4|
|---|---|---|---|
|Row1Col1|Row1Col2|Row1Col3|Row1Col4|
|Row2Col1|Row2Col2|^^|^^|

Expected: Columns 3 and 4 of Row1 should span both Row1 and Row2.

---

## Test 2: Basic Comma Table Rowspan

Table*4
Header1, Header2, Header3, Header4,
Row1Col1, Row1Col2, Row1Col3, Row1Col4,
Row2Col1, Row2Col2, ^^, ^^

Expected: Same as Test 1 - columns 3 and 4 span two rows.

---

## Test 3: Multiple Consecutive Rowspans

|Name|Age|City|Country|
|---|---|---|---|
|Alice|25|NYC|USA|
|Bob|30|^^|^^|
|Charlie|35|^^|^^|

Expected: "NYC" and "USA" cells span three rows (Alice, Bob, and Charlie).

---

## Test 4: Mixed Rowspans

|Col1|Col2|Col3|
|---|---|---|
|A1|B1|C1|
|A2|^^|C2|
|A3|B3|^^|

Expected:
- B1 spans rows 1-2
- C2 spans rows 2-3

---

## Test 5: Rowspan with Colors

|:R-A:Name|:G-A:Age|:B-A:City|
|---|---|---|
|Alice|25|NYC|
|Bob|30|^^|

Expected: Red, green, and blue column borders with "NYC" spanning two rows.

---

## Test 6: Rowspan with Alignment

|:Name:|Age:|:City:|
|---|---|---|
|Alice|25|NYC|
|Bob|30|^^|

Expected: Center-aligned Name, right-aligned Age, center-aligned City with "NYC" spanning.

---

## Test 7: Complex Table with All Features

|:R-A::Header1:|:G-A:Header2|:B-A::Header3:|
|---|---|---|
|**Bold**|@@Italic@@|Normal|
|Text1|Text2|^^|
|Text3|^^|^^|

Expected: Colored headers with alignment, formatted text, and complex rowspan pattern.

---

## Test 8: Comma Table with Multiple Rowspans

Table*3
Name, Age, City,
Alice, 25, NYC,
Bob, ^^, ^^,
Charlie, ^^, LA

Expected:
- Age "25" spans Alice and Bob
- City "NYC" spans Alice and Bob
- City "LA" is in Charlie's row

---

## Test 9: Empty Cell Marker with Rowspan

|Col1|Col2|Col3|
|---|---|---|
|A1|-|C1|
|A2|^^|^^|

Expected: Col2 shows empty marker (-) spanning two rows, Col3 "C1" spans two rows.

---

## Test 10: Single Column Rowspan

|Name|
|---|
|Alice|
|^^|
|^^|

Expected: "Alice" spans three rows in a single-column table.
