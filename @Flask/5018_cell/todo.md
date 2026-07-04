# Task: Fix Zoom Scale Not Applying Correctly After Sheet Switch

## Problem
When zoom is set to something other than 100%, switching sheets shows text at the wrong size (too small or too large). Refreshing fixes it. The issue is in `#headerRow > th:nth-of-type(2) > div > span:nth-of-type(1)` (the `fontSizeDisplay` span and zoom controls).

## Root Cause
`applyFontSizeScale()` was called synchronously at the end of `renderTable()` before the browser had computed layout for the freshly-appended DOM elements. `getComputedStyle(cell).fontSize` returns `0` or stale values on newly-appended elements, causing font to be set to `0px`. Additionally, `switchSheet` had a redundant `setTimeout(() => applyFontSizeScale(), 0)` call that could cause double-scaling.

## Tasks
- [X] Fix `applyFontSizeScale()` to use `requestAnimationFrame` so it runs after browser layout is computed
- [X] Fix `applyFontSizeScale()` to be idempotent — divide out previous scale before applying new scale (like `adjustFontSize` already does) to prevent double-scaling
- [X] Remove the redundant `setTimeout(() => applyFontSizeScale(), 0)` in `switchSheet` since `renderTable` already handles it
