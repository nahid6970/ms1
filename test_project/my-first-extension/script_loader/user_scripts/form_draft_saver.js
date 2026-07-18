(function() {
  const STORAGE_PREFIX = 'draft_saver_';
  const restoredElements = new WeakSet();
  
  function getElementId(el) {
    return el.id || el.name || Array.from(document.querySelectorAll(el.tagName)).indexOf(el);
  }

  function getStorageKey(el) {
    return STORAGE_PREFIX + window.location.host + window.location.pathname + '_' + el.tagName.toLowerCase() + '_' + getElementId(el);
  }

  function restoreDrafts() {
    const inputs = document.querySelectorAll('input:not([type="password"]):not([type="hidden"]):not([type="checkbox"]):not([type="radio"]), textarea');
    inputs.forEach(input => {
      if (restoredElements.has(input)) return;
      
      const key = getStorageKey(input);
      const savedValue = localStorage.getItem(key);
      if (savedValue && !input.value) {
        input.value = savedValue;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
      restoredElements.add(input);
    });
  }

  function saveDraft(e) {
    const el = e.target;
    if ((el.tagName === 'INPUT' && !['password', 'hidden', 'checkbox', 'radio'].includes(el.type)) || el.tagName === 'TEXTAREA') {
      const key = getStorageKey(el);
      if (el.value.trim() === '') {
        localStorage.removeItem(key);
      } else {
        localStorage.setItem(key, el.value);
      }
    }
  }

  function clearDrafts(e) {
    const form = e.target;
    const inputs = form.querySelectorAll('input, textarea');
    inputs.forEach(input => {
      const key = getStorageKey(input);
      localStorage.removeItem(key);
    });
  }

  document.addEventListener('input', saveDraft);
  document.addEventListener('submit', clearDrafts);
  
  // Run immediately and scan periodically for dynamic inputs
  restoreDrafts();
  setInterval(restoreDrafts, 2000);
  
  console.log('Form Draft Saver loaded.');
})();
