(function () {
  if (window.__forceVisibleCursorLoaded) return;
  window.__forceVisibleCursorLoaded = true;

  const scriptPath = 'user_scripts/force_visible_cursor.js';
  let enabled = true;
  let cursorStyle = 'arrow';
  const changedElements = new Map();
  let cursorHost = null;
  let cursorShadow = null;

  const cursorOptions = {
    arrow: {
      width: 28, height: 36, hotspotX: 0, hotspotY: 0,
      svg: '<path d="M2 1.5v27l7-7 5 11 5-2.2-5-10.8h10L2 1.5z" fill="white" stroke="black" stroke-width="2" stroke-linejoin="round"/>'
    },
    hand: {
      width: 28, height: 36, hotspotX: 7, hotspotY: 2,
      svg: '<path d="M7 17V5a2 2 0 0 1 4 0v8-9a2 2 0 0 1 4 0v9-7a2 2 0 0 1 4 0v9-5a2 2 0 0 1 4 0v11c0 7-4 12-11 12h-1c-4 0-6-2-8-5l-3-5a2 2 0 0 1 3-3l4 3z" fill="white" stroke="black" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
    },
    crosshair: {
      width: 28, height: 28, hotspotX: 14, hotspotY: 14,
      svg: '<circle cx="14" cy="14" r="8" fill="white" fill-opacity=".65" stroke="black" stroke-width="2"/><path d="M14 0v9m0 10v9M0 14h9m10 0h9" stroke="black" stroke-width="2"/><path d="M14 0v9m0 10v9M0 14h9m10 0h9" stroke="white" stroke-width=".8"/>'
    },
    dot: {
      width: 18, height: 18, hotspotX: 9, hotspotY: 9,
      svg: '<circle cx="9" cy="9" r="6" fill="white" stroke="black" stroke-width="3"/><circle cx="9" cy="9" r="2" fill="#ff3b30"/>'
    }
  };

  function renderCursor() {
    if (!cursorShadow) return;
    const option = cursorOptions[cursorStyle] || cursorOptions.arrow;
    cursorShadow.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="${option.width}" height="${option.height}" viewBox="0 0 ${option.width} ${option.height}" aria-hidden="true" style="display:block;overflow:visible">${option.svg}</svg>`;
  }

  function showOverlayCursor(event) {
    if (!cursorHost) {
      cursorHost = document.createElement('div');
      cursorHost.id = '__force_visible_cursor_overlay__';
      cursorHost.style.cssText = 'position:fixed !important;inset:0 auto auto 0 !important;width:32px !important;height:40px !important;z-index:2147483647 !important;pointer-events:none !important;contain:strict !important;';
      cursorShadow = cursorHost.attachShadow({ mode: 'closed' });
      renderCursor();
      (document.documentElement || document).appendChild(cursorHost);
    }

    const option = cursorOptions[cursorStyle] || cursorOptions.arrow;
    cursorHost.style.setProperty('transform', `translate3d(${event.clientX - option.hotspotX}px, ${event.clientY - option.hotspotY}px, 0)`, 'important');
    cursorHost.style.setProperty('display', 'block', 'important');
  }

  function restoreCursors() {
    for (const [element, previous] of changedElements) {
      if (previous.value) {
        element.style.setProperty('cursor', previous.value, previous.priority);
      } else {
        element.style.removeProperty('cursor');
      }
    }
    changedElements.clear();
    cursorHost?.remove();
    cursorHost = null;
    cursorShadow = null;
  }

  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName !== 'local') return;
    if (changes.visibleCursorStyle) {
      const selectedStyle = changes.visibleCursorStyle.newValue;
      cursorStyle = cursorOptions[selectedStyle] ? selectedStyle : 'arrow';
      renderCursor();
    }
    if (changes.enabledScripts) {
      enabled = Boolean(changes.enabledScripts.newValue?.[scriptPath]);
      if (!enabled) restoreCursors();
    }
  });

  chrome.storage.local.get(['visibleCursorStyle'], (result) => {
    if (cursorOptions[result.visibleCursorStyle]) {
      cursorStyle = result.visibleCursorStyle;
      renderCursor();
    }
  });

  document.addEventListener('pointermove', (event) => {
    if (!enabled) return;
    showOverlayCursor(event);

    const target = event.target;
    if (!(target instanceof Element)) return;

    if (!changedElements.has(target)) {
      changedElements.set(target, {
        value: target.style.getPropertyValue('cursor'),
        priority: target.style.getPropertyPriority('cursor')
      });
    }
    target.style.setProperty('cursor', 'none', 'important');
  }, true);

  document.addEventListener('pointerleave', () => {
    if (cursorHost) cursorHost.style.setProperty('display', 'none', 'important');
  });
})();
