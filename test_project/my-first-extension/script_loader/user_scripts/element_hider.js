(function () {
  const STORAGE_KEY = 'element_hider_rules';
  const PICKER_ACTIVE_CLASS = '__eh_picker_active__';

  // ─── Helpers ──────────────────────────────────────────────────────────────

  function currentPort() {
    return window.location.port || (window.location.protocol === 'https:' ? '443' : '80');
  }

  function loadRules(cb) {
    chrome.storage.local.get([STORAGE_KEY], (result) => {
      cb(result[STORAGE_KEY] || {});
    });
  }

  function saveRules(rules, cb) {
    chrome.storage.local.set({ [STORAGE_KEY]: rules }, cb);
  }

  // ─── CSS Injection ────────────────────────────────────────────────────────

  let styleEl = null;

  function applyHiddenSelectors(selectors) {
    if (!styleEl) {
      styleEl = document.createElement('style');
      styleEl.id = '__element_hider_styles__';
      document.head.appendChild(styleEl);
    }
    styleEl.textContent = selectors && selectors.length > 0
      ? selectors.join(',\n') + ' { display: none !important; }'
      : '';
  }

  function refreshHiding() {
    loadRules((rules) => {
      const portRules = rules[currentPort()];
      applyHiddenSelectors(
        portRules && portRules.enabled && portRules.selectors ? portRules.selectors : []
      );
    });
  }

  // ─── Floating Action Button (Shadow DOM) ──────────────────────────────────

  function getFabBtn() {
    const host = document.getElementById('__eh_host__');
    return host && host.shadowRoot ? host.shadowRoot.getElementById('fab') : null;
  }

  function updateFabState() {
    const btn = getFabBtn();
    if (!btn) return;
    if (pickerActive) {
      btn.textContent = '✕';
      btn.title = 'Cancel picker (ESC)';
      btn.classList.add('picking');
    } else {
      btn.textContent = '👁';
      btn.title = 'Pick element to hide';
      btn.classList.remove('picking');
    }
  }

  function injectFab() {
    if (document.getElementById('__eh_host__')) return;

    // Host wrapper — fixed position, above everything
    const host = document.createElement('div');
    host.id = '__eh_host__';
    // Use setAttribute so inline style beats any page stylesheet
    host.setAttribute('style',
      'all:initial!important;' +
      'position:fixed!important;' +
      'bottom:16px!important;' +
      'right:16px!important;' +
      'width:42px!important;' +
      'height:42px!important;' +
      'z-index:2147483647!important;' +
      'pointer-events:none!important;' +
      'display:block!important;'
    );

    // Shadow DOM — page CSS cannot penetrate this
    const shadow = host.attachShadow({ mode: 'open' });
    shadow.innerHTML = `
      <style>
        button {
          all: unset;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 42px;
          height: 42px;
          border-radius: 50%;
          border: 1px solid #555;
          background: #2d2d30;
          color: #d4d4d4;
          font-size: 18px;
          cursor: pointer;
          box-shadow: 0 2px 10px rgba(0,0,0,0.6);
          pointer-events: all;
          box-sizing: border-box;
          transition: background 0.2s, transform 0.15s;
          user-select: none;
        }
        button:hover { transform: scale(1.12); }
        button.picking { background: #c0392b; border-color: #e74c3c; }
      </style>
      <button id="fab" title="Pick element to hide">👁</button>
    `;

    shadow.getElementById('fab').addEventListener('click', () => {
      pickerActive ? stopPicker() : startPicker();
    });

    // Attach to <html>, not <body> — body overflow:hidden can clip fixed children
    document.documentElement.appendChild(host);
  }

  // ─── Visual Picker ────────────────────────────────────────────────────────

  let pickerActive = false;
  let highlightOverlay = null;

  function getSimpleSelector(el) {
    if (el.id) return '#' + CSS.escape(el.id);
    let selector = el.tagName.toLowerCase();
    if (el.className && typeof el.className === 'string') {
      const classes = el.className.trim().split(/\s+/).filter(Boolean);
      if (classes.length > 0) selector += '.' + classes.map(CSS.escape).join('.');
    }
    return selector;
  }

  function createOverlay() {
    const el = document.createElement('div');
    el.id = '__eh_highlight_overlay__';
    el.setAttribute('style',
      'position:fixed!important;' +
      'pointer-events:none!important;' +
      'z-index:2147483646!important;' +
      'background:rgba(86,156,214,0.2)!important;' +
      'border:2px solid #569cd6!important;' +
      'box-sizing:border-box!important;' +
      'transition:top 0.06s,left 0.06s,width 0.06s,height 0.06s!important;'
    );
    document.documentElement.appendChild(el);
    return el;
  }

  function positionOverlay(el) {
    if (!highlightOverlay) return;
    const r = el.getBoundingClientRect();
    highlightOverlay.style.cssText = highlightOverlay.getAttribute('style') +
      `top:${r.top}px!important;left:${r.left}px!important;` +
      `width:${r.width}px!important;height:${r.height}px!important;display:block!important;`;
  }

  function showToast(message, color) {
    const old = document.getElementById('__eh_toast__');
    if (old) old.remove();
    const toast = document.createElement('div');
    toast.id = '__eh_toast__';
    toast.textContent = message;
    toast.setAttribute('style',
      'position:fixed!important;' +
      'bottom:70px!important;' +
      'left:50%!important;' +
      'transform:translateX(-50%)!important;' +
      `background:${color || '#1e1e1e'}!important;` +
      'color:#d4d4d4!important;' +
      'font-family:monospace!important;' +
      'font-size:12px!important;' +
      'padding:8px 16px!important;' +
      'border-radius:4px!important;' +
      'border:1px solid #555!important;' +
      'z-index:2147483647!important;' +
      'pointer-events:none!important;' +
      'white-space:nowrap!important;' +
      'opacity:1!important;' +
      'transition:opacity 0.4s ease!important;'
    );
    document.documentElement.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; }, 1800);
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 2300);
  }

  function isOurElement(el) {
    // Ignore our own injected UI
    return el.id === '__eh_host__' ||
           el.id === '__eh_highlight_overlay__' ||
           el.id === '__eh_toast__';
  }

  function onPickerMouseMove(e) {
    if (isOurElement(e.target)) return;
    positionOverlay(e.target);
  }

  function onPickerClick(e) {
    if (isOurElement(e.target)) return;
    e.preventDefault();
    e.stopPropagation();

    const selector = getSimpleSelector(e.target);
    const port = currentPort();

    loadRules((rules) => {
      if (!rules[port]) rules[port] = { enabled: true, selectors: [] };
      if (!rules[port].selectors.includes(selector)) {
        rules[port].selectors.push(selector);
      }
      saveRules(rules, () => {
        refreshHiding();
        showToast(`Hidden: ${selector}`, '#163d2a');
      });
    });

    stopPicker();
  }

  function onPickerKeyDown(e) {
    if (e.key === 'Escape') stopPicker();
  }

  function startPicker() {
    if (pickerActive) return;
    pickerActive = true;
    document.documentElement.classList.add(PICKER_ACTIVE_CLASS);
    highlightOverlay = createOverlay();
    document.addEventListener('mousemove', onPickerMouseMove, true);
    document.addEventListener('click', onPickerClick, true);
    document.addEventListener('keydown', onPickerKeyDown, true);
    showToast('Click an element to hide it  |  ESC to cancel', '#1a2f4a');
    updateFabState();
  }

  function stopPicker() {
    if (!pickerActive) return;
    pickerActive = false;
    document.documentElement.classList.remove(PICKER_ACTIVE_CLASS);
    if (highlightOverlay) { highlightOverlay.remove(); highlightOverlay = null; }
    document.removeEventListener('mousemove', onPickerMouseMove, true);
    document.removeEventListener('click', onPickerClick, true);
    document.removeEventListener('keydown', onPickerKeyDown, true);
    updateFabState();
  }

  // ─── Init ─────────────────────────────────────────────────────────────────

  function init() {
    // Inject FAB immediately if body exists, else wait for DOM
    if (document.body) {
      injectFab();
    } else {
      document.addEventListener('DOMContentLoaded', injectFab);
    }

    // Apply any existing rules for this port
    refreshHiding();
  }

  // Re-apply hiding when popup changes rules
  chrome.storage.onChanged.addListener((changes) => {
    if (changes[STORAGE_KEY]) refreshHiding();
  });

  init();
  console.log('[Element Hider] loaded on port:', currentPort());
})();
