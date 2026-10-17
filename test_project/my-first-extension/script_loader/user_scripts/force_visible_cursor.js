(function () {
  if (window.__forceVisibleCursorLoaded) return;
  window.__forceVisibleCursorLoaded = true;

  const scriptPath = 'user_scripts/force_visible_cursor.js';
  let enabled = true;
  const changedElements = new Map();
  let cursorHost = null;

  function showOverlayCursor(event) {
    if (!cursorHost) {
      cursorHost = document.createElement('div');
      cursorHost.id = '__force_visible_cursor_overlay__';
      cursorHost.style.cssText = 'position:fixed !important;inset:0 auto auto 0 !important;width:32px !important;height:40px !important;z-index:2147483647 !important;pointer-events:none !important;contain:strict !important;';
      const shadow = cursorHost.attachShadow({ mode: 'closed' });
      shadow.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36" aria-hidden="true" style="display:block;overflow:visible">
          <path d="M2 1.5v27l7-7 5 11 5-2.2-5-10.8h10L2 1.5z" fill="white" stroke="black" stroke-width="2" stroke-linejoin="round"/>
        </svg>`;
      (document.documentElement || document).appendChild(cursorHost);
    }

    cursorHost.style.setProperty('transform', `translate3d(${event.clientX}px, ${event.clientY}px, 0)`, 'important');
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
  }

  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName !== 'local' || !changes.enabledScripts) return;
    enabled = Boolean(changes.enabledScripts.newValue?.[scriptPath]);
    if (!enabled) restoreCursors();
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
