(() => {
  if (window.__inspectorActivate) { window.__inspectorActivate(); return; }

  let active = false, hovered = null, panel = null, cursorStyle = null, overlayEl = null;

  // ── Helpers ───────────────────────────────────────────────────────────────

  function getCssSelector(el) {
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    let cur = el;
    while (cur && cur.nodeType === 1 && cur !== document.body) {
      let part = cur.tagName.toLowerCase();
      if (cur.id) { parts.unshift('#' + CSS.escape(cur.id)); break; }
      const sibs = Array.from(cur.parentNode?.children || []).filter(c => c.tagName === cur.tagName);
      if (sibs.length > 1) part += `:nth-of-type(${sibs.indexOf(cur) + 1})`;
      parts.unshift(part);
      cur = cur.parentNode;
    }
    return parts.join(' > ');
  }

  function getXPath(el) {
    if (el.id) return `//*[@id="${el.id}"]`;
    const parts = [];
    let cur = el;
    while (cur && cur.nodeType === 1) {
      const sibs = Array.from(cur.parentNode?.children || []).filter(c => c.tagName === cur.tagName);
      parts.unshift(cur.tagName.toLowerCase() + (sibs.length > 1 ? `[${sibs.indexOf(cur)+1}]` : ''));
      cur = cur.parentNode;
    }
    return '/' + parts.join('/');
  }

  function getStyles(el) {
    const cs = window.getComputedStyle(el);
    return ['display','position','width','height','margin','padding','background','color',
            'font-size','font-family','border','flex','z-index','opacity','overflow']
      .map(k => `${k}: ${cs.getPropertyValue(k)}`).join(';\n') + ';';
  }

  function buildData(el) {
    return [
      { label: 'CSS Selector',    value: getCssSelector(el) },
      { label: 'Tag',             value: el.tagName.toLowerCase() },
      { label: 'Classes',         value: el.className || '(none)' },
      { label: 'ID',              value: el.id || '(none)' },
      { label: 'XPath',           value: getXPath(el) },
      { label: 'Attributes',      value: Array.from(el.attributes).map(a=>`${a.name}="${a.value}"`).join('\n') || '(none)' },
      { label: 'Inline Style',    value: el.style.cssText || '(none)' },
      { label: 'Computed Style',  value: getStyles(el) },
      { label: 'HTML (open tag)', value: el.cloneNode(false).outerHTML },
      { label: 'Text Content',    value: (el.textContent||'').trim().slice(0,200) || '(none)' },
    ];
  }

  function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  // ── Highlight ─────────────────────────────────────────────────────────────

  function showOverlay(el) {
    if (!overlayEl) {
      overlayEl = document.createElement('div');
      overlayEl.style.cssText = 'position:fixed;pointer-events:none;z-index:2147483646;background:rgba(59,130,246,0.35);border:2px solid #3b82f6;box-sizing:border-box;transition:all 0.05s;';
      document.body.appendChild(overlayEl);
    }
    const r = el.getBoundingClientRect();
    Object.assign(overlayEl.style, {
      display: 'block',
      top: r.top + 'px', left: r.left + 'px',
      width: r.width + 'px', height: r.height + 'px',
    });
  }

  function hideOverlay() {
    if (overlayEl) overlayEl.style.display = 'none';
  }

  // ── Panel ─────────────────────────────────────────────────────────────────

  function showPanel(el) {
    if (panel) panel.remove();
    panel = document.createElement('div');
    panel.id = '__insp_panel';
    panel.innerHTML = `
      <div id="__insp_header"><span>🔍 Inspector</span><button id="__insp_close">✕</button></div>
      <div id="__insp_tag">&lt;${el.tagName.toLowerCase()}&gt;</div>
      <div id="__insp_rows"></div>`;
    document.body.appendChild(panel);

    const rows = panel.querySelector('#__insp_rows');
    buildData(el).forEach(({ label, value }) => {
      const row = document.createElement('div');
      row.className = '__insp_row';
      row.innerHTML = `<div class="__insp_label">${label}</div><pre class="__insp_value">${esc(value)}</pre><button class="__insp_copy">Copy</button>`;
      row.querySelector('.__insp_copy').addEventListener('click', () => {
        const btn = row.querySelector('.__insp_copy');
        const ok = () => { btn.textContent = '✓'; setTimeout(() => btn.textContent = 'Copy', 1200); };
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(value).then(ok);
        } else {
          const ta = document.createElement('textarea');
          ta.value = value;
          ta.style.cssText = 'position:fixed;opacity:0;';
          document.body.appendChild(ta); ta.select();
          document.execCommand('copy'); ta.remove(); ok();
        }
      });
      rows.appendChild(row);
    });

    panel.querySelector('#__insp_close').onclick = deactivate;

    let ox, oy, dragging = false;
    panel.querySelector('#__insp_header').addEventListener('mousedown', e => {
      dragging = true; ox = e.clientX - panel.offsetLeft; oy = e.clientY - panel.offsetTop;
      e.preventDefault();
    });
    document.addEventListener('mousemove', e => {
      if (!dragging) return;
      panel.style.left = (e.clientX - ox) + 'px';
      panel.style.top = (e.clientY - oy) + 'px';
      panel.style.right = 'auto';
    });
    document.addEventListener('mouseup', () => dragging = false);
  }

  // ── Events ────────────────────────────────────────────────────────────────

  function onMouseOver(e) {
    if (panel && panel.contains(e.target)) return;
    hovered = e.target; showOverlay(hovered);
  }
  function onClick(e) {
    if (panel && panel.contains(e.target)) return;
    e.preventDefault(); e.stopPropagation();
    showPanel(hovered || e.target);
    stopSelecting();
  }
  function onKeyDown(e) { if (e.key === 'Escape') deactivate(); }

  // ── Activate / Deactivate ─────────────────────────────────────────────────

  function activate() {
    if (active) return;
    active = true;
    if (panel) { panel.remove(); panel = null; }
    cursorStyle = document.createElement('style');
    cursorStyle.textContent = '*{cursor:pointer!important}';
    document.head.appendChild(cursorStyle);
    document.addEventListener('mouseover', onMouseOver, true);
    document.addEventListener('click', onClick, true);
    document.addEventListener('keydown', onKeyDown, true);
  }

  function stopSelecting() {
    active = false;
    if (cursorStyle) { cursorStyle.remove(); cursorStyle = null; }
    hideOverlay();
    document.removeEventListener('mouseover', onMouseOver, true);
    document.removeEventListener('click', onClick, true);
  }

  function deactivate() {
    stopSelecting();
    if (overlayEl) { overlayEl.remove(); overlayEl = null; }
    document.removeEventListener('keydown', onKeyDown, true);
    if (panel) { panel.remove(); panel = null; }
  }

  window.__inspectorActivate = activate;
  window.__inspectorDeactivate = deactivate;

  activate();
})();
