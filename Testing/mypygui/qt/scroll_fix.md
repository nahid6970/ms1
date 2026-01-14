# Height & Scroll Comparison: old_version.py vs script_manager_gui_qt.py

## Key Differences Found

### 1. CyberButton Size Policy

**Old (working):**
```python
self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
```

**New (broken):**
```python
self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
```

### 2. CyberButton Default Height Fallback

**Old (working):**
```python
if h > 0: self.setFixedHeight(h)
else: self.setMinimumHeight(45)
```

**New (broken):**
```python
if h > 0: self.setFixedHeight(h)
# Global default height is handled in refresh_grid for consistency
```

The new version removed `setMinimumHeight(45)` fallback.

### 3. refresh_grid Height Logic

**Old (working - simple):**
```python
btn = CyberButton(script.get("name", "Unnamed"), script_data=script)

# Apply dynamic preferences
if script.get("height", 0) == 0:
    btn.setFixedHeight(def_h)
```

**New (broken - complex):**
```python
btn = CyberButton(script.get("name", "Unnamed"), script_data=script)

# Determine effective height for this specific item
item_h = script.get("height", 0)
if item_h == 0: item_h = def_h

# Scale height by row span to ensure it actually takes up the space
spacing = 10
total_h = (item_h * r_span) + (spacing * (r_span - 1))
btn.setFixedHeight(total_h) 
```

The new version adds row_span calculation which may cause issues.

### 4. Grid Row Stretch

**Old:** No row stretch added after items

**New:** Adds stretch at end:
```python
self.grid.setRowStretch(r + 1, 1)
```

---

## Recommendation

To fix the new version while keeping scroll working:

1. Keep `SizePolicy.Policy.Fixed` for vertical (needed for scroll)
2. Restore `setMinimumHeight(45)` fallback in CyberButton
3. Simplify the height logic in refresh_grid back to the old approach
4. Remove or keep the row stretch (test both)

The old version's height worked because buttons had `Expanding` vertical policy which let them fill space. The new version needs `Fixed` for scroll, but the height calculation became too complex.
