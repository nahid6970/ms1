# Hierarchical Folder Picker Dropdown

A custom popup dropdown that visually distinguishes parent folders from subfolders using indentation, compact sizing, and an SVG tree-indent arrow.

## Structure

```html
<div id="folderPickerPopup"></div>
```

```css
#folderPickerPopup {
  display: none;
  position: fixed;
  z-index: 5000;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  min-width: 160px;
  padding: 6px;
  max-height: 320px;
  overflow-y: auto;
}
```

## JavaScript — Building Items

Sort folders so subfolders appear immediately after their parent, then render each as a `<button>`:

```js
function openFolderPickerPopup(event, currentFolderId) {
  const allFolders = window._folders; // your folders array
  const topLevel = allFolders.filter(f => !f.parentId);
  const ordered = topLevel.flatMap(f => [f, ...allFolders.filter(s => s.parentId === f._id)]);

  const items = [
    { label: 'No folder', value: '', isSubfolder: false },
    ...ordered.map(f => ({ label: f.name, value: f._id, isSubfolder: !!f.parentId }))
  ];

  const popup = document.getElementById('folderPickerPopup');
  popup.innerHTML = items.map(item => `
    <button onclick="pickFolder('${item.value}')" style="
      display: flex;
      align-items: center;
      gap: 5px;
      width: 100%;
      text-align: left;
      padding: ${item.isSubfolder ? '5px 10px 5px 22px' : '8px 14px'};
      background: ${item.value === currentFolderId ? '#eff6ff' : 'transparent'};
      color: ${item.value === currentFolderId ? '#1d4ed8' : '#1e293b'};
      border: none;
      border-radius: 8px;
      font-size: ${item.isSubfolder ? '12px' : '13px'};
      cursor: pointer;
    ">
      ${item.isSubfolder ? `
        <svg width="11" height="11" viewBox="0 0 12 12" fill="none" style="flex-shrink:0;opacity:0.4">
          <path d="M2 2v6h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M7 8l3 0" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M8 6l2 2-2 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>` : ''}
      ${item.label}
    </button>
  `).join('');

  // Position near trigger
  const rect = event.target.getBoundingClientRect();
  popup.style.display = 'block';
  const pw = popup.offsetWidth || 160;
  const ph = popup.offsetHeight || 200;
  let left = rect.left;
  let top = rect.bottom + 6;
  if (left + pw > window.innerWidth - 8) left = window.innerWidth - pw - 8;
  if (top + ph > window.innerHeight - 8) top = rect.top - ph - 6;
  popup.style.left = left + 'px';
  popup.style.top = top + 'px';
}

// Close on outside click
document.addEventListener('click', e => {
  if (!document.getElementById('folderPickerPopup').contains(e.target)) {
    document.getElementById('folderPickerPopup').style.display = 'none';
  }
});
```

## Key Design Decisions

| Property | Parent folder | Subfolder |
|---|---|---|
| `padding-left` | `14px` | `22px` |
| `padding-top/bottom` | `8px` | `5px` |
| `font-size` | `13px` | `12px` |
| SVG arrow | — | ✓ (opacity 0.4) |

## Native `<select>` Fallback

SVG doesn't work inside `<option>` elements. Use a text prefix instead:

```js
options.map(o => `<option value="${o.id}">
  ${o.parentId ? '  › ' : ''}${o.name}
</option>`)
```
