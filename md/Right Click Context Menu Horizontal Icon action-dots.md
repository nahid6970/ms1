# Action Dots Pattern

Replace bulky icon buttons on cards/items with minimal 12px dot buttons that appear on hover. Clean, space-saving, and works great for galleries, file managers, dashboards.

## The CSS

```css
.action-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  padding: 0;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.35);
  transition: transform 0.15s, box-shadow 0.15s;
}
.action-dot:hover { transform: scale(1.35); box-shadow: 0 2px 8px rgba(0,0,0,0.45); }

/* Color variants */
.action-dot.red    { background: #ef4444; }                                          /* delete */
.action-dot.blue   { background: #3b82f6; }                                          /* action / popup */
.action-dot.yellow { background: #f59e0b; box-shadow: 0 1px 6px rgba(245,158,11,0.6); } /* pin / favorite */
.action-dot.grey   { background: #94a3b8; }                                          /* inactive toggle */
.action-dot.green  { background: #22c55e; }                                          /* confirm / active */
```

## Card Setup

```css
/* Show dots only on hover */
.card { position: relative; }

.card-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
  z-index: 10;
}

.card:hover .card-actions {
  opacity: 1;
  pointer-events: auto;
}
```

## HTML

```html
<div class="card">
  <!-- card content -->

  <div class="card-actions">
    <!-- grey when inactive, yellow when active (e.g. pinned) -->
    <button class="action-dot grey" onclick="togglePin(id)" title="Pin"></button>

    <!-- opens a popup picker instead of a dropdown -->
    <button class="action-dot blue" onclick="openPickerPopup(event, id)" title="Move to folder"></button>

    <!-- destructive action -->
    <button class="action-dot red" onclick="deleteItem(id)" title="Delete"></button>
  </div>
</div>
```

## Popup Picker (for the blue dot)

Instead of a `<select>` dropdown, the blue dot opens a floating popup.

```html
<div id="pickerPopup" style="display:none; position:fixed; z-index:5000;
  background:white; border:1px solid #e2e8f0; border-radius:12px;
  box-shadow:0 8px 32px rgba(0,0,0,0.18); min-width:160px; padding:6px;
  max-height:320px; overflow-y:auto;">
</div>
```

```js
const popup = document.getElementById('pickerPopup');
let _activeId = null;

function openPickerPopup(event, id, currentValue = '') {
  event.stopPropagation();
  _activeId = id;

  const options = [
    { label: 'No folder', value: '' },
    { label: 'Work',      value: 'work' },
    { label: 'Personal',  value: 'personal' },
  ];

  popup.innerHTML = options.map(o => `
    <button onclick="pickOption('${o.value}')" style="
      display:block; width:100%; text-align:left;
      padding:9px 14px; border:none; border-radius:8px; cursor:pointer; font-size:13px;
      background:${o.value === currentValue ? '#eff6ff' : 'transparent'};
      color:${o.value === currentValue ? '#1d4ed8' : '#1e293b'};
    ">${o.label}</button>
  `).join('');

  // Smart positioning
  popup.style.display = 'block';
  const { left: x, bottom: y, top } = event.target.getBoundingClientRect();
  const pw = popup.offsetWidth  || 160;
  const ph = popup.offsetHeight || 200;
  const left = Math.min(x, window.innerWidth  - pw - 8);
  const top2 = y + ph > window.innerHeight - 8 ? top - ph - 6 : y + 6;
  popup.style.left = left + 'px';
  popup.style.top  = top2 + 'px';
}

function pickOption(value) {
  if (_activeId) applyOption(_activeId, value); // your logic here
  closePopup();
}

function closePopup() { popup.style.display = 'none'; _activeId = null; }

document.addEventListener('click', e => { if (!popup.contains(e.target)) closePopup(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closePopup(); });
```

## Pinned / Active State Visual

When a dot toggles state, flip its color class and add a visible effect to the card:

```js
function togglePin(id) {
  const card = document.querySelector(`[data-id="${id}"]`);
  const dot  = card.querySelector('.action-dot.grey, .action-dot.yellow');
  const isPinned = dot.classList.contains('yellow');

  dot.classList.toggle('grey',   isPinned);
  dot.classList.toggle('yellow', !isPinned);
  card.classList.toggle('pinned', !isPinned);
}
```

```css
/* Strong pinned card effect so it's obvious at a glance */
.card.pinned {
  border: 2px solid #f59e0b;
  box-shadow: 0 0 0 2px #f59e0b, 0 4px 16px rgba(245,158,11,0.35);
}

/* Optional emoji badge */
.card.pinned::before {
  content: '📌';
  position: absolute;
  top: 6px; left: 8px;
  font-size: 14px;
  z-index: 5;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.4));
}
```

## Color Convention (suggestion)

| Color  | Use case                        |
|--------|---------------------------------|
| red    | Delete / destructive            |
| blue   | Picker / action popup           |
| yellow | Pinned / favorited (active)     |
| grey   | Toggle off / inactive state     |
| green  | Confirm / online / active state |
