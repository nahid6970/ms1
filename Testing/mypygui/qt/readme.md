# Scroll Issue Fix

## Problem
Items in the grid don't scroll when they exceed the window height - they just get cut off at the window border.

## Root Cause
In `CyberButton.__init__` (around line 46):

```python
self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
```

The vertical `Expanding` policy causes buttons to stretch to fill available space in the scroll area viewport. This prevents the grid container from growing taller than the viewport, so no scrollbar appears.

## Fix
Change the vertical size policy from `Expanding` to `Fixed`:

```python
self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
```

- Horizontal `Expanding` - buttons fill column width (keeps current behavior)
- Vertical `Fixed` - buttons respect their set height, allowing grid to grow and scroll
