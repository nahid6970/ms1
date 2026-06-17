(() => {
  if (window.__inspectorActive) return;

  let active = false;
  let hovered = null;
  let panel = null;
  let overlay = null;

  // ── Helpers ──────────────────────────────────────────────────────────────

  function getCssSelector(el) {
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    let cur = el;
    while (cur && cur.nodeType === 1 && cur !== document.body) {
      let part = cur.tagName.toLowerCase();
      if (cur.id) { part = '#' + CSS.escape(cur.id); parts.unshift(part); break; }
      const siblings = Array.from(cur.parentNode?.children || []).filter(c => c.tagName === cur.tagName);
      if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(cur) + 1})`;
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
      const siblings = Array.from(cur.parentNode?.children || []).filter(c => c.tagName === cur.tagName);
      const idx = siblings.indexOf(cur) + 1;
      parts.unshift(cur.tagName.toLowerCase() + (siblings.length > 1 ? `[${idx}]` : ''));
      cur = cur.parentNode;
    }
    return '/' + parts.join('/');
  }

  function getStyles(el) {
    const computed = window.getComputedStyle(el);
    const keys = ['display','position','width','height','margin','padding','background','color',
                  'font-size','font-family','border','flex','grid','z-index','opacity','overflow'];
    return keys.map(k => `${k}: ${computed.getPropertyValue(k)}`).join(';\n') + ';';
  }

  function getAttrs(el) {
    return Array.from(el.attributes).map(a => `${a.name}="${a.value}"`).join('\n') || '(none)';
  }

  function getOuterHTML(el) {
    const clone = el.cloneNode(false);
    return clone.outerHTML;
  }

  function buildData(el) {
    return [
      { label: 'CSS Selector', value: getCssSelector(el) },
      { label: 'Tag',          value: el.tagName.toLowerCase() },
      { label: 'Classes',      value: el.className || '(none)' },
      { label: 'ID',           value: el.id || '(none)' },
      { label: 'XPath',        value: getXPath(el) },
      { label: 'Attributes',   value: getAttrs(el) },
      { label: 'Inline Style', value: el.style.cssText || '(none)' },
      { label: 'Computed Style', value: getStyles(el) },
      { label: 'HTML (open tag)', value: getOuterHTML(el) },
      { label: 'Text Content', value: (el.textContent || '').trim().slice(0, 200) || '(none)' },
    ];
  }

  // ── Overlay highlight ─────────────────────────────────────────────────────

  function showOverlay(el) {
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = '__insp_overlay';
      Object.assign(overlay.style, {
        position: 'fixed', pointerEvents: 'none', zIndex: '2147483646',
        background: 'rgba(59,130,246,0.25)', border: '2px solid #3b82f6',
        boxSizing: 'border-box', transition: 'all 0.05s',
      });
      document.body.appendChild(overlay);
    }
    const r = el.getBoundingClientRect();
    Object.assign(overlay.style, {
      top: r.top + 'px', left: r.left + 'px',
      width: r.width + 'px', height: r.height + 'px', display: 'block',
    });
  }

  function hideOverlay() {
    if (overlay) overlay.style.display = 'none';
  }

  // ── Panel ─────────────────────────────────────────────────────────────────

  function showPanel(el) {
    if (panel) panel.remove();

    panel = document.createElement('div');
    panel.id = '__insp_panel';
    panel.innerHTML = `
      <div id="__insp_header">
        <span>🔍 Inspector</span>
        <button id="__insp_close">✕</button>
      </div>
      <div id="__insp_tag">&lt;${el.tagName.toLowerCase()}&gt;</div>
      <div id="__insp_rows"></div>`;
    document.body.appendChild(panel);

    const rows = panel.querySelector('#__insp_rows');
    buildData(el).forEach(({ label, value }) => {
      const row = document.createElement('div');
      row.className = '__insp_row';
      row.innerHTML = `
        <div class="__insp_label">${label}</div>
        <pre class="__insp_value">${escHtml(value)}</pre>
        <button class="__insp_copy" data-val="${escAttr(value)}">Copy</button>`;
      rows.appendChild(row);
    });

    panel.querySelector('#__insp_close').onclick = deactivate;

    panel.querySelectorAll('.__insp_copy').forEach(btn => {
      btn.onclick = () => {
        const val = btn.dataset.val;
        const ok = () => { btn.textContent = '✓'; setTimeout(() => (btn.textContent = 'Copy'), 1200); };
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(val).then(ok);
        } else {
          const ta = document.createElement('textarea');
          ta.value = val;
          ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0;';
          document.body.appendChild(ta);
          ta.focus(); ta.select();
          document.execCommand('copy');
          ta.remove();
          ok();
        }
      };
    });

    // Drag panel
    const header = panel.querySelector('#__insp_header');
    let ox, oy, dragging = false;
    header.addEventListener('mousedown', e => {
      dragging = true; ox = e.clientX - panel.offsetLeft; oy = e.clientY - panel.offsetTop;
    });
    document.addEventListener('mousemove', e => {
      if (!dragging) return;
      panel.style.left = (e.clientX - ox) + 'px';
      panel.style.top  = (e.clientY - oy) + 'px';
      panel.style.right = 'auto';
    });
    document.addEventListener('mouseup', () => { dragging = false; });
  }

  function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function escAttr(s) { return String(s).replace(/"/g,'&quot;'); }

  // ── Event handlers ────────────────────────────────────────────────────────

  function onMouseOver(e) {
    if (!active) return;
    if (panel && panel.contains(e.target)) return;
    hovered = e.target;
    showOverlay(hovered);
  }

  function onClick(e) {
    if (!active) return;
    if (panel && panel.contains(e.target)) return;
    e.preventDefault(); e.stopPropagation();
    showPanel(hovered || e.target);
  }

  // ── Activate / Deactivate ─────────────────────────────────────────────────

  window.__inspectorActivate = function () {
    if (active) return;
    active = true;
    window.__inspectorActive = true;
    document.body.style.cursor = 'crosshair';
    document.addEventListener('mouseover', onMouseOver, true);
    document.addEventListener('click', onClick, true);
  };

  window.__inspectorDeactivate = deactivate;

  function deactivate() {
    active = false;
    window.__inspectorActive = false;
    document.body.style.cursor = '';
    document.removeEventListener('mouseover', onMouseOver, true);
    document.removeEventListener('click', onClick, true);
    hideOverlay();
    if (panel) { panel.remove(); panel = null; }
  }

})();
